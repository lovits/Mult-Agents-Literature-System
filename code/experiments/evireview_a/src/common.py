from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[4]
DATASET_ROOT = REPO_ROOT / "code" / "dataset" / "prism_iclr2024_sample"
EXPERIMENT_ROOT = REPO_ROOT / "code" / "experiments" / "evireview_a"
DATA_DIR = EXPERIMENT_ROOT / "data"
REPORT_DIR = EXPERIMENT_ROOT / "reports"


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def rel_path(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def resolve_repo_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_stats(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "bytes": 0, "chars": 0, "sha256": ""}
    data = path.read_text(encoding="utf-8", errors="ignore")
    return {
        "exists": True,
        "bytes": path.stat().st_size,
        "chars": len(data),
        "sha256": sha256_file(path),
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9_+-]*|\d+(?:\.\d+)?", (text or "").lower())


def cosine_sparse(left: dict[str, float], right: dict[str, float]) -> float:
    if not left or not right:
        return 0.0
    if len(left) > len(right):
        left, right = right, left
    dot = sum(value * right.get(key, 0.0) for key, value in left.items())
    if dot == 0:
        return 0.0
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def split_atomic_items(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []

    items: list[str] = []
    current: list[str] = []
    bullet_re = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if current:
                items.append(" ".join(current).strip())
                current = []
            continue
        if bullet_re.match(line):
            if current:
                items.append(" ".join(current).strip())
            current = [bullet_re.sub("", line).strip()]
        else:
            current.append(line)
    if current:
        items.append(" ".join(current).strip())

    if len(items) <= 1 and len(text) > 450:
        pieces = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])", normalize_ws(text))
        items = [piece.strip() for piece in pieces if len(piece.strip()) >= 30]

    return [normalize_ws(item) for item in items if len(normalize_ws(item)) >= 20]


def classify_weakness_category(text: str) -> str:
    lower = text.lower()
    rules = [
        ("related_work", ["related work", "prior work", "citation", "cite", "novelty", "contribution"]),
        ("experiment", ["experiment", "evaluation", "baseline", "ablation", "result", "dataset", "metric"]),
        ("method", ["method", "approach", "model", "algorithm", "prompt", "framework", "formulation"]),
        ("reproducibility", ["reproduc", "implementation", "code", "hyperparameter", "closed source"]),
        ("clarity", ["unclear", "clarify", "confusing", "presentation", "explain", "motivation"]),
        ("validity", ["fair", "control", "bias", "spurious", "limitation", "validity"]),
    ]
    for category, keywords in rules:
        if any(keyword in lower for keyword in keywords):
            return category
    return "other"


def classify_section(section_path: str) -> str:
    lower = section_path.lower()
    rules = [
        ("abstract", ["abstract"]),
        ("introduction", ["introduction", "intro"]),
        ("related_work", ["related work", "background"]),
        ("method", ["method", "approach", "model", "framework", "algorithm", "preliminar"]),
        ("experiment", ["experiment", "evaluation", "result", "benchmark", "analysis", "ablation"]),
        ("limitation", ["limitation", "discussion", "future work"]),
        ("conclusion", ["conclusion"]),
        ("appendix", ["appendix", "supplement"]),
        ("reference", ["reference", "bibliography"]),
    ]
    for section_type, keywords in rules:
        if any(keyword in lower for keyword in keywords):
            return section_type
    return "other"


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
    return section_type in EXPECTED_SECTIONS_BY_CATEGORY.get(category, EXPECTED_SECTIONS_BY_CATEGORY["other"])


def section_prior(category: str, section_type: str) -> float:
    if section_alignment(category, section_type):
        return 1.0
    if section_type in {"reference", "appendix"}:
        return 0.15
    return 0.0


def infer_severity(text: str, source_section: str) -> str:
    lower = text.lower()
    if any(token in lower for token in ["main concern", "major", "significant", "not convincing", "lack of", "fails to"]):
        return "major"
    if source_section.lower() == "questions":
        return "minor_or_question"
    return "unknown"
