# 竞品观察运行说明

## 本机访问

网站入口：<http://127.0.0.1:3300/observe/outputs/competitor-ui-prototype.html>

读取接口：

- `GET /api/observation/snapshot`：五个栏目使用的完整快照。
- `GET /api/observation/status`：17 个来源的最近状态、条数和失败信息。
- `GET /api/observation/events?product=ima`：动态与官方发布记录。
- `GET /api/observation/feedback?product=workbuddy`：用户反馈样本。
- `GET /api/observation/reports`：日报、周报、月报索引。

页面读取采集快照与外部推送记录的合并结果；打开页面不会触发抓取或模型调用。来源状态异常时保留上一次页面数据，并显示异常数量。

## Harness 推送

本机独立服务：在仓库目录运行 `npm run dev:observe`。首次自动生成 `.env.observation`，其中 `INGEST_TOKEN` 是本机推送密钥；不要提交该文件或把密钥写进网页。默认只监听 `127.0.0.1:3300`，不需要 PostgreSQL、模型 API 或 Docker。更换端口可在该文件中设置 `OBSERVATION_PORT`；`OBSERVATION_ROOT` 指向含 `outputs/observation.json` 的内容根目录，相对路径以仓库为准。服务重启后配置生效。

Harness 配置：

- Method：`POST`
- URL：`http://127.0.0.1:3300/api/observation/events`
- Header：`Authorization: Bearer <.env.observation 中的 INGEST_TOKEN>`
- Header：`Content-Type: application/json`
- Body：见 [harness-push-example.json](harness-push-example.json)，将示例内容替换为真实采集记录。

`source_id` 是采集来源标识，字母、数字、短横线或下划线，最多 80 位；`items` 每批 1–50 条。每条必填 `product`、`title`、`url`；`excerpt`、`publisher` 和 `published_at` 可选。没有原始发布日期时传 `null`，不要用抓取时间冒充发布日期；有日期时须使用带时区的 ISO 时间。来源链接只接受无账号密码的 HTTP(S) 地址。当前产品标识：`notebook`、`ima`、`lexiang`、`weknora`、`chatgpt`、`workbuddy`、`doubao`、`patsnap`、`xinghe`。

成功返回 `ok:true`、`created`、`updated`、`unchanged` 和记录 `ids`。相同产品与原文 URL 去重；重复推送不会重复出现，内容改变会更新。推送记录保存在 `data/observation-push.sqlite3`，与内置采集快照分开，服务重启或重新采集后仍保留。网页读取时合并，已有采集记录与推送记录的产品和链接相同时优先显示已有采集记录。页面默认每分钟更新，手动刷新可立即读取。

这一入口接收动态线索，不自动生成日报正文、用户反馈分类或战略结论，也不会把提交内容自动标为官方已验证事实。未带有效密钥返回 401，字段错误返回 400 且整批不写入，观察快照不可用返回 503。

本机命令行调用（在仓库目录；示例文件应先替换为真实记录）：

```bash
node --env-file=.env.observation --input-type=module <<'JS'
import { readFile } from 'node:fs/promises';
const response = await fetch(`http://127.0.0.1:${process.env.OBSERVATION_PORT || 3300}/api/observation/events`, {
  method: 'POST',
  headers: { Authorization: `Bearer ${process.env.INGEST_TOKEN}`, 'Content-Type': 'application/json' },
  body: await readFile('docs/harness-push-example.json', 'utf8'),
});
console.log(response.status, await response.json());
JS
```

Docker 模式沿用 `.env` 中的 `INGEST_TOKEN`，独立服务使用的 `.env.observation` 不会自动进入容器。推送 SQLite 在 API 的持久数据卷 `/data/observation` 下；页面、接口的路径不变。

## 数据更新

`collector` 容器每小时运行一次：

1. 从 `monitor/sources.json` 的 17 个公共 RSS、Apple、GitHub 和 Hacker News 来源读取数据。
2. 保存原始响应、SQLite 去重状态和 `outputs/monitor-data.json`。
3. 重新生成 `outputs/observation.json`、动态页面和日报。
4. 将新闻与官方发布记录按来源分批（每批最多 50 条）送到 AIHOT 的认证导入接口。
5. AIHOT 负责入库和后续公开内容处理；同步状态保存在 `data/aihot-sync.json`。

基线记录、历史补录和新发现线索会保留标记；重复运行不会重复发送或重复入库。评论、GitHub Issue 保留在竞品观察数据中，不会混入 AIHOT 的新闻导入。

手动立即更新：

```bash
docker compose -f docker-compose.yml -f compose.observation.yml exec collector python3 /workspace/monitor/run.py --once
```

只重新构建当前快照，不抓取来源：

```bash
docker compose -f docker-compose.yml -f compose.observation.yml exec collector python3 /workspace/monitor/run.py --once --no-collect
```

查看状态：

```bash
docker compose -f docker-compose.yml -f compose.observation.yml ps
docker compose -f docker-compose.yml -f compose.observation.yml logs --tail 50 collector
```

## 启停

启动：

```bash
docker compose -f docker-compose.yml -f compose.observation.yml up -d
```

停止：

```bash
docker compose -f docker-compose.yml -f compose.observation.yml down
```

当前端口只绑定本机：网站 `3300`、API `3301`、PostgreSQL `55432`。上线前需要另行配置域名、HTTPS、访问控制和数据备份；当前默认只适合本机验证和持续采集。

## 证据边界

新闻检索 RSS 只代表标题级线索；官方署名和正文需要继续核验。Apple 评论仅是中国区 iOS 的有限样本，不代表全部用户。网站保留原文链接、发布日期和首次发现时间，不把采集时间当成发布日，也不以样本计数推算总体满意度。
