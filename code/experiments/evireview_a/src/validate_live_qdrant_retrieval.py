from __future__ import annotations

import json

from common import DATA_DIR


def main() -> None:
    path = DATA_DIR / "live_qdrant_retrieval_metrics.json"
    if not path.exists():
        raise SystemExit("live_qdrant_retrieval_metrics.json missing")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "ok":
        raise SystemExit("live Qdrant experiment is not successful")
    if payload.get("index", {}).get("point_count", 0) <= 0:
        raise SystemExit("no Qdrant points were indexed")
    required = {
        "qdrant_bm25_sparse",
        "qdrant_openrouter_dense",
        "qdrant_bm25_openrouter_rrf_hybrid",
    }
    if set(payload.get("methods", {})) != required:
        raise SystemExit("live Qdrant method set mismatch")
    for method in required:
        metrics = payload["methods"][method]["main"]
        for name in ("hit_at_1", "hit_at_3", "hit_at_5", "hit_at_10", "mrr"):
            if not 0 <= metrics.get(name, -1) <= 1:
                raise SystemExit(f"invalid {method}.{name}")
        if metrics.get("latency_ms_p95", 0) <= 0:
            raise SystemExit(f"missing {method} latency")
    print("live Qdrant retrieval validator passed")


if __name__ == "__main__":
    main()
