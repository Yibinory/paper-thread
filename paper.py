#!/usr/bin/env python3
"""PaperThread command-line tool and loopback-only HTTP application."""
import argparse
import copy
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import shutil
import sys
from pathlib import Path
from socketserver import TCPServer
from urllib.parse import parse_qs, unquote, urlsplit
import zipfile
from library import Library, ROOT, PDF_DIRECTORIES, digest, write_json
from paper_sources import import_paper


class LocalHTTPServer(ThreadingHTTPServer):
    def server_bind(self):
        # This server only binds loopback; reverse DNS adds no useful information
        # and can stall startup on machines with slow hostname resolution.
        TCPServer.server_bind(self)
        self.server_name = 'localhost'
        self.server_port = self.server_address[1]


def bundle(lib):
    revisions = {}
    pending = list(lib.docs.values())
    for d in pending:
        for ident, rev in d.get('references', {}).items():
            key = ident + '@' + rev
            if key not in revisions:
                old = lib.get(ident, rev)
                revisions[key] = old
                pending.append(old)
    return {'documents':lib.docs,'revisions':revisions,'reader':lib.reader()}


def build(lib):
    errors = lib.check()
    if errors:
        raise ValueError('\n'.join(errors))
    lib.pin()
    content = 'window.READER_BUNDLE=' + json.dumps(bundle(lib),ensure_ascii=False).replace('</','<\\/') + ';\n'
    (ROOT / 'web/bundle.js').write_text(content, encoding='utf-8')
    return {'reports':sum(d['kind']=='report' for d in lib.docs.values()),'concepts':sum(d['kind']=='concept' for d in lib.docs.values()),'validation':'passed'}


def review_pack(lib, ident, destination, draft=None):
    """Export only the reading experience, without source PDFs or author notes."""
    doc = copy.deepcopy(draft if draft is not None else lib.get(ident))
    if doc.get('id') != ident:
        raise ValueError('Draft ID must match the requested document')
    doc['revision'] = digest(doc)
    target = Path(destination).resolve()
    target.mkdir(parents=True, exist_ok=True)
    is_concept = doc.get('kind') == 'concept'
    entry = 'concept.json' if is_concept else 'report.json'
    pinned = doc.get('references', {})
    knowledge, pending = {}, [a['data-concept'] for a in lib.references(doc)]
    def reading_copy(d):
        # Bibliographic titles remain, but no paths to the paper or review history.
        clean = {k:copy.deepcopy(d[k]) for k in ('id','kind','title','subtitle','summary','sections','interactives','revision') if k in d}
        clean['sources'] = [{'id':s['id'],'title':s['title']} for s in d.get('sources',[])]
        for section in clean.get('sections',[]):
            for src in bodies_for_images(section):
                relative = Path(src.lstrip('/'))
                source = (lib.root / relative).resolve()
                if not source.is_relative_to((lib.root/'data/figures').resolve()):
                    raise ValueError('Review figures must be local report figures')
                output = target / relative
                output.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, output)
        return clean
    while pending:
        key = pending.pop()
        if key == ident or key in knowledge:
            continue
        concept = lib.get(key, pinned.get(key))
        knowledge[key] = reading_copy(concept)
        pending.extend(a['data-concept'] for a in lib.references(concept))
    write_json(target/entry, reading_copy(doc))
    write_json(target/'knowledge.json', knowledge)
    instructions = (
        '交互配置也是报告的一部分：检查可改变的状态、显示值、推导与文字后备说明。\n'
        '只阅读 report.json、knowledge.json 和包内配图；不要打开原论文、外部来源、作者笔记或历史评审。\n'
        '你是尚未读过这篇论文、可能第一次接触该领域的读者。不要用记忆补全正文。\n'
        '先顺序阅读：在进入新部分时，先依据前文记录已建立的认识和未解决的问题，再判断新内容为什么值得在此出现、所需前提是否已经讲过。无需预测唯一的下一节，但不能用后文或记忆倒补理由。\n'
        '遇到理解断点就记录位置、原句、具体问题、前文支持位置和缺少的解释；即使句子都看得懂，也记录路线选择突然、先细节后整体、比较或实验缺少所服务问题等结构性断点。需要时才读对应知识链接。\n'
        '随后放下标题，仅凭正文连贯解释整篇论文：困难如何引出所选思路、完整方案怎样工作、证据怎样改变结论。为连接本身提供正文依据；逐节摘要不等于整篇解释。区分有共同目的的并列分支与没有明确作用的材料堆放。\n'
        '再用报告中的证据复述任务、比较对象、一次完整算法过程、设计理由和主要结果；每项给出支持位置，无法支持就标为缺口。\n'
        '分别报告整体组织与局部理解的问题及严重度。评价解释是否成立，不评价作者努力、篇幅或排版；过渡句或章节检查通过不能代替整体通过。不要自行写修补答案。\n'
        '如已看过原文或作者讨论，明确标记为同上下文自查，不能称独立盲读。\n')
    if is_concept:
        instructions = (
            '只阅读 concept.json、knowledge.json 和包内配图；不要打开原始文献、外部来源、作者笔记或历史评审。\n'
            '你是第一次接触这个概念的读者。需要时才沿知识链接阅读，不要用已有专业知识补全正文。\n'
            '顺序记录理解断点：位置、原句、具体问题、已经知道什么、缺少哪一步、链接是否解决，以及严重度。\n'
            '只凭包内证据解释问题与原理，重建关键推导及条件，独立算完例子，再改变一个输入或假设预测结果。每个非平凡步骤给出支持位置。\n'
            '说明应用如何把数据变成输入、输出如何用于决策；解释所述变体改变什么、何时适用或失效。没有证据的步骤标为缺口。\n'
            '遇到尚不理解的必要知识时，沿嵌套链接继续阅读，直到获得当前步骤需要的理解，再逐层返回检验能否完成原来的步骤；不要只检查第一层链接。记录每次跳转所需知识、目标实际提供的解释及返回后仍缺什么。\n'
            '检查是否需要循环阅读才能获得第一个定义；目标存在或能打开不代表解释足够，缺失或过浅的依赖要明确报出。交互若存在，还要检查状态、数值和静态说明。\n'
            '返回具体问题及严重度，不自行编造修补答案，不以篇幅或排版证明质量。\n'
            '如已看过来源或作者讨论，标记 same_context_knowledge_only，不能称独立盲读。来源与正确性审核在另一个阶段进行。\n')
    (target/'instructions.txt').write_text(instructions, encoding='utf-8')
    revision_key = 'concept_revision' if is_concept else 'report_revision'
    return {'directory':str(target),'entry':entry,revision_key:doc['revision'],'knowledge_pages':len(knowledge)}


def bodies_for_images(section):
    from library import bodies
    return bodies({'sections':[section]}).images


def export(lib, destination):
    build(lib)
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    for item in (ROOT / 'web').iterdir():
        if item.is_dir():
            shutil.copytree(item, destination/item.name, dirs_exist_ok=True)
        else:
            shutil.copy2(item, destination/item.name)
    shutil.copytree(ROOT/'data/figures',destination/'data/figures',dirs_exist_ok=True)
    for directory in PDF_DIRECTORIES:
        if (ROOT/directory).is_dir():
            shutil.copytree(ROOT/directory,destination/directory,dirs_exist_ok=True)
    archive = destination.with_suffix('.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for file in destination.rglob('*'):
            if file.is_file():
                z.write(file, str(file.relative_to(destination)))
    return {'directory':str(destination),'zip':str(archive),'entry':str(destination/'index.html')}


def serve(lib, port):
    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            if args and str(args[1] if len(args)>1 else '') not in ('200','304'):
                super().log_message(format,*args)

        def json_response(self, value, code=200):
            body=json.dumps(value,ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length',str(len(body)))
            self.send_header('Cache-Control','no-store')
            self.end_headers(); self.wfile.write(body)

        def do_GET(self):
            parsed=urlsplit(self.path)
            q=parse_qs(parsed.query)
            arg=lambda k,default=None:q.get(k,[default])[0]
            try:
                if parsed.path.startswith('/api/') or parsed.path == '/bundle.js':
                    with lib.lock:
                        lib.reload()
                if parsed.path == '/api/catalog':
                    return self.json_response({'documents':lib.catalog(),'reader':lib.reader()})
                if parsed.path == '/api/document':
                    d=lib.get(arg('id',''))
                    # Reports always open the current document. Knowledge may be pinned.
                    if d['kind']=='concept' and arg('revision'):
                        d=lib.get(arg('id',''),arg('revision'))
                    d=copy.deepcopy(d)
                    d['backlinks']=lib.backlinks(d['id'])
                    d['latest_revision']=lib.get(d['id'])['revision']
                    return self.json_response(d)
                if parsed.path == '/api/search':
                    return self.json_response(lib.search(arg('q',''),arg('context',''),arg('kind'),limit=min(int(arg('limit',8)),30)))
                if parsed.path == '/api/reader':
                    return self.json_response(lib.reader())
                if parsed.path == '/api/status':
                    return self.json_response({'documents':len(lib.docs),'retrieval':'lexical','concept_resolution':'authoring_agent'})
                if parsed.path == '/bundle.js':
                    body=('window.READER_BUNDLE='+json.dumps(bundle(lib),ensure_ascii=False).replace('</','<\\/')+';').encode()
                    self.send_response(200);self.send_header('Content-Type','text/javascript; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body);return
                if parsed.path.startswith('/api/'):
                    return self.json_response({'error':'Not found'},404)
                return super().do_GET()
            except KeyError as e:
                return self.json_response({'error':str(e)},404)
            except (ValueError,TypeError) as e:
                return self.json_response({'error':str(e)},400)
            except Exception as e:
                return self.json_response({'error':type(e).__name__+': '+str(e)},500)

        def do_POST(self):
            try:
                origin=self.headers.get('Origin')
                host=self.headers.get('Host')
                if self.headers.get('X-Paper-Reader') != '1' or (origin and origin != 'http://'+host):
                    return self.json_response({'error':'Same-origin application requests required'},403)
                size=int(self.headers.get('Content-Length','0'))
                if size<1 or size>2_000_000:
                    return self.json_response({'error':'Invalid body size'},413)
                data=json.loads(self.rfile.read(size))
                path=urlsplit(self.path).path
                with lib.lock:
                    lib.reload()
                if path == '/api/reader':
                    return self.json_response(lib.reader(data['id'],data.get('state'),data.get('note')))
                if path == '/api/alias':
                    return self.json_response(lib.add_alias(data['id'],data['alias'],data['expected_revision']))
                if path == '/api/document':
                    return self.json_response(lib.save(data['document'],data.get('expected_revision')))
                return self.json_response({'error':'Not found'},404)
            except (ValueError,KeyError,TypeError) as e:
                return self.json_response({'error':str(e)},400)
            except Exception as e:
                return self.json_response({'error':type(e).__name__+': '+str(e)},500)

        def translate_path(self, path):
            path=unquote(urlsplit(path).path)
            directory = next((d for d in (*PDF_DIRECTORIES, 'data/figures') if path.startswith('/'+d+'/')), None)
            if directory:
                base=ROOT/directory;suffix=path[len('/'+directory+'/'):]
            else:
                base=ROOT/'web';suffix=path.lstrip('/') or 'index.html'
            target=(base/suffix).resolve()
            if not target.is_relative_to(base.resolve()):
                return str(ROOT/'web/__not_found__')
            return str(target)

        def end_headers(self):
            self.send_header('X-Content-Type-Options','nosniff')
            super().end_headers()

    server=LocalHTTPServer(('127.0.0.1',port),Handler)
    print('PaperThread: http://127.0.0.1:'+str(server.server_port),flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main():
    # JSON output must remain UTF-8 when redirected on Windows, including paths.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser(description='Local paper reports and reusable knowledge')
    sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('serve');s.add_argument('--port',type=int,default=8765)
    s=sub.add_parser('import-paper',help='Import a local PDF or a direct PDF URL; the agent resolves paper pages first')
    s.add_argument('source');s.add_argument('--source-url',help='Original paper page for provenance')
    s.add_argument('--max-mb',type=int,default=100,help='Maximum imported file size in MiB (default: 100)')
    s=sub.add_parser('search');s.add_argument('query');s.add_argument('--context',default='');s.add_argument('--kind',choices=['concept','report']);s.add_argument('--limit',type=int,default=6)
    s=sub.add_parser('get');s.add_argument('id');s.add_argument('--revision')
    s=sub.add_parser('save');s.add_argument('file');s.add_argument('--expected-revision')
    s=sub.add_parser('alias');s.add_argument('id');s.add_argument('name');s.add_argument('--expected-revision',required=True)
    s=sub.add_parser('merge');s.add_argument('source');s.add_argument('target');s.add_argument('--expected-source',required=True);s.add_argument('--expected-target',required=True)
    s=sub.add_parser('inventory');s.add_argument('--kind',choices=['concept','report'],default='concept');s.add_argument('--domain',default='');s.add_argument('--offset',type=int,default=0);s.add_argument('--limit',type=int,default=50)
    s=sub.add_parser('review-pack');s.add_argument('id');s.add_argument('--to',required=True);s.add_argument('--draft')
    s=sub.add_parser('pin');s.add_argument('--refresh',action='store_true')
    s=sub.add_parser('export');s.add_argument('--to',default=str(ROOT/'output/offline-reader'))
    sub.add_parser('check');sub.add_parser('build');sub.add_parser('catalog')
    args=p.parse_args();lib=Library()
    try:
        if args.command=='serve':return serve(lib,args.port)
        if args.command=='import-paper':out=import_paper(lib.root,args.source,args.source_url,args.max_mb*1024*1024)
        elif args.command=='search':out=lib.search(args.query,args.context,args.kind,args.limit)
        elif args.command=='get':out=lib.get(args.id,args.revision)
        elif args.command=='catalog':out=lib.catalog()
        elif args.command=='save':out=lib.save(json.loads(Path(args.file).read_text(encoding='utf-8')),args.expected_revision)
        elif args.command=='alias':out=lib.add_alias(args.id,args.name,args.expected_revision)
        elif args.command=='merge':out=lib.merge(args.source,args.target,args.expected_source,args.expected_target)
        elif args.command=='inventory':out=lib.inventory(args.kind,args.domain,args.offset,args.limit)
        elif args.command=='review-pack':out=review_pack(lib,args.id,args.to,json.loads(Path(args.draft).read_text(encoding='utf-8')) if args.draft else None)
        elif args.command=='pin':lib.pin(args.refresh);out={'pinned':True}
        elif args.command=='check':
            errors=lib.check();out={'ok':not errors,'documents':len(lib.docs),'errors':errors}
            print(json.dumps(out,ensure_ascii=False,indent=2));return 1 if errors else 0
        elif args.command=='build':out=build(lib)
        elif args.command=='export':out=export(lib,args.to)
        print(json.dumps(out,ensure_ascii=False,indent=2))
    except Exception as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False),file=sys.stderr);return 1
    return 0

if __name__=='__main__':
    sys.exit(main())
