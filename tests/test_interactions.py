import copy,json,unittest,tempfile
from pathlib import Path
from interactions import validate_interactives
from library import Library
from paper import bundle,review_pack
from test_library import concept

class InteractionTests(unittest.TestCase):
    def doc(self):
        d=concept();d['sections'][0]['html']='<div data-interactive="distance"><p>3.2 是下界，3.85 是完整距离。</p></div>'
        d['interactives']={'distance':{'type':'pq-bound','title':'下界','question':'改变阈值看是否回查','provenance':'构造算例','minimum':.1,'values':[.33,.51,.76,.28,.44,.61,.55,.37]}}
        return d
    def test_contract_rejects_missing_or_orphaned_widgets(self):
        d=self.doc();self.assertEqual(validate_interactives(d),[])
        d['sections'][0]['html']='<p>文字</p>'
        self.assertIn('Interactive configurations and slots must match',validate_interactives(d))
    def test_empty_fallback_rejected(self):
        d=self.doc();d['sections'][0]['html']='<div data-interactive="distance"></div>'
        self.assertIn('Interactive needs static fallback text',validate_interactives(d))

    def test_logit_example_validates_domain_and_nonfinite_inputs(self):
        d=self.doc()
        c={'type':'regularized-logit','title':'权重','question':'观察最优变化','provenance':'教学算例',
           'parameters':{'fixed_logit':.5,'initial_feature':1,'feature_weight':1.5,'max_shift':2},
           'lambda_range':{'min':0,'max':.8,'step':.01,'initial':.2},'feature_label':'背景'}
        d['interactives']['distance']=c
        self.assertEqual(validate_interactives(d),[])
        for field,value in [('max_shift',0),('feature_weight',-1),('fixed_logit',float('nan')),('initial_feature',True)]:
            bad=copy.deepcopy(d);bad['interactives']['distance']['parameters'][field]=value
            self.assertTrue(validate_interactives(bad))
        for field,value in [('max',0),('step',0),('initial',1),('min',-.1)]:
            bad=copy.deepcopy(d);bad['interactives']['distance']['lambda_range'][field]=value
            self.assertTrue(validate_interactives(bad))

    def test_calculations_reject_invalid_parameters(self):
        for v in [float('nan'),-1,None,True]:
            d=self.doc();d['interactives']['distance']['values'][0]=v
            self.assertTrue(validate_interactives(d))
        d=self.doc();d['interactives']['distance']={'type':'rabitq-bound','title':'界','question':'q','provenance':'p','parameters':{'dimension':1}}
        self.assertTrue(validate_interactives(d))
    def test_review_pack_includes_operable_content_and_static_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib=Library(Path(tmp));d=self.doc();lib.save(d)
            result=review_pack(lib,d['id'],Path(tmp)/'pack')
            packed=json.loads((Path(tmp)/'pack'/result['entry']).read_text(encoding='utf-8'))
            self.assertEqual(packed['interactives'],d['interactives']);self.assertIn('3.85',packed['sections'][0]['html'])
    def test_report_update_keeps_one_current_report_and_pinned_knowledge(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'test_paper').mkdir();(root/'test_paper/test.pdf').write_bytes(b'%PDF-1.4')
            lib=Library(root);lib.save(concept());kold=lib.get('k-pq')['revision']
            report={'id':'r-test','kind':'report','title':'报告','summary':'旧','status':'ready','sections':[{'id':'mechanism','title':'正文','html':'<a data-concept="k-pq">PQ</a>'}],'sources':[{'id':'paper','title':'原文','url':'/test_paper/test.pdf'}],'paper':{'pdf':'test_paper/test.pdf','pages':1}}
            lib.save(report);lib.pin();old=copy.deepcopy(lib.get('r-test'));prev=old['revision']
            changed=copy.deepcopy(lib.get('k-pq'));changed['summary']='新知识';lib.save(changed,kold)
            new=copy.deepcopy(old);new.update(summary='新版',previous_revision=prev);lib.save(new,prev);lib.pin()
            result=bundle(lib)
            self.assertEqual([d['id'] for d in lib.catalog('report')],['r-test'])
            self.assertEqual(result['documents']['r-test']['summary'],'新版')
            self.assertNotIn('previous_revision',result['documents']['r-test'])
            self.assertFalse(any(d['kind']=='report' for d in result['revisions'].values()))
            self.assertEqual(result['revisions']['k-pq@'+kold]['summary'],concept()['summary'])
            self.assertEqual(result['documents']['r-test']['references']['k-pq'],kold)

if __name__=='__main__':unittest.main()
