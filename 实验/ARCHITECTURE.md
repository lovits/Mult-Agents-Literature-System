# 实验目录架构

## 设计原则

- 实验代码、数据、配置、测试和结果互相隔离。
- 原始数据只读；可再生中间数据进入 `dataset/processed/`。
- 第三方数据仓库源码、Git 元数据、压缩包和历史实验不进入当前实验目录。
- `src/evireview/` 只实现本论文的多 Agent RAG 自动评审领域能力。

## 目录职责

```text
实验/
├── conf/                    # 可复现实验参数与数据注册
├── dataset/
│   ├── raw/                # 按实验角色组织的只读数据
│   └── processed/          # 可由脚本重新生成的中间数据
├── outputs/                # 指标、日志与报告，不进入 Git
├── scripts/                # 下载、实验运行和验收入口
├── src/evireview/
│   ├── conf/               # 运行配置模型
│   ├── dao/                # 数据集与外部来源适配
│   ├── evaluation/         # 实验指标
│   ├── models/             # 领域协议
│   ├── rag/                # Paper-RAG 与后续 Literature-RAG
│   ├── service/            # 论文解析、数据处理等服务
│   └── system/             # Agent-RAG 自动评审系统编排层
└── tests/
    ├── unit/               # 组件行为测试
    ├── experiments/        # 数据与实验验收
    └── fixtures/           # 最小测试样本
```

## 数据角色

| 目录 | 用途 | 是否可用于调参 |
| --- | --- | --- |
| `raw/primary/` | 完整论文处理与端到端评审 | 可以，需固定划分 |
| `raw/evaluation/` | 带 Gold 标签的组件严格评价 | 仅开发集可调参 |
| `raw/literature/` | Literature-RAG 固定外部语料 | 不得混入在线搜索结果 |
| `raw/demo/` | 未见论文最终演示 | 不可以 |
| `raw/restricted/` | 尚需申请的数据占位与状态说明 | 不适用 |

## 当前边界

当前阶段只实现后端实验，不包含前端、部署脚本、第三方模型训练代码或其他旧实验实现。

## 后端 Agent-RAG 系统层

`src/evireview/system/` 是当前实验代码的系统入口，不直接承载指标优化。它把已有
组件编排为一条可复现后端链路：

1. `paper_adapter.py`：将 OpenReview/arXiv-like 输入转换为 `PaperDocument` 和
   `EvidenceBlock`；
2. `planner.py`：为每条候选弱点生成 section-aware、evidence-type-aware 的
   `QueryPlan`；
3. `review_pipeline.py`：串联 candidate generation、Paper-RAG、support/refutation
   双向审计、adjudication 和 report assembly；
4. `ranker.py`：实现 evidence-aware Meta-Reviewer Top-K 去重、排序与置信度标注；
5. `schemas.py` / `config.py`：定义系统级请求、结果、trace 和配置。

该层不输出论文接收/拒稿决策，不包含 human-check 路由，也不包含前端代码。它用于
后续 E6 端到端实验和 provider 模型接入前的稳定系统框架。
