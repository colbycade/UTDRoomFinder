from flask import Flask, render_template, request, jsonify
from mock_db import get_all_rooms, get_room, get_buildings, get_rooms_by_building, add_event, remove_user_event, cancel_event
from datetime import datetime

app = Flask(__name__)

# Home page with search form
@app.route('/')
def search():
    today = datetime.now().strftime('%Y-%m-%d')
    buildings = get_buildings()
    building_to_rooms = get_rooms_by_building()
    return render_template('search.html', today=today, buildings=buildings, building_to_rooms=building_to_rooms)

# Search results page (redirect to schedule page)
@app.route('/results', methods=['POST'])
def search_results():
    building = request.form.get('building')
    room = request.form.get('room')
    date = request.form.get('date')

    # Validate input and redirect to the schedule page
    if building == "Any Building" or room == "Any Room Number":
        # For simplicity, redirect to the first room in the database
        room_data = get_all_rooms()[0]
        building = room_data['building']
        floor = room_data['floor']
        room = room_data['room']
    else:
        room_data = get_room(building, floor=None, room=room)
        if not room_data:
            return render_template('results.html', rooms=[], criteria={"error": "Room not found"})
        floor = room_data['floor']

    return render_template('schedule.html', building=building, floor=floor, room=room, today=date or datetime.now().strftime('%Y-%m-%d'))

# Room schedule (API call)
@app.route('/api/schedule/<building>/<floor>/<room>')
def get_schedule(building, floor, room):
    room_data = get_room(building, floor, room)
    if room_data:
        return jsonify(room_data['schedule'])
    return jsonify({"error": "Room not found"}), 404

# Schedule page
@app.route('/schedule/<building>/<floor>/<room>')
def schedule(building, floor, room):
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('schedule.html', building=building, floor=floor, room=room, today=today)

# Campus Map page
@app.route('/map')
def map():
    return render_template('map.html')

# Report error (API call)
@app.route('/api/report', methods=['POST'])
def report_error():
    room = request.form.get('room')
    building = request.form.get('building')
    floor = request.form.get('floor')
    time_block = request.form.get('time_block')
    report_type = request.form.get('report_type')
    event_title = request.form.get('event_title', '')
    explanation = request.form.get('explanation', '')
    date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))  # Use current date if not provided

    if report_type == "add":
        try:
            start_time, end_time = time_block.split(' - ')
        except ValueError:
            return jsonify({"error": "Invalid time block format"}), 400
        success = add_event(building, floor, room, date, start_time, end_time, event_title)
        if not success:
            return jsonify({"error": "Room not found"}), 404
        return jsonify({"status": "Event added", "building": building, "floor": floor, "room": room, "time_block": time_block, "event_title": event_title})

    elif report_type == "remove":
        success = remove_user_event(building, floor, room, date, time_block)
        if not success:
            return jsonify({"error": "Room or event not found"}), 404
        return jsonify({"status": "Event removed", "building": building, "floor": floor, "room": room, "time_block": time_block})

    elif report_type == "cancelled":
        success = cancel_event(building, floor, room, date, time_block)
        if not success:
            return jsonify({"error": "Room or event not found"}), 404
        return jsonify({"status": "Event marked as cancelled", "building": building, "floor": floor, "room": room, "time_block": time_block, "explanation": explanation})

    return jsonify({"status": "Report submitted", "building": building, "floor": floor, "room": room, "time_block": time_block})
