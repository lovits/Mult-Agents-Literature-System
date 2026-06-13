import argparse
import hashlib
import json
from pathlib import Path

import httpx

from evireview.dao.source_clients import parse_arxiv_entries


API_URL = "https://export.arxiv.org/api/query"


def download_snapshot(category: str, limit: int, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    client = httpx.Client(timeout=120, follow_redirects=True, headers={"User-Agent": "EviReview-Lite/0.1"})
    response = client.get(
        API_URL,
        params={
            "search_query": f"cat:{category}",
            "start": 0,
            "max_results": limit,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        },
    )
    response.raise_for_status()
    entries = parse_arxiv_entries(response.text)
    for entry in entries:
        pdf_response = client.get(entry["pdf_url"])
        pdf_response.raise_for_status()
        pdf_path = output / "pdfs" / f"{entry['arxiv_id']}.pdf"
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_path.write_bytes(pdf_response.content)
        entry["local_pdf"] = str(pdf_path)
        entry["pdf_sha256"] = hashlib.sha256(pdf_response.content).hexdigest()
    metadata_path = output / "papers.json"
    metadata_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = {
        "source": API_URL,
        "category": category,
        "papers": len(entries),
        "selection": "latest_by_submitted_date",
        "supervision": "none; unseen demonstration only",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", default="cs.CL")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dataset/raw/demo/arxiv_unseen_2026-06-13"),
    )
    args = parser.parse_args()
    print(json.dumps(download_snapshot(args.category, args.limit, args.output), indent=2))


if __name__ == "__main__":
    main()
