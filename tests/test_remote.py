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

    def test_failure_not_delivered(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); (p/'input.json').write_text(json.dumps(dict(door='/usr/bin/false',prompt='test',painter='chatgpt')))
            runner=p/'runner.py'; runner.write_text(MOD['RUNNER'])
            subprocess.run(['python3',str(runner),str(p)],check=True,timeout=10)
            self.assertEqual(json.loads((p/'status.json').read_text())['state'],'failed')


if __name__=='__main__': unittest.main()
