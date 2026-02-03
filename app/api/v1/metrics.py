from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_db, require_org_roles
from app.models.enums import RoleEnum
from app.schemas.org import MetricsResponse
from app.services import metrics_service

router = APIRouter(prefix="/orgs/{org_id}/metrics", tags=["metrics"])


@router.get("", response_model=MetricsResponse)
def org_metrics(
    org_id: int,
    db=Depends(get_db),
    membership=Depends(require_org_roles([RoleEnum.admin])),
):
    return metrics_service.get_metrics(db, org_id)
