# 竞品观察布局调整 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 根据参考图调整竞品观察的全局宽度、日报对齐、往期侧栏和口碑观察排版。

**Architecture:** 保持 `work/ui-prototype` 作为页面生成源；在 CSS 中覆盖宽度和响应式布局，在 `digest.js` 中过滤面向用户的日报状态文案，在 `digest.html` 与 `feedback.css` 中保持语义结构和移动端降级。生成脚本继续把这些源合并到 `outputs/competitor-ui-prototype.html`，数据和 API 不变。

**Tech Stack:** HTML, CSS, vanilla JavaScript, Python page builder, Node/TypeScript checks.

## Global Constraints

- 内容正文保持左对齐。
- 页面不设置内容区最大宽度，随屏幕宽度延展。
- 保持五个栏目和持续更新 API。
- 日报侧栏不显示“编辑版”“采集汇总”等内部状态。
- 新闻、Issue 和用户评论继续保持证据类型区分。

### Task 1: Remove fixed content width and align report content

**Files:**
- Modify: `work/ui-prototype/prototype.css`
- Modify: `work/ui-prototype/digest.css`

- [x] 将 `--content-width` 改为不限制宽度的布局规则，保留 `width:100%` 和响应式内边距。
- [x] 让日报正文、头部、元信息、页脚和前后期导航共享左边缘。
- [x] 保留 1100px、760px、420px 断点，检查表格、图片、对话框不产生页面级横向溢出。

### Task 2: Simplify report history labels and stabilize story grid

**Files:**
- Modify: `work/ui-prototype/digest.js`
- Modify: `work/ui-prototype/digest.css`

- [x] 期次下拉和往期列表只渲染日期与标题，不渲染 `status`。
- [x] 日报头部不渲染状态字段。
- [x] 双栏 `.digest-columns` 让每个故事共享同一列网格；单个故事跨整行并保持左对齐。

### Task 3: Align perception cards

**Files:**
- Modify: `work/ui-prototype/feedback.css`

- [x] 为口碑卡片建立排名、内容、数量三段网格，确保标题、标签、提及数和正文长度一致。
- [x] 限制长标题和引用的行高与换行方式，避免卡片宽度被内容撑开。
- [x] 移动端改为排名与内容两列，数量回到标题行内，保持可读性。

### Task 4: Build and verify

**Files:**
- Regenerate: `outputs/competitor-ui-prototype.html`, `outputs/prototype-news.json`, `outputs/observation.json`

- [x] Run `python3 work/ui-prototype/build.py`.
- [x] Run `node work/ui-prototype/check-responsive.cjs`.
- [x] Run `node work/ui-prototype/check.cjs` and `python3 work/ui-prototype/verify.py`.
- [x] Run `npm run typecheck` and the observation standalone test.
- [x] Run `git diff --check` inside `website`.
