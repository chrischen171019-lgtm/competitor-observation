const fs=require('fs'),vm=require('vm'),assert=require('assert');
const names=JSON.parse(fs.readFileSync('outputs/observation.json')).names;
class El{constructor(id=''){this.id=id;this.dataset={};this.attrs={};this.hidden=false;this.value='';this.innerHTML='';this.textContent=''}setAttribute(k,v){this.attrs[k]=String(v)}removeAttribute(k){delete this.attrs[k]}addEventListener(){}focus(){}click(){this.onclick?.()}scrollIntoView(){}showModal(){this.open=true}close(){this.open=false}querySelector(){return null}}
const ids=['digest-history','digest-masthead','digest-neighbours','digest-edition','digest-reader','digest-meta','digest-body','breadcrumb','product-switcher','notebook-nav','ima-nav','strategy-nav','feed-count','news-feed','more-news','detail-body','news-detail','close-news','search-news','date-from','date-to','reset-news','hot-product','hot-summary','hot-board','hot-detail-body','hot-detail','close-hot','hot-method-button','hot-method','feedback-product','feedback-days','feedback-kind','feedback-source','feedback-reset','feedback-count','feedback-list','perception-product','perception-days','perception-overview','perception-list','unclassified-label','unclassified-records','perception-unclassified'];
const els=Object.fromEntries(ids.map(x=>[x,new El(x)]));els['.research-toc']=new El();
const sections=['competitors','updates','digest','feedback','strategy'].map(x=>els['site-'+x]=new El('site-'+x));
const products=Object.keys(names).map(k=>{const b=new El();b.dataset.key=k;return b});
const panels=Object.keys(names).map(k=>new El('panel-'+k));
const nav=sections.map(x=>{const e=new El();e.dataset.section=x.id.slice(5);return e});
const filters=['all',...Object.keys(names)].map(k=>{const e=new El();e.dataset.filterProduct=k;return e});
const kinds=['all','official','media','account','official-lead'].map(k=>{const e=new El();e.dataset.filterKind=k;return e});
const reportTabs=['daily','weekly','monthly'].map(k=>{const e=new El();e.dataset.reportKind=k;return e});
const document={body:{dataset:{}},getElementById:id=>els[id]||null,querySelector:s=>els[s.startsWith('#')?s.slice(1):s]||null,querySelectorAll:s=>({'#product-tabs button':products,'main > div[role=tabpanel]':sections,'#site-competitors > article':panels,'.app-sidebar [data-section]':nav,'[data-filter-product]':filters,'[data-filter-kind]':kinds,'[data-detail]':[],'[data-report-kind]':reportTabs}[s]||[])};
const context={document,window:{scrollTo(){},addEventListener(){}},location:{hash:'#section-updates'},requestAnimationFrame:fn=>fn(),console};
els['feedback-product'].value='all';els['feedback-days'].value='30';els['perception-days'].value='30';els['feedback-kind'].value='all';els['feedback-source'].value='all';els['hot-product'].value='all';vm.createContext(context);const s=fs.readFileSync('outputs/competitor-ui-prototype.html','utf8');const scripts=s.split('<script>').slice(1).map(x=>x.split('</script>')[0]);vm.runInContext(scripts.at(-1),context);
assert(els['feed-count'].textContent.startsWith(run('PROTOTYPE.events.length')+' 条'));assert.equal(document.body.dataset.siteSection,'updates');
function run(x){return vm.runInContext(x,context)}
run("state.product='weknora';render()");assert(els['feed-count'].textContent.startsWith(run("PROTOTYPE.events.filter(e=>e.product==='weknora').length")+' 条'));
filters.find(b=>b.dataset.filterProduct==='ima').click();run("state.q='no-record-9daaf68';render()");assert(els['news-feed'].innerHTML.includes('暂无动态记录'));assert.equal(filters.find(b=>b.dataset.filterProduct==='ima').attrs['aria-pressed'],'true');
run("reset();state.q='Uber';render()");assert(els['feed-count'].textContent.startsWith(run('PROTOTYPE.events.filter(eligible).length')+' 条'));
run("reset();state.from='2026-10-27';render()");assert(els['feed-count'].textContent.startsWith(run('PROTOTYPE.events.filter(eligible).length')+' 条'));
run("openDetail('2c3db46a4b8f1d41bf4b2940')");assert(els['news-detail'].open);assert(els['detail-body'].innerHTML.includes('正文仍需核验'));
context.location.hash='#product-ima';run('route()');assert.equal(document.body.dataset.siteSection,'competitors');assert(!panels.find(p=>p.id==='panel-ima').hidden);assert(panels.find(p=>p.id==='panel-notebook').hidden);
context.location.hash='#section-reports';run('route()');assert.equal(document.body.dataset.siteSection,'digest');assert(els['product-switcher'].hidden);
console.log('PASS: product/search/date filters, empty state, evidence dialog, product switch and legacy report redirect.');

context.location.hash='#section-hot';run('route()');assert.equal(document.body.dataset.siteSection,'digest');assert(!els['site-digest'].hidden);assert(els['digest-body'].innerHTML.includes(run('PROTOTYPE.reports[0].title')));
for(const kind of ['weekly','monthly']){reportTabs.find(b=>b.dataset.reportKind===kind).click();assert(els['digest-body'].innerHTML.includes('本期尚未整理为主题分析'));assert(els['digest-meta'].innerHTML.includes('打开完整报告'));assert.equal(els['digest-reader'].attrs['aria-labelledby'],'digest-tab-'+kind)}
reportTabs[0].click();els['digest-edition'].onchange({target:{value:'daily-2026-10-26'}});assert(els['digest-body'].innerHTML.includes('371 条记录'));reportTabs[1].click();reportTabs[0].click();assert.equal(els['digest-edition'].value,'daily-2026-10-26');
reportTabs[0].onkeydown({key:'End',preventDefault(){}});assert.equal(run('reportKind'),'monthly');
run('const savedReports=PROTOTYPE.reports;PROTOTYPE.reports=[];renderReport()');assert(els['digest-body'].innerHTML.includes('该周期尚无报告'));assert(els['digest-edition'].disabled);run('PROTOTYPE.reports=savedReports;renderReport()');
assert(!s.includes('竞品热点榜'));
console.log('PASS: report tabs, prior editions, keyboard, empty state and old hot route.');

context.location.hash='#section-feedback';run('route()');assert.equal(document.body.dataset.siteSection,'feedback');let result=run('perceptionData()');assert(result.topics.length>5);assert(result.topics[0].id==='continuity');assert.equal((els['perception-list'].innerHTML.match(/class="perception-card"/g)||[]).length,5);els['perception-product'].value='notebook';run('renderPerceptions()');assert(els['perception-list'].innerHTML.includes('样本不足'));els['perception-product'].value='ima';run('renderPerceptions()');assert(run('perceptionData().topics[0].id')==='research');els['perception-product'].value='doubao';run('renderPerceptions()');assert(run('perceptionData().topics[0].id')==='companionship');els['perception-days'].value='1';run('renderPerceptions()');assert.equal(run('perceptionData().records.length'),0);console.log('PASS: perception Top 5, evidence counts, product/date filters and Gemini empty state.');
const dailyGrid=run("issueCalendar(PROTOTYPE.reports.find(r=>r.id==='daily-2026-10-27'),PROTOTYPE.reports.filter(r=>r.kind==='daily'))");
const monthIssues=dailyGrid.cells.filter(c=>c.id).length;assert(dailyGrid.number>0);assert.equal(dailyGrid.note,`本月 ${monthIssues} 期`);assert.equal(dailyGrid.cells.filter(c=>c.state==='current').length,1);assert.equal(dailyGrid.cells.filter(c=>c.state==='pad').length<7,true);assert.equal(dailyGrid.subcaption,'星期二');
run("reportKind='daily';chooseReport('daily-2026-10-26')");assert(els['digest-masthead'].innerHTML.includes('第 1 期'));assert.equal(els['digest-edition'].value,'daily-2026-10-26');assert(els['digest-masthead'].innerHTML.includes('issue-dot current'));
assert.equal(run("isoWeek('2026-10-26').week"),44);assert.equal(run("isoWeek('2027-01-01').year"),2026);assert.equal(run("isoWeek('2027-01-01').week"),53);assert.equal(run("isoWeek('2027-01-04').week"),1);
const weekReport=run("PROTOTYPE.reports.find(r=>r.kind==='weekly')"),weekGrid=run("issueCalendar(PROTOTYPE.reports.find(r=>r.kind==='weekly'),PROTOTYPE.reports.filter(r=>r.kind==='weekly'))");assert.equal(weekGrid.cells.length,53);assert.equal(weekGrid.figure,String(run("isoWeek(PROTOTYPE.reports.find(r=>r.kind==='weekly').date).week")));assert.equal(weekGrid.note,`全年 ${run("PROTOTYPE.reports.filter(r=>r.kind==='weekly'&&r.date.slice(0,4)===PROTOTYPE.reports.find(r=>r.kind==='weekly').date.slice(0,4)).length")} 期`);
const monthReport=run("PROTOTYPE.reports.find(r=>r.kind==='monthly')"),monthGrid=run("issueCalendar(PROTOTYPE.reports.find(r=>r.kind==='monthly'),PROTOTYPE.reports.filter(r=>r.kind==='monthly'))");assert.equal(monthGrid.cells.length,12);assert.equal(monthGrid.figure,String(Number(monthReport.date.slice(5,7))));
console.log('PASS: calendar alignment, real issue counts, current selection, report switching, ISO week/year boundary and month grid.');
for(const section of ['competitors','updates','digest','feedback','strategy']){context.location.hash=section==='competitors'?'#product-notebook':'#section-'+section;run('route()');assert.equal(document.body.dataset.siteSection,section);assert.equal(sections.filter(p=>!p.hidden).length,1);assert.equal(nav.filter(n=>n.attrs['aria-current']==='page').length,1)}
for(const product of Object.keys(names)){context.location.hash='#product-'+product;run('route()');assert.equal(panels.filter(p=>!p.hidden).length,1);assert(!panels.find(p=>p.id==='panel-'+product).hidden);assert.equal(products.find(b=>b.dataset.key===product).attrs['aria-selected'],'true')}
for(const product of ['all',...Object.keys(names)]){filters.find(b=>b.dataset.filterProduct===product).click();assert.equal(filters.filter(b=>b.attrs['aria-pressed']==='true').length,1);assert.equal(run('state.product'),product)}
run('reset()');assert(els['feed-count'].textContent.startsWith(run('PROTOTYPE.events.length')+' 条'));assert.equal(run('state.q'),'');assert.equal(run('state.from'),'');
context.location.hash='#section-discover';run('route()');assert.equal(document.body.dataset.siteSection,'updates');
context.location.hash='#not-a-page';run('route()');assert.equal(document.body.dataset.siteSection,'updates');
console.log('PASS: five primary sections, all nine research products, ten feed filters, reset and removed/unknown routes.');
const beforeLive=run('PROTOTYPE.events.length');
run("state.product='ima';state.q='';const next=JSON.parse(JSON.stringify(PROTOTYPE));next.cutoff='2026-10-27T23:59:00+08:00';next.events.push({...next.events.find(e=>e.product==='ima'),id:'live-new',title:'API 新动态',published_at:null});acceptObservation(next)");
assert.equal(run('PROTOTYPE.events.length'),beforeLive+1);assert.equal(run('state.product'),'ima');
run('visibleLimit=9999;render()');assert(els['news-feed'].innerHTML.includes('日期待核验'));
console.log('PASS: API snapshot adds a new record, preserves filters, and handles unknown publication dates.');
