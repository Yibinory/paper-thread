"""Local, file-first knowledge store. CLI and HTTP server share this implementation."""
from __future__ import annotations
import collections
from contextlib import contextmanager
import hashlib
from html.parser import HTMLParser
from interactions import validate_interactives
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import threading
import time
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
PDF_DIRECTORIES = ('data/papers', 'test_paper')
ID_RE = re.compile(r'^[a-z][a-z0-9-]{1,79}$')


def is_local_paper(root, relative):
    if not relative or Path(relative).is_absolute():
        return False
    target = (Path(root) / relative).resolve()
    return target.is_file() and any(
        target.is_relative_to((Path(root) / directory).resolve())
        for directory in PDF_DIRECTORIES)


class TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def handle_endtag(self, tag):
        self.parts.append(' ')


def plain(value):
    parser = TextParser()
    parser.feed(str(value))
    parser.close()
    return ''.join(parser.parts)


def digest(doc):
    clean = {k: v for k, v in doc.items() if k != 'revision'}
    return hashlib.sha256(json.dumps(clean, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temp, path)


class BodyParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.images, self.errors = [], [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        allowed = {'p','ul','ol','li','strong','b','i','em','blockquote','table','thead','tbody','tfoot','tr','th','td','figure','img','figcaption','details','summary','code','pre','div','span','h3','h4','a','br','hr','sub','sup','small','dl','dt','dd'}
        if tag not in allowed:
            self.errors.append('Disallowed HTML tag: ' + tag)
        for key, value in attrs:
            if key.startswith('on') or key in ('style', 'srcdoc'):
                self.errors.append('Disallowed HTML attribute: ' + key)
            if key in ('href', 'src') and value and not re.match(r'^(https?://|/data/figures/|#)', value):
                self.errors.append('Invalid URL: ' + value)
        if tag == 'a':
            self.links.append(a)
        if tag == 'img':
            self.images.append(a.get('src', ''))


def bodies(doc):
    parser = BodyParser()
    for section in doc.get('sections', []):
        parser.feed(section.get('html', ''))
    return parser


class Library:
    def __init__(self, root=ROOT):
        self.root = Path(root)
        self.data = self.root / 'data'
        self.local = self.root / '.local'
        self.local.mkdir(exist_ok=True)
        for directory in ('data/reports', 'data/concepts', 'data/figures', 'data/reviews', 'data/revisions', 'data/papers'):
            (self.root / directory).mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.reload()
        with self.db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS reader (id TEXT PRIMARY KEY, state TEXT, note TEXT, updated REAL)')

    @contextmanager
    def db(self):
        connection = sqlite3.connect(self.local / 'reader.sqlite3')
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def reload(self):
        self.docs = {}
        self.paths = {}
        for kind in ('concepts', 'reports'):
            for path in sorted((self.data / kind).glob('*.json')):
                doc = json.loads(path.read_text(encoding='utf-8'))
                if doc['id'] in self.docs:
                    raise ValueError('Duplicate ID: ' + doc['id'])
                doc['revision'] = digest(doc)
                self.docs[doc['id']] = doc
                self.paths[doc['id']] = path

    def get(self, ident, revision=None):
        if not ID_RE.fullmatch(ident):
            raise KeyError(ident)
        if revision:
            if not re.fullmatch('[a-f0-9]{16}', revision):
                raise ValueError('Invalid revision')
            path = self.data / 'revisions' / ident / (revision + '.json')
            if path.exists():
                return json.loads(path.read_text(encoding='utf-8'))
            if ident in self.docs and self.docs[ident]['revision'] == revision:
                return self.docs[ident]
            # An old ID may now redirect; new references to it pin the canonical page.
            seen = {ident}
            cur = self.docs.get(ident, {}).get('redirect')
            while cur and cur not in seen:
                seen.add(cur)
                candidate = self.data / 'revisions' / cur / (revision + '.json')
                if candidate.exists():
                    return json.loads(candidate.read_text(encoding='utf-8'))
                if self.docs.get(cur, {}).get('revision') == revision:
                    return self.docs[cur]
                cur = self.docs.get(cur, {}).get('redirect')
            raise KeyError('Revision not found: ' + revision)
        seen = set()
        while self.docs[ident].get('redirect'):
            if ident in seen:
                raise ValueError('Redirect cycle')
            seen.add(ident)
            ident = self.docs[ident]['redirect']
        return self.docs[ident]

    def card(self, doc):
        keys = ('id','kind','title','subtitle','summary','domain','tags','aliases','scope','not_this','status','revision','reading_minutes','paper','contributions')
        c = {k: doc[k] for k in keys if k in doc}
        c['url'] = '/#/' + doc['kind'] + '/' + doc['id']
        c['sections'] = [{'id': s['id'], 'title': s['title']} for s in doc.get('sections', [])]
        return c

    def catalog(self, kind=None):
        return [self.card(d) for d in self.docs.values() if not d.get('redirect') and d.get('status') == 'ready' and (not kind or d['kind'] == kind)]

    def inventory(self, kind='concept', domain='', offset=0, limit=50):
        """Compact, pageable definitions for the authoring agent to judge meaning."""
        if offset < 0 or not 1 <= limit <= 200:
            raise ValueError('offset must be nonnegative; limit must be 1–200')
        cards = self.catalog(kind)
        domains = sorted({c['domain'] for c in cards if c.get('domain')})
        if domain:
            cards = [c for c in cards if domain.casefold() in c.get('domain','').casefold()]
        keys = ('id','title','summary','domain','aliases','scope','not_this','revision','sections')
        page = [{k:c[k] for k in keys if k in c} for c in cards[offset:offset+limit]]
        return {'entries':page, 'total':len(cards), 'offset':offset,
                'next_offset':offset+limit if offset+limit < len(cards) else None,
                'domains':domains, 'notice':'目录不按相似度排除条目；概念身份由调用 agent 根据定义和本文用法判断。'}

    def references(self, doc):
        return [a for a in bodies(doc).links if a.get('data-concept')]

    def check(self, docs=None):
        docs = self.docs if docs is None else docs
        errors = []
        for ident, doc in docs.items():
            def err(message):
                errors.append(ident + ': ' + message)
            if not ID_RE.fullmatch(ident):
                err('Invalid document ID')
            if doc.get('redirect'):
                seen, cur = set(), ident
                while docs.get(cur, {}).get('redirect'):
                    if cur in seen:
                        err('Redirect cycle'); break
                    seen.add(cur); cur = docs[cur]['redirect']
                if cur not in docs:
                    err('Missing redirect target')
                continue
            for key in ('title','summary','kind','sections','sources','status'):
                if not doc.get(key):
                    err('Missing ' + key)
            if doc.get('kind') not in ('concept','report') or doc.get('status') not in ('draft','ready'):
                err('Invalid kind or status')
            if doc.get('kind') == 'concept':
                for key in ('aliases','scope','not_this','semantic_terms','prerequisites'):
                    if key not in doc:
                        err('Missing concept field ' + key)
            section_ids = [s.get('id') for s in doc.get('sections', [])]
            if len(section_ids) != len(set(section_ids)) or any(not isinstance(s, str) or not ID_RE.fullmatch(s) for s in section_ids):
                err('Invalid or duplicate section ID')
            for error in validate_interactives(doc):
                err(error)
            parser = bodies(doc)
            for error in parser.errors:
                err(error)
            source_ids = {s['id'] for s in doc.get('sources', [])}
            for source in doc.get('sources', []):
                url = source.get('url','')
                local_url = any(url.startswith('/' + directory + '/') for directory in PDF_DIRECTORIES)
                if not re.match(r'^https?://', url) and not local_url:
                    err('Invalid source URL ' + url)
                elif local_url:
                    if not is_local_paper(self.root, unquote(urlsplit(url).path).lstrip('/')):
                        err('Missing/invalid local source ' + url)
            for ref in parser.links:
                target = ref.get('data-concept')
                if target:
                    if target not in docs or docs[target].get('kind') != 'concept':
                        err('Unknown concept ' + target); continue
                    td = docs[target]
                    visited = set()
                    while td.get('redirect') and td['id'] not in visited:
                        visited.add(td['id']); td = docs.get(td['redirect'], {})
                    # Reports retain the exact concept content used when authored.
                    rev = doc.get('references', {}).get(target)
                    if rev:
                        try:
                            td = self.get(target, rev)
                        except (KeyError, ValueError):
                            err('Missing pinned revision ' + target)
                    if doc.get('status') == 'ready' and td.get('status') != 'ready':
                        err('Ready document links to draft ' + target)
                    if ref.get('data-section') and ref['data-section'] not in {s['id'] for s in td.get('sections', [])}:
                        err('Missing section in ' + target + ': ' + ref['data-section'])
                sid = ref.get('data-source')
                if sid and not (sid == 'paper' and doc.get('paper')) and sid not in source_ids:
                    err('Unknown source ' + sid)
                page = ref.get('data-page')
                if sid == 'paper' and page and (not page.isdigit() or not 1 <= int(page) <= doc.get('paper',{}).get('pages',0)):
                    err('Invalid PDF page ' + str(page))
            for image in parser.images:
                if image.startswith('/data/figures/'):
                    target = (self.root / image.lstrip('/')).resolve()
                    if not target.is_relative_to((self.root / 'data/figures').resolve()) or not target.is_file():
                        err('Missing/invalid image ' + image)
            if doc.get('paper'):
                if not is_local_paper(self.root, doc['paper'].get('pdf','')):
                    err('Missing/invalid PDF')
            for dep in doc.get('prerequisites', []):
                if dep not in docs or docs[dep].get('kind') != 'concept':
                    err('Unknown prerequisite ' + dep)
        visited, active = set(), set()
        def visit(ident):
            if ident in active:
                errors.append('Prerequisite cycle: ' + ident); return
            if ident in visited:
                return
            active.add(ident)
            for dep in docs.get(ident, {}).get('prerequisites', []):
                visit(dep)
            active.remove(ident); visited.add(ident)
        for ident in docs:
            visit(ident)
        return errors

    def snapshot(self, doc):
        doc = dict(doc, revision=digest(doc))
        path = self.data / 'revisions' / doc['id'] / (doc['revision'] + '.json')
        if not path.exists():
            write_json(path, doc)
        return doc['revision']

    def pin(self, refresh=False):
        with self.lock:
            errors = self.check()
            if errors:
                raise ValueError('\n'.join(errors))
            for doc in self.docs.values():
                self.snapshot(doc)
            updates = {}
            for source_doc in self.docs.values():
                doc = json.loads(json.dumps(source_doc))
                if doc.get('kind') != 'report':
                    continue
                refs = {} if refresh else doc.setdefault('references', {})
                pending = [a['data-concept'] for a in self.references(doc)]
                visited = set()
                while pending:
                    key = pending.pop()
                    if key in visited:
                        continue
                    visited.add(key)
                    if refresh or key not in refs:
                        refs[key] = self.get(key)['revision']
                    pinned = self.get(key, refs[key])
                    pending.extend(a['data-concept'] for a in self.references(pinned))
                    pending.extend(pinned.get('prerequisites', []))
                doc['references'] = {k: v for k, v in refs.items() if k in visited}
                updates[doc['id']] = doc
            errors = self.check(dict(self.docs, **updates))
            if errors:
                raise ValueError('\n'.join(errors))
            for ident, doc in updates.items():
                doc['revision'] = self.snapshot(doc)
                write_json(self.paths[ident], doc)
            self.reload()

    def save(self, doc, expected=None):
        with self.lock:
            doc = dict(doc)
            doc.pop('previous_revision', None)  # Retire legacy report-comparison metadata.
            ident = doc.get('id','')
            if not ID_RE.fullmatch(ident):
                raise ValueError('Invalid ID')
            old = self.docs.get(ident)
            if old and expected != old['revision']:
                raise ValueError('Revision conflict: read the latest document before saving')
            if old and old['kind'] != doc.get('kind'):
                raise ValueError('Document kind is immutable')
            candidate = dict(self.docs, **{ident: doc})
            errors = self.check(candidate)
            if errors:
                raise ValueError('\n'.join(errors))
            if old:
                self.snapshot(old)
            doc = dict(doc, revision=digest(doc))
            self.snapshot(doc)
            folder = 'concepts' if doc['kind'] == 'concept' else 'reports'
            write_json(self.data / folder / (ident + '.json'), doc)
            self.reload()
            return self.card(doc)

    def add_alias(self, ident, alias, expected):
        if not alias.strip() or len(alias) > 160:
            raise ValueError('Alias must be 1–160 characters')
        doc = json.loads(json.dumps(self.get(ident)))
        if doc['kind'] != 'concept':
            raise ValueError('Aliases are for concepts')
        if alias.strip() not in doc['aliases']:
            doc['aliases'].append(alias.strip())
        return self.save(doc, expected)

    def merge(self, source, target, expected_source, expected_target):
        with self.lock:
            if source == target:
                raise ValueError('Cannot merge into itself')
            s, t = self.get(source), json.loads(json.dumps(self.get(target)))
            if s['kind'] != 'concept' or t['kind'] != 'concept' or s['id'] != source or t['id'] != target:
                raise ValueError('Merge requires two canonical concepts')
            if s['revision'] != expected_source or t['revision'] != expected_target:
                raise ValueError('Revision conflict')
            # Reviewers must reconcile content first; merge only establishes identity.
            t['aliases'] = list(dict.fromkeys(t['aliases'] + [s['title']] + s['aliases']))
            redirected = dict(s, redirect=target)
            updates = {target: t, source: redirected}
            for key, d in self.docs.items():
                if key not in updates and source in d.get('prerequisites', []):
                    updates[key] = dict(d, prerequisites=[target if x == source else x for x in d['prerequisites']])
            errors = self.check(dict(self.docs, **updates))
            if errors:
                raise ValueError('\n'.join(errors))
            for key, doc in updates.items():
                self.snapshot(self.docs[key]); self.snapshot(doc)
                write_json(self.paths[key], doc)
            self.reload()
            return self.card(self.get(target))

    @staticmethod
    def tokens(text):
        text = text.lower()
        terms = re.findall(r'[a-z0-9]+', text)
        for run in re.findall(r'[\u3400-\u9fff]+', text):
            terms += [run[i:i+2] for i in range(len(run)-1)] or [run]
        return collections.Counter(terms)

    def search_text(self, doc):
        return '\n'.join([doc['title'], *doc.get('aliases', []), doc.get('summary',''), doc.get('scope',''), *doc.get('semantic_terms', []), *[plain(s['title'] + ' ' + s['html']) for s in doc.get('sections', [])]])

    def search(self, query, context='', kind=None, limit=8):
        query = query.strip()
        if not query and not context:
            return {'results':[], 'retrieval':'lexical'}
        candidates = {k:d for k,d in self.docs.items() if not d.get('redirect') and d.get('status') == 'ready' and (not kind or d['kind']==kind)}
        qtokens = self.tokens(query + ' ' + context)
        score, reason, section = collections.defaultdict(float), collections.defaultdict(list), {}
        for ident,d in candidates.items():
            text = self.search_text(d)
            tokens = self.tokens(text)
            shared = sum(min(n, tokens[t]) for t,n in qtokens.items())
            if shared:
                score[ident] += 0.24 * shared / max(sum(qtokens.values()), 1)
                reason[ident].append('内容关键词')
            names = [d['title'],*d.get('aliases',[])]
            if query.casefold() in [x.casefold() for x in names]:
                score[ident] += 1.5; reason[ident].append('名称或别名一致，仍需核对语境')
            elif len(query) >= 2 and any(query.casefold() in n.casefold() or (len(n)>2 and n.casefold() in query.casefold()) for n in names):
                score[ident] += 0.45; reason[ident].append('名称相关')
        results = []
        for ident in sorted(score, key=score.get, reverse=True)[:limit]:
            c = self.card(candidates[ident])
            c.update(score=round(score[ident],4), reasons=reason[ident], suggested_section=section.get(ident))
            results.append(c)
        return {'results':results, 'retrieval':'lexical', 'notice':'名称与关键词候选，不判断同义。调用 agent 应结合 inventory 目录和 get 正文核对定义；无匹配不代表知识不存在。'}

    def backlinks(self, ident):
        target = self.get(ident)['id']
        equivalent = {key for key in self.docs if self.get(key)['id'] == target}
        return [{'id':d['id'],'title':d['title'],'kind':d['kind'],'sections':[s['id'] for s in d.get('sections',[]) if any(a.get('data-concept') in equivalent for a in bodies({'sections':[s]}).links)]} for d in self.docs.values() if not d.get('redirect') and any(a['data-concept'] in equivalent for a in self.references(d))]

    def reader(self, ident=None, state=None, note=None):
        with self.db() as db:
            if ident is not None and (state is not None or note is not None):
                if ident not in self.docs:
                    raise KeyError(ident)
                old = db.execute('SELECT state,note FROM reader WHERE id=?',(ident,)).fetchone() or ('unread','')
                state = old[0] if state is None else state
                note = old[1] if note is None else note
                if state not in ('unread','reading','known','confused','done') or len(note)>50000:
                    raise ValueError('Invalid reader data')
                db.execute('INSERT OR REPLACE INTO reader VALUES (?,?,?,?)',(ident,state,note,time.time()))
            return {r[0]:{'state':r[1],'note':r[2],'updated':r[3]} for r in db.execute('SELECT * FROM reader')}
