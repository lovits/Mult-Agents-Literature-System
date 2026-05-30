from __future__ import annotations

import urllib.request

from common import DATA_DIR, ensure_dirs, sha256_file, write_json


RAW_BASE = "https://raw.githubusercontent.com/YanzhuGuo/SubstanReview/main/annotation_final"
LICENSE_URL = "https://raw.githubusercontent.com/YanzhuGuo/SubstanReview/main/LICENSE"
FILES = ("train.jsonl", "test.jsonl")


def main() -> None:
    ensure_dirs()
    out_dir = DATA_DIR / "substanreview_raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = []
    for filename in FILES:
        url = f"{RAW_BASE}/{filename}"
        out_path = out_dir / filename
        with urllib.request.urlopen(url, timeout=30) as response:
            payload = response.read()
        out_path.write_bytes(payload)
        files.append(
            {
                "split": filename.removesuffix(".jsonl"),
                "url": url,
                "path": str(out_path.relative_to(DATA_DIR.parent.parent.parent.parent)),
                "bytes": out_path.stat().st_size,
                "sha256": sha256_file(out_path),
            }
        )
        print(f"Wrote {out_path} bytes={len(payload)}")

    license_path = out_dir / "LICENSE"
    with urllib.request.urlopen(LICENSE_URL, timeout=30) as response:
        license_payload = response.read()
    license_path.write_bytes(license_payload)
    print(f"Wrote {license_path} bytes={len(license_payload)}")

    write_json(
        DATA_DIR / "substanreview_raw_manifest.json",
        {
            "dataset": "SubstanReview",
            "source_repository": "https://github.com/YanzhuGuo/SubstanReview",
            "paper": "https://aclanthology.org/2023.findings-emnlp.684/",
            "license": {
                "type": "Apache-2.0",
                "url": LICENSE_URL,
                "path": str(license_path.relative_to(DATA_DIR.parent.parent.parent.parent)),
                "sha256": sha256_file(license_path),
            },
            "files": files,
        },
    )


if __name__ == "__main__":
    main()
