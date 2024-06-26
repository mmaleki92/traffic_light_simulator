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
            else:
                # Spawning from bottom, use left half of the lane
                y_position = height + 30
                speed = -2
                lane_position = lane_base + quarter_lane  # Adjusted for the left half of the lane
            car = Car(lane_position, y_position, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), speed, 'vertical')
        
        else:
            # Base lane position is the center of each lane
            lane_base = height // 2 - lane_width // 2 if random.choice([True, False]) else height // 2 + lane_width // 2
            if random.choice([True, False]):
                # Spawning from left, use right half of the lane
                x_position = -30
                speed = 2
                lane_position = lane_base + 3 * quarter_lane  # Adjusted for the right half of the lane
            else:
                # Spawning from right, use left half of the lane
                x_position = width + 30
                speed = -2
                lane_position = lane_base + quarter_lane  # Adjusted for the left half of the lane
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

# Frame rate
clock = pygame.time.Clock()

def main():
    running = True
    # Initial traffic light status with orientation specified
    lights = [
        {'pos': (width // 2 - 30, height // 2 - 120), 'red': False, 'yellow': False, 'green': False, 'vertical': True},
        {'pos': (width // 2 - 30, height // 2 + 100), 'red': False, 'yellow': False, 'green': False, 'vertical': True},
        {'pos': (width // 2 - 120, height // 2 - 30), 'red': False, 'yellow': True, 'green': False, 'vertical': False},
        {'pos': (width // 2 + 100, height // 2 - 30), 'red': False, 'yellow': False, 'green': False, 'vertical': False}
    ]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)
        draw_road(screen)

        spawn_cars(cars, spawn_rate=0.05)  # Adjust spawn rate as needed

        manage_traffic_lights(cars, lights)

        # Check and remove out-of-bounds cars, then draw remaining cars
        for car in cars[:]:  # Iterate over a copy of the list
            car.move()
            if car.is_out_of_bounds(width, height):
                cars.remove(car)
            else:
                car.draw(screen)
        for light in lights:
            draw_traffic_light(screen, light['pos'], light['red'], light['yellow'], light['green'], light.get('vertical', False))
        
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
