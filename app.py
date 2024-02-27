from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Initialize dictionaries to store click analysis data
clicks_last_day_by_hour = {}
clicks_last_week_by_day = {}
clicks_last_month_by_week = {}

# Function to save click analysis data to a JSON file
def save_clicks_data():
    try:
        with open('clicks_data.json', 'w') as file:
            json.dump({
                'click_data': {
                    qr_id: {
                        'clicks_last_day_by_hour': clicks_last_day_by_hour.get(qr_id, {}),
                        'clicks_last_week_by_day': clicks_last_week_by_day.get(qr_id, {}),
                        'clicks_last_month_by_week': clicks_last_month_by_week.get(qr_id, {})
                    } for qr_id in set(clicks_last_day_by_hour.keys()) |
                                set(clicks_last_week_by_day.keys()) |
                                set(clicks_last_month_by_week.keys())
                }
            }, file)
    except IOError as e:
        print(f'Error: Unable to write json file {e}')
    except Exception as e:
        print(f'Unexpected error occurred: {e}')

# Function to load click analysis data from a JSON file
def load_clicks_data():
    try:
        with open('clicks_data.json', 'r') as file:
            data = json.load(file)
            for qr_id, click_data in data.get('click_data', {}).items():
                clicks_last_day_by_hour[qr_id] = click_data.get('clicks_last_day_by_hour', {})
                clicks_last_week_by_day[qr_id] = click_data.get('clicks_last_week_by_day', {})
                clicks_last_month_by_week[qr_id] = click_data.get('clicks_last_month_by_week', {})
    except FileNotFoundError:
        print("error due to file not found")

# Load click analysis data when the application starts
load_clicks_data()

# Endpoint to analyze QR code data
@app.route('/analyze_qr_code', methods=['POST'])
def analyze_qr_code():
    # Get data from the POST request
    try:
        data = request.json 
        qr_id = data.get('qr_id')
        timestamp_str = data.get('timestamp')
        timestamp = datetime.fromisoformat(timestamp_str)

        # Update clicks data
        update_clicks_last_day_by_hour(qr_id, timestamp)
        update_clicks_last_week_by_day(qr_id, timestamp)
        update_clicks_last_month_by_week(qr_id, timestamp)

        # Save clicks data to the JSON file
        save_clicks_data()

        return jsonify({'Message': "QR code analyzed successfully"})
    except Exception as e:
        return jsonify({'Error': f'An unexpected error occurred: {e}'})

# Function to update clicks data for the last day by hour
def update_clicks_last_day_by_hour(qr_id, timestamp):
    current_hour = timestamp.strftime('%Y-%m-%d %H')
    clicks_last_day_by_hour.setdefault(qr_id, {}).update({current_hour: clicks_last_day_by_hour.get(qr_id, {}).get(current_hour, 0) + 1})

# Function to update clicks data for the last week by day
def update_clicks_last_week_by_day(qr_id, timestamp):
    current_day = timestamp.strftime('%Y-%m-%d')
    clicks_last_week_by_day.setdefault(qr_id, {}).update({current_day: clicks_last_week_by_day.get(qr_id, {}).get(current_day, 0) + 1})

# Function to update clicks data for the last month by week
def update_clicks_last_month_by_week(qr_id, timestamp):
    current_week_start = (timestamp - timedelta(days=timestamp.weekday())).strftime('%Y-%m-%d')
    current_week_end = (timestamp + timedelta(days=6 - timestamp.weekday())).strftime('%Y-%m-%d')
    current_week = f"{current_week_start} to {current_week_end}"
    clicks_last_month_by_week.setdefault(qr_id, {}).update({current_week: clicks_last_month_by_week.get(qr_id, {}).get(current_week, 0) + 1})

# Endpoint to get clicks for the last day by hour
# Endpoint to get clicks for the last day by hour
@app.route('/clicks_last_day_by_hour/<qr_id>', methods=['GET'])
def get_clicks_last_day_by_hour(qr_id):
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)

    relevant_data = {timestamp: clicks for timestamp, clicks in clicks_last_day_by_hour.get(qr_id, {}).items()
                     if start_time <= datetime.fromisoformat(timestamp) <= end_time}

    if relevant_data:
        print("succesful")
        return jsonify(relevant_data)
    else:
        print("empty")
        return jsonify({})


# Endpoint to get clicks for the last week by day
@app.route('/clicks_last_week_by_day/<qr_id>', methods=['GET'])
def get_clicks_last_week_by_day(qr_id):
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)

    relevant_data = {timestamp: clicks for timestamp, clicks in clicks_last_week_by_day.get(qr_id, {}).items()
                     if start_time <= datetime.fromisoformat(timestamp) <= end_time}

    if relevant_data:
        return jsonify(relevant_data)
    else:
        return jsonify({})

# Endpoint to get clicks for the last month by week
@app.route('/clicks_last_month_by_week/<qr_id>', methods=['GET'])
def get_clicks_last_month_by_week(qr_id):
    end_time = datetime.now()
    start_time = end_time - timedelta(days=30)

    relevant_data = {timestamp: clicks for timestamp, clicks in clicks_last_month_by_week.get(qr_id, {}).items()
                     if start_time <= datetime.fromisoformat(timestamp.split(' to ')[0]) <= end_time}

    if relevant_data:
        return jsonify(relevant_data)
    else:
        return jsonify({})


if __name__ == "__main__":
    app.run(debug=True)
