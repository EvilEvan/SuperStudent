"""
SuperStudent - Welcome Screen

This module implements the welcome screen, which is the first screen shown
when the game starts. It allows the user to choose the display size.
"""
import pygame
import random
import math

class WelcomeScreen:
    """
    Welcome screen for SuperStudent game, showing title and display size options.
    """
    
    def __init__(self, screen_width, screen_height, resource_manager):
        """
        Initialize the welcome screen.
        
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
            resource_manager: Resource manager for loading/unloading resources
        """
        self.width = screen_width
        self.height = screen_height
        self.resource_manager = resource_manager
        
        # Calculate scaling factor based on screen size
        self.base_height = 1080  # Base design height
        self.scale_factor = self.height / self.base_height
        
        # Track button states
        self.default_button = None
        self.qboard_button = None
        self.selected_mode = None
        
        # Particle effect elements
        self.grav_particles = []
        self.title_color = None
        self.color_transition = 0.0
        self.current_color = None
        self.next_color = None
        
        # Track whether initialization has been done
        self.initialized = False
    
    def initialize(self):
        """
        Initialize resources and state for the welcome screen.
        
        Returns:
            True if initialization was successful
        """
        # Initialize fonts
        self.title_font = self.resource_manager.get_font("title")
        self.small_font = self.resource_manager.get_font("small")
        self.collab_font = pygame.font.Font(None, int(100 * self.scale_factor))
        
        # Detect current display type
        self.detected_mode = self._detect_display_type()
        
        # Calculate UI positions
        self._calculate_layout()
        
        # Setup animation elements
        self._setup_particles()
        self._setup_colors()
        
        # Create static background (optimization)
        self._create_static_background()
        
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
        
        return True
    
    def draw(self, screen):
        """
        Draw the welcome screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw the static background first
        screen.blit(self.static_surface, (0, 0))
        
        # Draw title with current color
        title_text = "Super Student"
        title_rect_center = (self.width // 2, self.height // 2 - self.title_offset)
        
        # Glowing title effect
        highlight_color = (min(self.title_color[0]+80, 255), min(self.title_color[1]+80, 255), min(self.title_color[2]+80, 255))
        shadow_color = (max(self.title_color[0]-90, 0), max(self.title_color[1]-90, 0), max(self.title_color[2]-90, 0))
        mid_color = (max(self.title_color[0]-40, 0), max(self.title_color[1]-40, 0), max(self.title_color[2]-40, 0))
        
        # Draw shadow layers
        shadow = self.title_font.render(title_text, True, (20, 20, 20))
        shadow_rect = shadow.get_rect(center=(title_rect_center[0] + 1, title_rect_center[1] + 1))
        screen.blit(shadow, shadow_rect)
        
        # Draw glowing layers
        glow_colors = [(r//2, g//2, b//2), (r//3, g//3, b//3)]
        for i, glow_color in enumerate(glow_colors):
            glow = self.title_font.render(title_text, True, glow_color)
            offset = i + 1
            for dx, dy in [(-offset,0), (offset,0), (0,-offset), (0,offset)]:
                glow_rect = glow.get_rect(center=(title_rect_center[0] + dx, title_rect_center[1] + dy))
                screen.blit(glow, glow_rect)
        
        # Draw title layers
        highlight = self.title_font.render(title_text, True, highlight_color)
        highlight_rect = highlight.get_rect(center=(title_rect_center[0] - 4, title_rect_center[1] - 4))
        screen.blit(highlight, highlight_rect)
        
        mid_tone = self.title_font.render(title_text, True, mid_color)
        mid_rect = mid_tone.get_rect(center=(title_rect_center[0] + 2, title_rect_center[1] + 2))
        screen.blit(mid_tone, mid_rect)
        
        inner_shadow = self.title_font.render(title_text, True, shadow_color)
        inner_shadow_rect = inner_shadow.get_rect(center=(title_rect_center[0] + 4, title_rect_center[1] + 4))
        screen.blit(inner_shadow, inner_shadow_rect)
        
        title = self.title_font.render(title_text, True, self.title_color)
        title_rect = title.get_rect(center=title_rect_center)
        screen.blit(title, title_rect)
        
        # Draw buttons with highlight based on mouse position
        mx, my = pygame.mouse.get_pos()
        
        # Draw default button with highlight if hovered
        if self.default_button.collidepoint(mx, my):
            # Highlight
            pygame.draw.rect(screen, (0, 220, 255), self.default_button, 3)
        else:
            # Normal
            pygame.draw.rect(screen, (0, 200, 255), self.default_button, 2)
        
        # Draw QBoard button with highlight if hovered
        if self.qboard_button.collidepoint(mx, my):
            # Highlight
            pygame.draw.rect(screen, (255, 20, 170), self.qboard_button, 3)
        else:
            # Normal
            pygame.draw.rect(screen, (255, 0, 150), self.qboard_button, 2)
        
        # Draw pulsing SANGSOM text
        pulse_factor = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.001)
        bright_yellow = (255, 255, 0)
        lite_yellow = (255, 255, 150)
        sangsom_color = tuple(int(bright_yellow[i] * (1 - pulse_factor) + lite_yellow[i] * pulse_factor) for i in range(3))
        
        # Update SANGSOM color
        collab_text2 = self.collab_font.render("SANGSOM", True, sangsom_color)
        screen.blit(collab_text2, self.collab_rect2)
        
        # Display framerate if in debug mode
        from settings import DEBUG_MODE, SHOW_FPS
        if DEBUG_MODE and SHOW_FPS:
            fps = int(1.0 / max(delta_time, 0.001))
            fps_text = self.small_font.render(f"FPS: {fps}", True, (255, 255, 255))
            screen.blit(fps_text, (10, 10))
        
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
            return "QUIT"
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if self.default_button.collidepoint(mx, my):
                self.selected_mode = "DEFAULT"
                self.resource_manager.set_display_mode("DEFAULT")
                return "LEVEL_MENU"
            elif self.qboard_button.collidepoint(mx, my):
                self.selected_mode = "QBOARD"
                self.resource_manager.set_display_mode("QBOARD")
                return "LEVEL_MENU"
        
        return None
    
    def cleanup(self):
        """Clean up resources when exiting the screen."""
        # Most resources are managed by the resource manager, just clear references
        self.grav_particles = None
        self.static_surface = None
        return True
    
    def _detect_display_type(self):
        """Determine initial display mode based on screen size."""
        # If screen is larger than typical desktop monitors, assume it's a QBoard
        if self.width >= 1920 and self.height >= 1080:
            if self.width > 2560 or self.height > 1440:  # Larger than QHD is likely QBoard
                return "QBOARD"
        # Default to smaller format for typical monitors/laptops
        return "DEFAULT"
    
    def _calculate_layout(self):
        """Calculate positions and sizes for UI elements based on screen size."""
        # Apply scaling to title and buttons
        self.title_offset = int(50 * self.scale_factor)
        self.button_width = int(200 * self.scale_factor)
        self.button_height = int(60 * self.scale_factor)
        self.button_spacing = int(20 * self.scale_factor)
        self.button_y_pos = int(200 * self.scale_factor)
        self.instruction_y_pos = int(150 * self.scale_factor)
        
        # Define button rectangles
        self.default_button = pygame.Rect(
            (self.width // 2 - self.button_width - self.button_spacing, 
             self.height // 2 + self.button_y_pos), 
            (self.button_width, self.button_height)
        )
        
        self.qboard_button = pygame.Rect(
            (self.width // 2 + self.button_spacing, 
             self.height // 2 + self.button_y_pos), 
            (self.button_width, self.button_height)
        )
        
        # Calculate collaboration text positions
        collab_text1 = self.collab_font.render("In collaboration with ", True, (255, 255, 255))
        collab_text2 = self.collab_font.render("SANGSOM", True, (255, 255, 0))
        collab_text3 = self.collab_font.render(" Kindergarten", True, (255, 255, 255))
        
        self.collab_rect1 = collab_text1.get_rect()
        self.collab_rect1.right = self.width // 2 - collab_text2.get_width() // 2
        self.collab_rect1.centery = self.height // 2 + int(350 * self.scale_factor)
        
        self.collab_rect2 = collab_text2.get_rect(
            center=(self.width // 2, self.height // 2 + int(350 * self.scale_factor))
        )
        
        self.collab_rect3 = collab_text3.get_rect()
        self.collab_rect3.left = self.collab_rect2.right
        self.collab_rect3.centery = self.height // 2 + int(350 * self.scale_factor)
    
    def _setup_particles(self):
        """Set up gravitational particles for the background effect."""
        # Vivid bright colors for particles
        particle_colors = [
            (255, 0, 128),   # Bright pink
            (0, 255, 128),   # Bright green
            (128, 0, 255),   # Bright purple
            (255, 128, 0),   # Bright orange
            (0, 128, 255)    # Bright blue
        ]
        
        # Create gravitational particles (random positions)
        self.grav_particles = []
        for _ in range(120):
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(200, max(self.width, self.height))
            x = self.width // 2 + math.cos(angle) * distance
            y = self.height // 2 + math.sin(angle) * distance
            self.grav_particles.append({
                "x": x,
                "y": y,
                "color": random.choice(particle_colors),
                "size": random.randint(int(13 * self.scale_factor), int(17 * self.scale_factor)),
            })
    
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
        self.current_color = random.choice(flame_colors)
        self.next_color = random.choice(flame_colors)
        
        # Set initial title color
        r = int(self.current_color[0] * 0.5 + self.next_color[0] * 0.5)
        g = int(self.current_color[1] * 0.5 + self.next_color[1] * 0.5)
        b = int(self.current_color[2] * 0.5 + self.next_color[2] * 0.5)
        self.title_color = (r, g, b)
    
    def _create_static_background(self):
        """Create a static background surface with elements that don't change."""
        self.static_surface = pygame.Surface((self.width, self.height))
        self.static_surface.fill((0, 0, 0))  # Black background
        
        # Draw static gravitational particles
        for particle in self.grav_particles:
            pygame.draw.circle(
                self.static_surface, 
                particle["color"],
                (int(particle["x"]), int(particle["y"])),
                particle["size"]
            )
        
        # Draw static UI elements
        
        # Draw default button background
        pygame.draw.rect(self.static_surface, (20, 20, 20), self.default_button)
        for i in range(1, 6):
            default_rect = pygame.Rect(
                self.default_button.x - i, 
                self.default_button.y - i, 
                self.default_button.width + 2*i, 
                self.default_button.height + 2*i
            )
            pygame.draw.rect(self.static_surface, (0, 200, 255), default_rect, 1)
        
        # Draw QBoard button background
        pygame.draw.rect(self.static_surface, (20, 20, 20), self.qboard_button)
        for i in range(1, 6):
            qboard_rect = pygame.Rect(
                self.qboard_button.x - i, 
                self.qboard_button.y - i, 
                self.qboard_button.width + 2*i, 
                self.qboard_button.height + 2*i
            )
            pygame.draw.rect(self.static_surface, (255, 0, 150), qboard_rect, 1)
        
        # Draw button text
        default_text = self.small_font.render("Default", True, (255, 255, 255))
        default_text_rect = default_text.get_rect(center=self.default_button.center)
        self.static_surface.blit(default_text, default_text_rect)
        
        qboard_text = self.small_font.render("QBoard", True, (255, 255, 255))
        qboard_text_rect = qboard_text.get_rect(center=self.qboard_button.center)
        self.static_surface.blit(qboard_text, qboard_text_rect)
        
        # Draw instructions and auto-detected mode
        display_text = self.small_font.render("Choose Display Size:", True, (255, 255, 255))
        display_rect = display_text.get_rect(center=(self.width // 2, self.height // 2 + self.instruction_y_pos))
        self.static_surface.blit(display_text, display_rect)
        
        auto_text = self.small_font.render(f"Auto-detected: {self.detected_mode}", True, (200, 200, 200))
        auto_rect = auto_text.get_rect(center=(self.width // 2, self.height // 2 + self.button_y_pos + self.button_height + 30))
        self.static_surface.blit(auto_text, auto_rect)
        
        # Draw collaboration text
        collab_text1 = self.collab_font.render("In collaboration with ", True, (255, 255, 255))
        collab_text3 = self.collab_font.render(" Kindergarten", True, (255, 255, 255))
        self.static_surface.blit(collab_text1, self.collab_rect1)
        self.static_surface.blit(collab_text3, self.collab_rect3)
        
        # Draw creator text
        creator_text = self.small_font.render("Created by Teacher Evan and Teacher Lee", True, (255, 255, 255))
        creator_rect = creator_text.get_rect(center=(self.width // 2, self.height - 40))
        self.static_surface.blit(creator_text, creator_rect) 