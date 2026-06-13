from evireview.dao.dataset_dao import DatasetRegistry


def test_required_dataset_roles_and_sources_are_registered():
    registry = DatasetRegistry.from_yaml("conf/experiments/e0_data.yaml")

    assert {
        "nlpeer",
        "openreview",
        "peerqa",
        "claimcheck",
        "reviewcritique",
        "local_literature",
        "arxiv_unseen",
    } <= set(registry.names())
    assert {
        "raw_primary",
        "strict_evaluation",
        "literature_corpus",
        "unseen_demo",
    } <= set(registry.roles())
    assert all(item.source_url and item.supervision and item.local_path for item in registry.items)


def test_restricted_dataset_is_not_reported_as_downloaded():
    registry = DatasetRegistry.from_yaml("conf/experiments/e0_data.yaml")
    nlpeer = registry.by_name("nlpeer")

    assert nlpeer.access == "restricted"
    assert nlpeer.download_status == "requires_application"
