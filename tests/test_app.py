def register(client, email="test@example.com", password="Passw0rd!"):
    return client.post(
        "/register",
        data={"name": "Test User", "email": email, "password": password},
    )


def login(client, email="test@example.com", password="Passw0rd!"):
    return client.post("/login", data={"email": email, "password": password})


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_home_page_loads(client):
    assert client.get("/").status_code == 200


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_register_creates_user_and_rejects_duplicate(client):
    first = register(client)
    assert b"Registration successful" in first.data

    second = register(client)
    assert b"Email already registered" in second.data


def test_login_success_and_failure(client):
    register(client)

    login(client, password="wrong-password")
    with client.session_transaction() as sess:
        assert "user_id" not in sess

    login(client)
    with client.session_transaction() as sess:
        assert "user_id" in sess
