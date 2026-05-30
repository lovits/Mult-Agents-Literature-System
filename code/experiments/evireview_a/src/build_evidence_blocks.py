from __future__ import annotations

import re
from collections import Counter

from common import (
    DATA_DIR,
    ensure_dirs,
    classify_section,
    normalize_ws,
    read_csv,
    resolve_repo_path,
    tokenize,
    write_json,
    write_jsonl,
)


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.M)
TARGET_TOKENS = 420
OVERLAP_TOKENS = 70
MIN_TOKENS = 60


def iter_sections(markdown: str):
    matches = list(HEADING_RE.finditer(markdown))
    if not matches:
        yield "Document", markdown
        return

    stack: list[tuple[int, str]] = []
    prefix = markdown[: matches[0].start()].strip()
    if prefix:
        yield "Document", prefix

    for i, match in enumerate(matches):
        level = len(match.group(1))
        title = normalize_ws(match.group(2))
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, title))
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        body = markdown[start:end].strip()
        if body:
            yield " > ".join(item[1] for item in stack), body


def chunk_text(text: str) -> list[str]:
    words = text.split()
    if len(words) <= TARGET_TOKENS:
        return [normalize_ws(text)] if len(tokenize(text)) >= MIN_TOKENS else []

    chunks: list[str] = []
    step = max(1, TARGET_TOKENS - OVERLAP_TOKENS)
    for start in range(0, len(words), step):
        piece = " ".join(words[start : start + TARGET_TOKENS])
        if len(tokenize(piece)) >= MIN_TOKENS:
            chunks.append(normalize_ws(piece))
        if start + TARGET_TOKENS >= len(words):
            break
    return chunks


def main() -> None:
    ensure_dirs()
    manifest_path = DATA_DIR / "manifest_clean.csv"
    if not manifest_path.exists():
        raise SystemExit("manifest_clean.csv missing; run prepare_manifest.py first")

    rows = read_csv(manifest_path)
    blocks: list[dict[str, object]] = []
    per_paper_counts: Counter[str] = Counter()
    section_counts: Counter[str] = Counter()

    for row in rows:
        md_path = resolve_repo_path(row["markdown_path"])
        markdown = md_path.read_text(encoding="utf-8", errors="ignore")
        local_index = 0
        for section_path, section_text in iter_sections(markdown):
            section_type = classify_section(section_path)
            for chunk_index, chunk in enumerate(chunk_text(section_text), start=1):
                local_index += 1
                token_count = len(tokenize(chunk))
                block = {
                    "block_id": f"{row['paper_index']}_b{local_index:04d}",
                    "paper_id": row["paper_id"],
                    "forum": row["forum"],
                    "paper_index": row["paper_index"],
                    "title": row["title"],
                    "decision": row["decision"],
                    "section_path": section_path,
                    "section_type": section_type,
                    "chunk_index_in_section": chunk_index,
                    "token_count": token_count,
                    "char_len": len(chunk),
                    "text": chunk,
                }
                blocks.append(block)
                per_paper_counts[row["paper_id"]] += 1
                section_counts[section_type] += 1

    write_jsonl(DATA_DIR / "evidence_blocks.jsonl", blocks)
    summary = {
        "paper_count": len(rows),
        "evidence_block_count": len(blocks),
        "papers_with_blocks": len(per_paper_counts),
        "min_blocks_per_paper": min(per_paper_counts.values()) if per_paper_counts else 0,
        "max_blocks_per_paper": max(per_paper_counts.values()) if per_paper_counts else 0,
        "mean_blocks_per_paper": round(sum(per_paper_counts.values()) / len(per_paper_counts), 2) if per_paper_counts else 0,
        "section_type_counts": dict(section_counts),
        "target_tokens": TARGET_TOKENS,
        "overlap_tokens": OVERLAP_TOKENS,
        "min_tokens": MIN_TOKENS,
    }
    write_json(DATA_DIR / "evidence_blocks_summary.json", summary)
    print(f"Wrote {DATA_DIR / 'evidence_blocks.jsonl'}")
    print(f"Wrote {DATA_DIR / 'evidence_blocks_summary.json'}")
    print(f"blocks={len(blocks)} papers={len(per_paper_counts)}/{len(rows)}")


if __name__ == "__main__":
    main()

