from __future__ import annotations

import re


FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*(?:\n|$)", re.S)
STANDALONE_IMAGE_RE = re.compile(r"^\s*!\[[^\]]*\]\([^)]+\)\s*$", re.M)
STANDALONE_HTML_IMAGE_RE = re.compile(r"^\s*<img\b[^>]*>\s*$", re.M | re.I)


def normalize_mineru_markdown(markdown: str) -> str:
    normalized = FRONTMATTER_RE.sub("", markdown or "", count=1)
    normalized = STANDALONE_IMAGE_RE.sub("", normalized)
    normalized = STANDALONE_HTML_IMAGE_RE.sub("", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()
