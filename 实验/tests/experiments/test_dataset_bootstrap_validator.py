from scripts.validate_dataset_bootstrap import validate


def test_dataset_bootstrap_passes_only_with_all_four_data_layers():
    result = validate()

    assert result["status"] == "passed"
    assert result["passed"] is True
    assert result["checks"]["raw_primary"]["passed"] is True
    assert result["checks"]["strict_evaluation"]["passed"] is True
    assert result["checks"]["strict_evaluation"]["substanreview_reviews"] == 550
    assert result["checks"]["literature_corpus"]["passed"] is True
    assert result["checks"]["unseen_demo"]["passed"] is True
    assert result["checks"]["clean_dataset_layout"]["passed"] is True
