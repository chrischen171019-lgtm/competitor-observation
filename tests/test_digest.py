import copy,json,sys,tempfile,unittest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'monitor'))
import digest,collect
DAY='2026-10-27'
class DigestTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.event=dict(id='e1',product='ima',category='review',classification='新发现线索',title='具体体验',excerpt='这是一条有具体任务和使用场景的评论，值得进一步核验。',first_seen=DAY+'T09:00:00+08:00',url='https://example.com/review',published_at=DAY,verification='待核验')
  self.article=dict(id='ima-use',product='ima',section='口碑观察',badge='未复现',title='使用体验',summary='样本观察',meaning='待核验价值',next='核验场景',limits='非总体结论',observations=['具体观察'],evidence_ids=['e1'],quotes=[dict(id='e1',text='具体任务和使用场景')])
  self.editorial=dict(date=DAY,headline='今日观察',intro='基于证据编辑',articles=[self.article],takeaways=[dict(article='ima-use',text='值得核验的场景')])
  self.statuses=[dict(id='feed',status='ok',count=1)]
  self.run=dict(at=DAY+'T09:00:00+08:00',sources=self.statuses)
 def tearDown(self):self.tmp.cleanup()
 def save(self,edited=True):
  (self.root/'outputs').mkdir(exist_ok=True)
  (self.root/'outputs/monitor-data.json').write_text(json.dumps(dict(events=[self.event],runs=[self.run])))
  if edited:
   (self.root/'monitor/editorials').mkdir(parents=True,exist_ok=True)
   (self.root/'monitor/editorials'/f'{DAY}.json').write_text(json.dumps(self.editorial))
 def test_evidence_and_quote_validation(self):
  digest.validate(self.editorial,{'e1':self.event},DAY)
  with self.assertRaises(AssertionError):digest.validate(self.editorial,{},DAY)
  self.article['quotes'][0]['text']='凭空编造的引文'
  with self.assertRaises(AssertionError):digest.validate(self.editorial,{'e1':self.event},DAY)
 def test_future_evidence_rejected(self):
  self.event['first_seen']='2026-10-28T09:00:00+08:00'
  with self.assertRaises(AssertionError):digest.validate(self.editorial,{'e1':self.event},DAY)
 def test_filter_retains_all_raw_records(self):
  events=[self.event]
  for changes in [dict(classification='历史补录'),dict(classification='首次采集基线'),dict(category='news_lead',title='无关新闻'),dict(excerpt='很好')]:
   events.append(dict(self.event,**changes))
  rows,chosen=digest.candidates(events,DAY)
  self.assertEqual(len(rows),5);self.assertEqual(chosen,[self.event])
 def test_render_escapes_and_keeps_appendix(self):
  self.event['title']='<script>alert(1)</script>';self.save()
  digest.publish(DAY,root=self.root)
  page=(self.root/f'reports/daily-{DAY}.html').read_text()
  self.assertIn('编辑版',page);self.assertNotIn('<script>alert(1)</script>',page)
  self.assertIn('&lt;script&gt;',page)
  self.assertIn('id="e-e1"',(self.root/f'reports/evidence-{DAY}.html').read_text())
 def test_candidate_and_empty_edition(self):
  self.save(edited=False);digest.publish(DAY,root=self.root)
  self.assertIn('自动候选稿',(self.root/f'reports/daily-{DAY}.html').read_text())
  self.editorial.update(articles=[],takeaways=[],headline='今日暂无足够证据形成主题')
  self.save();digest.publish(DAY,root=self.root)
  self.assertIn('今日暂无足够证据形成主题',(self.root/f'reports/daily-{DAY}.html').read_text())
 def test_collection_preserves_edited_daily_and_filters_archive(self):
  self.save();c=collect.connect(self.root/'test.db')
  c.execute('INSERT INTO events VALUES(?,?,?,?)',('e1',json.dumps(self.event),self.event['first_seen'],self.event['first_seen']))
  c.execute('INSERT INTO runs VALUES(?,?)',(self.run['at'],json.dumps(self.run)))
  with patch.object(collect,'ROOT',self.root):
   collect.render(c,dict(products=[dict(id='ima',name='ima')]),datetime.fromisoformat(self.run['at']),self.statuses)
  c.close()
  self.assertIn('今日观察',(self.root/f'reports/daily-{DAY}.html').read_text())
  payload=json.loads((self.root/'outputs/monitor-data.json').read_text())
  self.assertEqual(len(payload['archives']),3)
  self.assertFalse(any('evidence-' in x['name'] for x in payload['archives']))
if __name__=='__main__':unittest.main()
