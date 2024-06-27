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

@app.post("/traffic-lights", response_model=list)
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
