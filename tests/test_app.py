"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    initial_state = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball": {
            "description": "Learn basketball skills and compete in games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis training and friendly matches",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["sarah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and visual arts exploration",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["alice@mergington.edu", "lucas@mergington.edu"]
        },
        "Music Band": {
            "description": "Learn instruments and perform in concerts",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["grace@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Build and program robots for competitions",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu", "tyler@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["maya@mergington.edu"]
        }
    }
    
    # Clear and repopulate activities
    activities.clear()
    activities.update(initial_state)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(initial_state)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9
    
    def test_get_activities_contains_activity_details(self, client, reset_activities):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_has_correct_participants(self, client, reset_activities):
        """Test that participants list is correct"""
        response = client.get("/activities")
        data = response.json()
        
        assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]
        assert data["Programming Class"]["participants"] == ["emma@mergington.edu", "sophia@mergington.edu"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that duplicate signups are rejected"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test signing up multiple different students"""
        # Sign up first student
        response1 = client.post(
            "/activities/Tennis%20Club/signup?email=student1@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Sign up second student
        response2 = client.post(
            "/activities/Tennis%20Club/signup?email=student2@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both are in the activity
        activities_response = client.get("/activities")
        participants = activities_response.json()["Tennis Club"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client, reset_activities):
        """Test unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_nonexistent_student(self, client, reset_activities):
        """Test unregistering a student not in the activity returns 400"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=notastudent@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_multiple_participants(self, client, reset_activities):
        """Test unregistering multiple participants from same activity"""
        # Unregister first participant
        response1 = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Unregister second participant
        response2 = client.delete(
            "/activities/Chess%20Club/unregister?email=daniel@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both are removed
        activities_response = client.get("/activities")
        participants = activities_response.json()["Chess Club"]["participants"]
        assert len(participants) == 0


class TestIntegrationScenarios:
    """Integration tests combining multiple operations"""
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test signing up and then unregistering"""
        # Sign up
        response1 = client.post(
            "/activities/Basketball/signup?email=newplayer@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        assert "newplayer@mergington.edu" in activities_response.json()["Basketball"]["participants"]
        
        # Unregister
        response2 = client.delete(
            "/activities/Basketball/unregister?email=newplayer@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify unregister
        activities_response = client.get("/activities")
        assert "newplayer@mergington.edu" not in activities_response.json()["Basketball"]["participants"]
    
    def test_activity_capacity_tracking(self, client, reset_activities):
        """Test that participant count updates correctly"""
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Art Studio"]["participants"])
        
        # Sign up new participant
        client.post(
            "/activities/Art%20Studio/signup?email=newartist@mergington.edu"
        )
        
        after_signup = client.get("/activities")
        after_count = len(after_signup.json()["Art Studio"]["participants"])
        assert after_count == initial_count + 1
        
        # Unregister participant
        client.delete(
            "/activities/Art%20Studio/unregister?email=newartist@mergington.edu"
        )
        
        after_unregister = client.get("/activities")
        final_count = len(after_unregister.json()["Art Studio"]["participants"])
        assert final_count == initial_count
