# Simulated database for UTD Room Finder

# Schema:
# - Room: Represents a room on campus
#   - room (str): Room number (e.g., "102")
#   - building (str): Building code (e.g., "ECSS")
#   - floor (str): Floor number (e.g., "2")
#   - schedule (dict): Mapping of dates to list of time blocks
#     - Date (str): Format "YYYY-MM-DD" (e.g., "2025-03-24")
#     - Time Block (dict): Represents a scheduled event
#       - start_time (str): Start time in 24-hour format (e.g., "09:00")
#       - end_time (str): End time in 24-hour format (e.g., "11:00")
#       - status (str): "Confirmed", "Cancelled", or "User Reported"
#       - event_title (str): Event name (e.g., "ENGL 1301")

# Mock data (remove "Available" entries, set status to "Confirmed")
mock_rooms = [
    {
        "room": "102",
        "building": "ECSS",
        "floor": "2",
        "schedule": {
            "2025-03-09": [
                {"start_time": "09:00", "end_time": "11:00", "status": "Confirmed", "event_title": "CS 1337"},
            ],
            "2025-03-24": [
                {"start_time": "09:00", "end_time": "10:00", "status": "Confirmed", "event_title": "CS 1337"},
                {"start_time": "14:00", "end_time": "16:00", "status": "Confirmed", "event_title": "MATH 2417"}
            ],
            "2025-03-25": [
                {"start_time": "10:00", "end_time": "12:00", "status": "Confirmed", "event_title": "PHYS 2125"}
            ],
            "2025-03-26": []
        }
    },
    {
        "room": "301",
        "building": "ENG",
        "floor": "2",
        "schedule": {
            "2025-03-09": [
                {"start_time": "09:00", "end_time": "11:00", "status": "Confirmed", "event_title": "ENGL 1301"},
            ],
            "2025-03-24": [
                {"start_time": "09:00", "end_time": "11:00", "status": "Confirmed", "event_title": "ENGL 1301"},
                {"start_time": "13:30", "end_time": "14:30", "status": "Confirmed", "event_title": "PHYS 2123"},
            ],
            "2025-03-25": [
                {"start_time": "09:00", "end_time": "11:00", "status": "Confirmed", "event_title": "ENGL 1301"},
            ],
            "2025-03-26": []
        }
    },
    {
        "room": "118",
        "building": "JSOM",
        "floor": "1",
        "schedule": {
            "2025-03-09": [
                {"start_time": "10:00", "end_time": "12:00", "status": "Confirmed", "event_title": "BA 1310"},
            ],
            "2025-03-24": [
                {"start_time": "10:00", "end_time": "12:00", "status": "Confirmed", "event_title": "BA 1310"}
            ],
            "2025-03-25": [],
            "2025-03-26": [
                {"start_time": "13:00", "end_time": "14:00", "status": "Confirmed", "event_title": "ECON 2301"}
            ]
        }
    },
    {
        "room": "901",
        "building": "JSOM",
        "floor": "2",
        "schedule": {
            "2025-03-09": [
                {"start_time": "15:00", "end_time": "17:00", "status": "Confirmed", "event_title": "MKT 3300"},
            ],
            "2025-03-24": [
                {"start_time": "15:00", "end_time": "17:00", "status": "Confirmed", "event_title": "MKT 3300"}
            ],
            "2025-03-25": [
                {"start_time": "09:00", "end_time": "10:00", "status": "Confirmed", "event_title": "FIN 3320"}
            ],
            "2025-03-26": []
        }
    },
    {
        "room": "208",
        "building": "GR",
        "floor": "4",
        "available": False,
        "schedule": {
            "2025-03-09": [
                {"start_time": "08:00", "end_time": "18:00", "status": "Confirmed", "event_title": "HIST 1301"}
            ],
            "2025-03-24": [
                {"start_time": "08:00", "end_time": "18:00", "status": "Confirmed", "event_title": "HIST 1301"}
            ],
            "2025-03-25": [
                {"start_time": "10:00", "end_time": "14:00", "status": "Confirmed", "event_title": "GOVT 2305"}
            ],
            "2025-03-26": [
                {"start_time": "11:00", "end_time": "13:00", "status": "Confirmed", "event_title": "PSY 2301"}
            ]
        }
    }
]

# Functions to interact with the mock database
def get_all_rooms():
    """Return all rooms in the database."""
    return mock_rooms

def get_room(building, floor, room):
    """Return a specific room by building, floor, and room number."""
    return next((r for r in mock_rooms if r['room'] == room and r['building'] == building and r['floor'] == floor), None)

def get_buildings():
    """Return a sorted list of unique buildings."""
    return sorted(set(room['building'] for room in mock_rooms))

def get_rooms_by_building():
    """Return a dictionary mapping buildings to their room numbers."""
    building_to_rooms = {}
    for room in mock_rooms:
        building = room['building']
        if building not in building_to_rooms:
            building_to_rooms[building] = []
        building_to_rooms[building].append(room['room'])
    return building_to_rooms

def add_event(building, floor, room, date, start_time, end_time, event_title, status="User Reported"):
    """Add an event to the room's schedule for the specified date."""
    room_data = get_room(building, floor, room)
    if not room_data:
        return False
    if date not in room_data['schedule']:
        room_data['schedule'][date] = []
    room_data['schedule'][date].append({
        "start_time": start_time,
        "end_time": end_time,
        "status": status,
        "event_title": event_title
    })
    # Sort the schedule by start time
    room_data['schedule'][date].sort(key=lambda x: x['start_time'])
    return True

def remove_user_event(building, floor, room, date, time_block):
    """Remove a user-reported event from the room's schedule for the specified date and time block."""
    room_data = get_room(building, floor, room)
    if not room_data or date not in room_data['schedule']:
        return False
    schedule = room_data['schedule'][date]
    room_data['schedule'][date] = [
        slot for slot in schedule
        if not (slot['start_time'] + ' - ' + slot['end_time'] == time_block and slot['status'] == "User Reported")
    ]
    return True

def cancel_event(building, floor, room, date, time_block):
    """Mark an event as cancelled in the room's schedule for the specified date and time block."""
    room_data = get_room(building, floor, room)
    if not room_data or date not in room_data['schedule']:
        return False
    for slot in room_data['schedule'][date]:
        if slot['start_time'] + ' - ' + slot['end_time'] == time_block and slot['status'] == "Confirmed":
            slot['status'] = "Cancelled"
            return True
    return False