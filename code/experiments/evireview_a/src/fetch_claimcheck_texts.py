from __future__ import annotations

import urllib.error
import urllib.request

from common import DATA_DIR, ensure_dirs, sha256_file, write_json


REPO = "https://github.com/JHU-CLSP/CLAIMCHECK"
RAW_BASE = "https://raw.githubusercontent.com/JHU-CLSP/CLAIMCHECK/main"
FILES = {
    "README.md": f"{RAW_BASE}/README.md",
    "source_pilot.json": f"{RAW_BASE}/data/texts/source/pilot.json",
    "source_main.json": f"{RAW_BASE}/data/texts/source/main.json",
}
LICENSE_URLS = (
    f"{RAW_BASE}/LICENSE",
    f"{RAW_BASE}/LICENSE.md",
    "https://api.github.com/repos/JHU-CLSP/CLAIMCHECK/license",
)


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()


def detect_license() -> dict[str, str]:
    for url in LICENSE_URLS:
        try:
            payload = fetch(url)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                continue
            raise
        if payload:
            return {"status": "found", "url": url}
    return {
        "status": "not_found",
        "note": "No LICENSE file or GitHub license endpoint was found on 2026-05-30; raw text files are kept out of git.",
    }


def main() -> None:
    ensure_dirs()
    out_dir = DATA_DIR / "claimcheck_raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = []
    for name, url in FILES.items():
        out_path = out_dir / name
        payload = fetch(url)
        out_path.write_bytes(payload)
        files.append(
            {
                "name": name,
                "url": url,
                "bytes": out_path.stat().st_size,
                "sha256": sha256_file(out_path),
            }
        )
        print(f"Wrote {out_path} bytes={len(payload)}")

    write_json(
        DATA_DIR / "claimcheck_raw_manifest.json",
        {
            "dataset": "CLAIMCHECK",
            "source_repository": REPO,
            "paper": "https://aclanthology.org/2025.findings-emnlp.1185/",
            "license": detect_license(),
            "files": files,
        },
    )


if __name__ == "__main__":
    main()
