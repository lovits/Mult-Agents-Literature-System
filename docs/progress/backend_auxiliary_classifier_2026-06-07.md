# 后端辅助分类节点进度

日期：2026-06-07

## 目标

补齐开题报告中的辅助 accept/reject 分类输出，同时严格保持“分类不是主贡献、不能替代人工决策”的边界。

## 工程实现

完整图末尾新增：

```text
rank_findings -> classify_auxiliary_decision
```

分类头只读取 verifier 与 evidence-aware ranker 已有信息，输出：

- `label`: Accept / Reject tendency
- `reject_score`
- 透明 feature counts
- `metric_boundary=auxiliary diagnostic`
- `not_for_decision=true`
- 强制 warning

该输出不反向影响 weakness generation、retrieval、verification、deduplication 或 ranking。

## 真实标签实验

在 30 篇具有 silver evidence 覆盖且 Accept/Reject 平衡的本地 OpenReview 论文上：

| Method | Accuracy | Macro-F1 | ROC-AUC |
| --- | ---: | ---: | ---: |
| Evidence-risk signal | 0.4333 | 0.4007 | 0.3978 |
| Majority baseline | 0.5000 | 0.3333 | 0.5000 |
| Existing metadata baseline | - | 0.6800 | - |

结论：透明 evidence-risk signal 虽比 majority baseline 的 Macro-F1 略高，但明显低于 metadata baseline，且 ROC-AUC 低于随机水平。它只能保留为诊断与案例分析，不能成为系统创新点或自动 paper decision。
