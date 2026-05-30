from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from common import DATA_DIR, REPORT_DIR, ensure_dirs, load_json, read_csv, resolve_repo_path, write_json


API_BASE = "https://api2.openreview.net/notes"


def fetch_note(forum_id: str) -> dict:
    query = urllib.parse.urlencode({"id": forum_id, "details": "directReplies"})
    with urllib.request.urlopen(f"{API_BASE}?{query}", timeout=30) as response:
        payload = json.load(response)
    notes = payload.get("notes", [])
    if not notes:
        raise ValueError(f"OpenReview returned no notes for {forum_id}")
    return notes[0]


def extract_decision_text(note: dict) -> str:
    for reply in note.get("details", {}).get("directReplies", []):
        invitations = " ".join(reply.get("invitations", []))
        content = reply.get("content", {})
        if "Decision" in invitations or "decision" in content:
            values = []
            for value in content.values():
                if isinstance(value, dict) and "value" in value:
                    values.append(str(value["value"]))
            return "\n".join(values)
    return ""


def main() -> None:
    ensure_dirs()
    manifest_path = DATA_DIR / "manifest_clean.csv"
    if not manifest_path.exists():
        raise SystemExit("manifest_clean.csv missing; run prepare_manifest.py first")

    rows = read_csv(manifest_path)
    validations = []
    failures = []

    for idx, row in enumerate(rows, start=1):
        local_json = load_json(resolve_repo_path(row["json_path"]))
        try:
            remote = fetch_note(row["forum"])
            title_remote = remote.get("content", {}).get("title", {}).get("value", "")
            title_local = local_json.get("content", {}).get("title", {}).get("value", "")
            decision_text = extract_decision_text(remote)
            decision_match = row["decision"].lower() in decision_text.lower()
            result = {
                "paper_id": row["paper_id"],
                "forum": row["forum"],
                "openreview_url": row["openreview_url"],
                "api_url": f"{API_BASE}?id={row['forum']}&details=directReplies",
                "remote_note_found": True,
                "forum_matches": remote.get("forum") == row["forum"],
                "title_matches_manifest": title_remote.strip() == row["title"].strip(),
                "title_matches_local_json": title_remote.strip() == title_local.strip(),
                "remote_direct_replies_count": len(remote.get("details", {}).get("directReplies", [])),
                "local_direct_replies_count": row["direct_replies_count_json"],
                "decision_text_contains_manifest_decision": decision_match,
            }
            validations.append(result)
        except Exception as exc:
            failure = {"paper_id": row["paper_id"], "forum": row["forum"], "error": repr(exc)}
            failures.append(failure)
            validations.append({**failure, "remote_note_found": False})
        time.sleep(0.15)
        if idx % 10 == 0:
            print(f"validated {idx}/{len(rows)}")

    summary = {
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "api_base": API_BASE,
        "paper_count": len(rows),
        "remote_note_found": sum(1 for item in validations if item.get("remote_note_found")),
        "forum_matches": sum(1 for item in validations if item.get("forum_matches")),
        "title_matches_manifest": sum(1 for item in validations if item.get("title_matches_manifest")),
        "title_matches_local_json": sum(1 for item in validations if item.get("title_matches_local_json")),
        "decision_text_contains_manifest_decision": sum(
            1 for item in validations if item.get("decision_text_contains_manifest_decision")
        ),
        "failures": failures,
        "verdict": "reliable" if not failures and all(item.get("title_matches_manifest") for item in validations) else "review_required",
        "limitations": [
            "This validates that the OpenReview API currently returns matching paper records and direct replies.",
            "It does not prove that every review-text extraction span is lossless; extraction quality is audited separately.",
            "Rejected submissions and reviews are public through OpenReview at validation time, but redistribution policy should still be described in the thesis.",
        ],
        "items": validations,
    }
    write_json(DATA_DIR / "source_reliability_report.json", summary)

    md_lines = [
        "# OpenReview Source Reliability Report",
        "",
        f"- Validated at: {summary['validated_at']}",
        f"- API base: {API_BASE}",
        f"- Paper count: {summary['paper_count']}",
        f"- Remote notes found: {summary['remote_note_found']}/{summary['paper_count']}",
        f"- Forum matches: {summary['forum_matches']}/{summary['paper_count']}",
        f"- Title matches manifest: {summary['title_matches_manifest']}/{summary['paper_count']}",
        f"- Decision text contains manifest decision: {summary['decision_text_contains_manifest_decision']}/{summary['paper_count']}",
        f"- Verdict: {summary['verdict']}",
        "",
        "## Limitations",
        "",
    ]
    md_lines.extend(f"- {item}" for item in summary["limitations"])
    (REPORT_DIR / "source_reliability_report.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"Wrote {DATA_DIR / 'source_reliability_report.json'}")
    print(f"Wrote {REPORT_DIR / 'source_reliability_report.md'}")
    print(f"verdict={summary['verdict']} remote_note_found={summary['remote_note_found']}/{summary['paper_count']}")


if __name__ == "__main__":
    main()

