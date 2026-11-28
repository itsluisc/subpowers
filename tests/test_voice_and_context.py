#!/usr/bin/env python3
"""Offline unit & integration tests for:
- ElevenLabs paid voice lane (status, voices, speak, sfx, music, dry-run, intone --speak chain)
- URL & Creator context engine (SSRF guard, X post, webpage, opt-in Poppy AI MCP, opt-in TokScript MCP)
- Style-referenced carousels (cover-anchored multi-slide deck + --test-cover council)
- Shared stdio MCP tools (subpowers_voice, subpowers_context, subpowers_carousel, from_url)
"""
import http.server
from pathlib import Path
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
BIN = os.path.join(REPO, "bin")
STUBS = os.path.join(REPO, "tests", "stubs")
sys.path.insert(0, STUBS)
import fakeimg  # noqa: E402
try:
    import PIL
except ImportError:
    PIL = None

ELEVENLABS_STUB = """#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
log = os.environ.get("STUB_EL_LOG")
if log:
    open(log, "a").write(json.dumps(args) + "\\n")
if os.environ.get("STUB_EL_LOGGED_OUT") == "1":
    print("Not logged in. Run `elevenlabs auth login` to authenticate.")
    sys.exit(1)
if args[:2] == ["auth", "status"]:
    print("Scheme: OAuth\\n  authenticated")
    sys.exit(0)
if args[:2] == ["user", "get"]:
    print(json.dumps({"subscription": {"tier": "creator", "character_count": 1000, "character_limit": 100000}}))
    sys.exit(0)
if args[:2] == ["voices", "search"]:
    print(json.dumps({"voices": [
        {"voice_id": "vPremade1234567890", "name": "Rachel", "category": "premade"},
        {"voice_id": "vClonedLuis1234567", "name": "Luis Clone", "category": "cloned"},
    ]}))
    sys.exit(0)
if "-o" in args:
    out = args[args.index("-o") + 1]
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "wb") as f:
        f.write(b"RIFF\\x24\\x00\\x00\\x00WAVEfmt stub-elevenlabs-audio")
    sys.exit(0)
print("unexpected elevenlabs args:", args, file=sys.stderr)
sys.exit(1)
"""


class MockHandler(http.server.BaseHTTPRequestHandler):
    png_bytes = b""

    def log_message(self, format, *args):
        return

    def do_GET(self):
        if self.path.startswith("/elonmusk/status/12345"):
            payload = {
                "tweet": {
                    "text": "Starship flight test update from Starbase.",
                    "author": {"name": "Elon Musk", "screen_name": "elonmusk"},
                    "media": {"photos": [{"url": f"http://127.0.0.1:{self.server.server_port}/photo.png"}]},
                }
            }
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(body)
        elif self.path == "/photo.png":
            self.send_response(200); self.send_header("Content-Type", "image/png"); self.end_headers()
            self.wfile.write(self.png_bytes)
        elif self.path == "/article":
            page = (
                '<html><head><title>Creator Study</title>'
                '<meta property="og:title" content="Bold Carousel Design"/>'
                '<meta property="og:description" content="High contrast editorial slides outperform plain templates by 3x."/>'
                f'<meta property="og:image" content="http://127.0.0.1:{self.server.server_port}/photo.png"/>'
                '</head><body><p>Body text.</p></body></html>'
            ).encode("utf-8")
            self.send_response(200); self.send_header("Content-Type", "text/html"); self.end_headers()
            self.wfile.write(page)
        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        ln = int(self.headers.get("Content-Length", "0"))
        req = json.loads(self.rfile.read(ln).decode("utf-8"))
        tname = (req.get("params") or {}).get("name")
        img_url = f"http://127.0.0.1:{self.server.server_port}/photo.png"
        if self.path == "/poppy":
            data = {"title": "Viral Carousel", "author": "@creator", "hook": "Stop making boring slides", "on_screen_text": "3 rules", "image_url": img_url}
        elif self.path == "/tokscript":
            data = {"posts": [{"type": "carousel", "views": 950000, "caption": "Editorial typography hook", "cover_image": img_url}]}
        else:
            data = {"tool": tname}
        resp = {"jsonrpc": "2.0", "id": req.get("id", 1), "result": {"content": [{"type": "text", "text": json.dumps(data)}]}}
        body = json.dumps(resp).encode("utf-8")
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(body)


class SubpowersVoiceContextCarouselTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tmp_png = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp_png.close()
        fakeimg.png(tmp_png.name, 400, 400)
        with open(tmp_png.name, "rb") as f:
            MockHandler.png_bytes = f.read()
        os.unlink(tmp_png.name)
        cls.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), MockHandler)
        cls.port = cls.httpd.server_port
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="subpowers-vc-test.")
        self.home = os.path.join(self.tmp, "home")
        self.out = os.path.join(self.tmp, "out")
        self.pdir = os.path.join(self.tmp, "path")
        for d in (self.home, self.out, self.pdir):
            os.makedirs(d, exist_ok=True)
        for t in ("bash", "sh", "env", "python3", "perl", "cat", "cp", "mv", "rm", "ln", "mkdir", "mktemp", "dirname", "basename", "readlink", "date", "grep", "sed", "awk", "tr", "wc", "head", "tail", "ls", "find", "sort", "touch", "chmod", "sleep", "tar", "uname", "cut", "shasum"):
            found = shutil.which(t)
            if found:
                os.symlink(found, os.path.join(self.pdir, t))
        for stub in ("codex", "agy", "grok", "curl", "higgsfield"):
            os.symlink(os.path.join(STUBS, stub), os.path.join(self.pdir, stub))
        el_path = os.path.join(self.pdir, "elevenlabs")
        with open(el_path, "w", encoding="utf-8") as f:
            f.write(ELEVENLABS_STUB)
        os.chmod(el_path, os.stat(el_path).st_mode | stat.S_IXUSR)
        self.stub_log = os.path.join(self.tmp, "stub.log")
        self.paints_log = os.path.join(self.tmp, "paints.log")
        self.el_log = os.path.join(self.tmp, "el.log")
        for f in (self.stub_log, self.paints_log, self.el_log):
            open(f, "w").close()
        self.env = {
            "HOME": self.home,
            "PATH": self.pdir,
            "TMPDIR": self.tmp,
            # Keep the real decoder available even when HOME hides the user site.
            "PYTHONPATH": os.pathsep.join(filter(None, (STUBS, os.path.dirname(os.path.dirname(PIL.__file__)) if PIL else None))),
            "STUB_LOG": self.stub_log,
            "STUB_PAINTS": self.paints_log,
            "STUB_EL_LOG": self.el_log,
            "SUBPOWERS_NO_AUTOUPDATE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
        }

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_sp(self, *args, extra_env=None):
        env = dict(self.env)
        if extra_env:
            env.update(extra_env)
        return subprocess.run(["bash", os.path.join(BIN, "subpowers"), *args], env=env, capture_output=True, text=True, timeout=60)

    def test_elevenlabs_voice_and_intone_speak_chain(self):
        # 1) Status + voices + speak auto-picking cloned voice & wav_44100
        rs = self.run_sp("voice", "status", "--json")
        self.assertEqual(rs.returncode, 0, rs.stderr)
        self.assertTrue(json.loads(rs.stdout)["paid_tool"])

        wav = os.path.join(self.out, "hello.wav")
        rd = self.run_sp("voice", "speak", "Testing dry run characters", wav, "--dry-run")
        self.assertEqual(rd.returncode, 0, rd.stderr)
        self.assertEqual(json.loads(rd.stdout)["estimated_chars"], 26)
        self.assertFalse(os.path.exists(wav))

        rsp = self.run_sp("voice", "speak", "Hey everyone welcome back", wav)
        self.assertEqual(rsp.returncode, 0, rsp.stderr)
        self.assertTrue(os.path.isfile(wav))
        with open(self.el_log) as f:
            elog = f.read()
        self.assertIn("vClonedLuis1234567", elog)
        self.assertIn("wav_44100", elog)

        # 2) SFX & music
        sfx_out = os.path.join(self.out, "whoosh.mp3")
        self.assertEqual(self.run_sp("voice", "sfx", "cinematic riser whoosh", sfx_out, "--duration", "2.5", "--loop").returncode, 0)
        self.assertTrue(os.path.isfile(sfx_out))
        mus_out = os.path.join(self.out, "bed.mp3")
        self.assertEqual(self.run_sp("voice", "music", "warm lo-fi beats", mus_out, "--duration", "15", "--instrumental").returncode, 0)
        self.assertTrue(os.path.isfile(mus_out))

        # 3) One-command intone --speak chain (ElevenLabs -> Higgsfield Intone)
        char_img = os.path.join(self.tmp, "char.png")
        room_img = os.path.join(self.tmp, "room.png")
        fakeimg.png(char_img, 640, 640); fakeimg.png(room_img, 640, 640)
        with open(os.path.join(self.home, ".stub-higgsfield-credits"), "w", encoding="utf-8") as f:
            f.write("200.0")
        vid = os.path.join(self.out, "avatar-talk.mp4")
        ri = self.run_sp("intone", vid, "--character", char_img, "--location", room_img, "--speak", "Watch what subpowers can build.", "--voice", "Luis Clone")
        self.assertEqual(ri.returncode, 0, ri.stderr)
        self.assertTrue(os.path.isfile(vid))
        self.assertTrue(os.path.isfile(os.path.join(self.out, "avatar-talk.voice.wav")))

    def test_context_ssrf_guard_and_public_poppy_tokscript_sources(self):
        # 1) SSRF guard MUST refuse localhost / loopback by default
        r_ssrf = self.run_sp("context", f"http://127.0.0.1:{self.port}/article", "--json")
        self.assertEqual(r_ssrf.returncode, 2, r_ssrf.stderr)
        self.assertIn("non-public IP", r_ssrf.stderr)

        base = f"http://127.0.0.1:{self.port}"
        local_env = {
            "SUBPOWERS_CONTEXT_ALLOW_LOCAL": "1",
            "SUBPOWERS_FXTWITTER_BASE": base,
            "SUBPOWERS_POPPY_MCP_URL": f"{base}/poppy",
            "SUBPOWERS_TOKSCRIPT_MCP_URL": f"{base}/tokscript",
            "POPPY_MCP_KEY": "stub-poppy-key",
            "TOKSCRIPT_API_KEY": "stub-tokscript-key",
        }

        # 2) X post reference + image --from-url
        rx = self.run_sp("context", "https://x.com/elonmusk/status/12345", "--source", "public", "--json", extra_env=local_env)
        self.assertEqual(rx.returncode, 0, rx.stderr)
        dx = json.loads(rx.stdout)
        self.assertEqual(dx["kind"], "x_post")
        self.assertIn("Starship flight test", dx["summary"])
        self.assertEqual(len(dx["ref_images"]), 1 if PIL else 0)

        img_out = os.path.join(self.out, "elon-card.png")
        rimg = self.run_sp("image", "editorial thumbnail reacting to post", img_out, "--painter", "chatgpt", "--from-url", "https://x.com/elonmusk/status/12345", extra_env=local_env)
        self.assertEqual(rimg.returncode, 0, rimg.stderr)
        self.assertTrue(os.path.isfile(img_out))
        with open(os.path.join(self.out, "elon-card.prompt.txt")) as f:
            self.assertIn("Starship flight test", f.read())

        # 3) Opt-in Poppy AI & TokScript creator reference
        rp = self.run_sp("context", "https://www.instagram.com/p/ABC123/", "--source", "poppy", "--json", extra_env=local_env)
        self.assertNotEqual(rp.returncode, 0)
        self.assertIn("HTTPS", rp.stderr)
        rt = self.run_sp("context", "@creator", "--source", "tokscript", "--json", extra_env=local_env)
        self.assertNotEqual(rt.returncode, 0)
        self.assertIn("HTTPS", rt.stderr)
        auto = self.run_sp("context", "@creator", "--json", extra_env=local_env)
        self.assertNotEqual(auto.returncode, 0)
        self.assertIn("explicitly select", auto.stderr)

    def test_style_referenced_carousel_and_mcp_tools(self):
        slides = os.path.join(self.tmp, "slides.txt")
        with open(slides, "w", encoding="utf-8") as f:
            f.write("Stop Making Boring Carousels | bold editorial cover\n[graphic] Anchor Slide 2 to Slide 1 | clean split layout\n")
        sref = os.path.join(self.tmp, "creator-slide.png")
        fakeimg.png(sref, 640, 800)
        cdir = os.path.join(self.out, "deck")
        brand_path = Path(self.tmp) / "brand.txt"
        brand_path.write_text("demo brand")
        rc = self.run_sp("carousel", slides, cdir, "--approved-sha256", hashlib.sha256(Path(slides).read_bytes()).hexdigest(), "--style-ref", sref, "--brand-file", str(brand_path), "--painter", "chatgpt")
        self.assertEqual(rc.returncode, 0, rc.stderr)
        self.assertTrue(os.path.isfile(os.path.join(cdir, "01.png")))
        self.assertTrue(os.path.isfile(os.path.join(cdir, "02.png")))
        self.assertTrue(os.path.isfile(os.path.join(cdir, "carousel.prompt.txt")))

        receipt = (Path(cdir) / "carousel.prompt.txt").read_text()
        self.assertIn("style_refs_passed: creator-slide.png", receipt)
        self.assertIn("brand_file: brand.txt", receipt)
        for rec in Path(cdir).glob("*.prompt.txt"):
            self.assertNotIn(self.tmp, rec.read_text())
            self.assertNotIn(REPO, rec.read_text())

        # Face-bleed guard + multi-format batch + brand-file/offer/parallel
        me_img = os.path.join(self.tmp, "me.png")
        fakeimg.png(me_img, 400, 400)
        self.assertEqual(self.run_sp("refs", "add", "host", me_img).returncode, 0)
        brand_md = os.path.join(self.tmp, "brand.md")
        with open(brand_md, "w", encoding="utf-8") as f:
            f.write("# Brand Guide\nDirect, gritty disruptor voice. No corporate fluff.\n")
        fspec = os.path.join(self.tmp, "formats.json")
        with open(fspec, "w", encoding="utf-8") as f:
            json.dump({
                "brand_file": brand_md,
                "offer": "$99 30-day live challenge",
                "formats": [
                    {
                        "name": "fmt-a",
                        "refs": "host",
                        "style_refs": [sref],
                        "style_desc": "Dark schematic editorial cover",
                        "slides": ["Cover A | portrait", "[graphic] Slide 2 A | diagram", "Slide 3 A | CTA"],
                    },
                    {
                        "name": "fmt-b",
                        "refs": "host",
                        "style_desc": "White woven paper magazine cover",
                        "slides": ["Cover B | magazine", "[graphic] Slide 2 B | big stat"],
                    },
                ],
            }, f)
        batch_dir = os.path.join(self.out, "batch")
        rb = self.run_sp("carousel", "--formats-json", fspec, batch_dir, "--painter", "chatgpt", "--parallel", "2")
        self.assertEqual(rb.returncode, 0, rb.stderr)
        self.assertTrue(os.path.isfile(os.path.join(batch_dir, "fmt-a", "slides.txt")))
        self.assertFalse(os.path.exists(os.path.join(batch_dir, "fmt-a", "01.png")))

        # Script-first approval gate (--plan-only writes scripts-for-approval.md with ZERO images painted)
        plan_dir = os.path.join(self.out, "plan-only")
        rp = self.run_sp("carousel", "--formats-json", fspec, plan_dir, "--plan-only")
        self.assertEqual(rp.returncode, 0, rp.stderr)
        self.assertTrue(os.path.isfile(os.path.join(plan_dir, "scripts-for-approval.md")))
        self.assertFalse(os.path.exists(os.path.join(plan_dir, "fmt-a", "01.png")))

        # MCP tools: tools/list + script-first gate blocks stage='render' without approved=true
        reqs = "\n".join([
            json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}),
            json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "subpowers_voice", "arguments": {"action": "status"}}}),
            json.dumps({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "subpowers_context", "arguments": {"target": "status"}}}),
            json.dumps({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "subpowers_carousel", "arguments": {"output_dir": "relative-dir", "topic": "test"}}}),
            json.dumps({"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "subpowers_carousel", "arguments": {"output_dir": plan_dir, "slides_file": slides, "stage": "render"}}}),
        ]) + "\n"
        rm = subprocess.run(["python3", os.path.join(BIN, "subpowers-mcp")], input=reqs, env=self.env, capture_output=True, text=True, timeout=30)
        self.assertEqual(rm.returncode, 0, rm.stderr)
        res = [json.loads(l) for l in rm.stdout.splitlines() if l.strip()]
        names = {t["name"] for t in res[0]["result"]["tools"]}
        self.assertTrue({"subpowers_voice", "subpowers_context", "subpowers_carousel"}.issubset(names))
        self.assertFalse(res[1]["result"]["isError"])
        self.assertFalse(res[2]["result"]["isError"])
        self.assertTrue(res[3]["result"]["isError"])
        self.assertTrue(res[4]["result"]["isError"])
        self.assertIn("SCRIPT-FIRST GATE", res[4]["result"]["content"][0]["text"])


if __name__ == "__main__":
    unittest.main()
