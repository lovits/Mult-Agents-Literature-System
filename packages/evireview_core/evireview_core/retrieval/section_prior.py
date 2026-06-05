from __future__ import annotations


EXPECTED_SECTIONS_BY_CATEGORY = {
    "related_work": {"related_work", "introduction", "reference"},
    "experiment": {"experiment", "method", "limitation"},
    "method": {"method", "experiment"},
    "reproducibility": {"method", "experiment", "appendix"},
    "clarity": {"introduction", "method", "other"},
    "validity": {"experiment", "method", "limitation"},
    "other": {"abstract", "introduction", "method", "experiment", "other"},
}


def section_alignment(category: str, section_type: str) -> bool:
    expected = EXPECTED_SECTIONS_BY_CATEGORY.get(category, EXPECTED_SECTIONS_BY_CATEGORY["other"])
    return section_type in expected


def section_prior(category: str, section_type: str) -> float:
    if category == section_type:
        return 1.15
    if section_alignment(category, section_type):
        return 0.85
    if section_type in {"reference", "appendix"}:
        return 0.15
    return 0.0
