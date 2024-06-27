import requests
import pygame
import sys
from settings import FPS, BLACK, width, height
from draw_objects import draw_road, draw_traffic_light, Car
import random

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

traffic_lights = [
    {'pos': (width // 2 - 30, height // 2 - 120), 'red': True, 'yellow': False, 'green': False, 'direction': 'up'},
    {'pos': (width // 2 - 30, height // 2 + 100), 'red': True, 'yellow': False, 'green': False, 'direction': 'down'},
    {'pos': (width // 2 - 120, height // 2 - 30), 'red': True, 'yellow': True, 'green': False, 'direction': 'left'},
    {'pos': (width // 2 + 100, height // 2 - 30), 'red': True, 'yellow': False, 'green': False, 'direction': 'right'}
]

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

def spawn_cars(cars, spawn_rate=0.1):
    global lane_counters  # Ensure we use the global lane_counters
    if random.random() < spawn_rate:
        direction = random.choice(['up-down', 'down-up', 'left-right', 'right-left'])
        road_width = 100
        lane_width = road_width // 2
        
        if direction in ['up-down', 'down-up']:
            lane_base_left = width // 2 - lane_width
            lane_base_right = width // 2 + lane_width
            if direction == 'up-down':
                y_position = -30
                speed = 2
                lane_position = lane_base_left + lane_width // 2
                lane_counters['top'] += 1
            else:
                y_position = height + 30
                speed = -2
                lane_position = lane_base_right - lane_width // 2
                lane_counters['bottom'] += 1

            car = Car(lane_position, y_position, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), speed, 'vertical', direction)
        
        else:
            lane_base_top = height // 2 - lane_width
            lane_base_bottom = height // 2 + lane_width
            if direction == 'left-right':
                x_position = -30
                speed = 2
                lane_position = lane_base_bottom - lane_width // 2
                lane_counters['left'] += 1
            else:
                x_position = width + 30
                speed = -2
                lane_position = lane_base_top + lane_width // 2
                lane_counters['right'] += 1

            car = Car(x_position, lane_position, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), speed, 'horizontal', direction)

        cars.append(car)
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

# Frame rate
clock = pygame.time.Clock()

def main():
    global lane_counters  # Ensure we use the global lane_counters
    global traffic_lights  # Ensure we use the global traffic_lights
    running = True
    lane_counters.update(fetch_lane_counters())
    traffic_lights = fetch_traffic_lights()
    
    while running:
        screen.fill(BLACK)

        draw_lane_counters(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_road(screen)

        spawn_cars(cars, spawn_rate=0.05)

        manage_traffic_lights(cars, traffic_lights)

        for car in cars[:]:
            car.move()
            if car.is_out_of_bounds(width, height):
                if car.direction == 'vertical':
                    if car.speed > 0:
                        lane_counters['top'] -= 1
                    else:
                        lane_counters['bottom'] -= 1
                else:
                    if car.speed > 0:
                        lane_counters['left'] -= 1
                    else:
                        lane_counters['right'] -= 1
                cars.remove(car)
                update_lane_counters(lane_counters)
            else:
                car.draw(screen)

        for light in traffic_lights:
            draw_traffic_light(screen, light['pos'], light['red'], light['yellow'], light['green'], light['direction'])

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    cars = []
    main()
