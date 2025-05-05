# Written by Colby
# Basic Function Testing for Flask App

import pytest
import os

# Set environment variable before importing the app to use mock database
os.environ['DB_TYPE'] = 'mock'

from app import app as flask_app # Rename to avoid conflict with pytest 'app' fixture
from app import db as mock_db  # Import to directly verify database interactions
    
# Use Pytest Fixtures for managing testing context

@pytest.fixture(scope='module') # Only create the app once per test module
def app():
    flask_app.config.update({"TESTING": True})
    yield flask_app

# Test client to simulate requests to the app
@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True) # Runs automatically for EVERY test function
def reset_mock_db_state():
    mock_db.clear_db() # clear the mock database
    yield # test function runs here

# Constants for testing
DATE = "2025-04-14"
BUILDING = "TestBuilding"
ROOM = "T.101"
SEARCH_START_TIME = "12:00"
SEARCH_END_TIME = "14:00"
MIN_DURATION = "30"
EVENT_START_TIME = "10:00"
EVENT_END_TIME = "12:00"
EVENT_TITLE = "Test Event"
NOTES = "Test Notes"
MOCK_EMPTY_SCHEDULE = [
    {
        "building": BUILDING,
        "room": ROOM,
        "schedule": {}
    }
]
def get_mock_room_data(status="Scheduled"):
    return [
        {
            "building": BUILDING,
            "room": ROOM,
            "schedule": {
                DATE: [
                    {
                        "start_time": EVENT_START_TIME,
                        "end_time": EVENT_END_TIME,
                        "status": status,
                        "event_title": EVENT_TITLE,
                        "notes": NOTES
                    }
                ]
            }
        }
    ]

# Unit Tests for app.py

# Test GET /
def test_search_page_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Find a Room at UTD" in response.data

# Test GET /map
def test_map_page_loads(client):
    response = client.get('/map')
    assert response.status_code == 200
    assert b"Campus Map" in response.data

# Test POST /results search with no parameters
def test_results_page_loads(client):
    form_data = {
        'building': "Any Building",
        'room': "Any Room",
        'date': DATE,
        'start_time': '',
        'end_time': '',
        'duration': ''
    }
    response = client.post('/results', data=form_data)
    assert response.status_code == 200
    assert b"Available Rooms" in response.data
    assert b"No rooms available" in response.data # no results

# Test search with specific room
def test_search_room(client):
    mock_db.rooms = get_mock_room_data()
    form_data = {
        'building': BUILDING,
        'room': ROOM,
        'date': DATE,
        'start_time': '',
        'end_time': '',
        'duration': ''
    }
    response = client.post('/results', data=form_data)
    print(response.data)
    assert BUILDING.encode('utf-8') in response.data
    assert ROOM.encode('utf-8') in response.data
    assert b"View Schedule" in response.data # room appears in results

# Test search with specific time range and duration
def test_search_time(client):
    mock_db.rooms = get_mock_room_data()
    form_data = {
        'building': BUILDING,
        'room': ROOM,
        'date': DATE,
        'start_time': SEARCH_START_TIME,
        'end_time': SEARCH_END_TIME,
        'duration': MIN_DURATION
    }
    response = client.post('/results', data=form_data)
    assert SEARCH_START_TIME.encode('utf-8') in response.data
    assert SEARCH_END_TIME.encode('utf-8') in response.data
    assert MIN_DURATION.encode('utf-8') in response.data
    assert b"View Schedule" in response.data # room appears in results

def test_results_room_not_found(client):
    mock_db.rooms = [] # Ensure DB is empty or doesn't contain the room
    form_data = {
        'building': BUILDING,
        'room': "NonExistentRoom",
        'date': DATE,
        'start_time': '',
        'end_time': '',
        'duration': ''
    }
    response = client.post('/results', data=form_data)
    assert response.status_code == 200
    assert b"No rooms available matching your criteria" in response.data

# Test GET /api/schedule/<building>/<room>
def test_get_schedule(client):
    mock_db.rooms = get_mock_room_data()
    response = client.get(f'/api/schedule/{BUILDING}/{ROOM}')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    json_data = response.get_json()
    assert DATE in json_data
    assert len(json_data[DATE]) == 1
    assert json_data[DATE][0]['start_time'] == EVENT_START_TIME
    assert json_data[DATE][0]['end_time'] == EVENT_END_TIME
    assert json_data[DATE][0]['status'] == "Scheduled"
    assert json_data[DATE][0]['event_title'] == EVENT_TITLE
    assert json_data[DATE][0]['notes'] == NOTES

# Test POST /api/report
# user reports an event
def test_add_event(client):
    mock_db.rooms = MOCK_EMPTY_SCHEDULE
    form_data = {
        'building': BUILDING,
        'room': ROOM,
        'date': DATE,
        'start_time': SEARCH_START_TIME,
        'end_time': SEARCH_END_TIME,
        'report_type': 'add',
        'event_title': EVENT_TITLE,
        'notes': NOTES
    }
    response = client.post('/api/report', data=form_data)
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    json_data = response.get_json()
    assert json_data['building'] == BUILDING
    assert json_data['room'] == ROOM
    assert json_data['start_time'] == SEARCH_START_TIME
    assert json_data['end_time'] == SEARCH_END_TIME
    assert json_data['event_title'] == EVENT_TITLE
    assert json_data['notes'] == NOTES

# user removes a user reported event
def test_remove_event(client):
    mock_db.rooms = get_mock_room_data("User Reported")
    form_data = {
        'building': BUILDING,
        'room': ROOM,
        'date': DATE,
        'start_time': EVENT_START_TIME,
        'end_time': EVENT_END_TIME,
        'report_type': 'remove'
    }

    response = client.post('/api/report', data=form_data)
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    json_data = response.get_json()
    assert json_data['building'] == BUILDING
    assert json_data['room'] == ROOM
    assert json_data['start_time'] == EVENT_START_TIME
    assert json_data['end_time'] == EVENT_END_TIME

# user marks a scheduled event as cancelled
def test_cancel_event(client):
    mock_db.rooms = get_mock_room_data()
    form_data = {
        'building': BUILDING,
        'room': ROOM,
        'date': DATE,
        'start_time': EVENT_START_TIME,
        'end_time': EVENT_END_TIME,
        'report_type': 'cancel',
        'notes': NOTES
    }
    response = client.post('/api/report', data=form_data)
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    json_data = response.get_json()
    assert json_data['building'] == BUILDING
    assert json_data['room'] == ROOM
    assert json_data['start_time'] == EVENT_START_TIME
    assert json_data['end_time'] == EVENT_END_TIME
    assert json_data['notes'] == NOTES

# user marks a cancelled event as scheduled 
def test_confirm_event(client):
    mock_db.rooms = get_mock_room_data("Cancelled")
    form_data = {
        'building': BUILDING,
        'room': ROOM,
        'date': DATE,
        'start_time': EVENT_START_TIME,
        'end_time': EVENT_END_TIME,
        'report_type': 'confirm',
        'notes': NOTES
    }
    response = client.post('/api/report', data=form_data)
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    json_data = response.get_json()
    assert json_data['building'] == BUILDING
    assert json_data['room'] == ROOM
    assert json_data['start_time'] == EVENT_START_TIME
    assert json_data['end_time'] == EVENT_END_TIME
    assert json_data['notes'] == NOTES