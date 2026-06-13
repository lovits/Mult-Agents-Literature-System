import argparse
import json
from pathlib import Path

from evireview.dao.dataset_dao import DatasetRegistry, audit_registry


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="conf/experiments/e0_data.yaml")
    parser.add_argument("--output", default="outputs/reports/e0_data_audit.json")
    args = parser.parse_args()

    registry = DatasetRegistry.from_yaml(args.config)
    audit = audit_registry(registry, Path("."))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(audit["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
