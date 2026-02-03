from sqlalchemy import select

from app.core.security import create_access_token, hash_password
from app.models.enums import RoleEnum
from app.models.membership import Membership
from app.models.org import Org
from app.models.user import User


def test_customer_forbidden_on_metrics(client, db_session):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "admin3@example.com", "password": "password123", "org_name": "North"},
    )
    assert response.status_code == 200

    org = db_session.scalar(select(Org).where(Org.name == "North"))
    assert org is not None

    customer = User(email="customer@example.com", password_hash=hash_password("password123"))
    db_session.add(customer)
    db_session.flush()

    membership = Membership(user_id=customer.id, org_id=org.id, role=RoleEnum.customer)
    db_session.add(membership)
    db_session.commit()

    customer_token = create_access_token(customer.id)
    headers = {"Authorization": f"Bearer {customer_token}"}

    metrics = client.get(f"/api/v1/orgs/{org.id}/metrics", headers=headers)
    assert metrics.status_code == 403
