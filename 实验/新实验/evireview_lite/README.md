# EviReview-Lite 新实验

本目录从零实现最新版开题报告定义的多 Agent、双 RAG、双向证据审计自动论文评审后端。

当前不包含前端，不复用旧实验指标。

## 快速验证

```bash
../../../.venv/bin/python -m pytest -q
../../../.venv/bin/python scripts/run_e0.py --config conf/experiments/e0_data.yaml
../../../.venv/bin/python scripts/validate_dataset_bootstrap.py
```

详细数据说明见 `dataset/DATASET_REPORT.md`，当前进度见 `PROGRESS.md`。
