from evireview.evaluation.e4_metrics import (
    macro_f1,
    mean_absolute_error,
    multilabel_macro_f1,
)


def test_mean_absolute_error_preserves_ordinal_distance():
    assert mean_absolute_error([1, 5], [2, 3]) == 1.5


def test_macro_f1_includes_unpredicted_classes():
    assert macro_f1(["a", "b"], ["a", "a"], labels=["a", "b"]) == 1 / 3


def test_multilabel_macro_f1_scores_each_weakness_type():
    gold = [{"insufficient"}, {"clarity"}]
    predicted = [{"insufficient"}, {"insufficient"}]

    assert multilabel_macro_f1(gold, predicted, labels=["insufficient", "clarity"]) == 1 / 3
