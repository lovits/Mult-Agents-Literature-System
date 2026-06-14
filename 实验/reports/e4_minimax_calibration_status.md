# E4 MiniMax-M2.7 Provider 校准状态

日期：2026-06-14

## 目的

按照开题报告 E4 主实验协议，接入 MiniMax-M2.7 并运行 provider-backed A0-A4：

- A0：No Verification；
- A1：LLM-only Judge；
- A2：Single Judge + Paper-RAG；
- A3：Support-only + Adjudicator；
- A4：Support + Refutation + Adjudicator。

## 接入结果

- 官方模型 ID：`MiniMax-M2.7`；
- 有效区域：中国区；
- OpenAI-compatible Base URL：`https://api.minimaxi.com/v1`；
- 全球区 `https://api.minimax.io/v1` 对当前 Key 返回 401；
- 中国区 `/v1/models` 返回 200，并确认 `MiniMax-M2.7` 可用；
- Key 仅通过当前进程环境变量传入，未写入任何仓库文件。

## 当前校准状态

首条 CLAIMCHECK 样本已经进入 A0-A4 provider runner。A1-A4 共计划执行 6 次真实调用，但全部返回：

```text
HTTP 429
Token Plan usage limit reached
MiniMax error code: 2056
```

因此当前 Autoresearch 状态为 `pending_quota`，不能生成或报告正式模型指标。

| 检查 | 结果 |
| --- | --- |
| 模型与中国区端点可达 | 通过 |
| A0-A4 runner 数据链路 | 通过 |
| A0-A4 系统覆盖 | 通过 |
| 实际成功调用 | 0 / 6 |
| 失败分类 | `http_429`: 6 |
| 模型 tokens | 0 |
| 校准验收 | `pending_quota` |

## 已完成工程能力

1. OpenAI-compatible provider，支持 MiniMax M2.x reasoning 输出；
2. JSON-only 结构化输出解析；
3. A0-A4 统一 runner；
4. Paper-RAG evidence bundle 输入；
5. Support、Refutation 与 Adjudicator 独立调用；
6. 越界证据过滤；
7. 调用数、tokens、延迟、失败原因与逐样本轨迹记录；
8. Provider 失败时回退 `uncertain`，不会静默当作成功。

## 额度恢复后的执行命令

```bash
cd /Users/qianye/Downloads/毕业设计/实验
export MINIMAX_API_KEY=...
../.venv/bin/python scripts/run_e4_provider.py \
  --config conf/experiments/e4_minimax_calibration.yaml
../.venv/bin/python scripts/validate_e4_minimax_calibration.py
```

校准通过后再扩大样本规模，不能直接将当前失败回退结果用于论文结论。

## 官方依据

- MiniMax API Overview：<https://platform.minimax.io/docs/api-reference/api-overview>
- OpenAI-compatible Chat Completions：<https://platform.minimax.io/docs/api-reference/text-chat-openai>
- Token Plan 第三方工具与区域配置：<https://platform.minimax.io/docs/token-plan/other-tools>
