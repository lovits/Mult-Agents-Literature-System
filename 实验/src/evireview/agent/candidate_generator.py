import re


GENERATOR_NAME = "system_deterministic_baseline_v1"


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
