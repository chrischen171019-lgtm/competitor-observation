import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'work/ui-prototype'))
from hot import rank_groups
class HotTests(unittest.TestCase):
 def event(self,id,at,publisher='36Kr',comments=0):
  return dict(id=id,product='chatgpt',title='同一事件 - '+publisher,category='news_lead',published_at=at,first_seen='2026-10-27T09:00:00+08:00',comments=comments)
 def test_window_uses_publication_not_discovery(self):
  rows=[self.event('old','2026-10-25T08:59:59+08:00'),self.event('edge','2026-10-25T09:00:00+08:00'),self.event('future','2026-10-27T09:00:01+08:00')]
  result=rank_groups(rows,'2026-10-27T09:00:00+08:00',[('x','chatgpt','event',['old','edge','future'])])
  e=result['events'][0];self.assertEqual(e['record_count'],1);self.assertAlmostEqual(e['heat'],0.25)
 def test_duplicate_channel_uses_latest_and_aliases(self):
  rows=[self.event('a','2026-10-27T09:00:00+08:00'),self.event('b','2026-10-26T09:00:00+08:00','36氪')]
  e=rank_groups(rows,'2026-10-27T09:00:00+08:00',[('x','chatgpt','event',['a','b'])])['events'][0]
  self.assertEqual(e['source_count'],1);self.assertEqual(e['heat'],1)
 def test_multisource_ranks_and_comments_do_not_inflate(self):
  rows=[self.event('a','2026-10-27T09:00:00+08:00',comments=9000),self.event('b','2026-10-27T08:00:00+08:00'),self.event('c','2026-10-27T08:00:00+08:00','财联社')]
  groups=[('one','chatgpt','one',['a']),('two','chatgpt','two',['b','c'])]
  r=rank_groups(rows,'2026-10-27T09:00:00+08:00',groups)['events'];self.assertEqual(r[0]['id'],'two');self.assertEqual(r[1]['heat'],1)
 def test_no_future_discoveries_and_missing_evidence(self):
  e=self.event('a','2026-10-27T09:00:00+08:00');e['first_seen']='2026-10-28T09:00:00+08:00'
  self.assertEqual(rank_groups([e],'2026-10-27T09:00:00+08:00',[('x','chatgpt','event',['a'])])['events'],[])
  with self.assertRaises(ValueError):rank_groups([],'2026-10-27T09:00:00+08:00',[('x','chatgpt','event',['missing'])])
if __name__=='__main__':unittest.main()
