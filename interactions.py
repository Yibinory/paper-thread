"""Validate structured, non-executable explanations before they enter the reader."""
import math
import re
from html.parser import HTMLParser

class Slots(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.depth=0; self.active=[]; self.fallbacks={}; self.invalid_slots=[]
    def handle_starttag(self, tag, attrs):
        if tag=='div':self.depth+=1
        value=dict(attrs).get('data-interactive')
        if value is not None:
            self.ids.append(value)
            if tag!='div':self.invalid_slots.append(value)
            else:self.active.append([value,self.depth,[]])
    def handle_data(self,data):
        for item in self.active:item[2].append(data)
    def handle_endtag(self,tag):
        if tag=='div':
            for item in list(self.active):
                if item[1]==self.depth:
                    self.fallbacks[item[0]]=''.join(item[2]).strip();self.active.remove(item)
            self.depth-=1

def validate_interactives(doc):
    errors=[]; specs=doc.get('interactives',{})
    parser=Slots()
    for s in doc.get('sections',[]):parser.feed(s.get('html',''))
    if not isinstance(specs,dict):return ['interactives must be an object']
    if parser.invalid_slots:errors.append('Interactive slot must be a div')
    if any(not parser.fallbacks.get(key) for key in parser.ids):errors.append('Interactive needs static fallback text')
    if len(parser.ids)!=len(set(parser.ids)):errors.append('Duplicate interactive slot')
    if set(specs)!=set(parser.ids):errors.append('Interactive configurations and slots must match')
    def text(v):return isinstance(v,str) and bool(v.strip())
    def number(v):return isinstance(v,(float,int)) and not isinstance(v,bool) and math.isfinite(v)
    for key,c in specs.items():
        if not re.fullmatch(r'[a-z][a-z0-9-]{1,79}',key) or not isinstance(c,dict):
            errors.append('Invalid interactive ID/configuration');continue
        bad=lambda message:errors.append(key+': '+message)
        if not all(text(c.get(k)) for k in ('title','question','provenance')):bad('Missing explanation contract')
        t=c.get('type')
        if t=='trace':
            steps=c.get('steps')
            if not isinstance(steps,list) or len(steps)<2:bad('Trace needs at least two states');continue
            for s in steps:
                if not isinstance(s,dict) or not all(text(s.get(k)) for k in ('label','caption','changes','holds','reason')):bad('Incomplete trace step');continue
                states=s.get('states')
                if not isinstance(states,list) or not states:bad('Trace needs visible state');continue
                for v in states:
                    if not isinstance(v,dict) or not text(v.get('label')) or not text(v.get('value')) or v.get('state') not in ('active','fixed','read'):bad('Invalid visible state')
        elif t=='evidence':
            cols=c.get('columns');cases=c.get('cases')
            if not isinstance(cols,list) or not cols or not all(text(x) for x in cols) or not text(c.get('measure')):bad('Invalid evidence columns');continue
            if not isinstance(cases,list) or not cases:bad('Missing evidence cases');continue
            for s in cases:
                if not isinstance(s,dict) or not all(text(s.get(k)) for k in ('label','condition','takeaway')):bad('Incomplete evidence case');continue
                if not isinstance(s.get('rows'),list) or not s['rows']:bad('Missing evidence rows');continue
                for r in s['rows']:
                    if not isinstance(r,dict) or not text(r.get('label')) or not isinstance(r.get('values'),list) or len(r['values'])!=len(cols):bad('Invalid evidence row');continue
                    if not all(text(v) or number(v) for v in r['values']):bad('Invalid evidence value')
        elif t=='pq-bound':
            vs=c.get('values');m=c.get('minimum')
            if m!=0.1 or not isinstance(vs,list) or len(vs)!=8 or not all(number(v) and v>=m for v in vs):bad('PQ example needs eight finite distances ≥ 0.1, minimum 0.1')
        elif t=='rabitq-bound':
            # This renderer explains the stated worked example; arbitrary parameters
            # would invalidate both labels and the interpretation of the controls.
            if c.get('parameters')!={'dimension':256,'a':0.8,'ro':2,'rq':3,'numerator':0.4}:bad('Unsupported RaBitQ worked-example parameters')
        else:bad('Unknown interactive type')
    return errors
