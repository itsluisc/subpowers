import json
import os
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

MOD = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'bin/remote'))


class RemoteTests(unittest.TestCase):
    def test_embedded_programs_compile(self):
        for name in ('RUNNER','PREPARE','STATUS'):
            compile(MOD[name], name, 'exec')

    def test_runner_restores_missing_systemd_home(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            door = p/'fake-subpowers'
            door.write_text('#!/usr/bin/env python3\nimport os,pathlib,sys\np=pathlib.Path(sys.argv[3]); p.write_bytes(b"\\x89PNG\\r\\n\\x1a\\n"+b"x"*60); p.with_suffix(".prompt.txt").write_text("test receipt"); p.with_suffix(".home").write_text(os.environ["HOME"])\n')
            door.chmod(0o700)
            (p/'input.json').write_text(json.dumps(dict(door=str(door),prompt='a banana',painter='chatgpt')))
            runner = p/'runner.py'; runner.write_text(MOD['RUNNER'])
            env = dict(os.environ); env.pop('HOME',None)
            r = subprocess.run(['python3',str(runner),str(p)],env=env,capture_output=True,timeout=10)
            self.assertEqual(r.returncode,0)
            status = json.loads((p/'status.json').read_text())
            self.assertEqual(status['state'],'delivered')
            self.assertEqual(len(status['sha256']),64)
            self.assertTrue((p/'image.home').read_text().startswith('/'))

    def test_runner_declines_stdout_jpeg(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            door = p / 'fake-subpowers'
            door.write_text(
                '#!/usr/bin/env python3\n'
                'import pathlib, sys\n'
                'requested = pathlib.Path(sys.argv[3])\n'
                'jpg = requested.with_suffix(".jpg")\n'
                'jpg.write_bytes(b"\\xff\\xd8\\xff" + b"x" * 60)\n'
                'jpg.with_suffix(".prompt.txt").write_text("jpg receipt")\n'
                'print(jpg)\n'
            )
            door.chmod(0o700)
            (p / 'input.json').write_text(json.dumps(dict(door=str(door), prompt='a banana', painter='antigravity')))
            runner = p / 'runner.py'
            runner.write_text(MOD['RUNNER'])
            r = subprocess.run(['python3', str(runner), str(p)], capture_output=True, timeout=10)
            self.assertEqual(r.returncode, 0, r.stderr)
            status = json.loads((p / 'status.json').read_text())
            self.assertEqual(status['state'], 'failed')
            self.assertIsNone(status['output'])
            self.assertFalse((p / 'image.png').exists())

    def test_runner_ignores_path_outside_job(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / 'job'
            p.mkdir()
            outside = root / 'image.jpg'
            outside.write_bytes(b'\xff\xd8\xff' + b'y' * 60)
            door = p / 'fake-subpowers'
            door.write_text(
                '#!/usr/bin/env python3\n'
                'import os\n'
                'print(os.environ["OUTSIDE"])\n'
            )
            door.chmod(0o700)
            (p / 'input.json').write_text(json.dumps(dict(door=str(door), prompt='a banana', painter='grok')))
            runner = p / 'runner.py'
            runner.write_text(MOD['RUNNER'])
            env = dict(os.environ, OUTSIDE=str(outside))
            subprocess.run(['python3', str(runner), str(p)], env=env, check=True, timeout=10)
            status = json.loads((p / 'status.json').read_text())
            self.assertEqual(status['state'], 'failed')
            self.assertIsNone(status['output'])

    def test_fetch_validates_exact_png_job_path(self):
        job = "a" * 32
        root = f"/home/test/.subpowers/jobs/{job}"
        validate = MOD["validate_remote_png"]
        validate(f"{root}/image.png", job)
        for path in (f"{root}/image.jpg", f"{root}/../{job}/image.png",
                     f"/tmp/{job}/image.png", root.replace(job, "b" * 32) + "/image.png"):
            with self.subTest(path=path), self.assertRaises(RuntimeError):
                validate(path, job)

    def test_failure_not_delivered(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); (p/'input.json').write_text(json.dumps(dict(door='/usr/bin/false',prompt='test',painter='chatgpt')))
            runner=p/'runner.py'; runner.write_text(MOD['RUNNER'])
            subprocess.run(['python3',str(runner),str(p)],check=True,timeout=10)
            self.assertEqual(json.loads((p/'status.json').read_text())['state'],'failed')


if __name__=='__main__': unittest.main()


class OfflineFetch(unittest.TestCase):
    def setUp(self):
        import hashlib
        from unittest.mock import patch

        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dest = Path(tmp.name) / "result.png"
        self.jpg = self.dest.with_suffix(".jpg")
        self.raw = b"\xff\xd8\xff" + b"q" * 80
        job = "a" * 32
        self.status = dict(state="delivered", output=f"/home/test/.subpowers/jobs/{job}/image.jpg",
                           sha256=hashlib.sha256(self.raw).hexdigest())
        self.args = ["remote", "stub", "fetch", job]
        stub = patch.dict(MOD["main"].__globals__, ssh=lambda *args: dict(self.status))
        stub.start()
        self.addCleanup(stub.stop)

    def fetch(self, path, *args, before_copy=None):
        from contextlib import redirect_stdout
        from unittest.mock import patch
        import io

        def copy_stub(cmd, **kwargs):
            if before_copy:
                before_copy()
            Path(cmd[-1]).write_bytes(b"receipt" if cmd[-2].endswith(".txt") else self.raw)
        with patch("sys.argv", [*self.args, str(path), *args]), \
             patch("subprocess.run", side_effect=copy_stub), redirect_stdout(io.StringIO()):
            MOD["main"]()

    def test_jpeg_is_rejected_before_any_copy(self):
        from unittest.mock import Mock

        prompt = self.dest.with_suffix(".prompt.txt")
        meta = self.dest.with_suffix(".remote.json")
        for path in (self.dest, prompt, meta):
            path.write_bytes(b"original")
        for output in (self.dest, self.jpg):
            with self.subTest(output=output.name):
                copied = Mock()
                with self.assertRaises(RuntimeError):
                    self.fetch(output, before_copy=copied)
                copied.assert_not_called()
                self.assertFalse(self.jpg.exists())
                for path in (self.dest, prompt, meta):
                    self.assertEqual(path.read_bytes(), b"original")

    def use_png(self):
        import hashlib
        self.raw = b"\x89PNG\r\n\x1a\n" + b"x" * 80
        self.status.update(output=self.status["output"][:-3] + "png",
                           sha256=hashlib.sha256(self.raw).hexdigest())

    def test_verified_png_still_delivers_both_receipts(self):
        self.use_png()
        self.fetch(self.dest)
        self.assertEqual(self.dest.read_bytes(), self.raw)
        self.assertEqual(self.dest.with_suffix(".prompt.txt").read_bytes(), b"receipt")
        meta = json.loads(self.dest.with_suffix(".remote.json").read_text())
        self.assertEqual(meta["local_sha256"], self.status["sha256"])
        self.assertTrue(meta["digest_match"])

    def test_bad_digest_preserves_png(self):
        self.use_png()
        self.dest.write_bytes(b"previous")
        self.status["sha256"] = "0" * 64
        with self.assertRaisesRegex(RuntimeError, "digest mismatch"):
            self.fetch(self.dest)
        self.assertEqual(self.dest.read_bytes(), b"previous")

    def test_status_rejects_receipt_link_leaving_job(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve()
            job = "a" * 32
            root = home/".subpowers/jobs"/job
            root.mkdir(parents=True)
            img = root/"image.png"
            img.write_bytes(b"fixture")
            other = home/"outside"
            other.write_text("fixture")
            (root/"image.prompt.txt").symlink_to(other)
            (root/"status.json").write_text(json.dumps(dict(state="delivered",output=str(img))))
            run = subprocess.run(["python3","-c",MOD["STATUS"],job],env=dict(os.environ,HOME=str(home)),
                                 capture_output=True,text=True,check=True)
            self.assertEqual(json.loads(run.stdout)["state"],"failed")
