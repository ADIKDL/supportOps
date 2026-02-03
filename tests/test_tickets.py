from sqlalchemy import select

from app.models.org import Org


def test_create_and_list_tickets(client, db_session):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "admin2@example.com", "password": "password123", "org_name": "Zen"},
    )
    token = response.json()["access_token"]

    org = db_session.scalar(select(Org).where(Org.name == "Zen"))
    assert org is not None

    headers = {"Authorization": f"Bearer {token}"}

    create = client.post(
        f"/api/v1/orgs/{org.id}/tickets",
        json={"subject": "Login issue", "body": "Cannot sign in", "priority": "high"},
        headers=headers,
    )
    assert create.status_code == 200

    listing = client.get(
        f"/api/v1/orgs/{org.id}/tickets",
        headers=headers,
    )
    assert listing.status_code == 200
    data = listing.json()
    assert len(data["items"]) == 1
