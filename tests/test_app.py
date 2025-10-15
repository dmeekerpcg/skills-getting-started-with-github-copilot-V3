"""
Tests for the FastAPI application
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_read_root():
    """Test root endpoint returns index.html"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]  # Verify we get HTML back

def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    # Check that we have activities in response
    assert len(data) > 0
    # Check structure of first activity
    first_activity = list(data.values())[0]
    assert all(key in first_activity for key in ["description", "schedule", "max_participants", "participants"])

def test_signup_for_activity_success():
    """Test successful activity signup"""
    # Get first activity name
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]
    
    # Try to sign up a new participant
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]

    # Verify participant was added
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity_name]["participants"]

def test_signup_for_activity_duplicate():
    """Test signing up same student twice fails"""
    # Get first activity name and participant
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]
    first_participant = activities[activity_name]["participants"][0]
    
    # Try to sign up existing participant
    response = client.post(f"/activities/{activity_name}/signup?email={first_participant}")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]

def test_signup_for_nonexistent_activity():
    """Test signing up for non-existent activity"""
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]

def test_unregister_from_activity_success():
    """Test successful unregistration from activity"""
    # Get first activity name and participant
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]
    first_participant = activities[activity_name]["participants"][0]
    
    # Try to unregister participant
    response = client.delete(f"/activities/{activity_name}/unregister?email={first_participant}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert first_participant in data["message"]
    assert activity_name in data["message"]

    # Verify participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert first_participant not in activities[activity_name]["participants"]

def test_unregister_nonexistent_participant():
    """Test unregistering non-existent participant"""
    # Get first activity name
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]
    
    response = client.delete(f"/activities/{activity_name}/unregister?email=nonexistent@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]

def test_unregister_from_nonexistent_activity():
    """Test unregistering from non-existent activity"""
    response = client.delete("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]