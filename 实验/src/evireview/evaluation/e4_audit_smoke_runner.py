from collections import Counter

from evireview.agent.evidence_adjudicator import EvidenceAdjudicator
from evireview.agent.refutation_agent import RefutationAgent
from evireview.agent.support_agent import SupportAgent
from evireview.dao.claimcheck import ClaimCheckDataset, ClaimCheckWeakness
from evireview.evaluation.e4_metrics import macro_f1
from evireview.evaluation.label_mapping import (
    CLAIMCHECK_AGREEMENT_MAPPING_VERSION,
    claimcheck_agreement_to_decision,
)
from evireview.models.audit import AdjudicationResult, AuditCase
from evireview.models.evidence import EvidenceBlock, EvidenceBundle
from evireview.models.weakness import CandidateWeakness
from evireview.rag.bm25 import BM25Retriever


DECISION_LABELS = ["keep", "reject", "uncertain"]


def run_e4_audit_protocol_smoke(dataset: ClaimCheckDataset, *, top_k: int = 5) -> dict:
    examples = [example for example in dataset.examples if example.split == "main"]
    systems = {"A3_heuristic_smoke": [], "A4_heuristic_smoke": []}
    traces = []
    integrity = Counter()

    for example in examples:
        candidate = _candidate(example)
        bundle = _bundle(example, top_k=top_k)
        allowed = {
            item.evidence_id
            for item in bundle.paper_evidence + bundle.literature_evidence
        }
        support = SupportAgent().run(candidate, bundle)
        refutation = RefutationAgent().run(candidate, bundle)
        a3 = EvidenceAdjudicator().decide(
            candidate,
            support,
            _empty_refutation(candidate),
        )
        a4 = EvidenceAdjudicator().decide(candidate, support, refutation)
        gold_proxy = claimcheck_agreement_to_decision(example.agreement)
        systems["A3_heuristic_smoke"].append((a3, gold_proxy))
        systems["A4_heuristic_smoke"].append((a4, gold_proxy))

        cases = [support, refutation]
        integrity["invalid_citations"] += sum(
            len(set(case.evidence_ids) - allowed) for case in cases
        )
        integrity["missing_bidirectional_cases"] += int(
            support.stance != "support" or refutation.stance != "refutation"
        )
        integrity["empty_case_strength_violations"] += sum(
            not case.evidence_ids and case.strength > 0.2 for case in cases
        )
        integrity["human_check_decisions"] += int(
            "human" in a4.decision or "human" in a4.reason.lower()
        )
        traces.append(
            {
                "example_id": example.example_id,
                "candidate": candidate.model_dump(),
                "bundle_evidence_ids": sorted(allowed),
                "gold_agreement_proxy": gold_proxy,
                "support": support.model_dump(),
                "refutation": refutation.model_dump(),
                "A3_heuristic_smoke": a3.model_dump(),
                "A4_heuristic_smoke": a4.model_dump(),
            }
        )

    return {
        "protocol": {
            "name": "e4-audit-protocol-smoke-v1",
            "formal_a0_a4_result": False,
            "provider_backed": False,
            "fixed_bidirectional_execution": True,
            "label_mapping_version": CLAIMCHECK_AGREEMENT_MAPPING_VERSION,
            "label_mapping_is_proxy": True,
            "covered_refuted_gold": False,
            "top_k": top_k,
        },
        "evaluated": len(examples),
        "systems": {
            name: _system_metrics(rows)
            for name, rows in systems.items()
        },
        "integrity": {
            "invalid_citations": integrity["invalid_citations"],
            "missing_bidirectional_cases": integrity["missing_bidirectional_cases"],
            "empty_case_strength_violations": integrity[
                "empty_case_strength_violations"
            ],
            "human_check_decisions": integrity["human_check_decisions"],
        },
        "traces": traces,
    }


def _candidate(example: ClaimCheckWeakness) -> CandidateWeakness:
    weakness_types = example.weakness_types
    aspect = (
        "novelty"
        if "novelty" in weakness_types
        else "related_work"
        if "related_work" in weakness_types
        else "experiment"
    )
    return CandidateWeakness(
        candidate_id=example.example_id,
        paper_id=example.paper_review_id,
        aspect=aspect,
        target=example.target_claims[0] if example.target_claims else "paper claim",
        weakness=example.weakness,
        severity="major" if example.agreement >= 4 else "minor",
        suggestion="Provide evidence that resolves the weakness.",
        source_agent="claimcheck_import",
    )


def _bundle(example: ClaimCheckWeakness, *, top_k: int) -> EvidenceBundle:
    blocks = [
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
    return EvidenceBundle(
        candidate_id=example.example_id,
        paper_evidence=BM25Retriever(blocks).retrieve(example.weakness, top_k),
        literature_evidence=[],
    )


def _empty_refutation(candidate: CandidateWeakness) -> AuditCase:
    return AuditCase(
        candidate_id=candidate.candidate_id,
        stance="refutation",
        claim="No refutation case is used in the support-only smoke baseline.",
        evidence_ids=[],
        strength=0.0,
        rationale="A3 ablates the Refutation Agent.",
    )


def _system_metrics(rows: list[tuple[AdjudicationResult, str]]) -> dict:
    decisions = [result.decision for result, _ in rows]
    gold = [gold_label for _, gold_label in rows]
    correct = sum(
        predicted == expected
        for predicted, expected in zip(decisions, gold, strict=True)
    )
    return {
        "agreement_proxy_accuracy": correct / len(rows) if rows else 0.0,
        "agreement_proxy_macro_f1": macro_f1(gold, decisions, labels=DECISION_LABELS),
        "decision_distribution": dict(Counter(decisions)),
        "cost_per_candidate": 0.0,
    }
