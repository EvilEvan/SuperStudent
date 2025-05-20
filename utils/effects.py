"""
Visual effects module for SuperStudent game.
Handles particles, cracks, explosions, and other visual effects.
"""
import pygame
import random
import math
from settings import (
    WHITE, BLACK, FLAME_COLORS, LASER_EFFECTS,
    SHAKE_DURATION_MISCLICK, SHAKE_MAGNITUDE_MISCLICK,
    MAX_CRACKS, CRACK_DURATION
)

class EffectsManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.particles = []
        self.explosions = []
        self.lasers = []
        self.glass_cracks = []
        self.background_shattered = False
        self.shatter_timer = 0
        self.opposite_background = BLACK
        self.current_background = WHITE
        self.shake_duration = 0
        self.shake_magnitude = 0

    def create_particle(self, x, y, color, size, dx, dy, duration):
        """Create a new particle effect."""
        self.particles.append({
            "x": x, "y": y, "color": color, "size": size,
            "dx": dx, "dy": dy, "duration": duration,
            "start_duration": duration, "active": True
        })

    def create_crack(self, x, y):
        """Create a new glass crack effect."""
        if len(self.glass_cracks) >= MAX_CRACKS:
            self.background_shattered = True
            self.shatter_timer = CRACK_DURATION
            return

        angle = random.uniform(0, 2 * math.pi)
        length = random.randint(50, 150)
        self.glass_cracks.append({
            "x": x, "y": y, "angle": angle,
            "length": length, "duration": CRACK_DURATION
        })

    def create_explosion(self, x, y, color=None, max_radius=270, duration=30):
        """Create an explosion effect."""
        if color is None:
            color = random.choice(FLAME_COLORS)
        self.explosions.append({
            "x": x, "y": y, "color": color,
            "radius": 0, "max_radius": max_radius,
            "duration": duration, "start_duration": duration
        })

    def create_flame_effect(self, start_x, start_y, end_x, end_y):
        """Create a flame effect between two points."""
        self.lasers.append({
            "start_x": start_x, "start_y": start_y,
            "end_x": end_x, "end_y": end_y,
            "color": random.choice(FLAME_COLORS),
            "duration": 10
        })

    def handle_misclick(self, x, y):
        """Handle a misclick by creating effects."""
        self.create_crack(x, y)
        self.create_explosion(x, y)
        self.shake_duration = SHAKE_DURATION_MISCLICK
        self.shake_magnitude = SHAKE_MAGNITUDE_MISCLICK

    def update(self):
        """Update all effects."""
        # Update particles
        for particle in self.particles[:]:
            particle["duration"] -= 1
            if particle["duration"] <= 0:
                self.particles.remove(particle)
                continue
            particle["x"] += particle["dx"]
            particle["y"] += particle["dy"]
            particle["size"] *= 0.95

        # Update explosions
        for explosion in self.explosions[:]:
            explosion["duration"] -= 1
            if explosion["duration"] <= 0:
                self.explosions.remove(explosion)
                continue
            progress = 1 - (explosion["duration"] / explosion["start_duration"])
            explosion["radius"] = explosion["max_radius"] * progress

        # Update lasers
        for laser in self.lasers[:]:
            laser["duration"] -= 1
            if laser["duration"] <= 0:
                self.lasers.remove(laser)

        # Update cracks
        for crack in self.glass_cracks[:]:
            crack["duration"] -= 1
            if crack["duration"] <= 0:
                self.glass_cracks.remove(crack)

        # Update shatter timer
        if self.background_shattered:
            self.shatter_timer -= 1
            if self.shatter_timer <= 0:
                self.background_shattered = False
                self.current_background, self.opposite_background = self.opposite_background, self.current_background

        # Update screen shake
        if self.shake_duration > 0:
            self.shake_duration -= 1

    def draw(self, surface):
        """Draw all effects to the surface."""
        # Draw background
        surface.fill(self.current_background)

        # Draw cracks
        for crack in self.glass_cracks:
            end_x = crack["x"] + math.cos(crack["angle"]) * crack["length"]
            end_y = crack["y"] + math.sin(crack["angle"]) * crack["length"]
            pygame.draw.line(surface, BLACK, (crack["x"], crack["y"]), (end_x, end_y), 2)

        # Draw particles
        for particle in self.particles:
            pygame.draw.circle(surface, particle["color"],
                             (int(particle["x"]), int(particle["y"])),
                             int(particle["size"]))

        # Draw explosions
        for explosion in self.explosions:
            pygame.draw.circle(surface, explosion["color"],
                             (int(explosion["x"]), int(explosion["y"])),
                             int(explosion["radius"]))

        # Draw lasers
        for laser in self.lasers:
            pygame.draw.line(surface, laser["color"],
                           (laser["start_x"], laser["start_y"]),
                           (laser["end_x"], laser["end_y"]), 3)

    def get_shake_offset(self):
        """Get the current screen shake offset."""
        if self.shake_duration > 0:
            return (random.randint(-self.shake_magnitude, self.shake_magnitude),
                   random.randint(-self.shake_magnitude, self.shake_magnitude))
        return (0, 0)

    def get_background_state(self):
        """Get the current background state."""
        return {
            "background_shattered": self.background_shattered,
            "current_background": self.current_background,
            "opposite_background": self.opposite_background,
            "shatter_timer": self.shatter_timer
        }

    def set_background_state(self, is_shattered, current_bg, opposite_bg, timer_val):
        """Set the background state."""
        self.background_shattered = is_shattered
        self.current_background = current_bg
        self.opposite_background = opposite_bg
        self.shatter_timer = timer_val

# Standalone functions for backward compatibility
def create_explosion(x, y, color=None, max_radius=270, duration=30):
    """
    Backward compatibility function for create_explosion.
    This will be removed in future versions.
    """
    import warnings
    warnings.warn(
        "Direct call to create_explosion is deprecated. Use Effects.create_explosion instead.",
        DeprecationWarning, stacklevel=2
    )
    # Create a temporary effects object (inefficient, for compatibility only)
    temp_effects = EffectsManager(800, 600)  # Use default size
    return temp_effects.create_explosion(x, y, color, max_radius, duration) 