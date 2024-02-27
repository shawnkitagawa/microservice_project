import requests
import json
from datetime import datetime

def print_map_with_indentation(m, indent):
    for key, value in m.items():
        if isinstance(value, dict):
            print(indent + key + ":")
            print_map_with_indentation(value, indent + "  ")
        elif isinstance(value, list):
            print(indent + key + ":")
            for i, item in enumerate(value):
                print(f"{indent}  [{i}]: {item}")
        else:
            print(f"{indent}{key}: {value}")

def concurrent_write(ids, times):
    for id in ids:
        for time in times:
            status, body, err = poster(id, time)
            if err:
                print(f"ISSUE: {status} code, {body} message, {err} error")
            else:
                print(f"SUCCESS: {status} code, {body} message")

def main():
    ids = ['id1', 'id2', 'id3']
    times = [
        datetime(2024, 1, 25, 20, 34, 6),
        datetime(2024, 2, 8, 20, 34, 6),
        datetime(2024, 2, 22, 20, 34, 6),
        # Add more timestamps as needed
    ]

    # concurrent_write(ids, times) # Uncomment to test concurrently writing to API

    for id in ids:
        for time in times:
            status, body, err = poster(id, time)
            if err:
                print(f"ISSUE: {status} code, {body} message, {err} error")
            else:
                print(f"SUCCESS: {status} code, {body} message")

        for endpoint in ['clicks_last_day_by_hour', 'clicks_last_week_by_day', 'clicks_last_month_by_week']:
            url = f"http://127.0.0.1:5000/{endpoint}/{id}"
            data, err = get_data(url)
            if err:
                print(f"Error getting {endpoint} data for {id}, error: {err}")
            else:
                print(f"{endpoint.capitalize()} data for {id}:")
                print_map_with_indentation(data, "   ")

def get_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, str(e)

def poster(id, time):
    url = "http://127.0.0.1:5000/analyze_qr_code"
    payload = {
        "qr_id": id,
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S')
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.status_code, response.text, None
    except requests.exceptions.RequestException as e:
        return 0, "", str(e)

if __name__ == "__main__":
    main()