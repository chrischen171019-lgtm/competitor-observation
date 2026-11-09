import importlib.util,unittest,json,tempfile,sqlite3
from datetime import datetime,timedelta
from pathlib import Path
spec=importlib.util.spec_from_file_location('monitor',Path(__file__).resolve().parents[1]/'monitor/collect.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class MonitorTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.c=m.connect(Path(self.tmp.name)/'t.db');self.now=datetime(2026,10,26,9,tzinfo=m.TZ)
 def tearDown(self):self.c.close();self.tmp.cleanup()
 def test_baseline_dedup_old_news(self):
  s={'id':'feed','product':'ima','category':'review'}
  e=m.item(s,'1','Title','Body','https://example.com/1','2026-10-25T08:00:00+08:00')
  a=m.ingest(self.c,s,[e],self.now);self.assertEqual(a[0]['classification'],'首次采集基线')
  self.assertEqual(m.ingest(self.c,s,[e],self.now+timedelta(days=1)),[])
  old=m.item(s,'2','old','Body','https://example.com/2','2025-01-01T00:00:00Z')
  a=m.ingest(self.c,s,[old],self.now);self.assertEqual(a[0]['classification'],'历史补录')
 def test_empty_first_response_is_not_a_baseline(self):
  s={'id':'empty','product':'ima','category':'review'}
  m.ingest(self.c,s,[],self.now)
  e=m.item(s,'first','Title','Body','https://example.com/first','2026-10-26T08:00:00+08:00')
  added=m.ingest(self.c,s,[e],self.now)
  self.assertEqual(added[0]['classification'],'首次采集基线')
 def test_rss_and_unsafe_url(self):
  s={'id':'rss','kind':'rss','product':'ima','category':'news_lead'}
  result=m.parse(s,b'<rss><channel><item><guid>x</guid><title>Title</title><description>&lt;script&gt;bad&lt;/script&gt;</description><link>javascript:bad()</link></item></channel></rss>')
  self.assertEqual(result[0]['url'],'');self.assertNotIn('<script>',result[0]['excerpt'])
 def test_issue_not_pr(self):
  s={'id':'issues','kind':'github_issues','product':'weknora','category':'feedback'}
  data=[{'id':1,'title':'PR','pull_request':{}},{'id':2,'title':'Question','html_url':'https://example.com/issue','created_at':'2026-10-25T00:00:00Z'}]
  self.assertEqual(len(m.parse(s,json.dumps(data).encode())),1)
 def test_rating_preserved(self):
  s={'id':'apple','kind':'apple','product':'ima','category':'review','app_id':123,'region':'CN'}
  data={'feed':{'entry':[{'id':{'label':'r1'},'title':{'label':'Review'},'content':{'label':'Text'},'im:rating':{'label':'2'},'im:version':{'label':'1.0'},'updated':{'label':'2026-10-25T00:00:00Z'}}]}}
  e=m.parse(s,json.dumps(data).encode())[0];self.assertEqual(e['rating'],'2');self.assertEqual(e['region'],'CN')
if __name__=='__main__':unittest.main()
