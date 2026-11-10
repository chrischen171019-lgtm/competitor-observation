// Local observation pages and push API, with no PostgreSQL or worker startup.
import { existsSync } from "node:fs";
import { appendFile, writeFile } from "node:fs/promises";
import { randomBytes } from "node:crypto";
import path from "node:path";
import Fastify from "fastify";

const repository = path.resolve(import.meta.dirname, "../..");
const envFile = path.join(repository, ".env.observation");
if (existsSync(envFile)) process.loadEnvFile(envFile);
if (!process.env.INGEST_TOKEN) {
 const entry = `INGEST_TOKEN=${randomBytes(32).toString("hex")}\n`;
 if (existsSync(envFile)) await appendFile(envFile, "\n" + entry, { mode: 0o600 });
 else await writeFile(envFile, "# 本机竞品推送密钥；不要上传或放入网页。\n" + entry, { mode: 0o600, flag: "wx" });
 process.loadEnvFile(envFile);
}
const root = path.resolve(repository, process.env.OBSERVATION_ROOT || ".");
const { registerObservation } = await import("./server.ts");
const { loadObservation } = await import("@aihot/backend/publication/observation");
await loadObservation(root); // Fail before listening if the configured content is unavailable.
const app = Fastify({ logger: { level: "warn", redact: ["req.headers.authorization"] } });
registerObservation(app, root);
app.get("/", async (_req, reply) => reply.redirect("/observe"));
try {
 const address = await app.listen({ host: "127.0.0.1", port: Number(process.env.OBSERVATION_PORT || 3300) });
 console.log(`竞品观察：${address}/observe/outputs/competitor-ui-prototype.html`);
 console.log(`推送接口：POST ${address}/api/observation/events`);
 console.log(`推送密钥配置：${envFile}（INGEST_TOKEN，不会出现在网页中）`);
 console.log(`内容目录：${root}`);
} catch (error) { app.log.error(error); process.exitCode = 1; }
for (const signal of ["SIGINT", "SIGTERM"] as const) process.once(signal, async () => { await app.close(); });
