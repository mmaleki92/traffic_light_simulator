import requests

BASE_URL = "http://127.0.0.1:8000"


response = requests.get(f"{BASE_URL}/lane-counters")

print(response.json())
light_status = {
    "id": 1,
    "red": True,
    "yellow": False,
    "green": False
    }
response = requests.post(f"{BASE_URL}/traffic-lights", json=light_status)

