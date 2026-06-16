import re


GENERATOR_NAME = "system_deterministic_baseline_v1"
CUE_AWARE_GENERATOR_NAME = "system_cue_aware_baseline_v2"


def generate_candidate_weaknesses(submission: dict, *, max_candidates: int = 6) -> list[dict]:
    paper_id = submission["paper_id"]
    content = submission.get("content", {})
    abstract = _clean(content.get("abstract", ""))
    title = _clean(content.get("title", paper_id))
    keywords = [_clean(str(item)) for item in content.get("keywords", []) if str(item).strip()]
    primary_area = _clean(content.get("primary_area", ""))
    target = _target(title, keywords, primary_area)
    evidence_ids = _content_evidence_ids(paper_id, content)
    candidates = [
        _candidate(
            paper_id,
            0,
            "experiment",
            target,
            "The empirical evaluation may need stronger ablation analysis to isolate which component drives the reported gains.",
            "major",
            "Add component-level ablations and report how each removed module changes the main metric.",
            evidence_ids,
            abstract,
        ),
        _candidate(
            paper_id,
            1,
            "missing_baseline",
            target,
            "The baseline comparison may be incomplete or insufficiently justified for the claimed contribution.",
            "major",
            "Compare against the closest recent baselines and explain why each baseline is appropriate.",
            evidence_ids,
            abstract,
        ),
        _candidate(
            paper_id,
            2,
            "reproducibility",
            target,
            "The implementation and reproduction details may not be specific enough for independent verification.",
            "major",
            "Provide implementation settings, hyperparameters, compute budget, data preprocessing, and release artifacts.",
            evidence_ids,
            abstract,
        ),
        _candidate(
            paper_id,
            3,
            "method",
            target,
            "The method description may leave key assumptions or algorithmic choices underspecified.",
            "minor",
            "Clarify the core assumptions, decision rules, and failure cases of the proposed method.",
            evidence_ids,
            abstract,
        ),
        _candidate(
            paper_id,
            4,
            "related_work",
            target,
            "The related work discussion may need a sharper comparison with closely related approaches.",
            "minor",
            "Separate conceptual novelty from engineering differences and cite directly competing methods.",
            evidence_ids,
            abstract,
        ),
        _candidate(
            paper_id,
            5,
            "novelty",
            target,
            "The novelty claim may need clearer positioning against existing work in the same problem setting.",
            "minor",
            "State the exact technical delta over prior work and map it to the evidence in the experiments.",
            evidence_ids,
            abstract,
        ),
    ]
    ranked = sorted(candidates, key=lambda item: (-item["rank_score"], item["candidate_id"]))
    return ranked[:max_candidates]


def generate_cue_aware_candidate_weaknesses(
    submission: dict,
    *,
    max_candidates: int = 6,
) -> list[dict]:
    paper_id = submission["paper_id"]
    content = submission.get("content", {})
    abstract = _clean(content.get("abstract", ""))
    title = _clean(content.get("title", paper_id))
    keywords = [_clean(str(item)) for item in content.get("keywords", []) if str(item).strip()]
    primary_area = _clean(content.get("primary_area", ""))
    context = " ".join([title, abstract, " ".join(keywords), primary_area]).lower()
    target = _target(title, keywords, primary_area)
    evidence_ids = _content_evidence_ids(paper_id, content)
    candidates = [
        _cue_candidate(
            paper_id,
            0,
            "experiment",
            target,
            "The empirical evaluation may need stronger ablation analysis and direct validation of the claimed mechanism.",
            "major",
            "Add component ablations and targeted validation experiments tied to the main claim.",
            evidence_ids,
            abstract,
            context,
            {"experiment", "evaluation", "ablation", "study", "benchmark", "results"},
        ),
        _cue_candidate(
            paper_id,
            1,
            "missing_baseline",
            target,
            "The baseline comparison may be incomplete, especially against closely related recent or task-specific methods.",
            "major",
            "Compare with the closest task-specific baselines and justify omissions explicitly.",
            evidence_ids,
            abstract,
            context,
            {"baseline", "compare", "comparison", "benchmark", "state-of-the-art"},
        ),
        _cue_candidate(
            paper_id,
            2,
            "reproducibility",
            target,
            "The implementation, dataset, hyperparameter, and compute details may not be sufficient for reproduction.",
            "major",
            "Report code, data processing, hyperparameters, random seeds, and compute budget.",
            evidence_ids,
            abstract,
            context,
            {"implementation", "code", "dataset", "hyperparameter", "training", "compute"},
        ),
        _cue_candidate(
            paper_id,
            3,
            "method",
            target,
            "The method may rely on strong assumptions or underspecified algorithmic choices that need clearer justification.",
            "major",
            "State the assumptions, algorithmic choices, and failure cases, then test sensitivity to them.",
            evidence_ids,
            abstract,
            context,
            {"assumption", "assumptions", "method", "algorithm", "framework", "system", "identification"},
        ),
        _cue_candidate(
            paper_id,
            4,
            "related_work",
            target,
            "The related work comparison may need a sharper discussion of overlapping prior approaches.",
            "minor",
            "Separate conceptual novelty from engineering differences and cite directly competing methods.",
            evidence_ids,
            abstract,
            context,
            {"related", "prior", "existing", "literature", "contrastive", "tool", "agent"},
        ),
        _cue_candidate(
            paper_id,
            5,
            "novelty",
            target,
            "The novelty claim may need clearer positioning against existing work in the same problem setting.",
            "minor",
            "State the exact technical delta over prior work and map it to experimental evidence.",
            evidence_ids,
            abstract,
            context,
            {"novel", "new", "first", "introduce", "propose", "benchmark"},
        ),
    ]
    candidates.extend(_domain_cue_candidates(paper_id, target, evidence_ids, abstract, context))
    ranked = sorted(candidates, key=lambda item: (-item["rank_score"], item["candidate_id"]))
    return _diversified_top_k(ranked, max_candidates)


def _candidate(
    paper_id: str,
    index: int,
    aspect: str,
    target: str,
    weakness: str,
    severity: str,
    suggestion: str,
    evidence_ids: list[str],
    abstract: str,
) -> dict:
    return {
        "candidate_id": f"{paper_id}:system:{index}",
        "paper_id": paper_id,
        "aspect": aspect,
        "target": target,
        "weakness": weakness,
        "severity": severity,
        "suggestion": suggestion,
        "source_agent": GENERATOR_NAME,
        "evidence_ids": evidence_ids,
        "confidence": _confidence(aspect, abstract),
        "rank_score": _rank_score(aspect, severity, abstract),
        "source_review_id": None,
    }


def _cue_candidate(
    paper_id: str,
    index: int,
    aspect: str,
    target: str,
    weakness: str,
    severity: str,
    suggestion: str,
    evidence_ids: list[str],
    abstract: str,
    context: str,
    cue_terms: set[str],
) -> dict:
    item = _candidate(
        paper_id,
        index,
        aspect,
        target,
        weakness,
        severity,
        suggestion,
        evidence_ids,
        abstract,
    )
    item["candidate_id"] = f"{paper_id}:cue:{index}"
    item["source_agent"] = CUE_AWARE_GENERATOR_NAME
    item["rank_score"] = round(
        item["rank_score"] + min(_cue_match_count(context, cue_terms), 4) * 0.16,
        6,
    )
    item["confidence"] = round(min(item["confidence"] + min(_cue_match_count(context, cue_terms), 3) * 0.08, 0.88), 6)
    return item


def _domain_cue_candidates(
    paper_id: str,
    target: str,
    evidence_ids: list[str],
    abstract: str,
    context: str,
) -> list[dict]:
    templates = [
        (
            {"judge", "judgment", "annotation", "annotator", "benchmark"},
            "experiment",
            "The benchmark evaluation may need stronger human annotation details and validation of automatic judge reliability.",
            "Report annotator expertise, agreement, adjudication rules, and compare automatic judges against human judgment.",
        ),
        (
            {"system", "identification", "dynamics", "latent", "control"},
            "method",
            "The method may depend on strong observability, control-input, or system-identification assumptions.",
            "Clarify the assumptions and test cases where partial observability or control noise breaks the method.",
        ),
        (
            {"interpretability", "autoencoder", "sae", "sparse", "concept"},
            "experiment",
            "The interpretability claims may need larger quantitative validation beyond qualitative examples.",
            "Add quantitative reliability tests, feature stability checks, and comparisons to existing interpretability methods.",
        ),
        (
            {"physics", "inverse", "pde", "experimental", "design"},
            "missing_baseline",
            "The experimental design method may need comparison with existing neural or physics-informed design baselines.",
            "Compare with established experiment-design and neural inverse-problem baselines under the same budget.",
        ),
        (
            {"agent", "tool", "calling", "retrieval", "generalization"},
            "experiment",
            "The agent or tool-use evaluation may need broader task coverage and stronger out-of-distribution testing.",
            "Evaluate on diverse tasks, unseen tools, and ablate retrieval, refinement, or tool-selection components.",
        ),
        (
            {"tabular", "ensemble", "mlp", "parameter-efficient"},
            "missing_baseline",
            "The tabular learning comparison may need stronger baselines and dataset coverage.",
            "Compare against tuned tree, transformer, retrieval, and ensemble baselines across varied tabular datasets.",
        ),
        (
            {"backdoor", "poisoned", "attack", "trigger", "defense"},
            "experiment",
            "The backdoor-defense evaluation may need broader attacks, triggers, and adaptive threat models.",
            "Test multiple trigger types, poisoning ratios, adaptive attacks, and clean-accuracy tradeoffs.",
        ),
    ]
    candidates = []
    for offset, (cues, aspect, weakness, suggestion) in enumerate(templates, start=20):
        matches = _cue_match_count(context, cues)
        if matches == 0:
            continue
        candidates.append(
            _cue_candidate(
                paper_id,
                offset,
                aspect,
                target,
                weakness,
                "major",
                suggestion,
                evidence_ids,
                abstract,
                context,
                cues,
            )
        )
    return candidates


def _diversified_top_k(candidates: list[dict], limit: int) -> list[dict]:
    selected = []
    used_aspects = set()
    for candidate in candidates:
        if candidate["aspect"] in used_aspects and len(selected) < min(limit, 3):
            continue
        selected.append(candidate)
        used_aspects.add(candidate["aspect"])
        if len(selected) == limit:
            return selected
    for candidate in candidates:
        if candidate not in selected:
            selected.append(candidate)
        if len(selected) == limit:
            return selected
    return selected


def _cue_match_count(context: str, cue_terms: set[str]) -> int:
    return sum(term in context for term in cue_terms)


def _rank_score(aspect: str, severity: str, abstract: str) -> float:
    score = 0.35 if severity == "major" else 0.18
    tokens = set(_tokens(abstract))
    aspect_terms = {
        "experiment": {"experiment", "evaluation", "ablation", "study", "results"},
        "missing_baseline": {"baseline", "compare", "comparison", "state-of-the-art"},
        "reproducibility": {"code", "implementation", "hyperparameter", "reproducibility"},
        "method": {"method", "model", "algorithm", "framework", "approach"},
        "related_work": {"related", "prior", "existing", "literature"},
        "novelty": {"novel", "new", "first", "propose"},
    }
    matched = len(tokens & aspect_terms.get(aspect, set()))
    score += min(matched, 3) * 0.12
    if aspect in {"experiment", "missing_baseline", "reproducibility"}:
        score += 0.1
    return round(score, 6)


def _confidence(aspect: str, abstract: str) -> float:
    tokens = set(_tokens(abstract))
    if not tokens:
        return 0.25
    cue_terms = {
        "experiment": {"experiment", "evaluation", "result", "ablation"},
        "missing_baseline": {"baseline", "compare", "comparison"},
        "reproducibility": {"implementation", "code", "dataset", "hyperparameter"},
        "method": {"method", "model", "algorithm", "framework"},
        "related_work": {"related", "prior", "existing"},
        "novelty": {"novel", "new", "propose"},
    }
    matched = len(tokens & cue_terms.get(aspect, set()))
    return round(min(0.35 + 0.15 * matched, 0.8), 6)


def _content_evidence_ids(paper_id: str, content: dict) -> list[str]:
    ids = []
    for field in ("title", "abstract", "keywords", "primary_area"):
        value = content.get(field)
        if value:
            ids.append(f"{paper_id}:content:{field}")
    return ids or [f"{paper_id}:content:metadata"]


def _target(title: str, keywords: list[str], primary_area: str) -> str:
    if keywords:
        return ", ".join(keywords[:3])
    if primary_area:
        return primary_area
    return title


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)?", text.lower())


def _clean(text: str) -> str:
    return " ".join(str(text).split())
