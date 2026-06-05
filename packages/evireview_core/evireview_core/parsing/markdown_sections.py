from __future__ import annotations

import re
from dataclasses import dataclass


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.M)


@dataclass(frozen=True)
class ParsedSection:
    section_path: str
    section_type: str
    text: str


def normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z][a-z0-9_+-]*|\d+(?:\.\d+)?", (text or "").lower())


def classify_section(section_path: str) -> str:
    lower = section_path.lower()
    rules = [
        ("abstract", ("abstract",)),
        ("introduction", ("introduction", "intro")),
        ("related_work", ("related work", "background")),
        ("experiment", ("experiment", "evaluation", "result", "benchmark", "analysis", "ablation")),
        ("method", ("method", "approach", "model", "framework", "algorithm", "preliminar")),
        ("limitation", ("limitation", "discussion", "future work")),
        ("conclusion", ("conclusion",)),
        ("appendix", ("appendix", "supplement")),
        ("reference", ("reference", "bibliography")),
    ]
    for section_type, keywords in rules:
        if any(keyword in lower for keyword in keywords):
            return section_type
    return "other"


def iter_sections(markdown: str) -> list[ParsedSection]:
    matches = list(HEADING_RE.finditer(markdown))
    sections: list[ParsedSection] = []
    if not matches:
        text = markdown.strip()
        if text:
            sections.append(ParsedSection("Document", "other", text))
        return sections

    stack: list[tuple[int, str]] = []
    prefix = markdown[: matches[0].start()].strip()
    if prefix:
        sections.append(ParsedSection("Document", "other", prefix))

    for index, match in enumerate(matches):
        level = len(match.group(1))
        title = normalize_ws(match.group(2))
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, title))
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        body = markdown[start:end].strip()
        if body:
            path = " > ".join(item[1] for item in stack)
            sections.append(ParsedSection(path, classify_section(path), body))
    return sections


def chunk_text(
    text: str,
    target_tokens: int = 420,
    overlap_tokens: int = 70,
    min_tokens: int = 60,
) -> list[str]:
    words = text.split()
    if len(words) <= target_tokens:
        return [normalize_ws(text)] if len(tokenize(text)) >= min_tokens else []

    chunks: list[str] = []
    step = max(1, target_tokens - overlap_tokens)
    for start in range(0, len(words), step):
        piece = " ".join(words[start : start + target_tokens])
        if len(tokenize(piece)) >= min_tokens:
            chunks.append(normalize_ws(piece))
        if start + target_tokens >= len(words):
            break
    return chunks
