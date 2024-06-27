from fastapi import FastAPI
from pydantic import BaseModel
from settings import width, height
app = FastAPI()

# Initial lane counters for each direction
lane_counters = {
    'top': 0,
    'bottom': 0,
    'left': 0,
    'right': 0
}

# # Initial traffic light statuses
# traffic_lights = [
#     {'id': 1, 'pos': (400 - 30, 300 - 120), 'red': True, 'yellow': False, 'green': False, 'direction': 'up'},
#     {'id': 2, 'pos': (400 - 30, 300 + 100), 'red': True, 'yellow': False, 'green': False, 'direction': 'down'},
#     {'id': 3, 'pos': (400 - 120, 300 - 30), 'red': True, 'yellow': True, 'green': False, 'direction': 'left'},
#     {'id': 4, 'pos': (400 + 100, 300 - 30), 'red': True, 'yellow': False, 'green': False, 'direction': 'right'}
# ]

# Initial traffic light status with orientation specified
traffic_lights = [
    {'pos': (width // 2 - 30, height // 2 - 120), 'red': True, 'yellow': False, 'green': False, 'direction': 'up'},
    {'pos': (width // 2 - 30, height // 2 + 100), 'red': True, 'yellow': False, 'green': False, 'direction': 'down'},
    {'pos': (width // 2 - 120, height // 2 - 30), 'red': True, 'yellow': True, 'green': False, 'direction': 'left'},
    {'pos': (width // 2 + 100, height // 2 - 30), 'red': True, 'yellow': False, 'green': False, 'direction': 'right'}
]



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

@app.post("/traffic-lights")
def update_traffic_lights(light_status: LightStatus):
    for light in traffic_lights:
        if light['id'] == light_status.id:
            light['red'] = light_status.red
            light['yellow'] = light_status.yellow
            light['green'] = light_status.green
    return traffic_lights

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
