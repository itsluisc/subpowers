import hashlib
import json
import os
import socket
import runpy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from stubs.fakeimg import jpeg

BIN = Path(__file__).resolve().parents[1] / "bin"


def load(name):
    with patch.object(sys, "path", [str(BIN), *sys.path]):
        return runpy.run_path(str(BIN / name))


class SafetyTests(unittest.TestCase):
    def test_paid_sources_need_explicit_selection(self):
        fetch = load("context-ref")["fetch_context"]
        for name in ("poppy", "tokscript"):
            with patch.dict(fetch.__globals__, {"fetch_"+name: lambda target: {"kind": name},
                                                "env_get": lambda *a: "configured"}):
                with tempfile.TemporaryDirectory() as root:
                    with self.assertRaises(ValueError):
                        fetch("@demo", out_dir=Path(root))
                    self.assertEqual(fetch("@demo", source=name, out_dir=Path(root), download_images=False)["kind"], name)

    def test_authenticated_transport_never_delegates_redirects(self):
        m = load("context-ref")
        with self.assertRaisesRegex(ValueError,"HTTPS"):
            m["mcp_http_call"]("http://example.invalid", "x", {}, {})
        handler = m["NoAuthRedirect"]()
        with patch("urllib.request.build_opener") as build, patch.dict(m["mcp_http_call"].__globals__, {"validate_public_url": lambda u:u}):
            build.return_value.open.side_effect = RuntimeError("mock TLS transport")
            with self.assertRaisesRegex(RuntimeError, "mock TLS"):
                m["mcp_http_call"]("https://example.invalid", "x", {}, {"Authorization":"dummy"})
            self.assertIsInstance(build.call_args.args[0],type(handler))
        for code in (301,302,303,307,308):
            with self.assertRaises(ValueError):
                handler.redirect_request(None,None,code,"",{},"https://other.invalid")

    def test_both_openers_check_actual_connection_before_socket_use(self):
        m = load("context-ref")
        public = (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443))
        denied = (*public[:4], ("127.0.0.1", 443))
        for call in [lambda: m["http_get"]("http://example.invalid"),
                     lambda: m["http_get"]("https://example.invalid"),
                     lambda: m["mcp_http_call"]("https://example.invalid", "test", {}, {})]:
            with patch.dict(os.environ, {"SUBPOWERS_CONTEXT_ALLOW_LOCAL": "0",
                                         "https_proxy": "http://proxy.invalid"}), patch(
                    "socket.getaddrinfo", side_effect=[[public], [denied]]) as dns, patch("socket.socket") as sock:
                with self.assertRaisesRegex(ValueError, "non-public"):
                    call()
                self.assertEqual(dns.call_count, 2)
                sock.assert_not_called()
        with patch("socket.getaddrinfo", return_value=[public]) as dns, patch("socket.socket") as sock:
            m["checked_connect"](("example.invalid", 443), 5)
            dns.assert_called_once()
            sock.return_value.connect.assert_called_once_with(public[4])

    def test_social_and_youtube_fetch_only_through_guarded_transport(self):
        m = load("context-ref")
        for name, args, body in [("fetch_youtube", ("https://youtu.be/example", "example"), b"{}"),
                                 ("fetch_social_video_or_page", ("https://vimeo.com/example",), b"ok"),
                                 ("fetch_social_video_or_page", ("https://example.invalid/vimeo.com",), b"ok")]:
            fn = m[name]
            with patch.dict(fn.__globals__, {"http_get": lambda *a, **k: (body, "", a[0])}), patch(
                    "shutil.which", return_value="yt-dlp"), patch("subprocess.run") as child:
                self.assertTrue(fn(*args))
                child.assert_not_called()

    def test_carousel_refuses_reused_delivery_and_confines_batch_formats(self):
        main = load("carousel")["main"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "approved.txt"
            p.write_text("One")
            dest = root / "delivery"
            dest.mkdir()
            stale = dest / "02.png"
            stale.write_bytes(b"accepted")
            self.assertNotEqual(main([str(p), str(dest), "--approved-sha256",
                                      hashlib.sha256(p.read_bytes()).hexdigest()]), 0)
            self.assertEqual(list(dest.iterdir()), [stale])
            self.assertEqual(stale.read_bytes(), b"accepted")
            spec = root / "formats.json"
            for idx, name in enumerate((".", "..")):
                spec.write_text(json.dumps([{"name":name, "slides":["one"]}]))
                self.assertNotEqual(main(["--formats-json", str(spec), str(root/f"batch{idx}")]), 0)
            self.assertFalse(list(root.rglob("slides.txt")))
            batch = root / "linked-batch"
            batch.mkdir()
            (batch / "outside").symlink_to(dest, target_is_directory=True)
            spec.write_text(json.dumps([{"name":"outside", "slides":["one"]}]))
            self.assertNotEqual(main(["--formats-json", str(spec), str(batch)]), 0)
            self.assertEqual(list(dest.iterdir()), [stale])

    def test_voice_key_only_in_environment(self):
        run = load("elevenlabs-voice")["run_el"]
        with patch.dict(run.__globals__, {"find_cli":lambda:"voice","api_key":lambda:"dummy"}), patch("subprocess.run") as child:
            run(["voices"])
            self.assertEqual(child.call_args.args[0], ["voice","voices"])
            self.assertEqual(child.call_args.kwargs["env"]["ELEVENLABS_API_KEY"], "dummy")

    def test_approval_binds_file_bytes_and_rejects_topics(self):
        m=load("carousel")
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"slides.txt";p.write_text("first")
            digest=hashlib.sha256(p.read_bytes()).hexdigest()
            p.write_text("changed")
            self.assertNotEqual(m["main"]([str(p),str(Path(root)/"new"),"--approved-sha256",digest]),0)
            tool=load("subpowers-mcp")["handle_tool"]
            for extra in ({"topic":"new"}, {"formats_json":str(p)}, {"topic":"new","test_cover":True}):
                ok,_=tool("subpowers_carousel", dict(output_dir=root,stage="render",approved=True,approved_sha256=digest,**extra))
                self.assertFalse(ok)

    def test_context_publishes_no_remote_links(self):
        fetch = load("context-ref")["fetch_context"]
        link = "https://example.invalid/media?signature=fixture"
        raw = {"kind":"demo", "source_url":link, "image_urls":[link], "title":"Photo "+link,
               "summary":"Example", "unexpected":{"download":link}}
        for download in (False, True):
            with self.subTest(download=download), tempfile.TemporaryDirectory() as root, patch.dict(
                fetch.__globals__, {"fetch_poppy": lambda _: raw.copy(),
                                    "download_image": lambda url, dest, idx: str(dest/"ref_1.png")}):
                ctx = fetch("@demo", source="poppy", out_dir=Path(root), download_images=download)
                saved = (Path(root)/"context.json").read_text()
                self.assertNotIn(root, saved)
                self.assertEqual(json.loads(saved)["ref_images"], ["ref_1.png"] if download else [])
                self.assertNotIn("signature", saved)
                self.assertNotIn("unexpected", ctx)
                self.assertEqual(len(ctx["ref_images"]), int(download))
                self.assertIn("Example", ctx["prompt_context"])

    def test_context_rejects_header_only_reference_before_save(self):
        fetch = load("context-ref")["download_image"]
        data = b"\x89PNG\r\n\x1a\n" + bytes(300)
        with tempfile.TemporaryDirectory() as tmp, patch.dict(fetch.__globals__, {
                "http_get": lambda *a, **kw: (data, "image/png", None)}):
            self.assertIsNone(fetch("https://example.invalid/ref", Path(tmp), 1))
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_cover_is_really_png_or_refused(self):
        main = load("carousel")["main"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script, cover = root / "slides.txt", root / "cover.png"
            script.write_text("One slide")
            digest = hashlib.sha256(script.read_bytes()).hexdigest()
            jpeg(cover, 32, 32)
            args = ["--approved-sha256", digest, "--cover", str(cover)]
            rc = main([str(script), str(root / "deck"), *args])
            slide = root / "deck/01.png"
            try:
                from PIL import Image
            except ImportError:
                self.assertNotEqual(rc, 0)
                self.assertFalse(slide.exists())
            else:
                self.assertEqual(rc, 0)
                with Image.open(slide) as im:
                    im.load()
                    self.assertEqual((im.format, im.size), ("PNG", (32, 32)))
            cover.write_bytes(b"invalid")
            self.assertNotEqual(main([str(script), str(root / "bad"), *args]), 0)
            self.assertFalse((root / "bad/01.png").exists())
