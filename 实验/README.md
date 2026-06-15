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
```

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

详细数据说明见 `dataset/README.md`，当前进度见 `PROGRESS.md`。
