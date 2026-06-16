import argparse
import json
from pathlib import Path

import yaml

from evireview.dao.literature import LiteratureCorpus
from evireview.evaluation.literature_rag_runner import (
    LiteratureQuery,
    run_literature_rag_baselines,
)


ROOT = Path(__file__).resolve().parents[1]


def run(config_path: str | Path, *, root: Path = ROOT) -> dict:
    config_path = Path(config_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    corpus = LiteratureCorpus.from_source_dir(root / config["dataset"]["path"])
    queries = _queries_from_config(config, corpus)
    result = run_literature_rag_baselines(
        corpus,
        queries,
        top_k=config.get("top_k", 10),
    )
    output = root / config["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    report = root / config["report"]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(_render_report(result), encoding="utf-8")
    return result


def _queries_from_config(config: dict, corpus: LiteratureCorpus) -> list[LiteratureQuery]:
    queries = []
    for item in config["queries"]:
        gold_doc_ids = [
            corpus.find_by_title_keyword(keyword).doc_id
            for keyword in item["gold_title_keywords"]
        ]
        queries.append(
            LiteratureQuery(
                query_id=item["query_id"],
                query=item["query"],
                aspect=item["aspect"],
                as_of_year=item["as_of_year"],
                gold_doc_ids=gold_doc_ids,
            )
        )
    return queries


def _render_report(result: dict) -> str:
    lines = [
        "# E3 Controlled Literature-RAG Baselines",
        "",
        "## Protocol",
        "",
        "- Frozen local corpus: true",
        "- Online retrieval: false",
        "- Purpose: novelty, related work, and missing-baseline evidence support",
        "",
        "## Dataset",
        "",
        f"- Markdown documents: {result['dataset']['markdown_docs']}",
        f"- Metadata-complete documents: {result['dataset']['metadata_complete_docs']}",
        f"- Year range: {result['dataset']['min_year']}--{result['dataset']['max_year']}",
        "",
        "## Metrics",
        "",
        "| System | Recall@10 | MRR | Literature Relevance@10 | Citation Validity | Future Leakage |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, metrics in result["systems"].items():
        lines.append(
            "| {name} | {recall:.4f} | {mrr:.4f} | {rel:.4f} | {valid:.4f} | {leak} |".format(
                name=name,
                recall=metrics["recall@10"],
                mrr=metrics["mrr"],
                rel=metrics["literature_relevance@10"],
                valid=metrics["citation_validity_rate"],
                leak=metrics["future_leakage_count"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "L0_no_literature is the no-external-evidence baseline. "
            "L3_hybrid_metadata_filter is the controlled Literature-RAG setting used by the proposed system: "
            "it keeps the hybrid ranking signal while enforcing the as-of-year metadata boundary.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="conf/experiments/e3_literature_rag.yaml")
    args = parser.parse_args()
    result = run(ROOT / args.config)
    print(json.dumps({key: value for key, value in result.items() if key != "sample_rankings"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
