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

    def test_runner_honors_stdout_jpeg(self):
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
            self.assertEqual(status['state'], 'delivered')
            self.assertTrue(status['output'].endswith('/image.jpg'))
            self.assertFalse((p / 'image.png').exists())
            self.assertEqual(len(status['sha256']), 64)

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

    def test_fetch_accepts_real_extension(self):
        job = 'a' * 32
        name, ext = MOD['remote_image_path']('/home/u/.subpowers/jobs/%s/image.jpg' % job, job)
        self.assertEqual((name, ext), ('image.jpg', 'jpg'))
        dest = MOD['fetch_destination'](Path('/tmp/banana.png'), 'jpg')
        self.assertEqual(dest.name, 'banana.jpg')
        same = MOD['fetch_destination'](Path('/tmp/banana.jpg'), 'jpg')
        self.assertEqual(same.name, 'banana.jpg')
        self.assertTrue(MOD['image_bytes_match'](b'\xff\xd8\xff' + b'x' * 40, 'jpg'))
        self.assertFalse(MOD['image_bytes_match'](b'\x89PNG\r\n\x1a\n' + b'x' * 40, 'jpg'))
        with self.assertRaises(RuntimeError):
            MOD['remote_image_path']('/tmp/%s/../../etc/image.jpg' % job, job)
        with self.assertRaises(RuntimeError):
            MOD['remote_image_path']('/home/u/.subpowers/jobs/%s/image.png' % job, 'b' * 32)

    def test_failure_not_delivered(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); (p/'input.json').write_text(json.dumps(dict(door='/usr/bin/false',prompt='test',painter='chatgpt')))
            runner=p/'runner.py'; runner.write_text(MOD['RUNNER'])
            subprocess.run(['python3',str(runner),str(p)],check=True,timeout=10)
            self.assertEqual(json.loads((p/'status.json').read_text())['state'],'failed')


if __name__=='__main__': unittest.main()
