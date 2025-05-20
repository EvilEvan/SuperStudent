"""
Glass crack system for creating and managing glass break effects.
"""

import pygame
import random
from typing import List, Tuple, Dict
from dataclasses import dataclass

@dataclass
class Crack:
    pos: Tuple[float, float]
    angle: float
    length: float
    width: float
    life: float
    max_life: float

class GlassCrackManager:
    def __init__(self):
        self.cracks: List[Crack] = []
        self.shattered: Dict[Tuple[int, int], float] = {}  # (x, y) -> life
    
    def create_crack(self, pos: Tuple[float, float], angle: float = None,
                    length: float = 50.0, width: float = 2.0, life: float = 2.0) -> None:
        """Create a glass crack at the given position."""
        if angle is None:
            angle = random.uniform(0, 360)
        
        self.cracks.append(Crack(pos, angle, length, width, life, life))
    
    def create_shatter(self, pos: Tuple[float, float], radius: float = 30.0) -> None:
        """Create a shattered glass effect at the given position."""
        for _ in range(20):
            angle = random.uniform(0, 2 * 3.14159)
            distance = random.uniform(0, radius)
            x = int(pos[0] + distance * pygame.math.Vector2(1, 0).rotate(angle).x)
            y = int(pos[1] + distance * pygame.math.Vector2(1, 0).rotate(angle).y)
            self.shattered[(x, y)] = random.uniform(0.5, 2.0)
    
    def update(self, dt: float) -> None:
        """Update all cracks and shattered pieces."""
        # Update cracks
        for crack in self.cracks[:]:
            crack.life -= dt
            if crack.life <= 0:
                self.cracks.remove(crack)
        
        # Update shattered pieces
        for pos in list(self.shattered.keys()):
            self.shattered[pos] -= dt
            if self.shattered[pos] <= 0:
                del self.shattered[pos]
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw all cracks and shattered pieces."""
        # Draw cracks
        for crack in self.cracks:
            alpha = int(255 * (crack.life / crack.max_life))
            color = (200, 200, 200, alpha)
            end_pos = (
                crack.pos[0] + crack.length * pygame.math.Vector2(1, 0).rotate(crack.angle).x,
                crack.pos[1] + crack.length * pygame.math.Vector2(1, 0).rotate(crack.angle).y
            )
            pygame.draw.line(surface, color, crack.pos, end_pos, int(crack.width))
        
        # Draw shattered pieces
        for (x, y), life in self.shattered.items():
            alpha = int(255 * (life / 2.0))
            color = (200, 200, 200, alpha)
            size = int(3 * (life / 2.0))
            pygame.draw.circle(surface, color, (x, y), size) 