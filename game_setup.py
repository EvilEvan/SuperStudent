"""
Module: game_setup
This module handles game initialization and resource setup for Super Student.
"""

import pygame
import random
import math
from settings import (
    COLORS_COLLISION_DELAY, DISPLAY_MODES, DEFAULT_MODE, DISPLAY_SETTINGS_PATH,
    LEVEL_PROGRESS_PATH, MAX_CRACKS, WHITE, BLACK, FLAME_COLORS, LASER_EFFECTS,
    LETTER_SPAWN_INTERVAL, SEQUENCES, GAME_MODES, GROUP_SIZE,
    SHAKE_DURATION_MISCLICK, SHAKE_MAGNITUDE_MISCLICK,
    GAME_OVER_CLICK_DELAY, GAME_OVER_COUNTDOWN_SECONDS,
    DEBUG_MODE, SHOW_FPS, FONT_SIZES, MOTHER_RADIUS
)
from welcome_display import welcome_screen_content
from level_selection import level_menu_content
from colors_level import run_colors_level

from utils.resource_manager import ResourceManager
from utils.particle_system import ParticleManager

# Initialize pygame
pygame.init()

pygame.event.set_allowed([
    pygame.FINGERDOWN,
    pygame.FINGERUP,
    pygame.FINGERMOTION,
    pygame.QUIT,
    pygame.KEYDOWN,
    pygame.MOUSEBUTTONDOWN,
    pygame.MOUSEBUTTONUP,
])

# Set up display
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Super Student")


def detect_display_type():
    info = pygame.display.Info()
    screen_w, screen_h = info.current_w, info.current_h
    if screen_w >= 1920 and screen_h >= 1080:
        if screen_w > 2560 or screen_h > 1440:
            return "QBOARD"
    return "DEFAULT"

# Determine display mode
DISPLAY_MODE = DEFAULT_MODE
try:
    with open(DISPLAY_SETTINGS_PATH, "r") as f:
        loaded_mode = f.read().strip()
        if loaded_mode in DISPLAY_MODES:
            DISPLAY_MODE = loaded_mode
except Exception as e:
    DISPLAY_MODE = detect_display_type()

# Global particle manager placeholder
particle_manager = None


def init_resources():
    global font_sizes, fonts, large_font, small_font, TARGET_FONT, TITLE_FONT
    global MAX_PARTICLES, MAX_EXPLOSIONS, MAX_SWIRL_PARTICLES, particle_manager

    # Import settings for resource limits
    from settings import MAX_PARTICLES as PARTICLES_SETTINGS, MAX_EXPLOSIONS as EXPLOSIONS_SETTINGS, MAX_SWIRL_PARTICLES as SWIRL_SETTINGS

    resource_manager = ResourceManager()
    resource_manager.set_display_mode(DISPLAY_MODE)
    MAX_PARTICLES = PARTICLES_SETTINGS[DISPLAY_MODE]
    MAX_EXPLOSIONS = EXPLOSIONS_SETTINGS[DISPLAY_MODE]
    MAX_SWIRL_PARTICLES = SWIRL_SETTINGS[DISPLAY_MODE]
    font_sizes = FONT_SIZES[DISPLAY_MODE]["regular"]
    resources = resource_manager.initialize_game_resources()
    fonts = resources['fonts']
    large_font = resources['large_font']
    small_font = resources['small_font']
    TARGET_FONT = resources['target_font']
    TITLE_FONT = resources['title_font']
    
    particle_manager = ParticleManager(max_particles=MAX_PARTICLES)
    particle_manager.set_culling_distance(WIDTH)
    
    try:
        with open(DISPLAY_SETTINGS_PATH, "w") as f:
            f.write(DISPLAY_MODE)
    except Exception as e:
        pass
    print(f"Resources initialized for display mode: {DISPLAY_MODE}")
    return resource_manager

# Initialize resources on module import
resource_manager = init_resources()

# Expose key variables
__all__ = ['screen', 'WIDTH', 'HEIGHT', 'DISPLAY_MODE', 'init_resources', 'resource_manager', 'detect_display_type'] 