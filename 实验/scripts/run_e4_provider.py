import argparse
import json
import os
from pathlib import Path

import yaml

from evireview.agent.provider import OpenAICompatibleProvider
from evireview.dao.claimcheck import ClaimCheckDataset
from evireview.evaluation.e4_provider_runner import run_e4_provider_experiment


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="conf/experiments/e4_minimax_calibration.yaml")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    config = yaml.safe_load((ROOT / args.config).read_text(encoding="utf-8"))
    api_key = os.environ.get("EVIREVIEW_LLM_API_KEY") or os.environ.get("MINIMAX_API_KEY")
    if not api_key:
        raise SystemExit("EVIREVIEW_LLM_API_KEY or MINIMAX_API_KEY is required")
    provider = OpenAICompatibleProvider(
        base_url=os.environ.get("EVIREVIEW_LLM_BASE_URL", config["provider"]["base_url"]),
        model=os.environ.get("EVIREVIEW_LLM_MODEL", config["provider"]["model"]),
        api_key=api_key,
        timeout=config["provider"]["timeout_seconds"],
        max_completion_tokens=config["provider"]["max_completion_tokens"],
    )
    dataset = ClaimCheckDataset.from_source_dir(ROOT / config["dataset"]["path"])
    result = run_e4_provider_experiment(
        dataset,
        provider,
        limit=args.limit if args.limit is not None else config["experiment"]["limit"],
        top_k=config["retrieval"]["top_k"],
    )
    output = ROOT / config["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "traces"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
