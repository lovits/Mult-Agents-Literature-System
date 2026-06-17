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
│   ├── dao/                # 数据集、PDF/Markdown/OpenReview/JSON 来源适配
│   ├── evaluation/         # 实验指标
│   ├── models/             # 领域协议
│   ├── rag/                # Paper-RAG 与后续 Literature-RAG
│   ├── service/            # 文档归一化、解析 Agent 编排与证据映射
│   ├── agent/              # 候选评审、解析、审计与排序 Agent
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
   `EvidenceBlock`，后续由统一文档解析管线替代其直接拼接职责；
2. `planner.py`：为每条候选弱点生成 section-aware、evidence-type-aware 的
   `QueryPlan`；
3. `review_pipeline.py`：串联 candidate generation、Paper-RAG、support/refutation
   双向审计、adjudication 和 report assembly；
4. `ranker.py`：实现 evidence-aware Meta-Reviewer Top-K 去重、排序与置信度标注；
5. `schemas.py` / `config.py`：定义系统级请求、结果、trace 和配置。

该层不输出论文接收/拒稿决策，不包含 human-check 路由，也不包含前端代码。它用于
后续 E6 端到端实验和 provider 模型接入前的稳定系统框架。

## 统一文档解析层

论文解析主路径采用 LLM-first 的 Agent 管线：

```text
Source Adapter
  -> Document Normalizer
  -> Document Parsing Agent
     -> Structure Segmentation
     -> LLM Section Labeling
     -> LLM Evidence-Type Labeling
  -> Evidence Mapper
```

职责边界：

1. `Source Adapter` 接入 PDF、Markdown、OpenReview、arXiv 和 JSON/JSONL，记录来源、
   checksum 和原始 metadata，不直接生成证据块；
2. `Document Normalizer` 将所有输入统一转换为 Markdown，并生成 `parse_manifest.json`；
   PDF 优先使用 MinerU，失败或低置信时使用 Docling / OCR / LLM fallback；
3. `Document Parsing Agent` 从 Markdown 中识别 heading、paragraph、table、figure caption、
   algorithm、equation、appendix、reference 和 page boundary，并形成候选文档块；
4. `Document Parsing Agent` 使用 LLM 作为章节别名映射和证据类型映射的主路径。LLM 必须从固定
   canonical section 与 evidence type 集合中选择，并输出 `canonical_section`、`evidence_type`、
   `confidence`、`rationale` 和 `matched_cues`；
5. 代码层只做 JSON schema 校验、固定标签集合约束、低置信 fallback 和解析轨迹记录，不使用规则词典优先；
6. `Evidence Mapper` 将 `DocumentBlock` 转换为 `EvidenceBlock`，保留 raw section title、
   page/span、parser、LLM confidence、prompt version、fallback reason 和解析来源。

固定 canonical section：

```text
front_matter / abstract / introduction / related_work / method / experiments /
ablation / results / analysis / limitations / discussion / conclusion /
appendix / references / unknown
```

LLM 在该层的边界：

- 作为章节别名、文本标签和证据类型映射的主路径；
- 不改写论文正文；
- 不直接生成评审弱点；
- 不决定证据是否支持结论；
- 输出必须通过 JSON schema 和固定标签集合校验；
- 无效 JSON、越界标签或低置信输出统一落为 `unknown`，并记录 fallback 原因；
- 每次调用记录模型名、prompt 版本、置信度和 fallback 原因。
