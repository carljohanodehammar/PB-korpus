"""Kontrollera att kompletteringar inte bryter historik och belägg."""
import hashlib,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_edition import build
class EditionTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)/'site';shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns('__pycache__'));self.manifest=self.root/'editorial/edition.json'
 def tearDown(self):self.temp.cleanup()
 def test_new_revision_keeps_old_evidence_and_raw_text(self):
  m=json.loads(self.manifest.read_text());item=m['pages'][0];old=self.root/'editorial/revisions'/item['revisions'][-1];before=old.read_bytes();r=json.loads(before);r['revision']=3;r['parentRevision']=2;r['changeReason']='Test av framtida komplettering';candidate=self.root/'candidate.json';candidate.write_text(json.dumps(r,ensure_ascii=False))
  raw=self.root/'docs/texts'/(r['documentId']+'.json');raw_before=raw.read_bytes()
  subprocess.run([sys.executable,str(self.root/'scripts/add_revision.py'),str(candidate)],check=True,capture_output=True)
  out=json.loads((self.root/'docs/edition.json').read_text());current=next(x for x in out['pages'] if x['pageId']==r['pageId']);self.assertEqual(current['revision'],3);self.assertEqual(old.read_bytes(),before);self.assertEqual(raw.read_bytes(),raw_before)
  self.assertEqual([x['revision'] for x in out['history'][r['pageId']]],[1,2,3]);self.assertIn('E-K05-MATRIKEL@2',out['evidence']);self.assertIn('E-K05-MATRIKEL@3',out['evidence']);self.assertEqual(next(e for e in out['register'] if e['id']=='T-MATRIKEL')['evidence'][0]['revision'],2)
 def test_wrong_original_version_rejected(self):
  m=json.loads(self.manifest.read_text());p=self.root/'editorial/revisions'/m['pages'][0]['revisions'][-1];r=json.loads(p.read_text());r['sourceSha256']='0'*64;p.write_text(json.dumps(r));
  with self.assertRaises(AssertionError):build(self.root)
 def test_missing_evidence_rejected(self):
  p=self.root/'editorial/register.json';r=json.loads(p.read_text());r['entries'][0]['evidence'][0]['revision']=999;p.write_text(json.dumps(r));
  with self.assertRaises(AssertionError):build(self.root)
 def test_immutable_corpus_revision_rejected_before_export(self):
  corpus=Path(self.temp.name)/'corpus';target=corpus/'03_normaliserad_text/reviews';target.mkdir(parents=True);m=json.loads(self.manifest.read_text());name=m['pages'][0]['revisions'][0];(target/name).write_text('tidigare sparad version');public=self.root/'docs/edition.json';before=public.read_bytes()
  with self.assertRaises(ValueError):build(self.root,corpus)
  self.assertEqual(public.read_bytes(),before)
if __name__=='__main__':unittest.main()
