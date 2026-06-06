from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.http import CreatedRunResponse, PaperImportInput, PersistedPaperReviewAuditInput
from app.services.review_audit_service import QueueDeliveryError


router = APIRouter()


def _not_found(exc: KeyError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/papers/import", status_code=status.HTTP_201_CREATED)
def import_paper(payload: PaperImportInput, request: Request) -> dict[str, Any]:
    try:
        return request.app.state.paper_service.import_markdown(payload.paper_id, payload.title, payload.markdown)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc


@router.get("/papers")
def list_papers(request: Request) -> list[dict[str, Any]]:
    return request.app.state.paper_service.list_papers()


@router.get("/papers/{paper_id}")
def get_paper(paper_id: str, request: Request) -> dict[str, Any]:
    try:
        return request.app.state.paper_service.get_paper(paper_id)
    except KeyError as exc:
        raise _not_found(exc) from exc


@router.get("/papers/{paper_id}/runs")
def list_paper_runs(paper_id: str, request: Request) -> list[dict[str, Any]]:
    try:
        return request.app.state.service.list_runs_for_paper(paper_id)
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


@router.get("/papers/{paper_id}/versions")
def list_paper_versions(paper_id: str, request: Request) -> list[dict[str, Any]]:
    try:
        return request.app.state.paper_service.list_versions(paper_id)
    except KeyError as exc:
        raise _not_found(exc) from exc


@router.get("/papers/{paper_id}/versions/{version_id}/evidence-blocks")
def get_version_evidence_blocks(paper_id: str, version_id: str, request: Request) -> list[dict[str, Any]]:
    try:
        return request.app.state.paper_service.get_version_evidence_blocks(paper_id, version_id)
    except KeyError as exc:
        raise _not_found(exc) from exc


@router.post(
    "/papers/{paper_id}/review-audit",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=CreatedRunResponse,
)
def create_persisted_paper_review_audit(
    paper_id: str,
    payload: PersistedPaperReviewAuditInput,
    request: Request,
) -> dict[str, Any]:
    try:
        return request.app.state.service.create_from_paper_and_enqueue(
            paper_id,
            payload.to_weaknesses(),
            top_k=payload.top_k,
            finding_top_k=payload.finding_top_k,
            graph_profile=payload.graph_profile,
        )
    except KeyError as exc:
        raise _not_found(exc) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
    except QueueDeliveryError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="queue unavailable") from exc
