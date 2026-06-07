from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace

from evireview_core.domain.models import EvidenceBlock, VerificationResult, Weakness
from evireview_core.retrieval.bm25 import RetrievedEvidence, bm25_search
from evireview_core.retrieval.hierarchical import hierarchical_search
from evireview_core.verification.heuristic import verify_with_heuristics


QueryPlanner = Callable[[Weakness], str]
Retriever = Callable[[Weakness, str, list[EvidenceBlock], int], list[RetrievedEvidence]]
Verifier = Callable[[Weakness, list[RetrievedEvidence]], VerificationResult]


CATEGORY_TERMS = {
    "experiment": "ablation baseline evaluation result comparison",
    "method": "method algorithm implementation design",
    "related_work": "related work prior comparison novelty",
    "reproducibility": "implementation code hyperparameter reproducibility",
    "limitation": "limitation failure future work",
    "clarity": "definition explanation motivation",
}


def direct_query(weakness: Weakness) -> str:
    return weakness.weakness_text


def category_expansion_query(weakness: Weakness) -> str:
    terms = CATEGORY_TERMS.get(weakness.category, weakness.category.replace("_", " "))
    return f"{weakness.weakness_text} {terms}".strip()


def hierarchical_retriever(
    weakness: Weakness,
    query: str,
    docs: list[EvidenceBlock],
    top_k: int,
) -> list[RetrievedEvidence]:
    return hierarchical_search(replace(weakness, weakness_text=query), docs, top_k=top_k)


def bm25_retriever(
    weakness: Weakness,
    query: str,
    docs: list[EvidenceBlock],
    top_k: int,
) -> list[RetrievedEvidence]:
    return bm25_search(query, [doc for doc in docs if doc.paper_id == weakness.paper_id], top_k=top_k)


@dataclass(frozen=True)
class ComponentRegistry:
    query_planners: dict[str, QueryPlanner]
    retrievers: dict[str, Retriever]
    hosted_retrievers: tuple[str, ...]
    weakness_generators: tuple[str, ...]
    verifiers: dict[str, Verifier]
    hosted_verifiers: tuple[str, ...]

    def query_planner(self, name: str) -> QueryPlanner:
        if name not in self.query_planners:
            raise KeyError(f"query planner not found: {name}")
        return self.query_planners[name]

    def retriever(self, name: str) -> Retriever:
        if name not in self.retrievers:
            raise KeyError(f"retriever not found: {name}")
        return self.retrievers[name]

    def query_planner_names(self) -> tuple[str, ...]:
        return tuple(sorted(self.query_planners))

    def retriever_names(self) -> tuple[str, ...]:
        return tuple(sorted((*self.retrievers, *self.hosted_retrievers)))

    def weakness_generator_names(self) -> tuple[str, ...]:
        return tuple(sorted(self.weakness_generators))

    def verifier(self, name: str) -> Verifier:
        if name not in self.verifiers:
            raise KeyError(f"verifier not found: {name}")
        return self.verifiers[name]

    def verifier_names(self) -> tuple[str, ...]:
        return tuple(sorted((*self.verifiers, *self.hosted_verifiers)))


DEFAULT_COMPONENT_REGISTRY = ComponentRegistry(
    query_planners={
        "direct": direct_query,
        "category_expansion": category_expansion_query,
    },
    retrievers={
        "hierarchical": hierarchical_retriever,
        "bm25": bm25_retriever,
    },
    hosted_retrievers=("qdrant_sparse", "qdrant_hybrid"),
    weakness_generators=("imported", "minimax"),
    verifiers={"heuristic": verify_with_heuristics},
    hosted_verifiers=("minimax",),
)
