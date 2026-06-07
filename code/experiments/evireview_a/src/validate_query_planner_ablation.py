from __future__ import annotations

import json
from pathlib import Path

from common import DATA_DIR


RESULT = Path(".omx/specs/autoresearch-query-planner-ablation/result.json")


def main() -> None:
    payload = json.loads((DATA_DIR / "query_planner_ablation_metrics.json").read_text(encoding="utf-8"))
    planners = payload.get("planners", {})
    passed = (
        payload.get("status") == "ok"
        and set(planners) == {"direct", "category_expansion"}
        and payload.get("metric_boundary") == "gold mapped targets"
        and all(planners[name]["main"].get("mapped_target_count", 0) > 0 for name in planners)
        and payload.get("recommended_default") in planners
    )
    result = {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "validation_mode": "mission-validator-script",
        "summary": "Query planner variants were compared on the same ready-label CLAIMCHECK targets.",
        "output_artifact_path": "code/experiments/evireview_a/reports/query_planner_ablation_report.md",
        "evidence": {
            "main_hit_at_3_delta": payload.get("main_hit_at_3_delta"),
            "recommended_default": payload.get("recommended_default"),
        },
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if not passed:
        raise SystemExit(1)
    print(result["summary"])


if __name__ == "__main__":
    main()
