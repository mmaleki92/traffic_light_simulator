from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
import os
from settings import width, height, traffic_lights

app = FastAPI(
    title="Traffic Control API",
    description="API for managing traffic simulation and control system",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data persistence
DATA_FILE = "traffic_data.json"

# Initial lane counters for each direction
lane_counters = {
    'top': 0,
    'bottom': 0,
    'left': 0,
    'right': 0
}

# Models
class LightStatus(BaseModel):
    id: int
    red: bool = Field(default=False, description="Red light status")
    yellow: bool = Field(default=False, description="Yellow light status")
    green: bool = Field(default=False, description="Green light status")
    
    @validator('id')
    def validate_id(cls, v):
        if v < 0:
            raise ValueError('ID must be non-negative')
        return v
    
    @validator('green')
    def check_traffic_conflicts(cls, green_value, values):
        # This is a basic validator that can be extended based on your requirements
        # For complex validations involving multiple lights, use a dependency instead
        return green_value

class LaneCounter(BaseModel):
    top: int = Field(default=0, ge=0, description="Number of cars from top lane")
    bottom: int = Field(default=0, ge=0, description="Number of cars from bottom lane")
    left: int = Field(default=0, ge=0, description="Number of cars from left lane")
    right: int = Field(default=0, ge=0, description="Number of cars from right lane")

class AccidentLog(BaseModel):
    message: str = Field(..., description="Accident description")
    is_accident: bool = Field(default=True, description="Whether this is an actual accident")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="When the accident occurred")

class TrafficPattern(BaseModel):
    name: str = Field(..., description="Name of the traffic pattern")
    description: str = Field(default="", description="Description of what this pattern does")
    lights: List[LightStatus] = Field(..., description="Light configurations for this pattern")

class Statistics(BaseModel):
    total_cars: int
    cars_per_lane: Dict[str, int]
    accidents: int
    timestamp: str

# Storage for accident logs with timestamp
accident_logs = []

# Storage for traffic patterns
traffic_patterns = {
    "all_red": {
        "description": "All lights are red - emergency situation",
        "lights": [
            {"id": i, "red": True, "yellow": False, "green": False} for i in range(len(traffic_lights))
        ]
    },
    "north_south_flow": {
        "description": "Allow north-south traffic flow",
        "lights": [
            {"id": 0, "red": False, "yellow": False, "green": True},  # up direction
            {"id": 1, "red": False, "yellow": False, "green": True},  # down direction
            {"id": 2, "red": True, "yellow": False, "green": False},  # left direction
            {"id": 3, "red": True, "yellow": False, "green": False}   # right direction
        ]
    },
    "east_west_flow": {
        "description": "Allow east-west traffic flow",
        "lights": [
            {"id": 0, "red": True, "yellow": False, "green": False},  # up direction
            {"id": 1, "red": True, "yellow": False, "green": False},  # down direction
            {"id": 2, "red": False, "yellow": False, "green": True},  # left direction
            {"id": 3, "red": False, "yellow": False, "green": True}   # right direction
        ]
    }
}

# Function to load data from file
def load_data():
    global lane_counters, accident_logs, traffic_patterns
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                lane_counters = data.get('lane_counters', lane_counters)
                accident_logs = data.get('accident_logs', accident_logs)
                traffic_patterns = data.get('traffic_patterns', traffic_patterns)
    except Exception as e:
        print(f"Error loading data: {e}")

# Function to save data to file
def save_data():
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump({
                'lane_counters': lane_counters,
                'accident_logs': accident_logs,
                'traffic_patterns': traffic_patterns
            }, f, indent=2)
    except Exception as e:
        print(f"Error saving data: {e}")

# Load data when server starts
load_data()

# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": app.version
    }

@app.get("/lane-counters", response_model=LaneCounter, tags=["Traffic Data"])
def get_lane_counters():
    """
    Get the current count of vehicles for each lane.
    """
    return lane_counters

@app.post("/lane-counters", response_model=LaneCounter, tags=["Traffic Data"])
def update_lane_counters(counters: LaneCounter):
    """
    Update the vehicle counts for lanes.
    """
    lane_counters.update(counters.dict(exclude_unset=True))
    save_data()
    return lane_counters

@app.get("/traffic-lights", tags=["Traffic Control"])
def get_traffic_lights():
    """
    Get the current status of all traffic lights.
    """
    return traffic_lights

@app.post("/traffic-lights", response_model=list, tags=["Traffic Control"])
def update_traffic_lights(light_status: LightStatus):
    """
    Update the status of a specific traffic light by ID.
    """
    for light in traffic_lights:
        if light['id'] == light_status.id:
            light['red'] = light_status.red
            light['yellow'] = light_status.yellow
            light['green'] = light_status.green
            save_data()
            return traffic_lights
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Traffic light with ID {light_status.id} not found"
    )

@app.post("/log-accident", tags=["Safety"])
def log_accident(accident: AccidentLog):
    """
    Log a traffic accident or safety incident.
    """
    log_entry = accident.dict()
    accident_logs.append(log_entry)
    save_data()
    return {"message": "Accident logged successfully", "is_accident": accident.is_accident}

@app.get("/log-accident", response_model=List[AccidentLog], tags=["Safety"])
def get_accident_logs():
    """
    Retrieve all logged accidents and safety incidents.
    """
    return accident_logs

@app.get("/check-accident", tags=["Safety"])
def check_accident():
    """
    Check if there's a potential accident situation based on traffic light configuration.
    """
    horizontal_green = any(light['green'] for light in traffic_lights if light['direction'] in ['left', 'right'])
    vertical_green = any(light['green'] for light in traffic_lights if light['direction'] in ['up', 'down'])
    is_accident = horizontal_green and vertical_green
    
    message = ""
    if is_accident:
        message = "WARNING: Potential accident! Conflicting green lights detected."
        # Log this as an accident automatically
        log_entry = {
            "message": message,
            "is_accident": True,
            "timestamp": datetime.now().isoformat()
        }
        accident_logs.append(log_entry)
        save_data()
    
    return {"is_accident": is_accident, "message": message}

@app.get("/traffic-patterns", tags=["Traffic Control"])
def get_traffic_patterns():
    """
    Get all available traffic light patterns.
    """
    return traffic_patterns

@app.post("/traffic-patterns", tags=["Traffic Control"])
def create_traffic_pattern(pattern: TrafficPattern):
    """
    Create a new traffic pattern or update an existing one.
    """
    traffic_patterns[pattern.name] = {
        "description": pattern.description,
        "lights": [light.dict() for light in pattern.lights]
    }
    save_data()
    return {"message": f"Traffic pattern '{pattern.name}' saved successfully"}

@app.post("/apply-pattern/{pattern_name}", tags=["Traffic Control"])
def apply_traffic_pattern(pattern_name: str):
    """
    Apply a predefined traffic pattern to the current traffic lights.
    """
    if pattern_name not in traffic_patterns:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Traffic pattern '{pattern_name}' not found"
        )
    
    pattern = traffic_patterns[pattern_name]
    for light_config in pattern["lights"]:
        for light in traffic_lights:
            if light['id'] == light_config['id']:
                light['red'] = light_config['red']
                light['yellow'] = light_config['yellow']
                light['green'] = light_config['green']
    
    save_data()
    return {"message": f"Applied traffic pattern: {pattern_name}", "traffic_lights": traffic_lights}

@app.get("/statistics", response_model=Statistics, tags=["Analytics"])
def get_statistics():
    """
    Get traffic statistics including total car count and accident count.
    """
    total_cars = sum(lane_counters.values())
    accident_count = sum(1 for log in accident_logs if log.get("is_accident", False))
    
    return {
        "total_cars": total_cars,
        "cars_per_lane": lane_counters,
        "accidents": accident_count,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/reset", tags=["System"])
def reset_system():
    """
    Reset all counters and logs (but keep traffic patterns).
    """
    global lane_counters, accident_logs
    lane_counters = {
        'top': 0,
        'bottom': 0,
        'left': 0,
        'right': 0
    }
    accident_logs = []
    save_data()
    return {"message": "System reset successfully"}

# Run the server when executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)