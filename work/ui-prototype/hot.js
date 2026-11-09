const HOT=PROTOTYPE.hot;
const hotProduct=document.getElementById('hot-product');
const hotDate=s=>s.slice(0,16).replace('T',' ');
function hotVoices(e){return `<div class="hot-voices"><div class="hot-faces" aria-hidden="true">${e.channels.slice(0,4).map(c=>`<span>${esc(c[0])}</span>`).join('')}</div>${esc(e.channels.join('、'))}<br>${e.source_count} 个发布渠道 · ${e.record_count} 条记录</div>`}
function hotScore(e){return `<div class="hot-number">${e.heat.toFixed(2)}<small>来源关注热度</small></div>`}
function hotCard(e,rank,lead){return `<article class="hot-card ${lead?'hot-lead':''}"><div class="hot-rankline"><span class="hot-rank">NO.${String(rank).padStart(2,'0')}</span><span class="hot-tag">${e.source_count>1?'多渠道线索':'单渠道线索'}</span><span class="hot-product">${esc(PROTOTYPE.names[e.product])}</span></div><h2><button class="headline-button" data-hot-detail="${e.id}">${esc(e.title)}</button></h2><p>${e.has_discussion?'包含社区帖子；帖内说法尚未独立核实。':'按已采集标题归组，相关事实和转载关系仍待正文核验。'}${lead?'点击查看这个事件的报道与讨论来源。':''}</p>${lead?`<hr class="hot-divider"><p>最新记录 · ${hotDate(e.latest)}<br>${esc(e.evidence[0].title)}</p>`:''}<div class="hot-card-bottom">${hotVoices(e)}${hotScore(e)}</div></article>`}
function renderHot(){
 const rows=HOT.events.filter(e=>hotProduct.value==='all'||e.product===hotProduct.value).slice(0,10);
 document.getElementById('hot-summary').textContent=`过去 48 小时 · ${hotProduct.value==='all'?'九产品合并榜':PROTOTYPE.names[hotProduct.value]} · ${rows.length} 件事`;
 document.getElementById('hot-board').innerHTML=rows.length?`<div class="hot-top">${rows.slice(0,3).map((e,i)=>hotCard(e,i+1,i===0)).join('')}</div>${rows.length>3?`<div class="hot-row-heading"><strong>继续看 <span>No.04–${String(rows.length).padStart(2,'0')}</span></strong><span>发布渠道 · 来源关注热度</span></div><ol class="hot-list" start="4">${rows.slice(3).map((e,i)=>`<li class="hot-row"><span class="hot-rank">${String(i+4).padStart(2,'0')}</span><div><h3><button class="headline-button" data-hot-detail="${e.id}">${esc(e.title)}</button></h3><p>${esc(PROTOTYPE.names[e.product])} · 最新 ${hotDate(e.latest)} · ${e.record_count} 条记录</p></div>${hotVoices(e)}${hotScore(e)}</li>`).join('')}</ol>`:''}<p class="hot-remaining">${rows.length<10?'当前范围不足 10 件事，按已有证据展示，不补造名次。':'展示当前原型归组样本中热度最高的 10 件事。'} 无可比历史，暂不显示涨跌与走势。</p>`:'<div class="hot-empty"><h2>这个产品暂没有符合窗口的事件样本</h2><p>不代表没有讨论；当前来源覆盖与事件归组尚不完整。</p></div>';
 document.querySelectorAll('[data-hot-detail]').forEach(b=>b.onclick=()=>openHot(b.dataset.hotDetail));
}
function openHot(id){
 const e=HOT.events.find(e=>e.id===id);
 document.getElementById('hot-detail-body').innerHTML=`<div class="hot-kicker">48H / 事件详情</div><h2>${esc(e.title)}</h2><p>${esc(PROTOTYPE.names[e.product])} · ${e.source_count} 个发布渠道 · ${e.record_count} 条窗口内记录 · 热度 ${e.heat.toFixed(2)}</p><p class="note">${esc(HOT.method)} 媒体署名为 RSS 所示，转载同源关系未全部核实；不能视为独立机构或独立用户人数。</p>${e.has_discussion?`<p class="note">本窗口内帖子采集时累计评论合计 ${e.comments_snapshot} 条，仅供上下文；没有评论时间明细，不当作 48 小时新增评论，也不计入排名。</p>`:''}${e.evidence.map(r=>`<div class="hot-evidence"><small>${esc(r.publisher)} · ${hotDate(r.published_at)} · ${r.category==='discussion'?'社区讨论':'媒体线索'}</small><h3>${esc(r.title)}</h3>${r.excerpt?`<p>${esc(r.excerpt)}</p>`:'<p class="note">当前只有帖子标题，正文未采集。</p>'}<small>证据 ID：${esc(r.id)}</small><p><a href="${esc(r.url)}" target="_blank" rel="noopener noreferrer">查看来源 ↗</a></p></div>`).join('')}`;
 document.getElementById('hot-detail').showModal();
}
hotProduct.onchange=renderHot;document.getElementById('close-hot').onclick=()=>document.getElementById('hot-detail').close();
document.getElementById('hot-method-button').onclick=()=>{const d=document.getElementById('hot-method');d.open=true;d.scrollIntoView({block:'start'})};
renderHot();
