import requests
import pygame
import sys
from settings import FPS, BLACK, width, height, traffic_lights
from draw_objects import draw_road, draw_traffic_light, Car
import random
import pygame
import pytmx
import time

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Crossroad Simulation")

# URL of the FastAPI server
BASE_URL = "http://127.0.0.1:8000"

lane_counters = {
    'top': 0,
    'bottom': 0,
    'left': 0,
    'right': 0
}

# Track spawn timers for each direction
spawn_timers = {
    'up-down': 0,
    'down-up': 0,
    'left-right': 0,
    'right-left': 0
}
# Spawn intervals (in frames) for each direction
spawn_intervals = {
    'up-down': 60,
    'down-up': 70,
    'left-right': 65,
    'right-left': 75
}
# Maximum number of cars (set this to a reasonable number based on your system performance)
MAX_CARS = 100

# Define a larger simulation area that extends beyond the visible window
# This will be used for car management outside the visible area
simulation_bounds = {
    'left': -200,
    'right': width + 200,
    'top': -200,
    'bottom': height + 200
}

# Track the last time we did a cleanup of stalled cars
last_cleanup_time = time.time()
cleanup_interval = 5  # seconds between cleanup checks

def fetch_lane_counters():
    try:
        response = requests.get(f"{BASE_URL}/lane-counters")
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch lane counters: {e}")
    return lane_counters  # Return the current lane_counters if the server is not available

def update_lane_counters(counters):
    try:
        response = requests.post(f"{BASE_URL}/lane-counters", json=counters)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Failed to update lane counters: {e}")
    return False

def fetch_traffic_lights():
    try:
        response = requests.get(f"{BASE_URL}/traffic-lights")
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch traffic lights: {e}")
    return traffic_lights  # Return the initialized traffic_lights if the server is not available

def update_traffic_light(light_status):
    try:
        response = requests.post(f"{BASE_URL}/traffic-lights", json=light_status)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Failed to update traffic light: {e}")
    return False

def log_accident(is_accident, message):
    try:
        response = requests.post(f"{BASE_URL}/log-accident", json={"message": message, "is_accident": is_accident})
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Failed to log accident: {e}")
    return False


def spawn_cars(cars):
    global lane_counters, spawn_timers
    
    # If we're at capacity, don't attempt to spawn more cars
    if len(cars) >= MAX_CARS:
        return 0  # Return 0 to indicate no cars were spawned
    
    cars_spawned = 0
    # Update all spawn timers
    for direction in spawn_timers:
        spawn_timers[direction] += 1
    
    # Calculate how many slots we have available
    available_slots = MAX_CARS - len(cars)
    
    # Try to spawn cars for each direction if timer is up
    for direction in spawn_timers:
        if available_slots <= 0:
            break  # Stop if we're at capacity
            
        if spawn_timers[direction] >= spawn_intervals[direction]:
            spawn_timers[direction] = 0  # Reset the timer
            
            # Spawn the car
            road_width = 50  # Increased to accommodate 4 lanes in total, 2 per direction
            lane_width = road_width // 4  # 4 lanes, each lane has a width of road_width/4
            
            if direction in ['up-down', 'down-up']:
                # Choose a random lane among the two available for the direction
                lane_number = random.choice([1, 2])  # 1 or 2 for top and bottom lanes
                lane_base_left = width // 2 - road_width // 2 + lane_width * (lane_number - 1)
                lane_base_right = width // 2 + road_width // 2 - lane_width * lane_number
                
                if direction == 'up-down':
                    y_position = simulation_bounds['top']  # Start above the visible area
                    speed = 2
                    lane_position = lane_base_left + lane_width // 2 - 14
                    lane_counters['top'] += 1
                else:
                    y_position = simulation_bounds['bottom']  # Start below the visible area
                    speed = -2
                    lane_position = lane_base_right + lane_width // 2
                    lane_counters['bottom'] += 1

                car = Car(lane_position, y_position, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), speed, 'vertical', direction)
            else:
                # Choose a random lane among the two available for the direction
                lane_number = random.choice([1, 2])  # 1 or 2 for left and right lanes
                lane_base_top = height // 2 - road_width // 2 + lane_width * (lane_number - 1)
                lane_base_bottom = height // 2 + road_width // 2 - lane_width * lane_number
                
                if direction == 'left-right':
                    x_position = simulation_bounds['left']  # Start to the left of the visible area
                    speed = 2
                    lane_position = lane_base_bottom + lane_width // 2 
                    lane_counters['left'] += 1
                else:
                    x_position = simulation_bounds['right']  # Start to the right of the visible area
                    speed = -2
                    lane_position = lane_base_top + lane_width // 2 -10
                    lane_counters['right'] += 1

                car = Car(x_position, lane_position, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), speed, 'horizontal', direction)

            cars.add(car)  # Use add() instead of append()
            cars_spawned += 1
            available_slots -= 1
            update_lane_counters(lane_counters)
            print(f"Added car: {direction} at: {lane_position} with speed {speed}")
    
    return cars_spawned

def manage_traffic_lights(cars, lights):
    """
    Manages how cars respond to traffic lights.
    Updated to handle both visible and non-visible cars consistently.
    """
    # Create a dictionary to represent the traffic light state for each direction
    light_states = {
        'up': False,    # Green state for up direction
        'down': False,  # Green state for down direction
        'left': False,  # Green state for left direction
        'right': False  # Green state for right direction
    }
    
    # First, determine the state of each directional traffic light
    for light in lights:
        if light['green']:
            light_states[light['direction']] = True
    
    # Use a fixed stop distance for all cars to be consistent
    stop_distance = 50
    
    # Apply the traffic light rules to all cars
    for car in cars:
        # Initially assume the car can move
        car.moving = True
        
        # Check if the car needs to stop based on traffic lights
        if car.direction == 'horizontal':
            if car.spawn_direction == 'left-right' and not light_states['left']:
                # Calculate if car is approaching a red light
                for light in lights:
                    if light['direction'] == 'left':
                        if light['pos'][0] - stop_distance <= car.rect.right < light['pos'][0] + stop_distance:
                            car.moving = False
                            break
            
            elif car.spawn_direction == 'right-left' and not light_states['right']:
                # Calculate if car is approaching a red light
                for light in lights:
                    if light['direction'] == 'right':
                        if light['pos'][0] - stop_distance <= car.rect.left < light['pos'][0] + stop_distance:
                            car.moving = False
                            break
        
        elif car.direction == 'vertical':
            if car.spawn_direction == 'up-down' and not light_states['up']:
                # Calculate if car is approaching a red light
                for light in lights:
                    if light['direction'] == 'up':
                        if light['pos'][1] - stop_distance <= car.rect.bottom < light['pos'][1] + stop_distance:
                            car.moving = False
                            break
            
            elif car.spawn_direction == 'down-up' and not light_states['down']:
                # Calculate if car is approaching a red light
                for light in lights:
                    if light['direction'] == 'down':
                        if light['pos'][1] - stop_distance <= car.rect.top < light['pos'][1] + stop_distance:
                            car.moving = False
                            break

def draw_lane_counters(screen):
    font = pygame.font.Font(None, 20)
    colors = {'top': (255, 255, 255), 'bottom': (255, 255, 255), 'left': (255, 255, 255), 'right': (255, 255, 255)}
    positions = {'top': (50, 50), 'bottom': (50, height - 50), 'left': (50, 100), 'right': (width - 150, 100)}
    for lane, count in lane_counters.items():
        text_surface = font.render(f'{lane.capitalize()} Lane: {count}', True, colors[lane])
        screen.blit(text_surface, positions[lane])

def check_for_accidents(lights):
    horizontal_green = any(light['green'] for light in lights if light['direction'] in ['left', 'right'])
    vertical_green = any(light['green'] for light in lights if light['direction'] in ['up', 'down'])
    return horizontal_green and vertical_green

def is_car_in_extended_bounds(car):
    """
    Check if a car is within our extended simulation bounds.
    This allows cars to exist outside the visible window but still be simulated.
    """
    if car.direction == 'horizontal':
        return simulation_bounds['left'] - 50 <= car.rect.x <= simulation_bounds['right'] + 50
    else:  # vertical
        return simulation_bounds['top'] - 50 <= car.rect.y <= simulation_bounds['bottom'] + 50

def cleanup_stalled_cars(cars, lights):
    """
    Remove cars that have been stalled for too long to prevent gridlock.
    This helps maintain car flow even when traffic lights cause congestion.
    """
    # Check if lights are green to avoid removing cars that are legitimately waiting
    light_states = {
        'up': False, 
        'down': False, 
        'left': False, 
        'right': False
    }
    for light in lights:
        if light['green']:
            light_states[light['direction']] = True
    
    cars_to_remove = []
    
    # If we're at or near capacity, be more aggressive with cleanup
    at_capacity = len(cars) >= MAX_CARS * 0.9
    
    for car in cars:
        # If the car isn't moving but should be moving based on traffic lights, it might be stuck
        if not car.moving:
            if car.direction == 'horizontal':
                if (car.spawn_direction == 'left-right' and light_states['left']) or \
                   (car.spawn_direction == 'right-left' and light_states['right']):
                    # The car should be moving but isn't
                    cars_to_remove.append(car)
            elif car.direction == 'vertical':
                if (car.spawn_direction == 'up-down' and light_states['up']) or \
                   (car.spawn_direction == 'down-up' and light_states['down']):
                    # The car should be moving but isn't
                    cars_to_remove.append(car)
        
        # Remove edge cases - cars that are really far out
        if not is_car_in_extended_bounds(car):
            cars_to_remove.append(car)
        
        # If we're at capacity, remove some off-screen cars to make room
        if at_capacity and not car.rect.colliderect(pygame.Rect(0, 0, width, height)):
            # Make sure we prefer to remove cars that are moving away from the intersection
            if car.direction == 'horizontal':
                if (car.spawn_direction == 'left-right' and car.rect.left > width/2) or \
                   (car.spawn_direction == 'right-left' and car.rect.right < width/2):
                    cars_to_remove.append(car)
            elif car.direction == 'vertical':
                if (car.spawn_direction == 'up-down' and car.rect.top > height/2) or \
                   (car.spawn_direction == 'down-up' and car.rect.bottom < height/2):
                    cars_to_remove.append(car)
    
    # Remove the cars we identified
    for car in cars_to_remove:
        if car in cars:  # Make sure the car is still in the group
            cars.remove(car)
            print(f"Removed car during cleanup. Remaining: {len(cars)}")

# Frame rate
clock = pygame.time.Clock()

def load_map(filename):
    tmx_data = pytmx.util_pygame.load_pygame(filename)
    return tmx_data

def draw_map_surface(tmx_data, scale):
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    
    # Create a surface with the size of the entire map
    map_surface = pygame.Surface((map_width, map_height), pygame.SRCALPHA)
    
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    map_surface.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))
    
    # Scale the map surface
    scaled_surface = pygame.transform.scale(map_surface, (int(map_width * scale), int(map_height * scale)))
    
    return scaled_surface

def main():
    global last_cleanup_time
    
    tmx_data = load_map("map.tmx")
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    
    # Calculate scale factor to fit the map to the screen size
    scale_x = width / map_width
    scale_y = height / map_height
    scale = min(scale_x, scale_y)  # Maintain aspect ratio by using the smaller scale factor
    scaled_map_surface = draw_map_surface(tmx_data, scale)
    global lane_counters  # Use the global counters
    global traffic_lights  # And the global traffic light settings
    running = True
    cars = pygame.sprite.Group()  # This will hold all car sprites
    lane_counters.update(fetch_lane_counters())
    traffic_lights = fetch_traffic_lights()

    # Font for displaying stats
    font = pygame.font.Font(None, 24)
    debug_mode = False  # Toggle for showing debug info
    
    # Track statistics
    cars_spawned_this_frame = 0
    cars_removed_this_frame = 0

    while running:
        frame_start_car_count = len(cars)
        cars_spawned_this_frame = 0
        cars_removed_this_frame = 0
        
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:  # Press 'D' to toggle debug mode
                    debug_mode = not debug_mode
                elif event.key == pygame.K_c:  # Press 'C' to force cleanup
                    pre_cleanup_count = len(cars)
                    cleanup_stalled_cars(cars, traffic_lights)
                    post_cleanup_count = len(cars)
                    print(f"Manual cleanup removed {pre_cleanup_count - post_cleanup_count} cars")

        # Fetch latest traffic light states
        traffic_lights = fetch_traffic_lights()
        
        # Regular cleanup check on timer
        current_time = time.time()
        if current_time - last_cleanup_time >= cleanup_interval:
            cleanup_stalled_cars(cars, traffic_lights)
            last_cleanup_time = current_time
        
        # Spawn cars only if we're not at capacity
        if len(cars) < MAX_CARS:
            cars_spawned_this_frame = spawn_cars(cars)
        
        # Manage traffic lights for ALL cars
        manage_traffic_lights(cars, traffic_lights)
        
        if check_for_accidents(traffic_lights):
            log_accident(True, "Warning: Potential accident! Both vertical and horizontal lanes have green lights!")
        
        # Update ALL cars
        starting_car_count = len(cars)
        for car in list(cars):  # Make a copy for safe iteration
            car.update(cars)
            
            # Check if car is far outside our extended bounds
            if not is_car_in_extended_bounds(car):
                cars.remove(car)
                cars_removed_this_frame += 1
        
        # Calculate how many cars were removed during update
        cars_removed_this_frame = starting_car_count - len(cars) + cars_spawned_this_frame
    
        # Draw the map
        screen.blit(scaled_map_surface, (0, 0))
        
        # Only draw cars that would be visible on screen for efficiency
        for car in cars:
            if car.rect.colliderect(pygame.Rect(0, 0, width, height)):
                screen.blit(car.image, car.rect)
        
        # Draw traffic lights
        for light in traffic_lights:
            draw_traffic_light(screen, light['pos'], light['red'], light['yellow'], light['green'], light['direction'])
        
        # Display lane counters and stats
        draw_lane_counters(screen)
        
        # Always show car count
        cars_text = font.render(f"Cars: {len(cars)}/{MAX_CARS}", True, (255, 255, 255))
        screen.blit(cars_text, (width - 150, 20))
        
        # Debug information if enabled
        if debug_mode:
            visible_cars = sum(1 for car in cars if car.rect.colliderect(pygame.Rect(0, 0, width, height)))
            moving_cars = sum(1 for car in cars if car.moving)
            
            debug_text = [
                f"FPS: {int(clock.get_fps())}",
                f"Visible cars: {visible_cars}",
                f"Total cars: {len(cars)}",
                f"Moving cars: {moving_cars}",
                f"Spawned this frame: {cars_spawned_this_frame}",
                f"Removed this frame: {cars_removed_this_frame}",
                f"Next cleanup in: {int(cleanup_interval - (time.time() - last_cleanup_time))}s"
            ]
            
            for i, text in enumerate(debug_text):
                debug_surface = font.render(text, True, (255, 255, 0))
                screen.blit(debug_surface, (10, height - 30 - i * 25))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()