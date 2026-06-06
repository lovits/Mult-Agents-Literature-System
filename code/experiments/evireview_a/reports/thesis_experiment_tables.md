# EviReview-Lite Thesis Experiment Tables

用途：本文件把当前 A 版实验结果整理成毕业论文实验章节可直接引用的表格。所有数值来自已落盘的 metrics JSON；未人工标注的结果统一写成 proxy / diagnostic。

## Table 1. 数据集与实验角色

| 数据集 / 样本 | 当前规模 | 用途 | 标签 / 监督来源 | 写作口径 |
| --- | ---: | --- | --- | --- |
| Local OpenReview/PRISM | 50 papers / 1463 weaknesses / 2597 blocks | 端到端论文评审辅助主数据 | OpenReview human reviews + paper text | 主应用场景；evidence gold 未完成 |
| SubstanReview | 552 test claims | substantiation verifier floor | Eval/Jus span pair | 外部人标 verifier 参照 |
| PeerReview Bench | 3881 annotations | review-quality/verifier baseline | correctness / significance / evidence labels | 无需新增人工标注的 verifier 辅助实验 |
| PeerQA-XT | 500 / 1252 test rows | Paper-RAG QA retrieval | peer-review-derived question + answer | answer-token support proxy，不是 gold evidence span |
| CLAIMCHECK | 155 main weaknesses | paper-grounded critique verifier/ranker | Grounded / Ungrounded labels | 只提交聚合结果，不提交 raw row text |
| GLM-4.6V reviewer sample | 10 papers / 27 weaknesses | LLM reviewer candidate generation | model-generated + silver verifier | clean 10-paper diagnostic，不是最终 provider benchmark |
| MiniMax-M2.7 reviewer sample | 5 papers / 15 weaknesses | LLM reviewer candidate generation | model-generated + silver verifier | 5-paper diagnostic，不是最终 provider benchmark |

## Table 2. 本地 OpenReview Paper-RAG 检索

| 方法 | Query count | Non-empty | Top-1 section align | Top-3 section align | 说明 |
| --- | ---: | ---: | ---: | ---: | --- |
| BM25 | 1463 | 0.9891 | 0.6151 | 0.8341 | section-alignment proxy |
| TF-IDF cosine | 1463 | 0.9891 | 0.6247 | 0.8238 | section-alignment proxy |
| Hybrid | 1463 | 0.9891 | 0.6164 | 0.83 | section-alignment proxy |
| Section-aware hybrid | 1463 | 0.9891 | 0.7021 | 0.8618 | section-alignment proxy |
| Hierarchical Paper-RAG | 1463 | 1 | 0.9993 | 1 | section-alignment proxy |

## Table 3. PeerQA-XT Paper-RAG QA 检索

| 方法 | Hit@1 | Hit@3 | Hit@5 | Mean answer-token recall@3 |
| --- | ---: | ---: | ---: | ---: |
| BM25 question | 0.24 | 0.598 | 0.794 | 0.4223 |
| Hybrid question | 0.242 | 0.596 | 0.792 | 0.4193 |
| Section-aware question | 0.246 | 0.606 | 0.806 | 0.4234 |
| Hierarchical question | 0.222 | 0.59 | 0.788 | 0.4209 |
| PRF section-aware question | 0.244 | 0.582 | 0.78 | 0.4188 |
| Query decomposed question | 0.208 | 0.532 | 0.734 | 0.3929 |
| Domain section-aware question | 0.208 | 0.536 | 0.742 | 0.3951 |
| Oracle answer query | 0.496 | 0.902 | 0.966 | 0.5547 |

结论口径：section-aware 是当前最稳 non-oracle 方法；oracle answer query 显示检索空间存在足够证据，但手写 query decomposition 与 PRF expansion 都会降低结果。

## Table 4. Verifier / Review-quality Baselines

| 数据集 | 任务 | 方法 | 主指标 | 少数类 / 关键类表现 | 写作口径 |
| --- | --- | --- | ---: | --- | --- |
| SubstanReview | claim substantiation | Multinomial NB | Macro-F1 0.6411 | Supported F1 0.5963 | supervised verifier floor |
| CLAIMCHECK | Grounded/Ungrounded | Feature verifier | Macro-F1 0.5076 | Ungrounded F1 0.3551 | diagnostic; verifier 仍弱 |
| PeerReview Bench | evidence | Evidence-aware feature logistic | Macro-F1 0.573 | Requires More recall 0.2381 | 少数类 recall 是主要缺口 |
| PeerReview Bench | significance | Balanced NB | Macro-F1 0.4207 | Not Significant recall 0.1383 | review-quality auxiliary |
| PeerReview Bench | correctness | Balanced context NB | Macro-F1 0.5686 | Not Correct recall 0.283 | review-quality auxiliary |

## Table 5. Reviewer Agent 生成与同批对比

| 生成器 | Papers | Generated weaknesses | Generic rate | Coverage recall@0.18 | Mean support | Partial+ rate | 说明 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Rubric-agent full baseline | 50 | 194 | 0.1804 | 0.4805 | - | - | deterministic pipeline baseline |
| GLM-4.6V clean sample | 10 | 27 | 0.0741 | 0.5952 | 0.467 | 0.5556 | clean 10-paper diagnostic |
| MiniMax-M2.7 sample | 5 | 15 | 0.0667 | 0.5232 | 0.467 | 0.4667 | 5-paper diagnostic |
| Rubric-agent on GLM overlap | 5 | 20 | 0.15 | 0.4437 | 0.2061 | 0 | paired comparison |
| GLM-4.6V on overlap | 5 | 12 | 0.0833 | 0.5232 | 0.3751 | 0.3333 | paired comparison |
| MiniMax-M2.7 on overlap | 5 | 15 | 0.0667 | 0.5232 | 0.467 | 0.4667 | paired comparison |

## Table 6. Hierarchical Paper-RAG 与 Generated Weakness Ranker

| Source | Candidates | Hierarchical mean support | Hierarchical partial+ | Top-3 rows | Top-3 mean support | Top-3 partial+ | 写作口径 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GLM-4.6V reviewer | 27 | 0.5212 | 0.6667 | 27 | 0.5212 | 0.6667 | silver-label diagnostic |
| Rubric-agent | 194 | 0.1999 | 0.0258 | 141 | 0.2343 | 0.0355 | silver-label diagnostic |

## Table 7. Evidence-aware Ranker 外部诊断与辅助分类

| 模块 | 数据集 | 方法 | 指标 | 说明 |
| --- | --- | --- | ---: | --- |
| Claim evidence ranker | CLAIMCHECK | bm25_max_similarity | MAP 0.7771 | Top-1 grounded rate 0.625 |
| Auxiliary accept/reject classifier | Local OpenReview/PRISM | metadata | Macro-F1 0.68 | 只作为辅助案例分析 |

## 实验章节写作口径

- 主贡献写成：Reviewer Agent 生成候选弱点，Paper-RAG 检索证据，Verifier 判定支持度，Ranker 输出可审计 top weaknesses。
- PeerQA-XT、PeerReview Bench、SubstanReview、CLAIMCHECK 都是不新增人工标注的外部实验支撑，但各自只覆盖 retrieval / verifier / ranker 的一部分。
- GLM-4.6V clean 10-paper 结果用于 provider diagnostic；不能写成最终模型优劣排名。
- Local OpenReview 的 300-row retrieval comparison queue 仍未人工标注，因此 section-aware vs hierarchical 的最终 evidence hit 不能下定论。
- Accept/reject classification 是 auxiliary，不应成为系统主指标。
