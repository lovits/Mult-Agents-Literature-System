import argparse
import hashlib
import json
import time
from pathlib import Path

import httpx

from evireview.dao.source_clients import parse_arxiv_entries


API_URL = "https://export.arxiv.org/api/query"
RETRYABLE_EXCEPTIONS = (
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadError,
    httpx.ReadTimeout,
    httpx.RemoteProtocolError,
)


def get_with_retries(client: httpx.Client, url: str, *, params: dict | None = None) -> httpx.Response:
    last_error = None
    for attempt in range(3):
        try:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response
        except RETRYABLE_EXCEPTIONS as exc:
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    if last_error is not None:
        raise last_error
    response = client.get(url, params=params)
    response.raise_for_status()
    return response


def download_snapshot(category: str, limit: int, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    client = httpx.Client(timeout=120, follow_redirects=True, headers={"User-Agent": "EviReview-Lite/0.1"})
    response = get_with_retries(
        client,
        API_URL,
        params={
            "search_query": f"cat:{category}",
            "start": 0,
            "max_results": limit,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        },
    )
    entries = parse_arxiv_entries(response.text)
    failures = []
    for entry in entries:
        pdf_path = output / "pdfs" / f"{entry['arxiv_id']}.pdf"
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            pdf_response = get_with_retries(client, entry["pdf_url"])
            pdf_path.write_bytes(pdf_response.content)
            entry["local_pdf"] = str(pdf_path)
            entry["pdf_sha256"] = hashlib.sha256(pdf_response.content).hexdigest()
            entry["pdf_status"] = "downloaded"
        except httpx.HTTPError as exc:
            entry["pdf_status"] = "failed"
            entry["pdf_error"] = str(exc)
            failures.append({"arxiv_id": entry["arxiv_id"], "error": str(exc)})
    metadata_path = output / "papers.json"
    metadata_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = {
        "source": API_URL,
        "category": category,
        "papers": len(entries),
        "valid_pdfs": sum(entry.get("pdf_status") == "downloaded" for entry in entries),
        "pdf_failures": len(failures),
        "failures": failures,
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
