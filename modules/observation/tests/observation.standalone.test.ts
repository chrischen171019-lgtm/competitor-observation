import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import Fastify from 'fastify';

test('snapshot, events and source status share the latest stored data; private paths stay unavailable', async () => {
 const root = await mkdtemp(path.join(tmpdir(), 'observation-'));
 const app = Fastify();
 try {
  await mkdir(path.join(root, 'outputs'));
  const { registerObservation } = await import('../server.ts');
  registerObservation(app, root);
  assert.equal((await app.inject('/api/observation/snapshot')).statusCode, 503);
  const snapshot = { schema_version: 1, cutoff: '2026-10-27T17:00:00+08:00', names: { ima: 'ima' }, events: [{id:'one',product:'ima',title:'new item'}], reports: [], perceptions: {records: []}, source_status: [{id:'source',status:'error',count:0}] };
  await writeFile(path.join(root, 'outputs/observation.json'), JSON.stringify(snapshot));
  assert.deepEqual((await app.inject('/api/observation/events?product=ima')).json().items, snapshot.events);
  assert.equal((await app.inject('/api/observation/events?product=other')).json().items.length, 0);
  assert.equal((await app.inject('/api/observation/status')).json().sources[0].status, 'error');
  snapshot.events.push({id:'two',product:'ima',title:'later item'});
  await writeFile(path.join(root, 'outputs/observation.json'), JSON.stringify(snapshot));
  assert.equal((await app.inject('/api/observation/snapshot')).json().events.length, 2);
  await writeFile(path.join(root,'outputs/competitor-ui-prototype.html'), '<h1>竞品观察</h1>');
  const page=await app.inject('/observe/outputs/competitor-ui-prototype.html');
  assert.equal(page.statusCode,200);
  assert.ok(page.headers['content-type']!.includes('text/html'));
  for(const url of ['/observe/data/monitor.sqlite3','/observe/outputs/monitor-data.json','/observe/.env','/observe/reports/revisions/x.html'])assert.equal((await app.inject(url)).statusCode,404);
 } finally {await app.close();await rm(root,{recursive:true,force:true});}
});

test('authenticated pushes reach the page snapshot, survive refresh/restart and reject invalid batches without partial writes', async () => {
 const root = await mkdtemp(path.join(tmpdir(), 'observation-push-'));
 const token = process.env.INGEST_TOKEN;
 process.env.INGEST_TOKEN = 'observation-local-test-0123456789';
 const headers = { authorization: 'Bearer ' + process.env.INGEST_TOKEN };
 const { registerObservation } = await import('../server.ts');
 let app = Fastify();
 try {
  await mkdir(path.join(root, 'outputs'));
  const snapshot = { schema_version: 1, cutoff: '2026-10-27T17:00:00+08:00', names: { ima: 'ima' }, events: [{id:'existing',product:'ima',title:'original',url:'https://example.org/original'}], reports: [{id:'keep-report',body:'preserve editorial'}], perceptions: {records: [], themes: []}, source_status: [] };
  const file = path.join(root, 'outputs/observation.json');
  await writeFile(file, JSON.stringify(snapshot));
  registerObservation(app, root);
  const payload = { source_id: 'harness-local', items: [{ product: 'ima', title: '新的功能线索', url: 'https://example.org/update', excerpt: '<script>example</script>', published_at: '2026-11-10T01:00:00Z' }] };
  assert.equal((await app.inject({method:'POST',url:'/api/observation/events',payload})).statusCode,401);
  assert.equal((await app.inject({method:'POST',url:'/api/observation/events',headers:{authorization:'Bearer wrong'},payload})).statusCode,401);
  const post = () => app.inject({method:'POST',url:'/api/observation/events',headers,payload});
  const first = await post();
  assert.equal(first.statusCode,200,first.body);
  assert.equal(first.json().created,1);
  assert.equal(first.json().unchanged,0);
  assert.equal(first.json().ok,true);
  const data = (await app.inject('/api/observation/snapshot')).json();
  assert.equal(data.events.length,2);
  const added = data.events.find((e: {title:string}) => e.title===payload.items[0].title);
  assert.equal(Date.parse(added.published_at),Date.parse(payload.items[0].published_at));
  assert(added.published_at.endsWith('+08:00'));
  assert.equal(added.verification,'待核验');
  assert.notEqual(added.kind,'official');
  assert.equal(data.source_status.find((s:{id:string})=>s.id==='harness-local').count,1);
  assert.deepEqual(data.reports,snapshot.reports);
  assert.equal((await readFile(file,'utf8')),JSON.stringify(snapshot),'collector snapshot is not rewritten by push');
  const retry=(await post()).json();
  assert.equal(retry.created,0);assert.equal(retry.unchanged,1);
  const lastSeen=data.events.find((e:{id:string})=>e.id===added.id).last_seen;
  await new Promise(resolve=>setTimeout(resolve,5));
  assert.equal((await post()).json().updated,0);
  const afterRetry=(await app.inject('/api/observation/events')).json().items.find((e:{id:string})=>e.id===added.id);
  assert.equal(afterRetry.last_seen,lastSeen);
  const duplicateBatch=await app.inject({method:'POST',url:'/api/observation/events',headers,payload:{source_id:'harness-local',items:[payload.items[0],payload.items[0]]}});
  assert.equal(duplicateBatch.json().unchanged,2);
  const concurrent=await Promise.all([post(),post()]);
  assert(concurrent.every(r=>r.json().created===0));
  for(const invalid of [
   {product:'not-a-product'}, {url:'javascript:alert(1)'}, {url:'not-a-url'}, {url:'https://user:secret@example.org/a'}, {published_at:'yesterday'}, {title:''},
  ]) {
   const reply=await app.inject({method:'POST',url:'/api/observation/events',headers,payload:{source_id:'harness-local',items:[{...payload.items[0],url:'https://example.org/should-not-write'},{...payload.items[0],...invalid}]}});
   assert.equal(reply.statusCode,400,reply.body);
  }
  assert.equal((await app.inject('/api/observation/events')).json().items.length,2);
  payload.items[0].title='已更新的线索';
  assert.equal((await post()).json().updated,1);
  await app.close();app=Fastify();registerObservation(app,root);
  snapshot.events.push({id:'collected-copy',product:'ima',title:'collector verified copy',url:'https://example.org/update'});
  await writeFile(file,JSON.stringify(snapshot));
  assert.equal((await app.inject('/api/observation/events?product=ima')).json().items.filter((e:{url:string})=>e.url===payload.items[0].url).length,1);
  snapshot.events=[];
  await writeFile(file,JSON.stringify(snapshot));
  const persisted=(await app.inject('/api/observation/events?product=ima')).json();
  assert.equal(persisted.items.length,1);
  assert.equal(persisted.items[0].title,'已更新的线索');
  assert.equal(persisted.items[0].id,added.id);
  assert.equal(persisted.items[0].first_seen,added.first_seen);
  assert.equal((await app.inject('/observe/data/observation-push.sqlite3')).statusCode,404);
 } finally {
  await app.close();await rm(root,{recursive:true,force:true});
  if(token===undefined)delete process.env.INGEST_TOKEN;else process.env.INGEST_TOKEN=token;
 }
});
