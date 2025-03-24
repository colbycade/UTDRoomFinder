from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Mock data (replace with database calls later)
mock_rooms = [
    {"room": "ECSS 2.102", "building": "ECSS", "available": True, "schedule": {"2025-03-24": ["09:00-10:00", "14:00-16:00"]}},
    {"room": "JSOM 1.118", "building": "JSOM", "available": False, "schedule": {"2025-03-24": ["10:00-12:00"]}}
]

# Home page with search form
@app.route('/')
def search():
    return render_template('search.html')

# Search results (API call placeholder)
@app.route('/api/search', methods=['POST'])
def search_rooms():
    # Get form data
    building = request.form.get('building')
    date = request.form.get('date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')

    # Placeholder logic: filter mock data
    results = [room for room in mock_rooms if (not building or room['building'] == building) and room['available']]
    return jsonify({"rooms": results})

# Room schedule (API call placeholder)
@app.route('/api/schedule/<room>')
def get_schedule(room):
    # Find room in mock data
    room_data = next((r for r in mock_rooms if r['room'] == room), None)
    if room_data:
        return jsonify(room_data['schedule'])
    return jsonify({"error": "Room not found"}), 404

# Schedule page
@app.route('/schedule/<room>')
def schedule(room):
    return render_template('schedule.html', room=room)

# Report error (API call placeholder)
@app.route('/api/report', methods=['POST'])
def report_error():
    room = request.form.get('room')
    time_block = request.form.get('time_block')
    report_type = request.form.get('report_type')
    # Placeholder response
    return jsonify({"status": "Report submitted", "room": room, "time_block": time_block})

if __name__ == '__main__':
    app.run(debug=True)