"""
SuperStudent - Base Level Class

This module provides the BaseLevel class which serves as the foundation for all game levels.
It implements common functionality and defines the interface that level classes should implement.
"""
import pygame
import random
import math

class BaseLevel:
    """
    Base class for all game levels, providing common functionality and interface.
    All level implementations should inherit from this class.
    """
    
    def __init__(self, screen_width, screen_height, resource_manager, particle_system, effects):
        """
        Initialize the base level.
        
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
            resource_manager: Resource manager for loading/unloading resources
            particle_system: Particle system for creating particles
            effects: Effects system for explosions, screen shake, etc.
        """
        self.width = screen_width
        self.height = screen_height
        self.resource_manager = resource_manager
        self.particle_system = particle_system
        self.effects = effects
        
        # Basic game state
        self.score = 0
        self.game_started = False
        self.game_over = False
        
        # Common elements
        self.stars = []
        self.active_touches = {}
        
        # Tracking for delta time movement
        self.last_update_time = pygame.time.get_ticks()
    
    def initialize(self):
        """
        Initialize level-specific resources and state.
        
        Override this method in level implementations.
        
        Returns:
            True if initialization successful, False otherwise
        """
        # Create background stars
        self._initialize_stars()
        return True
    
    def update(self, delta_time):
        """
        Update the level state.
        
        Args:
            delta_time: Time elapsed since last frame in seconds
            
        Returns:
            True to continue running, False to exit the level
        """
        # Update stars with time-based movement
        self._update_stars(delta_time)
        
        # Update effects systems
        self.effects.update()
        self.particle_system.update(delta_time)
        
        return True
    
    def draw(self, screen):
        """
        Draw the level.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Get current shake offset
        offset_x, offset_y = self.effects.get_shake_offset()
        
        # Draw background elements
        self._draw_stars(screen, offset_x, offset_y)
        
        # Draw glass cracks
        self.effects.draw_cracks(screen)
        
        # Draw particles
        self.particle_system.draw(screen, offset_x, offset_y)
        
        # Draw explosions
        self.effects.draw_explosions(screen, offset_x, offset_y)
        
        # Draw lasers
        self.effects.draw_lasers(screen, offset_x, offset_y)
    
    def handle_event(self, event):
        """
        Process a pygame event.
        
        Args:
            event: Pygame event to process
            
        Returns:
            New game state if level should exit, None to continue
        """
        # Handle basic events, custom handling in subclasses
        if event.type == pygame.QUIT:
            return "QUIT"
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "LEVEL_MENU"
        
        if event.type == pygame.FINGERDOWN:
            touch_id = event.finger_id
            touch_x = event.x * self.width
            touch_y = event.y * self.height
            self.active_touches[touch_id] = (touch_x, touch_y)
            
            # Let subclasses handle the actual logic
            self._handle_touch(touch_x, touch_y)
        
        if event.type == pygame.FINGERUP:
            touch_id = event.finger_id
            if touch_id in self.active_touches:
                del self.active_touches[touch_id]
        
        return None
    
    def cleanup(self):
        """Clean up resources when exiting the level."""
        # Reset game state
        self.game_started = False
        self.game_over = False
        
        # Clear effects
        self.particle_system.clear()
        
        # Allow subclasses to clean up their resources
        return True
    
    def _initialize_stars(self, count=100):
        """Initialize background stars."""
        self.stars = []
        for _ in range(count):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            radius = random.randint(2, 4)
            self.stars.append([x, y, radius])
    
    def _update_stars(self, delta_time):
        """Update star positions with time-based movement."""
        for star in self.stars:
            x, y, radius = star
            
            # Scale movement by delta time for consistent speed
            y += 60 * delta_time  # Move at ~1 pixel per frame at 60 FPS
            
            # Wrap stars when they go off screen
            if y > self.height + radius:
                y = random.randint(-50, -10)
                x = random.randint(0, self.width)
            
            star[0] = x
            star[1] = y
    
    def _draw_stars(self, screen, offset_x=0, offset_y=0):
        """Draw background stars."""
        for star in self.stars:
            x, y, radius = star
            pygame.draw.circle(
                screen, 
                (200, 200, 200),  # Consistent color for stars
                (int(x + offset_x), int(y + offset_y)), 
                radius
            )
    
    def _handle_touch(self, x, y):
        """
        Handle a touch or click at the given coordinates.
        
        Override this method in level implementations.
        
        Args:
            x, y: Touch/click coordinates
        """
        # Base implementation just starts the game
        if not self.game_started:
            self.game_started = True
    
    def _handle_misclick(self, x, y):
        """
        Handle a misclick (click that didn't hit a target).
        
        Args:
            x, y: Misclick coordinates
            
        Returns:
            True if the screen shattered (max cracks reached)
        """
        # Create a crack at the click location
        should_shatter = self.effects.create_crack(x, y)
        
        # If we've reached the max cracks, trigger the screen shatter effect
        if should_shatter:
            self.effects.shatter_screen()
            return True
        
        return False 