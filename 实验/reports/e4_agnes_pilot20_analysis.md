# E4 Agnes-2.0-Flash 分层 Pilot20 分析

日期：2026-06-14

## 实验定位

本实验使用 `agnes-2.0-flash` 运行 provider-backed A0-A4，并按 CLAIMCHECK
agreement validity proxy 对 `keep/reject/uncertain` 进行确定性分层抽样，共
20 条。该规模用于正式主实验前诊断，不作为 155 条全量主结果。

## 可靠性优化

首次 Pilot20 出现 4 次瞬时网络失败。随后只增加对 `ConnectError`、
`RemoteProtocolError` 和 HTTP 408/5xx 的最多两次有限重试，不修改 Prompt、
样本、标签、检索或裁决协议。复跑后网络失败清零，剩余 1 次 Refutation JSON
解析失败，定位于 `main:lENeWLXn4W1:0`，系统按协议回退为低强度空案例。

## 复跑结果

| 系统 | Accuracy | Macro-F1 | Tokens/候选 | 延迟 ms/候选 |
| --- | ---: | ---: | ---: | ---: |
| A0 No Verification | 0.3500 | 0.1728 | 0 | 0 |
| A1 LLM-only Judge | **0.4500** | **0.3439** | 555 | 3,017 |
| A2 Single Judge + Paper-RAG | 0.4000 | 0.2635 | 4,373 | 7,524 |
| A3 Support-only + Adjudicator | 0.3500 | 0.2480 | 9,224 | 12,618 |
| A4 Support + Refutation + Adjudicator | 0.3000 | 0.1739 | 13,782 | 26,555 |

完整性指标：

- Evidence Attribution Accuracy：`1.0000`；
- 越界证据引用：`0 / 203`；
- Provider/解析失败：`1`；
- A4 相对 A2 Macro-F1：`-0.0896`；
- A4 相对 A3 Macro-F1：`-0.0741`；
- A4/A2 token 比：`3.1516`；
- A4/A2 延迟比：`3.5295`。

## 成功标准判定

| 标准 | 结果 |
| --- | --- |
| A4 相对 A2 Macro-F1 至少提高 5 个百分点 | 未通过 |
| A4 相对 A3 Macro-F1 至少提高 5 个百分点 | 未通过 |
| Evidence Attribution Accuracy ≥ 0.75 | 通过 |
| A4 成本不超过 A2 的 2.5 倍 | 未通过 |
| Provider/解析失败为 0 | 未通过 |

实验 verdict：`failed_with_metrics`。

## 误差分析与下一步

1. A2 倾向 `reject`，说明检索到相关段落后，Judge 容易把“论文存在相关内容”
   误解释为 weakness 不成立。
2. A3/A4 倾向 `keep`，说明 Support Case 对 Adjudicator 的影响强于
   Refutation Case；增加 Agent 数量没有自动提高有效性判断。
3. A4 的证据引用约束有效，但独立重复传输相同 evidence 导致 token 成本超过
   目标。
4. 下一轮只允许一次有界优化：
   - 强化“相关证据不等于支持或反驳”的 Prompt 约束；
   - 强制 Refutation 明确指出论文中解决 weakness 的具体语句；
   - 缩短 Adjudicator 输入，仅传结构化案例与引用证据，不重复全部 evidence。
5. 优化必须先在 pilot 分层集复跑；若 A4 仍不优于 A2/A3，则保留负结果并停止
   扩大，不在 main 全集反复调参。
