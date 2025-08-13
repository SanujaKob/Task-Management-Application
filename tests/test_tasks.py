from fastapi.testclient import TestClient


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


def test_task_crud_flow(client: TestClient):
    headers = auth_headers(client)

    # Create
    res = client.post("/tasks/", json={"title": "Task 1"}, headers=headers)
    assert res.status_code == 201
    task_id = res.json()["id"]

    # Read
    res = client.get(f"/tasks/{task_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Task 1"

    # Update
    res = client.patch(
        f"/tasks/{task_id}",
        json={"status": "in_progress", "progress": 50},
        headers=headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "in_progress"
    assert body["progress"] == 50

    # Delete
    res = client.delete(f"/tasks/{task_id}", headers=headers)
    assert res.status_code == 204

    # Confirm deletion
    res = client.get(f"/tasks/{task_id}", headers=headers)
    assert res.status_code == 404
