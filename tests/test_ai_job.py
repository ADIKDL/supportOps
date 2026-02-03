from sqlalchemy import select

from app.models.org import Org


def test_ai_triage_job_creates_insight(client, db_session):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "admin4@example.com", "password": "password123", "org_name": "West"},
    )
    token = response.json()["access_token"]

    org = db_session.scalar(select(Org).where(Org.name == "West"))
    assert org is not None

    headers = {"Authorization": f"Bearer {token}"}

    create = client.post(
        f"/api/v1/orgs/{org.id}/tickets",
        json={"subject": "Urgent bug", "body": "App crashes", "priority": "urgent"},
        headers=headers,
    )
    ticket_id = create.json()["id"]

    triage = client.post(
        f"/api/v1/orgs/{org.id}/tickets/{ticket_id}/ai/triage",
        headers=headers,
    )
    assert triage.status_code == 200

    get_insight = client.get(
        f"/api/v1/orgs/{org.id}/tickets/{ticket_id}/ai/triage",
        headers=headers,
    )
    assert get_insight.status_code == 200
    data = get_insight.json()
    assert data["category"]
    assert data["urgency_score"]
