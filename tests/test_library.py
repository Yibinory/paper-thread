import copy
import json
from pathlib import Path
import tempfile
import unittest
from library import Library, digest, write_json, plain
from paper import review_pack


def concept(ident='k-pq', title='乘积量化'):
    return {'id':ident,'kind':'concept','title':title,'subtitle':'','summary':'把高维向量分段编码，用小码本压缩并通过查表估计距离。','domain':'向量检索','tags':['检索'],'status':'ready','aliases':['PQ','Product Quantization'],'scope':'独立子空间的量化和查表','not_this':['不是标量量化'],'semantic_terms':['vector subspace codebook compression'],'prerequisites':[],'sections':[{'id':'mechanism','title':'分段编码','html':'<p>每个子向量在自己的码本里选择代表点。</p>'}],'sources':[{'id':'primary','title':'Source','url':'https://example.org/paper'}]}


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        for p in ('data/concepts','data/reports','data/figures','test_paper'):(self.root/p).mkdir(parents=True)
        write_json(self.root/'data/concepts/k-pq.json',concept())
        self.lib=Library(self.root)

    def tearDown(self):self.tmp.cleanup()

    def test_alias_search_case_and_language(self):
        for q in ('PQ','product quantization','乘积量化'):
            self.assertEqual(self.lib.search(q)['results'][0]['id'],'k-pq')

    def test_plain_preserves_math_comparison_and_following_prose(self):
        self.assertIn(r'0 \le t<\Delta',plain(r'<p>\(0 \le t<\Delta\)，随机舍入。</p>'))
        self.assertIn('随机舍入',plain(r'<p>\(0 \le t<\Delta\)，随机舍入。</p>'))

    def test_versions_and_stale_writes(self):
        old=copy.deepcopy(self.lib.get('k-pq'));self.lib.snapshot(old)
        new=copy.deepcopy(old);new['title']='PQ 的编码与距离'
        self.lib.save(new,old['revision'])
        self.assertEqual(self.lib.get('k-pq',old['revision'])['title'],'乘积量化')
        with self.assertRaisesRegex(ValueError,'Revision conflict'):self.lib.save(old,old['revision'])

    def test_unknown_or_draft_links_rejected(self):
        new=concept('k-second','另一个概念');new['sections'][0]['html']='<p><a data-concept="k-missing">Missing</a></p>'
        with self.assertRaisesRegex(ValueError,'Unknown concept'):self.lib.save(new)
        new['sections'][0]['html']='<p>草稿</p>';new['status']='draft';self.lib.save(new)
        old=copy.deepcopy(self.lib.get('k-pq'));old['sections'][0]['html']='<p><a data-concept="k-second">Draft</a></p>'
        with self.assertRaisesRegex(ValueError,'links to draft'):self.lib.save(old,old['revision'])

    def test_invalid_anchor_and_cycle_rejected(self):
        new=concept('k-second','二');new['prerequisites']=['k-pq'];self.lib.save(new)
        old=copy.deepcopy(self.lib.get('k-pq'));old['prerequisites']=['k-second']
        with self.assertRaisesRegex(ValueError,'cycle'):self.lib.save(old,old['revision'])
        old['prerequisites']=[];old['sections'][0]['html']='<a data-concept="k-second" data-section="missing">二</a>'
        with self.assertRaisesRegex(ValueError,'Missing section'):self.lib.save(old,old['revision'])

    def test_html_rejects_executable_content(self):
        for body in ('<script>alert(1)</script>','<img src="/data/figures/test.png" onerror="alert(1)">','<a href="javascript:alert(1)">x</a>'):
            new=concept('k-new','新');new['sections'][0]['html']=body
            with self.assertRaises(ValueError):self.lib.save(new)

    def test_reader_status_requires_explicit_write(self):
        self.lib.get('k-pq');self.assertEqual(self.lib.reader(),{})
        self.lib.reader('k-pq',state='confused',note='不能把相似当相同')
        reopened=Library(self.root)
        self.assertEqual(reopened.reader()['k-pq']['state'],'confused')
        self.assertEqual(reopened.reader()['k-pq']['note'],'不能把相似当相同')

    def test_merge_preserves_ids_and_history(self):
        second=concept('k-other','另一种叫法');second['aliases']=['PQ别名'];self.lib.save(second)
        a,b=self.lib.get('k-other'),self.lib.get('k-pq');rev=a['revision']
        self.lib.merge('k-other','k-pq',a['revision'],b['revision'])
        self.assertEqual(self.lib.get('k-other')['id'],'k-pq')
        self.assertEqual(self.lib.get('k-other',rev)['title'],'另一种叫法')
        self.assertIn('PQ别名',self.lib.get('k-pq')['aliases'])

    def test_report_pins_survive_concept_revision(self):
        (self.root/'test_paper/paper.pdf').write_bytes(b'%PDF-1.4')
        report={'id':'r-paper','kind':'report','title':'报告','summary':'示例','status':'ready','sections':[{'id':'main','title':'正文','html':'<p><a data-concept="k-pq" data-section="mechanism">PQ</a></p>'}],'sources':[{'id':'paper','title':'paper','url':'/test_paper/paper.pdf'}],'paper':{'pdf':'test_paper/paper.pdf','pages':1}}
        self.lib.save(report);self.lib.pin();pinned=self.lib.get('r-paper')['references']['k-pq']
        d=copy.deepcopy(self.lib.get('k-pq'));d['sections'][0]['id']='renamed';d['summary']='新版内容';self.lib.save(d,d['revision'])
        self.lib.pin()
        self.assertEqual(self.lib.get('r-paper')['references']['k-pq'],pinned)
        self.assertEqual(self.lib.get('k-pq',pinned)['sections'][0]['id'],'mechanism')
        self.assertEqual(self.lib.check(),[])

    def test_missing_source_file_rejected(self):
        new=concept('k-new','新');new['sources'][0]['url']='/test_paper/missing.pdf#page=2'
        with self.assertRaisesRegex(ValueError,'local source'):self.lib.save(new)

    def test_new_reference_to_merged_id_and_backlinks(self):
        second=concept('k-old','旧名');self.lib.save(second)
        a,b=self.lib.get('k-old'),self.lib.get('k-pq')
        self.lib.merge('k-old','k-pq',a['revision'],b['revision'])
        d=concept('k-reference','引用者');d['sections'][0]['html']='<p><a data-concept="k-old">旧名</a></p>';self.lib.save(d)
        self.assertIn('k-reference',[x['id'] for x in self.lib.backlinks('k-pq')])
        self.lib.snapshot(self.lib.get('k-pq'))
        self.assertEqual(self.lib.get('k-old',self.lib.get('k-pq')['revision'])['id'],'k-pq')

    def test_nested_knowledge_pins(self):
        second=concept('k-base','基础');self.lib.save(second)
        d=copy.deepcopy(self.lib.get('k-pq'));d['sections'][0]['html']='<p><a data-concept="k-base">基础</a></p>';self.lib.save(d,d['revision'])
        (self.root/'test_paper/paper.pdf').write_bytes(b'%PDF-1.4')
        report={'id':'r-nested','kind':'report','title':'报告','summary':'示例','status':'ready','sections':[{'id':'main','title':'正文','html':'<a data-concept="k-pq">PQ</a>'}],'sources':[{'id':'paper','title':'paper','url':'/test_paper/paper.pdf'}],'paper':{'pdf':'test_paper/paper.pdf','pages':1}}
        self.lib.save(report);self.lib.pin();self.assertIn('k-base',self.lib.get('r-nested')['references'])

    def test_inventory_covers_aliases_without_keyword_match(self):
        other=concept('k-rotation','随机正交变换');other['aliases']=['旋转坐标系'];other['domain']='线性代数'
        self.lib.save(other)
        pages=[];offset=0
        while True:
            page=self.lib.inventory(limit=1,offset=offset);pages.extend(page['entries'])
            if page['next_offset'] is None:break
            offset=page['next_offset']
        self.assertEqual({d['id'] for d in pages},{'k-pq','k-rotation'})
        rotation=next(d for d in pages if d['id']=='k-rotation')
        self.assertIn('旋转坐标系',rotation['aliases'])
        self.assertEqual(rotation['scope'],other['scope'])
        self.assertNotIn('html',rotation['sections'][0])
        self.assertEqual(self.lib.inventory(domain='线性')['total'],1)

    def test_review_pack_uses_draft_and_pinned_nested_knowledge(self):
        base=concept('k-base','基础');self.lib.save(base)
        d=copy.deepcopy(self.lib.get('k-pq'));d['sections'][0]['html']='<p><a data-concept="k-base">基础</a></p>'
        self.lib.save(d,d['revision'])
        (self.root/'test_paper/paper.pdf').write_bytes(b'%PDF-1.4')
        report={'id':'r-review','kind':'report','title':'旧版','summary':'示例','status':'ready','sections':[{'id':'main','title':'正文','html':'<a data-concept="k-pq">PQ</a>'}],'sources':[{'id':'paper','title':'paper','url':'/test_paper/paper.pdf'}],'paper':{'pdf':'test_paper/paper.pdf','pages':1}}
        self.lib.save(report);self.lib.pin()
        draft=copy.deepcopy(self.lib.get('r-review'));draft['title']='新版草稿';draft['author_notes']='不要泄漏给读者'
        old_base=draft['references']['k-base']
        updated=copy.deepcopy(self.lib.get('k-base'));updated['title']='基础的新版本';self.lib.save(updated,updated['revision'])
        target=self.root/'review';review_pack(self.lib,'r-review',target,draft)
        packed=json.loads((target/'report.json').read_text(encoding='utf-8'));knowledge=json.loads((target/'knowledge.json').read_text(encoding='utf-8'))
        self.assertEqual(packed['title'],'新版草稿')
        self.assertEqual(self.lib.get('r-review')['title'],'旧版')
        self.assertEqual(knowledge['k-base']['revision'],old_base)
        self.assertNotIn('author_notes',packed);self.assertNotIn('paper',packed)
        self.assertNotIn('url',packed['sources'][0])
        self.assertFalse(list(target.rglob('*.pdf')))

    def test_concept_review_pack_keeps_draft_root_on_related_link_roundtrip(self):
        related=concept('k-related','应用')
        related['sections'][0]['html']='<p><a data-concept="k-pq">回到基础</a></p>'
        self.lib.save(related)
        draft=copy.deepcopy(self.lib.get('k-pq'))
        draft['title']='独立教程草稿'
        draft['sections'][0]['html']='<p><a data-concept="k-related">应用</a></p>'
        draft['author_notes']='不进入阅读包'
        target=self.root/'knowledge-review'
        result=review_pack(self.lib,'k-pq',target,draft)
        packed=json.loads((target/'concept.json').read_text(encoding='utf-8'))
        linked=json.loads((target/'knowledge.json').read_text(encoding='utf-8'))
        self.assertEqual(packed['title'],'独立教程草稿')
        self.assertEqual(result['concept_revision'],digest(draft))
        self.assertEqual(set(linked),{'k-related'})
        self.assertNotIn('author_notes',packed)
        self.assertNotIn('url',packed['sources'][0])
        self.assertFalse((target/'report.json').exists())
        self.assertEqual(self.lib.get('k-pq')['title'],'乘积量化')

if __name__=='__main__':unittest.main()
