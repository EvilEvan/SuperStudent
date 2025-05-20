"""
Explosion system for creating and managing explosion effects.
"""

import pygame
import random
from typing import List, Tuple
from .particle import ParticlePool

class ExplosionManager:
    def __init__(self, particle_pool: ParticlePool):
        self.particle_pool = particle_pool
    
    def create_explosion(self, pos: Tuple[float, float], color: Tuple[int, int, int],
                        particle_count: int = 20, size: float = 5.0,
                        speed: float = 200.0, life: float = 1.0) -> None:
        """Create an explosion effect at the given position."""
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * 3.14159)
            speed_factor = random.uniform(0.5, 1.0)
            velocity = (
                speed * speed_factor * pygame.math.Vector2(1, 0).rotate(angle).x,
                speed * speed_factor * pygame.math.Vector2(1, 0).rotate(angle).y
            )
            particle_size = random.uniform(size * 0.5, size * 1.5)
            particle_life = random.uniform(life * 0.5, life * 1.5)
            
            self.particle_pool.create_particle(pos, velocity, color, particle_size, particle_life)
    
    def create_laser_explosion(self, pos: Tuple[float, float], color: Tuple[int, int, int]) -> None:
        """Create a laser-specific explosion effect."""
        self.create_explosion(pos, color, particle_count=15, size=3.0, speed=150.0, life=0.5) 