from scripts.validate_e4_baselines import validate


def test_e4_baselines_are_complete_reproducible_and_honestly_ranked():
    result = validate()

    assert result["passed"] is True
    assert result["checks"]["protocol"]["development_split"] == "pilot"
    assert result["checks"]["protocol"]["evaluation_split"] == "main"
    assert result["checks"]["association"]["evaluated"] == 91
    assert result["checks"]["association"]["excluded"] == 64
    assert result["checks"]["association"]["sample_results"] == 91
    assert result["metrics"]["strongest_association_system"] == "C1_bm25"
    assert result["metrics"]["C1_bm25_recall@5"] > 0.75
    assert result["checks"]["labeling"]["evaluated"] == 155
    assert result["next_experiment"] == "E4 A1-A4 evidence audit systems"
