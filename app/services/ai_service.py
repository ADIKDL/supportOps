from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.core.config import settings
from app.models.enums import AICategoryEnum
from app.models.ticket import Ticket

logger = logging.getLogger(__name__)


class TriagePayload(BaseModel):
    category: AICategoryEnum
    urgency_score: int = Field(ge=1, le=10)
    suggested_reply: str


class AIProvider:
    model_name: str

    def triage(self, ticket: Ticket) -> TriagePayload:
        raise NotImplementedError


class StubProvider(AIProvider):
    model_name = "stub"

    def triage(self, ticket: Ticket) -> TriagePayload:
        text = f"{ticket.subject} {ticket.body}".lower()
        if "bill" in text or "invoice" in text:
            category = AICategoryEnum.billing
        elif "bug" in text or "error" in text or "crash" in text:
            category = AICategoryEnum.bug
        elif "feature" in text or "request" in text:
            category = AICategoryEnum.feature
        else:
            category = AICategoryEnum.other

        if "urgent" in text or "asap" in text:
            urgency = 9
        elif "soon" in text:
            urgency = 6
        else:
            urgency = 3

        reply = (
            "Thanks for reaching out. We have logged your issue and will follow up "
            "shortly with next steps."
        )

        return TriagePayload(
            category=category,
            urgency_score=urgency,
            suggested_reply=reply,
        )


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model_name = model

    def triage(self, ticket: Ticket) -> TriagePayload:
        prompt = (
            "You are an AI support triage assistant. Return ONLY valid JSON that matches "
            'this schema: {"category": "billing|bug|feature|other", '
            '"urgency_score": 1-10, "suggested_reply": "..."}."'
        )
        user_content = (
            f"Subject: {ticket.subject}\n"
            f"Body: {ticket.body}\n"
            "Classify category, urgency_score (1-10), and suggested_reply."
        )
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.2,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=settings.ai_timeout_seconds) as client:
            response = client.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        parsed = _extract_json(content)
        return TriagePayload.model_validate(parsed)


def _extract_json(text: str) -> Any:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        lines = cleaned.splitlines()
        if lines and lines[0].strip().lower().startswith("json"):
            lines = lines[1:]
        cleaned = "\n".join(lines)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def get_provider() -> AIProvider:
    if settings.openai_api_key:
        return OpenAIProvider(settings.openai_api_key, settings.openai_model)
    return StubProvider()
