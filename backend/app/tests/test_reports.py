def test_reports_overview(client, auth_headers):
    response = client.get("/api/v1/reports/overview", headers=auth_headers)
    assert response.status_code == 200
    assert "total_scans" in response.json()["data"]

