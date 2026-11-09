from pathlib import Path
import re,json,html,sys
sys.path.append(str(Path(__file__).resolve().parents[2]/"monitor"))
from observation import news_records
from collect import atomic
from digest import make_reports
from feedback import make_feedback
from perceptions import make_perceptions
R=Path(__file__).resolve().parents[2];W=R/'work/ui-prototype'
s=(R/'outputs/competitor-research-complete.html').read_text();original=s
names={'notebook':'Gemini Notebook','ima':'ima','lexiang':'乐享知识库','weknora':'WeKnora','chatgpt':'ChatGPT','workbuddy':'WorkBuddy','doubao':'豆包','patsnap':'智慧芽','xinghe':'星河智源'}
data=json.loads((R/'outputs/monitor-data.json').read_text());events=news_records(data,names)
proto=dict(schema_version=1,source_status=data['source_status'],names=names,events=events,cutoff=data['generated_at'],reports=make_reports(R),feedback=make_feedback(data),perceptions=make_perceptions(data))
def icon(i):
 paths=['<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M12 4v16M4 12h16"/>','<path d="M9 6h12M9 12h12M9 18h12M3 6h1M3 12h1M3 18h1"/>','<path d="M4 19V5m0 14h17M8 15l4-5 4 2 5-7"/>','<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6m-6 4h6m-6 4h4"/>','<circle cx="10" cy="10" r="6"/><path d="m15 15 6 6"/>']
 return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">'+paths[i]+'</svg>'
nav=''
for i,(k,label) in enumerate([('competitors','竞品研究'),('updates','全部竞品动态'),('digest','竞品日报'),('feedback','用户反馈'),('strategy','战略分析')]):
 nav+='<a href="#'+('product-notebook' if k=='competitors' else 'section-'+k)+'" data-section="'+k+'">'+icon(i%5)+'<span>'+label+'</span></a>'
sidebar='<aside class="app-sidebar"><a class="app-brand" href="#section-updates"><span class="brand-dot"></span>竞品观察</a><div class="app-caption">PRODUCT INTELLIGENCE</div><div class="nav-label">工作台</div><nav aria-label="主导航">'+nav+'</nav><div class="side-bottom"><div class="app-status"><i></i>数据采集状态</div><p>9 个产品 · API / RSS<br><span id=live-updated>读取最新数据中</span></p><a href="competitor-research-complete.html#section-updates">返回现有版本 ↗</a><a href="aihot-prototype-notice.html">开源来源与适配说明 ↗</a></div></aside>'
products='<button data-filter-product="all" aria-pressed="true">全部产品</button>'+''.join('<button data-filter-product="'+k+'" aria-pressed="false">'+v+'</button>' for k,v in names.items())
news='<header class="page-heading"><div><h1>全部竞品动态</h1><p>关注产品发布、功能更新与行业应用，按原始发布时间排列。</p></div><div class="edition">9 PRODUCTS<br>NEWS TIMELINE</div></header><div class="feed-toolbar"><div class="type-pills" role="group" aria-label="按产品筛选">'+products+'</div><label class="search-field">'+icon(4)+'<input id="search-news" type="search" aria-label="搜索标题、摘要、产品或发布机构" placeholder="搜索标题、产品、发布机构…"></label></div><div class="filter-meta"><span id="feed-count" role="status" aria-live="polite"></span><div class="date-range"><label for="date-from">日期</label><input type="date" id="date-from" aria-label="开始日期"><span>至</span><input type="date" id="date-to" aria-label="结束日期"><button class="quiet-button" id="reset-news">重置</button></div></div><div class="feed-notice"><details><summary id="source-summary">来源更新状态</summary><div id="source-health"></div></details></div><div id="news-feed"></div><div class="more-row"><button id="more-news" hidden>加载更多动态</button></div><p class="feed-end">按发布日归档 · 标题与摘录保留出处 · 不以采集时间冒充新闻时间</p>'
s=s.replace('</head>','<style>'+(W/'prototype.css').read_text()+(W/'digest.css').read_text()+(W/'feedback.css').read_text()+'</style></head>',1)
s=re.sub('<title>.*?</title>','<title>竞品观察</title>',s,count=1)
a=s.index('<header class=product-header>');b=s.index('<aside>',a);c=s.index('</aside>',b)+len('</aside>')
header=s[a:b];switcher=header[header.index('<div id=product-switcher>'):].rsplit('</header>',1)[0]
chapters=''.join(re.findall(r'<nav.*?</nav>',s[b:c],re.S));s=s[:a]+sidebar+s[c:]
pos=re.search(r'<main[^>]*>',s).end()
top='<div class="app-top"><span>工作台 / <b id="breadcrumb">全部竞品动态</b><strong class="prototype-tag" id="live-status" role="status">已保存数据</strong></span><a href="competitor-research-complete.html">原有研究内容完整保留 ↗</a></div>'+switcher+'<details class="research-toc"><summary>研究章节目录</summary>'+chapters+'</details>'
s=s[:pos]+top+s[pos:]
a=s.index('<!-- monitor:updates:start -->')+len('<!-- monitor:updates:start -->');b=s.index('<!-- monitor:updates:end -->',a);s=s[:a]+news+s[b:]
digest_panel=(W/'digest.html').read_text()
feedback_panel=(W/'perceptions.html').read_text().replace('FEEDBACK_OPTIONS',''.join('<option value='+k+'>'+v+'</option>' for k,v in names.items())).replace('FEEDBACK_CUTOFF',data['generated_at'][:16].replace('T',' '))
s=s.replace('</main>',digest_panel+feedback_panel+'</main>',1)
scripts=re.findall(r'<script[^>]*>(.*?)</script>',s,re.S);zoom=next(x for x in scripts if 'const uiDialog=' in x)
s=re.sub(r'<script[^>]*>.*?</script>','',s,flags=re.S)
js='const PROTOTYPE='+json.dumps(proto,ensure_ascii=False).replace('<',chr(92)+'u003c')+';'+chr(10)+(W/'prototype.js').read_text()+chr(10)+(W/'issue-calendar.js').read_text()+chr(10)+(W/'digest.js').read_text()+chr(10)+(W/'perceptions.js').read_text()+chr(10)+(W/'live.js').read_text()
s=s.replace('</body>','<dialog class="news-dialog" id="news-detail" aria-label="动态来源详情"><div class="dialog-top"><span>发布内容 / 证据</span><button id="close-news">关闭 ×</button></div><div id="detail-body"></div></dialog><script>'+zoom+'</script><script>'+js+'</script></body>')
def panels(t):return {m.group(1):m.group(2) for m in re.finditer(r'<article id=.?((?:panel-)[a-z]+)[^>]*>(.*?)</article>',t,re.S)}
assert len(panels(s))==10 and panels(s)==panels(original)
# Keep the source report's archive and discovery records on disk, but remove those
# workbench panels from this active prototype as requested. Marker endings make the
# top-level removal safe even when the panel contains nested divs.
for obsolete in ('reports','discover'):
 start=s.index('<div id="site-'+obsolete+'"')
 marker=s.index('<!-- monitor:'+obsolete+':end -->',start)
 close=s.index('</div>',marker)+len('</div>')
 s=s[:start]+s[close:]
for key,label in [('competitors','竞品研究'),('updates','全部竞品动态'),('strategy','战略分析')]:
 s=s.replace('aria-labelledby="site-tab-'+key+'"','aria-label="'+label+'"')
atomic(R/'outputs/competitor-ui-prototype.html',s)
atomic(R/'outputs/prototype-news.json',json.dumps(proto,ensure_ascii=False,indent=2))
atomic(R/'outputs/observation.json',json.dumps(proto,ensure_ascii=False))
license=(R/'LICENSE').read_text();notice=(R/'NOTICE').read_text()
(R/'outputs/aihot-prototype-notice.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>原型适配说明</title><style>body{max-width:850px;margin:50px auto;padding:24px;font:16px/1.8 system-ui}pre{white-space:pre-wrap}</style><a href="competitor-ui-prototype.html">返回原型</a><h1>前端适配说明</h1><p>基于 <a href="https://github.com/KKKKhazix/AIHOT">KKKKhazix/AIHOT</a>，提交 aa8e5b1bc4895267f98abe59c87dfed8a22bf35f。</p><p>沿用 app.css 色彩变量，依据 Sidebar.tsx、routes/all.tsx、DayList.tsx、Timeline.tsx、FeedItem.tsx，以及报告页 ReportLayout.tsx、ReportNav.tsx、ReportPaper.tsx、IssueDots.tsx 与 Halftone.tsx 的结构适配为本地 HTML / JavaScript 原型。尚未部署完整 React / API / worker。使用自己的站名。</p><p>现有研究正文与截图不变；新闻为真实采集样本，媒体正文核验与官号接入尚未完成。未改变当前定时采集，也未对外发布。</p><h2>MIT License</h2><pre>'+html.escape(license)+'</pre><h2>NOTICE</h2><pre>'+html.escape(notice)+'</pre></html>')
print('Generated observation website with live collection records; all original research panels unchanged.')
