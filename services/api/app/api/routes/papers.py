from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.http import PaperImportInput


router = APIRouter()


def _not_found(exc: KeyError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/papers/import", status_code=status.HTTP_201_CREATED)
def import_paper(payload: PaperImportInput, request: Request) -> dict[str, Any]:
    try:
        return request.app.state.paper_service.import_markdown(payload.paper_id, payload.title, payload.markdown)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc


@router.get("/papers/{paper_id}")
def get_paper(paper_id: str, request: Request) -> dict[str, Any]:
    try:
        return request.app.state.paper_service.get_paper(paper_id)
    except KeyError as exc:
        raise _not_found(exc) from exc


@router.get("/papers/{paper_id}/sections")
def get_sections(paper_id: str, request: Request) -> list[dict[str, Any]]:
    try:
        return request.app.state.paper_service.get_sections(paper_id)
    except KeyError as exc:
        raise _not_found(exc) from exc


@router.get("/papers/{paper_id}/evidence-blocks")
def get_evidence_blocks(paper_id: str, request: Request) -> list[dict[str, Any]]:
    try:
        return request.app.state.paper_service.get_evidence_blocks(paper_id)
    except KeyError as exc:
        raise _not_found(exc) from exc
