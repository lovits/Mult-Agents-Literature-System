from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel


class DatasetItem(BaseModel):
    name: str
    role: Literal[
        "raw_primary",
        "strict_evaluation",
        "literature_corpus",
        "unseen_demo",
    ]
    source_url: str
    local_path: str
    access: Literal["public", "restricted", "local"]
    license: str
    supervision: str
    download_status: Literal[
        "pending",
        "downloaded",
        "requires_application",
        "local_snapshot",
    ]
    usage: list[str]


class DatasetRegistry(BaseModel):
    items: list[DatasetItem]

    @classmethod
    def from_yaml(cls, path: str | Path) -> "DatasetRegistry":
        payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return cls.model_validate(payload)

    def names(self) -> list[str]:
        return [item.name for item in self.items]

    def roles(self) -> list[str]:
        return [item.role for item in self.items]

    def by_name(self, name: str) -> DatasetItem:
        return next(item for item in self.items if item.name == name)


def audit_registry(registry: DatasetRegistry, project_root: Path) -> dict:
    datasets: dict[str, dict] = {}
    status_counts = {
        "downloaded": 0,
        "requires_application": 0,
        "local_snapshot": 0,
        "pending": 0,
    }
    for item in registry.items:
        path = project_root / item.local_path
        files = [candidate for candidate in path.rglob("*") if candidate.is_file()] if path.exists() else []
        bytes_total = sum(candidate.stat().st_size for candidate in files)
        status_counts[item.download_status] += 1
        datasets[item.name] = {
            "role": item.role,
            "download_status": item.download_status,
            "path_exists": path.exists(),
            "files": len(files),
            "bytes": bytes_total,
            "usage": item.usage,
        }
    return {
        "summary": {
            "registered": len(registry.items),
            **status_counts,
        },
        "datasets": datasets,
    }
