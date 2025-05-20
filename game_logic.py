"""
Module: game_logic
This module contains game loop and effect functions for Super Student.
Extracted from SuperStudent.py for better modularity.
"""

import pygame
import random
import math

from game_setup import screen, WIDTH, HEIGHT, DISPLAY_MODE, resource_manager
from settings import WHITE, BLACK, FLAME_COLORS, COLORS_COLLISION_DELAY

# Global state variables for game effects and logic
particle_pool = []
particles = []
shake_duration = 0
shake_magnitude = 10
active_touches = {}
explosions = []
lasers = []
glass_cracks = []
background_shattered = False
CRACK_DURATION = 600
shatter_timer = 0
opposite_background = BLACK
current_background = WHITE

game_over_triggered = False
game_over_delay = 0
GAME_OVER_DELAY_FRAMES = 60
player_color_transition = 0
player_current_color = FLAME_COLORS[0]
player_next_color = FLAME_COLORS[1]

charging_ability = False
charge_timer = 0
charge_particles = []
ability_target = None
swirl_particles = []
particles_converging = False
convergence_target = None
convergence_timer = 0


def create_particle(x, y, color, size, dx, dy, duration):
    """Creates a new particle and adds it to the global particles list."""
    particle = {"x": x, "y": y, "color": color, "size": size, "dx": dx, "dy": dy, "duration": duration}
    particles.append(particle)
    return particle


def create_crack(x, y):
    """Creates a crack effect at the given coordinates."""
    crack = {"x": x, "y": y, "duration": CRACK_DURATION}
    glass_cracks.append(crack)
    return crack


def draw_cracks(surface):
    """Draws all active cracks onto the provided surface."""
    for crack in glass_cracks:
        # Placeholder: drawing a small circle for each crack
        pygame.draw.circle(surface, BLACK, (crack["x"], crack["y"]), 5)


def create_explosion(x, y, color=None, max_radius=270, duration=30):
    """Creates an explosion effect at the given coordinates."""
    explosion = {"x": x, "y": y, "color": color if color else WHITE, "max_radius": max_radius, "duration": duration}
    explosions.append(explosion)
    return explosion


def handle_misclick(x, y):
    """Handles a misclick event by triggering visual feedback."""
    create_crack(x, y)
    create_explosion(x, y)


def draw_explosion(explosion, offset_x=0, offset_y=0):
    """Draws the explosion effect on the screen."""
    pygame.draw.circle(screen, explosion["color"], (explosion["x"] + offset_x, explosion["y"] + offset_y), 10)


def create_flame_effect(start_x, start_y, end_x, end_y):
    """Creates a flame effect from a start point to an end point."""
    flame = {"start": (start_x, start_y), "end": (end_x, end_y)}
    lasers.append(flame)
    return flame


def draw_flamethrower(laser, offset_x=0, offset_y=0):
    """Draws a flamethrower effect (laser) with an offset."""
    start = (laser["start"][0] + offset_x, laser["start"][1] + offset_y)
    end = (laser["end"][0] + offset_x, laser["end"][1] + offset_y)
    pygame.draw.line(screen, BLACK, start, end, 3)


def game_over_screen():
    """Displays the game over screen."""
    font = pygame.font.SysFont(None, 48)
    text = font.render("Game Over", True, BLACK)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(2000)


def game_loop(mode):
    """Main game loop."""
    global shake_duration, shake_magnitude, particles, active_touches, explosions, lasers, player_color_transition, player_current_color, player_next_color, charging_ability, charge_timer, charge_particles, ability_target, swirl_particles, particles_converging, convergence_target, convergence_timer, glass_cracks, background_shattered, shatter_timer

    # Reset game state
    shake_duration = 0
    shake_magnitude = 0
    particles = []
    explosions = []
    lasers = []
    active_touches.clear()
    glass_cracks.clear()
    background_shattered = False
    shatter_timer = 0
    convergence_timer = 0
    charge_timer = 0
    convergence_target = None
    player_color_transition = 0

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Additional event handling can be added here

        screen.fill(current_background)
        # Draw game effects
        draw_cracks(screen)
        for explosion in explosions:
            draw_explosion(explosion)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    game_loop(DISPLAY_MODE) 