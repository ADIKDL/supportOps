"""Model registry imports.

Importing this module ensures all models are registered on Base.metadata.
"""
from app.models.user import User  # noqa: F401
from app.models.org import Org  # noqa: F401
from app.models.membership import Membership  # noqa: F401
from app.models.ticket import Ticket  # noqa: F401
from app.models.comment import Comment  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.ai_ticket_insight import AITicketInsight  # noqa: F401
