# EviReview-Lite 实验

本目录直接承载最新版开题报告定义的多 Agent、双 RAG、双向证据审计自动论文评审后端及全部实验代码，不再使用额外的实验包装目录。

当前不包含前端，不复用旧实验指标。

目录分层与边界见 `ARCHITECTURE.md`。

## 快速验证

```bash
../.venv/bin/python -m pytest -q
../.venv/bin/python scripts/run_e0.py --config conf/experiments/e0_data.yaml
../.venv/bin/python scripts/validate_dataset_bootstrap.py
../.venv/bin/python scripts/validate_flat_layout_task6.py
../.venv/bin/python scripts/validate_peerqa_e2_foundation.py
../.venv/bin/python scripts/run_e2.py --config conf/experiments/e2_paper_rag.yaml
../.venv/bin/python scripts/validate_execution_stage_a_b.py
../.venv/bin/python scripts/validate_agent_rag_system_framework.py
```

Agent-RAG 后端系统框架验收：

```bash
../.venv/bin/python scripts/validate_agent_rag_system_framework.py
```

该验收只检查候选弱点生成、Query Planner、Paper-RAG、双向审计、自动裁决、
Meta-Reviewer Top-K 排序和报告组装链路是否完整；不做指标优化，也不宣称相对
baseline 已经提升。

正式 E2 使用独立 Python 3.12 环境：

```bash
uv venv --python 3.12 .venv-formal
UV_HTTP_TIMEOUT=300 uv pip install --python .venv-formal/bin/python -e '.[dev,formal]'
HF_HUB_OFFLINE=1 .venv-formal/bin/python scripts/run_e2.py \
  --config conf/experiments/e2_paper_rag_formal.yaml
../.venv/bin/python scripts/validate_e2_formal.py
```

正式 E4 CLAIMCHECK 基线：

```bash
HF_HUB_OFFLINE=1 .venv-formal/bin/python scripts/run_e4_baselines.py \
  --config conf/experiments/e4_claimcheck_baselines.yaml
../.venv/bin/python scripts/validate_e4_baselines.py
```

E4 固定双向证据审计协议 smoke：

```bash
../.venv/bin/python scripts/run_e4_audit_protocol_smoke.py
../.venv/bin/python scripts/validate_e4_audit_protocol.py
```

该 smoke 仅验证协议、轨迹和证据引用约束，不是正式 provider-backed A0-A4。

MiniMax-M2.7 provider 校准：

```bash
export MINIMAX_API_KEY=...
../.venv/bin/python scripts/run_e4_provider.py \
  --config conf/experiments/e4_minimax_calibration.yaml
../.venv/bin/python scripts/validate_e4_minimax_calibration.py
```

当前 Token Plan 返回 HTTP 429 / MiniMax 2056，校准状态为 `pending_quota`。

Agnes-2.0-Flash 分层 Pilot20：

```bash
export EVIREVIEW_LLM_API_KEY=...
../.venv/bin/python scripts/run_e4_provider.py \
  --config conf/experiments/e4_agnes_calibration.yaml
../.venv/bin/python scripts/validate_e4_agnes_calibration.py
../.venv/bin/python scripts/run_e4_provider.py \
  --config conf/experiments/e4_agnes_pilot20.yaml
../.venv/bin/python scripts/validate_e4_agnes_pilot20.py
```

当前 Pilot20 已完成，实验 verdict 为 `failed_with_metrics`，暂不扩大。

Agnes 一次有界优化：

```bash
export EVIREVIEW_LLM_API_KEY=...
../.venv/bin/python scripts/run_e4_provider.py \
  --config conf/experiments/e4_agnes_pilot20_optimized.yaml
../.venv/bin/python scripts/validate_e4_agnes_bounded_optimization.py
```

有界优化使 A4 Macro-F1 提升至 `0.2910`，A4/A2 token 比降至 `2.4829`，
但仍有 2 次 Provider/解析失败。按冻结协议停止扩大，下一步转入 SubstanReview
证据充分性辅助实验。

SubstanReview 辅助评价：

```bash
../.venv/bin/python scripts/run_substanreview_baselines.py \
  --config conf/experiments/substanreview_baselines.yaml
../.venv/bin/python scripts/validate_substanreview_baselines.py
```

当前官方 test split 上 Claim Evidence Coverage 为 `0.4155`，最强 baseline 为
`S0_proximity`，Supported F1 为 `0.5925`，Evidence Hit@1 为 `0.6680`。该结果
只作为 review claim-evidence substantiation 辅助评价，不作为 weakness validity
或 covered/refuted Gold。

E6 端到端报告与候选生成诊断：

```bash
../.venv/bin/python scripts/run_e6_end_to_end_report.py \
  --config conf/experiments/e6_end_to_end_report.yaml
../.venv/bin/python scripts/validate_e6_end_to_end_report.py
../.venv/bin/python scripts/run_e6_candidate_diagnostics.py \
  --config conf/experiments/e6_candidate_diagnostics.yaml
../.venv/bin/python scripts/validate_e6_candidate_diagnostics.py
```

当前 OpenReview seed 为 30 篇论文、122 条 Official Review。B3 cue-aware
candidate generator 相对 B2 的 proxy overlap delta 为 `+0.0044`；E6-D 诊断显示
B3 在 19 篇论文上提升、11 篇论文上退化，下一步使用退化样本做 provider-generated
candidates 对照。

当前 B4 Agent-RAG pipeline 已接入 E6，完整运行 candidate generation、Query Planner、
Paper-RAG、support/refutation 双向审计、Adjudication 和 Meta-Reviewer Top-K。
B4 的 proxy overlap 为 `0.0559`，相对 B3 的 `0.0549` 小幅提升 `+0.0010`；
Trace、Top-K、Pipeline Stage 和 Support/Refutation 覆盖均为 `1.0000`。

当前 B5 Balanced Agent-RAG pipeline 在 B4 基础上只优化 Top-K 选择层：优先保留不同
aspect 的候选，并加入 `0.03` 候选先验权重。B5 proxy overlap 为 `0.0570`，相对
B4 提升 `+0.0011`，Aspect Diversity 从 `0.9111` 恢复到 `1.0000`。

E6-B5 diagnostics 进一步确认：B5 相对 B4 为 `7/21/2` 篇提升/持平/退化；
更有代表性的瓶颈是 `experiment` 切片，Proxy Overlap@K 为 `0.0510`。下一轮优化
应优先做候选过滤或 aspect-specific query planning，而不是继续扩大 provider prompt。

E6 DeepSeek provider 候选生成对照：

```bash
export EVIREVIEW_LLM_API_KEY=...
export EVIREVIEW_LLM_BASE_URL=https://api.ccode.vip/v1
export EVIREVIEW_LLM_MODEL=deepseek-v4-flash-free
../.venv/bin/python scripts/run_e6_provider_candidates.py \
  --config conf/experiments/e6_deepseek_provider_candidates.yaml
../.venv/bin/python scripts/validate_e6_provider_candidates.py
```

当前 E6-P 已在 8 个 E6-D failure cases 上完成，但 verdict 为 `failed_with_metrics`：
provider output coverage 为 `0.0000`，provider_failures 为 `8`，P1 相对 B3/B2
failure slice 均未提升。该结果说明当前 provider 配置不能替代 B3，需要先处理限流、
JSON 输出稳定性或更换更稳定模型。

后端 Agent-RAG 系统框架：

```bash
../.venv/bin/python scripts/validate_agent_rag_system_framework.py
```

当前框架验收通过：单篇论文输入可自动完成论文分块、候选弱点生成、结构与证据类型
感知 Paper-RAG、support/refutation 双向证据审计、adjudication、Meta-Reviewer
Top-K 排序和结构化报告组装。该阶段是框架搭建，不报告新的 baseline 提升。

详细数据说明见 `dataset/README.md`，当前进度见 `PROGRESS.md`。
