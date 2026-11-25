from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_authenticated_analysis_and_private_history():
    client = TestClient(app)
    email = f"{uuid4().hex}@example.com"
    registered = client.post("/api/auth/register", json={"email": email, "password": "correct-horse-battery"})
    assert registered.status_code == 200
    token = registered.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/analyze/timeline", headers=headers, json={"statement": "I left at 8 pm. I arrived at 9 pm."})
    assert response.status_code == 200
    assert len(response.json()["metadata"]["timeline"]) == 2

    history = client.get("/api/history", headers=headers)
    assert history.status_code == 200
    assert history.json()[0]["analysis_type"] == "timeline"


def test_analysis_requires_authentication():
    response = TestClient(app).post("/api/analyze/statement", json={"statement": "A claim."})
    assert response.status_code == 401


def _register(client: TestClient) -> dict[str, str]:
    email = f"{uuid4().hex}@example.com"
    response = client.post("/api/auth/register", json={"email": email, "password": "correct-horse-battery"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_history_is_private_and_delete_is_owner_scoped():
    client = TestClient(app)
    owner = _register(client)
    other_user = _register(client)
    created = client.post("/api/analyze/statement", headers=owner, json={"statement": "A private claim."})
    analysis_id = created.json()["metadata"].get("analysis_id")
    assert created.status_code == 200

    owner_history = client.get("/api/history", headers=owner)
    assert owner_history.status_code == 200
    analysis_id = owner_history.json()[0]["id"]
    assert client.get(f"/api/history/{analysis_id}", headers=other_user).status_code == 404
    assert client.delete(f"/api/history/{analysis_id}", headers=other_user).status_code == 404
    assert client.delete(f"/api/history/{analysis_id}", headers=owner).status_code == 204


def test_invalid_input_and_upload_validation_are_rejected():
    client = TestClient(app)
    headers = _register(client)
    assert client.post("/api/analyze/statement", headers=headers, json={"statement": ""}).status_code == 422
    response = client.post("/api/analyze/evidence", headers=headers, data={"claim": "A claim"}, files={"evidence": ("bad.exe", b"not evidence", "application/octet-stream")})
    assert response.status_code == 400


def test_analysis_modes_and_valid_text_evidence():
    client = TestClient(app)
    headers = _register(client)
    conversation = client.post("/api/analyze/conversation", headers=headers, json={"statement": "Alice: I arrived at 8 pm.\n[8:30 pm] Bob: The meeting started at 9 pm."})
    assert conversation.status_code == 200
    assert [turn["speaker"] for turn in conversation.json()["metadata"]["turns"]] == ["Alice", "Bob"]

    comparison = client.post("/api/analyze/compare", headers=headers, json={"statement": "I left at 8 pm.", "previous_statements": ["I left at 7 pm."]})
    assert comparison.status_code == 200
    assert comparison.json()["metadata"]["versions"] == 2

    evidence = client.post("/api/analyze/evidence", headers=headers, data={"claim": "The note says hello."}, files={"evidence": ("note.txt", b"hello", "text/plain")})
    assert evidence.status_code == 200
    assert evidence.json()["extracted_text"] == "hello"


def test_login_rejects_wrong_password_and_duplicate_registration():
    client = TestClient(app)
    email = f"{uuid4().hex}@example.com"
    payload = {"email": email, "password": "correct-horse-battery"}
    assert client.post("/api/auth/register", json=payload).status_code == 200
    assert client.post("/api/auth/register", json=payload).status_code == 409
    assert client.post("/api/auth/login", json={"email": email, "password": "wrong-password"}).status_code == 401


def test_malformed_token_returns_unauthorized_instead_of_server_error():
    response = TestClient(app).get("/api/auth/profile", headers={"Authorization": "Bearer not.a.valid.token"})
    assert response.status_code == 401
