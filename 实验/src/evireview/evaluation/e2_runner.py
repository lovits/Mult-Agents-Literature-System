import hashlib
import re
import time
from collections.abc import Callable, Sequence

from evireview.dao.peerqa import PeerQADataset, PeerQAExample
from evireview.evaluation.retrieval_metrics import evaluate_ranking
from evireview.models.evidence import EvidenceBlock
from evireview.models.weakness import QueryPlan
from evireview.rag.bm25 import BM25Retriever, tokenize
from evireview.rag.dense import DenseRetriever
from evireview.rag.paper_rag import PaperRAG, PaperRAGConfig


SYSTEMS = ("P0", "P1", "P2", "P3", "P4")


def hashing_embed(text: str, dimensions: int = 256) -> list[float]:
    vector = [0.0] * dimensions
    for token in tokenize(text):
        digest = hashlib.blake2b(token.encode(), digest_size=8).digest()
        index = int.from_bytes(digest, "big") % dimensions
        vector[index] += 1.0
    return vector


def run_e2(
    dataset: PeerQADataset,
    *,
    limit: int | None,
    top_k: int,
    embedding_name: str,
    embedding_metadata: dict | None = None,
    embed: Callable[[str], list[float]] | None = None,
    query_embed: Callable[[str], list[float]] | None = None,
    embed_many: Callable[[Sequence[str]], list[list[float]]] | None = None,
) -> dict:
    if embed is None:
        if embedding_name != "hashing-smoke":
            raise ValueError("formal embedding requires an explicit embed callable")
        embed = hashing_embed

    examples = dataset.examples[:limit] if limit is not None else dataset.examples
    sample_results = []
    failures = []
    for example in examples:
        try:
            sample_results.append(
                _run_example(dataset, example, top_k, embed, query_embed, embed_many)
            )
        except Exception as error:
            failures.append({"question_id": example.question_id, "error": str(error)})
    return {
        "protocol": {
            "embedding": embedding_name,
            "embedding_metadata": embedding_metadata or {},
            "formal_result": embedding_name != "hashing-smoke",
            "gold_used_only_for_evaluation": True,
            "latency_scope": "retrieval_after_query_embedding_warmup",
            "systems": list(SYSTEMS),
        },
        "samples": len(sample_results),
        "failures": failures,
        "systems": _aggregate(sample_results),
        "sample_results": sample_results,
    }


def _run_example(
    dataset: PeerQADataset,
    example: PeerQAExample,
    top_k: int,
    embed: Callable[[str], list[float]],
    query_embed: Callable[[str], list[float]] | None,
    embed_many: Callable[[Sequence[str]], list[list[float]]] | None,
) -> dict:
    blocks = dataset.blocks_by_paper[example.paper_id]
    plan = _plan_question(example)
    bm25 = BM25Retriever(blocks)
    dense = DenseRetriever(blocks, embed, query_embed=query_embed, embed_many=embed_many)
    rag = PaperRAG(blocks, embed, query_embed=query_embed, embed_many=embed_many)
    if query_embed is not None:
        query_embed(example.question)
    retrievers = {
        "P0": lambda: bm25.retrieve(example.question, top_k),
        "P1": lambda: dense.retrieve(example.question, top_k),
        "P2": lambda: rag.retrieve(plan, PaperRAGConfig(mode="P2", top_k=top_k)).items,
        "P3": lambda: rag.retrieve(plan, PaperRAGConfig(mode="P3", top_k=top_k)).items,
        "P4": lambda: rag.retrieve(plan, PaperRAGConfig(mode="P4", top_k=top_k)).items,
    }
    block_by_id = {block.block_id: block for block in blocks}
    systems = {}
    for name, retrieve in retrievers.items():
        started = time.perf_counter()
        items = retrieve()
        latency_ms = (time.perf_counter() - started) * 1_000
        ranked_ids = [item.evidence_id for item in items]
        metrics = evaluate_ranking(ranked_ids, example.relevant_evidence_ids, cutoffs=(1, 3, 5))
        metrics["evidence_type_match@5"] = _evidence_type_match(
            ranked_ids, example.relevant_evidence_ids, block_by_id
        )
        metrics["latency_ms"] = latency_ms
        systems[name] = metrics
    return {"question_id": example.question_id, "paper_id": example.paper_id, "systems": systems}


def _plan_question(example: PeerQAExample) -> QueryPlan:
    question = example.question.lower()
    expected_sections = []
    expected_types = []
    if re.search(
        r"\b(result|score|compare|comparison|ablation|experiment|evaluation|benchmark|performance)\b",
        question,
    ):
        expected_sections = ["Experiments", "Results", "Ablation", "Appendix"]
    if re.search(r"\b(table|result|score)\b", question):
        expected_types.append("table_caption")
    if re.search(r"\b(figure|plot|graph)\b", question):
        expected_types.append("figure_caption")
    if re.search(r"\b(method|algorithm|procedure)\b", question):
        expected_sections = ["Method", "Methods", "Algorithm", "Appendix"]
    if re.search(r"\b(algorithm|procedure|pseudocode)\b", question):
        expected_types.append("algorithm")
    return QueryPlan(
        candidate_id=example.question_id,
        aspect="experiment",
        keyword_queries=[example.question],
        semantic_query=example.question,
        expected_sections=expected_sections,
        expected_evidence_types=expected_types,
        literature_required=False,
    )


def _evidence_type_match(
    ranked_ids: list[str],
    relevant_ids: set[str],
    block_by_id: dict[str, EvidenceBlock],
) -> float:
    gold_types = {block_by_id[item_id].evidence_type for item_id in relevant_ids}
    if not ranked_ids:
        return 0.0
    matches = sum(block_by_id[item_id].evidence_type in gold_types for item_id in ranked_ids[:5])
    return matches / min(len(ranked_ids), 5)


def _aggregate(sample_results: list[dict]) -> dict[str, dict[str, float]]:
    if not sample_results:
        return {name: {} for name in SYSTEMS}
    systems = {}
    for name in SYSTEMS:
        rows = [sample["systems"][name] for sample in sample_results]
        systems[name] = {
            metric: sum(row[metric] for row in rows) / len(rows)
            for metric in rows[0]
        }
    return systems
