from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.http import CreatedRunResponse, ReviewAuditInput
from app.services.review_audit_service import QueueDeliveryError


router = APIRouter()


def _not_found(exc: KeyError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/runs/review-audit", status_code=status.HTTP_202_ACCEPTED, response_model=CreatedRunResponse)
def create_review_audit(payload: ReviewAuditInput, request: Request) -> dict[str, Any]:
    try:
        return request.app.state.service.create_and_enqueue(payload.to_request())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
    except QueueDeliveryError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="queue unavailable") from exc


@router.get("/runs/{run_id}")
def get_run(run_id: str, request: Request) -> dict[str, Any]:
    try:
        return request.app.state.service.get_run(run_id)
    except KeyError as exc:
        raise _not_found(exc) from exc


@router.get("/runs/{run_id}/findings")
def get_findings(run_id: str, request: Request) -> list[dict[str, Any]]:
    try:
        return request.app.state.service.get_findings(run_id)
    except KeyError as exc:
        raise _not_found(exc) from exc


@router.get("/runs/{run_id}/trace")
def get_trace(run_id: str, request: Request) -> list[dict[str, Any]]:
    try:
        return request.app.state.service.get_trace(run_id)
    except KeyError as exc:
        raise _not_found(exc) from exc


@router.get("/runs/{run_id}/agent-trace")
def get_agent_trace(run_id: str, request: Request) -> list[dict[str, Any]]:
    try:
        return request.app.state.service.get_agent_trace(run_id)
    except KeyError as exc:
        raise _not_found(exc) from exc


@router.get("/runs/{run_id}/workspace")
def get_workspace(run_id: str, request: Request) -> dict[str, Any]:
    try:
        return request.app.state.service.get_workspace(run_id)
    except KeyError as exc:
        raise _not_found(exc) from exc


@router.get("/jobs/{job_id}")
def get_job(job_id: str, request: Request) -> dict[str, Any]:
    try:
        return request.app.state.service.get_job(job_id)
    except KeyError as exc:
        raise _not_found(exc) from exc
