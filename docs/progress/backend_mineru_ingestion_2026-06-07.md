# 后端 MinerU Parsed-PDF 导入进度

日期：2026-06-07

## 目标

补齐 Markdown-only 导入缺口，将 MinerU 已解析的 PDF Markdown 接入统一 Paper Section、Evidence Block、不可变版本和 review-audit 契约。

## 完成内容

- 新增 MinerU Markdown 适配器：
  - 删除 YAML frontmatter；
  - 删除独立图片链接噪声；
  - 保留标题层级、图注、表格文本、公式和正文。
- 新增 `POST /api/papers/import-mineru`。
- API 接收解析后的 Markdown，不接受任意本地文件路径。
- paper 与 immutable paper version 保存：
  - `source_type=mineru_markdown`
  - `source_ref=<原 PDF 或解析资产引用>`
- 普通 Markdown 导入继续保持 `source_type=markdown`。

## 真实资产验收

使用仓库中的 FactReview MinerU 文档完成：

```text
MinerU parsed Markdown
  -> 21 sections
  -> 28 evidence blocks
  -> persisted immutable version
  -> qdrant_sparse retrieval
  -> verifier
  -> deduplication
  -> ranker
```

运行状态为 `succeeded`，目标弱点被判定为 `Partially Supported`。

## 边界

- 后端不重复实现 PDF OCR、版面识别或公式识别；这些能力由 MinerU 提供。
- 当前接口接收 MinerU parsed Markdown，而不是原始 PDF 二进制。
- `source_ref` 只保存来源引用，不由 API 读取该路径，避免任意文件读取风险。
