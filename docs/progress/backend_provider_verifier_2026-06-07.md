# 后端 Provider Evidence Judge 与 ready-label 验收

日期：2026-06-07

## 本轮目标

补齐开题报告 Stage 3 Evidence Verification 的可选择后端路径，使 verifier 能独立于 retriever 配置、执行和验收。

## 后端实现

1. review-audit 配置新增 `verifier`，当前支持 `heuristic` 和 `minimax`。
2. `heuristic` 保持默认，避免外部调用改变现有可复现实验。
3. `minimax` 由 Worker 从环境变量构造，不允许 API 请求传入密钥。
4. structured evidence judge 只接收 weakness 与检索后的 evidence bundle。
5. provider 输出被约束到既定 verifier labels、`0..1` support score 和实际检索到的 evidence IDs。
6. system prompt 明确将论文正文视为不可信数据，禁止执行正文中的指令。
7. verifier 名称进入持久化结果，支持后续独立消融和审计。

## ready-label 复跑结果

| 数据集 | 方法 | 主要结果 | 结论 |
| --- | --- | --- | --- |
| SubstanReview | Multinomial NB substantiation verifier | Test Macro-F1 `0.6411`; Supported F1 `0.5963` | 证明 verifier 层可在人工标签上独立评估 |
| CLAIMCHECK | Feature-fusion groundedness verifier | Macro-F1 `0.5076`; Ungrounded F1 `0.3551` | 少数类有所改善，但不够强，不能提升为默认 verifier |
| CLAIMCHECK | Train-fold embedding threshold | Macro-F1 `0.5477`; Ungrounded F1 `0.3056` | embedding 更适合 retrieval，不足以单独完成 verifier |

## 研究驱动的架构修正

- PRISM 2026 支持将 reviewer 评价拆分为多维度，而不是只看文本相似度或总分。
- Mind the Blind Spots 支持后续增加 `target × aspect` focus coverage。
- LLM-as-a-Reviewer 与 Breaking the Reviewer 支持把 prompt injection / textual attack 作为独立后端验收维度。
- TreeReview 支持研究动态问题树 planner，但现有 query-planner ready-label 消融没有提升，因此暂不改变默认 planner。

## 验证边界

- 自动化测试覆盖 structured verifier 标签约束、证据 ID 白名单、API 组件校验、Worker 注入执行和结果审计。
- 当前环境没有 `MINIMAX_API_KEY`，真实 hosted MiniMax Evidence Judge 尚未在本轮重跑。
- 在 ready-label 结果证明提升前，默认 verifier 继续保持 `heuristic`，并明确标记为 silver diagnostic。
