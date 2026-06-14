import argparse
import json
from pathlib import Path

import yaml

from evireview.dao.claimcheck import ClaimCheckDataset
from evireview.evaluation.e4_audit_smoke_runner import run_e4_audit_protocol_smoke


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="conf/experiments/e4_audit_protocol_smoke.yaml",
    )
    args = parser.parse_args()

    config = yaml.safe_load((ROOT / args.config).read_text(encoding="utf-8"))
    dataset = ClaimCheckDataset.from_source_dir(ROOT / config["dataset"]["path"])
    result = run_e4_audit_protocol_smoke(dataset, top_k=config["retrieval"]["top_k"])
    output = ROOT / config["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
