def mean_absolute_error(gold: list[int], predicted: list[int]) -> float:
    if not gold or len(gold) != len(predicted):
        raise ValueError("gold and predicted must be non-empty and equally sized")
    return sum(abs(left - right) for left, right in zip(gold, predicted, strict=True)) / len(
        gold
    )


def macro_f1(gold: list[str], predicted: list[str], *, labels: list[str]) -> float:
    if len(gold) != len(predicted):
        raise ValueError("gold and predicted must be equally sized")
    return sum(_binary_f1(gold, predicted, label) for label in labels) / len(labels)


def multilabel_macro_f1(
    gold: list[set[str]],
    predicted: list[set[str]],
    *,
    labels: list[str],
) -> float:
    if len(gold) != len(predicted):
        raise ValueError("gold and predicted must be equally sized")
    scores = []
    for label in labels:
        binary_gold = [label if label in values else "__negative__" for values in gold]
        binary_predicted = [
            label if label in values else "__negative__" for values in predicted
        ]
        scores.append(_binary_f1(binary_gold, binary_predicted, label))
    return sum(scores) / len(scores)


def _binary_f1(gold: list[str], predicted: list[str], positive: str) -> float:
    true_positive = sum(
        left == positive and right == positive
        for left, right in zip(gold, predicted, strict=True)
    )
    false_positive = sum(
        left != positive and right == positive
        for left, right in zip(gold, predicted, strict=True)
    )
    false_negative = sum(
        left == positive and right != positive
        for left, right in zip(gold, predicted, strict=True)
    )
    denominator = 2 * true_positive + false_positive + false_negative
    return 0.0 if denominator == 0 else 2 * true_positive / denominator
