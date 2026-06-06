# Agent-RAG 重构 Phase 2D 进度

日期：2026-06-06

## 本阶段目标

让审计任务直接引用已导入论文的持久化证据块，避免客户端和运行输入重复传输证据正文，同时保持审计任务使用的证据集合可追踪。

## 已完成内容

1. 论文范围审计接口
   - 新增 `POST /api/papers/{paper_id}/review-audit`。
   - 请求仅包含弱点、`top_k` 和 `finding_top_k`。
   - 严格拒绝内联 `evidence_blocks` 和其他额外字段。
   - 保留原有 `POST /api/runs/review-audit`，兼容外部或临时内联证据。

2. 紧凑运行输入
   - 创建任务时按稳定顺序快照论文的证据块 ID。
   - 新运行输入保存 `evidence_block_ids` 和 `evidence_source=persisted_paper_snapshot`。
   - 新运行输入不保存证据正文。

3. Worker 证据解析
   - Worker 同时支持旧的内联证据与新的证据 ID 快照。
   - 按快照顺序从 SQLite 精确解析证据块。
   - 任意快照证据缺失时任务显式失败，避免静默使用不完整证据集合。

4. 生命周期可靠性
   - 新旧审计入口共享入队与失败补偿逻辑。
   - 队列未配置时在创建运行前拒绝，避免遗留孤儿 queued 记录。
   - 队列投递失败时继续将已持久化运行标记为 failed。

## 分层边界

- FastAPI 路由只负责 HTTP 校验和错误映射。
- `ReviewAuditService` 负责证据快照、运行创建和入队编排。
- `SQLiteRunRepository` 负责有序 ID 快照和精确解析。
- Worker 负责在执行边界解析证据并调用确定性核心流程。

## 当前限制与风险

- 证据块当前仍属于可替换的论文派生资产；若论文在任务执行前被重导入且旧 ID 被删除，任务会显式失败。
- 后续要实现真正可长期复现的运行，应增加论文资产版本和不可变 evidence snapshot 表。
- 当前仍为 `silver diagnostic`，不替代人工金标评估。
- 未实现前端、PDF/MinerU 导入、鉴权、多租户和对象存储。

## 验证结果

- API 测试 17 项通过。
- 后端测试 27 项通过。
- 核心测试 25 项通过。
- Redis/RQ 显式集成测试 1 项通过。
- 真实 HTTP 链路验证：
  - Markdown 论文导入返回 201。
  - 论文范围审计创建返回 202。
  - SQLite 运行输入只包含 `evidence_block_ids`，不包含 `evidence_blocks` 或论文证据正文。
  - RQ worker 完成运行，状态为 succeeded。
  - 报告创建与 Markdown 读取成功。

## 下一阶段建议

1. 为论文资产增加 `version_id`，使运行引用不可变版本，而不是当前活动论文记录。
2. 将数据集版本、实验配置、运行与报告关联为可复现实验清单。
3. 增加批量论文审计任务，为后续实验复跑和论文结果表格提供统一入口。
