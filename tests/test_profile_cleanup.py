"""Exercise isolated-profile cleanup with the repository painter stub only."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ProfileTests(unittest.TestCase):
    def verify(self, break_receipt):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            home = base / "home"
            login = home / ".gemini/antigravity-cli/antigravity-oauth-token"
            login.parent.mkdir(parents=True)
            login.write_text("fixture")
            if break_receipt:
                (base / "sample.prompt.txt").mkdir()
            env = dict(HOME=str(home), TMPDIR=tmp, PATH=os.defpath,
                       AGY_BIN=str(ROOT / "tests/stubs/agy"),
                       AGY_IMAGE_KEEP_WORKDIR="1")
            run = subprocess.run(["bash", str(ROOT / "bin/antigravity-image"),
                                  "fixture", str(base / "sample.jpg")],
                                 env=env,capture_output=True,timeout=30)
            self.assertEqual(run.returncode, 5 if break_receipt else 0, run.stderr)
            profiles = list(base.glob("antigravity-image.*/profile"))
            self.assertEqual(len(profiles), 1)
            self.assertFalse((profiles[0] / "antigravity-cli" / login.name).exists())
            self.assertTrue(login.is_file())

    def test_kept_success(self):
        self.verify(False)

    def test_failed_delivery(self):
        self.verify(True)
