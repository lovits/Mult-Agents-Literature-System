# 后端 Deduplication Agent 进度

日期：2026-06-07

## 目标

补齐开题报告主链路中 verifier 与 evidence-aware ranker 之间的候选去重节点，并使用无需新增人工标注的 rubric-agent 数据完成消融。

## 工程结果

- 新增确定性 `evireview_core.deduplication` 模块。
- 只在同一论文、同一类别内合并高度重复候选。
- 重复组优先保留 evidence-aware 分数更高的候选。
- 完整图新增 `deduplicate_weaknesses` 节点。
- 新增 `no_dedup` 消融 profile。
- 结果保存候选数、去重后数量、重复数量和 `duplicate_of` 审计映射。

## 实验结果

Rubric-agent silver 消融使用 49 篇论文、194 条候选：

| Profile | Deduplicated | Removed | Reduction | Partial+ |
| --- | ---: | ---: | ---: | ---: |
| full | 172 | 22 | 0.1134 | 0.0360 |
| no_dedup | 194 | 0 | 0.0000 | 0.0355 |

去重减少 11.34% 的论文内重复候选，同时 shared silver reference 的 Partial+ 基本保持。该实验没有 human-gold 去重标签，因此结论限于输出紧凑性和可审计性。

## 设计边界

- 禁止跨论文去重；跨论文模板相似不代表某篇论文的具体弱点可以删除。
- 不使用类别不同的候选互相覆盖，避免丢失 focus/aspect 多样性。
- 去重不替代 verifier 或 ranker。
- 当前词面策略作为可复现 baseline；未来语义去重必须先通过 ready-label 或人工 gold 评估。
