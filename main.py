import requests
import pygame
import sys
from settings import FPS, BLACK, width, height, traffic_lights
from draw_objects import draw_road, draw_traffic_light, Car
import random
import pygame
import pytmx

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
    'up-down': 60,  # Spawn a car every ~2 seconds (with 30 FPS)
    'down-up': 70,
    'left-right': 65,
    'right-left': 75
}
# Maximum number of cars (set this to a reasonable number based on your system performance)
MAX_CARS = 100

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
    global lane_counters, spawn_timers  # Use the global counters and timers
    
    # Don't spawn more cars if we've reached the maximum
    if len(cars) >= MAX_CARS:
        return
    
    # Update all spawn timers
    for direction in spawn_timers:
        spawn_timers[direction] += 1
    
    # Try to spawn cars for each direction if timer is up
    for direction in spawn_timers:
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
                    y_position = -20
                    speed = 2
                    lane_position = lane_base_left + lane_width // 2 - 14
                    lane_counters['top'] += 1
                else:
                    y_position = height + 30
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
                    x_position = -30
                    speed = 2
                    lane_position = lane_base_bottom + lane_width // 2 
                    lane_counters['left'] += 1
                else:
                    x_position = width + 30
                    speed = -2
                    lane_position = lane_base_top + lane_width // 2 -10
                    lane_counters['right'] += 1

                car = Car(x_position, lane_position, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), speed, 'horizontal', direction)

            cars.add(car)  # Use add() instead of append()
            update_lane_counters(lane_counters)
            print(f"Added car: {direction} at: {lane_position} with speed {speed}")

def manage_traffic_lights(cars, lights):
    stop_distance = 50
    for car in cars:
        car.moving = True
        for light in lights:
            if car.direction == 'horizontal' and car.spawn_direction in ['left-right', 'right-left']:
                if car.spawn_direction == 'left-right' and light['direction'] == 'left':
                    if not light['green'] and light['pos'][0] - stop_distance <= car.rect.right < light['pos'][0] + stop_distance:
                        car.moving = False
                        break
                elif car.spawn_direction == 'right-left' and light['direction'] == 'right':
                    if not light['green'] and light['pos'][0] - stop_distance <= car.rect.left < light['pos'][0] + stop_distance:
                        car.moving = False
                        break
            elif car.direction == 'vertical' and car.spawn_direction in ['up-down', 'down-up']:
                if car.spawn_direction == 'up-down' and light['direction'] == 'up':
                    if not light['green'] and light['pos'][1] - stop_distance <= car.rect.bottom < light['pos'][1] + stop_distance:
                        car.moving = False
                        break
                elif car.spawn_direction == 'down-up' and light['direction'] == 'down':
                    if not light['green'] and light['pos'][1] - stop_distance <= car.rect.top < light['pos'][1] + stop_distance:
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

    # Display stats
    font = pygame.font.Font(None, 24)

    while running:
        screen.fill(BLACK)
        draw_lane_counters(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Spawn cars with our new deterministic approach
        spawn_cars(cars)
        
        # Display number of cars
        cars_text = font.render(f"Cars: {len(cars)}/{MAX_CARS}", True, (255, 255, 255))
        screen.blit(cars_text, (width - 150, 20))

        manage_traffic_lights(cars, traffic_lights)
        traffic_lights = fetch_traffic_lights()

        if check_for_accidents(traffic_lights):
            log_accident(True, "Warning: Potential accident! Both vertical and horizontal lanes have green lights!")
        
        # Update all cars
        for car in list(cars):  # Make a copy of the cars list for safe iteration
            car.update(cars)
            
            # Check if car is out of bounds and remove if necessary
            if car.is_out_of_bounds(width, height):
                cars.remove(car)  # Remove the car if it is out of bounds
        
        # Draw the map and all the objects
        screen.blit(scaled_map_surface, (0, 0))
        cars.draw(screen)
        for light in traffic_lights:
            draw_traffic_light(screen, light['pos'], light['red'], light['yellow'], light['green'], light['direction'])
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()