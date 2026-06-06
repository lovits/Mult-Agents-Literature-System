from __future__ import annotations

import json
from pathlib import Path

from common import DATA_DIR, REPORT_DIR


def main() -> None:
    comparison = json.loads((DATA_DIR / "generated_reviewer_comparison_metrics.json").read_text(encoding="utf-8"))
    unified = json.loads((DATA_DIR / "unified_metrics.json").read_text(encoding="utf-8"))
    required = {"rubric_agent", "glm_reviewer", "minimax_reviewer"}
    passed = (
        comparison.get("overlap_paper_count", 0) >= 5
        and required.issubset(comparison.get("generators", {}))
        and all(item.get("paper_count") == comparison["overlap_paper_count"] for item in comparison["generators"].values())
        and any(item.get("method") == "minimax_reviewer" for item in unified)
    )
    result = {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": "Three reviewer generators compared on an exact common paper overlap and exported through Phase 2H-A.",
        "overlap_paper_count": comparison.get("overlap_paper_count", 0),
        "generators": sorted(comparison.get("generators", {})),
        "output_artifact_path": str(REPORT_DIR / "generated_reviewer_comparison_report.md"),
    }
    output = Path(".omx/specs/autoresearch-provider-paired-comparison/result.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
