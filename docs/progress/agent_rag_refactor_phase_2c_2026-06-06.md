# Agent-RAG 重构 Phase 2C 进度

日期：2026-06-06

## 本阶段目标

在不开发前端、不调用外部模型、不修改既有实验数据的前提下，补齐 Agent-RAG 后端的论文资产导入与审计报告资产链路，使现有确定性 Paper-RAG 审计流程可以通过 API 使用持久化论文证据，并产出可追踪的 Markdown 报告。

## 已完成内容

1. Markdown 论文导入
   - 使用现有 `iter_sections` 解析章节。
   - 使用现有 `chunk_text` 构建证据块。
   - 保留短但有效的章节作为证据。
   - 使用稳定哈希生成 section/block ID。
   - 同一 `paper_id` 重导入时，在 SQLite 事务内原子替换派生资产。

2. 论文资产持久化与 API
   - 新增 `papers`、`paper_sections`、`evidence_blocks` 表。
   - 新增论文导入、论文信息、章节列表、证据块列表接口。
   - 导入响应不回显原始 Markdown。
   - 公共证据块 DTO 与审计输入契约一致，可直接用于创建审计运行。

3. 审计报告资产
   - 新增确定性 Markdown 报告渲染器。
   - 仅允许成功运行生成报告。
   - 报告明确标注 `silver diagnostic`，包含排序发现、验证证据 ID 和运行轨迹。
   - 报告文件写入被 Git 忽略的 `storage/reports/`，SQLite 只保存元数据和内部路径。
   - 公共报告元数据不暴露内部文件路径、队列字段或内部错误。

4. 分层边界
   - 核心报告转换位于 `packages/evireview_core`。
   - SQLite 持久化位于 repository。
   - 论文和报告用例位于 service。
   - HTTP 转换位于独立 FastAPI router。

## 当前接口

- `POST /api/papers/import`
- `GET /api/papers/{paper_id}`
- `GET /api/papers/{paper_id}/sections`
- `GET /api/papers/{paper_id}/evidence-blocks`
- `POST /api/runs/{run_id}/report`
- `GET /api/reports/{report_id}`
- `GET /api/reports/{report_id}/markdown`

## 验证边界

- API 测试 15 项、后端测试 21 项、核心测试 25 项通过。
- Redis/RQ 显式集成测试 1 项通过。
- 真实 HTTP 链路已覆盖论文导入、证据块读取、审计入队、worker 执行、报告生成和 Markdown 读取。
- 回归覆盖论文导入、原子替换、短章节保留、导入证据直接审计、报告生成、未完成运行拒绝、404/409/422 和公共响应脱敏。
- 报告和现有工作流仍属于银标诊断，不是人工金标评估。
- Phase 2C 只支持 Markdown 文本；PDF/MinerU 作为后续导入适配器。
- 当前未做前端、鉴权、项目多租户、对象存储和外部模型调用。

## 下一阶段建议

1. 增加“使用已导入 evidence blocks 创建审计运行”的轻量服务方法，避免客户端重复传回证据正文。
2. 增加 PDF/MinerU 导入适配器，但保持统一的 section/evidence-block 持久化契约。
3. 将实验配置、数据集版本与审计报告关联，形成论文实验可复现实验清单。
4. 在后端契约稳定后再开始前端，优先实现论文资产、运行轨迹、证据审计和报告查看四个工作视图。
