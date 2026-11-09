# 竞品观察运行说明

## 本机访问

网站入口：<http://127.0.0.1:3300/observe/outputs/competitor-ui-prototype.html>

读取接口：

- `GET /api/observation/snapshot`：五个栏目使用的完整快照。
- `GET /api/observation/status`：17 个来源的最近状态、条数和失败信息。
- `GET /api/observation/events?product=ima`：动态与官方发布记录。
- `GET /api/observation/feedback?product=workbuddy`：用户反馈样本。
- `GET /api/observation/reports`：日报、周报、月报索引。

页面只读取已经保存的快照；打开页面不会触发抓取或模型调用。来源状态异常时保留上一次页面数据，并显示异常数量。

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
