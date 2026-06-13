import argparse
import hashlib
import json
from pathlib import Path

import httpx

from evireview.dao.source_clients import flatten_openreview_content, select_official_reviews


API_BASE = "https://api2.openreview.net"


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def download_snapshot(venue: str, limit: int, output: Path, download_pdfs: bool) -> dict:
    client = httpx.Client(timeout=90, follow_redirects=True, headers={"User-Agent": "EviReview-Lite/0.1"})
    response = client.get(f"{API_BASE}/notes", params={"content.venueid": venue, "limit": limit})
    response.raise_for_status()
    submissions = response.json()["notes"]
    records = []
    for note in submissions:
        forum_response = client.get(f"{API_BASE}/notes", params={"forum": note["forum"], "limit": 1000})
        forum_response.raise_for_status()
        reviews = select_official_reviews(forum_response.json()["notes"])
        record = {
            "paper_id": note["id"],
            "forum": note["forum"],
            "license": note.get("license"),
            "content": flatten_openreview_content(note["content"]),
            "reviews": [
                {
                    "id": review["id"],
                    "content": flatten_openreview_content(review["content"]),
                }
                for review in reviews
            ],
        }
        if download_pdfs:
            pdf_path = record["content"].get("pdf")
            if pdf_path:
                pdf_response = client.get(f"{API_BASE}{pdf_path}")
                pdf_response.raise_for_status()
                local_pdf = output / "pdfs" / f"{note['id']}.pdf"
                local_pdf.parent.mkdir(parents=True, exist_ok=True)
                local_pdf.write_bytes(pdf_response.content)
                record["local_pdf"] = str(local_pdf)
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
