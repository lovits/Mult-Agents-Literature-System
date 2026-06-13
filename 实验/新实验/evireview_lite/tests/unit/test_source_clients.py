from evireview.dao.source_clients import (
    flatten_openreview_content,
    parse_arxiv_entries,
    select_official_reviews,
)


def test_openreview_content_value_wrappers_are_flattened():
    content = {
        "title": {"value": "A paper"},
        "keywords": {"value": ["retrieval", "agents"]},
    }

    assert flatten_openreview_content(content) == {
        "title": "A paper",
        "keywords": ["retrieval", "agents"],
    }


def test_only_official_reviews_are_selected():
    notes = [
        {"invitations": ["ICLR.cc/2025/Conference/-/Official_Review"], "id": "r1"},
        {"invitations": ["ICLR.cc/2025/Conference/-/Comment"], "id": "c1"},
    ]

    assert [note["id"] for note in select_official_reviews(notes)] == ["r1"]


def test_arxiv_entries_preserve_pdf_and_identifier():
    xml = """<?xml version="1.0"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>http://arxiv.org/abs/2606.13681v1</id>
        <title>New Paper</title>
        <published>2026-06-11T17:59:59Z</published>
        <link href="https://arxiv.org/pdf/2606.13681v1" type="application/pdf"/>
      </entry>
    </feed>"""

    assert parse_arxiv_entries(xml)[0] == {
        "arxiv_id": "2606.13681v1",
        "title": "New Paper",
        "published": "2026-06-11T17:59:59Z",
        "pdf_url": "https://arxiv.org/pdf/2606.13681v1",
    }
