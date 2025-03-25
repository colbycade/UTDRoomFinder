from flask import Flask, render_template, request, jsonify, url_for
from mock_db import get_all_rooms, get_room, get_buildings, get_rooms_by_building, add_event, remove_user_event, cancel_event, uncancel_event, get_rooms_with_sufficient_gap, get_next_availability_on_date, to_minutes
from datetime import datetime

app = Flask(__name__)

# Home page with search form
@app.route('/')
def search():
    today = datetime.now().strftime('%Y-%m-%d')
    buildings = get_buildings()
    building_to_rooms = get_rooms_by_building()
    
    # Get query parameters to pre-fill the form
    building = request.args.get('building', 'Any Building')
    room = request.args.get('room', 'Any Room Number')
    date = request.args.get('date', today)
    start_time = request.args.get('start_time', '')
    end_time = request.args.get('end_time', '')
    duration = request.args.get('duration', '')

    return render_template('search.html', 
                         today=today, 
                         buildings=buildings, 
                         building_to_rooms=building_to_rooms,
                         selected_building=building,
                         selected_room=room,
                         selected_date=date,
                         selected_start_time=start_time,
                         selected_end_time=end_time,
                         selected_duration=duration)

# Search results page
@app.route('/results', methods=['POST'])
def search_results():
    building = request.form.get('building')
    room = request.form.get('room')
    date = request.form.get('date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    duration = request.form.get('duration')

    # Validate that a date is selected
    if not date:
        return render_template('results.html', rooms=[], criteria={
            "building": building,
            "room": room,
            "date": date,
            "start_time": start_time or "00:00",
            "end_time": end_time or "23:59",
            "duration": duration,
            "error": "Please select a date"
        })

    # Validate start time is before end time if both are provided
    if start_time and end_time:
        try:
            start_minutes = to_minutes(start_time)
            end_minutes = to_minutes(end_time)
            print(f"Validating times: start_time={start_time} ({start_minutes} minutes), end_time={end_time} ({end_minutes} minutes)")  # Debugging
            if start_minutes >= end_minutes:
                print("Validation failed: Start time is not before end time")  # Debugging
                return render_template('results.html', rooms=[], criteria={
                    "building": building,
                    "room": room,
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "error": "Start time must be before end time"
                })
        except ValueError as e:
            print(f"Error parsing times: {e}")  # Debugging
            return render_template('results.html', rooms=[], criteria={
                "building": building,
                "room": room,
                "date": date,
                "start_time": start_time,
                "end_time": end_time,
                "duration": duration,
                "error": "Invalid time format"
            })

    # Find rooms with sufficient gaps
    rooms = get_rooms_with_sufficient_gap(building, date, start_time, end_time, duration)

    # If a specific room is selected, filter the rooms list to only include that room
    if building != "Any Building" and room != "Any Room Number":
        room_data = get_room(building, room)
        if not room_data:
            return render_template('results.html', rooms=[], criteria={
                "building": building,
                "room": room,
                "date": date,
                "start_time": start_time or "00:00",
                "end_time": end_time or "23:59",
                "duration": duration,
                "error": "Room not found"
            })
        # Filter rooms to only include the selected room
        rooms = [r for r in rooms if r['building'] == building and r['room'] == room]

    # Compute next availability for each room on the specified date
    rooms_with_availability = []
    for room_item in rooms:
        next_slot = get_next_availability_on_date(
            room_item['building'],
            room_item['room'],
            date,
            start_time or "00:00",
            end_time or "23:59",
            duration
        )
        room_data = {
            'building': room_item['building'],
            'room': room_item['room'],
            'next_availability': next_slot if next_slot else "Not available today"
        }
        rooms_with_availability.append(room_data)

    # Debug the value of room before setting criteria
    print(f"Setting criteria.room to: {room} (type: {type(room)})")

    return render_template('results.html', rooms=rooms_with_availability, criteria={
        "building": building,
        "room": room,
        "date": date,
        "start_time": start_time or "00:00",
        "end_time": end_time or "23:59",
        "duration": duration
    })

# Room schedule (API call)
@app.route('/api/schedule/<building>/<room>')
def get_schedule(building, room):
    room_data = get_room(building, room)
    if room_data:
        return jsonify(room_data['schedule'])
    return jsonify({"error": "Room not found"}), 404

# Schedule page
@app.route('/schedule/<building>/<room>')
def schedule(building, room):
    today = datetime.now().strftime('%Y-%m-%d')
    # Ensure search_criteria is always provided
    search_criteria = request.args.to_dict()
    if not search_criteria:
        search_criteria = {
            'building': building,
            'room': room,
            'date': today,
            'start_time': '',
            'end_time': '',
            'duration': ''
        }
    return render_template('schedule.html', 
                         building=building, 
                         room=room, 
                         today=today,
                         search_criteria=search_criteria)

# Campus Map page
@app.route('/map')
def map():
    return render_template('map.html')

# Report error (API call)
@app.route('/api/report', methods=['POST'])
def report_error():
    room = request.form.get('room')
    building = request.form.get('building')
    time_block = request.form.get('time_block')
    report_type = request.form.get('report_type')
    event_title = request.form.get('event_title', '')
    notes = request.form.get('notes', '')
    date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))

    if report_type == "add":
        try:
            start_time, end_time = time_block.split(' - ')
        except ValueError:
            return jsonify({"error": "Invalid time block format"}), 400
        result = add_event(building, room, date, start_time, end_time, event_title, notes=notes)
        if result is not True:
            return jsonify({"error": result}), 400  # Return validation error
        return jsonify({"status": "Event added", "building": building, "room": room, "time_block": time_block, "event_title": event_title, "notes": notes})

    elif report_type == "remove":
        success = remove_user_event(building, room, date, time_block)
        if not success:
            return jsonify({"error": "Room or event not found"}), 404
        return jsonify({"status": "Event removed", "building": building, "room": room, "time_block": time_block})

    elif report_type == "cancelled":
        success = cancel_event(building, room, date, time_block, notes=notes)
        if not success:
            return jsonify({"error": "Room or event not found"}), 404
        return jsonify({"status": "Event marked as cancelled", "building": building, "room": room, "time_block": time_block, "notes": notes})

    elif report_type == "uncancel":
        success = uncancel_event(building, room, date, time_block, notes=notes)
        if not success:
            return jsonify({"error": "Room or event not found"}), 404
        return jsonify({"status": "Event marked as scheduled", "building": building, "room": room, "time_block": time_block, "notes": notes})

    return jsonify({"status": "Report submitted", "building": building, "room": room, "time_block": time_block})