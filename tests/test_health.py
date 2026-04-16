def test_health_endpoint_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_returns_ok(client):
    response = client.get("/health")
    assert response.json() == {"status": "ok"}
