from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models.user_model import User
from app.models.notification_model import Notification


def auth_headers(client: TestClient):
    payload = {
        "email": "user@example.com",
        "full_name": "Test User",
        "password": "secret",
    }
    client.post("/auth/signup", json=payload)
    res = client.post(
        "/auth/login",
        data={"username": payload["email"], "password": payload["password"]},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_notification_read_flow(client: TestClient, db_session):
    headers = auth_headers(client)
    user = db_session.scalar(select(User).where(User.email == "user@example.com"))
    note = Notification(user_id=user.id, message="hello")
    db_session.add(note)
    db_session.commit()
    db_session.refresh(note)

    res = client.get("/notifications/", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["read_at"] is None

    res = client.post(f"/notifications/{note.id}/read", headers=headers)
    assert res.status_code == 204

    res = client.get("/notifications/", headers=headers)
    assert res.status_code == 200
    assert res.json()[0]["read_at"] is not None
