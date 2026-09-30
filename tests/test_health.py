def test_health_check(client):
    """Test standard health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_db_health_check(client):
    """Test database connectivity health check endpoint."""
    response = client.get("/api/v1/db-health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
