import os
import pytest
from fastapi.testclient import TestClient
import unittest.mock as mock

from backend.main import app
from backend.models.database import Base, init_db, AsyncSessionLocal

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """
    Auto-run database initialization once for module level testing.
    """
    import asyncio
    asyncio.run(init_db())

def test_root_endpoint():
    """
    Test root health check route.
    """
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"
    assert "ResearchPilot" in response.json()["service"]

@mock.patch("backend.api.endpoints.run_research_pipeline")
def test_start_research_endpoint(mock_run_pipeline):
    """
    Test that starting research invokes database storage and launches background pipeline task.
    """
    # Setup mock to ignore actual background process execution
    mock_run_pipeline.return_value = None
    
    client = TestClient(app)
    
    # 1. Post request to trigger research
    payload = {"topic": "SOTA Quantum Deep Learning"}
    response = client.post("/api/research/start", json=payload)
    
    assert response.status_code == 200
    res_data = response.json()
    assert "job_id" in res_data
    assert res_data["status"] == "searching"
    
    job_id = res_data["job_id"]
    
    # 2. Get request to check status in SQLite
    status_response = client.get(f"/api/research/status/{job_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["id"] == job_id
    assert status_data["topic"] == "SOTA Quantum Deep Learning"
    assert status_data["status"] == "searching"
    assert status_data["progress_percentage"] == 15
