"""No provider calls or real credentials: exercise the loopback fallback contract."""
import base64
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

BIN = Path(__file__).resolve().parents[1] / "bin" / "cliproxy-image"
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=")
MODEL = "gemini-3.1-flash-image"


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.out = self.root / "test.png"
        (self.root / "key").write_text("secret-never-print")
        self.posts = []
        self.mode = "ok"
        case = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                if case.mode == "redirect":
                    self.send_response(302)
                    self.send_header("Location", "https://example.invalid/steal")
                    self.end_headers()
                    return
                self.send_response(200)
                self.end_headers()
                owner = "gemini-api" if case.mode == "wrong-owner" else "antigravity"
                self.wfile.write(json.dumps({"data": [{"id": MODEL, "owned_by": owner}]}).encode())

            def do_POST(self):
                case.posts.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
                if case.mode == "quota":
                    self.send_response(429)
                    self.end_headers()
                    self.wfile.write(b"secret-never-print")
                    return
                self.send_response(200)
                self.end_headers()
                url = "data:image/png;base64," + base64.b64encode(PNG).decode()
                if case.mode == "remote":
                    url = "https://example.invalid/image.png"
                if case.mode == "invalid":
                    url = "data:image/png;base64," + base64.b64encode(b"fake" * 20).decode()
                self.wfile.write(json.dumps({"model": MODEL, "choices": [{"message": {"images": [{"image_url": {"url": url}}]}}]}).encode())

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.env = dict(os.environ, AGY_IMAGE_PROXY_URL="http://127.0.0.1:%d" % self.server.server_port,
                        AGY_IMAGE_PROXY_KEY_FILE=str(self.root / "key"), AGY_PROXY_IMAGE_MODEL=MODEL)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.tmp.cleanup()

    def run_image(self):
        r = subprocess.run(["python3", str(BIN), "a banana", str(self.out)], env=self.env, capture_output=True, text=True, timeout=10)
        self.assertNotIn("secret-never-print", r.stdout + r.stderr)
        return r

    def test_success_receipt(self):
        self.assertEqual(self.run_image().returncode, 0)
        self.assertEqual(self.out.read_bytes(), PNG)
        r = json.loads(self.out.with_suffix(".generation.json").read_text())
        self.assertEqual(r["provider_observed_model"], MODEL)
        self.assertFalse(r["native_agy_fixed"])
        self.assertEqual(r["state"], "delivered")
        self.assertEqual(len(self.posts), 1)
        self.assertEqual(self.posts[0]["messages"][0]["content"][0]["text"], "a banana")

    def test_remote_origin_refused(self):
        self.env["AGY_IMAGE_PROXY_URL"] = "https://example.invalid"
        self.assertNotEqual(self.run_image().returncode, 0)
        self.assertEqual(len(self.posts), 0)

    def test_redirect_refused(self):
        self.mode = "redirect"
        self.assertNotEqual(self.run_image().returncode, 0)
        self.assertEqual(len(self.posts), 0)

    def test_missing_model_refuses_downgrade(self):
        self.env["AGY_PROXY_IMAGE_MODEL"] = "gemini-nano-banana-2.1"
        self.assertNotEqual(self.run_image().returncode, 0)
        self.assertEqual(len(self.posts), 0)

    def test_wrong_provider_refused(self):
        self.mode = "wrong-owner"
        self.assertNotEqual(self.run_image().returncode, 0)
        self.assertEqual(len(self.posts), 0)

    def test_quota_no_retry_or_secret_log(self):
        self.mode = "quota"
        self.assertNotEqual(self.run_image().returncode, 0)
        self.assertEqual(len(self.posts), 1)
        self.assertFalse(self.out.exists())
        self.assertEqual(json.loads(self.out.with_suffix(".generation.json").read_text())["state"], "submitted_outcome_unknown")

    def test_remote_image_url_not_fetched(self):
        self.mode = "remote"
        self.assertNotEqual(self.run_image().returncode, 0)
        self.assertFalse(self.out.exists())

    def test_invalid_image_not_delivered(self):
        self.mode = "invalid"
        self.assertNotEqual(self.run_image().returncode, 0)
        self.assertFalse(self.out.exists())


if __name__ == "__main__":
    unittest.main()
