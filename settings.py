# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
FPS = 60
width, height = 600, 600


# Initial traffic light status with orientation specified
traffic_lights = [
    {'id': 1, 'pos': (width // 2 - 30, height // 2 - 120), 'red': True, 'yellow': False, 'green': False, 'direction': 'up'},
    {'id': 2, 'pos': (width // 2 - 120, height // 2 - 30), 'red': True, 'yellow': True, 'green': False, 'direction': 'left'},
    {'id': 3, 'pos': (width // 2 - 30, height // 2 + 100), 'red': True, 'yellow': False, 'green': False, 'direction': 'down'},
    {'id': 4, 'pos': (width // 2 + 100, height // 2 - 30), 'red': True, 'yellow': False, 'green': False, 'direction': 'right'}
]