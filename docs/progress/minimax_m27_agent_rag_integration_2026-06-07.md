# MiniMax M2.7 Agent-RAG 接入与实验进度

日期：2026-06-07

## 本次目标

冻结前端工作，继续后端 Agent-RAG 与实验主线。接入 MiniMax Token/Coding Plan 的 `MiniMax-M2.7`，并将 provider-backed weakness generation 纳入显式状态图。

## 已完成工程内容

1. 新增无第三方依赖的 MiniMax OpenAI-compatible provider adapter。
   - 中国区 endpoint：`https://api.minimaxi.com/v1/chat/completions`
   - 模型：`MiniMax-M2.7`
   - key 只从 `MINIMAX_API_KEY` 环境变量读取。
   - 支持有限重试、超时、structured JSON 提取、`<think>` 区块剥离和公开错误脱敏。

2. 新增通用 `StructuredReviewerGenerator`。
   - 将 provider structured output 转换为 domain `Weakness`。
   - 保存 provider、model、prompt、schema、attempt、latency 等诊断 metadata。

3. 扩展显式 Agent-RAG graph。
   - 新增首节点 `generate_or_import_weaknesses`。
   - 已有 weakness 时走 deterministic import，不触发 provider。
   - 无 weakness 且注入 generator 时执行 provider generation。
   - 完整链路为：生成或导入 -> 检索 -> 校验 -> 排序。

4. 新增独立 MiniMax reviewer diagnostic 脚本和产物。
   - 不覆盖 GLM 结果。
   - 复用现有 PRISM/OpenReview 样本、coverage proxy、Paper-RAG retrieval 与 silver verifier。

## 真实调用与实验结果

### 接口与完整图验证

- `MiniMax-M2.7` 中国区接口最小 structured JSON 请求成功。
- 一篇论文的真实完整 Agent-RAG 链路成功：
  - generated weaknesses：3
  - ranked findings：3
  - `generate_or_import_weaknesses`：succeeded
  - `retrieve_evidence`：succeeded
  - `verify_weaknesses`：succeeded
  - `rank_findings`：succeeded

### 5 篇 reviewer diagnostic

| 指标 | 结果 |
| --- | ---: |
| 选中论文 | 5 |
| 成功生成论文 | 5 |
| 生成 weaknesses | 15 |
| 失败论文 | 0 |
| generic rate | 0.0667 |
| human weakness recall@0.18 proxy | 0.5232 |
| mean silver support score | 0.4670 |
| Supported | 2 |
| Partially Supported | 5 |
| Mentioned but Not Problem | 7 |
| Unsupported | 1 |

## 指标边界

- MiniMax 输出为 provider diagnostic / silver diagnostic，不是 human-gold 评测。
- recall 使用与既有 reviewer 实验相同的文本相似度 coverage proxy。
- verifier 标签来自本地 silver verifier，适合比较流程与 provider 行为，不适合直接声明最终评审准确率。

## 下一步

1. 把 graph 配置注册表接入 worker，使 provider / retriever / verifier / ranker 可按实验 manifest 选择。
2. 增加 `imported vs MiniMax generated`、`with vs without verifier` 节点消融导出。
3. 在保持无人工标注约束下，将 MiniMax diagnostic 扩到与 GLM 相同论文集合后做 paired provider comparison。
4. 再进入 Dense/Qdrant hybrid retrieval。

