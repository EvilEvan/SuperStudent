"""
SuperStudent - Level Menu Screen

This module implements the level menu screen, where the player can
select which game level to play.
"""
import pygame
import random
import math

class LevelMenu:
    """
    Level menu screen for SuperStudent game, showing available levels.
    """
    
    def __init__(self, screen_width, screen_height, resource_manager):
        """
        Initialize the level menu screen.
        
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
            resource_manager: Resource manager for loading/unloading resources
        """
        self.width = screen_width
        self.height = screen_height
        self.resource_manager = resource_manager
        
        # Button rectangles
        self.abc_rect = None
        self.num_rect = None
        self.shapes_rect = None
        self.clcase_rect = None
        self.colors_rect = None
        
        # Animation elements
        self.repel_particles = []
        self.color_transition = 0.0
        self.current_color = None
        self.next_color = None
        self.title_color = None
        
        # Track whether initialization has been done
        self.initialized = False
    
    def initialize(self):
        """
        Initialize resources and state for the level menu.
        
        Returns:
            True if initialization was successful
        """
        # Load fonts
        self.title_font = self.resource_manager.get_font("title")
        self.small_font = self.resource_manager.get_font("small")
        
        # Calculate button layout - fixed positions
        button_width = 300
        button_height = 80
        
        self.abc_rect = pygame.Rect(
            (self.width // 2 - button_width - 20, self.height // 2 - button_height - 10), 
            (button_width, button_height)
        )
        
        self.num_rect = pygame.Rect(
            (self.width // 2 + 20, self.height // 2 - button_height - 10), 
            (button_width, button_height)
        )
        
        self.shapes_rect = pygame.Rect(
            (self.width // 2 - button_width - 20, self.height // 2 + 10), 
            (button_width, button_height)
        )
        
        self.clcase_rect = pygame.Rect(
            (self.width // 2 + 20, self.height // 2 + 10), 
            (button_width, button_height)
        )
        
        self.colors_rect = pygame.Rect(
            (self.width // 2 - 150, self.height // 2 + 120), 
            (300, 80)
        )
        
        # Setup animation elements
        self._setup_colors()
        self._setup_particles()
        
        self.initialized = True
        return True
    
    def update(self, delta_time):
        """
        Update animation elements.
        
        Args:
            delta_time: Time elapsed since last frame in seconds
            
        Returns:
            True to continue running, False to exit
        """
        # Update color transition for title
        self.color_transition += 0.5 * delta_time  # Scale with delta time
        if self.color_transition >= 1:
            self.color_transition = 0
            self.current_color = self.next_color
            
            # From FLAME_COLORS
            flame_colors = [
                (255, 69, 0),    # OrangeRed
                (255, 140, 0),   # DarkOrange
                (255, 165, 0),   # Orange
                (255, 215, 0),   # Gold
                (255, 255, 0),   # Yellow
                (138, 43, 226),  # BlueViolet
                (75, 0, 130),    # Indigo
                (65, 105, 225)   # RoyalBlue
            ]
            
            # Choose a different color than current
            available_colors = [c for c in flame_colors if c != self.current_color]
            self.next_color = random.choice(available_colors)
        
        # Update title color
        r = int(self.current_color[0] * (1 - self.color_transition) + self.next_color[0] * self.color_transition)
        g = int(self.current_color[1] * (1 - self.color_transition) + self.next_color[1] * self.color_transition)
        b = int(self.current_color[2] * (1 - self.color_transition) + self.next_color[2] * self.color_transition)
        self.title_color = (r, g, b)
        
        # Update particles with delta time
        for particle in self.repel_particles:
            # Move particles AWAY from center
            particle["x"] += math.cos(particle["angle"]) * particle["speed"] * delta_time * 60
            particle["y"] += math.sin(particle["angle"]) * particle["speed"] * delta_time * 60
            
            # Reset particles that move off screen
            if (particle["x"] < 0 or particle["x"] > self.width or
                particle["y"] < 0 or particle["y"] > self.height):
                # New angle for variety
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(5, 50)  # Start close to center
                particle["x"] = self.width // 2 + math.cos(angle) * distance
                particle["y"] = self.height // 2 + math.sin(angle) * distance
                particle["angle"] = angle
                particle["color"] = random.choice(self.particle_colors)
                particle["size"] = random.randint(13, 17)
                particle["speed"] = random.uniform(1.0, 3.0)
        
        return True
    
    def draw(self, screen):
        """
        Draw the level menu screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Fill background with black
        screen.fill((0, 0, 0))
        
        # Draw particles
        for particle in self.repel_particles:
            pygame.draw.circle(
                screen, 
                particle["color"],
                (int(particle["x"]), int(particle["y"])),
                particle["size"]
            )
        
        # Draw title
        title_text = self.small_font.render("Choose Mission:", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.width // 2, self.height // 2 - 150))
        screen.blit(title_text, title_rect)
        
        # Draw buttons with highlights if hovered
        mx, my = pygame.mouse.get_pos()
        
        # A B C button
        self._draw_neon_button(screen, self.abc_rect, (255, 0, 150), mx, my)
        abc_text = self.small_font.render("A B C", True, (255, 255, 255))
        abc_text_rect = abc_text.get_rect(center=self.abc_rect.center)
        screen.blit(abc_text, abc_text_rect)
        
        # 1 2 3 button
        self._draw_neon_button(screen, self.num_rect, (0, 200, 255), mx, my)
        num_text = self.small_font.render("1 2 3", True, (255, 255, 255))
        num_text_rect = num_text.get_rect(center=self.num_rect.center)
        screen.blit(num_text, num_text_rect)
        
        # Shapes button
        self._draw_neon_button(screen, self.shapes_rect, (0, 255, 0), mx, my)
        shapes_text = self.small_font.render("Shapes", True, (255, 255, 255))
        shapes_text_rect = shapes_text.get_rect(center=self.shapes_rect.center)
        screen.blit(shapes_text, shapes_text_rect)
        
        # C/L Case button
        self._draw_neon_button(screen, self.clcase_rect, (255, 255, 0), mx, my)
        clcase_text = self.small_font.render("C/L Case", True, (255, 255, 255))
        clcase_text_rect = clcase_text.get_rect(center=self.clcase_rect.center)
        screen.blit(clcase_text, clcase_text_rect)
        
        # Colors button
        self._draw_neon_button(screen, self.colors_rect, (128, 0, 255), mx, my)
        colors_text = self.small_font.render("Colors", True, (255, 255, 255))
        colors_text_rect = colors_text.get_rect(center=self.colors_rect.center)
        screen.blit(colors_text, colors_text_rect)
        
        pygame.display.flip()
    
    def handle_event(self, event):
        """
        Handle pygame events.
        
        Args:
            event: Pygame event to process
            
        Returns:
            New game state if screen should exit, None to continue
        """
        if event.type == pygame.QUIT:
            return "QUIT"
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "WELCOME"
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            if self.abc_rect.collidepoint(mx, my):
                return "ABC_LEVEL"
            elif self.num_rect.collidepoint(mx, my):
                return "NUMBERS_LEVEL"
            elif self.shapes_rect.collidepoint(mx, my):
                return "SHAPES_LEVEL"
            elif self.clcase_rect.collidepoint(mx, my):
                return "CLCASE_LEVEL"
            elif self.colors_rect.collidepoint(mx, my):
                return "COLORS_LEVEL"
        
        return None
    
    def cleanup(self):
        """Clean up resources when exiting the screen."""
        self.repel_particles = []
        return True
    
    def _setup_colors(self):
        """Set up colors for transitions and effects."""
        # From FLAME_COLORS
        flame_colors = [
            (255, 69, 0),    # OrangeRed
            (255, 140, 0),   # DarkOrange
            (255, 165, 0),   # Orange
            (255, 215, 0),   # Gold
            (255, 255, 0),   # Yellow
            (138, 43, 226),  # BlueViolet
            (75, 0, 130),    # Indigo
            (65, 105, 225)   # RoyalBlue
        ]
        
        # Initialize with random colors
        self.current_color = flame_colors[0]
        self.next_color = flame_colors[1]
        
        # Set initial title color
        r = int(self.current_color[0] * 0.5 + self.next_color[0] * 0.5)
        g = int(self.current_color[1] * 0.5 + self.next_color[1] * 0.5)
        b = int(self.current_color[2] * 0.5 + self.next_color[2] * 0.5)
        self.title_color = (r, g, b)
        
        # Define particle colors
        self.particle_colors = [
            (255, 0, 128),   # Bright pink
            (0, 255, 128),   # Bright green
            (128, 0, 255),   # Bright purple
            (255, 128, 0),   # Bright orange
            (0, 128, 255)    # Bright blue
        ]
    
    def _setup_particles(self):
        """Set up particles for the menu background."""
        # Create OUTWARD moving particles
        self.repel_particles = []
        for _ in range(700):
            # Start particles near center
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(10, 100)  # Close to center
            x = self.width // 2 + math.cos(angle) * distance
            y = self.height // 2 + math.sin(angle) * distance
            self.repel_particles.append({
                "x": x,
                "y": y,
                "color": random.choice(self.particle_colors),
                "size": random.randint(5, 7),
                "speed": random.uniform(3.0, 6.0),
                "angle": angle  # Store the angle for outward movement
            })
    
    def _draw_neon_button(self, surface, rect, base_color, mx, my):
        """
        Draw a button with a neon glow effect.
        
        Args:
            surface: Surface to draw on
            rect: Button rectangle
            base_color: Base color for the button glow
            mx, my: Mouse position for hover detection
        """
        # Check if mouse is hovering over this button
        is_hovering = rect.collidepoint(mx, my)
        
        # Enhance color slightly if hovering
        if is_hovering:
            glow_color = (
                min(base_color[0] + 20, 255),
                min(base_color[1] + 20, 255),
                min(base_color[2] + 20, 255)
            )
            glow_intensity = 6  # More intense glow when hovering
        else:
            glow_color = base_color
            glow_intensity = 5  # Normal glow intensity
        
        # Fill the button with a dark background
        pygame.draw.rect(surface, (20, 20, 20), rect)
        
        # Draw a neon glow border by drawing multiple expanding outlines
        for i in range(1, glow_intensity):
            neon_rect = pygame.Rect(
                rect.x - i, 
                rect.y - i, 
                rect.width + 2*i, 
                rect.height + 2*i
            )
            pygame.draw.rect(surface, glow_color, neon_rect, 1)
        
        # Draw a solid border
        pygame.draw.rect(surface, glow_color, rect, 2)