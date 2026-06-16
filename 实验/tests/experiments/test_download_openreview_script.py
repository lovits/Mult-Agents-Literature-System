import json

import httpx

from scripts import download_openreview


class FakeResponse:
    def __init__(self, payload=None, content=b"", error=None):
        self.payload = payload
        self.content = content
        self.error = error

    def json(self):
        return self.payload

    def raise_for_status(self):
        if self.error:
            raise self.error


class FakeOpenReviewClient:
    def __init__(self, *args, **kwargs):
        pass

    def get(self, url, params=None):
        if params and "content.venueid" in params:
            return FakeResponse(
                {
                    "notes": [
                        {
                            "id": "paper-1",
                            "forum": "forum-1",
                            "license": "CC BY 4.0",
                            "content": {
                                "title": {"value": "Paper"},
                                "abstract": {"value": "Abstract"},
                                "pdf": {"value": "/pdf/paper-1"},
                            },
                        }
                    ]
                }
            )
        if params and params.get("forum") == "forum-1":
            return FakeResponse(
                {
                    "notes": [
                        {
                            "id": "review-1",
                            "invitations": ["ICLR.cc/2025/Conference/Submission1/Official_Review"],
                            "content": {"weaknesses": {"value": "Missing ablation."}},
                        }
                    ]
                }
            )
        request = httpx.Request("GET", url)
        response = httpx.Response(429, request=request)
        return FakeResponse(
            error=httpx.HTTPStatusError("rate limited", request=request, response=response)
        )


def test_valid_pdf_requires_pdf_header_and_nontrivial_size(tmp_path):
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-" + b"x" * 1_001)
    text = tmp_path / "paper.txt"
    text.write_text("not a pdf", encoding="utf-8")

    assert download_openreview.valid_pdf(pdf) is True
    assert download_openreview.valid_pdf(text) is False
    assert download_openreview.valid_pdf(tmp_path / "missing.pdf") is False


def test_download_snapshot_records_pdf_failures_without_aborting(tmp_path, monkeypatch):
    monkeypatch.setattr(download_openreview.httpx, "Client", FakeOpenReviewClient)

    manifest = download_openreview.download_snapshot(
        "ICLR.cc/2025/Conference",
        limit=1,
        output=tmp_path,
        download_pdfs=True,
    )

    assert manifest["papers"] == 1
    assert manifest["official_reviews"] == 1
    assert manifest["valid_pdfs"] == 0
    assert manifest["pdf_failures"] == 1

    submissions = json.loads((tmp_path / "submissions_with_reviews.json").read_text(encoding="utf-8"))
    assert submissions[0]["pdf_status"] == "failed"
    assert "pdf_error" in submissions[0]
