import argparse
import json
from pathlib import Path

import yaml

from evireview.dao.claimcheck import ClaimCheckDataset
from evireview.evaluation.e4_baseline_runner import run_e4_baselines
from evireview.rag.embedding import SentenceTransformerEmbedder


ROOT = Path(__file__).resolve().parents[1]


def build_embedding_provider(config: dict) -> SentenceTransformerEmbedder:
    embedding = config["embedding"]
    return SentenceTransformerEmbedder(
        model_name=embedding["name"],
        revision=embedding["revision"],
        device=embedding.get("device", "cpu"),
        local_files_only=embedding.get("local_files_only", True),
        query_instruction=embedding["query_instruction"],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="conf/experiments/e4_claimcheck_baselines.yaml")
    args = parser.parse_args()

    config = yaml.safe_load((ROOT / args.config).read_text(encoding="utf-8"))
    dataset = ClaimCheckDataset.from_source_dir(ROOT / config["dataset"]["path"])
    provider = build_embedding_provider(config)
    result = run_e4_baselines(
        dataset,
        embed_document=provider.embed_document,
        embed_query=provider.embed_query,
        embed_many=provider.embed_documents,
    )
    result["protocol"]["embedding"] = config["embedding"]
    output = ROOT / config["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
