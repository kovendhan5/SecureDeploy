import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestRoot:
    """Tests for root endpoint"""

    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "SecureDeploy API"
        assert "version" in data
        assert data["version"] == "1.0.0"

    def test_root_contains_endpoints(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "endpoints" in data
        assert "health" in data["endpoints"]
        assert "metrics" in data["endpoints"]


class TestHealth:
    """Tests for health check endpoint"""

    def test_health_endpoint_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_ok_status(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"

    def test_health_endpoint_contains_timestamp(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        # Verify it's a valid ISO format timestamp
        from datetime import datetime
        try:
            datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
            is_valid_iso = True
        except ValueError:
            is_valid_iso = False
        assert is_valid_iso


class TestInfo:
    """Tests for info endpoint"""

    def test_info_endpoint(self):
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert "app" in data
        assert data["app"] == "SecureDeploy"
        assert "version" in data
        assert "environment" in data
        assert "timestamp" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
