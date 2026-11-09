#!/usr/bin/env python3
"""Editorial daily publication, backed by explicit evidence IDs."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse,json,html,re,sys
ROOT=Path(__file__).resolve().parents[1]
NAMES={'notebook':'NotebookLM','ima':'ima','lexiang':'乐享知识库','weknora':'WeKnora','chatgpt':'ChatGPT','workbuddy':'WorkBuddy','doubao':'豆包','patsnap':'智慧芽','xinghe':'星河智源','market':'市场观察'}
def esc(value):return html.escape(str(value or ''),quote=True)
def url(value):return value if str(value).startswith(('https://','http://')) else ''
def write(path,text):
 sys.path.insert(0,str(ROOT/'monitor'))
 from collect import atomic
 atomic(path,text)
def candidates(events,day):
 rows=[e for e in events if e['first_seen'][:10]==day]
 chosen=[]
 aliases={'notebook':r'notebooklm|gemini notebook','ima':r'\bima\b','lexiang':'乐享','weknora':'weknora','chatgpt':'chatgpt','workbuddy':'workbuddy','doubao':'豆包','patsnap':'智慧芽','xinghe':'星河智源'}
 for e in rows:
  if e['classification'] in ('历史补录','首次采集基线'):continue
  if e['category']=='news_lead' and not re.search(aliases.get(e['product'],r'(?!)'),e['title'],re.I):continue
  if e['category']=='review' and len(e['excerpt'])<18:continue
  chosen.append(e)
 return rows,chosen

def validate(editorial,events,day):
 assert editorial['date']==day,'Edition date mismatch'
 assert 0<=len(editorial['articles'])<=8,'Need 0–8 focused articles'
 assert (1<=len(editorial['takeaways'])<=3) if editorial['articles'] else not editorial['takeaways'],'Need takeaways only when there are articles'
 ids=set()
 for a in editorial['articles']:
  assert re.fullmatch('[a-z0-9-]+',a['id']) and a['id'] not in ids,'Invalid article ID'
  ids.add(a['id']);assert a['product'] in NAMES
  for field in ['section','badge','title','summary','meaning','next','limits']:assert a.get(field),'Missing '+field
  assert a['evidence_ids'],'Missing evidence'
  for key in a['evidence_ids']:
   assert key in events,'Unknown evidence '+key
   assert events[key]['first_seen'][:10]<=day,'Future evidence'
  for quote in a.get('quotes',[]):
   assert quote['id'] in a['evidence_ids'],'Quote evidence not linked'
   assert quote['text'] and quote['text'] in events[quote['id']]['excerpt'],'Quote not verbatim'
 for t in editorial['takeaways']:assert t['article'] in ids

CSS='''
:root{--ink:#172b35;--muted:#52636b;--line:#d9e2df;--green:#006b5c;--paper:#fff;--bg:#f4f6f5}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.85 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}a{color:var(--green);text-underline-offset:4px}a:focus-visible,summary:focus-visible{outline:3px solid #a74b20;outline-offset:4px}.shell{max-width:1080px;margin:auto;padding:32px 28px 72px}.top{display:flex;justify-content:space-between;gap:16px;align-items:center;border-bottom:1px solid var(--line);padding-bottom:20px}.top a{padding:8px 0;min-height:44px}.brand{font-weight:700;letter-spacing:1px}.hero{padding:40px 0 24px}.eyebrow{color:var(--green);font-weight:650;font-size:13px;letter-spacing:1px}h1{font-size:clamp(30px,4.3vw,48px);line-height:1.3;letter-spacing:-1px;max-width:850px;margin:14px 0 20px}.intro{font-size:18px;max-width:850px}.muted,.meta{color:var(--muted);font-size:13px}.takeaways{background:#eaf4f0;border-left:4px solid var(--green);padding:22px 28px;margin:8px 0 32px}.takeaways h2{font-size:19px;margin:0 0 8px}.takeaways li{margin:10px 0}.jump{display:flex;gap:12px;flex-wrap:wrap;margin:0 0 22px}.jump a{padding:8px 14px;background:white;border:1px solid var(--line);border-radius:6px;min-height:44px}.story{background:white;border:1px solid var(--line);border-radius:12px;padding:30px 36px;margin:20px 0;scroll-margin-top:24px}.story h2{font-size:clamp(23px,3vw,29px);line-height:1.5;margin:14px 0}.badge{display:inline-block;padding:3px 9px;background:#edf2ef;color:#355447;font-size:12px;border-radius:4px;margin-left:9px}.summary{font-size:18px}.facts{padding-left:22px}.facts li{margin:8px 0}.meaning{border-left:3px solid #7da897;padding:1px 0 1px 18px;margin:20px 0}.meaning strong,.next strong{color:var(--green)}blockquote{margin:12px 0;padding:12px 18px;background:#f6f8f7;border-left:2px solid var(--line)}blockquote p{margin:0}details{margin-top:18px;border-top:1px solid var(--line)}summary{cursor:pointer;min-height:44px;padding:10px 0;color:var(--green);font-weight:600}.evidence{padding:16px 0;border-top:1px solid var(--line);font-size:14px;overflow-wrap:anywhere}.evidence p{margin:8px 0}.bottom{padding:24px 0;border-top:1px solid var(--line);margin-top:32px}.health{font-size:14px;padding-left:20px}.empty{background:white;padding:30px;border:1px solid var(--line);border-radius:12px}.candidate{padding:20px 0;border-bottom:1px solid var(--line)}@media(max-width:650px){.shell{padding:20px 16px 40px}.top{align-items:flex-start;flex-wrap:wrap}.hero{padding-top:28px}.story{padding:22px 20px}.takeaways{padding:18px 20px}.badge{margin-left:0;display:table;margin-top:6px}.intro,.summary{font-size:16px}}@media print{body{background:white}.shell{padding:0;max-width:none}.jump{display:none}.story{break-inside:avoid;border:0;padding:10px 0}.top a{display:none}}
'''

def publish(day,root=None):
 root=Path(root) if root is not None else ROOT
 data=json.loads((root/'outputs/monitor-data.json').read_text())
 byid={e['id']:e for e in data['events']};rows,selected=candidates(data['events'],day)
 day_runs=[r for r in data.get('runs',[]) if r['at'][:10]==day]
 assert day_runs,'No run for this date; do not fabricate coverage'
 latest=max(day_runs,key=lambda r:r['at']);statuses=latest['sources'];cutoff=latest['at']
 packet={'date':day,'cutoff':cutoff,'source_status':statuses,'total_newly_seen':len(rows),'candidate_count':len(selected),'candidates':selected}
 write(root/'reports'/('candidates-'+day+'.json'),json.dumps(packet,ensure_ascii=False,indent=2))
 # Evidence appendix contains all newly seen records, including excluded/noisy ones.
 def evidence(e):
  return '<div class="evidence" id="e-'+esc(e['id'])+'"><strong>'+esc(NAMES.get(e['product'],e['product']))+' · '+esc(e['title'])+'</strong><p>'+esc(e['excerpt'])+'</p><div class="meta">'+esc(e['category'])+' · '+esc(e['classification'])+' · 发布 '+esc(e.get('published_at') or '未知')+' · 首次发现 '+esc(e['first_seen'])+(' · 版本 '+esc(e.get('version')) if e.get('version') else '')+(' · 原始评分 '+esc(e['rating']) if e.get('rating') else '')+'<br>证据 ID：'+esc(e['id'])+'</div><a href="'+esc(url(e['url']))+'" target="_blank" rel="noopener">原始来源</a>'+('<p class="meta">应用商店链接可能指向评论列表；单条记录以证据 ID 和已采集原文定位。</p>' if e['category']=='review' else '')+'</div>'
 appendix='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>采集附录 '+day+'</title><style>'+CSS+'</style><main class="shell"><a href="daily-'+day+'.html">返回编辑日报</a><h1>采集附录 · '+day+'</h1><p>完整保留 '+str(len(rows))+' 条当日新入库记录。包含历史补录、低信息量短评与待筛选新闻，不表示每条都值得作为日报结论。</p>'+''.join(evidence(e) for e in rows)+'</main></html>'
 write(root/'reports'/('evidence-'+day+'.html'),appendix)
 editorial_path=root/'monitor/editorials'/(day+'.json')
 editorial=json.loads(editorial_path.read_text()) if editorial_path.exists() else None
 top='<div class="top"><span class="brand">竞品观察 / DAILY BRIEF</span><a href="../outputs/competitor-research-complete.html#section-reports">返回研究站</a></div>'
 md=[]
 if editorial:
  validate(editorial,byid,day)
  title=editorial['headline']
  body='<header class="hero"><div class="eyebrow">'+day+' · 竞品日报 · 编辑版</div><h1>'+esc(title)+'</h1><p class="intro">'+esc(editorial['intro'])+'</p><p class="meta">采集截止 '+esc(cutoff)+' · '+str(len(editorial['articles']))+' 个主题 · 基于已采集证据编辑</p></header>'
  body+=('<section class="takeaways"><h2>今日要点</h2><ol>'+''.join('<li><a href="#'+esc(t['article'])+'">'+esc(t['text'])+'</a></li>' for t in editorial['takeaways'])+'</ol></section>') if editorial['takeaways'] else ''
  groups=list(dict.fromkeys(a['section'] for a in editorial['articles']))
  body+='<nav class="jump" aria-label="日报主题">'+''.join('<a href="#'+next(a['id'] for a in editorial['articles'] if a['section']==g)+'">'+esc(g)+'</a>' for g in groups)+'</nav>'
  md=['# '+day+' 竞品日报：'+title,editorial['intro'],'## 今日重点']+[str(i+1)+'. '+t['text'] for i,t in enumerate(editorial['takeaways'])]
  for a in editorial['articles']:
   body+='<article class="story" id="'+a['id']+'"><div class="eyebrow">'+esc(a['section'])+' / '+esc(NAMES[a['product']])+'<span class="badge">'+esc(a['badge'])+'</span></div><h2>'+esc(a['title'])+'</h2><p class="summary">'+esc(a['summary'])+'</p><ul class="facts">'+''.join('<li>'+esc(x)+'</li>' for x in a['observations'])+'</ul>'
   for q in a.get('quotes',[]):
    e=byid[q['id']];body+='<blockquote><p>“'+esc(q['text'])+'”</p><span class="meta">原文节选 · '+esc(e.get('published_at','')[:10])+' · '+esc(e.get('version',''))+'</span></blockquote>'
   body+='<div class="meaning"><strong>为什么值得关注</strong><p>'+esc(a['meaning'])+'</p></div><p class="next"><strong>下一步看什么：</strong>'+esc(a['next'])+'</p><p class="muted">'+esc(a['limits'])+'</p><details><summary>查看 '+str(len(a['evidence_ids']))+' 条来源与原文</summary>'+''.join(evidence(byid[k]) for k in a['evidence_ids'])+'</details></article>'
   md+=['## '+a['title'],a['badge'],a['summary']]+['- '+x for x in a['observations']]+['**为什么值得关注：** '+a['meaning'],'**下一步看什么：** '+a['next'],'**边界：** '+a['limits']]+['来源 '+k+'：<'+byid[k]['url']+'>' for k in a['evidence_ids']]
 else:
  title='今日候选已到齐，等待编辑提炼'
  body='<header class="hero"><div class="eyebrow">'+day+' · 自动候选稿</div><h1>'+title+'</h1><p class="intro">本页尚未经过主题归纳。自动过滤历史补录、无产品名的新闻标题和低信息量短评后，保留 '+str(len(selected))+' 条候选；不把采集数量当作重要性。</p></header><div class="empty"><h2>待编辑，不自动凑结论</h2><p>确认来源、合并同一事件，再写清变化、用户场景和边界。下列最多 6 条仅为候选预览，按类型和时间排列，并非重要性排名。</p>'
  preview=sorted(selected,key=lambda e:({'release':0,'feedback':1,'news_lead':2,'review':3,'discovery':4,'discussion':5}.get(e['category'],6),e.get('published_at') or ''))[:6]
  for e in preview:body+='<div class="candidate"><strong>'+esc(NAMES[e['product']])+' · '+esc(e['title'])+'</strong><p>'+esc(e['excerpt'][:220])+'</p><a href="'+esc(url(e['url']))+'">待核验来源</a></div>'
  body+='</div>';md=['# '+day+' 竞品日报（自动候选稿）','尚未完成编辑；不生成无证据结论。',f'{len(selected)} 条候选，完整记录见采集附录。']
 good=sum(s['status']=='ok' for s in statuses);zero=[s['id'] for s in statuses if s['status']=='ok' and not s['count']]
 health='<p>'+str(good)+' / '+str(len(statuses))+' 个来源成功响应。'+('零样本：'+esc('、'.join(zero))+'。' if zero else '')+'成功或零样本都不代表完整覆盖。</p><ul class="health">'+''.join('<li>'+esc(s['id'])+' · '+esc(s['status'])+' · '+str(s['count'])+' 条'+(' · '+esc(s['error']) if s.get('error') else '')+'</li>' for s in statuses)+'</ul>'
 body+='<footer class="bottom"><p><a href="evidence-'+day+'.html">查看全部 '+str(len(rows))+' 条采集记录</a> · <a href="daily-'+day+'.md">Markdown 版本</a></p><details><summary>采集范围与运行状态</summary>'+health+'</details><p class="muted">正文区分用户自述、媒体线索与编辑分析。评论样本不代表总体满意度；issue 不等于已确认缺陷。未调用独立 AI API；本期'+('由 Codex 会话基于证据编辑。' if editorial else '尚待编辑。')+'</p></footer>'
 document='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(day+' 竞品日报 · '+title)+'</title><style>'+CSS+'</style></head><body><main class="shell">'+top+body+'</main></body></html>'
 path=root/'reports'/('daily-'+day+'.html')
 write(path,document);write(path.with_suffix('.md'),'\n\n'.join(md)+'\n\n采集附录：evidence-'+day+'.html\n')
 revision=root/'reports/revisions'/('daily-'+day+'-editorial-'+datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%dT%H%M%S%f')+'.html');write(revision,document)
 # Refresh only the archive links; preserve all product content and other panels.
 report=root/'outputs/competitor-research-complete.html'
 if report.exists():
  page=report.read_text();start='<!-- monitor:reports:start -->';end='<!-- monitor:reports:end -->'
  if start in page:
   entries=[]
   for f in sorted((root/'reports').glob('*.html'),reverse=True):
    if not f.name.startswith(('daily-','weekly-','monthly-')):continue
    label=('编辑日报' if (root/'monitor/editorials'/(f.stem[6:]+'.json')).exists() else '候选日报') if f.name.startswith('daily-') else '采集汇总'
    entries.append('<li><a href="../reports/'+f.name+'">'+esc(f.stem)+' · '+label+'</a></li>')
   content='<header><h1>报告归档</h1><p>日报按主题精选；完整采集记录移入附录。周报、月报暂保留采集汇总，尚未完成编辑升级。</p></header><ul>'+''.join(entries)+'</ul>'
   a=page.index(start)+len(start);b=page.index(end,a);write(report,page[:a]+content+page[b:])
 print(json.dumps({'date':day,'status':'edited' if editorial else 'pending_editorial','raw_records':len(rows),'candidates':len(selected),'articles':len(editorial['articles']) if editorial else 0,'path':str(path)},ensure_ascii=False))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--date',required=True);args=parser.parse_args();datetime.strptime(args.date,'%Y-%m-%d');publish(args.date)
