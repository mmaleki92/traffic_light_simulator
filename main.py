import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 600, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Crossroad Simulation")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

# Frame rate
clock = pygame.time.Clock()
def draw_traffic_light(surface, pos, red_on, yellow_on, green_on, vertical=False):
    light_width, light_height = (20, 60) if not vertical else (60, 20)
    padding = 3
    circle_radius = 6
    black = (0, 0, 0)
    gray = (50, 50, 50)
    red = (255, 0, 0) if red_on else gray
    yellow = (255, 255, 0) if yellow_on else gray
    green = (0, 255, 0) if green_on else gray

    # Draw the traffic light box
    light_rect = pygame.Rect(pos[0], pos[1], light_width, light_height)
    pygame.draw.rect(surface, black, light_rect)

    # Calculate and draw the traffic light circles
    if vertical:
        # Horizontal layout
        start_x = pos[0] + padding + circle_radius
        y = pos[1] + light_height // 2
        pygame.draw.circle(surface, red, (start_x, y), circle_radius)
        pygame.draw.circle(surface, yellow, (start_x + 2 * (padding + circle_radius), y), circle_radius)
        pygame.draw.circle(surface, green, (start_x + 4 * (padding + circle_radius), y), circle_radius)
    else:
        # Vertical layout
        start_y = pos[1] + padding + circle_radius
        x = pos[0] + light_width // 2
        pygame.draw.circle(surface, red, (x, start_y), circle_radius)
        pygame.draw.circle(surface, yellow, (x, start_y + 2 * (padding + circle_radius)), circle_radius)
        pygame.draw.circle(surface, green, (x, start_y + 4 * (padding + circle_radius)), circle_radius)

def draw_arrow(surface, color, start, end, arrow_size=15, opacity=153):
    # Create a new surface with the same size as the main screen but with per-pixel alpha
    arrow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    # Set opacity (153 out of 255 for about 60% opacity)
    # Draw the line and arrowhead
    pygame.draw.line(arrow_surface, color + (opacity,), start, end, 2)
    rotation = pygame.math.Vector2(start) - pygame.math.Vector2(end)
    rotation.scale_to_length(arrow_size)
    right = rotation.rotate(-45) + pygame.math.Vector2(end)
    left = rotation.rotate(45) + pygame.math.Vector2(end)
    pygame.draw.polygon(arrow_surface, color + (opacity,), [end, right, left])

    # Blit the arrow surface onto the main surface
    surface.blit(arrow_surface, (0, 0))


def draw_road():
    road_width = 100  # Increased road width
    lane_width = road_width // 2
    # Draw the vertical and horizontal roads
    pygame.draw.rect(screen, GRAY, (width // 2 - road_width, 0, road_width * 2, height))
    pygame.draw.rect(screen, GRAY, (0, height // 2 - road_width, width, road_width * 2))

    # Dashed lines for the roads
    for y in range(0, height, 40):  # Adjust spacing for larger roads
        pygame.draw.line(screen, WHITE, (width // 2, y), (width // 2, y + 20), 3)  # Thicker lines
    for x in range(0, width, 40):
        pygame.draw.line(screen, WHITE, (x, height // 2), (x + 20, height // 2), 3)  # Thicker lines

    # Corrected lane arrows for vertical road
    # Left lane arrows (pointing upwards)
    # draw_arrow(screen, WHITE, (width // 2 - lane_width, 3 * height // 4 + 30), (width // 2 - lane_width, 3 * height // 4))
    # draw_arrow(screen, WHITE, (width // 2 - lane_width, height // 4 + 30), (width // 2 - lane_width, height // 4))

    # # Right lane arrows (pointing downwards)
    # draw_arrow(screen, WHITE, (width // 2 + lane_width, height // 4 - 30), (width // 2 + lane_width, height // 4))
    # draw_arrow(screen, WHITE, (width // 2 + lane_width, 3 * height // 4 - 30), (width // 2 + lane_width, 3 * height // 4))

    # # Horizontal road arrows (already corrected previously)
    # draw_arrow(screen, WHITE, (width // 4, height // 2 - lane_width), (width // 4 + 30, height // 2 - lane_width))  # Left
    # draw_arrow(screen, WHITE, (3 * width // 4 + 30, height // 2 + lane_width), (3 * width // 4, height // 2 + lane_width))  # Right
    # draw_arrow(screen, WHITE, (width // 4 - 30, height // 2 + lane_width), (width // 4, height // 2 + lane_width))  # Left opposite lane
    # draw_arrow(screen, WHITE, (3 * width // 4, height // 2 - lane_width), (3 * width // 4 + 30, height // 2 - lane_width))  # Right opposite lane

def main():
    running = True
    # Initial traffic light status with orientation specified
    lights = [
        {'pos': (width // 2 - 30, height // 2 - 120), 'red': True, 'yellow': False, 'green': False, 'vertical': True},
        {'pos': (width // 2 - 30, height // 2 + 100), 'red': False, 'yellow': False, 'green': True, 'vertical': True},
        {'pos': (width // 2 - 120, height // 2 - 30), 'red': False, 'yellow': True, 'green': False, 'vertical': False},
        {'pos': (width // 2 + 100, height // 2 - 30), 'red': False, 'yellow': False, 'green': True, 'vertical': False}
    ]

    while running:
        for event in pygame.event.get():
            if event.type is pygame.QUIT:
                running = False

        screen.fill(BLACK)
        draw_road()
        # Draw each traffic light
        for light in lights:
            draw_traffic_light(screen, light['pos'], light['red'], light['yellow'], light['green'], light.get('vertical', False))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
