const $=s=>document.querySelector(s);
const allProducts=Object.entries(PROTOTYPE.names);
const productTabs=[...document.querySelectorAll('#product-tabs button')];
const sitePanels=[...document.querySelectorAll('main > div[role=tabpanel]')];
let selectedProduct='notebook',visibleLimit=12;
function route(){
 const hash=location.hash.slice(1);let section='updates';
 if(hash.startsWith('product-')&&PROTOTYPE.names[hash.slice(8)]){section='competitors';selectedProduct=hash.slice(8)}
 else if(hash.startsWith('section-'))section=hash.slice(8);
 else if(hash){const target=document.getElementById(hash);const p=target?.closest('#site-competitors > article');if(p){section='competitors';selectedProduct=p.id.slice(6)}else if(target?.closest('#site-strategy'))section='strategy';else if(target?.closest('#site-digest'))section='digest'}
 if(section==='hot'||section==='reports')section='digest';
 if(section==='discover')section='updates';
 if(!document.getElementById('site-'+section))section='updates';
 sitePanels.forEach(p=>p.hidden=p.id!=='site-'+section);
 document.body.dataset.siteSection=section;
 document.querySelectorAll('.app-sidebar [data-section]').forEach(a=>{if(a.dataset.section===section)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});
 $('#breadcrumb').textContent={updates:'全部竞品动态',digest:'竞品日报',feedback:'用户反馈',competitors:'竞品研究',strategy:'战略分析'}[section];
 $('#product-switcher').hidden=section!=='competitors';
 document.querySelectorAll('#site-competitors > article').forEach(p=>p.hidden=p.id!=='panel-'+selectedProduct);
 productTabs.forEach(b=>{const active=b.dataset.key===selectedProduct;b.setAttribute('aria-selected',active);b.tabIndex=active?0:-1});
 ['notebook','ima','strategy'].forEach(key=>$('#'+key+'-nav').hidden=key==='strategy'?section!=='strategy':section!=='competitors'||key!==selectedProduct);
 $('.research-toc').hidden=!(section==='strategy'||(section==='competitors'&&['notebook','ima'].includes(selectedProduct)));
 if(!hash||hash.startsWith('section-')||hash.startsWith('product-'))window.scrollTo(0,0);else requestAnimationFrame(()=>document.getElementById(hash)?.scrollIntoView());
}
productTabs.forEach((b,i)=>{b.onclick=()=>location.hash='product-'+b.dataset.key;b.onkeydown=e=>{let n;if(e.key==='ArrowRight')n=(i+1)%productTabs.length;if(e.key==='ArrowLeft')n=(i+productTabs.length-1)%productTabs.length;if(e.key==='Home')n=0;if(e.key==='End')n=productTabs.length-1;if(n!==undefined){e.preventDefault();productTabs[n].focus();productTabs[n].click()}}});
window.addEventListener('hashchange',route);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const state={product:'all',q:'',from:'',to:''};
function eligible(e){return (state.product==='all'||e.product===state.product)&&(!state.q||(e.title+e.excerpt+e.publisher+PROTOTYPE.names[e.product]).toLowerCase().includes(state.q.toLowerCase()))&&(!state.from||(e.published_at||'').slice(0,10)>=state.from)&&(!state.to||Boolean(e.published_at)&&(e.published_at||'').slice(0,10)<=state.to)}
function render(){
 const records=PROTOTYPE.events.filter(eligible).sort((a,b)=>(b.published_at||'').localeCompare(a.published_at||''));
 $('#feed-count').textContent=`${records.length} 条动态 · 发布时间倒序 · 北京时间`;
 const shown=records.slice(0,visibleLimit),days=[...new Set(shown.map(e=>(e.published_at||'日期待核验').slice(0,10)))];
 $('#news-feed').innerHTML=days.map(day=>{const entries=shown.filter(e=>(e.published_at||'日期待核验').startsWith(day));const weekday=day==='日期待核验'?'':new Date(day+'T12:00:00+08:00').toLocaleDateString('zh-CN',{weekday:'long',timeZone:'Asia/Shanghai'});return `<section class="feed-day" aria-label="${day}"><header class="day-header"><h2>${day==='日期待核验'?day:Number(day.slice(5,7))+'月'+Number(day.slice(8))+'日'}</h2><span>${weekday} · ${day==='日期待核验'?'':day.slice(0,4)}</span><span class="count">${entries.length} 条</span></header><ol class="feed-rows">${entries.map(e=>`<li class="feed-slot"><time datetime="${e.published_at||''}">${e.published_at?e.published_at.slice(11,16):'待核验'}</time><span class="time-rail" aria-hidden="true"></span><article class="news-card"><div class="news-source"><span class="source-avatar" aria-hidden="true">${esc(e.publisher.slice(0,1))}</span><span>${esc(e.publisher)}</span><span class="source-kind ${e.kind==='official'?'official':''}">${esc(e.sourceLabel)}</span><span class="product-name">${esc(PROTOTYPE.names[e.product])}</span></div><h3><button class="headline-button" data-detail="${e.id}">${esc(e.title)}</button></h3><p>${esc(e.preview)}</p><div class="news-foot"><span class="news-topic">${esc(e.topic)}</span><span class="evidence-state">${e.kind==='official'?'官方发布记录':'正文待核验'}</span><a href="${esc(e.url)}" target="_blank" rel="noopener noreferrer">${e.kind==='official'?'阅读原文':'查看来源（聚合链接）'} ↗</a></div></article></li>`).join('')}</ol></section>`}).join('')||'<div class="empty-feed"><h2>当前筛选下暂无动态记录</h2><p>这不代表该产品没有动态。可检查来源状态或调整筛选条件。</p><button class="quiet-button" id="empty-reset">清除筛选</button></div>';
 $('#empty-reset')?.addEventListener('click',reset);
 $('#more-news').hidden=records.length<=visibleLimit;
 document.querySelectorAll('[data-detail]').forEach(b=>b.onclick=()=>openDetail(b.dataset.detail));
}
function openDetail(id){const e=PROTOTYPE.events.find(x=>x.id===id);$('#detail-body').innerHTML=`<div class="news-source">${esc(PROTOTYPE.names[e.product])} · ${esc(e.publisher)} · ${esc(e.sourceLabel)}</div><h2>${esc(e.title)}</h2><p>${esc(e.preview)}</p><dl><dt>发布时间</dt><dd>${esc((e.published_at||'日期待核验').replace('T',' '))}（原始来源记录）</dd><dt>首次采集</dt><dd>${esc(e.first_seen)}</dd><dt>证据状态</dt><dd>${esc(e.classification)} · ${e.kind==='official'?'来自官方 GitHub Release；以下为截断摘录':'RSS 标题线索；发布主体和正文仍需核验'}</dd></dl><h3>已采集原文</h3><blockquote>${esc(e.excerpt)}</blockquote><p class="note">${e.kind==='official'?'完整更新说明请查看官方原文。':'当前摘要与标题内容重复，不扩写功能、客户关系或效果；聚合链接可能继续跳转至发布媒体。'}</p><a class="original" href="${esc(e.url)}" target="_blank" rel="noopener noreferrer">前往来源 ↗</a>`;$('#news-detail').showModal()}
$('#close-news').onclick=()=>$('#news-detail').close();
function bindFilters(){document.querySelectorAll('[data-filter-product]').forEach(b=>{b.setAttribute('aria-pressed',b.dataset.filterProduct===state.product);b.onclick=()=>{state.product=b.dataset.filterProduct;visibleLimit=12;bindFilters();render()}})}
function reset(){Object.assign(state,{product:'all',q:'',from:'',to:''});$('#search-news').value='';$('#date-from').value='';$('#date-to').value='';visibleLimit=12;bindFilters();render()}
$('#search-news').oninput=e=>{state.q=e.target.value;visibleLimit=12;render()};
$('#date-from').onchange=e=>{state.from=e.target.value;render()};$('#date-to').onchange=e=>{state.to=e.target.value;render()};$('#reset-news').onclick=reset;$('#more-news').onclick=()=>{visibleLimit+=12;render()};
bindFilters();render();route();
