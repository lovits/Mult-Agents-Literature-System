# Agent RAG Refactor Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first refactor increment for EviReview-Lite by extracting reusable Agent-RAG domain, parsing, retrieval, verification, ranking, and deterministic workflow code into `packages/evireview_core` without changing current experiment outputs.

**Architecture:** This plan implements the foundation layer from `docs/design/agent_rag_frontend_backend_refactor_architecture_2026-06-02.md`. It keeps `code/experiments/evireview_a` as the reproducible experiment sandbox and introduces a dependency-free Python core package that future FastAPI, worker, and frontend work can call.

**Tech Stack:** Python 3 standard library, dataclasses, `unittest`, JSON/JSONL fixtures, existing experiment artifacts. No new dependencies in this foundation increment.

---

## Scope Check

The architecture spec covers several subsystems: reusable core, FastAPI backend, worker queue, Next.js frontend, experiment dashboard, and Qdrant/dense retrieval. This plan intentionally implements only the first independently testable subsystem: `evireview_core`.

Out of scope for this plan:

- Creating `services/api`.
- Creating `services/worker`.
- Creating `apps/web`.
- Adding Qdrant, Redis, PostgreSQL, RQ, FastAPI, Next.js, or other new dependencies.
- Re-running GLM or OpenRouter provider experiments.
- Moving or deleting files under `code/experiments/evireview_a`.

Follow-up plans after this foundation:

1. `FastAPI review-audit API + local worker plan`.
2. `Next.js paper workspace + experiment dashboard plan`.
3. `Qdrant dense retrieval adapter plan`.

## Existing Inputs

Read these before implementing:

- `docs/design/agent_rag_frontend_backend_refactor_architecture_2026-06-02.md`
- `docs/design/evireview_lite_technical_design.md`
- `code/experiments/evireview_a/src/common.py`
- `code/experiments/evireview_a/src/build_evidence_blocks.py`
- `code/experiments/evireview_a/src/retrieve_bm25.py`
- `code/experiments/evireview_a/src/verify_evidence_baseline.py`
- `code/experiments/evireview_a/src/rank_generated_weaknesses.py`
- `code/experiments/evireview_a/reports/thesis_experiment_tables.md`

## File Structure

Create:

```text
packages/
  evireview_core/
    evireview_core/
      __init__.py
      domain/
        __init__.py
        models.py
      io/
        __init__.py
        jsonl.py
      parsing/
        __init__.py
        markdown_sections.py
      retrieval/
        __init__.py
        bm25.py
        section_prior.py
        hierarchical.py
      verification/
        __init__.py
        heuristic.py
        labels.py
      ranking/
        __init__.py
        evidence_aware.py
      workflow/
        __init__.py
        deterministic.py
    README.md

tests/
  evireview_core/
    __init__.py
    fixtures/
      sample_blocks.jsonl
      sample_weaknesses.jsonl
    test_domain_models.py
    test_jsonl.py
    test_markdown_sections.py
    test_bm25.py
    test_hierarchical.py
    test_heuristic_verifier.py
    test_evidence_aware_ranker.py
    test_deterministic_workflow.py
```

Modify:

```text
code/experiments/evireview_a/README.md
docs/progress/evireview_current_progress_2026-05-30.md
```

Do not modify in this plan:

```text
code/experiments/evireview_a/data/*
code/experiments/evireview_a/reports/*
code/experiments/evireview_a/src/run_glm_reviewer_experiment.py
```

## Shared Commands

Use these commands from repo root:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest discover -s tests/evireview_core -v
python3 -m compileall -q packages/evireview_core tests/evireview_core
git diff --check
python3 - <<'PY'
from __future__ import annotations

import os
import re
import sys

patterns = [
    "90" + "a4" + "ea" + "1b",
    "l1VFY" + "HX2E6k" + "Chsjm",
    "GL" + "M" + r"_API_KEY=.*[A-Za-z0-9]",
    "ZHI" + "PU" + r".*90" + "a4",
    "ZA" + "I" + r"_API_KEY=.*[A-Za-z0-9]",
]
combined = re.compile("|".join(patterns))
matches: list[str] = []
for root, dirs, files in os.walk("."):
    dirs[:] = [name for name in dirs if name not in {".git", ".omx"}]
    for name in files:
        path = os.path.join(root, name)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                for line_number, line in enumerate(handle, start=1):
                    if combined.search(line):
                        matches.append(f"{path}:{line_number}")
        except OSError:
            continue
if matches:
    print("\n".join(matches))
    sys.exit(1)
PY
```

Expected verification notes:

- `unittest` should report all tests passing after each task's implementation step.
- `compileall` should exit with status `0`.
- `git diff --check` should produce no output and exit with status `0`.
- The secret scan should produce no output and exit with status `0`; any printed path is a failure.

---

### Task 1: Core Package Skeleton

**Files:**
- Create: `packages/evireview_core/evireview_core/__init__.py`
- Create: `packages/evireview_core/evireview_core/domain/__init__.py`
- Create: `packages/evireview_core/evireview_core/io/__init__.py`
- Create: `packages/evireview_core/evireview_core/parsing/__init__.py`
- Create: `packages/evireview_core/evireview_core/retrieval/__init__.py`
- Create: `packages/evireview_core/evireview_core/verification/__init__.py`
- Create: `packages/evireview_core/evireview_core/ranking/__init__.py`
- Create: `packages/evireview_core/evireview_core/workflow/__init__.py`
- Create: `packages/evireview_core/README.md`
- Create: `tests/evireview_core/__init__.py`
- Create: `tests/evireview_core/test_domain_models.py`

- [ ] **Step 1: Write the failing import test**

Create `tests/evireview_core/test_domain_models.py`:

```python
from __future__ import annotations

import unittest


class PackageImportTest(unittest.TestCase):
    def test_package_exposes_version(self) -> None:
        import evireview_core

        self.assertEqual(evireview_core.__version__, "0.1.0")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_domain_models -v
```

Expected: `ModuleNotFoundError: No module named 'evireview_core'`.

- [ ] **Step 3: Create the package skeleton**

Create `packages/evireview_core/evireview_core/__init__.py`:

```python
from __future__ import annotations

__version__ = "0.1.0"
```

Create these empty package files:

```python
from __future__ import annotations
```

Paths:

```text
packages/evireview_core/evireview_core/domain/__init__.py
packages/evireview_core/evireview_core/io/__init__.py
packages/evireview_core/evireview_core/parsing/__init__.py
packages/evireview_core/evireview_core/retrieval/__init__.py
packages/evireview_core/evireview_core/verification/__init__.py
packages/evireview_core/evireview_core/ranking/__init__.py
packages/evireview_core/evireview_core/workflow/__init__.py
tests/evireview_core/__init__.py
```

Create `packages/evireview_core/README.md`:

```markdown
# evireview_core

Reusable Python core for the EviReview-Lite Agent-RAG refactor.

This package contains dependency-free domain models, parsing helpers, retrieval baselines, verification labels, evidence-aware ranking, and deterministic workflow helpers. It is intentionally separate from `code/experiments/evireview_a`, which remains the reproducible experiment sandbox.

Run tests from the repository root:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest discover -s tests/evireview_core -v
```
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_domain_models -v
```

Expected: `Ran 1 test` and `OK`.

- [ ] **Step 5: Commit**

```bash
git add packages/evireview_core tests/evireview_core
git commit -m "Create EviReview core package skeleton" \
  -m "The refactor needs a dependency-free package boundary before API, worker, or frontend work can safely reuse experiment logic." \
  -m "Constraint: Keep existing experiment scripts and outputs unchanged" \
  -m "Confidence: high" \
  -m "Scope-risk: narrow" \
  -m "Tested: PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_domain_models -v"
```

---

### Task 2: Domain Models and Label Contracts

**Files:**
- Create: `packages/evireview_core/evireview_core/domain/models.py`
- Create: `packages/evireview_core/evireview_core/verification/labels.py`
- Modify: `tests/evireview_core/test_domain_models.py`

- [ ] **Step 1: Replace the domain test with model contract checks**

Replace `tests/evireview_core/test_domain_models.py`:

```python
from __future__ import annotations

import unittest

from evireview_core.domain.models import EvidenceBlock, VerificationResult, Weakness
from evireview_core.verification.labels import VerifierLabel, is_supported_or_better


class DomainModelTest(unittest.TestCase):
    def test_weakness_round_trip_dict(self) -> None:
        weakness = Weakness(
            weakness_id="w1",
            paper_id="p1",
            weakness_text="The experiment lacks ablation studies.",
            category="experiment",
            severity="major",
            source="human_review",
        )

        self.assertEqual(Weakness.from_dict(weakness.to_dict()), weakness)

    def test_evidence_block_round_trip_dict(self) -> None:
        block = EvidenceBlock(
            block_id="b1",
            paper_id="p1",
            section_path="Experiments > Ablations",
            section_type="experiment",
            text="We compare the model without the reranker.",
        )

        self.assertEqual(EvidenceBlock.from_dict(block.to_dict()), block)

    def test_verification_result_round_trip_dict(self) -> None:
        result = VerificationResult(
            weakness_id="w1",
            label=VerifierLabel.PARTIALLY_SUPPORTED.value,
            support_score=0.7,
            evidence_block_ids=("b1", "b2"),
            rationale="The paper mentions ablations but not all claimed settings.",
            verifier="heuristic_v1",
        )

        self.assertEqual(VerificationResult.from_dict(result.to_dict()), result)

    def test_supported_or_better(self) -> None:
        self.assertTrue(is_supported_or_better(VerifierLabel.SUPPORTED.value))
        self.assertTrue(is_supported_or_better(VerifierLabel.PARTIALLY_SUPPORTED.value))
        self.assertFalse(is_supported_or_better(VerifierLabel.UNSUPPORTED.value))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_domain_models -v
```

Expected: import failure for `evireview_core.domain.models`.

- [ ] **Step 3: Add verifier labels**

Create `packages/evireview_core/evireview_core/verification/labels.py`:

```python
from __future__ import annotations

from enum import Enum


class VerifierLabel(str, Enum):
    SUPPORTED = "Supported"
    PARTIALLY_SUPPORTED = "Partially Supported"
    MENTIONED_NOT_PROBLEM = "Mentioned but Not Problem"
    GENERIC_VAGUE = "Generic / Vague"
    UNSUPPORTED = "Unsupported"
    CONTRADICTED = "Contradicted"


SUPPORTED_OR_BETTER = {
    VerifierLabel.SUPPORTED.value,
    VerifierLabel.PARTIALLY_SUPPORTED.value,
}


def is_supported_or_better(label: str) -> bool:
    return label in SUPPORTED_OR_BETTER
```

- [ ] **Step 4: Add domain dataclasses**

Create `packages/evireview_core/evireview_core/domain/models.py`:

```python
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class PaperSection:
    paper_id: str
    section_path: str
    section_type: str
    text: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PaperSection":
        return cls(
            paper_id=str(payload["paper_id"]),
            section_path=str(payload["section_path"]),
            section_type=str(payload["section_type"]),
            text=str(payload["text"]),
        )


@dataclass(frozen=True)
class EvidenceBlock:
    block_id: str
    paper_id: str
    section_path: str
    section_type: str
    text: str
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EvidenceBlock":
        return cls(
            block_id=str(payload["block_id"]),
            paper_id=str(payload["paper_id"]),
            section_path=str(payload["section_path"]),
            section_type=str(payload["section_type"]),
            text=str(payload["text"]),
            score=float(payload.get("score", 0.0)),
        )


@dataclass(frozen=True)
class Weakness:
    weakness_id: str
    paper_id: str
    weakness_text: str
    category: str
    severity: str = "unknown"
    source: str = "human_review"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Weakness":
        return cls(
            weakness_id=str(payload["weakness_id"]),
            paper_id=str(payload["paper_id"]),
            weakness_text=str(payload["weakness_text"]),
            category=str(payload.get("category", payload.get("category_rule", "other"))),
            severity=str(payload.get("severity", payload.get("severity_hint", "unknown"))),
            source=str(payload.get("source", "human_review")),
        )


@dataclass(frozen=True)
class RetrievalCandidate:
    weakness_id: str
    block_id: str
    rank: int
    score: float
    retriever: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VerificationResult:
    weakness_id: str
    label: str
    support_score: float
    evidence_block_ids: tuple[str, ...]
    rationale: str
    verifier: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["evidence_block_ids"] = list(self.evidence_block_ids)
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "VerificationResult":
        return cls(
            weakness_id=str(payload["weakness_id"]),
            label=str(payload.get("label", payload.get("pred_label", ""))),
            support_score=float(payload.get("support_score", 0.0)),
            evidence_block_ids=tuple(str(item) for item in payload.get("evidence_block_ids", [])),
            rationale=str(payload.get("rationale", "")),
            verifier=str(payload.get("verifier", "")),
        )


@dataclass(frozen=True)
class RankedFinding:
    weakness_id: str
    rank: int
    rank_score: float
    label: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
```

- [ ] **Step 5: Run the test to verify it passes**

Run:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_domain_models -v
```

Expected: `Ran 4 tests` and `OK`.

- [ ] **Step 6: Commit**

```bash
git add packages/evireview_core/evireview_core/domain packages/evireview_core/evireview_core/verification tests/evireview_core/test_domain_models.py
git commit -m "Define EviReview core domain contracts" \
  -m "Stable dataclasses and verifier labels keep API, worker, and experiment adapters from redefining weakness and evidence schemas independently." \
  -m "Constraint: Preserve existing JSON field compatibility such as category_rule and pred_label" \
  -m "Confidence: high" \
  -m "Scope-risk: narrow" \
  -m "Tested: PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_domain_models -v"
```

---

### Task 3: JSONL and Text Utilities

**Files:**
- Create: `packages/evireview_core/evireview_core/io/jsonl.py`
- Create: `packages/evireview_core/evireview_core/parsing/markdown_sections.py`
- Create: `tests/evireview_core/test_jsonl.py`
- Create: `tests/evireview_core/test_markdown_sections.py`

- [ ] **Step 1: Write failing JSONL tests**

Create `tests/evireview_core/test_jsonl.py`:

```python
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from evireview_core.io.jsonl import read_jsonl, write_jsonl


class JsonlTest(unittest.TestCase):
    def test_write_and_read_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.jsonl"
            rows = [{"id": "a", "value": 1}, {"id": "b", "value": 2}]

            write_jsonl(path, rows)

            self.assertEqual(read_jsonl(path), rows)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Write failing parsing tests**

Create `tests/evireview_core/test_markdown_sections.py`:

```python
from __future__ import annotations

import unittest

from evireview_core.parsing.markdown_sections import chunk_text, classify_section, iter_sections, normalize_ws, tokenize


class MarkdownSectionsTest(unittest.TestCase):
    def test_iter_sections_preserves_nested_path(self) -> None:
        markdown = "# Method\nMain method text.\n## Ablation\nAblation details."

        sections = list(iter_sections(markdown))

        self.assertEqual(sections[0].section_path, "Method")
        self.assertEqual(sections[0].section_type, "method")
        self.assertEqual(sections[1].section_path, "Method > Ablation")
        self.assertEqual(sections[1].section_type, "experiment")

    def test_chunk_text_keeps_short_valid_block(self) -> None:
        text = " ".join(["ablation"] * 80)

        chunks = chunk_text(text, target_tokens=30, overlap_tokens=5, min_tokens=10)

        self.assertGreaterEqual(len(chunks), 3)
        self.assertTrue(all("ablation" in chunk for chunk in chunks))

    def test_normalize_and_tokenize(self) -> None:
        self.assertEqual(normalize_ws("A\n\n  B"), "A B")
        self.assertEqual(tokenize("Ablation-1 improves F1 by 3.5"), ["ablation-1", "improves", "f1", "by", "3.5"])

    def test_classify_section(self) -> None:
        self.assertEqual(classify_section("Experiments > Ablation"), "experiment")
        self.assertEqual(classify_section("Related Work"), "related_work")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run tests to verify they fail**

Run:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_jsonl tests.evireview_core.test_markdown_sections -v
```

Expected: import failures for `evireview_core.io.jsonl` and `evireview_core.parsing.markdown_sections`.

- [ ] **Step 4: Implement JSONL helpers**

Create `packages/evireview_core/evireview_core/io/jsonl.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
```

- [ ] **Step 5: Implement markdown section helpers**

Create `packages/evireview_core/evireview_core/parsing/markdown_sections.py`:

```python
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
```

- [ ] **Step 6: Run tests to verify they pass**

Run:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_jsonl tests.evireview_core.test_markdown_sections -v
```

Expected: `Ran 5 tests` and `OK`.

- [ ] **Step 7: Commit**

```bash
git add packages/evireview_core/evireview_core/io packages/evireview_core/evireview_core/parsing tests/evireview_core/test_jsonl.py tests/evireview_core/test_markdown_sections.py
git commit -m "Extract EviReview text and JSONL helpers" \
  -m "The core package needs dependency-free IO and markdown parsing before retrieval and workflow code can be tested outside experiment scripts." \
  -m "Constraint: Mirror existing experiment parsing behavior without changing experiment artifacts" \
  -m "Confidence: high" \
  -m "Scope-risk: narrow" \
  -m "Tested: PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_jsonl tests.evireview_core.test_markdown_sections -v"
```

---

### Task 4: BM25 Retrieval Core

**Files:**
- Create: `packages/evireview_core/evireview_core/retrieval/bm25.py`
- Create: `tests/evireview_core/test_bm25.py`

- [ ] **Step 1: Write the failing BM25 test**

Create `tests/evireview_core/test_bm25.py`:

```python
from __future__ import annotations

import unittest

from evireview_core.domain.models import EvidenceBlock
from evireview_core.retrieval.bm25 import bm25_search


class Bm25Test(unittest.TestCase):
    def test_bm25_returns_matching_experiment_block_first(self) -> None:
        blocks = [
            EvidenceBlock("b1", "p1", "Method", "method", "The model uses a planner."),
            EvidenceBlock("b2", "p1", "Experiments", "experiment", "The ablation study removes the reranker."),
            EvidenceBlock("b3", "p1", "Related Work", "related_work", "Prior work studies agents."),
        ]

        results = bm25_search("missing ablation study", blocks, top_k=2)

        self.assertEqual(results[0].block_id, "b2")
        self.assertEqual(results[0].rank, 1)
        self.assertGreater(results[0].score, 0.0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_bm25 -v
```

Expected: import failure for `evireview_core.retrieval.bm25`.

- [ ] **Step 3: Implement BM25 search**

Create `packages/evireview_core/evireview_core/retrieval/bm25.py`:

```python
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass

from evireview_core.domain.models import EvidenceBlock
from evireview_core.parsing.markdown_sections import tokenize


@dataclass(frozen=True)
class RetrievedEvidence:
    block_id: str
    paper_id: str
    section_path: str
    section_type: str
    text: str
    rank: int
    score: float
    retriever: str


def bm25_scores(
    query_tokens: list[str],
    docs: list[EvidenceBlock],
    k1: float = 1.5,
    b: float = 0.75,
) -> list[tuple[float, EvidenceBlock]]:
    if not docs:
        return []

    tokenized_docs = [tokenize(doc.text) for doc in docs]
    doc_lens = [len(tokens) for tokens in tokenized_docs]
    avgdl = sum(doc_lens) / len(doc_lens)
    df = Counter()
    for tokens in tokenized_docs:
        df.update(set(tokens))

    q_counts = Counter(query_tokens)
    n_docs = len(docs)
    scored: list[tuple[float, EvidenceBlock]] = []
    for doc, tokens, doc_len in zip(docs, tokenized_docs, doc_lens):
        tf = Counter(tokens)
        score = 0.0
        for term, qtf in q_counts.items():
            if term not in tf:
                continue
            idf = math.log(1 + (n_docs - df[term] + 0.5) / (df[term] + 0.5))
            denom = tf[term] + k1 * (1 - b + b * doc_len / avgdl)
            score += idf * (tf[term] * (k1 + 1) / denom) * qtf
        if score > 0:
            scored.append((round(score, 6), doc))
    return sorted(scored, key=lambda item: item[0], reverse=True)


def bm25_search(query: str, docs: list[EvidenceBlock], top_k: int = 5) -> list[RetrievedEvidence]:
    ranked = bm25_scores(tokenize(query), docs)[:top_k]
    return [
        RetrievedEvidence(
            block_id=doc.block_id,
            paper_id=doc.paper_id,
            section_path=doc.section_path,
            section_type=doc.section_type,
            text=doc.text,
            rank=rank,
            score=score,
            retriever="bm25",
        )
        for rank, (score, doc) in enumerate(ranked, start=1)
    ]
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_bm25 -v
```

Expected: `Ran 1 test` and `OK`.

- [ ] **Step 5: Commit**

```bash
git add packages/evireview_core/evireview_core/retrieval/bm25.py tests/evireview_core/test_bm25.py
git commit -m "Extract BM25 retrieval into EviReview core" \
  -m "BM25 is the strongest transparent baseline in the current thesis pipeline and needs to be reusable by future API and worker code." \
  -m "Constraint: No new retrieval dependency in the foundation increment" \
  -m "Confidence: high" \
  -m "Scope-risk: narrow" \
  -m "Tested: PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_bm25 -v"
```

---

### Task 5: Section Prior and Hierarchical Retrieval

**Files:**
- Create: `packages/evireview_core/evireview_core/retrieval/section_prior.py`
- Create: `packages/evireview_core/evireview_core/retrieval/hierarchical.py`
- Create: `tests/evireview_core/test_hierarchical.py`

- [ ] **Step 1: Write the failing hierarchical retrieval test**

Create `tests/evireview_core/test_hierarchical.py`:

```python
from __future__ import annotations

import unittest

from evireview_core.domain.models import EvidenceBlock, Weakness
from evireview_core.retrieval.hierarchical import hierarchical_search
from evireview_core.retrieval.section_prior import section_prior


class HierarchicalRetrievalTest(unittest.TestCase):
    def test_section_prior_prefers_expected_experiment_section(self) -> None:
        self.assertEqual(section_prior("experiment", "experiment"), 1.0)
        self.assertEqual(section_prior("experiment", "reference"), 0.15)
        self.assertEqual(section_prior("experiment", "related_work"), 0.0)

    def test_hierarchical_search_returns_section_routed_candidate(self) -> None:
        weakness = Weakness(
            weakness_id="w1",
            paper_id="p1",
            weakness_text="The paper lacks ablation baselines.",
            category="experiment",
            severity="major",
        )
        blocks = [
            EvidenceBlock("b1", "p1", "Method", "method", "The method has a planner."),
            EvidenceBlock("b2", "p1", "Experiments", "experiment", "The paper reports datasets and baselines."),
            EvidenceBlock("b3", "p1", "References", "reference", "References are listed here."),
        ]

        results = hierarchical_search(weakness, blocks, top_k=2)

        self.assertEqual(results[0].block_id, "b2")
        self.assertEqual(results[0].retriever, "hierarchical_rrf")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_hierarchical -v
```

Expected: import failure for `evireview_core.retrieval.hierarchical`.

- [ ] **Step 3: Implement section priors**

Create `packages/evireview_core/evireview_core/retrieval/section_prior.py`:

```python
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
    if section_alignment(category, section_type):
        return 1.0
    if section_type in {"reference", "appendix"}:
        return 0.15
    return 0.0
```

- [ ] **Step 4: Implement hierarchical retrieval**

Create `packages/evireview_core/evireview_core/retrieval/hierarchical.py`:

```python
from __future__ import annotations

from collections import defaultdict

from evireview_core.domain.models import EvidenceBlock, Weakness
from evireview_core.retrieval.bm25 import RetrievedEvidence, bm25_search
from evireview_core.retrieval.section_prior import section_prior


RRF_K = 60


def _section_read(weakness: Weakness, docs: list[EvidenceBlock], top_k: int) -> list[RetrievedEvidence]:
    scored: list[tuple[float, EvidenceBlock]] = []
    for doc in docs:
        prior = section_prior(weakness.category, doc.section_type)
        if prior > 0:
            scored.append((prior, doc))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [
        RetrievedEvidence(
            block_id=doc.block_id,
            paper_id=doc.paper_id,
            section_path=doc.section_path,
            section_type=doc.section_type,
            text=doc.text,
            rank=rank,
            score=score,
            retriever="section_read",
        )
        for rank, (score, doc) in enumerate(scored[:top_k], start=1)
    ]


def _rrf_merge(ranked_lists: list[list[RetrievedEvidence]], top_k: int) -> list[RetrievedEvidence]:
    scores: dict[str, float] = defaultdict(float)
    by_block: dict[str, RetrievedEvidence] = {}
    for ranked in ranked_lists:
        for item in ranked:
            scores[item.block_id] += 1.0 / (RRF_K + item.rank)
            by_block[item.block_id] = item
    merged_ids = sorted(scores, key=lambda block_id: scores[block_id], reverse=True)[:top_k]
    return [
        RetrievedEvidence(
            block_id=by_block[block_id].block_id,
            paper_id=by_block[block_id].paper_id,
            section_path=by_block[block_id].section_path,
            section_type=by_block[block_id].section_type,
            text=by_block[block_id].text,
            rank=rank,
            score=round(scores[block_id], 6),
            retriever="hierarchical_rrf",
        )
        for rank, block_id in enumerate(merged_ids, start=1)
    ]


def hierarchical_search(weakness: Weakness, docs: list[EvidenceBlock], top_k: int = 5) -> list[RetrievedEvidence]:
    same_paper_docs = [doc for doc in docs if doc.paper_id == weakness.paper_id]
    keyword = bm25_search(weakness.weakness_text, same_paper_docs, top_k=top_k)
    routed = _section_read(weakness, same_paper_docs, top_k=top_k)
    return _rrf_merge([keyword, routed], top_k=top_k)
```

- [ ] **Step 5: Run the test to verify it passes**

Run:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_hierarchical -v
```

Expected: `Ran 2 tests` and `OK`.

- [ ] **Step 6: Commit**

```bash
git add packages/evireview_core/evireview_core/retrieval/section_prior.py packages/evireview_core/evireview_core/retrieval/hierarchical.py tests/evireview_core/test_hierarchical.py
git commit -m "Add section-routed hierarchical retrieval core" \
  -m "The architecture upgrades Paper-RAG from plain section-aware scoring to explicit keyword and section-read tools merged by RRF." \
  -m "Constraint: Keep this foundation implementation lexical and dependency-free" \
  -m "Confidence: high" \
  -m "Scope-risk: narrow" \
  -m "Tested: PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_hierarchical -v"
```

---

### Task 6: Heuristic Evidence Verifier

**Files:**
- Create: `packages/evireview_core/evireview_core/verification/heuristic.py`
- Create: `tests/evireview_core/test_heuristic_verifier.py`

- [ ] **Step 1: Write the failing verifier test**

Create `tests/evireview_core/test_heuristic_verifier.py`:

```python
from __future__ import annotations

import unittest

from evireview_core.domain.models import Weakness
from evireview_core.retrieval.bm25 import RetrievedEvidence
from evireview_core.verification.heuristic import verify_with_heuristics
from evireview_core.verification.labels import VerifierLabel


class HeuristicVerifierTest(unittest.TestCase):
    def test_verifier_marks_supported_when_evidence_overlaps(self) -> None:
        weakness = Weakness("w1", "p1", "The paper lacks ablation baselines.", "experiment", "major")
        evidence = [
            RetrievedEvidence(
                block_id="b1",
                paper_id="p1",
                section_path="Experiments",
                section_type="experiment",
                text="The ablation baseline removes the reranker and reports accuracy.",
                rank=1,
                score=2.0,
                retriever="bm25",
            )
        ]

        result = verify_with_heuristics(weakness, evidence)

        self.assertEqual(result.label, VerifierLabel.PARTIALLY_SUPPORTED.value)
        self.assertGreater(result.support_score, 0.0)
        self.assertEqual(result.evidence_block_ids, ("b1",))

    def test_verifier_marks_unsupported_without_evidence(self) -> None:
        weakness = Weakness("w1", "p1", "The paper lacks ablation baselines.", "experiment", "major")

        result = verify_with_heuristics(weakness, [])

        self.assertEqual(result.label, VerifierLabel.UNSUPPORTED.value)
        self.assertEqual(result.support_score, 0.0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_heuristic_verifier -v
```

Expected: import failure for `evireview_core.verification.heuristic`.

- [ ] **Step 3: Implement heuristic verifier**

Create `packages/evireview_core/evireview_core/verification/heuristic.py`:

```python
from __future__ import annotations

from evireview_core.domain.models import VerificationResult, Weakness
from evireview_core.parsing.markdown_sections import tokenize
from evireview_core.retrieval.bm25 import RetrievedEvidence
from evireview_core.verification.labels import VerifierLabel


def _overlap_ratio(left: str, right: str) -> float:
    left_tokens = set(tokenize(left))
    right_tokens = set(tokenize(right))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens)


def verify_with_heuristics(weakness: Weakness, evidence: list[RetrievedEvidence]) -> VerificationResult:
    if not evidence:
        return VerificationResult(
            weakness_id=weakness.weakness_id,
            label=VerifierLabel.UNSUPPORTED.value,
            support_score=0.0,
            evidence_block_ids=(),
            rationale="No retrieved evidence was available for this weakness.",
            verifier="heuristic_overlap_v1",
        )

    best_overlap = max(_overlap_ratio(weakness.weakness_text, item.text) for item in evidence)
    evidence_ids = tuple(item.block_id for item in evidence[:3])
    if best_overlap >= 0.45:
        label = VerifierLabel.PARTIALLY_SUPPORTED.value
        rationale = "Retrieved evidence shares substantial terms with the weakness and should be reviewed."
    elif best_overlap >= 0.2:
        label = VerifierLabel.MENTIONED_NOT_PROBLEM.value
        rationale = "Retrieved evidence mentions related terms but does not clearly establish the problem."
    else:
        label = VerifierLabel.UNSUPPORTED.value
        rationale = "Retrieved evidence has weak lexical overlap with the weakness."

    return VerificationResult(
        weakness_id=weakness.weakness_id,
        label=label,
        support_score=round(best_overlap, 4),
        evidence_block_ids=evidence_ids,
        rationale=rationale,
        verifier="heuristic_overlap_v1",
    )
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_heuristic_verifier -v
```

Expected: `Ran 2 tests` and `OK`.

- [ ] **Step 5: Commit**

```bash
git add packages/evireview_core/evireview_core/verification/heuristic.py tests/evireview_core/test_heuristic_verifier.py
git commit -m "Add heuristic evidence verifier core" \
  -m "A deterministic verifier keeps the refactored workflow runnable without hosted model calls and preserves the gold versus silver metric boundary." \
  -m "Constraint: This verifier is a diagnostic baseline, not a human-gold evaluator" \
  -m "Confidence: medium" \
  -m "Scope-risk: narrow" \
  -m "Directive: Do not report heuristic labels as final evidence gold labels" \
  -m "Tested: PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_heuristic_verifier -v"
```

---

### Task 7: Evidence-aware Ranker

**Files:**
- Create: `packages/evireview_core/evireview_core/ranking/evidence_aware.py`
- Create: `tests/evireview_core/test_evidence_aware_ranker.py`

- [ ] **Step 1: Write the failing ranker test**

Create `tests/evireview_core/test_evidence_aware_ranker.py`:

```python
from __future__ import annotations

import unittest

from evireview_core.domain.models import VerificationResult, Weakness
from evireview_core.ranking.evidence_aware import rank_weaknesses, score_finding
from evireview_core.verification.labels import VerifierLabel


class EvidenceAwareRankerTest(unittest.TestCase):
    def test_score_favors_supported_major_weakness(self) -> None:
        weakness = Weakness("w1", "p1", "Major missing ablation.", "experiment", "major")
        result = VerificationResult(
            weakness_id="w1",
            label=VerifierLabel.SUPPORTED.value,
            support_score=0.8,
            evidence_block_ids=("b1",),
            rationale="Evidence supports the issue.",
            verifier="test",
        )

        self.assertGreater(score_finding(weakness, result), 1.0)

    def test_rank_weaknesses_orders_by_evidence_score(self) -> None:
        weaknesses = [
            Weakness("w1", "p1", "Minor clarity issue.", "clarity", "minor"),
            Weakness("w2", "p1", "Major experiment issue.", "experiment", "major"),
        ]
        verification = {
            "w1": VerificationResult("w1", VerifierLabel.MENTIONED_NOT_PROBLEM.value, 0.2, ("b1",), "", "test"),
            "w2": VerificationResult("w2", VerifierLabel.SUPPORTED.value, 0.8, ("b2",), "", "test"),
        }

        ranked = rank_weaknesses(weaknesses, verification, top_k=2)

        self.assertEqual(ranked[0].weakness_id, "w2")
        self.assertEqual(ranked[0].rank, 1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_evidence_aware_ranker -v
```

Expected: import failure for `evireview_core.ranking.evidence_aware`.

- [ ] **Step 3: Implement evidence-aware ranker**

Create `packages/evireview_core/evireview_core/ranking/evidence_aware.py`:

```python
from __future__ import annotations

from evireview_core.domain.models import RankedFinding, VerificationResult, Weakness


LABEL_WEIGHTS = {
    "Supported": 1.0,
    "Partially Supported": 0.8,
    "Mentioned but Not Problem": 0.45,
    "Generic / Vague": 0.2,
    "Unsupported": 0.05,
    "Contradicted": 0.0,
}

SEVERITY_WEIGHTS = {
    "major": 1.0,
    "minor": 0.65,
    "minor_or_question": 0.6,
    "unknown": 0.75,
}


def score_finding(weakness: Weakness, result: VerificationResult) -> float:
    label_weight = LABEL_WEIGHTS.get(result.label, 0.25)
    severity_weight = SEVERITY_WEIGHTS.get(weakness.severity, 0.75)
    return round((0.45 + result.support_score) * label_weight * severity_weight, 6)


def rank_weaknesses(
    weaknesses: list[Weakness],
    verification: dict[str, VerificationResult],
    top_k: int = 3,
) -> list[RankedFinding]:
    scored: list[tuple[float, Weakness, VerificationResult]] = []
    for weakness in weaknesses:
        result = verification.get(weakness.weakness_id)
        if result is not None:
            scored.append((score_finding(weakness, result), weakness, result))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [
        RankedFinding(
            weakness_id=weakness.weakness_id,
            rank=rank,
            rank_score=score,
            label=result.label,
        )
        for rank, (score, weakness, result) in enumerate(scored[:top_k], start=1)
    ]
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_evidence_aware_ranker -v
```

Expected: `Ran 2 tests` and `OK`.

- [ ] **Step 5: Commit**

```bash
git add packages/evireview_core/evireview_core/ranking/evidence_aware.py tests/evireview_core/test_evidence_aware_ranker.py
git commit -m "Extract evidence-aware weakness ranking" \
  -m "The ranked finding contract turns verifier evidence into the shortlist that the frontend and thesis report need to display." \
  -m "Constraint: Preserve the existing diagnostic rank formula from generated weakness experiments" \
  -m "Confidence: medium" \
  -m "Scope-risk: narrow" \
  -m "Tested: PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_evidence_aware_ranker -v"
```

---

### Task 8: Deterministic Review-Audit Workflow

**Files:**
- Create: `packages/evireview_core/evireview_core/workflow/deterministic.py`
- Create: `tests/evireview_core/test_deterministic_workflow.py`

- [ ] **Step 1: Write the failing workflow test**

Create `tests/evireview_core/test_deterministic_workflow.py`:

```python
from __future__ import annotations

import unittest

from evireview_core.domain.models import EvidenceBlock, Weakness
from evireview_core.workflow.deterministic import run_deterministic_review_audit


class DeterministicWorkflowTest(unittest.TestCase):
    def test_workflow_returns_retrieval_verification_and_ranking(self) -> None:
        weaknesses = [
            Weakness("w1", "p1", "The paper lacks ablation baselines.", "experiment", "major"),
            Weakness("w2", "p1", "The motivation is unclear.", "clarity", "minor"),
        ]
        blocks = [
            EvidenceBlock("b1", "p1", "Experiments", "experiment", "The ablation baseline removes the reranker."),
            EvidenceBlock("b2", "p1", "Introduction", "introduction", "The paper motivates agent retrieval."),
        ]

        result = run_deterministic_review_audit(weaknesses, blocks, top_k=2)

        self.assertEqual(result["weakness_count"], 2)
        self.assertEqual(len(result["retrieval"]), 2)
        self.assertEqual(len(result["verification"]), 2)
        self.assertGreaterEqual(len(result["ranked_findings"]), 1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_deterministic_workflow -v
```

Expected: import failure for `evireview_core.workflow.deterministic`.

- [ ] **Step 3: Implement deterministic workflow**

Create `packages/evireview_core/evireview_core/workflow/deterministic.py`:

```python
from __future__ import annotations

from typing import Any

from evireview_core.domain.models import EvidenceBlock, VerificationResult, Weakness
from evireview_core.ranking.evidence_aware import rank_weaknesses
from evireview_core.retrieval.hierarchical import hierarchical_search
from evireview_core.verification.heuristic import verify_with_heuristics


def run_deterministic_review_audit(
    weaknesses: list[Weakness],
    blocks: list[EvidenceBlock],
    top_k: int = 5,
) -> dict[str, Any]:
    retrieval: dict[str, list[dict[str, Any]]] = {}
    verification: dict[str, VerificationResult] = {}

    for weakness in weaknesses:
        candidates = hierarchical_search(weakness, blocks, top_k=top_k)
        retrieval[weakness.weakness_id] = [
            {
                "block_id": item.block_id,
                "rank": item.rank,
                "score": item.score,
                "section_type": item.section_type,
                "retriever": item.retriever,
            }
            for item in candidates
        ]
        verification[weakness.weakness_id] = verify_with_heuristics(weakness, candidates)

    ranked = rank_weaknesses(weaknesses, verification, top_k=3)
    return {
        "workflow": "deterministic_review_audit_v1",
        "weakness_count": len(weaknesses),
        "evidence_block_count": len(blocks),
        "retrieval": retrieval,
        "verification": {key: value.to_dict() for key, value in verification.items()},
        "ranked_findings": [item.to_dict() for item in ranked],
        "metric_boundary": "silver diagnostic",
    }
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_deterministic_workflow -v
```

Expected: `Ran 1 test` and `OK`.

- [ ] **Step 5: Commit**

```bash
git add packages/evireview_core/evireview_core/workflow/deterministic.py tests/evireview_core/test_deterministic_workflow.py
git commit -m "Add deterministic review audit workflow" \
  -m "A minimal workflow proves the extracted core can execute weakness retrieval, verification, and ranking without API, worker, frontend, or hosted model dependencies." \
  -m "Constraint: Workflow output is silver diagnostic and must not overwrite experiment gold data" \
  -m "Confidence: medium" \
  -m "Scope-risk: narrow" \
  -m "Directive: Future API and worker code should call this core workflow instead of duplicating retrieval and verifier logic" \
  -m "Tested: PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_deterministic_workflow -v"
```

---

### Task 9: Fixture-backed End-to-end Core Regression

**Files:**
- Create: `tests/evireview_core/fixtures/sample_blocks.jsonl`
- Create: `tests/evireview_core/fixtures/sample_weaknesses.jsonl`
- Modify: `tests/evireview_core/test_deterministic_workflow.py`

- [ ] **Step 1: Add committed fixture data**

Create `tests/evireview_core/fixtures/sample_blocks.jsonl`:

```jsonl
{"block_id":"b1","paper_id":"p1","section_path":"Experiments","section_type":"experiment","text":"The ablation baseline removes the reranker and compares retrieval accuracy across settings."}
{"block_id":"b2","paper_id":"p1","section_path":"Method","section_type":"method","text":"The model uses a planner and a retrieval module to select evidence."}
{"block_id":"b3","paper_id":"p1","section_path":"Introduction","section_type":"introduction","text":"The paper motivates evidence-grounded review assistance for researchers."}
```

Create `tests/evireview_core/fixtures/sample_weaknesses.jsonl`:

```jsonl
{"weakness_id":"w1","paper_id":"p1","weakness_text":"The paper lacks ablation baselines for the reranker.","category":"experiment","severity":"major","source":"fixture"}
{"weakness_id":"w2","paper_id":"p1","weakness_text":"The motivation for evidence-grounded review assistance is unclear.","category":"clarity","severity":"minor","source":"fixture"}
```

- [ ] **Step 2: Extend workflow test to load fixtures**

Append this test method to `tests/evireview_core/test_deterministic_workflow.py` inside `DeterministicWorkflowTest`:

```python
    def test_workflow_runs_on_committed_jsonl_fixtures(self) -> None:
        from pathlib import Path

        from evireview_core.domain.models import EvidenceBlock, Weakness
        from evireview_core.io.jsonl import read_jsonl

        fixture_dir = Path(__file__).resolve().parent / "fixtures"
        weaknesses = [Weakness.from_dict(row) for row in read_jsonl(fixture_dir / "sample_weaknesses.jsonl")]
        blocks = [EvidenceBlock.from_dict(row) for row in read_jsonl(fixture_dir / "sample_blocks.jsonl")]

        result = run_deterministic_review_audit(weaknesses, blocks, top_k=2)

        self.assertEqual(result["workflow"], "deterministic_review_audit_v1")
        self.assertEqual(result["weakness_count"], 2)
        self.assertEqual(result["metric_boundary"], "silver diagnostic")
```

- [ ] **Step 3: Run the workflow test**

Run:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest tests.evireview_core.test_deterministic_workflow -v
```

Expected: `Ran 2 tests` and `OK`.

- [ ] **Step 4: Run the full core test suite**

Run:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest discover -s tests/evireview_core -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add tests/evireview_core/fixtures tests/evireview_core/test_deterministic_workflow.py
git commit -m "Lock the core workflow with JSONL fixtures" \
  -m "Small committed fixtures give future refactors a stable regression target without depending on large experiment artifacts or raw external data." \
  -m "Constraint: Fixtures must remain small and license-safe" \
  -m "Confidence: high" \
  -m "Scope-risk: narrow" \
  -m "Tested: PYTHONPATH=packages/evireview_core python3 -m unittest discover -s tests/evireview_core -v"
```

---

### Task 10: Experiment Adapter Documentation

**Files:**
- Modify: `code/experiments/evireview_a/README.md`
- Modify: `docs/progress/evireview_current_progress_2026-05-30.md`

- [ ] **Step 1: Add a README section explaining the new core boundary**

Append this section to `code/experiments/evireview_a/README.md`:

```markdown
## Refactor boundary

`code/experiments/evireview_a` remains the reproducible experiment sandbox. Stable, dependency-free logic is being extracted into `packages/evireview_core` so that future API, worker, and frontend code can reuse the same domain contracts.

Current boundary:

- Keep experiment scripts and existing metrics in this directory.
- Put reusable dataclasses, JSONL helpers, markdown section parsing, BM25 retrieval, hierarchical retrieval, heuristic verification, evidence-aware ranking, and deterministic workflow helpers in `packages/evireview_core`.
- Do not store provider secrets in either location.
- Do not treat heuristic or model-generated labels as human gold labels.

Run the core regression suite from repo root:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest discover -s tests/evireview_core -v
```
```

- [ ] **Step 2: Add a progress note**

Append this section to `docs/progress/evireview_current_progress_2026-05-30.md`:

```markdown
### Core refactor implementation plan

2026-06-05 update: the Agent-RAG frontend/backend architecture has been converted into a first implementation plan at `docs/superpowers/plans/2026-06-05-agent-rag-refactor-foundation.md`.

The first implementation increment is intentionally scoped to `packages/evireview_core`: domain contracts, JSONL helpers, markdown section parsing, BM25 retrieval, section-routed hierarchical retrieval, heuristic verifier, evidence-aware ranker, and a deterministic review-audit workflow. API, worker, frontend, and Qdrant work remain separate follow-up plans so the current experiment sandbox is not disrupted.
```

- [ ] **Step 3: Run documentation grep**

Run:

```bash
rg -n "Refactor boundary|Core refactor implementation plan|packages/evireview_core" code/experiments/evireview_a/README.md docs/progress/evireview_current_progress_2026-05-30.md
```

Expected: lines in both files mention `packages/evireview_core`.

- [ ] **Step 4: Commit**

```bash
git add code/experiments/evireview_a/README.md docs/progress/evireview_current_progress_2026-05-30.md
git commit -m "Document the EviReview core refactor boundary" \
  -m "Experiment scripts stay reproducible while stable logic moves into a reusable core package for future API and frontend work." \
  -m "Constraint: Current experiment outputs and metrics remain unchanged" \
  -m "Confidence: high" \
  -m "Scope-risk: narrow" \
  -m "Tested: rg -n \"Refactor boundary|Core refactor implementation plan|packages/evireview_core\" code/experiments/evireview_a/README.md docs/progress/evireview_current_progress_2026-05-30.md"
```

---

### Task 11: Final Verification and Push

**Files:**
- Verify all files from Tasks 1-10.

- [ ] **Step 1: Run full unittest suite**

Run:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest discover -s tests/evireview_core -v
```

Expected: all tests pass.

- [ ] **Step 2: Run compile check**

Run:

```bash
python3 -m compileall -q packages/evireview_core tests/evireview_core
```

Expected: exit status `0`, no output.

- [ ] **Step 3: Run diff whitespace check**

Run:

```bash
git diff --check
```

Expected: exit status `0`, no output.

- [ ] **Step 4: Run secret scan**

Run:

```bash
python3 - <<'PY'
from __future__ import annotations

import os
import re
import sys

patterns = [
    "90" + "a4" + "ea" + "1b",
    "l1VFY" + "HX2E6k" + "Chsjm",
    "GL" + "M" + r"_API_KEY=.*[A-Za-z0-9]",
    "ZHI" + "PU" + r".*90" + "a4",
    "ZA" + "I" + r"_API_KEY=.*[A-Za-z0-9]",
]
combined = re.compile("|".join(patterns))
matches: list[str] = []
for root, dirs, files in os.walk("."):
    dirs[:] = [name for name in dirs if name not in {".git", ".omx"}]
    for name in files:
        path = os.path.join(root, name)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                for line_number, line in enumerate(handle, start=1):
                    if combined.search(line):
                        matches.append(f"{path}:{line_number}")
        except OSError:
            continue
if matches:
    print("\n".join(matches))
    sys.exit(1)
PY
```

Expected: exit status `0`, no output.

- [ ] **Step 5: Inspect final diff summary**

Run:

```bash
git status --short
git log --oneline -8
```

Expected: working tree clean after the final commit; recent commits should correspond to the tasks above.

- [ ] **Step 6: Push**

Run:

```bash
git push
```

Expected: remote `main` updates successfully.

## Plan Self-review

Coverage:

- Domain schema: Task 2.
- JSONL and markdown helpers: Task 3.
- BM25 retrieval: Task 4.
- Section-routed hierarchical retrieval: Task 5.
- Heuristic verifier and silver metric boundary: Task 6.
- Evidence-aware ranker: Task 7.
- Deterministic Agent-RAG workflow: Task 8.
- Fixture regression: Task 9.
- Experiment/core boundary docs: Task 10.
- Verification and push: Task 11.

The plan intentionally does not implement API, worker, frontend, or Qdrant because those are separate subsystems and need their own implementation plans after the core package exists.
