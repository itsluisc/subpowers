#!/usr/bin/env python3
"""Unit & integration tests for subpowers v0.5.0:
- Dual plugin manifests (Claude Code .claude-plugin + .mcp.json + Antigravity plugin.json + mcp_config.json)
- Shared zero-dependency stdio MCP server (both newline-delimited JSON and Content-Length framing)
- Higgsfield Soul ID resolution, quality enum guard, Higgsfield video (t2v + omni_reference + cap)
- 4-painter council (--with-higgsfield) & 18% neutral gray (#3A3A3C) avatar sheet (--from + --style)
- install.sh --link multi-harness wiring
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
BIN = os.path.join(REPO, "bin")
STUBS = os.path.join(REPO, "tests", "stubs")
sys.path.insert(0, STUBS)
import fakeimg  # noqa: E402


def build_stub_path(tmpdir):
    pdir = os.path.join(tmpdir, "path")
    os.makedirs(pdir, exist_ok=True)
    base_tools = [
        "bash", "sh", "env", "python3", "perl", "cat", "cp", "mv", "rm", "ln",
        "mkdir", "mktemp", "dirname", "basename", "readlink", "date", "grep",
        "sed", "awk", "tr", "wc", "head", "tail", "ls", "find", "sort",
        "touch", "chmod", "sleep", "tar", "uname", "cut", "shasum",
    ]
    for t in base_tools:
        found = shutil.which(t)
        if found:
            os.symlink(found, os.path.join(pdir, t))
    for stub in ("codex", "agy", "grok", "curl", "higgsfield"):
        os.symlink(os.path.join(STUBS, stub), os.path.join(pdir, stub))
    return pdir


class SubpowersV05Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="subpowers-v05-test.")
        self.home = os.path.join(self.tmp, "home")
        self.out = os.path.join(self.tmp, "out")
        os.makedirs(self.home)
        os.makedirs(self.out)
        self.path = build_stub_path(self.tmp)
        self.stub_log = os.path.join(self.tmp, "stub.log")
        self.paints_log = os.path.join(self.tmp, "paints.log")
        open(self.stub_log, "w").close()
        open(self.paints_log, "w").close()
        self.env = {
            "HOME": self.home,
            "PATH": self.path,
            "TMPDIR": self.tmp,
            "STUB_LOG": self.stub_log,
            "STUB_PAINTS": self.paints_log,
            "SUBPOWERS_NO_AUTOUPDATE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
        }

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_sp(self, *args, extra_env=None):
        env = dict(self.env)
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            ["bash", os.path.join(BIN, "subpowers"), *args],
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )

    def test_dual_plugin_manifests_valid(self):
        for rel in (
            ".claude-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
            ".mcp.json",
            "plugin.json",
            "mcp_config.json",
        ):
            full = os.path.join(REPO, rel)
            self.assertTrue(os.path.isfile(full), f"missing {rel}")
            with open(full, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertIsInstance(data, dict)

        with open(os.path.join(REPO, ".mcp.json")) as f:
            cmcp = json.load(f)
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/bin/subpowers-mcp", cmcp["mcpServers"]["subpowers"]["args"])

        with open(os.path.join(REPO, "mcp_config.json")) as f:
            amcp = json.load(f)
        self.assertIn("${PLUGIN_ROOT}/bin/subpowers-mcp", amcp["mcpServers"]["subpowers"]["args"])

        with open(os.path.join(REPO, "plugin.json")) as f:
            ap = json.load(f)
        self.assertEqual(ap["name"], "subpowers")
        self.assertTrue(os.path.isfile(os.path.join(REPO, ap["logo"])))
        self.assertTrue(os.path.isfile(os.path.join(REPO, "skills", "subpowers", "SKILL.md")))
        self.assertTrue(os.access(os.path.join(BIN, "grok-video"), os.X_OK))
        self.assertTrue(os.access(os.path.join(BIN, "subpowers-mcp"), os.X_OK))

    def test_mcp_jsonl_and_framed_stdio(self):
        # 1) Newline-delimited JSON
        reqs = "\n".join([
            json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}}),
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
            json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
            json.dumps({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "subpowers_powers", "arguments": {}}}),
            json.dumps({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "subpowers_soul", "arguments": {"action": "list"}}}),
        ]) + "\n"
        r = subprocess.run(
            ["python3", os.path.join(BIN, "subpowers-mcp")],
            input=reqs,
            env=self.env,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = [json.loads(l) for l in r.stdout.splitlines() if l.strip()]
        self.assertEqual([m["id"] for m in lines], [1, 2, 3, 4])
        self.assertEqual(lines[0]["result"]["protocolVersion"], "2025-03-26")
        tool_names = {t["name"] for t in lines[1]["result"]["tools"]}
        self.assertTrue({"subpowers_image", "subpowers_avatar", "subpowers_video", "subpowers_soul", "subpowers_powers"}.issubset(tool_names))
        self.assertFalse(lines[2]["result"]["isError"])
        self.assertFalse(lines[3]["result"]["isError"])
        souls_payload = json.loads(lines[3]["result"]["content"][0]["text"])
        self.assertEqual(souls_payload["souls"][0]["name"], "Demo Creator")

        # 2) Content-Length framed JSON-RPC
        msg = json.dumps({"jsonrpc": "2.0", "id": 9, "method": "ping"}).encode("utf-8")
        framed = f"Content-Length: {len(msg)}\r\n\r\n".encode("ascii") + msg
        r2 = subprocess.run(
            ["python3", os.path.join(BIN, "subpowers-mcp")],
            input=framed,
            env=self.env,
            capture_output=True,
            timeout=30,
        )
        self.assertEqual(r2.returncode, 0)
        self.assertTrue(r2.stdout.startswith(b"Content-Length: "))
        body = r2.stdout.split(b"\r\n\r\n", 1)[1]
        self.assertEqual(json.loads(body)["id"], 9)

        # 3) Malformed tool arguments must return isError=True and keep server alive
        bad_reqs = "\n".join([
            json.dumps({"jsonrpc": "2.0", "id": 20, "method": "tools/call", "params": {"name": "subpowers_image", "arguments": ["not-an-object"]}}),
            json.dumps({"jsonrpc": "2.0", "id": 21, "method": "tools/call", "params": {"name": "subpowers_image", "arguments": {"prompt": "mug", "output_path": "/tmp/x.png", "ref_paths": "/tmp/not-a-list.png"}}}),
            json.dumps({"jsonrpc": "2.0", "id": 22, "method": "ping"}),
        ]) + "\n"
        r3 = subprocess.run(
            ["python3", os.path.join(BIN, "subpowers-mcp")],
            input=bad_reqs,
            env=self.env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(r3.returncode, 0, r3.stderr)
        res3 = [json.loads(l) for l in r3.stdout.splitlines() if l.strip()]
        self.assertEqual([m["id"] for m in res3], [20, 21, 22])
        self.assertTrue(res3[0]["result"]["isError"])
        self.assertTrue(res3[1]["result"]["isError"])
        self.assertEqual(res3[2]["result"], {})

    def test_higgsfield_soul_id_auto_route_and_quality_enum(self):
        out = os.path.join(self.out, "soul-shot.png")
        r = self.run_sp(
            "image", "portrait in a sunlit coffee shop", out, "--soul-id", "Demo Creator",
            extra_env={"HIGGSFIELD_IMAGE_QUALITY": "bogus"},
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("not valid for text2image_soul_v2", r.stderr)
        self.assertTrue(os.path.isfile(out))
        with open(os.path.join(self.out, "soul-shot.prompt.txt")) as f:
            rec = f.read()
        self.assertIn("image model requested: text2image_soul_v2", rec)
        self.assertIn("Demo Creator (11111111-2222-3333-4444-555555555555)", rec)
        with open(self.stub_log) as f:
            slog = f.read()
        self.assertIn('"--custom_reference_id", "11111111-2222-3333-4444-555555555555"', slog)
        self.assertIn('"--quality", "2k"', slog)

    def test_higgsfield_video_t2v_and_omni_reference_and_cap(self):
        # Text-only -> t2v + honors HIGGSFIELD_VIDEO_RESOLUTION
        vid1 = os.path.join(self.out, "clip1.mp4")
        r1 = self.run_sp(
            "video", "slow drone shot over coastal cliffs", vid1,
            "--painter", "higgsfield", "--aspect", "9:16",
            extra_env={"HIGGSFIELD_VIDEO_RESOLUTION": "1080p"},
        )
        self.assertEqual(r1.returncode, 0, r1.stderr)
        self.assertTrue(os.path.isfile(vid1))
        with open(self.stub_log) as f:
            slog = f.read()
            self.assertIn('"--mode", "t2v"', slog)
            self.assertIn('"--resolution", "1080p"', slog)

        # With first frame -> omni_reference
        first = os.path.join(self.tmp, "first.png")
        fakeimg.png(first, 1080, 1920)
        vid2 = os.path.join(self.out, "clip2.mp4")
        r2 = self.run_sp("video", "camera pushes in smoothly", vid2, "--painter", "higgsfield", "--first", first)
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.assertTrue(os.path.isfile(vid2))
        with open(self.stub_log) as f:
            self.assertIn('"--mode", "omni_reference"', f.read())

        # Over cap -> refused with 0 spend
        vid3 = os.path.join(self.out, "clip3.mp4")
        r3 = self.run_sp("video", "expensive clip", vid3, "--painter", "higgsfield", extra_env={"STUB_HF_COST": "99"})
        self.assertEqual(r3.returncode, 1)
        self.assertIn("over the cap", r3.stderr)
        self.assertFalse(os.path.exists(vid3))

        # Wait timeout after job submitted -> MUST exit 5 (billing safety) and print job id
        with open(os.path.join(self.home, ".stub-higgsfield-credits"), "w") as f:
            f.write("200.0")
        vid4 = os.path.join(self.out, "clip4.mp4")
        r4 = self.run_sp("video", "long render", vid4, "--painter", "higgsfield", extra_env={"STUB_HF_VIDEO_STILL_RUNNING": "1"})
        self.assertEqual(r4.returncode, 5, r4.stderr)
        self.assertIn("credits spent", r4.stderr)
        self.assertIn("higgsfield generate wait", r4.stderr)

        # Cross-painter flag guard: --voice rejected on higgsfield, --model rejected on grok
        r5 = self.run_sp("video", "talking clip", vid4, "--painter", "higgsfield", "--voice", "ara")
        self.assertEqual(r5.returncode, 2)
        self.assertIn("Grok-only", r5.stderr)
        r6 = self.run_sp("video", "talking clip", vid4, "--painter", "grok", "--model", "seedance_2_5", "--first", first)
        self.assertEqual(r6.returncode, 2)
        self.assertIn("Higgsfield video flags", r6.stderr)

    def test_council_with_higgsfield_and_default_safety(self):
        # Default council must NOT invoke higgsfield
        out1 = os.path.join(self.out, "c3.png")
        r1 = self.run_sp("image", "minimal desk lamp", out1, "--painter", "council")
        self.assertEqual(r1.returncode, 0, r1.stderr)
        with open(self.paints_log) as f:
            p1 = f.read()
        self.assertNotIn("higgsfield", p1)

        # Opt-in 4-painter council with --soul-id must succeed on ALL 4 painters without leaking --soul-id
        open(self.paints_log, "w").close()
        out2 = os.path.join(self.out, "c4.png")
        r2 = self.run_sp("image", "minimal desk lamp", out2, "--painter", "council", "--with-higgsfield", "--soul-id", "Demo Creator")
        self.assertEqual(r2.returncode, 0, r2.stderr)
        with open(self.paints_log) as f:
            p2 = f.read()
        for painter in ("codex", "agy", "grok", "higgsfield"):
            self.assertIn(painter, p2, f"{painter} did not paint in 4-way council with --soul-id")

    def test_avatar_dark_gray_and_from_flag(self):
        me = os.path.join(self.tmp, "me.png")
        fakeimg.png(me, 800, 1000)
        sheet = os.path.join(self.out, "avatar.png")
        r = self.run_sp("avatar", "--from", me, sheet, "--painter", "chatgpt", "--style", "3d-toon")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isfile(sheet))
        with open(os.path.join(self.out, "avatar.prompt.txt")) as f:
            rec = f.read()
        self.assertIn("#3A3A3C", rec)
        self.assertNotIn("18%", rec)
        self.assertIn("3D toon-shaded", rec)

    def test_install_link_multi_harness(self):
        dest = os.path.join(self.tmp, "fakehome")
        for sub in (".gemini/config", ".cursor", ".grok", ".hermes"):
            os.makedirs(os.path.join(dest, sub), exist_ok=True)
        r = subprocess.run(
            ["bash", os.path.join(REPO, "install.sh"), "--link", "--dest", dest, "--no-doctor"],
            env=self.env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.islink(os.path.join(dest, ".claude", "skills", "subpowers")))
        self.assertTrue(os.path.islink(os.path.join(dest, ".cursor", "rules", "subpowers.mdc")))
        for sub in (".agents/skills", ".codex/skills", ".gemini/config/skills", ".cursor/skills", ".grok/skills", ".hermes/skills"):
            self.assertTrue(os.path.isfile(os.path.join(dest, sub, "subpowers", "SKILL.md")), f"missing link under {sub}")
        for b in ("subpowers", "subpowers-mcp", "grok-video", "higgsfield-image", "higgsfield-video", "higgsfield-soul"):
            self.assertTrue(os.path.islink(os.path.join(dest, ".local", "bin", b)), f"missing bin link {b}")


if __name__ == "__main__":
    unittest.main()
