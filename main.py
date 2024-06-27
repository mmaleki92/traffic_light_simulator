"""
Morteza Maleki
github: mmaleki92
"""

import pygame
import sys
from settings import FPS, BLACK, width, height
from draw_objects import draw_road, draw_traffic_light, Car
import random

# Initialize Pygame
pygame.init()
# Initialize lane counters for each direction
lane_counters = {
    'top': 0,
    'bottom': 0,
    'left': 0,
    'right': 0
}

# Set up the display
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Crossroad Simulation")



def spawn_cars(cars, spawn_rate=0.1):
    if random.random() < spawn_rate:
        direction = random.choice(['up-down', 'down-up', 'left-right', 'right-left'])
        road_width = 100
        lane_width = road_width // 2
        
        if direction in ['up-down', 'down-up']:
            # Base lane position is the center of each lane
            lane_base_left = width // 2 - lane_width
            lane_base_right = width // 2 + lane_width
            if direction == 'up-down':
                # Spawning from top, use left lane
                y_position = -30
                speed = 2
                lane_position = lane_base_left + lane_width // 2  # Adjusted for the left lane
                lane_counters['top'] += 1
            else:
                # Spawning from bottom, use right lane
                y_position = height + 30
                speed = -2
                lane_position = lane_base_right - lane_width // 2  # Adjusted for the right lane
                lane_counters['bottom'] += 1

            car = Car(lane_position, y_position, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), speed, 'vertical', direction)
        
        else:
            # Base lane position is the center of each lane
            lane_base_top = height // 2 - lane_width
            lane_base_bottom = height // 2 + lane_width
            if direction == 'left-right':
                # Spawning from left, use bottom lane
                x_position = -30
                speed = 2
                lane_position = lane_base_bottom - lane_width // 2  # Adjusted for the bottom lane
                lane_counters['left'] += 1
            else:
                # Spawning from right, use top lane
                x_position = width + 30
                speed = -2
                lane_position = lane_base_top + lane_width // 2  # Adjusted for the top lane
                lane_counters['right'] += 1

            car = Car(x_position, lane_position, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), speed, 'horizontal', direction)

        cars.append(car)
        print(f"Added car: {direction} at: {lane_position} with speed {speed}")

def manage_traffic_lights(cars, lights):
    for car in cars:
        car.moving = True  # Assume the car can move unless a light says otherwise
        for light in lights:
            if car.direction == 'horizontal' and car.spawn_direction in ['left-right', 'right-left']:
                if car.spawn_direction == 'left-right' and light['direction'] == 'left':
                    if not light['green'] and light['pos'][0] - 150 <= car.rect.right < light['pos'][0] + 150:
                        car.moving = False
                        break
                elif car.spawn_direction == 'right-left' and light['direction'] == 'right':
                    if not light['green'] and light['pos'][0] - 150 <= car.rect.right < light['pos'][0] + 150:
                        car.moving = False
                        break
            elif car.direction == 'vertical' and car.spawn_direction in ['up-down', 'down-up']:
                if car.spawn_direction == 'up-down' and light['direction'] == 'up':
                    if not light['green'] and light['pos'][1] - 150 <= car.rect.bottom < light['pos'][1] + 150:
                        car.moving = False
                        break
                elif car.spawn_direction == 'down-up' and light['direction'] == 'down':
                    if not light['green'] and light['pos'][1] - 150 <= car.rect.bottom < light['pos'][1] + 150:
                        car.moving = False
                        break
cars = []

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
    running = True
    # Initial traffic light status with orientation specified
    lights = [
        {'pos': (width // 2 - 30, height // 2 - 120), 'red': False, 'yellow': False, 'green': True, 'direction': 'up'},
        {'pos': (width // 2 - 30, height // 2 + 100), 'red': True, 'yellow': False, 'green': False, 'direction': 'down'},
        {'pos': (width // 2 - 120, height // 2 - 30), 'red': False, 'yellow': True, 'green': True, 'direction': 'left'},
        {'pos': (width // 2 + 100, height // 2 - 30), 'red': False, 'yellow': False, 'green': True, 'direction': 'right'}
    ]

    while running:
        screen.fill(BLACK)

        draw_lane_counters(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_road(screen)

        spawn_cars(cars, spawn_rate=0.05)  # Adjust spawn rate as needed

        manage_traffic_lights(cars, lights)

        # Check and remove out-of-bounds cars, then draw remaining cars
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
            else:
                car.draw(screen)

        for light in lights:
            draw_traffic_light(screen, light['pos'], light['red'], light['yellow'], light['green'], light['direction'])
        
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
