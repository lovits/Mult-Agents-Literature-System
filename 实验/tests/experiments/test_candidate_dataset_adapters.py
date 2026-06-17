import json

from evireview.dao.candidate_datasets import (
    coerce_review_list,
    detect_section,
    paper_from_neurips_record,
    peercheck_summary,
    reviewrebuttal_summary,
)


def test_neurips_record_builds_paper_document_with_reviews():
    record = {
        "paper_id": "n1",
        "year": 2023,
        "conference": "NeurIPS 2023",
        "accepted": True,
        "title": "A Test Paper",
        "abstract": "Abstract text.",
        "pdf_url": "https://openreview.net/pdf?id=n1",
        "paper_text": "\n".join(
            [
                "A Test Paper",
                "",
                "Abstract",
                "This paper studies retrieval augmented paper review.",
                "",
                "1 Introduction",
                "The introduction motivates automatic review.",
                "",
                "Experiments",
                "Table 1 reports ablation results.",
            ]
        ),
        "reviews": json.dumps(["Review one", "Review two"]),
    }

    paper = paper_from_neurips_record(record)

    assert paper.paper_id == "n1"
    assert paper.metadata["review_count"] == 2
    assert "abstract" in paper.sections
    assert "experiments" in paper.sections
    assert any(block.evidence_type == "table_caption" for block in paper.blocks)


def test_coerce_review_list_handles_encoded_lists_and_plain_text():
    assert coerce_review_list("[\"a\", \"b\"]") == ["a", "b"]
    assert coerce_review_list("plain review") == ["plain review"]
    assert coerce_review_list([{"score": 6}]) == ['{"score": 6}']


def test_neurips_section_detector_handles_numbered_and_latex_headings():
    assert detect_section("## 2 Technical Overview") == "method"
    assert detect_section("2 Preliminary") == "method"
    assert detect_section("1.2.3 Experimental Evaluation") == "experiments"
    assert detect_section(r"\\section{Related works}") == "related_work"
    assert detect_section("Broader Impact") == "discussion"
    assert detect_section("Acknowledgments") is None


def test_reviewrebuttal_and_peercheck_summaries(tmp_path):
    reviews_path = tmp_path / "reviews.json"
    reviews_path.write_text(
        json.dumps(
            [
                {
                    "paper_id": "p1",
                    "reviews": [{"review_content": "good"}, {"review_content": "bad"}],
                    "review_initial_ratings_unified": [6, 5],
                    "review_final_ratings_unified": [7],
                    "metareview": "accept",
                    "decision": "Accept",
                }
            ]
        ),
        encoding="utf-8",
    )
    peercheck_path = tmp_path / "peercheck.jsonl"
    peercheck_path.write_text(
        json.dumps(
            {
                "file": "p.pdf",
                "answer": "Weaknesses\n- issue【1:2†p.pdf】\nOverall Score: 6",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    review_summary = reviewrebuttal_summary(reviews_path)
    peercheck = peercheck_summary(peercheck_path)

    assert review_summary["papers"] == 1
    assert review_summary["reviews"] == 2
    assert review_summary["rating_records"] == 3
    assert peercheck["rows"] == 1
    assert peercheck["citation_markers"] == 1
    assert peercheck["weakness_sections"] == 1
