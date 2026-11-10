# 竞品观察

这是一个围绕 AI 产品竞品观察构建的网站，包含竞品研究、动态跟踪、竞品日报、用户反馈和战略分析五个栏目。仓库同时保存页面原型、采集器、来源配置、观察数据快照和报告归档。

## 本地预览

最快的本机方式（Node.js 24，首次先 `npm ci`，不需要 PostgreSQL）：

```bash
npm run dev:observe
```

打开 <http://127.0.0.1:3300/observe/outputs/competitor-ui-prototype.html>。同一服务提供 `POST /api/observation/events`，用于 Harness 推送；首次启动自动生成 `.env.observation` 中的本机密钥。请求格式和使用方法见 [Harness 推送说明](docs/competitor-observation-live.md#harness-推送)。本机服务只监听本机地址，不自动抓取数据。

需要启动完整 AIHOT 底座与每小时采集时，准备 `.env`（从 `.env.example` 复制并按需填写），停止独立服务后启动：

```bash
docker compose -f docker-compose.yml -f compose.observation.yml up --build
```

打开 <http://127.0.0.1:3300/observe/outputs/competitor-ui-prototype.html>。API 服务默认监听本地 `3301` 端口。页面快照位于 `outputs/observation.json`；采集数据和本地数据库运行时保存在 `data/`，不会提交到 Git。

## 更新观察数据

项目包含 `monitor/` 下的来源采集、整理和同步脚本。内置采集器重新生成页面快照；Harness 使用 `POST /api/observation/events` 保存到独立 SQLite，网页读取时合并，因此不会被下一次采集覆盖。页面每分钟读取一次最新数据，手动刷新可立即读取。外部推送显示为待核验线索，暂不自动编入日报或口碑主题。AIHOT 的 `/api/ingest/items` 仍是另一条数据库导入路径。

## 目录

- `outputs/competitor-ui-prototype.html`：五栏目网站入口
- `outputs/competitor-research-complete.html`：竞品研究正文
- `outputs/observation.json`：页面观察数据快照
- `work/ui-prototype/`：页面构建器、交互与栏目样式
- `monitor/`：采集器、数据整理与 API 同步
- `reports/`：页面引用的日报、周报、月报归档
- `docs/`：数据来源、运行和编辑说明

本项目在 AIHOT 基础上适配；许可和上游来源见 [LICENSE](LICENSE)、[NOTICE](NOTICE) 与 `outputs/aihot-prototype-notice.html`。
