# Agent-RAG 重构 Phase 3 进度：Paper Workspace

日期：2026-06-06

## 阶段切换

本次不再继续扩展 Phase 2.x。根据重构架构文档，项目已正式进入 Phase 3：前端 Paper Workspace。

Phase 3 的目标是把开题报告主链路变成可检查、可展示、可答辩的证据工作流：

`weakness -> Paper-RAG evidence -> verifier -> evidence-aware ranker -> trace/report`

## 本次完成内容

1. Paper Workspace 前端
   - 新增同源页面：`GET /workspace/`。
   - 实现论文列表、审计运行列表和三栏工作区。
   - 中栏展示弱点、排序信息和不可变版本论文证据。
   - 右栏展示 verifier/ranker 结果、运行轨迹和报告导出。
   - 强制展示 `silver diagnostic` 等指标边界。
   - 支持空弱点、空运行、加载和错误状态。

2. Phase 3 公共读模型
   - 新增 `GET /api/papers`。
   - 新增 `GET /api/papers/{paper_id}/runs`。
   - 新增 `GET /api/runs/{run_id}/workspace`。
   - workspace 响应白名单化汇总论文、运行版本、弱点、证据、检索、验证、排序、轨迹和报告。
   - 不返回 `input_json`、`artifact_path`、队列 token 或内部错误。

3. 架构与技术选型
   - 首个 Phase 3 切片使用 FastAPI 同源托管的 HTML/CSS/JavaScript。
   - 未新增依赖，避免在没有明确依赖许可时安装 Next.js。
   - API 合约保持框架无关，后续可直接接入 Next.js 客户端。
   - 保留现有 SQLite、Redis/RQ 和不可变论文版本链路。

## Deep-research 与开题对齐结论

- 工作区围绕证据链组织，而不是做通用项目管理页面。
- 证据块、校验标签、支持分数和排序分数同时可见，直接支撑开题报告中的 Paper-RAG、Weakness Evidence Verifier 和 Evidence-aware Ranker。
- 运行版本和证据来源进入工作区读模型，避免答辩展示时无法说明实验复现边界。
- 指标性质显式展示，避免将 `silver diagnostic` 误写为人工金标结论。

## 浏览器验证

- 1440×900：三栏布局稳定，论文导航、证据工作区和校验详情互不重叠。
- 390×844：三栏按顺序堆叠为单栏。
- 移动布局 `bodyScrollWidth == bodyClientWidth`，无横向溢出。
- 浏览器控制台无 error/warn。
- 实际切换到 `Version Drift E2E` 运行后，可读取：
  - 弱点文本和 rank 1；
  - 不可变版本 A 的证据块；
  - `Mentioned but Not Problem` 标签；
  - support/rank score；
  - queued -> running -> succeeded 轨迹。

## 当前限制与风险

- 当前为本地可信研究工作台，没有鉴权；workspace API 会展示论文证据和弱点文本，不能直接暴露到公网。
- 本次完成 Phase 3 首个纵向切片，尚未实现项目 CRUD、PDF 预览和交互式运行创建表单。
- 前端暂未引入 Next.js、组件测试框架或构建工具。
- Experiment Dashboard 属于 Phase 4，尚未开始。
- Dense/Qdrant 属于 Phase 5，尚未开始。

## 后续正式阶段

1. 继续完成 Phase 3：项目导航、运行创建表单、证据筛选和更完整报告操作。
2. 进入 Phase 4：Experiment Dashboard，将现有实验 JSON/Markdown 指标转为答辩展示页面。
3. 最后进入 Phase 5：Dense/Qdrant 和 hybrid retrieval 对比实验。
