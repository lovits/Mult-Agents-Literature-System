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

详细数据说明见 `dataset/README.md`，当前进度见 `PROGRESS.md`。
