from __future__ import annotations

from collections import Counter
from pathlib import Path

from common import (
    DATASET_ROOT,
    DATA_DIR,
    ensure_dirs,
    file_stats,
    load_json,
    read_csv,
    rel_path,
    resolve_repo_path,
    write_csv,
    write_json,
)


def main() -> None:
    ensure_dirs()
    raw_manifest = DATASET_ROOT / "papers_manifest.csv"
    rows = read_csv(raw_manifest)
    clean_rows: list[dict[str, object]] = []
    issues: list[dict[str, str]] = []

    for idx, row in enumerate(rows, start=1):
        md_path = resolve_repo_path(row["mineru_v4_md_path"])
        review_path = resolve_repo_path(row["review_text_path"])
        json_path = resolve_repo_path(row["json_path"])
        pdf_path = resolve_repo_path(row["pdf_path"])

        md_stats = file_stats(md_path)
        review_stats = file_stats(review_path)
        json_stats = file_stats(json_path)

        title_json = ""
        direct_replies_count = ""
        local_json_ok = False
        if json_path.exists():
            try:
                note = load_json(json_path)
                title_json = note.get("content", {}).get("title", {}).get("value", "")
                direct_replies_count = len(note.get("details", {}).get("directReplies", []))
                local_json_ok = True
            except Exception as exc:  # pragma: no cover - audit path
                issues.append({"paper_id": row["paper_id"], "issue": f"json_parse_error: {exc}"})

        required_paths = {
            "markdown": md_path,
            "review_text": review_path,
            "openreview_json": json_path,
        }
        for label, path in required_paths.items():
            if not path.exists():
                issues.append({"paper_id": row["paper_id"], "issue": f"missing_{label}: {path}"})

        if title_json and title_json.strip() != row["title"].strip():
            issues.append({"paper_id": row["paper_id"], "issue": "manifest_title_differs_from_json"})

        clean_rows.append(
            {
                "paper_index": f"{idx:03d}",
                "paper_id": row["paper_id"],
                "forum": row["forum"],
                "title": row["title"],
                "decision": row["decision"],
                "decision_binary": 1 if row["decision"].lower() == "accept" else 0,
                "venue": row["venue"],
                "venueid": row["venueid"],
                "keyword_score": row["keyword_score"],
                "keyword_hits": row["keyword_hits"],
                "review_count_manifest": row["review_count"],
                "metareview_count_manifest": row["metareview_count"],
                "decision_note_count_manifest": row["decision_note_count"],
                "direct_replies_count_json": direct_replies_count,
                "openreview_url": row["openreview_url"],
                "pdf_url": row["pdf_url"],
                "pdf_local_exists": pdf_path.exists(),
                "markdown_path": rel_path(md_path),
                "review_text_path": rel_path(review_path),
                "json_path": rel_path(json_path),
                "markdown_chars": md_stats["chars"],
                "review_text_chars": review_stats["chars"],
                "markdown_sha256": md_stats["sha256"],
                "review_text_sha256": review_stats["sha256"],
                "json_sha256": json_stats["sha256"],
                "local_json_ok": local_json_ok,
            }
        )

    fieldnames = list(clean_rows[0].keys()) if clean_rows else []
    write_csv(DATA_DIR / "manifest_clean.csv", clean_rows, fieldnames)

    decision_counts = Counter(row["decision"] for row in clean_rows)
    audit = {
        "dataset_root": rel_path(DATASET_ROOT),
        "raw_manifest": rel_path(raw_manifest),
        "paper_count": len(clean_rows),
        "decision_counts": dict(decision_counts),
        "markdown_count": sum(1 for row in clean_rows if row["markdown_chars"]),
        "review_text_count": sum(1 for row in clean_rows if row["review_text_chars"]),
        "openreview_json_count": sum(1 for row in clean_rows if row["local_json_ok"]),
        "pdf_local_count": sum(1 for row in clean_rows if row["pdf_local_exists"]),
        "balanced_accept_reject": decision_counts.get("Accept", 0) == decision_counts.get("Reject", 0),
        "issues": issues,
        "source_note": "Local dataset README states the sample was downloaded from the public OpenReview API v2 and converted to Markdown with MinerU v4.",
    }
    write_json(DATA_DIR / "dataset_audit.json", audit)
    print(f"Wrote {DATA_DIR / 'manifest_clean.csv'}")
    print(f"Wrote {DATA_DIR / 'dataset_audit.json'}")
    print(f"papers={len(clean_rows)} decisions={dict(decision_counts)} issues={len(issues)}")


if __name__ == "__main__":
    main()

