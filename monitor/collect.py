#!/usr/bin/env python3
"""Public-source monitor. No credentials, no LLM, no automatic sentiment claims."""
from pathlib import Path
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
import sys,argparse,concurrent.futures,fcntl,hashlib,html,json,os,re,sqlite3,subprocess,tempfile,urllib.parse,xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
ROOT=Path(__file__).resolve().parents[1]
TZ=ZoneInfo('Asia/Shanghai')
MAX_BYTES=4_000_000

def clean(value):
 return re.sub(r'\s+',' ',re.sub('<[^>]+>',' ',html.unescape(str(value or '')))).strip()
def stamp(value):
 if not value:return None
 try:return datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(TZ).isoformat()
 except ValueError:
  try:return parsedate_to_datetime(value).astimezone(TZ).isoformat()
  except (ValueError,TypeError,OverflowError):return None
def safe_url(value):
 u=str(value or '');return u if urllib.parse.urlsplit(u).scheme in ('https','http') else ''
def atomic(path,text):
 path.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=path.parent,delete=False) as f:f.write(text);tmp=f.name
 os.replace(tmp,path)
def item(s,external,title,body,url,date=None,**extra):
 return dict(id=hashlib.sha256((s['id']+'|'+str(external)).encode()).hexdigest()[:24],source_id=s['id'],product=s['product'],category=s['category'],title=clean(title),excerpt=clean(body)[:600],url=safe_url(url),published_at=stamp(date),verification='待核验',summary_mode='原文摘录／规则提取（非 AI 摘要）',**extra)
def parse(s,raw):
 k=s['kind'];out=[]
 if k=='rss':
  root=ET.fromstring(raw)
  for x in root.findall('.//item')[:30]:
   url=x.findtext('link','');title=x.findtext('title','')
   out.append(item(s,x.findtext('guid') or url or title,title,x.findtext('description',''),url,x.findtext('pubDate')))
 else:
  d=json.loads(raw)
  if k=='apple':
   for x in d.get('feed',{}).get('entry',[]):
    if 'im:rating' not in x:continue
    eid=x.get('id',{}).get('label','');links=x.get('link',[]);links=[links] if isinstance(links,dict) else links
    url=next((z.get('attributes',{}).get('href') for z in links if z.get('attributes',{}).get('rel')=='alternate'),None)
    out.append(item(s,eid,x.get('title',{}).get('label',''),x.get('content',{}).get('label',''),url or f"https://apps.apple.com/cn/app/id{s['app_id']}?see-all=reviews",x.get('updated',{}).get('label'),rating=x['im:rating']['label'],version=x.get('im:version',{}).get('label'),region=s['region'],external_id=eid))
  elif k=='github_releases':
   if not isinstance(d,list):raise ValueError('Unexpected GitHub response')
   for x in d:out.append(item(s,x['id'],x.get('name') or x['tag_name'],x.get('body'),x['html_url'],x.get('published_at'),version=x['tag_name'],prerelease=x.get('prerelease',False)))
  elif k=='github_issues':
   if not isinstance(d,list):raise ValueError('Unexpected GitHub response')
   for x in d:
    if 'pull_request' in x:continue
    out.append(item(s,x['id'],x['title'],x.get('body'),x['html_url'],x.get('created_at'),source_updated_at=x.get('updated_at'),issue_state=x.get('state'),comments=x.get('comments')))
  elif k=='hn':
   for x in d.get('hits',[]):
    if s['keyword'].lower() not in (str(x.get('title',''))+' '+str(x.get('story_text',''))).lower():continue
    out.append(item(s,x['objectID'],x.get('title'),x.get('story_text'),f"https://news.ycombinator.com/item?id={x['objectID']}",x.get('created_at'),comments=x.get('num_comments')))
  else:raise ValueError('Unknown source kind')
 return out

def fetch(s):
 try:
  # curl uses macOS trusted certificates; no -k / certificate bypass.
  with tempfile.NamedTemporaryFile() as f:
   r=subprocess.run(['/usr/bin/curl','--fail','--silent','--show-error','--location','--proto','=https','--proto-redir','=https','--retry','1','--retry-delay','1','--connect-timeout','8','--max-time','20','--max-filesize',str(MAX_BYTES),'-A','CompetitorMonitor/0.1','-o',f.name,s['url']],capture_output=True,text=True,timeout=48)
   if r.returncode:raise RuntimeError(r.stderr.strip()[:350])
   raw=Path(f.name).read_bytes()
  if len(raw)>MAX_BYTES:raise ValueError('Response too large')
  entries=parse(s,raw)
  digest=hashlib.sha256(raw).hexdigest()
  path=ROOT/'data/raw'/s['id']/(digest+'.txt');path.parent.mkdir(parents=True,exist_ok=True)
  if not path.exists():path.write_bytes(raw)
  return s,entries,{'status':'ok','count':len(entries),'snapshot':str(path.relative_to(ROOT)),'sample_status':'有样本' if entries else '成功响应但无可用匹配样本（不代表无反馈）'}
 except Exception as exc:return s,[],{'status':'error','error':str(exc)[:400],'count':0}

def connect(path):
 c=sqlite3.connect(path)
 c.executescript('CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY,payload TEXT,first_seen TEXT,last_seen TEXT); CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY,payload TEXT); CREATE TABLE IF NOT EXISTS sources(id TEXT PRIMARY KEY,last_success TEXT);')
 return c

def ingest(c,s,entries,now):
 previous=c.execute("SELECT 1 FROM events WHERE json_extract(payload, '$.source_id')=? LIMIT 1",(s['id'],)).fetchone()
 added=[]
 for e in entries:
  row=c.execute('SELECT payload,first_seen FROM events WHERE id=?',(e['id'],)).fetchone()
  if row:
   old=json.loads(row[0]);e.update(first_seen=row[1],classification=old['classification'])
  else:
   published=stamp(e.get('published_at'))
   e['classification']='首次采集基线' if not previous else ('日期待核验' if not published else ('历史补录' if datetime.fromisoformat(published)<now-timedelta(days=2) else '新发现线索'))
   e['first_seen']=now.isoformat();added.append(e)
  e['last_seen']=now.isoformat()
  c.execute('INSERT OR REPLACE INTO events VALUES(?,?,?,?)',(e['id'],json.dumps(e,ensure_ascii=False),e['first_seen'],e['last_seen']))
 c.execute('INSERT OR REPLACE INTO sources VALUES(?,?)',(s['id'],now.isoformat()))
 return added

def render(c,config,now,statuses):
 records=[json.loads(x[0]) for x in c.execute('SELECT payload FROM events ORDER BY first_seen DESC,id')]
 names={p['id']:p['name'] for p in config['products']};names['market']='新产品观察'
 day=now.date().isoformat();week=(now-timedelta(days=now.weekday())).date().isoformat();month=now.strftime('%Y-%m-01')
 runs=[json.loads(x[0]) for x in c.execute('SELECT payload FROM runs ORDER BY id')]
 def escaped(v):return html.escape(str(v or ''),quote=True)
 def cards(rows):
  return ''.join('<div class="source"><strong>'+escaped(names.get(e['product'],e['product']))+' · '+escaped(e['title'])+'</strong><p>'+escaped(e['excerpt'])+'</p><p class="note">'+escaped(e['classification'])+' · '+escaped(e['verification'])+' · '+escaped(e['category'])+' · 发布：'+escaped(e.get('published_at') or '未知')+' · 首次发现：'+escaped(e['first_seen'])+((' · 原始评分：'+escaped(e['rating'])+' · 地区：'+escaped(e.get('region'))+' · 版本：'+escaped(e.get('version'))) if 'rating' in e else '')+'</p><a target="_blank" rel="noopener" href="'+escaped(e['url'])+'">查看来源</a></div>' for e in rows) or '<p>此范围暂无采集记录。请结合来源状态判断，不能据此断言没有变化。</p>'
 archives=[]
 for kind,start,label in [('weekly',week,'周报（进行中）'),('monthly',month,'月报（进行中）')]:
  rows=[e for e in records if e['first_seen'][:10]>=start and e['first_seen'][:10]<=day]
  period_runs=[r for r in runs if start<=r['at'][:10]<=day]
  health='<ul>'+''.join('<li>'+escaped(x['id'])+'：'+escaped(x['status'])+(' · '+escaped(x.get('error')) if x['status']=='error' else ' · '+str(x['count'])+' 条')+'</li>' for x in statuses)+'</ul>'
  intro=f'<h1>{label} · {start}</h1><p>截至 {now.isoformat()}，按首次发现时间归档，共 {len(rows)} 条记录。无 AI API：以下仅为原文摘录／规则提取，未经自动事实核验。</p><p>首次运行建立基线；旧消息标记历史补录；新闻不是用户口碑。抓取的最新页不保证完整覆盖。周期内共 {len(period_runs)} 次运行，历次状态见 JSON 数据中的 runs。</p>'
  body=intro+'<h2>本次来源检查</h2>'+health+'<h2>采集记录</h2>'+cards(rows)
  css='body{max-width:1000px;margin:40px auto;padding:0 24px;font:16px/1.8 -apple-system,sans-serif;color:#172b35}.source{border-bottom:1px solid #ddd;padding:20px 0}.note{color:#52636b}a{color:#006b5c}'
  document='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+label+'</title><style>'+css+'</style><body>'+body+'</body></html>'
  name=f'{kind}-{start}'
  revision=ROOT/'reports'/('revisions/'+name+'-'+now.strftime('%Y%m%dT%H%M%S%f')+'.html');atomic(revision,document);atomic(ROOT/'reports'/(name+'.html'),document)
  md=f'# {label} · {start}\n\n生成：{now.isoformat()}。无 AI API，仅规则提取。{len(rows)} 条。\n\n## 来源检查\n'+''.join(f"- {x['id']}: {x['status']} {x.get('error','')}\n" for x in statuses)+'\n## 记录\n'+''.join(f"\n### {names.get(e['product'],e['product'])} · {e['title']}\n\n{e['excerpt']}\n\n{e['classification']}；{e['verification']}；发布：{e.get('published_at') or '未知'}；发现：{e['first_seen']}\n\n来源：<{e['url']}>\n" for e in rows)
  atomic(ROOT/'reports'/(name+'.md'),md)
 for path in sorted(set((ROOT/'reports').glob('*.html'))|{ROOT/'reports'/('daily-'+day+'.html')},reverse=True):
  if path.name.startswith(('daily-','weekly-','monthly-')):archives.append({'name':path.stem,'url':'../reports/'+path.name})
 payload={'generated_at':now.isoformat(),'mode':'extractive_no_ai','source_status':statuses,'events':records,'runs':runs,'archives':archives}
 atomic(ROOT/'outputs/monitor-data.json',json.dumps(payload,ensure_ascii=False,indent=2))
 report=ROOT/'outputs/competitor-research-complete.html'
 if report.exists():
  page=report.read_text()
  sections={
   'updates':'<header><h1>动态与口碑线索</h1><p>最近检查：'+escaped(now.isoformat())+'。原文摘录／规则提取，非 AI 摘要。来源失败不代表没有变化。</p></header><details><summary>来源状态与覆盖范围</summary>'+''.join('<p>'+escaped(x['id'])+'：'+escaped(x['status'])+' · '+escaped(x.get('error',str(x['count'])+' 条'))+'</p>' for x in statuses)+'</details>'+cards([e for e in records if e['product']!='market'][:100]),
   'reports':'<header><h1>报告归档</h1><p>日报与当前周／月的采集汇总。当前周期会更新，每次生成的 HTML 修订版保留在 reports/revisions；尚未生成 AI 趋势分析。</p></header><ul>'+''.join('<li><a href="'+escaped(x['url'])+'">'+escaped(x['name'])+'</a> · <a href="'+escaped(x['url'].replace('.html','.md'))+'">Markdown</a></li>' for x in archives)+'</ul>',
   'discover':'<header><h1>新产品观察</h1><p>以下是检索候选线索，可能包含已有产品更新；未经核验，不自动加入 9 个竞品。</p></header>'+cards([e for e in records if e['product']=='market'][:40])}
  for key,body in sections.items():
   marker=f'<!-- monitor:{key}:start -->';ending=f'<!-- monitor:{key}:end -->'
   if marker in page:
    a=page.index(marker)+len(marker);b=page.index(ending,a);page=page[:a]+body+page[b:]
   else:
    from html.parser import HTMLParser
    class PanelParser(HTMLParser):
     def __init__(self):
      super().__init__();self.depth=0;self.start=None;self.end=None;self.lines=page.splitlines(keepends=True)
     def offset(self):
      line,col=self.getpos();return sum(map(len,self.lines[:line-1]))+col
     def handle_starttag(self,tag,attrs):
      if tag!='div':return
      if self.depth:self.depth+=1
      elif dict(attrs).get('id')=='site-'+key:self.start=self.offset()+len(self.get_starttag_text());self.depth=1
     def handle_endtag(self,tag):
      if tag=='div' and self.depth:
       self.depth-=1
       if not self.depth:self.end=self.offset()
    parser=PanelParser();parser.feed(page)
    if parser.start is None or parser.end is None:raise ValueError('Missing monitor panel '+key)
    page=page[:parser.start]+marker+body+ending+page[parser.end:]
  atomic(report,page)
 sys.path.insert(0,str(Path(__file__).resolve().parent))
 from digest import publish
 publish(day,root=ROOT)
 return len(records)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--offline',action='store_true');args=ap.parse_args()
 for folder in ['data','reports','outputs']:(ROOT/folder).mkdir(exist_ok=True)
 with (ROOT/'data/monitor.lock').open('w') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:print('Another run is active');return
  now=datetime.now(TZ);config=json.loads((ROOT/'monitor/sources.json').read_text());c=connect(ROOT/'data/monitor.sqlite3');statuses=[]
  sources=[s for s in config['sources'] if s.get('enabled')]
  results=[(s,[],{'status':'skipped','count':0,'error':'offline mode'}) for s in sources] if args.offline else list(concurrent.futures.ThreadPoolExecutor(max_workers=5).map(fetch,sources))
  for source,entries,result in results:
   result.update(id=source['id'],url=source['url'],checked_at=now.isoformat(),coverage=source['note'])
   if result['status']=='ok':
    added=ingest(c,source,entries,now);result['new_records']=len(added)
   prev=c.execute('SELECT last_success FROM sources WHERE id=?',(source['id'],)).fetchone();result['last_success']=prev[0] if prev else None;statuses.append(result)
  # Manual records use the same schema and explicit product / source link.
  manual=ROOT/'monitor/manual.jsonl'
  if manual.exists():
   for line in manual.read_text().splitlines():
    if not line.strip():continue
    x=json.loads(line)
    if x['product'] not in {p['id'] for p in config['products']} or not safe_url(x['url']):raise ValueError('Invalid manual record')
    source={'id':'manual','product':x['product'],'category':x.get('category','feedback')}
    ingest(c,source,[item(source,x['url'],x['title'],x['excerpt'],x['url'],x.get('published_at'))],now)
  run={'at':now.isoformat(),'sources':statuses};c.execute('INSERT INTO runs VALUES(?,?)',(now.isoformat(),json.dumps(run,ensure_ascii=False)));c.commit()
  count=render(c,config,now,statuses);c.close()
  failures=sum(x['status']=='error' for x in statuses)
  atomic(ROOT/'data/latest-run.json',json.dumps({'at':now.isoformat(),'total_records':count,'errors':failures,'sources':statuses},ensure_ascii=False,indent=2))
  print(json.dumps({'total_records':count,'sources':len(statuses),'errors':failures,'report':str(ROOT/'outputs/competitor-research-complete.html')},ensure_ascii=False))
  subprocess.run([sys.executable,str(ROOT/'work/ui-prototype/build.py')],check=True)
  if failures==len(statuses):raise SystemExit(2)
if __name__=='__main__':main()
