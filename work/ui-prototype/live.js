function renderSourceHealth(){
 const sources=PROTOTYPE.source_status||[],failed=sources.filter(s=>s.status==='error');
 const summary=document.getElementById('source-summary');
 if(summary)summary.textContent=`${sources.length} 个来源 · ${failed.length} 个异常 · 最近检查 ${PROTOTYPE.cutoff.slice(0,16).replace('T',' ')}`;
 const health=document.getElementById('source-health');
 if(health)health.innerHTML=sources.map(s=>`<p><strong>${esc(s.id)}</strong> · ${s.status==='ok'?`${Number(s.count)} 条记录`:esc(s.status==='error'?'采集失败':'未采集')} · ${esc(s.checked_at?.slice(0,16).replace('T',' ')||'')}<br><small>${esc(s.error||s.sample_status||s.coverage||'')}</small></p>`).join('');
 const updated=document.getElementById('live-updated');if(updated)updated.textContent=PROTOTYPE.cutoff.slice(0,16).replace('T',' ');
}
function acceptObservation(data){
 if(data.schema_version!==1||!Array.isArray(data.events)||!Array.isArray(data.reports)||!data.perceptions||!Array.isArray(data.source_status))throw Error('Invalid observation response');
 if((data.revision||data.cutoff)!==(PROTOTYPE.revision||PROTOTYPE.cutoff)){Object.assign(PROTOTYPE,data);PERCEPTIONS=data.perceptions;render();renderReport();renderPerceptions();}
 renderSourceHealth();
}
async function refreshObservation(){
 const label=document.getElementById('live-status');
 try{
  const response=await fetch('/api/observation/snapshot',{cache:'no-store',signal:AbortSignal.timeout(15000)});
  if(!response.ok)throw Error('Unavailable');
  acceptObservation(await response.json());
  const age=Date.now()-new Date(PROTOTYPE.cutoff).getTime(),failures=PROTOTYPE.source_status.filter(s=>s.status==='error').length;
  if(label)label.textContent=age>2*3600000?'超过 2 小时未更新':failures?`${failures} 个来源异常`:'已连接数据服务';
 }catch{if(label)label.textContent='更新连接失败 · 保留已加载内容';}
}
renderSourceHealth();
if(location.protocol==='http:'||location.protocol==='https:'){refreshObservation();setInterval(refreshObservation,60000);}
else {const label=document.getElementById('live-status');if(label)label.textContent='离线快照';}
