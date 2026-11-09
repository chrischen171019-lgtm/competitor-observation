from pathlib import Path
import re
R=Path(__file__).resolve().parents[2];p=R/'outputs/competitor-research-complete.html';s=p.read_text()
a=s.index('<article id=panel-strategy>');b=s.index('</article>',a)+len('</article>');v=s[a:b]
for key in ['feedback','trajectory','nextsteps']:
 v,n=re.subn(r'<section id="'+key+r'">.*?</section>','',v,count=1,flags=re.S);assert n==1
v,n=re.subn(r'<section id="opportunity">.*?</section>',lambda m:(R/'work/ui-prototype/opportunity.html').read_text(),v,count=1,flags=re.S);assert n==1
v=v.replace('本页补充五个战略维度，回答"竞品研究结果对产品决策意味着什么"。','本页保留商业模式与定价、护城河分析和战略机会地图。用户反馈独立维护，产品变化见动态栏目。')
a1=v.index('<section id="overview">');b1=v.index('</section>',a1)+len('</section>')
intro='<section id="overview"><h2><span class="num">00</span>分析框架说明</h2><p>战略页聚焦商业机制、竞争壁垒与机会假设。用户反馈和产品发布分别在独立栏目查看。</p><div class="callout"><p><strong>证据状态</strong></p><p>本次详细修订战略机会地图，将缺乏验证的市场空白和优先级判断改为具体场景、已有依据与反证条件。下方定价与护城河部分为历史草稿，本次未重新核验，其中套餐、价格、强弱判断不作为已确认事实或本次机会分析的依据。</p></div><p>产品研究正文保留原样；Innobook 功能差距尚需在竞品研究之后逐项核对。</p></section>'
v=v[:a1]+intro+v[b1:]
v=v.replace('<span class="num">13</span>','<span class="num">02</span>').replace('<span class="num">10</span>','<span class="num">01</span>')
v=v.replace('版本：补充稿 v0.1','版本：机会分析修订稿 v0.2').replace('本页为竞品研究战略补充稿 v0.1','本页为竞品研究战略补充稿 v0.2').replace('编写日期：2026.10.26','机会地图修订：2026.10.27')
s=s[:a]+v+s[b:]
nav='<nav id="strategy-nav" aria-label="战略分析导航" hidden><a href="#overview">00　分析框架说明</a><a href="#pricing">01　商业模式与定价</a><a href="#moat">02　护城河分析</a><a href="#opportunity">03　战略机会地图</a></nav>'
s,n=re.subn(r'<nav id="strategy-nav".*?</nav>',nav,s,count=1,flags=re.S);assert n==1
s=s.replace('<a href="#section-feedback">用户反馈</a>','<a href="competitor-ui-prototype.html#section-feedback">用户反馈</a>')
p.write_text(s)
print('Updated strategy: removed three sections; expanded five opportunity hypotheses.')
