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
│   └── service/            # 用例编排与论文处理服务
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
