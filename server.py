from fastapi import FastAPI
from pydantic import BaseModel
from settings import width, height, traffic_lights

app = FastAPI()

# Initial lane counters for each direction
lane_counters = {
    'top': 0,
    'bottom': 0,
    'left': 0,
    'right': 0
}

# Initial traffic light status with orientation specified
# traffic_lights = [
#     {'id': 1, 'pos': (width // 2 - 30, height // 2 - 120), 'red': True, 'yellow': False, 'green': False, 'direction': 'up'},
#     {'id': 2, 'pos': (width // 2 - 30, height // 2 + 100), 'red': True, 'yellow': False, 'green': False, 'direction': 'down'},
#     {'id': 3, 'pos': (width // 2 - 120, height // 2 - 30), 'red': True, 'yellow': True, 'green': False, 'direction': 'left'},
#     {'id': 4, 'pos': (width // 2 + 100, height // 2 - 30), 'red': True, 'yellow': False, 'green': False, 'direction': 'right'}
# ]

class LightStatus(BaseModel):
    id: int
    red: bool
    yellow: bool
    green: bool

class LaneCounter(BaseModel):
    top: int
    bottom: int
    left: int
    right: int

class AccidentLog(BaseModel):
    message: str
    is_accident: bool

accident_logs = []

@app.get("/lane-counters", response_model=LaneCounter)
def get_lane_counters():
    return lane_counters

@app.post("/lane-counters", response_model=LaneCounter)
def update_lane_counters(counters: LaneCounter):
    lane_counters.update(counters.dict())
    return lane_counters

@app.get("/traffic-lights")
def get_traffic_lights():
    return traffic_lights

@app.post("/traffic-lights", response_model=list)
def update_traffic_lights(light_status: LightStatus):
    for light in traffic_lights:
        if light['id'] == light_status.id:
            light['red'] = light_status.red
            light['yellow'] = light_status.yellow
            light['green'] = light_status.green
    return traffic_lights

@app.post("/log-accident")
def log_accident(accident: AccidentLog):
    accident_logs.append(accident.message)
    print()
    return {"message": "Accident logged successfully", "accident.is_accident": accident.is_accident}

@app.get("/accident-logs")
def get_accident_logs():
    return accident_logs

@app.get("/check-accident")
def check_accident():
    horizontal_green = any(light['green'] for light in traffic_lights if light['direction'] in ['left', 'right'])
    vertical_green = any(light['green'] for light in traffic_lights if light['direction'] in ['up', 'down'])
    is_accident = horizontal_green and vertical_green
    return {"is_accident": is_accident}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
