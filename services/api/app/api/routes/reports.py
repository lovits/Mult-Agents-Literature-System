from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response, status


router = APIRouter()


def _not_found(exc: KeyError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/runs/{run_id}/report", status_code=status.HTTP_201_CREATED)
def create_report(run_id: str, request: Request) -> dict[str, Any]:
    try:
        return request.app.state.report_service.create_for_run(run_id)
    except KeyError as exc:
        raise _not_found(exc) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/reports/{report_id}")
def get_report(report_id: str, request: Request) -> dict[str, Any]:
    try:
        return request.app.state.report_service.get_report(report_id)
    except KeyError as exc:
        raise _not_found(exc) from exc


@router.get("/reports/{report_id}/markdown", response_class=Response)
def get_report_markdown(report_id: str, request: Request) -> Response:
    try:
        return Response(request.app.state.report_service.get_markdown(report_id), media_type="text/markdown")
    except (KeyError, FileNotFoundError) as exc:
        raise _not_found(KeyError(str(exc))) from exc
