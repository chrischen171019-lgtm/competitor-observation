// Observation content shares the engine publication boundary.
import { readFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import path from "node:path";
import { readPushedEvents } from "../ingest/observation.ts";
export interface ObservationSnapshot {
 schema_version: number; cutoff: string; revision?:string; names: Record<string,string>;
 events: Array<{id:string;product:string;title:string;url?:string;published_at?:string|null}>;
 reports: unknown[]; perceptions: {records: Array<{product:string}>};
 source_status: Array<{id:string;status:string;count:number;checked_at?:string}>;
}
export async function loadObservation(root:string):Promise<ObservationSnapshot> {
 const text=await readFile(path.join(root,"outputs/observation.json"),"utf8");
 const data=JSON.parse(text) as ObservationSnapshot;
 if(data.schema_version!==1||!Array.isArray(data.events)||!Array.isArray(data.reports)||!Array.isArray(data.source_status)||!Array.isArray(data.perceptions?.records))throw new Error("Invalid observation snapshot");
 const pushed = readPushedEvents(root).filter(item => Object.hasOwn(data.names, item.product));
 data.revision = createHash("sha256").update(text).update(JSON.stringify(pushed)).digest("hex");
 // Collector snapshots and the independent push store never overwrite each other.
 const known = new Set(data.events.map(item => item.product + "\n" + item.url));
 data.events.push(...pushed.filter(item => !known.has(item.product + "\n" + item.url)));
 data.events.sort((a,b) => (b.published_at || "").localeCompare(a.published_at || "") || a.id.localeCompare(b.id));
 const sources = new Map<string, {id:string;status:string;count:number;checked_at:string}>();
 for (const item of pushed) {
  const source = sources.get(item.source_id) ?? { id: item.source_id, status: "ok", count: 0, checked_at: item.last_seen };
  source.count++;
  if (Date.parse(item.last_seen) > Date.parse(source.checked_at)) source.checked_at = item.last_seen;
  sources.set(item.source_id, source);
  if (Date.parse(item.last_seen) >= Date.parse(data.cutoff)) data.cutoff = item.last_seen;
 }
 for (const source of sources.values()) {
  // Keep collection failures visible even when a push client uses the same source name.
  if (!data.source_status.some(existing => existing.id === source.id)) data.source_status.push(source);
 }
 return data;
}
export function observationFile(root:string,relative:string):string|null {
 const pages=["outputs/competitor-ui-prototype.html","outputs/competitor-research-complete.html","outputs/aihot-prototype-notice.html"];
 const report=/^reports\/(daily|weekly|monthly)-\d{4}-\d{2}-\d{2}\.(html|md)$/.test(relative);
 if(!pages.includes(relative)&&!report)return null;
 return path.join(root,relative);
}
