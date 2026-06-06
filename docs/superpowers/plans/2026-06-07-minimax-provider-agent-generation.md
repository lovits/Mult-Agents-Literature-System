# MiniMax M2.7 Provider And Agent Generation Plan

## Goal

接入 MiniMax Token/Coding Plan 的 `MiniMax-M2.7`，把模型调用从实验脚本抽到可测试的 provider adapter，并补齐 Agent-RAG 的 `generate_or_import_weaknesses` 节点。前端不在本阶段范围内。

## Constraints

- API key 仅从 `MINIMAX_API_KEY` 环境变量读取，不进入代码、日志、报告或 durable docs。
- core 不新增第三方依赖，使用标准库 HTTP 和可注入 transport。
- 默认确定性工作流继续使用传入 weaknesses，不自动触发外部模型。
- MiniMax 实验属于 provider diagnostic / silver diagnostic，不作为 human-gold 结论。
- MiniMax 结果使用独立文件前缀，不覆盖 GLM 或其他实验产物。

## Implementation

1. 新增 provider contract 与 MiniMax OpenAI-compatible adapter。
2. adapter 统一处理 structured JSON、有限重试、超时和公开错误脱敏。
3. 在显式 Agent-RAG graph 中增加 `generate_or_import_weaknesses` 节点。
4. 通过可注入 generator 连接 provider 与 workflow，保留确定性导入路径。
5. 新增独立 MiniMax reviewer diagnostic 脚本并运行小规模样本。
6. 更新进度文档，记录真实请求结果、指标边界与剩余风险。

## Verification

- provider 与 workflow 单元测试先 RED 后 GREEN。
- core、backend、API 测试全量通过。
- MiniMax 最小真实调用成功，随后运行小规模 reviewer diagnostic。
- `compileall`、`git diff --check`、密钥扫描通过。

