from scripts.validate_flat_layout_task6 import validate


def test_flat_layout_and_task6_are_complete():
    result = validate()

    assert result["status"] == "passed"
    assert result["passed"] is True
    assert result["checks"]["flat_experiment_layout"]["passed"] is True
    assert result["checks"]["three_design_documents"]["passed"] is True
    assert result["checks"]["paper_rag_task6"]["passed"] is True
