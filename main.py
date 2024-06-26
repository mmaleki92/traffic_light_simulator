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
        direction = random.choice(['vertical', 'horizontal'])
        road_width = 100
        lane_width = road_width // 2
        quarter_lane = lane_width // 4  # Define quarter of a lane for precise positioning
        
        if direction == 'vertical':
            # Base lane position is the center of each lane
            lane_base = width // 2 - lane_width // 2 if random.choice([True, False]) else width // 2 + lane_width // 2
            if random.choice([True, False]):
                # Spawning from top, use right half of the lane
                y_position = -30
                speed = 2
                lane_position = lane_base + 3 * quarter_lane  # Adjusted for the right half of the lane
                lane_counters['top'] += 1

            else:
                # Spawning from bottom, use left half of the lane
                y_position = height + 30
                speed = -2
                lane_position = lane_base + quarter_lane  # Adjusted for the left half of the lane
                lane_counters['bottom'] += 1

            car = Car(lane_position, y_position, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), speed, 'vertical')
        
        else:
            # Base lane position is the center of each lane
            lane_base = height // 2 - lane_width // 2 if random.choice([True, False]) else height // 2 + lane_width // 2
            if random.choice([True, False]):
                # Spawning from left, use right half of the lane
                x_position = -30
                speed = 2
                lane_position = lane_base + 3 * quarter_lane  # Adjusted for the right half of the lane
                lane_counters['left'] += 1
            else:
                # Spawning from right, use left half of the lane
                x_position = width + 30
                speed = -2
                lane_position = lane_base + quarter_lane  # Adjusted for the left half of the lane
                lane_counters['right'] += 1

            car = Car(x_position, lane_position, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), speed, 'horizontal')

        cars.append(car)
        print(f"Added {direction} car at: {lane_position}, {'top' if speed > 0 else 'bottom' if direction == 'vertical' else 'right' if speed > 0 else 'left'} with speed {speed}")


def manage_traffic_lights(cars, lights):
    for car in cars:
        car.moving = True  # Assume the car can move unless a light says otherwise
        for light in lights:
            if car.direction == 'horizontal' and light['vertical'] and not light['green']:
                if light['pos'][0] - 150 <= car.rect.right < light['pos'][0] + 150:
                    car.moving = False
            elif car.direction == 'vertical' and not light['vertical'] and not light['green']:
                if light['pos'][1] - 150 <= car.rect.bottom < light['pos'][1] + 150:
                    car.moving = False


cars = [
    Car(width // 4, height // 2 - 10, (0, 0, 255), 2),  # Blue car
    Car(width // 4, height // 2 + 30, (255, 0, 0), 2)   # Red car
]

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
        {'pos': (width // 2 - 30, height // 2 - 120), 'red': False, 'yellow': False, 'green': True, 'vertical': True},
        {'pos': (width // 2 - 30, height // 2 + 100), 'red': False, 'yellow': False, 'green': True, 'vertical': True},
        {'pos': (width // 2 - 120, height // 2 - 30), 'red': False, 'yellow': True, 'green': True, 'vertical': False},
        {'pos': (width // 2 + 100, height // 2 - 30), 'red': False, 'yellow': False, 'green': True, 'vertical': False}
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
            draw_traffic_light(screen, light['pos'], light['red'], light['yellow'], light['green'], light.get('vertical', False))
        # light['green'] = random.choice([True, False])
        # light['green'] = True
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
