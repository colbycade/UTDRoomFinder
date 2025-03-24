from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Updated mock data with event details
mock_rooms = [
    {
        "room": "102",
        "building": "ECSS",
        "floor": "2",
        "available": True,
        "schedule": {
            "2025-03-24": [
                {"start_time": "09:00", "end_time": "10:00", "status": "Occupied", "event_title": "CS 1337"},
                {"start_time": "14:00", "end_time": "16:00", "status": "Occupied", "event_title": "MATH 2417"}
            ],
            "2025-03-25": [
                {"start_time": "10:00", "end_time": "12:00", "status": "Occupied", "event_title": "PHYS 2125"}
            ],
            "2025-03-26": []
        }
    },
    {
        "room": "301",
        "building": "ENG",
        "floor": "2",
        "available": True,
        "schedule": {
            "2025-03-24": [
                {"start_time": "07:00", "end_time": "09:00", "status": "Available", "event_title": ""},
                {"start_time": "09:00", "end_time": "11:00", "status": "Occupied", "event_title": "ENGL 1301"},
                {"start_time": "11:00", "end_time": "13:30", "status": "Available", "event_title": ""},
                {"start_time": "13:30", "end_time": "14:30", "status": "Occupied", "event_title": "PHYS 2123"},
                {"start_time": "14:30", "end_time": "17:00", "status": "Available", "event_title": ""}
            ],
            "2025-03-25": [
                {"start_time": "07:00", "end_time": "09:00", "status": "Available", "event_title": ""},
                {"start_time": "09:00", "end_time": "11:00", "status": "Occupied", "event_title": "ENGL 1301"},
                {"start_time": "11:00", "end_time": "12:45", "status": "Available", "event_title": ""}
            ],
            "2025-03-26": []
        }
    },
    {
        "room": "118",
        "building": "JSOM",
        "floor": "1",
        "available": True,
        "schedule": {
            "2025-03-24": [
                {"start_time": "10:00", "end_time": "12:00", "status": "Occupied", "event_title": "BA 1310"}
            ],
            "2025-03-25": [],
            "2025-03-26": [
                {"start_time": "13:00", "end_time": "14:00", "status": "Occupied", "event_title": "ECON 2301"}
            ]
        }
    },
    {
        "room": "901",
        "building": "JSOM",
        "floor": "2",
        "available": True,
        "schedule": {
            "2025-03-24": [
                {"start_time": "15:00", "end_time": "17:00", "status": "Occupied", "event_title": "MKT 3300"}
            ],
            "2025-03-25": [
                {"start_time": "09:00", "end_time": "10:00", "status": "Occupied", "event_title": "FIN 3320"}
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
            "2025-03-24": [
                {"start_time": "08:00", "end_time": "18:00", "status": "Occupied", "event_title": "HIST 1301"}
            ],
            "2025-03-25": [
                {"start_time": "10:00", "end_time": "14:00", "status": "Occupied", "event_title": "GOVT 2305"}
            ],
            "2025-03-26": [
                {"start_time": "11:00", "end_time": "13:00", "status": "Occupied", "event_title": "PSY 2301"}
            ]
        }
    }
]

# Home page with search form
@app.route('/')
def search():
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('search.html', today=today)

# Search results (API call with time filtering)
@app.route('/api/search', methods=['POST'])
def search_rooms():
    building = request.form.get('building')
    room = request.form.get('room')
    date = request.form.get('date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')

    # Convert times to 24-hour format for comparison
    def to_24hour(time_str):
        if not time_str:
            return None
        from datetime import datetime
        return datetime.strptime(time_str, '%I:%M %p').strftime('%H:%M') if 'AM' in time_str or 'PM' in time_str else time_str

    start_time_24 = to_24hour(start_time) if start_time else None
    end_time_24 = to_24hour(end_time) if end_time else None

    # Find available time slots for the results page
    results = []
    for room_data in mock_rooms:
        if building and building != 'Any Building' and room_data['building'] != building:
            continue
        if room and room != 'Any Room Number' and room_data['room'] != room:
            continue
        if date and date in room_data['schedule']:
            schedule = room_data['schedule'][date]
            if not schedule:  # No bookings means available all day
                results.append({
                    "building": room_data['building'],
                    "floor": room_data['floor'],
                    "room": room_data['room'],
                    "available_start": "07:00 AM",
                    "available_until": "10:00 PM"
                })
            else:
                # Find available time slots
                available_start = None
                available_until = None
                for i, slot in enumerate(schedule):
                    if start_time_24 and end_time_24:
                        slot_start = slot['start_time']
                        slot_end = slot['end_time']
                        if (start_time_24 < slot_end and end_time_24 > slot_start):
                            continue  # Overlaps with an occupied slot
                    if slot['status'] == "Available":
                        if not available_start:
                            available_start = slot['start_time']
                        available_until = slot['end_time']
                    else:
                        if available_start and available_until:
                            # Convert times to 12-hour format for display
                            start_12 = datetime.strptime(available_start, '%H:%M').strftime('%I:%M %p')
                            until_12 = datetime.strptime(available_until, '%H:%M').strftime('%I:%M %p')
                            if (not start_time_24 or not end_time_24) or (start_time_24 >= available_start and end_time_24 <= available_until):
                                results.append({
                                    "building": room_data['building'],
                                    "floor": room_data['floor'],
                                    "room": room_data['room'],
                                    "available_start": start_12,
                                    "available_until": until_12
                                })
                        available_start = None
                        available_until = None
                # Check if the last slot is available
                if available_start and available_until:
                    start_12 = datetime.strptime(available_start, '%H:%M').strftime('%I:%M %p')
                    until_12 = datetime.strptime(available_until, '%H:%M').strftime('%I:%M %p')
                    if (not start_time_24 or not end_time_24) or (start_time_24 >= available_start and end_time_24 <= available_until):
                        results.append({
                            "building": room_data['building'],
                            "floor": room_data['floor'],
                            "room": room_data['room'],
                            "available_start": start_12,
                            "available_until": until_12
                        })

    return jsonify({"rooms": results})

# Room schedule (API call)
@app.route('/api/schedule/<building>/<floor>/<room>')
def get_schedule(building, floor, room):
    room_data = next((r for r in mock_rooms if r['room'] == room and r['building'] == building and r['floor'] == floor), None)
    if room_data:
        return jsonify(room_data['schedule'])
    return jsonify({"error": "Room not found"}), 404

# Schedule page
@app.route('/schedule/<building>/<floor>/<room>')
def schedule(building, floor, room):
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('schedule.html', building=building, floor=floor, room=room, today=today)

# Report error (API call placeholder with mock response)
@app.route('/api/report', methods=['POST'])
def report_error():
    room = request.form.get('room')
    building = request.form.get('building')
    floor = request.form.get('floor')
    time_block = request.form.get('time_block')
    report_type = request.form.get('report_type')
    event_title = request.form.get('event_title', '')
    explanation = request.form.get('explanation', '')
    # Mock response based on report type
    if report_type == "cancelled":
        return jsonify({"status": "Event marked as cancelled", "building": building, "floor": floor, "room": room, "time_block": time_block, "explanation": explanation})
    elif report_type == "add":
        return jsonify({"status": "Event added", "building": building, "floor": floor, "room": room, "time_block": time_block, "event_title": event_title})
    elif report_type == "verify":
        return jsonify({"status": "Event accuracy reported", "building": building, "floor": floor, "room": room, "time_block": time_block})
    elif report_type == "remove":
        return jsonify({"status": "Event removed", "building": building, "floor": floor, "room": room, "time_block": time_block})
    elif report_type == "confirm":
        return jsonify({"status": "Event confirmed", "building": building, "floor": floor, "room": room, "time_block": time_block})
    return jsonify({"status": "Report submitted", "building": building, "floor": floor, "room": room, "time_block": time_block})

if __name__ == '__main__':
    app.run(debug=True)