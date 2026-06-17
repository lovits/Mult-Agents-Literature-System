import argparse
import hashlib
import json
import time
from pathlib import Path

import httpx

from evireview.dao.source_clients import flatten_openreview_content, select_official_reviews


API_BASE = "https://api2.openreview.net"
RETRYABLE_EXCEPTIONS = (
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadError,
    httpx.ReadTimeout,
    httpx.RemoteProtocolError,
)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def valid_pdf(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 1_000 and path.read_bytes()[:5] == b"%PDF-"


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


def download_snapshot(venue: str, limit: int, output: Path, download_pdfs: bool) -> dict:
    client = httpx.Client(timeout=90, follow_redirects=True, headers={"User-Agent": "EviReview-Lite/0.1"})
    response = get_with_retries(
        client,
        f"{API_BASE}/notes",
        params={"content.venueid": venue, "limit": limit},
    )
    submissions = response.json()["notes"]
    records = []
    note_failures = []
    for note in submissions:
        try:
            forum_response = get_with_retries(
                client,
                f"{API_BASE}/notes",
                params={"forum": note["forum"], "limit": 1000},
            )
            reviews = select_official_reviews(forum_response.json()["notes"])
            review_status = "ok"
            review_error = None
        except httpx.HTTPError as exc:
            reviews = []
            review_status = "failed"
            review_error = str(exc)
            note_failures.append({"paper_id": note["id"], "stage": "forum_notes", "error": str(exc)})
        record = {
            "paper_id": note["id"],
            "forum": note["forum"],
            "license": note.get("license"),
            "content": flatten_openreview_content(note["content"]),
            "review_fetch_status": review_status,
            "reviews": [
                {
                    "id": review["id"],
                    "content": flatten_openreview_content(review["content"]),
                }
                for review in reviews
            ],
        }
        if review_error:
            record["review_fetch_error"] = review_error
        if download_pdfs:
            pdf_path = record["content"].get("pdf")
            if pdf_path:
                local_pdf = output / "pdfs" / f"{note['id']}.pdf"
                local_pdf.parent.mkdir(parents=True, exist_ok=True)
                if valid_pdf(local_pdf):
                    record["local_pdf"] = str(local_pdf)
                    record["pdf_status"] = "cached"
                else:
                    try:
                        pdf_response = get_with_retries(client, f"{API_BASE}{pdf_path}")
                        local_pdf.write_bytes(pdf_response.content)
                        record["local_pdf"] = str(local_pdf)
                        record["pdf_status"] = "downloaded"
                    except httpx.HTTPError as exc:
                        record["pdf_status"] = "failed"
                        record["pdf_error"] = str(exc)
                        note_failures.append({"paper_id": note["id"], "stage": "pdf", "error": str(exc)})
        records.append(record)
    snapshot_path = output / "submissions_with_reviews.json"
    write_json(snapshot_path, records)
    manifest = {
        "source": API_BASE,
        "api_version": 2,
        "venue": venue,
        "requested_limit": limit,
        "papers": len(records),
        "official_reviews": sum(len(record["reviews"]) for record in records),
        "review_fetch_failures": sum(record.get("review_fetch_status") == "failed" for record in records),
        "valid_pdfs": sum(
            valid_pdf(output / "pdfs" / f"{record['paper_id']}.pdf") for record in records
        ),
        "pdf_failures": sum(record.get("pdf_status") == "failed" for record in records),
        "failures": note_failures,
        "snapshot_sha256": sha256(snapshot_path),
    }
    write_json(output / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--venue", default="ICLR.cc/2025/Conference")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dataset/raw/primary/openreview_iclr2025_seed"),
    )
    parser.add_argument("--download-pdfs", action="store_true")
    args = parser.parse_args()
    print(json.dumps(download_snapshot(args.venue, args.limit, args.output, args.download_pdfs), indent=2))


if __name__ == "__main__":
    main()
