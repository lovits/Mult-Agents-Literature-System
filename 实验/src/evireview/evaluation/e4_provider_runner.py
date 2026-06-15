from collections import Counter
from typing import Any

from evireview.agent.provider import ProviderHTTPError, ProviderResult
from evireview.dao.claimcheck import ClaimCheckDataset
from evireview.evaluation.e4_audit_smoke_runner import (
    DECISION_LABELS,
    _bundle,
    _candidate,
)
from evireview.evaluation.e4_metrics import macro_f1
from evireview.evaluation.label_mapping import (
    CLAIMCHECK_AGREEMENT_MAPPING_VERSION,
    claimcheck_agreement_to_decision,
)
from evireview.models.audit import AdjudicationResult, AuditCase


SYSTEMS = ["A0", "A1", "A2", "A3", "A4"]
AUDIT_PROFILES = {
    "standard_v1": {
        "support_role": "support",
        "refutation_role": "refutation",
        "adjudicator_role": "adjudicate",
        "compact_adjudicator_evidence": False,
    },
    "bounded_v2": {
        "support_role": "support_strict",
        "refutation_role": "refutation_strict",
        "adjudicator_role": "adjudicate_compact",
        "compact_adjudicator_evidence": True,
    },
}


def run_e4_provider_experiment(
    dataset: ClaimCheckDataset,
    provider: Any,
    *,
    limit: int | None = None,
    top_k: int = 5,
    selection: str = "head",
    audit_profile: str = "standard_v1",
) -> dict:
    if audit_profile not in AUDIT_PROFILES:
        raise ValueError(f"unknown audit profile: {audit_profile}")
    profile = AUDIT_PROFILES[audit_profile]
    examples = [example for example in dataset.examples if example.split == "main"]
    examples = _select_examples(examples, limit=limit, selection=selection)
    rows = {name: [] for name in SYSTEMS}
    costs = {name: Counter() for name in SYSTEMS}
    traces = []
    integrity = Counter()

    for example in examples:
        candidate = _candidate(example)
        bundle = _bundle(example, top_k=top_k)
        evidence = [item.model_dump() for item in bundle.paper_evidence]
        allowed = {item["evidence_id"] for item in evidence}
        base = {"candidate": candidate.model_dump()}
        gold = claimcheck_agreement_to_decision(example.agreement)
        trace = {"example_id": example.example_id, "gold_agreement_proxy": gold}
        a0 = _decision(candidate.candidate_id, {"decision": "keep", "confidence": 0.0})
        rows["A0"].append((a0, gold))
        trace["A0"] = a0.model_dump()

        for name, role, payload in [
            ("A1", "judge_no_evidence", base),
            ("A2", "judge_with_evidence", {**base, "evidence": evidence}),
        ]:
            decision, result = _provider_decision(
                provider, role, payload, candidate.candidate_id, allowed, integrity
            )
            _add_cost(costs[name], result)
            rows[name].append((decision, gold))
            trace[name] = decision.model_dump()

        support, support_result = _provider_case(
            provider,
            profile["support_role"],
            {**base, "evidence": evidence},
            candidate.candidate_id,
            "support",
            allowed,
            integrity,
        )
        a3_evidence = _adjudicator_evidence(
            evidence,
            cases=[support],
            compact=profile["compact_adjudicator_evidence"],
        )
        a3, a3_result = _provider_decision(
            provider,
            profile["adjudicator_role"],
            {
                **base,
                "evidence": a3_evidence,
                "support": support.model_dump(),
                "refutation": None,
            },
            candidate.candidate_id,
            {item["evidence_id"] for item in a3_evidence},
            integrity,
        )
        _add_cost(costs["A3"], support_result)
        _add_cost(costs["A3"], a3_result)
        rows["A3"].append((a3, gold))
        trace["A3"] = {"support": support.model_dump(), "decision": a3.model_dump()}

        refutation, refutation_result = _provider_case(
            provider,
            profile["refutation_role"],
            {**base, "evidence": evidence},
            candidate.candidate_id,
            "refutation",
            allowed,
            integrity,
        )
        a4_evidence = _adjudicator_evidence(
            evidence,
            cases=[support, refutation],
            compact=profile["compact_adjudicator_evidence"],
        )
        a4, a4_result = _provider_decision(
            provider,
            profile["adjudicator_role"],
            {
                **base,
                "evidence": a4_evidence,
                "support": support.model_dump(),
                "refutation": refutation.model_dump(),
            },
            candidate.candidate_id,
            {item["evidence_id"] for item in a4_evidence},
            integrity,
        )
        for result in [support_result, refutation_result, a4_result]:
            _add_cost(costs["A4"], result)
        rows["A4"].append((a4, gold))
        trace["A4"] = {
            "support": support.model_dump(),
            "refutation": refutation.model_dump(),
            "decision": a4.model_dump(),
        }
        traces.append(trace)

    return {
        "protocol": {
            "name": "e4-provider-a0-a4-v1",
            "provider_backed": True,
            "model": provider.model,
            "label_mapping_version": CLAIMCHECK_AGREEMENT_MAPPING_VERSION,
            "label_mapping_is_proxy": True,
            "covered_refuted_gold": False,
            "top_k": top_k,
            "limit": limit,
            "selection": selection,
            "audit_profile": audit_profile,
        },
        "evaluated": len(examples),
        "systems": {
            name: _metrics(rows[name], costs[name], len(examples)) for name in SYSTEMS
        },
        "integrity": {
            "invalid_citations": integrity["invalid_citations"],
            "cited_evidence_ids": integrity["cited_evidence_ids"],
            "evidence_attribution_accuracy": (
                1
                - integrity["invalid_citations"] / integrity["cited_evidence_ids"]
                if integrity["cited_evidence_ids"]
                else 1.0
            ),
            "failures": integrity["failures"],
            "failure_reasons": {
                key.removeprefix("failure_reason:"): value
                for key, value in integrity.items()
                if key.startswith("failure_reason:")
            },
        },
        "traces": traces,
    }


def _adjudicator_evidence(evidence, *, cases, compact: bool):
    if not compact:
        return evidence
    cited = {evidence_id for case in cases for evidence_id in case.evidence_ids}
    return [item for item in evidence if item["evidence_id"] in cited]


def _select_examples(examples, *, limit: int | None, selection: str):
    if limit is None:
        return examples
    if selection == "head":
        return examples[:limit]
    if selection != "stratified_proxy":
        raise ValueError(f"unknown selection strategy: {selection}")
    groups = {
        label: [
            example
            for example in examples
            if claimcheck_agreement_to_decision(example.agreement) == label
        ]
        for label in DECISION_LABELS
    }
    selected = []
    while len(selected) < limit and any(groups.values()):
        for label in DECISION_LABELS:
            if groups[label] and len(selected) < limit:
                selected.append(groups[label].pop(0))
    return selected


def _provider_case(provider, role, payload, candidate_id, stance, allowed, integrity):
    try:
        result = provider.complete_json(role, payload)
        raw_citations = result.data.get("evidence_ids", [])
        cited = [item for item in raw_citations if item in allowed]
        integrity["cited_evidence_ids"] += len(raw_citations)
        integrity["invalid_citations"] += len(raw_citations) - len(cited)
        case = AuditCase(
            candidate_id=candidate_id,
            stance=stance,
            claim=str(result.data.get("claim", f"{stance} case")),
            evidence_ids=cited,
            strength=min(float(result.data.get("strength", 0.0)), 0.2) if not cited
            else float(result.data.get("strength", 0.0)),
            rationale=str(result.data.get("rationale", "")),
        )
        return case, result
    except Exception as error:
        _record_failure(integrity, error)
        return AuditCase(
            candidate_id=candidate_id,
            stance=stance,
            claim=f"{stance} provider failure",
            evidence_ids=[],
            strength=0.0,
            rationale="Provider call or structured parsing failed.",
        ), None


def _provider_decision(provider, role, payload, candidate_id, allowed, integrity):
    try:
        result = provider.complete_json(role, payload)
        raw_citations = result.data.get("evidence_ids", [])
        cited = [item for item in raw_citations if item in allowed]
        integrity["cited_evidence_ids"] += len(raw_citations)
        integrity["invalid_citations"] += len(raw_citations) - len(cited)
        return _decision(candidate_id, {**result.data, "evidence_ids": cited}), result
    except Exception as error:
        _record_failure(integrity, error)
        return _decision(candidate_id, {
            "decision": "uncertain",
            "confidence": 0.0,
            "reason": "Provider call or structured parsing failed.",
        }), None


def _decision(candidate_id: str, data: dict) -> AdjudicationResult:
    decision = data.get("decision", "uncertain")
    if decision not in {"keep", "rewrite", "reject", "uncertain"}:
        decision = "uncertain"
    return AdjudicationResult(
        candidate_id=candidate_id,
        decision=decision,
        confidence=max(0.0, min(float(data.get("confidence", 0.0)), 1.0)),
        evidence_ids=data.get("evidence_ids", []),
        reason=str(data.get("reason", "")),
        rewritten_weakness=data.get("rewritten_weakness"),
    )


def _add_cost(counter: Counter, result: ProviderResult | None) -> None:
    if result is None:
        return
    counter["calls"] += 1
    counter["latency_ms"] += result.latency_ms
    counter["tokens"] += result.usage.get("total_tokens", 0)


def _record_failure(integrity: Counter, error: Exception) -> None:
    integrity["failures"] += 1
    reason = (
        f"http_{error.status_code}"
        if isinstance(error, ProviderHTTPError)
        else error.__class__.__name__
    )
    integrity[f"failure_reason:{reason}"] += 1


def _metrics(rows, costs: Counter, count: int) -> dict:
    gold = [gold for _, gold in rows]
    predicted = [result.decision for result, _ in rows]
    correct = sum(left == right for left, right in zip(gold, predicted, strict=True))
    return {
        "agreement_proxy_accuracy": correct / len(rows) if rows else 0.0,
        "agreement_proxy_macro_f1": macro_f1(gold, predicted, labels=DECISION_LABELS),
        "decision_distribution": dict(Counter(predicted)),
        "calls_per_candidate": costs["calls"] / count if count else 0.0,
        "tokens_per_candidate": costs["tokens"] / count if count else 0.0,
        "latency_ms_per_candidate": costs["latency_ms"] / count if count else 0.0,
    }
