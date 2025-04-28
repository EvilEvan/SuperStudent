"""
SuperStudent - Game Settings

This module contains all the constants and settings used throughout the game.
Centralizing settings here makes it easier to tune parameters and optimize performance.
"""
import pygame

# Display settings
DISPLAY_MODES = ["DEFAULT", "QBOARD"]
DEFAULT_MODE = "DEFAULT"

# Screen dimensions are determined at runtime, but we set defaults
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600

# Performance settings
FPS = 50
MAX_PARTICLES = {
    "DEFAULT": 200,
    "QBOARD": 400
}
MAX_EXPLOSIONS = {
    "DEFAULT": 5,
    "QBOARD": 10
}
MAX_SWIRL_PARTICLES = {
    "DEFAULT": 75,
    "QBOARD": 150
}
PARTICLE_CULLING_DISTANCE = DEFAULT_WIDTH  # Distance at which to cull offscreen particles
ENABLE_COLLISION_GRID = True  # Use spatial partitioning for collision detection
COLLISION_GRID_SIZE = 100  # Size of grid cells for spatial partitioning
COLORS_COLLISION_DELAY = 250  # Frames to wait before enabling collisions between dots in colors level (5 seconds at 50 FPS)

# Game timing constants
LETTER_SPAWN_INTERVAL = 30  # spawn interval in frames
VIBRATION_FRAMES = 30
DISPERSE_FRAMES = 30
CHECKPOINT_TRIGGER = 10  # Show checkpoint screen every 10 targets in Colors level

# Game constants
MAX_CRACKS = 15  # Number of cracks needed to shatter screen

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FLAME_COLORS = [
    (255, 69, 0),    # OrangeRed
    (255, 140, 0),   # DarkOrange
    (255, 165, 0),   # Orange
    (255, 215, 0),   # Gold
    (255, 255, 0),   # Yellow
    (138, 43, 226),  # BlueViolet
    (75, 0, 130),    # Indigo
    (65, 105, 225)   # RoyalBlue
]

# Colors level specific colors
COLORS_LIST = [
    (0, 0, 255),    # Blue
    (255, 0, 0),    # Red
    (0, 200, 0),    # Green
    (255, 255, 0),  # Yellow
    (128, 0, 255),  # Purple
]
COLOR_NAMES = ["Blue", "Red", "Green", "Yellow", "Purple"]

# Font sizes per display mode
FONT_SIZES = {
    "DEFAULT": {
        "regular": [130, 135, 140, 145, 105],
        "large": 150,
        "small": 36,
        "target": 210,
        "title": 320
    },
    "QBOARD": {
        "regular": [260, 270, 280, 290, 210],
        "large": 300,
        "small": 36,
        "target": 420,
        "title": 640
    }
}

# Mother dot radius based on display mode
MOTHER_RADIUS = {
    "DEFAULT": 90,
    "QBOARD": 180
}

# Dot properties
DOT_RADIUS = 24
DOT_SPEED_RANGE = (-6, 6)
DOT_SPEED_REDUCTION = 0.8  # 20% speed reduction on collision

# Laser effects
LASER_EFFECTS = [
    {"colors": FLAME_COLORS, "widths": [120, 140, 160, 180], "type": "flamethrower"},
    {"colors": [(173, 216, 230), (135, 206, 250)], "widths": [30, 50], "type": "ice"},
    {"colors": [(255, 20, 147), (255, 105, 180)], "widths": [40, 60], "type": "pink_magic"},
]

# Paths
LEVEL_PROGRESS_PATH = "level_progress.txt"
DISPLAY_SETTINGS_PATH = "display_settings.txt"

# Game modes
GAME_MODES = ["alphabet", "numbers", "shapes", "clcase", "colors"]

# Sequence definitions
SEQUENCES = {
    "alphabet": list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    "numbers": [str(i) for i in range(1, 27)],
    "shapes": ["Rectangle", "Square", "Circle", "Triangle", "Pentagon"],
    "clcase": list("abcdefghijklmnopqrstuvwxyz"),
    "colors": []  # Colors mode doesn't use sequence logic
}

# Groups per mode
GROUP_SIZE = 5  # Number of items per group

# Debug settings
DEBUG_MODE = False
SHOW_FPS = False
SHOW_COLLISION_GRID = False 