from __future__ import annotations

import re
from collections import Counter

from common import (
    DATA_DIR,
    ensure_dirs,
    infer_severity,
    classify_weakness_category,
    normalize_ws,
    read_csv,
    resolve_repo_path,
    split_atomic_items,
    write_json,
    write_jsonl,
)


REVIEW_RE = re.compile(r"^### Review\s+(\d+)\s*$", re.M)
SECTION_RE = re.compile(r"^####\s+(.+?)\s*$", re.M)
CAPTURE_SECTIONS = {"weaknesses", "questions"}


def iter_review_blocks(text: str):
    matches = list(REVIEW_RE.finditer(text))
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        yield match.group(1), text[start:end]


def iter_sections(block: str):
    matches = list(SECTION_RE.finditer(block))
    for i, match in enumerate(matches):
        section = normalize_ws(match.group(1)).lower()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(block)
        yield section, block[start:end].strip()


def main() -> None:
    ensure_dirs()
    manifest_path = DATA_DIR / "manifest_clean.csv"
    if not manifest_path.exists():
        raise SystemExit("manifest_clean.csv missing; run prepare_manifest.py first")

    rows = read_csv(manifest_path)
    weakness_rows: list[dict[str, object]] = []
    extraction_issues: list[dict[str, str]] = []

    for row in rows:
        review_path = resolve_repo_path(row["review_text_path"])
        text = review_path.read_text(encoding="utf-8", errors="ignore")
        paper_items = 0
        for review_number, block in iter_review_blocks(text):
            for section, body in iter_sections(block):
                if section not in CAPTURE_SECTIONS:
                    continue
                for item in split_atomic_items(body):
                    paper_items += 1
                    weakness_id = f"{row['paper_index']}_r{review_number}_{section}_{paper_items:03d}"
                    weakness_rows.append(
                        {
                            "weakness_id": weakness_id,
                            "paper_id": row["paper_id"],
                            "forum": row["forum"],
                            "paper_index": row["paper_index"],
                            "title": row["title"],
                            "decision": row["decision"],
                            "source": "human_review",
                            "review_number": review_number,
                            "source_section": section,
                            "weakness_text": item,
                            "category_rule": classify_weakness_category(item),
                            "severity_hint": infer_severity(item, section),
                            "char_len": len(item),
                        }
                    )
        if paper_items == 0:
            extraction_issues.append({"paper_id": row["paper_id"], "issue": "no_weakness_or_question_items_extracted"})

    out_path = DATA_DIR / "human_weaknesses.jsonl"
    write_jsonl(out_path, weakness_rows)

    counts = Counter(row["decision"] for row in weakness_rows)
    section_counts = Counter(row["source_section"] for row in weakness_rows)
    category_counts = Counter(row["category_rule"] for row in weakness_rows)
    per_paper_counts = Counter(row["paper_id"] for row in weakness_rows)
    summary = {
        "paper_count": len(rows),
        "weakness_item_count": len(weakness_rows),
        "papers_with_extracted_items": len(per_paper_counts),
        "decision_counts": dict(counts),
        "section_counts": dict(section_counts),
        "category_counts": dict(category_counts),
        "min_items_per_paper": min(per_paper_counts.values()) if per_paper_counts else 0,
        "max_items_per_paper": max(per_paper_counts.values()) if per_paper_counts else 0,
        "mean_items_per_paper": round(sum(per_paper_counts.values()) / len(per_paper_counts), 2) if per_paper_counts else 0,
        "extraction_issues": extraction_issues,
        "note": "Rule-based extraction captures reviewer Weaknesses and Questions sections. A later annotation pass should deduplicate and normalize high-priority items.",
    }
    write_json(DATA_DIR / "human_weaknesses_summary.json", summary)
    print(f"Wrote {out_path}")
    print(f"Wrote {DATA_DIR / 'human_weaknesses_summary.json'}")
    print(f"items={len(weakness_rows)} papers={len(per_paper_counts)}/{len(rows)}")


if __name__ == "__main__":
    main()

