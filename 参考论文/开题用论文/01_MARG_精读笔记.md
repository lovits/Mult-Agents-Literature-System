# MARG: Multi-Agent Review Generation for Scientific Papers 精读笔记

## 文件信息

- 原始 PDF：`/Users/qianye/Downloads/课题/开题用论文/01_MARG_Multi_Agent_Review_Generation.pdf`
- MinerU 转换目录：`/Users/qianye/Downloads/课题/开题用论文/01_MARG_MinerU_md/`
- 转换得到的 Markdown：`/Users/qianye/Downloads/课题/开题用论文/01_MARG_MinerU_md/01_MARG_Multi_Agent_Review_Generation.md`
- 图片资源目录：`/Users/qianye/Downloads/课题/开题用论文/01_MARG_MinerU_md/images/`

## 一句话概括

这篇论文提出 MARG，尤其是 MARG-S：把一篇长科学论文切分给多个 LLM worker agent 阅读，由 leader agent 协调，并引入面向实验、清晰度/可复现性、创新性/影响力的 expert agent，生成更具体、更有帮助的论文审稿意见。

## 核心问题

论文要解决的是自动生成 scientific peer-review feedback。这个任务比普通摘要或问答更难，因为审稿意见需要同时做到：

- 读懂论文主张、方法、实验和论证链条。
- 发现论文真正缺失、薄弱或不自洽的地方。
- 给出可操作的修改建议，而不是泛泛而谈。
- 处理长论文超过 GPT-4 8k context 的问题。

作者认为，单个 LLM 即使是 GPT-4，也会因为上下文长度、注意力利用和任务复杂度而生成大量泛化评论；多智能体结构可以把全文分布到不同 worker，同时通过专家角色诱导更细分的审稿视角。

## 方法结构

MARG 把一个 review generation 任务组织成一个多智能体系统：

- `leader agent`：负责规划、协调、向其他 agent 广播消息、收集回复并生成最终评论。
- `worker agents`：每个 worker 读取论文的一个 chunk，保留全文覆盖能力。
- `expert agents`：不是真的拥有额外知识，而是通过 prompt 被塑造成某类审稿视角的专家。

MARG-S 是本文的完整版本。它把审稿意见生成拆成三个独立的多智能体组：

1. 实验与评估：检查实验/理论证明是否支持论文主张。expert 会先“设计理想实验”，再和论文实际实验对照，从而更容易发现缺失实验。
2. 清晰度与可复现性：检查概念、方法、实验细节是否解释清楚，是否足够复现。expert 被设计成“高度好奇”，通过提问暴露论文没有回答的问题。
3. 创新性与影响力：检查论文是否清楚说明动机、目标、关键发现，以及和已有工作的关系。作者明确说明没有做外部 related work 检索，因此这一维度主要局限于论文内部陈述是否充分。

最后还有 refinement stage：每条初始评论会交给一个新的多智能体组检查是否清晰、具体、有效；无效评论应被删除，混合评论可拆分。

## 上下文管理

作者使用 8k-token GPT-4。MARG 的基本思路不是把全文压缩进一个上下文，而是让不同 worker 分别持有不同文本块。

但多轮通信也会膨胀上下文，因此作者做了不同 agent 的历史裁剪：

- worker：保留初始 prompt 和最近 3 条消息，因为 paper chunk 已占用大量 token。
- leader：保留自己发出的完整消息，裁剪收到的旧消息，因为 leader 往往会在对外消息中总结关键信息。
- expert：实验中未观察到明显 token 限制问题，所以不裁剪。

这个设计很重要：它说明多智能体并不自动解决长上下文问题，只是把“全文输入限制”转成了“通信和记忆管理问题”。

## Baseline 设计

论文比较了多个基线：

- SARG-B：简单 prompt，单 agent 分 chunk 生成，再合并。模拟普通用户最朴素使用 ChatGPT 的方式。
- SARG-TP：单 agent，但 prompt 更精心，并加入 refinement。
- MARG-TP：多 agent，但使用接近 SARG-TP 的统一 prompt，用于观察“多 agent 本身”是否有收益。
- LiZCa：Liang et al. 2023 的 GPT-4 审稿方法，主要通过截断论文输入，效率更高但长文覆盖不足。
- MARG-S：本文完整方法，含三个专家化多智能体组和 refinement。

一个关键结论是：简单地把任务改成多 agent 并不一定更好。MARG-TP 在 recall 上低于 SARG-TP。真正有效的是多 agent 结构让作者能设计更复杂的内部任务分工，尤其是 specialized expert agents。

## 自动评估

自动评估使用 ARIES 语料中的真实审稿意见作为参照。由于真实评论标注有限，作者用 GPT-4 从真实 review 中抽取 actionable feedback comments，然后对生成评论和真实评论做语义匹配。

匹配分两阶段：

1. many-many matching：把两组评论整体交给 GPT-4，多次随机打乱顺序，保留多次出现的候选匹配。
2. pairwise matching：对候选评论对逐个判断相关性和相对具体度。只有相关性为 medium/high 且生成评论不比真实评论更泛化时，才算匹配。

指标包括 recall、precision 和 pseudo-Jaccard。作者强调 recall 更重要，因为人类较容易忽略坏评论，但漏掉好评论的损失更大。

## 关键结果

自动评估中：

- MARG-S recall 最高：15.84。
- LiZCa precision 最高：9.96，但评论数量少，平均 4.0 条。
- MARG-S 平均生成 19.8 条评论，数量最多，因此 precision 较低：4.41。
- Human baseline recall 是 9.42，precision 是 12.00，说明人类审稿人之间也存在较大分歧。
- 去掉 refinement 后，MARG-S recall 从 15.84 降到 11.92，说明 refinement 确实有贡献。

用户研究中：

- 参与者为 9 名 NLP/HCI 研究者。
- 对比方法为 MARG-S、LiZCa、SARG-B。
- MARG-S 平均每篇论文产生 3.7 条 good comments。
- SARG-B 平均 1.7 条 good comments。
- LiZCa 平均 0.3 条 good comments。
- MARG-S 约 71% 评论被评为 specific 或 very specific；LiZCa 和 SARG-B 约 40%。
- MARG-S 的主要问题是 review 太长：9 名参与者中 6 名认为 “way too long”。

## 成本问题

MARG-S 的成本非常高。平均每篇论文：

- SARG-B：15,532 input tokens，3,249 generated tokens。
- SARG-TP：54,914 input tokens，6,853 generated tokens。
- MARG-TP：134,860 input tokens，5,264 generated tokens。
- LiZCa：7,398 input tokens，869 generated tokens。
- MARG-S：1,236,344 input tokens，51,255 generated tokens。

也就是说，MARG-S 用 token 换 recall 和 specificity。它不是一个轻量方案，而是一个高成本、高召回的审稿辅助系统。

## 失败分析

作者对 10 篇论文、30 个主阶段对话，以及 30 个 refinement 对话做了定性错误分析。

主阶段错误：

- 70% 对话包含至少一种错误。
- missing context：53%。leader 给 expert 发消息时漏掉必要上下文。
- misplaced SEND MESSAGE：47%。leader 写了上下文，但把 `SEND MESSAGE` 标记放错位置，导致上下文没有真正发送。
- fails to identify error：17%。其他 agent 没能指出 leader 的通信错误。
- ignores relevant information：10%。
- failure to respond、skipping steps、message loop、exceeds input token limit 各有少量出现。

refinement 阶段错误：

- 47% 情况下没有删除无效评论。
- 30% 情况下本该删除的评论被改写成另一个评论。
- 只有 3% 样本中系统正确删除了无效评论。

这个失败分析非常有价值：它表明多 agent 系统的瓶颈不只是模型能力，还包括通信协议脆弱、上下文传递不可靠、refinement 倾向于“修补”而不是“删除”。

## 我的理解与评价

这篇论文的贡献不在于证明 LLM 能“自动替代审稿人”，而在于展示了一种更工程化的长文档审稿框架：通过角色分工、任务分解、专家视角和后处理，让 GPT-4 产生更多具体评论。

最重要的洞察有三个：

1. 多 agent 的价值来自任务结构，而不是 agent 数量本身。MARG-TP 不如 SARG-TP，说明“多几个模型聊天”并不自然带来质量提升。
2. specificity 是用户感知 helpfulness 的关键因素。MARG-S 的优势主要来自更具体的评论，而不是显著更高的准确率。
3. 高 recall 和高成本强绑定。MARG-S 生成大量评论，其中既有更多好评论，也有大量坏评论。

从研究设计上看，本文做得比较扎实：既有自动评估，也有用户研究，还有失败模式分析。但也存在明显限制。

## 局限性

- 样本规模较小：用户研究只有 9 人。
- 任务集中在 NLP/HCI 相关研究者上传的论文，外推到其他学科还需要验证。
- 自动评估依赖 GPT-4 抽取和匹配评论，存在 evaluator bias。
- 输入不包含图表视觉信息，很多实验/公式/表格问题可能无法判断。
- related work critique 没有外部检索，因此创新性评价比较受限。
- MARG-S 成本极高，不适合直接大规模部署。
- refinement 阶段对无效评论的删除能力弱，导致 bad comments 仍然很多。

## 对开题或课题设计的启发

如果你的课题涉及“多智能体辅助论文审稿 / 科研写作反馈 / 长文档理解”，这篇论文可以作为重要基线或动机来源。

可以借鉴的方向：

- 把论文审稿拆成多个维度：实验充分性、方法清晰度、创新性、可复现性、伦理风险、相关工作覆盖等。
- 让 expert agent 不只是“评价”，而是先生成期望检查清单。例如实验专家先预测应有哪些实验，再对照论文。
- 加入严格的证据定位机制：每条评论必须引用论文段落、表格或图编号，降低幻觉。
- 改进 refinement：不仅让模型“改写”，还要强制做 prune decision，并要求给出删除理由。
- 加入 retrieval：对 related work、baseline 是否充分、实验设定是否过时等问题，必须接入外部文献检索。
- 降低成本：先用便宜模型做筛选和路由，只对高价值候选问题调用强模型。

## 适合作为后续工作的切入点

1. Evidence-grounded review generation：每条审稿意见绑定原文证据，解决准确性和可解释性问题。
2. Review comment pruning：专门研究如何删除无效或低价值评论，而不是不断改写。
3. Reviewer persona calibration：不同领域、不同审稿风格的 agent 如何组合。
4. Cost-aware multi-agent routing：动态决定哪些 chunk、哪些评论需要多 agent 深度讨论。
5. Figure/table-aware review generation：结合 PDF layout、表格解析、图像理解，弥补本文纯文本输入的缺陷。

## 总结

MARG-S 证明了多智能体 LLM 系统可以在科学论文审稿意见生成中提升评论的具体性和好评论数量，但它仍然远未达到可靠自动审稿水平。它更适合作为作者自查和 reviewer 辅助工具，而不是替代专家判断。

这篇论文对“多智能体系统为什么有用”给出了一个比较清醒的答案：不是因为多个 agent 本身更聪明，而是因为多 agent 架构允许我们把复杂认知任务拆成更可控的子任务，并通过不同 prompt 诱导不同审稿策略。
