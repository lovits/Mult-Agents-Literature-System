# 后端 Agent-RAG 状态图进度

日期：2026-06-06

## 方向调整

根据最新要求，前端工作已冻结。后续主线调整为实验与后端 Agent-RAG 系统搭建。

本次优先解决重构文档中长期存在的后端缺口：现有审计流程虽然可以执行，但仍由单一函数串联，尚未形成显式、可追踪、可替换节点的 Agent 状态图。

## 已完成内容

1. 显式 Agent-RAG 状态
   - 新增 `ReviewAuditState`。
   - 统一保存弱点、证据块、top-k 配置、检索候选、校验结果、排序结果和 Agent 节点轨迹。

2. 纯节点拆分
   - `generate_or_import_weaknesses`
   - `retrieve_evidence`
   - `verify_weaknesses`
   - `rank_findings`
   - 节点调用现有 hierarchical retrieval、heuristic verifier 和 evidence-aware ranker，不复制算法实现。

3. ReviewAuditGraph
   - 按固定顺序执行三个节点。
   - 每个成功节点记录 `node + status`。
   - 节点失败只记录异常类型，不记录 provider 响应、证据正文或内部错误详情。
   - 使用 `AgentNodeError` 标记具体失败节点。

4. 兼容现有实验与 worker
   - 保留 `run_deterministic_review_audit()` 作为稳定入口。
   - 现有 API、worker 和实验调用方无需修改调用方式。
   - 原有 `workflow`、retrieval、verification、ranked findings 和 `silver diagnostic` 字段保持不变。
   - 新增 `agent_trace`，为后续节点消融、provider 接入和运行诊断提供依据。

5. 后端可观察性
   - 新增 `GET /api/runs/{run_id}/agent-trace`。
   - 公共响应只返回节点名、状态和错误类型。
   - 不返回输入、证据正文、内部异常或 provider 响应。

## 与实验计划对齐

- RQ2 Paper-RAG 检索对应 `retrieve_evidence`。
- RQ3 证据校验对应 `verify_weaknesses`。
- Top-K 高价值问题排序对应 `rank_findings`。
- 节点级轨迹支持后续进行：
  - no-verifier / no-ranker 消融；
  - hierarchical / hybrid retriever 替换实验；
  - heuristic / feature / LLM verifier 对比；
  - rubric / GLM weakness provider 接入。

## 当前限制

- 当前图是显式固定状态图，尚未加入条件分支、节点重试和动态路由。
- weakness generation 已进入图，并已通过 MiniMax M2.7 真实调用验证；worker 配置注册表尚未开放 provider 选择。
- 当前只接入 deterministic hierarchical + heuristic 路径。
- 已接入统一 structured provider contract 与 MiniMax adapter；GLM/OpenRouter 尚待迁移。
- 尚未接入 Dense/Qdrant；现有 BM25/hierarchical baseline 保持不变。

## 真实后端链路验证

- 通过 API 导入一篇新论文并创建版本绑定审计运行。
- 真实 Redis/RQ worker 执行完成，运行状态达到 `succeeded`。
- `GET /api/runs/{run_id}/agent-trace` 返回：
  - `retrieve_evidence: succeeded`
  - `verify_weaknesses: succeeded`
  - `rank_findings: succeeded`
- 运行保留调度时不可变 `paper_version_id`。
- 前端文件未继续修改。

## 下一步后端顺序

1. 增加图配置注册表，使 provider/retriever/verifier/ranker 可按实验清单切换。
2. 迁移 GLM 调用到统一 provider contract。
3. 增加实验指标聚合与节点消融导出。
4. 最后接入 Dense/Qdrant hybrid retrieval。
