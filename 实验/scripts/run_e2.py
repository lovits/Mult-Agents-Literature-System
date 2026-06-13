import argparse
import json
from pathlib import Path

import yaml

from evireview.dao.peerqa import PeerQADataset
from evireview.evaluation.e2_runner import run_e2
from evireview.rag.embedding import SentenceTransformerEmbedder


ROOT = Path(__file__).resolve().parents[1]


def build_embedding_provider(config: dict) -> SentenceTransformerEmbedder | None:
    embedding = config["embedding"]
    if embedding["name"] == "hashing-smoke":
        return None
    return SentenceTransformerEmbedder(
        model_name=embedding["name"],
        revision=embedding["revision"],
        device=embedding.get("device", "cpu"),
        local_files_only=embedding.get("local_files_only", True),
        query_instruction=embedding["query_instruction"],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="conf/experiments/e2_paper_rag.yaml")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    config = yaml.safe_load((ROOT / args.config).read_text(encoding="utf-8"))
    peerqa_root = ROOT / config["dataset"]["path"]
    dataset = PeerQADataset.from_jsonl(peerqa_root / "papers.jsonl", peerqa_root / "qa.jsonl")
    provider = build_embedding_provider(config)
    embedding_metadata = {
        key: value
        for key, value in config["embedding"].items()
        if key != "name"
    }
    result = run_e2(
        dataset,
        limit=args.limit if args.limit is not None else config["run"]["limit"],
        top_k=config["run"]["top_k"],
        embedding_name=config["embedding"]["name"],
        embedding_metadata=embedding_metadata,
        embed=provider.embed_document if provider else None,
        query_embed=provider.embed_query if provider else None,
        embed_many=provider.embed_documents if provider else None,
    )
    output = ROOT / config["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("protocol", "samples", "failures", "systems")}, indent=2))


if __name__ == "__main__":
    main()
