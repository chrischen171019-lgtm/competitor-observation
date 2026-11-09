import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises';
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
