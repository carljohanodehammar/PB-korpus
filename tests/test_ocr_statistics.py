import importlib.util,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('ocr',Path(__file__).resolve().parents[1]/'scripts/ocr_batch.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class StatisticsTests(unittest.TestCase):
 def test_leading_quote_does_not_swallow_following_rows(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'page.tsv';p.write_text('conf\ttext\n20\t"ord\n90\tnästa\n80\tsista\n-1\t\n')
   score,count=module.read_statistics(p)
   self.assertEqual(count,3)
   self.assertAlmostEqual(score,(20*4+90*5+80*5)/14)
 def test_empty_page_is_not_high_confidence(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'page.tsv';p.write_text('conf\ttext\n-1\t\n')
   self.assertEqual(module.read_statistics(p),(0,0))
if __name__=='__main__':unittest.main()
