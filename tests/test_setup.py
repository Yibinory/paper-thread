"""Check first-run behavior with an empty library and copied skill installations."""
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.request import ProxyHandler, build_opener

from library import Library, write_json
from scripts.install_skills import NAMES, install

ROOT = Path(__file__).resolve().parents[1]


class SkillInstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / '文脉 with spaces'
        shutil.copytree(ROOT / 'skills', self.root / 'skills')
        self.destination = self.root / '.agents' / 'skills'

    def tearDown(self):
        self.tmp.cleanup()

    def test_copy_install_and_idempotency(self):
        self.assertIsNone(install(self.root, self.destination))
        for name in NAMES:
            target = self.destination / name
            self.assertFalse(target.is_symlink())
            self.assertEqual((target / 'SKILL.md').read_bytes(),
                             (self.root / 'skills' / name / 'SKILL.md').read_bytes())
            self.assertTrue(any((target / 'references').glob('*.md')))
        self.assertIsNone(install(self.root, self.destination))

    def test_collision_preflight_and_backup(self):
        # A collision in the second skill must not partially install the first.
        modified = self.destination / NAMES[1]
        modified.mkdir(parents=True)
        (modified / 'SKILL.md').write_text('自己的修改', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Already exists'):
            install(self.root, self.destination)
        self.assertFalse((self.destination / NAMES[0]).exists())
        backup = install(self.root, self.destination, update=True)
        self.assertEqual((backup / NAMES[1] / 'SKILL.md').read_text(encoding='utf-8'), '自己的修改')


class FreshCheckoutTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / '文脉 with spaces'
        self.root.mkdir()
        for name in ('paper.py', 'library.py', 'interactions.py', 'run.bat', 'run.command'):
            shutil.copy2(ROOT / name, self.root / name)
        shutil.copytree(ROOT / 'scripts', self.root / 'scripts', ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(ROOT / 'web', self.root / 'web', ignore=shutil.ignore_patterns('bundle.js'))

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_check_build_export(self):
        for arguments in (['check'], ['build'], ['export']):
            result = subprocess.run([sys.executable, 'paper.py', *arguments], cwd=self.root,
                                    capture_output=True, encoding='utf-8', timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            json.loads(result.stdout)
        self.assertTrue((self.root / 'output/offline-reader.zip').is_file())
        self.assertEqual(Library(self.root).catalog(), [])

    def test_json_is_stored_as_utf8(self):
        write_json(self.root / '文脉.json', {'title': '知识介绍：测量 α → β'})
        # The bytes on disk must be UTF-8, independent of the host default encoding.
        self.assertEqual(json.loads((self.root / '文脉.json').read_bytes())['title'], '知识介绍：测量 α → β')

    def test_native_launcher_serves_empty_site(self):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        if os.name == 'nt':
            command = [os.environ.get('COMSPEC', 'cmd.exe'), '/d', '/c', 'run.bat', '--port', str(port)]
        else:
            command = ['sh', str(self.root / 'run.command'), '--port', str(port)]
        env = {**os.environ, 'PAPERTHREAD_NO_PAUSE': '1',
               'PATH': str(Path(sys.executable).parent) + os.pathsep + os.environ.get('PATH', '')}
        opener = build_opener(ProxyHandler({}))
        base = 'http://127.0.0.1:' + str(port)
        with tempfile.TemporaryFile() as log:
            process = subprocess.Popen(command, cwd=self.root, env=env, stdout=log, stderr=log)
            try:
                deadline = time.monotonic() + 20
                while time.monotonic() < deadline and process.poll() is None:
                    try:
                        with opener.open(base + '/api/catalog', timeout=1) as response:
                            catalog = json.load(response)
                        break
                    except OSError:
                        time.sleep(0.1)
                else:
                    log.seek(0)
                    self.fail('Launcher failed: ' + log.read().decode('utf-8', errors='replace'))
                self.assertEqual(catalog, {'documents': [], 'reader': {}})
                with opener.open(base) as response:
                    self.assertIn('文脉 · PaperThread', response.read().decode('utf-8'))
                with opener.open(base + '/bundle.js') as response:
                    self.assertIn('"documents": {}', response.read().decode('utf-8'))
            finally:
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True)
                else:
                    process.terminate()
                process.wait(timeout=10)


if __name__ == '__main__':
    unittest.main()
