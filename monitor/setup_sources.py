from pathlib import Path
import json,urllib.parse
products=[('notebook','NotebookLM','NotebookLM'),('ima','ima','腾讯 ima'),('lexiang','乐享知识库','腾讯 乐享 知识库'),('weknora','WeKnora','WeKnora'),('chatgpt','ChatGPT','ChatGPT'),('workbuddy','WorkBuddy','腾讯 WorkBuddy'),('doubao','豆包','豆包 AI'),('patsnap','智慧芽','智慧芽'),('xinghe','星河智源','星河智源')]
sources=[]
def add(id,product,kind,url,category,note,**kw):sources.append(dict(id=id,product=product,kind=kind,url=url,category=category,note=note,enabled=True,**kw))
for key,name,q in products:
 add(key+'-news',key,'rss','https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':q+' when:7d','hl':'zh-CN','gl':'CN','ceid':'CN:zh-Hans'}),'news_lead','新闻检索线索，不能视作用户口碑或已确认产品变化；名称和产品模块需核验。')
for key,appid in [('ima',6737188438),('workbuddy',6761374913),('doubao',6459478672)]:
 add(key+'-appstore-cn',key,'apple',f'https://itunes.apple.com/cn/rss/customerreviews/id={appid}/sortBy=mostRecent/json','review','2026-10-26 通过 Apple 搜索核对应用名与开发主体；仅中国区 iOS 最新有限样本，不代表全平台用户。',app_id=appid,region='CN')
add('weknora-releases','weknora','github_releases','https://api.github.com/repos/Tencent/WeKnora/releases?per_page=20','release','官方发布记录；首次采集为基线，不等于今天发布。')
add('weknora-issues','weknora','github_issues','https://api.github.com/repos/Tencent/WeKnora/issues?state=all&sort=updated&direction=desc&per_page=30','feedback','开源仓库问题反馈；过滤 PR，issue 可能是提问或功能请求，并非全部为缺陷。')
for key,q in [('notebook','NotebookLM'),('chatgpt','ChatGPT')]:
 add(key+'-hn',key,'hn','https://hn.algolia.com/api/v1/search_by_date?'+urllib.parse.urlencode({'query':q,'tags':'story','hitsPerPage':30}),'discussion','技术社区帖子线索；提及产品不等于使用评价，未采集全部评论。',keyword=q)
add('new-products-news','market','rss','https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':'("AI知识库" OR "AI智能体") (发布 OR 上线) when:7d','hl':'zh-CN','gl':'CN','ceid':'CN:zh-Hans'}),'discovery','新产品候选线索，发布报道可能是旧产品更新，不能自动加入竞品库。')
Path('monitor/sources.json').write_text(json.dumps({'products':[{'id':k,'name':n} for k,n,q in products],'sources':sources},ensure_ascii=False,indent=2))
