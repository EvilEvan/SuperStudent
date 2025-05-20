"""
Settings module for SuperStudent game.
Contains game constants and configuration.
"""

from .display import DEFAULT_MODE, detect_display_type

# Game constants
FPS = 60
MAX_PARTICLES = 1000
MAX_EXPLOSIONS = 10
MAX_GLASS_CRACKS = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# Game settings
DEFAULT_LIVES = 3
DEFAULT_SCORE = 0
LEVEL_TIMEOUT = 60  # seconds

__all__ = [
    'FPS',
    'MAX_PARTICLES',
    'MAX_EXPLOSIONS',
    'MAX_GLASS_CRACKS',
    'WHITE',
    'BLACK',
    'RED',
    'GREEN',
    'BLUE',
    'YELLOW',
    'CYAN',
    'MAGENTA',
    'DEFAULT_LIVES',
    'DEFAULT_SCORE',
    'LEVEL_TIMEOUT',
    'DEFAULT_MODE',
    'detect_display_type'
] 