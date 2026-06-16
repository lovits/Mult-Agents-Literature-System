# SubstanReview 证据充分性辅助实验

日期：2026-06-16

## 实验定位

本实验对应开题报告中的“评审意见证据充分性辅助评价”。SubstanReview 提供
review 内部 claim-evidence span 标注，适合评价评审意见是否被同一条评审文本
中的理由支撑。

边界如下：

- 使用官方切分：`train=440`，`test=110`；
- 使用 gold claim span，只评价 evidence linkage 与 substantiation；
- threshold 仅在 train split 上选择，test split 只用于报告指标；
- 不把 SubstanReview 当作 weakness validity、covered/refuted 或录用分类 Gold。

## 数据统计

| 项目 | 数值 |
| --- | ---: |
| 总 review 数 | 550 |
| Train review 数 | 440 |
| Test review 数 | 110 |
| 总 claim 数 | 2,940 |
| Test claim 数 | 580 |
| Test claim-bearing review 数 | 106 |
| Test supported claim 数 | 241 |
| Claim Evidence Coverage | 0.4155 |
| Substantiated Claim Rate | 0.4251 |
| Mean SubstanScore | 176.0458 |

## Baseline

本阶段不训练模型，不新增依赖，只建立可复现下界：

| 系统 | 方法 |
| --- | --- |
| S0 Proximity | 选择距离 claim 最近的候选证据片段 |
| S1 Lexical | 选择与 claim token overlap 最高的候选证据片段 |
| S2 Hybrid | 0.7 lexical + 0.3 proximity |

候选证据片段来自 review 句子切分；若 claim 与 evidence 在同一句中，系统使用
claim 前后剩余片段作为候选证据，避免直接把 claim 本身当 evidence。

## 结果

| 系统 | Supported Precision | Supported Recall | Supported F1 | Evidence Hit@1 | Evidence Token-F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| S0 Proximity | 0.4240 | 0.9834 | **0.5925** | **0.6680** | **0.5030** |
| S1 Lexical | 0.4155 | 1.0000 | 0.5871 | 0.1701 | 0.2176 |
| S2 Hybrid | 0.4162 | 1.0000 | 0.5878 | 0.5187 | 0.4570 |

最强系统为 `S0_proximity`。该结果说明 SubstanReview 中大量 evidence 紧邻对应
claim，位置先验是很强的可复现下界；单纯 lexical overlap 不能稳定找到具体
evidence span。

## 结论与后续

SubstanReview 已可作为 E4/E6 的辅助 substantiation 指标来源：

- `Claim Evidence Coverage` 可衡量候选评审意见集合中有多少 claim 带有证据；
- `Substantiated Claim Rate` 可衡量每条 review 的平均证据支撑比例；
- `Evidence Hit@1` 和 `Evidence Token-F1` 可评价证据定位质量。

该实验不改变 CLAIMCHECK E4 的主结论：Agnes A4 在有界优化后质量和成本改善，
但因 provider/解析失败未达零失败门槛，仍停止扩大。下一步按实验计划进入
E3 Controlled Literature-RAG，建立外部文献证据的可核验检索 baseline。
