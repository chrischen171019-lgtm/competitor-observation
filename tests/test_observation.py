import importlib.util
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'monitor'))

class ObservationTests(unittest.TestCase):
 def test_live_news_not_a_fixed_sample(self):
  spec=importlib.util.find_spec('observation')
  self.assertIsNotNone(spec, 'live observation adapter is missing')
  from observation import news_records
  base=dict(id='new-id',product='ima',category='news_lead',title='新功能 - 媒体',url='https://example.org/news',excerpt='原文',published_at='2026-10-26T18:00:00+00:00',first_seen='2026-10-27T08:00:00+08:00')
  data={'events':[base,dict(base,id='review',category='review'),dict(base,id='bad',url='javascript:alert(1)'),dict(base,id='undated',published_at=None)]}
  rows=news_records(data,{'ima':'ima'})
  self.assertEqual([r['id'] for r in rows],['new-id','undated'])
  self.assertEqual(rows[0]['published_at'],'2026-10-27T02:00:00+08:00')
  self.assertIsNone(rows[1]['published_at'])
  self.assertEqual(rows[0]['publisher'],'媒体')

 def test_ingest_batches_preserve_identity_and_scope(self):
  spec=importlib.util.find_spec('sync_aihot')
  self.assertIsNotNone(spec, 'AIHOT bridge is missing')
  from sync_aihot import batches
  base=dict(source_id='weknora-releases',product='weknora',category='release',title='版本',url='https://example.org/1',published_at=None,classification='首次采集基线',excerpt='记录')
  events=[dict(base,id=str(i),url=f'https://example.org/{i}') for i in range(51)]+[dict(base,id='comment',category='review')]
  result=list(batches(events))
  self.assertEqual([len(b['items']) for b in result],[50,1])
  self.assertTrue(result[0]['items'][0]['raw']['_aihot']['baseline'])
  self.assertIsNone(result[0]['items'][0]['publishedAt'])
  self.assertEqual(result[0]['items'][0]['raw']['observation']['id'],'0')

if __name__=='__main__':unittest.main()
