from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.http import ExperimentManifestInput


router = APIRouter()


def _not_found(exc: KeyError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/experiments", status_code=status.HTTP_201_CREATED)
def create_experiment(payload: ExperimentManifestInput, request: Request) -> dict[str, Any]:
    return request.app.state.experiment_service.create(
        payload.name,
        payload.dataset_name,
        payload.dataset_version,
        payload.config,
    )


@router.get("/experiments")
def list_experiments(request: Request) -> list[dict[str, Any]]:
    return request.app.state.experiment_service.list()


@router.get("/experiments/{manifest_id}")
def get_experiment(manifest_id: str, request: Request) -> dict[str, Any]:
    try:
        return request.app.state.experiment_service.get(manifest_id)
    except KeyError as exc:
        raise _not_found(exc) from exc


@router.post("/experiments/{manifest_id}/runs/{run_id}")
def attach_experiment_run(manifest_id: str, run_id: str, request: Request) -> dict[str, Any]:
    try:
        return request.app.state.experiment_service.attach_run(manifest_id, run_id)
    except KeyError as exc:
        raise _not_found(exc) from exc
