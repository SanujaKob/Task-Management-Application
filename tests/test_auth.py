from fastapi.testclient import TestClient


def test_signup_login(client: TestClient):
    payload = {
        "email": "user@example.com",
        "full_name": "Test User",
        "password": "secret",
    }
    res = client.post("/auth/signup", json=payload)
    assert res.status_code == 201

    res = client.post(
        "/auth/login",
        data={"username": payload["email"], "password": payload["password"]},
    )
    assert res.status_code == 200
    token = res.json()["access_token"]
    assert token

    me = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == payload["email"]
