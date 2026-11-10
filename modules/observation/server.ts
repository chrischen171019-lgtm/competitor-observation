import path from "node:path";
import type { FastifyInstance } from "fastify";
import type { ServerModule } from "@aihot/backend/modules";
import { loadObservation, observationFile } from "@aihot/backend/publication/observation";
import { pushObservation, ObservationInputError } from "@aihot/backend/ingest/observation";
import { authorized, unauthorized } from "../../apps/api/src/routes/ingest.ts";

export function registerObservation(app:FastifyInstance,root=process.env.OBSERVATION_ROOT||path.resolve(import.meta.dirname,"../../..")) {
 app.post("/api/observation/events", {bodyLimit: 2 * 1024 * 1024}, async(req,reply)=>{
  reply.header("Cache-Control","no-store");
  if (!authorized(req)) return unauthorized(reply);
  let names: Record<string,string>;
  try { names = (await loadObservation(root)).names; }
  catch { return reply.code(503).send({ok:false,error:"observation_unavailable"}); }
  try { return pushObservation(root,req.body,names); }
  catch (error) {
   if (error instanceof ObservationInputError) return reply.code(400).send({ok:false,error:error.message});
   req.log.error({err:error},"observation push failed");
   return reply.code(500).send({ok:false,error:"observation_write_failed"});
  }
 });
 app.get("/observe",async(_req,reply)=>reply.redirect("/observe/outputs/competitor-ui-prototype.html"));
 app.get("/observe/*",async(req,reply)=>{
  const file=observationFile(root,(req.params as {"*":string})["*"]);
  if(!file)return reply.code(404).send({error:"not_found"});
  const {sendFile}=await import("../../apps/api/src/routes/static.ts");
  return sendFile(req,reply,file,{cacheControl:"no-store",type:file.endsWith(".html")?"text/html; charset=utf-8":"text/plain; charset=utf-8"});
 });
 for(const endpoint of ["snapshot","status","events","feedback","reports"])app.get("/api/observation/"+endpoint,async(req,reply)=>{
  reply.header("Cache-Control","no-store");
  try {
   const data=await loadObservation(root);
   const product=(req.query as {product?:string}).product;
   if(endpoint==="snapshot")return data;
   if(endpoint==="status")return {updated_at:data.cutoff,sources:data.source_status};
   if(endpoint==="reports")return {updated_at:data.cutoff,items:data.reports};
   const items=endpoint==="feedback"?data.perceptions.records:data.events;
   return {updated_at:data.cutoff,items:product?items.filter(item=>item.product===product):items};
  }catch{return reply.code(503).send({error:"observation_unavailable"});}
 });
}
const module:ServerModule={name:"observation",http:registerObservation};
export default module;
