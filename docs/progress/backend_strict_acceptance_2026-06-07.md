# 后端严格验收状态

日期：2026-06-07

范围：只验收后端与实验，不包含前端、鉴权、多租户和生产部署。

## 开题报告主链路

| 主链路能力 | 工程证据 | 实验证据 | 状态 |
| --- | --- | --- | --- |
| MinerU parsed-PDF ingestion | `POST /api/papers/import-mineru`、不可变版本、`source_type/source_ref` | 真实 FactReview MinerU 文档：21 sections / 28 blocks / audit succeeded | 完成 |
| Candidate weakness generation | imported + MiniMax structured reviewer | Rubric / GLM / MiniMax paired diagnostic | 工程完成；真实 hosted Worker 待最终复跑 |
| Query planning | `direct`、`category_expansion`、trace | CLAIMCHECK ready-label 消融，简单扩展无提升 | 完成 |
| Paper-RAG retrieval | BM25、hierarchical、Qdrant sparse/hybrid Worker | CLAIMCHECK ready-label + 真实 Qdrant | 完成 |
| Evidence verification | heuristic + MiniMax structured judge | SubstanReview / CLAIMCHECK / PeerReview Bench | 工程完成；真实 hosted Worker 待最终复跑 |
| Intra-paper deduplication | verifier 后独立节点 + `duplicate_of` | 194 -> 172，减少 11.34%，silver Partial+ 基本保持 | 完成 |
| Evidence-aware ranking | 独立 ranker + graph ablation | full 优于 no-verifier/no-ranker shared-silver reference | 完成 |
| Auxiliary classification | `not_for_decision=true` 诊断节点 | Macro-F1 0.4007，低于 metadata baseline 0.68 | 完成，明确否决为主贡献 |
| Persisted report | Markdown report API | Local acceptance test | 完成 |

## 本地总验收

已通过正式 acceptance test：

```text
MinerU parsed paper
  -> immutable SQLite version
  -> Redis/RQ
  -> Worker
  -> real Qdrant sparse retrieval
  -> heuristic verifier
  -> deduplication
  -> evidence-aware ranking
  -> auxiliary diagnostic classification
  -> persisted Markdown report
```

## 唯一未闭环的严格验收项

当前 shell 未设置 `MINIMAX_API_KEY`。因此以下真实 hosted 路径尚未完成最终复跑：

```text
API/persisted paper
  -> Redis/RQ
  -> MiniMax-M2.7 weakness generation
  -> Qdrant sparse retrieval
  -> MiniMax-M2.7 evidence judge
  -> deduplication
  -> ranker
  -> auxiliary diagnostic
  -> report
```

仓库已提供 gated test：

```text
tests/integration/test_minimax_backend_acceptance.py
```

需要环境：

```text
export MINIMAX_API_KEY
EVIREVIEW_MINIMAX_INTEGRATION=1
EVIREVIEW_QDRANT_INTEGRATION=1
EVIREVIEW_REDIS_INTEGRATION=1
EVIREVIEW_REDIS_URL=redis://127.0.0.1:6379/15
```

之前在聊天中明文发送的 Key 应先轮换，不应作为最终验收凭据。
