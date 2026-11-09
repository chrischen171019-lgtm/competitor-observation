// Observation content shares the engine publication boundary.
import { readFile } from "node:fs/promises";
import path from "node:path";
export interface ObservationSnapshot {
 schema_version: number; cutoff: string; names: Record<string,string>;
 events: Array<{id:string;product:string;title:string}>;
 reports: unknown[]; perceptions: {records: Array<{product:string}>};
 source_status: Array<{id:string;status:string;count:number}>;
}
export async function loadObservation(root:string):Promise<ObservationSnapshot> {
 const data=JSON.parse(await readFile(path.join(root,"outputs/observation.json"),"utf8")) as ObservationSnapshot;
 if(data.schema_version!==1||!Array.isArray(data.events)||!Array.isArray(data.reports)||!Array.isArray(data.source_status)||!Array.isArray(data.perceptions?.records))throw new Error("Invalid observation snapshot");
 return data;
}
export function observationFile(root:string,relative:string):string|null {
 const pages=["outputs/competitor-ui-prototype.html","outputs/competitor-research-complete.html","outputs/aihot-prototype-notice.html"];
 const report=/^reports\/(daily|weekly|monthly)-\d{4}-\d{2}-\d{2}\.(html|md)$/.test(relative);
 if(!pages.includes(relative)&&!report)return null;
 return path.join(root,relative);
}
