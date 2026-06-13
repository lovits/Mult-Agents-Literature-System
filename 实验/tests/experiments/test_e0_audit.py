from pathlib import Path

from evireview.dao.dataset_dao import DatasetRegistry, audit_registry


def test_e0_audit_separates_downloaded_restricted_and_local_sources():
    registry = DatasetRegistry.from_yaml("conf/experiments/e0_data.yaml")
    audit = audit_registry(registry, Path("."))

    assert audit["summary"]["registered"] == 7
    assert audit["summary"]["downloaded"] == 5
    assert audit["summary"]["requires_application"] == 1
    assert audit["summary"]["local_snapshot"] == 1
    assert audit["datasets"]["openreview"]["files"] >= 12
    assert audit["datasets"]["peerqa"]["files"] >= 5
