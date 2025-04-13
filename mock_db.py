# Simulated database for UTD Room Finder

# Schema:
# - Room: Represents a room on campus
#   - room (str): Room number (e.g., "2.102")
#   - building (str): Building code (e.g., "ECSS")
#   - schedule (dict): Mapping of dates to list of time blocks
#     - Date (str): Format "YYYY-MM-DD" (e.g., "2025-03-24")
#     - Time Block (dict): Represents a scheduled event
#       - start_time (str): Start time in 24-hour format (e.g., "09:00")
#       - end_time (str): End time in 24-hour format (e.g., "11:00")
#       - status (str): "Scheduled", "Cancelled", or "User Reported"
#       - event_title (str): Event name (e.g., "ENGL 1301")
#       - notes (str): Additional notes about the event or cancellation

mock_rooms = [
    {
        "room": "2.102",
        "building": "ECSS",
        "schedule": {
            "2025-03-24": [
                {"start_time": "09:00", "end_time": "11:00", "status": "Scheduled", "event_title": "CS 1337", "notes": ""},
                {"start_time": "12:00", "end_time": "13:00", "status": "User Reported", "event_title": "Study Group", "notes": "Group project meeting for CS 1337"}
            ],
            "2025-03-25": [
                {"start_time": "10:00", "end_time": "12:00", "status": "Scheduled", "event_title": "PHYS 2125", "notes": ""}
            ],
            "2025-03-26": [
                {"start_time": "09:00", "end_time": "10:00", "status": "Cancelled", "event_title": "CS 1337", "notes": "Professor out sick"},
                {"start_time": "14:00", "end_time": "16:00", "status": "Scheduled", "event_title": "MATH 2417", "notes": ""}
            ],
            "2025-03-27": [
                {"start_time": "10:00", "end_time": "12:00", "status": "Scheduled", "event_title": "PHYS 2125", "notes": ""}
            ]
        }
    },
    {
        "room": "2.301",
        "building": "ENG",
        "schedule": {
            "2025-03-09": [
                {"start_time": "09:00", "end_time": "11:00", "status": "Scheduled", "event_title": "ENGL 1301", "notes": ""}
            ],
            "2025-03-24": [
                {"start_time": "09:00", "end_time": "11:00", "status": "Scheduled", "event_title": "ENGL 1301", "notes": ""},
                {"start_time": "11:30", "end_time": "12:30", "status": "User Reported", "event_title": "Peer Review Session", "notes": "Reviewing essays for ENGL 1301"},
                {"start_time": "13:30", "end_time": "14:30", "status": "Cancelled", "event_title": "PHYS 2123", "notes": "Lab equipment failure"}
            ],
            "2025-03-25": [
                {"start_time": "09:00", "end_time": "11:00", "status": "Scheduled", "event_title": "ENGL 1301", "notes": ""}
            ],
            "2025-03-26": []
        }
    },
    {
        "room": "1.118",
        "building": "JSOM",
        "schedule": {
            "2025-03-09": [
                {"start_time": "10:00", "end_time": "12:00", "status": "Scheduled", "event_title": "BA 1310", "notes": ""}
            ],
            "2025-03-24": [
                {"start_time": "10:00", "end_time": "12:00", "status": "Scheduled", "event_title": "BA 1310", "notes": ""}
            ],
            "2025-03-25": [
                {"start_time": "14:00", "end_time": "15:30", "status": "User Reported", "event_title": "Team Meeting", "notes": "Discussing BA 1310 group presentation"}
            ],
            "2025-03-26": [
                {"start_time": "13:00", "end_time": "14:00", "status": "Scheduled", "event_title": "ECON 2301", "notes": ""}
            ]
        }
    },
    {
        "room": "2.901",
        "building": "JSOM",
        "schedule": {
            "2025-03-09": [
                {"start_time": "15:00", "end_time": "17:00", "status": "Scheduled", "event_title": "MKT 3300", "notes": ""}
            ],
            "2025-03-24": [
                {"start_time": "15:00", "end_time": "17:00", "status": "Cancelled", "event_title": "MKT 3300", "notes": "Guest speaker unavailable"}
            ],
            "2025-03-25": [
                {"start_time": "09:00", "end_time": "10:00", "status": "Scheduled", "event_title": "FIN 3320", "notes": ""}
            ],
            "2025-03-26": []
        }
    },
    {
        "room": "4.208",
        "building": "GR",
        "schedule": {
            "2025-03-09": [
                {"start_time": "08:00", "end_time": "18:00", "status": "Scheduled", "event_title": "HIST 1301", "notes": ""}
            ],
            "2025-03-24": [
                {"start_time": "08:00", "end_time": "18:00", "status": "Scheduled", "event_title": "HIST 1301", "notes": ""}
            ],
            "2025-03-25": [
                {"start_time": "10:00", "end_time": "14:00", "status": "Cancelled", "event_title": "GOVT 2305", "notes": "Class moved online"},
                {"start_time": "15:00", "end_time": "16:00", "status": "User Reported", "event_title": "Study Session", "notes": "Preparing for GOVT 2305 exam"}
            ],
            "2025-03-26": [
                {"start_time": "11:00", "end_time": "13:00", "status": "Scheduled", "event_title": "PSY 2301", "notes": ""}
            ]
        }
    }
]

def initialize_db():
    pass # Nothing to do for mock db

# Functions to interact with the mock database
def get_room(building, room):
    """Return a specific room by building and room number."""
    return next((r for r in mock_rooms if r['room'] == room and r['building'] == building), None)

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

def to_minutes(time_str):
    """Convert a time string (HH:MM) to minutes since midnight."""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

def check_overlap(building, room, date, start_time, end_time):
    """Check if the new event overlaps with any existing non-cancelled events."""
    room_data = get_room(building, room)
    if not room_data or date not in room_data['schedule']:
        return False  # No events, so no overlap

    start_minutes = to_minutes(start_time)
    end_minutes = to_minutes(end_time)

    for slot in room_data['schedule'][date]:
        if slot['status'] == "Cancelled":
            continue  # Ignore cancelled events
        slot_start = to_minutes(slot['start_time'])
        slot_end = to_minutes(slot['end_time'])
        # Check for overlap: if the new event starts before the existing event ends and ends after the existing event starts
        if start_minutes < slot_end and end_minutes > slot_start:
            return True  # Overlap found
    return False  # No overlap

def add_event(building, room, date, start_time, end_time, event_title, notes="", status="User Reported"):
    """Add an event to the room's schedule for the specified date with validation."""
    room_data = get_room(building, room)
    if not room_data:
        return "Room not found"

    # Validate start time is before end time
    start_minutes = to_minutes(start_time)
    end_minutes = to_minutes(end_time)
    if start_minutes >= end_minutes:
        return "Start time must be before end time"

    # Check for overlapping events
    if check_overlap(building, room, date, start_time, end_time):
        return "Event overlaps with an existing event"

    # Add the event
    if date not in room_data['schedule']:
        room_data['schedule'][date] = []
    room_data['schedule'][date].append({
        "start_time": start_time,
        "end_time": end_time,
        "status": status,
        "event_title": event_title,
        "notes": notes
    })
    # Sort the schedule by start time
    room_data['schedule'][date].sort(key=lambda x: x['start_time'])
    return True

def remove_user_event(building, room, date, time_block):
    """Remove a user-reported event from the room's schedule for the specified date and time block."""
    room_data = get_room(building, room)
    if not room_data or date not in room_data['schedule']:
        return False
    schedule = room_data['schedule'][date]
    room_data['schedule'][date] = [
        slot for slot in schedule
        if not (slot['start_time'] + ' - ' + slot['end_time'] == time_block and slot['status'] == "User Reported")
    ]
    return True

def cancel_event(building, room, date, time_block, notes=""):
    """Mark an event as cancelled in the room's schedule for the specified date and time block."""
    room_data = get_room(building, room)
    if not room_data or date not in room_data['schedule']:
        return False
    for slot in room_data['schedule'][date]:
        if slot['start_time'] + ' - ' + slot['end_time'] == time_block and slot['status'] == "Scheduled":
            slot['status'] = "Cancelled"
            # Prepend standard message and append explanation if provided
            base_message = "User reported event as cancelled."
            slot['notes'] = base_message if not notes else f"{base_message} Explanation: {notes}"
            return True
    return False

def uncancel_event(building, room, date, time_block, notes=""):
    """Mark a cancelled event as scheduled again in the room's schedule for the specified date and time block."""
    room_data = get_room(building, room)
    if not room_data or date not in room_data['schedule']:
        return False
    for slot in room_data['schedule'][date]:
        if slot['start_time'] + ' - ' + slot['end_time'] == time_block and slot['status'] == "Cancelled":
            slot['status'] = "Scheduled"
            # Overwrite notes with uncancel message
            base_message = "User Confirmed."
            slot['notes'] = base_message if not notes else f"{base_message} Explanation: {notes}"
            return True
    return False

def find_available_slots(building, room, date, start_time="00:00", end_time="23:59"):
    """Find all available time slots for a room on a given date within the specified time range."""
    room_data = get_room(building, room)
    if not room_data or date not in room_data['schedule'] or not room_data['schedule'][date]:
        # If no events, the entire time range is available
        return [(start_time, end_time)]

    # Convert times to minutes for easier comparison
    start_minutes = to_minutes(start_time)
    end_minutes = to_minutes(end_time)

    # Get events for the day, excluding cancelled ones
    events = [slot for slot in room_data['schedule'][date] if slot['status'] != "Cancelled"]
    events.sort(key=lambda x: to_minutes(x['start_time']))

    available_slots = []
    current_time = start_minutes

    # Check gaps between events
    for event in events:
        event_start = to_minutes(event['start_time'])
        event_end = to_minutes(event['end_time'])

        # Skip events that end before the start time or start after the end time
        if event_end <= start_minutes or event_start >= end_minutes:
            continue

        # If there's a gap before this event starts
        if current_time < event_start and event_start <= end_minutes:
            slot_start = max(current_time, start_minutes)
            slot_end = event_start
            if slot_start < slot_end:
                available_slots.append((
                    f"{slot_start // 60:02d}:{slot_start % 60:02d}",
                    f"{slot_end // 60:02d}:{slot_end % 60:02d}"
                ))

        # Move the current time to the end of this event
        current_time = max(current_time, event_end)

    # Check for a gap after the last event
    if current_time < end_minutes:
        available_slots.append((
            f"{current_time // 60:02d}:{current_time % 60:02d}",
            f"{end_minutes // 60:02d}:{end_minutes % 60:02d}"
        ))

    return available_slots

def get_next_availability_on_date(building, room, date, start_time="00:00", end_time="23:59", min_duration=1):
    """
    Find the next available time slot on the specified date that meets the criteria.
    Returns the time slot as a string (e.g., "10:00 - 12:00") or None if no slot is available.
    """
    available_slots = find_available_slots(building, room, date, start_time, end_time)
    min_duration = int(min_duration) if min_duration else 1

    # Find the first slot that meets the minimum duration
    for slot_start, slot_end in available_slots:
        slot_duration = to_minutes(slot_end) - to_minutes(slot_start)
        if slot_duration >= min_duration:
            return f"{slot_start} - {slot_end}"
    
    return None

def has_sufficient_gap(building, room, date, start_time, end_time, min_duration):
    """Check if a room has a gap of at least min_duration minutes between start_time and end_time."""
    available_slots = find_available_slots(building, room, date, start_time, end_time)
    for slot_start, slot_end in available_slots:
        slot_start_minutes = to_minutes(slot_start)
        slot_end_minutes = to_minutes(slot_end)
        slot_duration = slot_end_minutes - slot_start_minutes
        if slot_duration >= min_duration:
            return True
    return False

def get_rooms_with_sufficient_gap(building, date, start_time, end_time, min_duration):
    """Return a list of rooms in the specified building with at least one gap of min_duration minutes."""
    # Default times if not provided
    start_time = start_time or "00:00"
    end_time = end_time or "23:59"

    # If no duration is provided, set a minimal duration to ensure some availability
    min_duration = int(min_duration) if min_duration else 1

    free_rooms = []
    for room_data in mock_rooms:
        if building != "Any Building" and room_data['building'] != building:
            continue
        room = room_data['room']
        # If no events on that day, the whole day is available
        if date not in room_data['schedule'] or not room_data['schedule'][date]:
            free_rooms.append(room_data)
            continue
        # Otherwise, check for sufficient gaps
        if has_sufficient_gap(room_data['building'], room, date, start_time, end_time, min_duration):
            free_rooms.append(room_data)
    return free_rooms