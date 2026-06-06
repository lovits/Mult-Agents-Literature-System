from __future__ import annotations

import json
from pathlib import Path

from common import DATA_DIR


def main() -> None:
    metrics = json.loads((DATA_DIR / "graph_ablation_metrics.json").read_text(encoding="utf-8"))
    profiles = metrics.get("profiles", {})
    passed = (
        {"full", "no_verifier", "no_ranker"}.issubset(profiles)
        and metrics.get("candidate_count", 0) > 0
        and profiles["full"]["mean_reference_support"] >= profiles["no_verifier"]["mean_reference_support"]
        and profiles["full"]["mean_reference_support"] >= profiles["no_ranker"]["mean_reference_support"]
    )
    result = {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": "Full graph preserves the strongest mean support under the shared silver reference.",
        "profiles": profiles,
        "output_artifact_path": "code/experiments/evireview_a/reports/graph_ablation_report.md",
    }
    path = Path(".omx/specs/autoresearch-graph-ablation/result.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
