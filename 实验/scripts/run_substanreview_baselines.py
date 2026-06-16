import argparse
import json
from pathlib import Path

import yaml

from evireview.dao.substanreview import SubstanReviewDataset
from evireview.evaluation.substanreview_baseline_runner import (
    run_substanreview_baselines,
)


ROOT = Path(__file__).resolve().parents[1]


def run(config_path: str | Path, *, root: Path = ROOT) -> dict:
    config_path = Path(config_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    dataset = SubstanReviewDataset.from_source_dir(root / config["dataset"]["path"])
    result = run_substanreview_baselines(dataset)
    output = root / config["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="conf/experiments/substanreview_baselines.yaml",
    )
    args = parser.parse_args()

    result = run(ROOT / args.config)
    print(json.dumps({key: value for key, value in result.items() if key != "sample_results"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
