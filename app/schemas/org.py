from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OrgOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime


class MetricsResponse(BaseModel):
    by_status: dict[str, int]
    by_category: dict[str, int]
    sla: dict[str, int]
