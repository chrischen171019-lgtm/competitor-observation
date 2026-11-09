// Masthead adapted from AIHOT IssueDots / Halftone (MIT).
const datePad=n=>String(n).padStart(2,'0');
function isoWeek(date){const d=new Date(date+'T00:00:00Z');d.setUTCDate(d.getUTCDate()+3-(d.getUTCDay()+6)%7);const year=d.getUTCFullYear();return {year,week:1+Math.round(((d-new Date(Date.UTC(year,0,4)))/86400000-3+(new Date(Date.UTC(year,0,4)).getUTCDay()+6)%7)/7)}}
function issueCalendar(report,entries){
 const chronological=[...entries].sort((a,b)=>a.date.localeCompare(b.date));
 const number=r=>chronological.findIndex(e=>e.id===r.id)+1;
 const year=Number(report.date.slice(0,4)),month=Number(report.date.slice(5,7));
 let title,heads=[],columns,cells=[],figure,caption,subcaption;
 const add=(label,found)=>cells.push({label:label+(found?' · 第 '+number(found)+' 期':' · 暂无归档'),id:found?.id||null,state:found?.id===report.id?'current':found?'issue':'none'});
 if(report.kind==='daily'){
  title=['一','二','三','四','五','六','七','八','九','十','十一','十二'][month-1]+'月';columns=7;heads=['一','二','三','四','五','六','日'];
  const pad=(new Date(Date.UTC(year,month-1,1)).getUTCDay()+6)%7;
  cells=Array.from({length:pad},()=>({state:'pad'}));
  for(let day=1;day<=new Date(Date.UTC(year,month,0)).getUTCDate();day++){const key=report.date.slice(0,7)+'-'+datePad(day);add(key,entries.find(e=>e.date===key))}
  figure=report.date.slice(8);caption=year+' 年 '+month+' 月';subcaption=new Date(report.date+'T12:00:00Z').toLocaleDateString('zh-CN',{weekday:'long',timeZone:'Asia/Shanghai'});
 }else if(report.kind==='weekly'){
  const iso=isoWeek(report.date);title=iso.year+' 年';columns=13;
  for(let week=1;week<=isoWeek(iso.year+'-12-28').week;week++)add(iso.year+' 年第 '+week+' 周',entries.find(e=>{const w=isoWeek(e.date);return w.year===iso.year&&w.week===week}));
  figure=datePad(iso.week);caption=iso.year+' 年 · 第 '+iso.week+' 周';subcaption=report.date+' 起';
 }else{
  title=year+' 年';columns=6;
  for(let m=1;m<=12;m++)add(year+' 年 '+m+' 月',entries.find(e=>e.date.slice(0,7)===year+'-'+datePad(m)));
  figure=datePad(month);caption=year+' 年 '+month+' 月';subcaption='月度汇总';
 }
 return {title,heads,columns,cells,figure,caption,subcaption,number:number(report),note:(report.kind==='daily'?'本月':'全年')+' '+cells.filter(c=>c.id).length+' 期'};
}
function renderIssueBox(report,entries){
 const g=issueCalendar(report,entries),pattern='issue-dots-'+report.id;
 const svg='<svg class="issue-halftone" viewBox="0 0 160 110" aria-hidden="true"><defs><pattern id="'+esc(pattern)+'" width="4" height="3.46" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1.45" fill="currentColor"/><circle cx="3" cy="2.73" r="0.75" fill="currentColor"/></pattern><pattern id="'+esc(pattern)+'-idle" width="4" height="4" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="0.35" fill="currentColor" opacity=".2"/></pattern></defs><rect width="160" height="110" fill="url(#'+esc(pattern)+'-idle)"/><text x="80" y="87" text-anchor="middle" font-family="Arial, sans-serif" font-weight="900" font-size="100" fill="currentColor" opacity=".09">'+g.figure+'</text><text x="80" y="87" text-anchor="middle" font-family="Arial, sans-serif" font-weight="900" font-size="100" fill="url(#'+esc(pattern)+')">'+g.figure+'</text></svg>';
 return '<div class="issue-box"><div class="issue-date"><span class="issue-number" title="按当前本地同类报告归档顺序编号">第 '+g.number+' 期</span><span class="issue-date-label" aria-label="'+esc(g.caption+' '+g.subcaption)+'">'+svg+'</span><span>'+esc(g.caption)+'</span><span class="issue-weekday">'+esc(g.subcaption)+'</span></div><div class="issue-calendar"><div class="issue-calendar-title"><strong>'+esc(g.title)+'</strong><span>'+esc(g.note)+'</span></div><div class="issue-grid" style="--issue-columns:'+g.columns+'">'+g.heads.map(h=>'<span class="issue-weekhead">'+h+'</span>').join('')+g.cells.map(c=>c.state==='pad'?'<span aria-hidden="true"></span>':c.id?'<button class="issue-dot '+c.state+'" data-report-id="'+esc(c.id)+'" title="'+esc(c.label)+'" aria-label="'+esc(c.label)+'" '+(c.state==='current'?'aria-current="date"':'')+'><i aria-hidden="true"></i></button>':'<span class="issue-dot none" title="'+esc(c.label)+'" aria-label="'+esc(c.label)+'"><i aria-hidden="true"></i></span>').join('')+'</div><p class="issue-calendar-note">深色点可切换 · 浅色点暂无归档</p></div></div>';
}
