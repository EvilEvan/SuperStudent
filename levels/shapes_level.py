# levels/shapes_level.py

"""
SuperStudent - Shapes Level

This module implements the shapes level where players must identify and click on specific shapes.
"""

import pygame
import random
import math
from .base_level import BaseLevel

class ShapesLevel(BaseLevel):
    def __init__(self, screen_width, screen_height, resource_manager, particle_system, effects):
        super().__init__(screen_width, screen_height, resource_manager, particle_system, effects)
        
        # Shapes-specific state
        self.sequence = ["Rectangle", "Square", "Circle", "Triangle", "Pentagon"]
        self.current_group = self.sequence.copy()
        self.items_to_target = []
        self.target_item = None
        self.items_on_screen = []
        self.items_spawned = 0
        self.items_destroyed = 0
        self.total_items = len(self.sequence)
        self.shapes_first_round = True
        self.just_completed_level = False
        
        # Load shapes progress
        self._load_progress()
    
    def _load_progress(self):
        """Load shapes level progress from file."""
        try:
            with open("level_progress.txt", "r") as f:
                progress = f.read().strip()
                self.shapes_first_round = "shapes_completed" not in progress
        except:
            self.shapes_first_round = True
    
    def _save_progress(self):
        """Save shapes level progress to file."""
        try:
            with open("level_progress.txt", "w") as f:
                f.write("shapes_completed")
        except:
            pass
    
    def initialize(self):
        """Initialize the shapes level."""
        if not super().initialize():
            return False
        
        # Reset level state
        self.score = 0
        self.items_destroyed = 0
        self.items_spawned = 0
        self.items_on_screen.clear()
        
        # Set up target items
        self.items_to_target = self.sequence.copy()
        random.shuffle(self.items_to_target)
        if self.items_to_target:
            self.target_item = self.items_to_target[0]
        
        # Spawn initial shapes
        self._spawn_shapes()
        
        return True
    
    def _spawn_shapes(self):
        """Spawn all shapes for the current round."""
        for shape_name in self.sequence:
            shape = {
                "value": shape_name,
                "x": random.randint(50, self.width - 50),
                "y": random.randint(50, self.height - 150),
                "dx": random.uniform(-0.5, 0.5) * 60,
                "dy": random.uniform(-0.5, 0.5) * 60,
                "size": 50,  # Base size for shapes
                "rect": pygame.Rect(0, 0, 50, 50)  # Will be updated in update()
            }
            self.items_on_screen.append(shape)
            self.items_spawned += 1
    
    def update(self, delta_time):
        """Update the shapes level state."""
        if not super().update(delta_time):
            return False
        
        # Update shape positions and collisions
        for shape in self.items_on_screen:
            # Update position
            shape["x"] += shape["dx"] * delta_time
            shape["y"] += shape["dy"] * delta_time
            
            # Bounce off walls
            if shape["x"] - shape["size"]/2 < 0 or shape["x"] + shape["size"]/2 > self.width:
                shape["dx"] *= -1
            if shape["y"] - shape["size"]/2 < 0 or shape["y"] + shape["size"]/2 > self.height - 100:
                shape["dy"] *= -1
            
            # Update collision rect
            shape["rect"].center = (shape["x"], shape["y"])
        
        # Check for level completion
        if not self.items_to_target and not self.items_on_screen:
            if self.shapes_first_round:
                self.shapes_first_round = False
                self._save_progress()
                return "CHECKPOINT"
            else:
                return "LEVEL_COMPLETE"
        
        return True
    
    def draw(self, screen):
        """Draw the shapes level."""
        super().draw(screen)
        
        # Draw shapes
        for shape in self.items_on_screen:
            self._draw_shape(screen, shape)
        
        # Draw target indicator
        if self.target_item:
            self._draw_target_indicator(screen)
    
    def _draw_shape(self, screen, shape):
        """Draw a single shape."""
        x, y = shape["x"], shape["y"]
        size = shape["size"]
        
        if shape["value"] == "Rectangle":
            rect = pygame.Rect(x - size*1.5/2, y - size/2, size*1.5, size)
            pygame.draw.rect(screen, (255, 255, 255), rect, 3)
        elif shape["value"] == "Square":
            rect = pygame.Rect(x - size/2, y - size/2, size, size)
            pygame.draw.rect(screen, (255, 255, 255), rect, 3)
        elif shape["value"] == "Circle":
            pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), size//2, 3)
        elif shape["value"] == "Triangle":
            points = [
                (x, y - size/2),
                (x - size/2, y + size/2),
                (x + size/2, y + size/2)
            ]
            pygame.draw.polygon(screen, (255, 255, 255), points, 3)
        elif shape["value"] == "Pentagon":
            points = []
            for i in range(5):
                angle = math.radians(72 * i - 90)
                px = x + size/2 * math.cos(angle)
                py = y + size/2 * math.sin(angle)
                points.append((px, py))
            pygame.draw.polygon(screen, (255, 255, 255), points, 3)
    
    def _draw_target_indicator(self, screen):
        """Draw the current target shape indicator."""
        # Draw target shape in center
        x, y = self.width//2, self.height//2
        size = 100
        
        if self.target_item == "Rectangle":
            rect = pygame.Rect(x - size*1.5/2, y - size/2, size*1.5, size)
            pygame.draw.rect(screen, (255, 255, 255), rect, 5)
        elif self.target_item == "Square":
            rect = pygame.Rect(x - size/2, y - size/2, size, size)
            pygame.draw.rect(screen, (255, 255, 255), rect, 5)
        elif self.target_item == "Circle":
            pygame.draw.circle(screen, (255, 255, 255), (x, y), size//2, 5)
        elif self.target_item == "Triangle":
            points = [
                (x, y - size/2),
                (x - size/2, y + size/2),
                (x + size/2, y + size/2)
            ]
            pygame.draw.polygon(screen, (255, 255, 255), points, 5)
        elif self.target_item == "Pentagon":
            points = []
            for i in range(5):
                angle = math.radians(72 * i - 90)
                px = x + size/2 * math.cos(angle)
                py = y + size/2 * math.sin(angle)
                points.append((px, py))
            pygame.draw.polygon(screen, (255, 255, 255), points, 5)
    
    def _handle_touch(self, x, y):
        """Handle a touch/click event."""
        if not self.game_started:
            self.game_started = True
            return
        
        # Check if a shape was hit
        for shape in self.items_on_screen[:]:
            if shape["rect"].collidepoint(x, y):
                if shape["value"] == self.target_item:
                    # Correct shape hit
                    self.score += 10
                    self.items_destroyed += 1
                    self.items_on_screen.remove(shape)
                    
                    # Create effects
                    self.effects.create_explosion(shape["x"], shape["y"])
                    self.particle_system.create_particles(
                        shape["x"], shape["y"],
                        count=20,
                        color=(255, 255, 255),
                        size_range=(20, 40),
                        speed_range=(-2, 2),
                        duration=20
                    )
                    
                    # Update target
                    if self.items_to_target:
                        self.items_to_target.pop(0)
                        if self.items_to_target:
                            self.target_item = self.items_to_target[0]
                        else:
                            self.target_item = None
                else:
                    # Wrong shape hit
                    self._handle_misclick(x, y)
                return
        
        # No shape hit
        self._handle_misclick(x, y)
    
    def cleanup(self):
        """Clean up resources when exiting the level."""
        super().cleanup()
        self.items_on_screen.clear()
        return True 