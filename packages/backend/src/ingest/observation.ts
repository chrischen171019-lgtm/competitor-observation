import { createHash } from "node:crypto";
import { existsSync, mkdirSync } from "node:fs";
import path from "node:path";
import { DatabaseSync } from "node:sqlite";
import { z } from "zod";

const input = z.object({
 source_id: z.string().regex(/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}$/),
 items: z.array(z.object({
  product: z.string().min(1).max(80),
  title: z.string().trim().min(1).max(500),
  url: z.string().max(4096).url().refine(value => {
   try {
    const url = new URL(value);
    return ["https:", "http:"].includes(url.protocol) && !url.username && !url.password;
   } catch { return false; }
  }, "Use an HTTP(S) source URL without credentials"),
  excerpt: z.string().max(20_000).default(""),
  published_at: z.string().datetime({ offset: true }).nullable().optional(),
  publisher: z.string().trim().max(200).optional(),
 }).strict()).min(1).max(50),
}).strict();

export interface PushedEvent {
 id: string; product: string; source_id: string; title: string; url: string; excerpt: string;
 published_at: string | null; publisher: string; first_seen: string; last_seen: string;
 category: string; verification: string; classification: string; summary_mode: string;
 kind: string; sourceLabel: string; topic: string; preview: string; external: boolean;
}

const beijing = (time: number) => new Date(time + 8 * 3600_000).toISOString().replace("Z", "+08:00");
const databaseFile = (root: string) => path.join(process.env.OBSERVATION_PUSH_DIR ? path.resolve(root, process.env.OBSERVATION_PUSH_DIR) : path.join(root, "data"), "observation-push.sqlite3");

export function readPushedEvents(root: string): PushedEvent[] {
 const file = databaseFile(root);
 if (!existsSync(file)) return [];
 const db = new DatabaseSync(file, { readOnly: true });
 try {
  db.exec("PRAGMA busy_timeout = 5000");
  return db.prepare("SELECT payload FROM observation_events ORDER BY id").all().map(row => JSON.parse(String(row.payload)) as PushedEvent);
 } finally { db.close(); }
}

export class ObservationInputError extends Error {}

export function pushObservation(root: string, body: unknown, names: Record<string, string>) {
 const parsed = input.safeParse(body);
 if (!parsed.success) throw new ObservationInputError(parsed.error.issues.map(issue => `${issue.path.join(".")}: ${issue.message}`).join("; "));
 // Validate the complete batch before opening the store, so a bad product never causes a partial write.
 for (const item of parsed.data.items) {
  if (!Object.hasOwn(names, item.product)) throw new ObservationInputError(`Unknown product: ${item.product}`);
 }
 const unique = new Map<string, typeof parsed.data.items[number]>();
 for (const item of parsed.data.items) {
  const url = new URL(item.url); url.hash = "";
  unique.set(item.product + "\n" + url.href, item);
 }
 const items = [...unique.values()];
 const duplicateCount = parsed.data.items.length - items.length;
 mkdirSync(path.dirname(databaseFile(root)), { recursive: true });
 const db = new DatabaseSync(databaseFile(root));
 try {
  db.exec("PRAGMA busy_timeout = 5000; CREATE TABLE IF NOT EXISTS observation_events (id TEXT PRIMARY KEY, payload TEXT NOT NULL)");
  db.exec("BEGIN IMMEDIATE");
  let created = 0, updated = 0, unchanged = duplicateCount;
  const ids: string[] = [];
  try {
   const read = db.prepare("SELECT payload FROM observation_events WHERE id = ?");
   const save = db.prepare("INSERT INTO observation_events (id, payload) VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload");
   for (const item of items) {
    const url = new URL(item.url); url.hash = "";
    // One product/source URL is one piece of evidence, including across separate collectors.
    const id = "push-" + createHash("sha256").update(item.product + "\n" + url.href).digest("hex").slice(0, 24);
    ids.push(id);
    const row = read.get(id);
    const prior = row ? JSON.parse(String(row.payload)) as PushedEvent : null;
    const observedAt = beijing(Date.now());
    const event: PushedEvent = {
     id, product: item.product, source_id: parsed.data.source_id, title: item.title, url: url.href, excerpt: item.excerpt,
     published_at: item.published_at ? beijing(Date.parse(item.published_at)) : null,
     publisher: item.publisher || parsed.data.source_id,
     first_seen: prior?.first_seen ?? observedAt, last_seen: prior?.last_seen ?? observedAt,
     category: "news_lead", verification: "待核验", classification: "外部推送",
     summary_mode: "外部采集原文／摘录（未经自动核验）", kind: "account", sourceLabel: "外部采集 · 待核验",
     topic: "产品相关线索", preview: item.excerpt.slice(0, 220) || "已收录标题和原文链接，内容待核验。", external: true,
    };
    if (prior && Object.keys(event).every(key => key === "last_seen" || JSON.stringify((prior as unknown as Record<string, unknown>)[key]) === JSON.stringify((event as unknown as Record<string, unknown>)[key]))) { unchanged++; continue; }
    event.last_seen = observedAt;
    save.run(id, JSON.stringify(event));
    if (prior) updated++; else created++;
   }
   db.exec("COMMIT");
   return { ok: true, created, updated, unchanged, ids };
  } catch (error) { db.exec("ROLLBACK"); throw error; }
 } finally { db.close(); }
}
