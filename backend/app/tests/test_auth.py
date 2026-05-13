def test_register_login_and_me(client):
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "full_name": "Test User", "password": "Password123!", "role": "User"},
    )
    assert register.status_code == 201
    assert register.json()["success"] is True

    login = client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "Password123!"})
    assert login.status_code == 200
    token = login.json()["data"]["access_token"]

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["data"]["email"] == "user@example.com"

