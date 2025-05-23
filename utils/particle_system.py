"""
SuperStudent - Particle System

This module provides an optimized particle system with object pooling 
for all visual effects in the game.
"""
import pygame
import math
import random
from settings import PARTICLE_CULLING_DISTANCE, MAX_PARTICLES, ENABLE_COLLISION_GRID, COLLISION_GRID_SIZE

class ParticleManager:
    """
    Manages all particle effects in the game with efficient pooling.
    """
    
    def __init__(self, max_particles=200):
        """
        Initialize the particle manager.
        
        Args:
            max_particles: Maximum number of particles allowed
        """
        self.max_particles = max_particles
        self.particles = []
        self.particle_pool = []
        self.culling_distance = 0  # Will be set based on screen size
        
        # Create initial particle pool
        for _ in range(100):  # Pre-create some particles to reuse
            self.particle_pool.append({
                "x": 0, "y": 0, "color": (0,0,0), "size": 0, 
                "dx": 0, "dy": 0, "duration": 0, "start_duration": 0,
                "active": False
            })
    
    def set_culling_distance(self, distance):
        """Set the distance at which to cull offscreen particles."""
        self.culling_distance = distance
    
    def get_particle(self):
        """Get a particle from the pool or create a new one if needed."""
        # Check if there's an available particle in the pool
        for particle in self.particle_pool:
            if not particle["active"]:
                particle["active"] = True
                return particle
        
        # If we've reached the maximum number of particles, return None
        if len(self.particles) >= self.max_particles:
            return None
        
        # Create a new particle and add it to the list
        new_particle = {
            "x": 0, "y": 0, "color": (0,0,0), "size": 0, 
            "dx": 0, "dy": 0, "duration": 0, "start_duration": 0,
            "active": True
        }
        self.particles.append(new_particle)
        return new_particle
    
    def release_particle(self, particle):
        """Return a particle to the pool."""
        particle["active"] = False
    
    def create_particle(self, x, y, color, size, dx, dy, duration):
        """Create a new particle with the specified properties."""
        particle = self.get_particle()
        if particle:
            particle["x"] = x
            particle["y"] = y
            particle["color"] = color
            particle["size"] = size
            particle["dx"] = dx
            particle["dy"] = dy
            particle["duration"] = duration
            particle["start_duration"] = duration
            return particle
        return None
    
    def update(self, delta_time=1.0):
        """Update all active particles."""
        for particle in self.particles:
            if particle["active"]:
                # Move the particle
                particle["x"] += particle["dx"] * delta_time
                particle["y"] += particle["dy"] * delta_time
                
                # Decrease the duration
                particle["duration"] -= 1 * delta_time
                
                # Release the particle if it's expired or offscreen
                if particle["duration"] <= 0:
                    self.release_particle(particle)
                    continue
                
                # Cull particles that have moved far offscreen
                if self.culling_distance > 0:
                    distance_squared = particle["x"]**2 + particle["y"]**2
                    if distance_squared > self.culling_distance**2:
                        self.release_particle(particle)
    
    def draw(self, surface, offset_x=0, offset_y=0):
        """Draw all active particles."""
        for particle in self.particles:
            if particle["active"]:
                # Calculate opacity based on remaining duration
                if particle["start_duration"] > 0:
                    opacity = int(255 * (particle["duration"] / particle["start_duration"]))
                else:
                    opacity = 255
                
                # Create a temporary surface for the particle with alpha
                particle_surface = pygame.Surface((particle["size"]*2, particle["size"]*2), pygame.SRCALPHA)
                
                # Draw the particle with the calculated opacity
                color_with_alpha = (*particle["color"][:3], opacity)
                pygame.draw.circle(particle_surface, color_with_alpha, 
                                  (particle["size"], particle["size"]), particle["size"])
                
                # Draw the particle surface onto the main surface
                surface.blit(particle_surface, 
                           (particle["x"] - particle["size"] + offset_x, 
                            particle["y"] - particle["size"] + offset_y))

    def clear(self):
        """Clear all active particles."""
        for particle in self.particles:
            if particle["active"]:
                self.release_particle(particle)

class ParticleSystem:
    """
    Optimized particle system that manages particle creation, updating, and rendering.
    Implements object pooling and spatial partitioning for collision detection.
    """
    
    def __init__(self, screen_width, screen_height, display_mode="DEFAULT"):
        """
        Initialize the particle system.
        
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
            display_mode: Display mode affecting maximum particles
        """
        self.width = screen_width
        self.height = screen_height
        self.display_mode = display_mode
        
        # Set maximum particles based on display mode
        self.max_particles = MAX_PARTICLES[display_mode]
        
        # Initialize particle pool
        self.active_particles = []
        self.particle_pool = []
        
        # Pre-allocate particle objects
        self._initialize_particle_pool()
        
        # Spatial grid for collision detection
        self.use_spatial_grid = ENABLE_COLLISION_GRID
        self.grid_cell_size = COLLISION_GRID_SIZE
        self.collision_grid = {}
    
    def _initialize_particle_pool(self):
        """Initialize the particle pool with inactive particles."""
        for _ in range(self.max_particles):
            self.particle_pool.append({
                "x": 0, "y": 0, 
                "color": (0, 0, 0), 
                "size": 0,
                "dx": 0, "dy": 0, 
                "duration": 0, 
                "start_duration": 0,
                "active": False
            })
    
    def get_particle(self):
        """
        Get a particle from the pool or create a new one if needed.
        
        Returns:
            A particle object that can be configured and activated
        """
        # First try to reuse a particle from the pool
        for particle in self.particle_pool:
            if not particle["active"]:
                particle["active"] = True
                self.active_particles.append(particle)
                return particle
        
        # If pool is exhausted, check if we're at the limit
        if len(self.active_particles) >= self.max_particles:
            # Find the oldest particle (lowest duration) and recycle it
            oldest_particle = min(self.active_particles, key=lambda p: p["duration"])
            return oldest_particle
        
        # If we're below the limit, create a new particle
        new_particle = {
            "x": 0, "y": 0, 
            "color": (0, 0, 0), 
            "size": 0,
            "dx": 0, "dy": 0, 
            "duration": 0, 
            "start_duration": 0,
            "active": True
        }
        self.active_particles.append(new_particle)
        self.particle_pool.append(new_particle)
        return new_particle
    
    def release_particle(self, particle):
        """
        Release a particle back to the pool.
        
        Args:
            particle: The particle to release
        """
        if particle in self.active_particles:
            self.active_particles.remove(particle)
            particle["active"] = False
    
    def create_particle(self, x, y, color, size, dx, dy, duration):
        """
        Create and configure a particle.
        
        Args:
            x, y: Initial position
            color: Particle color (RGB tuple)
            size: Particle size
            dx, dy: Velocity components
            duration: Lifetime in frames
            
        Returns:
            The created particle object
        """
        particle = self.get_particle()
        particle["x"] = x
        particle["y"] = y
        particle["color"] = color
        particle["size"] = size
        particle["dx"] = dx
        particle["dy"] = dy
        particle["duration"] = duration
        particle["start_duration"] = duration
        return particle
    
    def update(self, delta_time):
        """
        Update all active particles.
        
        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        # Clear spatial grid if using it
        if self.use_spatial_grid:
            self.collision_grid = {}
        
        # Process each active particle
        for particle in list(self.active_particles):
            if particle["duration"] > 0:
                # Scale movement by delta time for consistent speed
                particle["x"] += particle["dx"] * delta_time * 60  # Scale to 60 FPS equivalent
                particle["y"] += particle["dy"] * delta_time * 60
                particle["duration"] -= 1
                
                # Culling: Remove particles that go too far off-screen
                if (particle["x"] < -PARTICLE_CULLING_DISTANCE or 
                    particle["x"] > self.width + PARTICLE_CULLING_DISTANCE or
                    particle["y"] < -PARTICLE_CULLING_DISTANCE or 
                    particle["y"] > self.height + PARTICLE_CULLING_DISTANCE):
                    self.release_particle(particle)
                    continue
                
                # Add to spatial grid if using it
                if self.use_spatial_grid:
                    cell_x = int(particle["x"] // self.grid_cell_size)
                    cell_y = int(particle["y"] // self.grid_cell_size)
                    grid_key = (cell_x, cell_y)
                    
                    if grid_key not in self.collision_grid:
                        self.collision_grid[grid_key] = []
                    
                    self.collision_grid[grid_key].append(particle)
            else:
                self.release_particle(particle)
    
    def draw(self, screen, offset_x=0, offset_y=0):
        """
        Draw all active particles.
        
        Args:
            screen: Pygame surface to draw on
            offset_x, offset_y: Offset to apply (e.g., for screen shake)
        """
        for particle in self.active_particles:
            # Apply fading effect
            alpha = max(0, 255 * (particle["duration"] / particle.get("start_duration", 30)))
            color = (*particle["color"][:3], int(alpha))
            
            # Draw particle with alpha
            size = int(particle["size"])
            if size > 0:
                particle_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, color, (size, size), size)
                screen.blit(
                    particle_surf, 
                    (int(particle["x"] - size + offset_x), 
                     int(particle["y"] - size + offset_y))
                )
    
    def clear(self):
        """Clear all active particles."""
        for particle in list(self.active_particles):
            self.release_particle(particle)
    
    def get_nearby_particles(self, x, y, radius):
        """
        Get particles near a point using spatial partitioning.
        
        Args:
            x, y: Center point
            radius: Search radius
            
        Returns:
            List of particles within the radius
        """
        if not self.use_spatial_grid:
            # If not using grid, do a naive search
            return [p for p in self.active_particles 
                   if math.hypot(p["x"] - x, p["y"] - y) <= radius]
        
        # Determine grid cells that might contain particles within the radius
        cell_radius = int(radius // self.grid_cell_size) + 1
        center_cell_x = int(x // self.grid_cell_size)
        center_cell_y = int(y // self.grid_cell_size)
        
        nearby_particles = []
        
        # Check all cells within the cell radius
        for cell_x in range(center_cell_x - cell_radius, center_cell_x + cell_radius + 1):
            for cell_y in range(center_cell_y - cell_radius, center_cell_y + cell_radius + 1):
                grid_key = (cell_x, cell_y)
                
                if grid_key in self.collision_grid:
                    # Add particles from this cell that are within the actual radius
                    for particle in self.collision_grid[grid_key]:
                        if math.hypot(particle["x"] - x, particle["y"] - y) <= radius:
                            nearby_particles.append(particle)
        
        return nearby_particles 