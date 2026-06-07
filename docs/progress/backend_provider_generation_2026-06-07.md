# 后端 Provider 弱点生成贯通进度

日期：2026-06-07

## 本轮目标

将已经存在于 core 和实验脚本中的 MiniMax structured reviewer 接入实际 API、持久化任务和 Worker，使开题报告 Stage 1 候选弱点生成能够进入同一条 Agent-RAG 后端主链路。

## 已实现

1. API review-audit 请求新增显式 `weakness_generator` 配置，当前支持 `imported` 和 `minimax`。
2. API 只接收组件名称，不接收 provider key；未知 generator 返回 422。
3. Worker 在任务显式选择 `minimax` 时从环境变量构造 `MiniMaxProvider` 和 `StructuredReviewerGenerator`。
4. 生成后的 weaknesses 继续进入 Query Planner、Paper-RAG、Verifier 和 Ranker。
5. 运行结果持久化实际生成 weaknesses、生成模式和脱敏 generation metadata。
6. Workspace read model 能读取生成后的 weaknesses，而不是只显示空的输入列表。
7. 实验批量调度请求保留 `weakness_generator` 配置。

## 验证边界

- Core、Backend 和 API 自动化测试已覆盖 provider generator 的配置校验、Worker 注入执行和生成结果持久化。
- 当前 shell 未提供 `MINIMAX_API_KEY`，因此本轮没有重新运行真实 hosted-provider 后端调用。
- 之前 MiniMax provider adapter 的真实调用与 reviewer diagnostic 结果保持有效，但不能替代本轮 Worker 路径的真实密钥验收。
- Provider 结果仍属于 silver diagnostic，必须经过 evidence gate，不能作为人工 gold 结论。

## 下一步

1. 增加可选择 verifier 注册表，并接入 provider-backed Evidence Judge。
2. 使用 CLAIMCHECK / SubstanReview ready-label 数据验证 verifier，而不是使用当前 heuristic silver labels 选择默认配置。
3. 在提供 `MINIMAX_API_KEY` 后执行一次真实 API -> Redis/RQ -> Worker -> MiniMax -> Retrieval -> Verifier -> Ranker 全链路验收。
