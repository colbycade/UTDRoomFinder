# Written by Colby

from flask import Flask, render_template, request, jsonify
from db_interface import DatabaseInterface
from mock_db import MockDatabase
from mongodb import MongoDatabase
from util import to_minutes
from datetime import datetime
import os

app = Flask(__name__)

# Select database based on environment variable
DB_TYPE = os.getenv("DB_TYPE", "mock")  # Default to 'mock'

def get_db() -> DatabaseInterface:
    if DB_TYPE.lower() == "mongo":
        return MongoDatabase()
    else:
        return MockDatabase()

# Initialize the database
try:
    db = get_db()
    db.initialize_db()
except Exception as e:
    print(f"Database initialization failed: {e}")
    raise
    

# Home page with search form
@app.route('/')
def search():
    today = datetime.now().strftime('%Y-%m-%d')
    buildings = db.get_buildings()
    building_to_rooms = db.get_rooms_by_building()
    
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
    start_time = request.form.get('start_time') or "00:00"
    end_time = request.form.get('end_time') or "23:59"
    duration = request.form.get('duration')

    criteria = {
        "building": building,
        "room": room,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "duration": duration
    }

    # Find rooms with sufficient gaps
    building = building if building != "Any Building" else None
    room = room if room != "Any Room Number" else None
    rooms = db.get_rooms_with_sufficient_gap(building, room, date, start_time, end_time, duration, limit=20)

    # Compute next availability for each room on the specified date
    rooms_with_availability = []
    for room_item in rooms:
        next_slot = db.get_next_availability_on_date(
            room_item['building'],
            room_item['room'],
            date,
            start_time,
            end_time,
            duration
        )
        room_data = {
            'building': room_item['building'],
            'room': room_item['room'],
            'location': room_item.get('location', None),
            'next_availability': next_slot if next_slot else "Not available today" # shouldn't happen
        }
        rooms_with_availability.append(room_data)

    return render_template('results.html', rooms=rooms_with_availability, criteria=criteria)

# Campus Map page
@app.route('/map')
def map():
    return render_template('map.html')

# Get room schedule
@app.route('/api/schedule/<building>/<room>')
def get_schedule(building, room):
    room_data = db.get_room(building, room)
    if room_data:
        return jsonify(room_data['schedule'])
    return jsonify({"error": "Room not found"}), 404

# Schedule page
@app.route('/schedule/<building>/<room>')
def schedule(building, room):
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    # Ensure search_criteria is always provided
    search_criteria = {
        'building': request.args.get('building_search', building),
        'room': request.args.get('room_search', room),
        'date': date,
        'start_time': request.args.get('start_time', ''),
        'end_time': request.args.get('end_time', ''),
        'duration': request.args.get('duration', '')
    }
    return render_template('schedule.html', 
                         building=building, 
                         room=room, 
                         today=date,
                         search_criteria=search_criteria)

# Report event error
@app.route('/api/report', methods=['POST'])
def report_error():
    room = request.form.get('room')
    building = request.form.get('building')
    date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    report_type = request.form.get('report_type')
    event_title = request.form.get('event_title', '')
    notes = request.form.get('notes', '')

    if report_type == "add":
        result = db.add_event(building, room, date, start_time, end_time, event_title, notes=notes)
        if result is not True:
            return jsonify({"error": result}), 400  # Return validation error
        return jsonify({
            "status": "Event added", 
            "building": building, 
            "room": room, 
            "start_time": start_time, 
            "end_time": end_time, 
            "event_title": event_title, 
            "notes": notes
            })

    elif report_type == "remove":
        success = db.remove_user_event(building, room, date, start_time, end_time)
        if not success:
            return jsonify({"error": "Room or event not found"}), 404
        return jsonify({
            "status": "Event removed", 
            "building": building, 
            "room": room, 
            "start_time": start_time, 
            "end_time": end_time
            })

    elif report_type == "cancel":
        success = db.cancel_event(building, room, date, start_time, end_time, notes=notes)
        if not success:
            return jsonify({"error": "Room or event not found"}), 404
        return jsonify({
            "status": "Event marked as cancelled", 
            "building": building, 
            "room": room, 
            "start_time": start_time, 
            "end_time": end_time, 
            "notes": notes
            })

    elif report_type == "confirm":
        success = db.uncancel_event(building, room, date, start_time, end_time, notes=notes)
        if not success:
            return jsonify({"error": "Room or event not found"}), 404
        return jsonify({
            "status": "Event marked as scheduled", 
            "building": building, 
            "room": room, 
            "start_time": start_time, 
            "end_time": end_time, 
            "notes": notes
            })

    return jsonify({"error": "Invalid report type"}), 400