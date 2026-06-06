from __future__ import annotations

from typing import Any


def render_review_audit_markdown(run: dict[str, Any], trace: list[dict[str, Any]]) -> str:
    result = run.get("result") or {}
    findings = result.get("ranked_findings") or []
    verification = result.get("verification") or {}
    trace_text = " -> ".join(str(event.get("event_type", "unknown")) for event in trace)
    lines = [
        f"# Review Audit Report: {run['paper_id']}",
        "",
        f"- Run ID: `{run['run_id']}`",
        f"- Status: `{run['status']}`",
        f"- Metric boundary: `{result.get('metric_boundary', 'silver diagnostic')}`",
        f"- Weaknesses: {result.get('weakness_count', 0)}",
        f"- Evidence blocks: {result.get('evidence_block_count', 0)}",
        f"- Trace: {trace_text or 'unavailable'}",
        "",
        "## Ranked Findings",
        "",
    ]
    if not findings:
        lines.append("No ranked findings.")
    for finding in findings:
        weakness_id = str(finding.get("weakness_id", "unknown"))
        verified = verification.get(weakness_id) or {}
        evidence_ids = ", ".join(f"`{item}`" for item in verified.get("evidence_block_ids", [])) or "none"
        lines.extend(
            [
                f"### {finding.get('rank', '-')} - {weakness_id}",
                "",
                f"- Label: `{finding.get('label', 'unknown')}`",
                f"- Rank score: {finding.get('rank_score', 0.0)}",
                f"- Support score: {verified.get('support_score', 0.0)}",
                f"- Evidence blocks: {evidence_ids}",
                f"- Rationale: {verified.get('rationale', 'unavailable')}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
