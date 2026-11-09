"""Evidence-backed editorial event groups for the local hot-board prototype."""
from datetime import datetime,timedelta
GROUPS=[
('workbuddy-fde','workbuddy','WorkBuddy 在成都发布 FDE 人才培养计划',['fcfcd624936457bd60f2fe8c','64fd4ecbd292c6bd52f18dd4']),
('workbuddy-kimi','workbuddy','WorkBuddy 接入 Kimi-K3.1-Pro，相关报道持续出现',['a602f274ed1af1f3849ee301','69b43313ebf5d88044fc81d6','da1bf2fcf35265fa3743710d']),
('doubao-roewe','doubao','荣威家越 07 搭载豆包 AI 座舱的上市报道',['97a3eabe85d073b1807d9a1b','89e92f05f33fe22f67259767']),
('doubao-phone','doubao','AI 周评讨论豆包手机遭拒',['b5e9faee7ad3042d7c785d00','05276f9b26528b8bd3162353']),
('workbuddy-platform','workbuddy','WorkBuddy 开放平台上线的媒体报道',['2c3db46a4b8f1d41bf4b2940']),
('chatgpt-sweden','chatgpt','HN 讨论瑞典政府办公场景限制 ChatGPT',['35f93fe45b5c1d1e63bcd147','42f4fc1616b178b4fa02ca6c','60f86f650e57d0aad69bcd21']),
('chatgpt-404','chatgpt','ChatGPT 将技术支持问题指向 404 Media，引发 HN 讨论',['8e6d345f67ebb9311bc838fc']),
('chatgpt-webmcp','chatgpt','HN 帖子讨论将 WebMCP 接入 ChatGPT',['0add8e2a341f097b1173ca49']),
('workbuddy-scienceora','workbuddy','ScienceOra 科研智能体上线 WorkBuddy 的报道',['00603c7be03489fd34e4c7f7']),
('doubao-tob','doubao','飞书与豆包整合的 ToB 业务报道',['f48059f94735611cbbec307e']),
('doubao-work','doubao','媒体关注「豆包工作」上线与办公场景',['67887e129c6d5edaea2f3364']),
('doubao-creation','doubao','豆包工作中的创作项目使用分享',['c824b9961c3f52b36615fcfe']),
('doubao-paid','doubao','媒体报道豆包付费版与月活变化',['51fbf9a08d47afffbe1b71e1']),
('workbuddy-market','workbuddy','媒体评论 WorkBuddy 在办公 AI 市场的表现',['b8abea4ddb7ffa142d27caf3','1600c846a456a71d86ac7856']),
('chatgpt-capcut','chatgpt','CapCut 插件登陆 ChatGPT 的报道线索',['892371149d93400d6ffddf74']),
('doubao-agent','doubao','媒体讨论豆包智能体下架说法与 Agent 定位',['e6c8542c9c838abaf002d833']),
('notebook-skills','notebook','NotebookLM 视频与播客笔记的 Skill 使用分享',['de498b40b7199b46c34146ad']),
('chatgpt-language','chatgpt','用户询问 ChatGPT 会话标题出现错误语言',['e742330de1f206bcaad12435']),
]
ALIASES={'Sohu':'搜狐','搜狐网':'搜狐','36Kr':'36氪','finance.sina.com.cn':'新浪','新浪财经':'新浪','手机新浪网':'新浪','QQ News':'腾讯新闻'}
def channel(e):
 if e['id'] in ('b5e9faee7ad3042d7c785d00','05276f9b26528b8bd3162353'):return '爱分析周评（转载合并）'
 if e['category']=='discussion':return 'Hacker News'
 name=e['title'].rsplit(' - ',1)[-1]
 return ALIASES.get(name,name)
def rank_groups(events,cutoff,groups=GROUPS):
 end=datetime.fromisoformat(cutoff);start=end-timedelta(hours=48);byid={e['id']:e for e in events};ranked=[]
 for key,product,title,ids in groups:
  rows=[];seen=set()
  for eid in ids:
   if eid not in byid:raise ValueError('Missing evidence '+eid)
   e=byid[eid]
   if e['product']!=product:raise ValueError('Product mismatch '+eid)
   if not e.get('published_at'):continue
   at=datetime.fromisoformat(e['published_at'])
   if not start<=at<=end or datetime.fromisoformat(e['first_seen'])>end:continue
   identity=(channel(e),e['title'],e['published_at'])
   if identity in seen:continue
   seen.add(identity);rows.append(dict(e,publisher=channel(e)))
  if not rows:continue
  rows.sort(key=lambda e:e['published_at'],reverse=True);voices={}
  for e in rows:
   age=(end-datetime.fromisoformat(e['published_at'])).total_seconds()/3600
   voices[e['publisher']]=max(voices.get(e['publisher'],0),2**(-age/24))
  ranked.append(dict(id=key,product=product,title=title,heat=sum(voices.values()),channels=list(voices),source_count=len(voices),record_count=len(rows),latest=rows[0]['published_at'],evidence=rows,comments_snapshot=sum(e.get('comments',0) for e in rows if e['category']=='discussion'),has_discussion=any(e['category']=='discussion' for e in rows)))
 ranked.sort(key=lambda e:(-e['heat'],-datetime.fromisoformat(e['latest']).timestamp(),e['id']))
 for i,e in enumerate(ranked):e['rank']=i+1
 return dict(cutoff=cutoff,window_start=start.isoformat(),window_hours=48,mode='source_attention_proxy',events=ranked,limit=10,method='同一事件、同一发布渠道在 48 小时内取最近一条；热度为各渠道 2^(-距截止小时数/24) 的总和。HN 暂按一个平台计算，评论累计数不计入热度。')
