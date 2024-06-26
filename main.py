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
    road_width = 50
    lane_width = road_width // 2
    # Draw the vertical and horizontal roads
    pygame.draw.rect(screen, GRAY, (width // 2 - road_width, 0, road_width * 2, height))
    pygame.draw.rect(screen, GRAY, (0, height // 2 - road_width, width, road_width * 2))

    # Dashed lines for the roads
    for y in range(0, height, 20):
        pygame.draw.line(screen, WHITE, (width // 2, y), (width // 2, y + 10), 2)
    for x in range(0, width, 20):
        pygame.draw.line(screen, WHITE, (x, height // 2), (x + 10, height // 2), 2)

    # Corrected lane arrows for vertical road
    # Left lane arrows (pointing upwards)
    draw_arrow(screen, WHITE, (width // 2 - lane_width, 3 * height // 4 + 30), (width // 2 - lane_width, 3 * height // 4))
    draw_arrow(screen, WHITE, (width // 2 - lane_width, height // 4 + 30), (width // 2 - lane_width, height // 4))

    # Right lane arrows (pointing downwards)
    draw_arrow(screen, WHITE, (width // 2 + lane_width, height // 4 - 30), (width // 2 + lane_width, height // 4))
    draw_arrow(screen, WHITE, (width // 2 + lane_width, 3 * height // 4 - 30), (width // 2 + lane_width, 3 * height // 4))

    # Horizontal road arrows (already corrected previously)
    draw_arrow(screen, WHITE, (width // 4, height // 2 - lane_width), (width // 4 + 30, height // 2 - lane_width))  # Left
    draw_arrow(screen, WHITE, (3 * width // 4 + 30, height // 2 + lane_width), (3 * width // 4, height // 2 + lane_width))  # Right
    draw_arrow(screen, WHITE, (width // 4 - 30, height // 2 + lane_width), (width // 4, height // 2 + lane_width))  # Left opposite lane
    draw_arrow(screen, WHITE, (3 * width // 4, height // 2 - lane_width), (3 * width // 4 + 30, height // 2 - lane_width))  # Right opposite lane

def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type is pygame.QUIT:
                running = False

        screen.fill(BLACK)
        draw_road()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
