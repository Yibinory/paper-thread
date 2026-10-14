"""Exercise local and URL ingestion without using anyone's actual papers."""
from http.server import BaseHTTPRequestHandler
import json
from pathlib import Path
import tempfile
import threading
import unittest

from library import Library
from paper import LocalHTTPServer
from paper_sources import import_paper

PDF = b'%PDF-1.4\n% synthetic import fixture\n%%EOF\n'


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'reading project'
        self.root.mkdir()
        self.source = Path(self.tmp.name) / '本地论文.pdf'
        self.source.write_bytes(PDF)

    def tearDown(self):
        self.tmp.cleanup()

    def test_external_file_copied_and_identical_bytes_reused(self):
        first = import_paper(self.root, self.source)
        self.assertTrue(first['pdf'].startswith('data/papers/'))
        self.assertFalse(first['reused'])
        self.assertEqual((self.root / first['pdf']).read_bytes(), PDF)
        self.assertEqual(self.source.read_bytes(), PDF)
        another = self.source.with_name('另一种名字.pdf')
        another.write_bytes(PDF)
        second = import_paper(self.root, another)
        self.assertEqual(first['pdf'], second['pdf'])
        self.assertTrue(second['reused'])
        record = json.loads((self.root / first['provenance']).read_text(encoding='utf-8'))
        self.assertEqual(len(record['origins']), 2)

    def test_new_version_does_not_overwrite_previous_source(self):
        first = import_paper(self.root, self.source)
        self.source.write_bytes(PDF + b'% revised\n')
        second = import_paper(self.root, self.source)
        self.assertNotEqual(first['pdf'], second['pdf'])
        self.assertEqual((self.root / first['pdf']).read_bytes(), PDF)

    def test_non_pdf_and_oversized_inputs_leave_no_partial_files(self):
        for contents, limit, message in [(b'<html>login</html>', 1000, 'not a PDF'),
                                          (b'', 1000, 'empty'), (PDF, 4, 'size limit')]:
            with self.subTest(message=message):
                self.source.write_bytes(contents)
                with self.assertRaisesRegex(ValueError, message):
                    import_paper(self.root, self.source, max_bytes=limit)
                self.assertEqual(list(self.root.rglob('*.part')), [])
                self.assertEqual(list((self.root / 'data/papers').glob('*.pdf')), [])

    def test_corrupted_stored_file_is_not_silently_reused(self):
        result = import_paper(self.root, self.source)
        (self.root / result['pdf']).write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            import_paper(self.root, self.source)
        self.assertEqual(list(self.root.rglob('*.part')), [])

    def test_url_redirect_records_original_page_and_resolved_pdf(self):
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                if self.path == '/redirect':
                    self.send_response(302)
                    self.send_header('Location', '/paper.pdf')
                    self.end_headers()
                else:
                    body = PDF if self.path == '/paper.pdf' else b'<html>Paper abstract</html>'
                    self.send_response(200)
                    self.send_header('Content-Length', str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)

        with LocalHTTPServer(('127.0.0.1', 0), Handler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base = 'http://127.0.0.1:' + str(server.server_port)
                result = import_paper(self.root, base + '/redirect', base + '/abstract')
                self.assertEqual((self.root / result['pdf']).read_bytes(), PDF)
                self.assertEqual(result['source_url'], base + '/abstract')
                record = json.loads((self.root / result['provenance']).read_text(encoding='utf-8'))
                self.assertEqual(record['origins'][0]['download_url'], base + '/paper.pdf')
                with self.assertRaisesRegex(ValueError, 'not a PDF'):
                    import_paper(self.root, base + '/abstract')
            finally:
                server.shutdown()
                thread.join(timeout=5)

    def test_reports_accept_managed_sources_and_reject_escape_paths(self):
        imported = import_paper(self.root, self.source)
        library = Library(self.root)
        report = {'id': 'r-imported', 'kind': 'report', 'title': 'Import test', 'summary': 'Test',
                  'status': 'ready', 'sections': [{'id': 'main', 'title': 'Main', 'html': '<p>Fixture</p>'}],
                  'sources': [{'id': 'paper', 'title': 'Paper', 'url': imported['url'] + '#page=1'}],
                  'paper': {'pdf': imported['pdf'], 'sha256': imported['sha256'], 'pages': 1}}
        library.save(report)
        self.assertEqual(library.check(), [])
        for path in ('../本地论文.pdf', 'data/papers/../../../本地论文.pdf', str(self.source)):
            with self.subTest(path=path):
                report['paper']['pdf'] = path
                self.assertTrue(any('invalid PDF' in error for error in library.check({report['id']: report})))
        report['paper']['pdf'] = imported['pdf']
        report['sources'][0]['url'] = '/data/papers/../../../本地论文.pdf'
        self.assertTrue(any('local source' in error for error in library.check({report['id']: report})))


if __name__ == '__main__':
    unittest.main()
