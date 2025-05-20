"""
Particle system for visual effects.
Handles creation, updating, and rendering of particles.
"""

import pygame
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Particle:
    pos: Tuple[float, float]
    velocity: Tuple[float, float]
    color: Tuple[int, int, int]
    size: float
    life: float
    max_life: float

class ParticlePool:
    def __init__(self, max_particles: int = 1000):
        self.particles: List[Particle] = []
        self.max_particles = max_particles
    
    def create_particle(self, pos: Tuple[float, float], velocity: Tuple[float, float],
                       color: Tuple[int, int, int], size: float, life: float) -> None:
        if len(self.particles) >= self.max_particles:
            return
        
        self.particles.append(Particle(pos, velocity, color, size, life, life))
    
    def update(self, dt: float) -> None:
        for particle in self.particles[:]:
            particle.life -= dt
            if particle.life <= 0:
                self.particles.remove(particle)
                continue
            
            x, y = particle.pos
            vx, vy = particle.velocity
            particle.pos = (x + vx * dt, y + vy * dt)
    
    def draw(self, surface: pygame.Surface) -> None:
        for particle in self.particles:
            alpha = int(255 * (particle.life / particle.max_life))
            color = (*particle.color, alpha)
            size = int(particle.size * (particle.life / particle.max_life))
            pygame.draw.circle(surface, color, (int(particle.pos[0]), int(particle.pos[1])), size) 