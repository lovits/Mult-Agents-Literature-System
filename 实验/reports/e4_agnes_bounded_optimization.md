# E4 Agnes 有界优化实验报告

日期：2026-06-15

## 研究问题与边界

上一轮 Agnes 分层 Pilot20 中，A4 双向证据审计的 Macro-F1 低于 A2/A3，
且 token 成本超过 A2 的 3 倍。本轮严格遵守“一次有界优化”协议，在相同
20 条 CLAIMCHECK main 分层样本、相同 BM25 Top-5 证据和相同
agreement validity proxy 上，只修改 A3/A4：

1. Support 必须证明 weakness 实际存在，相关性不足以构成支持；
2. Refutation 必须明确证明论文已解决或反驳 weakness；
3. 无明确证据时，case strength 不得高于 0.3；
4. Adjudicator 只接收结构化 case 与 case 已引用的 evidence，不重复传输全部
   Top-5 evidence；
5. A1/A2、样本、标签和检索结果不变。

CLAIMCHECK 没有逐条 `covered/refuted` Gold，因此本实验不报告或推断
Covered/Refuted Recall。

## 结果

| 系统 | Accuracy | Macro-F1 | Tokens/候选 | 延迟 ms/候选 |
| --- | ---: | ---: | ---: | ---: |
| A0 No Verification | 0.3500 | 0.1728 | 0 | 0 |
| A1 LLM-only Judge | **0.5000** | **0.3922** | 565 | 8,170 |
| A2 Single Judge + Paper-RAG | 0.3500 | 0.2333 | 4,376 | 21,302 |
| A3 Strict Support + Compact Adjudicator | 0.2500 | 0.1889 | 5,714 | 22,725 |
| A4 Strict Bidirectional Audit + Compact Adjudicator | 0.3500 | 0.2910 | 10,866 | 33,423 |

与上一轮和本轮 baseline 的对比：

- A4 相对上一轮 A4 Macro-F1：`+0.1171`；
- A4 相对本轮 A2 Macro-F1：`+0.0577`；
- A4 相对本轮 A3 Macro-F1：`+0.1021`；
- A4/A2 token 比：从 `3.1516` 降到 `2.4829`；
- A4 token 相对上一轮减少：`21.16%`；
- Evidence Attribution Accuracy：`0.8750`；
- 越界引用：`13 / 104`；
- Provider/解析失败：`2`。

失败样本：

- `main:tpIUgkq0xa0:0`：A3 Adjudicator 返回无法解析的结构化输出，回退为
  `uncertain`；
- `main:nkfSodI4ow0:2`：A4 Refutation 调用发生连接失败，回退为空案例。

## 验收结论

| 冻结标准 | 结果 |
| --- | --- |
| A4 相对上一轮 A4 Macro-F1 至少提高 0.03 | 通过 |
| A4 不低于本轮 A2 | 通过 |
| A4 不低于本轮 A3 | 通过 |
| A4/A2 token 比不超过 2.5 | 通过 |
| Evidence Attribution Accuracy 不低于 0.75 | 通过 |
| Provider/解析失败为 0 | **未通过** |

Autoresearch 实验 verdict：`failed_with_metrics`。

严格角色约束和紧凑仲裁输入改善了质量与成本，说明优化方向有效；但零失败
门槛未通过，且越界引用高于上一轮。按照预先冻结的停止规则，不扩大到
155 条 CLAIMCHECK main，不进行第二轮 Prompt 调参。

## 与论文和后续实验的关系

本轮结果支持将“双向证据审计”保留为可解释的工程机制，但不能宣称其已在
完整主实验上稳定优于单 Judge。SubstanReview 将作为下一阶段的独立辅助评价，
用于检验 claim-evidence coverage 与 substantiation，不用于证明 weakness
本身正确。该边界与 SubstanReview 的任务定义一致，也避免用 agreement proxy
替代不存在的 covered/refuted Gold。
