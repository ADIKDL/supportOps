from __future__ import annotations

from typing import Any

import redis
from rq import Queue, Retry

from app.core.config import settings
from app.jobs.triage_ticket import triage_ticket_job

_retry_policy = Retry(max=3, interval=[10, 30, 90])
_redis = None


def get_queue() -> Queue:
    global _redis
    if _redis is None:
        _redis = redis.Redis.from_url(settings.redis_url)
    return Queue(
        "default",
        connection=_redis,
        default_timeout=settings.rq_job_timeout,
        is_async=settings.rq_async,
    )


def enqueue_triage(ticket_id: int, org_id: int, actor_id: int) -> dict[str, Any]:
    if settings.testing:
        triage_ticket_job(ticket_id=ticket_id, org_id=org_id, actor_id=actor_id)
        return {"status": "completed", "job_id": None}

    queue = get_queue()
    job = queue.enqueue(
        triage_ticket_job,
        ticket_id=ticket_id,
        org_id=org_id,
        actor_id=actor_id,
        retry=_retry_policy,
    )
    return {"status": "queued", "job_id": job.id}
