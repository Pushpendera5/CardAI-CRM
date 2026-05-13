def test_contact_crud(client, auth_headers):
    create = client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={"name": "Rahul Sharma", "company_name": "ABC Technologies", "mobile": "9876543210", "email": "rahul@example.com"},
    )
    assert create.status_code == 201
    contact_id = create.json()["data"]["id"]

    listing = client.get("/api/v1/contacts?search=Rahul", headers=auth_headers)
    assert listing.status_code == 200
    assert listing.json()["data"]["total"] == 1

    update = client.put(f"/api/v1/contacts/{contact_id}", headers=auth_headers, json={"notes": "Met at expo"})
    assert update.status_code == 200
    assert update.json()["data"]["notes"] == "Met at expo"

    delete = client.delete(f"/api/v1/contacts/{contact_id}", headers=auth_headers)
    assert delete.status_code == 200

