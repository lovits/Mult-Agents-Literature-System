import json
from pathlib import Path

from evireview.models.evidence import EvidenceBlock
from evireview.models.weakness import QueryPlan
from evireview.rag.paper_rag import PaperRAG, PaperRAGConfig


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parent
EXPECTED_DESIGN_DOCUMENTS = {"最新开题报告.md", "设计方案.md", "实验方案.md"}


def task6_smoke_test() -> bool:
    blocks = [
        EvidenceBlock(
            block_id="intro",
            paper_id="p1",
            section="introduction",
            evidence_type="paragraph",
            text="We introduce a retrieval module.",
            ordinal=0,
        ),
        EvidenceBlock(
            block_id="ablation",
            paper_id="p1",
            section="ablation",
            evidence_type="table_caption",
            text="Table 1: Retrieval module ablation.",
            ordinal=1,
        ),
    ]
    plan = QueryPlan(
        candidate_id="w1",
        aspect="experiment",
        keyword_queries=["retrieval module ablation"],
        semantic_query="retrieval module ablation",
        expected_sections=["ablation"],
        expected_evidence_types=["table_caption"],
        literature_required=False,
    )
    vectors = {
        blocks[0].text: [1.0, 0.0],
        blocks[1].text: [0.8, 0.2],
        plan.semantic_query: [1.0, 0.0],
    }
    result = PaperRAG(blocks, embed=lambda text: vectors[text]).retrieve(
        plan,
        PaperRAGConfig(mode="P4", top_k=1),
    )
    return result.items[0].evidence_id == "ablation"


def validate() -> dict:
    design_files = {
        path.name for path in (REPO_ROOT / "设计方案").iterdir() if path.is_file()
    }
    forbidden_layouts = [
        EXPERIMENT_ROOT / "新实验",
        EXPERIMENT_ROOT / "evireview_lite",
    ]
    forbidden_tree_paths = [
        EXPERIMENT_ROOT / "新实验",
        EXPERIMENT_ROOT / "evireview_lite",
        EXPERIMENT_ROOT / "dataset/legacy_sources",
        EXPERIMENT_ROOT / "dataset/manifests",
    ]
    expected_source_layers = {
        "agent",
        "conf",
        "dao",
        "evaluation",
        "models",
        "rag",
        "service",
    }
    source_layers = {
        path.name
        for path in (EXPERIMENT_ROOT / "src/evireview").iterdir()
        if path.is_dir() and path.name != "__pycache__"
    }
    expected_dataset_roles = {"primary", "evaluation", "literature", "demo", "restricted"}
    dataset_roles = {
        path.name
        for path in (EXPERIMENT_ROOT / "dataset/raw").iterdir()
        if path.is_dir()
    }
    checks = {
        "flat_experiment_layout": {
            "passed": all(not path.exists() for path in forbidden_layouts)
            and (EXPERIMENT_ROOT / "src").exists()
            and (EXPERIMENT_ROOT / "tests").exists(),
            "forbidden_paths": [str(path) for path in forbidden_layouts],
        },
        "three_design_documents": {
            "passed": design_files == EXPECTED_DESIGN_DOCUMENTS,
            "files": sorted(design_files),
        },
        "paper_rag_task6": {
            "passed": task6_smoke_test(),
            "components": [
                "section_prior",
                "evidence_type_prior",
                "neighbor_expansion",
                "P2_P3_P4_ablation",
            ],
        },
        "clean_experiment_tree": {
            "passed": (
                all(not path.exists() for path in forbidden_tree_paths)
                and source_layers == expected_source_layers
                and dataset_roles == expected_dataset_roles
            ),
            "forbidden_paths": [str(path) for path in forbidden_tree_paths],
            "source_layers": sorted(source_layers),
            "dataset_roles": sorted(dataset_roles),
        },
    }
    passed = all(check["passed"] for check in checks.values())
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": "Flat experiment layout and Task 6 Paper-RAG are validated.",
        "checks": checks,
    }


def main() -> None:
    result = validate()
    output = REPO_ROOT / ".omx/specs/autoresearch-flat-layout-task6/result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
