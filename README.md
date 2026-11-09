# 竞品观察

这是一个围绕 AI 产品竞品观察构建的网站，包含竞品研究、动态跟踪、竞品日报、用户反馈和战略分析五个栏目。仓库同时保存页面原型、采集器、来源配置、观察数据快照和报告归档。

## 本地预览

当前页面由静态 HTML 原型和 AIHOT API 服务共同提供。先准备 `.env`（可从 `.env.example` 复制并按需填写），再启动：

```bash
docker compose -f docker-compose.yml -f compose.observation.yml up --build
```

打开 <http://127.0.0.1:3300/observe/outputs/competitor-ui-prototype.html>。API 服务默认监听本地 `3301` 端口。页面快照位于 `outputs/observation.json`；采集数据和本地数据库运行时保存在 `data/`，不会提交到 Git。

## 更新观察数据

项目包含 `monitor/` 下的来源采集、整理和同步脚本。先在 `monitor/sources.json` 配置观察来源，再按 `.env.example` 配置 API 连接信息。采集器写入的 API 数据与页面快照更新是两个步骤；仅成功写入 API 不代表页面快照已刷新。当前仓库提交的 `outputs/observation.json` 是可直接预览的最近一次快照，持续更新流程仍需按部署环境配置并验证。

## 目录

- `outputs/competitor-ui-prototype.html`：五栏目网站入口
- `outputs/competitor-research-complete.html`：竞品研究正文
- `outputs/observation.json`：页面观察数据快照
- `work/ui-prototype/`：页面构建器、交互与栏目样式
- `monitor/`：采集器、数据整理与 API 同步
- `reports/`：页面引用的日报、周报、月报归档
- `docs/`：数据来源、运行和编辑说明

本项目在 AIHOT 基础上适配；许可和上游来源见 [LICENSE](LICENSE)、[NOTICE](NOTICE) 与 `outputs/aihot-prototype-notice.html`。
