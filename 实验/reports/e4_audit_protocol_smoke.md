# E4 固定双向证据审计协议 Smoke

日期：2026-06-14

## 目的

本阶段实现开题报告 Task 10/11 定义的 Support Agent、Refutation Agent 与 Evidence Adjudicator，并在 CLAIMCHECK `main` 的全部 155 条 weakness 上验证固定双向执行、证据引用约束、自动裁决和可追踪输出。

本结果是离线启发式 smoke，`formal_a0_a4_result=false`，不能作为正式 A0-A4 主实验结果。

## 协议

- 每条候选固定运行 Support 与 Refutation，不使用争议触发升级；
- 两个 Agent 只能引用输入 EvidenceBundle 内证据；
- 空证据案例 strength 不得超过 0.2；
- Adjudicator 仅输出 `keep`、`rewrite`、`reject`、`uncertain`；
- 不存在 `human-check`；
- CLAIMCHECK `agreement` 使用版本化 `claimcheck-agreement-proxy-v1` 映射：
  - 1–2：`reject`
  - 3：`uncertain`
  - 4–5：`keep`
- 映射是 validity proxy，不生成 CLAIMCHECK 不具备的 `rewrite` 或 covered/refuted Gold。

## 完整性结果

| 检查 | 结果 |
| --- | ---: |
| 运行候选数 | 155 |
| 完整审计轨迹 | 155 |
| 越界证据引用 | 0 |
| 缺失双向案例 | 0 |
| 空案例强度违规 | 0 |
| human-check 决策 | 0 |

## Smoke 指标

| 系统 | Agreement Proxy Accuracy | Macro-F1 | 决策分布 |
| --- | ---: | ---: | --- |
| A3 Heuristic Smoke | 0.4194 | 0.2674 | keep 93，uncertain 62 |
| A4 Heuristic Smoke | 0.0774 | 0.1164 | keep 1，rewrite 78，reject 49，uncertain 27 |

## 结论

1. 固定双向证据审计协议和自动裁决数据链路已完成。
2. 启发式 A4 明显低于 A3，说明简单覆盖词和词汇重叠会导致 Refutation 过度触发。
3. 该负结果限制后续实现：正式 Refutation Agent 必须独立判断“论文是否实际覆盖或反驳该意见”，不能将相关段落直接视为反驳证据。
4. 正式 E4 必须运行 provider-backed A0-A4，并单独报告 A2 vs A4、A3 vs A4、成本和延迟。

## 文献对齐

- CLAIMCHECK 将 agreement 定义为 weakness validity 判断，并显示该判断存在专家分歧：<https://arxiv.org/abs/2503.21717>
- FactReview 使用 claim-level evidence verdict 与可追踪证据报告，支持保留审计轨迹的设计：<https://arxiv.org/abs/2604.04074>

## 限制

- 当前没有配置正式 LLM provider，因此没有运行 LLM-only Judge、Single Judge + Paper-RAG 或正式 Support/Refutation Agent。
- 当前 Refutation 是用于验证协议的确定性启发式，不代表论文创新有效。
- CLAIMCHECK 不含逐条 covered/refuted Gold，因此不报告 Covered/Refuted Recall。
