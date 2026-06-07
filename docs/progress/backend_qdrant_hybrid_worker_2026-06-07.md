# 后端 Qdrant / Hybrid Worker 进度

日期：2026-06-07

## 目标

将已经通过 CLAIMCHECK ready-label 实验和真实 Qdrant 查询验证的检索能力，接入正式 API、持久化任务和 Worker 主链路。

## 完成内容

- API 可选择 `qdrant_sparse` 与 `qdrant_hybrid`。
- Worker 新增 runtime retriever factory，不把基础设施调用放进 core workflow。
- `qdrant_sparse` 为当前论文 evidence blocks 构建 BM25 sparse vectors，并使用 `paper_id` payload filter。
- `qdrant_hybrid` 同时写入 sparse 与 dense vectors，使用 Qdrant native RRF。
- 新增 OpenAI-compatible embedding adapter；配置只从 Worker 环境变量读取。
- 运行结果和 agent trace 保存实际 retriever 名称。

## 环境变量

```text
QDRANT_URL
EVIREVIEW_EMBEDDING_BASE_URL
EVIREVIEW_EMBEDDING_API_KEY
EVIREVIEW_EMBEDDING_MODEL
```

`qdrant_sparse` 只需要 Qdrant。`qdrant_hybrid` 需要全部 embedding 配置。API 请求不接受密钥。

## 验收证据

- 本地真实 Qdrant `1.18.2` sparse Worker 全链路成功。
- `SQLite persisted job -> Redis/RQ -> Worker -> real Qdrant sparse -> persisted result` 成功。
- 真实 Qdrant + 环境变量 embedding adapter 的 hybrid Worker 成功。
- CLAIMCHECK gold mapped-target 结果保持：
  - Qdrant sparse Main Hit@3：`0.3611`
  - Qdrant dense Main Hit@3：`0.5000`
  - Qdrant native RRF hybrid Main Hit@3：`0.4306`

因此默认 retriever 仍保持 `hierarchical`。Qdrant/Hybrid 是可选择实验与运行配置，不被包装为默认最优方案。

## 当前限制

- Runtime collection 按 evidence 内容散列命名并在运行时重建，适合毕业设计单机验收，不适合高并发生产环境。
- 尚未实现 collection GC、远程网络压测、HNSW 调参与向量量化。
- 真实 hosted embedding Worker 调用仍需要用户提供有效环境变量；当前工程契约和真实 Qdrant 执行已验证。
