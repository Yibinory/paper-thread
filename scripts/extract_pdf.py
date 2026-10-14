#!/usr/bin/env python3
"""Extract local PDF pages with page provenance and optionally render specified pages."""
import argparse
import hashlib
import json
from pathlib import Path
from pypdf import PdfReader

parser=argparse.ArgumentParser()
parser.add_argument('pdf',type=Path)
parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--render',type=int,nargs='*',default=[])
args=parser.parse_args()
reader=PdfReader(args.pdf)
pages=[{'page':i+1,'text':page.extract_text() or ''} for i,page in enumerate(reader.pages)]
args.out.mkdir(parents=True,exist_ok=True)
(args.out/'pages.json').write_text(json.dumps({'file':str(args.pdf.resolve()),'sha256':hashlib.sha256(args.pdf.read_bytes()).hexdigest(),'pages':pages},ensure_ascii=False,indent=2),encoding='utf-8')
(args.out/'fulltext.txt').write_text('\n\n'.join('===== PDF PAGE '+str(p['page'])+' =====\n'+p['text'] for p in pages),encoding='utf-8')
if args.render:
 import pdfplumber
 with pdfplumber.open(args.pdf) as pdf:
  for number in args.render:
   if number<1 or number>len(pages):raise ValueError('Invalid page '+str(number))
   pdf.pages[number-1].to_image(resolution=140).save(args.out/('page-'+str(number)+'.png'))
print(json.dumps({'pages':len(pages),'rendered':args.render,'output':str(args.out)},ensure_ascii=False))
