from __future__ import annotations

import json
from collections import Counter, defaultdict

from common import DATA_DIR, ensure_dirs, write_json, write_jsonl


TARGET_PAPERS = 30
ITEMS_PER_PAPER = 8
PREFERRED_SECTION = "weaknesses"


def load_jsonl(path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def main() -> None:
    ensure_dirs()
    retrieval_path = DATA_DIR / "retrieval_bm25_top5.jsonl"
    if not retrieval_path.exists():
        raise SystemExit("retrieval_bm25_top5.jsonl missing; run retrieve_bm25.py first")

    items = list(load_jsonl(retrieval_path))
    by_paper = defaultdict(list)
    decision_by_paper = {}
    title_by_paper = {}
    weakness_meta = {}
    for weakness in load_jsonl(DATA_DIR / "human_weaknesses.jsonl"):
        weakness_meta[weakness["weakness_id"]] = weakness
        decision_by_paper[weakness["paper_id"]] = weakness["decision"]
        title_by_paper[weakness["paper_id"]] = weakness["title"]
    for item in items:
        by_paper[item["paper_id"]].append(item)

    accept_papers = sorted([pid for pid, d in decision_by_paper.items() if d == "Accept"])[: TARGET_PAPERS // 2]
    reject_papers = sorted([pid for pid, d in decision_by_paper.items() if d == "Reject"])[: TARGET_PAPERS // 2]
    selected_papers = reject_papers + accept_papers

    candidates = []
    category_counts = Counter()
    for paper_id in selected_papers:
        paper_items = by_paper[paper_id]
        paper_items.sort(
            key=lambda item: (
                item["source_section"] != PREFERRED_SECTION,
                category_counts[item["category_rule"]],
                -len(item["retrieved"]),
                item["weakness_id"],
            )
        )
        selected = paper_items[:ITEMS_PER_PAPER]
        for item in selected:
            meta = weakness_meta[item["weakness_id"]]
            category_counts[item["category_rule"]] += 1
            candidates.append(
                {
                    "annotation_id": f"ann_{len(candidates)+1:04d}",
                    "paper_id": paper_id,
                    "forum": item["forum"],
                    "title": title_by_paper[paper_id],
                    "decision": decision_by_paper[paper_id],
                    "weakness_id": item["weakness_id"],
                    "weakness_text": item["weakness_text"],
                    "category_rule": item["category_rule"],
                    "severity_hint": meta["severity_hint"],
                    "source_section": item["source_section"],
                    "retrieved_evidence_top5": item["retrieved"],
                    "gold_label": "",
                    "gold_evidence_block_ids": "",
                    "annotator_rationale": "",
                    "annotator_confidence": "",
                }
            )

    write_jsonl(DATA_DIR / "annotation_candidates_bm25.jsonl", candidates)
    summary = {
        "target_papers": TARGET_PAPERS,
        "items_per_paper": ITEMS_PER_PAPER,
        "candidate_count": len(candidates),
        "paper_count": len(selected_papers),
        "decision_counts": dict(Counter(item["decision"] for item in candidates)),
        "category_counts": dict(Counter(item["category_rule"] for item in candidates)),
        "label_set": [
            "Supported",
            "Partially Supported",
            "Mentioned but Not Problem",
            "Generic / Vague",
            "Unsupported",
            "Contradicted",
        ],
        "note": "Candidates are BM25-assisted annotation inputs. Empty gold fields are intentionally left for manual labeling.",
    }
    write_json(DATA_DIR / "annotation_candidates_summary.json", summary)
    print(f"Wrote {DATA_DIR / 'annotation_candidates_bm25.jsonl'}")
    print(f"Wrote {DATA_DIR / 'annotation_candidates_summary.json'}")
    print(f"candidates={len(candidates)} papers={len(selected_papers)}")


if __name__ == "__main__":
    main()

