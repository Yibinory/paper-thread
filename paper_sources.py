"""Store agent-resolved PDFs without requiring a user-managed input folder."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from library import PDF_DIRECTORIES, write_json


def import_paper(root, source, source_url=None, max_bytes=100 * 1024 * 1024):
    """Import a local file or direct HTTP(S) PDF; landing pages are resolved by the agent."""
    root = Path(root)
    source = str(source)
    remote = source.startswith(('https://', 'http://'))
    if source_url and urlsplit(source_url).scheme not in ('http', 'https'):
        raise ValueError('source-url must be an HTTP(S) paper page or PDF URL')
    if max_bytes <= 0:
        raise ValueError('max-mb must be positive')
    imports = root / '.local/imports'
    imports.mkdir(parents=True, exist_ok=True)
    origin = {'source': source if remote else str(Path(source).expanduser().resolve())}
    if source_url or remote:
        origin['source_url'] = source_url or source
    if remote:
        stream = urlopen(Request(source, headers={'User-Agent': 'PaperThread/1.0'}), timeout=30)
        origin['download_url'] = stream.geturl()
    else:
        stream = Path(source).expanduser().open('rb')
    temporary = None
    try:
        with stream, tempfile.NamedTemporaryFile(dir=imports, suffix='.part', delete=False) as output:
            temporary = Path(output.name)
            digest = hashlib.sha256()
            size = 0
            prefix = b''
            while chunk := stream.read(1024 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    raise ValueError('PDF exceeds the import size limit; increase --max-mb if needed')
                if not prefix:
                    prefix = chunk[:1024]
                    if not prefix.lstrip(b'\xef\xbb\xbf \r\n\t').startswith(b'%PDF-'):
                        raise ValueError('Source is not a PDF. For a paper page, the agent must locate its PDF link first.')
                digest.update(chunk)
                output.write(chunk)
            if not size:
                raise ValueError('Source is empty; no PDF was imported')
        sha256 = digest.hexdigest()
        relative = f'{PDF_DIRECTORIES[0]}/{sha256}.pdf'
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        reused = target.exists()
        if reused:
            existing = hashlib.sha256()
            with target.open('rb') as saved:
                while chunk := saved.read(1024 * 1024):
                    existing.update(chunk)
            if existing.hexdigest() != sha256:
                raise ValueError('Stored PDF checksum mismatch; inspect ' + relative)
        else:
            temporary.replace(target)
        record_path = imports / (sha256 + '.json')
        record = json.loads(record_path.read_text(encoding='utf-8')) if record_path.exists() else {
            'pdf': relative, 'sha256': sha256, 'bytes': size, 'origins': []}
        if origin not in record['origins']:
            record['origins'].append(origin)
        record['last_imported_at'] = datetime.now(timezone.utc).isoformat()
        write_json(record_path, record)
        return {'pdf': relative, 'url': '/' + relative, 'sha256': sha256,
                'bytes': size, 'reused': reused,
                'source_url': origin.get('source_url'),
                'provenance': record_path.relative_to(root).as_posix()}
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
