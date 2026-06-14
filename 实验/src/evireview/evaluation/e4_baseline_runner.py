from collections import Counter
from collections.abc import Callable, Sequence
from statistics import median

from evireview.dao.claimcheck import ClaimCheckDataset, ClaimCheckWeakness
from evireview.evaluation.e4_metrics import mean_absolute_error, multilabel_macro_f1
from evireview.evaluation.retrieval_metrics import evaluate_ranking
from evireview.models.evidence import EvidenceBlock
from evireview.rag.bm25 import BM25Retriever
from evireview.rag.dense import DenseRetriever
from evireview.rag.fusion import reciprocal_rank_fusion


WEAKNESS_TYPES = [
    "clarity",
    "contradictory",
    "insufficient",
    "novelty",
    "other",
    "related_work",
]


def run_e4_baselines(
    dataset: ClaimCheckDataset,
    *,
    embed_document: Callable[[str], list[float]] | None = None,
    embed_query: Callable[[str], list[float]] | None = None,
    embed_many: Callable[[Sequence[str]], list[list[float]]] | None = None,
) -> dict:
    development = [example for example in dataset.examples if example.split == "pilot"]
    evaluation = [example for example in dataset.examples if example.split == "main"]
    association_examples = [example for example in evaluation if example.relevant_text_ids]
    excluded = Counter(
        example.exclusion_reason
        for example in evaluation
        if not example.relevant_text_ids and example.exclusion_reason
    )
    association_systems, sample_results = _run_association(
        association_examples,
        embed_document=embed_document,
        embed_query=embed_query,
        embed_many=embed_many,
    )
    return {
        "protocol": {
            "development_split": "pilot",
            "evaluation_split": "main",
            "gold_used_only_for_evaluation": True,
            "covered_refuted_gold": False,
        },
        "association": {
            "evaluated": len(association_examples),
            "excluded_with_reason": dict(excluded),
            "excluded_examples": [
                {"example_id": example.example_id, "reason": example.exclusion_reason}
                for example in evaluation
                if not example.relevant_text_ids
            ],
            "systems": association_systems,
            "sample_results": sample_results,
        },
        "labeling": {
            "evaluated": len(evaluation),
            "W0_pilot_prior": _pilot_prior(development, evaluation),
        },
    }


def _run_association(
    examples: list[ClaimCheckWeakness],
    *,
    embed_document: Callable[[str], list[float]] | None,
    embed_query: Callable[[str], list[float]] | None,
    embed_many: Callable[[Sequence[str]], list[list[float]]] | None,
) -> tuple[dict, list[dict]]:
    rows: dict[str, list[dict[str, float]]] = {"C0_position": [], "C1_bm25": []}
    sample_results = []
    if embed_document is not None:
        rows["C2_dense"] = []
        rows["C3_hybrid"] = []
    for example in examples:
        blocks = _blocks(example)
        rankings = {
            "C0_position": [block.block_id for block in blocks],
            "C1_bm25": [
                item.evidence_id
                for item in BM25Retriever(blocks).retrieve(example.weakness, len(blocks))
            ],
        }
        if embed_document is not None:
            rankings["C2_dense"] = [
                item.evidence_id
                for item in DenseRetriever(
                    blocks,
                    embed_document,
                    query_embed=embed_query,
                    embed_many=embed_many,
                ).retrieve(example.weakness, len(blocks))
            ]
            rankings["C3_hybrid"] = [
                item.item_id
                for item in reciprocal_rank_fusion(
                    [rankings["C1_bm25"], rankings["C2_dense"]]
                )
            ]
        for name, ranking in rankings.items():
            rows[name].append(
                evaluate_ranking(ranking, example.relevant_text_ids, cutoffs=(1, 3, 5))
            )
        sample_results.append(
            {
                "example_id": example.example_id,
                "gold_ids": sorted(example.relevant_text_ids),
                "rankings": rankings,
            }
        )
    return (
        {name: _mean_metrics(metrics) for name, metrics in rows.items()},
        sample_results,
    )


def _pilot_prior(
    development: list[ClaimCheckWeakness],
    evaluation: list[ClaimCheckWeakness],
) -> dict[str, float | int | list[str]]:
    if not development or not evaluation:
        return {"available": False, "cost_per_candidate": 0.0}
    groundedness = int(median(example.groundedness_confidence for example in development))
    agreement = int(median(example.agreement for example in development))
    subjectivity = int(median(example.subjectivity for example in development))
    type_counts = Counter(
        weakness_type
        for example in development
        for weakness_type in example.weakness_types
    )
    predicted_types = {sorted(type_counts, key=lambda name: (-type_counts[name], name))[0]}
    return {
        "available": True,
        "pilot_groundedness_median": groundedness,
        "pilot_agreement_median": agreement,
        "pilot_subjectivity_median": subjectivity,
        "predicted_types": sorted(predicted_types),
        "groundedness_mae": mean_absolute_error(
            [example.groundedness_confidence for example in evaluation],
            [groundedness] * len(evaluation),
        ),
        "agreement_mae": mean_absolute_error(
            [example.agreement for example in evaluation],
            [agreement] * len(evaluation),
        ),
        "subjectivity_mae": mean_absolute_error(
            [example.subjectivity for example in evaluation],
            [subjectivity] * len(evaluation),
        ),
        "weakness_type_macro_f1": multilabel_macro_f1(
            [example.weakness_types for example in evaluation],
            [predicted_types] * len(evaluation),
            labels=WEAKNESS_TYPES,
        ),
        "cost_per_candidate": 0.0,
    }


def _blocks(example: ClaimCheckWeakness) -> list[EvidenceBlock]:
    return [
        EvidenceBlock(
            block_id=f"{example.paper_review_id}:{index}",
            paper_id=example.paper_review_id,
            section="paper_text",
            evidence_type="paragraph",
            text=text,
            ordinal=index,
        )
        for index, text in enumerate(example.paper_texts)
    ]


def _mean_metrics(rows: list[dict[str, float]]) -> dict[str, float]:
    if not rows:
        return {}
    return {
        metric: sum(row[metric] for row in rows) / len(rows)
        for metric in rows[0]
    }
