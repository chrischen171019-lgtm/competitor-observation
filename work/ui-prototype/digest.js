const reportTabs=[...document.querySelectorAll('[data-report-kind]')];
let reportKind='daily';
const reportSelection={};
const reportNames={daily:'日报',weekly:'周报',monthly:'月报'};
function chooseReport(id){reportSelection[reportKind]=id;renderReport();window.scrollTo(0,0)}
function renderReport(){
 const entries=PROTOTYPE.reports.filter(r=>r.kind===reportKind);
 const report=entries.find(r=>r.id===reportSelection[reportKind])||entries[0];
 $('#digest-edition').innerHTML=entries.map(r=>`<option value="${esc(r.id)}">${esc(r.date)} · ${esc(r.title)}</option>`).join('');
 $('#digest-edition').disabled=!report;
 $('#digest-reader').setAttribute('aria-labelledby','digest-tab-'+reportKind);
 reportTabs.forEach(b=>{const active=b.dataset.reportKind===reportKind;b.setAttribute('aria-selected',active);b.tabIndex=active?0:-1});
 if(!report){$('#digest-history').innerHTML='暂无往期';$('#digest-masthead').innerHTML='';$('#digest-neighbours').innerHTML='';$('#digest-meta').textContent='暂无已生成报告';$('#digest-body').innerHTML='<div class="digest-pending">该周期尚无报告，不能据此判断产品没有变化。</div>';return}
 reportSelection[reportKind]=report.id;$('#digest-edition').value=report.id;
 $('#digest-meta').innerHTML=`<span class="digest-links"><a href="${esc(report.url)}" target="_blank" rel="noopener">打开完整报告 ↗</a>${report.markdown?`<a href="${esc(report.markdown)}" target="_blank" rel="noopener">Markdown ↗</a>`:''}</span>`;
 $('#digest-body').innerHTML=report.body;
 const groups=[...new Set(entries.map(r=>r.date.slice(0,reportKind==='monthly'?4:7)))];
 $('#digest-history').innerHTML=groups.map(group=>'<section><h3>'+esc(group.replace('-',' 年 '))+(reportKind==='monthly'?' 年':' 月')+'</h3>'+entries.filter(r=>r.date.startsWith(group)).map(r=>'<button data-report-id="'+esc(r.id)+'" '+(r.id===report.id?'aria-current="true"':'')+'><span class="digest-issue-day">'+esc(reportKind==='monthly'?r.date.slice(5,7):r.date.slice(8))+'<small>'+(reportKind==='weekly'?'日起':reportKind==='monthly'?'月':'日')+'</small></span><span><strong>'+esc(r.title)+'</strong></span></button>').join('')+'</section>').join('');
 const dateLabel=reportKind==='monthly'?report.date.slice(0,7):reportKind==='weekly'?report.date+' 起的一周':report.date;
 $('#digest-masthead').innerHTML='<div class="digest-dateline"><span>'+esc(dateLabel)+'</span><span>产品 · 用户 · 场景</span></div><header class="digest-nameplate"><div><h1>竞品<span>'+reportNames[reportKind]+'</span></h1><p>竞品观察 / PRODUCT INTELLIGENCE</p></div>'+renderIssueBox(report,entries)+'</header>';
 const current=entries.indexOf(report),older=entries[current+1],newer=entries[current-1];
 $('#digest-neighbours').innerHTML=(older?'<button data-report-id="'+esc(older.id)+'"><small>← 上一期 · '+esc(older.date)+'</small><strong>'+esc(older.title)+'</strong></button>':'<span></span>')+(newer?'<button data-report-id="'+esc(newer.id)+'"><small>下一期 · '+esc(newer.date)+' →</small><strong>'+esc(newer.title)+'</strong></button>':'<span></span>');
 document.querySelectorAll('[data-report-id]').forEach(b=>b.onclick=()=>chooseReport(b.dataset.reportId));
}
reportTabs.forEach((b,i)=>{b.onclick=()=>{reportKind=b.dataset.reportKind;renderReport()};b.onkeydown=e=>{let n;if(e.key==='ArrowRight')n=(i+1)%3;if(e.key==='ArrowLeft')n=(i+2)%3;if(e.key==='Home')n=0;if(e.key==='End')n=2;if(n!==undefined){e.preventDefault();reportTabs[n].focus();reportTabs[n].click()}}});
$('#digest-edition').onchange=e=>chooseReport(e.target.value);
renderReport();
