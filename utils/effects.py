"""
SuperStudent - Visual Effects

This module provides visual effects like explosions, screen shake, cracks,
and other special effects for the game.
"""
import pygame
import random
import math
from settings import MAX_EXPLOSIONS, MAX_CRACKS

class Effects:
    """
    Manages visual effects like explosions, screen shake, and cracks.
    """
    
    def __init__(self, screen_width, screen_height, display_mode="DEFAULT"):
        """
        Initialize the effects system.
        
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
            display_mode: Current display mode
        """
        self.width = screen_width
        self.height = screen_height
        self.display_mode = display_mode
        
        # Screen shake effect
        self.shake_duration = 0
        self.shake_magnitude = 0
        
        # Explosions
        self.explosions = []
        self.max_explosions = MAX_EXPLOSIONS[display_mode]
        
        # Glass cracks
        self.glass_cracks = []
        self.max_cracks = MAX_CRACKS
        self.background_shattered = False
        self.shatter_timer = 0
        
        # Flame/laser effects
        self.lasers = []
    
    def start_shake(self, duration, magnitude):
        """
        Start a screen shake effect.
        
        Args:
            duration: Duration in frames
            magnitude: Maximum pixel offset
        """
        self.shake_duration = duration
        self.shake_magnitude = magnitude
    
    def get_shake_offset(self):
        """
        Get the current screen shake offset.
        
        Returns:
            A tuple (offset_x, offset_y) to apply to rendered objects
        """
        if self.shake_duration > 0:
            offset_x = random.randint(-self.shake_magnitude, self.shake_magnitude)
            offset_y = random.randint(-self.shake_magnitude, self.shake_magnitude)
            self.shake_duration -= 1
            return offset_x, offset_y
        return 0, 0
    
    def create_explosion(self, x, y, color=None, max_radius=270, duration=30):
        """
        Create an explosion effect.
        
        Args:
            x, y: Center of explosion
            color: Color of explosion (None for random)
            max_radius: Maximum radius of explosion
            duration: Duration in frames
        """
        # If too many explosions, remove the oldest one
        if len(self.explosions) >= self.max_explosions:
            self.explosions.pop(0)
        
        # Determine color if not specified
        if color is None:
            from settings import FLAME_COLORS
            color = random.choice(FLAME_COLORS)
        
        # Create explosion
        explosion = {
            "x": x,
            "y": y,
            "radius": 1,
            "max_radius": max_radius,
            "color": color,
            "duration": duration,
            "start_duration": duration
        }
        
        self.explosions.append(explosion)
        return explosion
    
    def create_flame_effect(self, start_x, start_y, end_x, end_y, duration=15):
        """
        Create a flame/laser effect between two points.
        
        Args:
            start_x, start_y: Starting point
            end_x, end_y: Ending point
            duration: Duration in frames
        """
        from settings import LASER_EFFECTS
        
        laser_effect = random.choice(LASER_EFFECTS)
        
        laser = {
            "start_pos": (start_x, start_y),
            "end_pos": (end_x, end_y),
            "colors": laser_effect["colors"],
            "widths": laser_effect["widths"],
            "type": laser_effect["type"],
            "duration": duration
        }
        
        self.lasers.append(laser)
        return laser
    
    def create_crack(self, x, y):
        """
        Create a crack in the glass effect.
        
        Args:
            x, y: Location of the crack
            
        Returns:
            True if the screen should shatter (max cracks reached)
        """
        if len(self.glass_cracks) >= self.max_cracks:
            # Already at max cracks, don't add more
            return False
        
        # Generate a random crack pattern
        segments = random.randint(3, 8)
        points = [(x, y)]  # Start at the click point
        
        # Generate random crack segments
        angle = random.uniform(0, 2 * math.pi)
        for _ in range(segments):
            length = random.uniform(30, 120)
            angle += random.uniform(-math.pi/4, math.pi/4)  # Change direction slightly
            
            # Calculate end point of this segment
            end_x = points[-1][0] + math.cos(angle) * length
            end_y = points[-1][1] + math.sin(angle) * length
            
            # Keep crack within screen bounds
            end_x = max(10, min(self.width - 10, end_x))
            end_y = max(10, min(self.height - 10, end_y))
            
            points.append((end_x, end_y))
        
        # Add branches with some probability
        branches = []
        for i in range(1, len(points)):
            if random.random() < 0.4:  # 40% chance of branch
                branch_start = points[i]
                branch_angle = angle + random.uniform(-math.pi/2, math.pi/2)
                branch_length = random.uniform(20, 60)
                
                branch_end_x = branch_start[0] + math.cos(branch_angle) * branch_length
                branch_end_y = branch_start[1] + math.sin(branch_angle) * branch_length
                
                # Keep branch within screen bounds
                branch_end_x = max(10, min(self.width - 10, branch_end_x))
                branch_end_y = max(10, min(self.height - 10, branch_end_y))
                
                branches.append((branch_start, (branch_end_x, branch_end_y)))
        
        # Create the crack object
        crack = {
            "points": points,
            "branches": branches,
            "width": random.uniform(1.5, 3.0),
            "alpha": 255,
            "outer_alpha": 80,
            "color": (255, 255, 255)
        }
        
        self.glass_cracks.append(crack)
        
        # Return True if we've reached the max cracks (screen should shatter)
        return len(self.glass_cracks) >= self.max_cracks
    
    def shatter_screen(self, duration=600):
        """
        Trigger the screen shatter effect.
        
        Args:
            duration: How long the shattered effect lasts in frames
        """
        self.background_shattered = True
        self.shatter_timer = duration
        
        # Add screen shake
        self.start_shake(10, 15)
    
    def update(self):
        """Update all effects."""
        # Update shatter timer
        if self.background_shattered and self.shatter_timer > 0:
            self.shatter_timer -= 1
            if self.shatter_timer <= 0:
                self.background_shattered = False
                self.glass_cracks = []  # Clear cracks when effect ends
        
        # Update explosions
        for explosion in list(self.explosions):
            if explosion["duration"] > 0:
                # Calculate current radius based on progress
                progress = 1 - (explosion["duration"] / explosion["start_duration"])
                # Use easing to make the explosion look more natural
                eased_progress = self._ease_out_cubic(progress)
                explosion["radius"] = explosion["max_radius"] * eased_progress
                
                explosion["duration"] -= 1
            else:
                self.explosions.remove(explosion)
        
        # Update lasers
        for laser in list(self.lasers):
            if laser["duration"] > 0:
                laser["duration"] -= 1
            else:
                self.lasers.remove(laser)
    
    def draw_cracks(self, surface):
        """
        Draw all cracks on the screen.
        
        Args:
            surface: Surface to draw on
        """
        for crack in self.glass_cracks:
            # Draw main crack line
            points = crack["points"]
            if len(points) > 1:
                # Draw outer glow
                for i in range(len(points) - 1):
                    pygame.draw.line(
                        surface,
                        (*crack["color"], crack["outer_alpha"]),
                        points[i], points[i+1],
                        int(crack["width"] * 3)
                    )
                
                # Draw inner bright line
                for i in range(len(points) - 1):
                    pygame.draw.line(
                        surface,
                        (*crack["color"], crack["alpha"]),
                        points[i], points[i+1],
                        int(crack["width"])
                    )
            
            # Draw branches
            for branch in crack["branches"]:
                # Draw outer glow
                pygame.draw.line(
                    surface,
                    (*crack["color"], crack["outer_alpha"]),
                    branch[0], branch[1],
                    int(crack["width"] * 2)
                )
                
                # Draw inner bright line
                pygame.draw.line(
                    surface,
                    (*crack["color"], crack["alpha"]),
                    branch[0], branch[1],
                    int(crack["width"])
                )
    
    def draw_explosions(self, surface, offset_x=0, offset_y=0):
        """
        Draw all active explosions.
        
        Args:
            surface: Surface to draw on
            offset_x, offset_y: Offset to apply (e.g., for screen shake)
        """
        for explosion in self.explosions:
            # Create multiple circles with decreasing alpha for glow effect
            for i in range(3):
                # Scale alpha and radius based on the iteration
                alpha = int(150 * (3-i) / 3 * (explosion["duration"] / explosion["start_duration"]))
                radius_scale = 1 - (i * 0.15)  # Each layer is 15% smaller
                
                # Draw explosion circle
                size = int(explosion["radius"] * radius_scale)
                
                # Use a separate surface for transparency
                glow_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                
                # Get appropriate color with alpha
                color = explosion["color"]
                draw_color = (color[0], color[1], color[2], alpha)
                
                # Draw circle on the glow surface
                pygame.draw.circle(glow_surface, draw_color, (size, size), size)
                
                # Blit the glow surface onto the main surface
                pos_x = int(explosion["x"] - size + offset_x)
                pos_y = int(explosion["y"] - size + offset_y)
                surface.blit(glow_surface, (pos_x, pos_y))
    
    def draw_lasers(self, surface, offset_x=0, offset_y=0):
        """
        Draw all active lasers.
        
        Args:
            surface: Surface to draw on
            offset_x, offset_y: Offset to apply (e.g., for screen shake)
        """
        for laser in self.lasers:
            if laser["type"] == "flamethrower":
                self._draw_flamethrower(surface, laser, offset_x, offset_y)
            else:
                # Draw a simple laser beam for other types
                pygame.draw.line(
                    surface,
                    random.choice(laser["colors"]),
                    (laser["start_pos"][0] + offset_x, laser["start_pos"][1] + offset_y),
                    (laser["end_pos"][0] + offset_x, laser["end_pos"][1] + offset_y),
                    random.choice(laser["widths"])
                )
    
    def _draw_flamethrower(self, surface, laser, offset_x=0, offset_y=0):
        """Draw a flamethrower effect."""
        start_x, start_y = laser["start_pos"]
        end_x, end_y = laser["end_pos"]
        
        # Apply shake offset
        start_x += offset_x
        start_y += offset_y
        end_x += offset_x
        end_y += offset_y
        
        # Calculate main direction vector and length
        dx = end_x - start_x
        dy = end_y - start_y
        length = math.hypot(dx, dy)
        
        # Create jagged path with multiple segments
        num_segments = int(length / 20)  # One segment per 20 pixels
        num_segments = max(2, min(num_segments, 10))  # Between 2 and 10 segments
        
        points = [(start_x, start_y)]
        
        for i in range(1, num_segments):
            # Calculate base position along the line
            t = i / num_segments
            base_x = start_x + dx * t
            base_y = start_y + dy * t
            
            # Add random deviation perpendicular to the main direction
            if length > 0:  # Avoid division by zero
                # Create perpendicular vector
                perpx = -dy / length
                perpy = dx / length
                
                # Add deviation that decreases as we get closer to the end
                deviation = 20 * (1 - t)  # Less deviation at the end
                offset = random.uniform(-deviation, deviation)
                
                point_x = base_x + perpx * offset
                point_y = base_y + perpy * offset
                
                points.append((point_x, point_y))
        
        # Add end point
        points.append((end_x, end_y))
        
        # Draw multiple flame layers with different widths for volume effect
        # Start with wider, more transparent layers
        for width in reversed(laser["widths"]):
            color = random.choice(laser["colors"])
            
            # Use separate surface for transparency effect
            flare_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Draw flame path with this width
            if len(points) >= 2:
                pygame.draw.lines(
                    flare_surface,
                    (*color, 150),  # Semi-transparent
                    False,  # Not closed
                    points,
                    width
                )
            
            # Apply surface with alpha blending
            surface.blit(flare_surface, (0, 0))
    
    def _ease_out_cubic(self, t):
        """Cubic easing function for natural-looking motion."""
        return 1 - (1 - t) ** 3

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
    temp_effects = Effects(800, 600)  # Use default size
    return temp_effects.create_explosion(x, y, color, max_radius, duration) 