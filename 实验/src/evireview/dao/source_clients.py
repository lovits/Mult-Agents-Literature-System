from xml.etree import ElementTree


ATOM = "{http://www.w3.org/2005/Atom}"


def flatten_openreview_content(content: dict) -> dict:
    return {
        key: value.get("value") if isinstance(value, dict) and "value" in value else value
        for key, value in content.items()
    }


def select_official_reviews(notes: list[dict]) -> list[dict]:
    return [
        note
        for note in notes
        if any(invitation.endswith("/Official_Review") for invitation in note.get("invitations", []))
    ]


def parse_arxiv_entries(xml: str) -> list[dict[str, str]]:
    root = ElementTree.fromstring(xml)
    entries = []
    for entry in root.findall(f"{ATOM}entry"):
        identifier = entry.findtext(f"{ATOM}id", default="").rsplit("/", 1)[-1]
        title = " ".join(entry.findtext(f"{ATOM}title", default="").split())
        published = entry.findtext(f"{ATOM}published", default="")
        pdf_url = next(
            (
                link.attrib["href"]
                for link in entry.findall(f"{ATOM}link")
                if link.attrib.get("type") == "application/pdf"
            ),
            "",
        )
        entries.append(
            {
                "arxiv_id": identifier,
                "title": title,
                "published": published,
                "pdf_url": pdf_url,
            }
        )
    return entries
