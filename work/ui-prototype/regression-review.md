# 工作台回归记录 · 2026-10-27

当前产物：outputs/competitor-ui-prototype.html，UI 原型 v8。

## 本次调整
- 主导航保留竞品研究、全部竞品动态、竞品日报、用户反馈、战略分析。移除报告归档和新产品观察的导航及面板，原始报告和采集记录保留。
- 日报保留周期切换、往期和来源证据；旧 reports 路由转到 digest，discover 路由转到 updates。
- 参考 AIHOT Sidebar、Tabs、AllPage、ReportLayout、ReportNav、ReportPaper 统一页面边界、控件间距与报纸阅读宽度。
- 动态产品切换和搜索框允许换行并可收缩，避免 flex 最小宽度撑开页面；研究页和动态页产品胶囊的字号、高度和选中态统一。
- 日报报头、正文、前后期导航统一为最大 1180px 的居中阅读区域。
- 清理已移除的来源筛选运行逻辑及旧站点 Tab 的悬空 ARIA 引用。

## 已执行验证
- python3 work/ui-prototype/build.py：构建成功，十个研究/战略正文面板与输入一致。
- node work/ui-prototype/check.cjs：五个栏目、九个研究产品、十个动态产品筛选、重置、日期/搜索、详情、报告周期、历史期次、空状态、日历、跨年周次、旧路由通过。
- python3 work/ui-prototype/verify.py：导航数量、已移除面板、唯一 ID、ARIA、锚点、本地报告链接、截图和脚本语法通过。
- python3 work/verify_navigation.py：九个原始产品正文和截图保持一致。

## 验证边界
本地浏览器工具返回“Local browser use is disabled in Work settings”。本次样式回归基于现有截图和本地 AIHOT 源码，未执行真实浏览器截图、多分辨率渲染或像素对比，不宣称完成视觉实测。
