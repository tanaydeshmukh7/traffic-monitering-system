import json
import os

DATA_FILE = os.path.join(
    os.path.dirname(__file__),
    "traffic_data.json"
)

def update_traffic(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def get_traffic():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "vehicle_count": 0,
            "violation_count": 0,
            "density": "LOW",
            "lane": "LANE 1",
            "signal": "RED",
            "system_status": "ONLINE"
        }