"""
Heads-Up Display system for showing game information.
"""

import pygame
from typing import Dict, Tuple, Optional

class HUD:
    def __init__(self):
        self.fonts: Dict[int, pygame.font.Font] = {}
        self.score: int = 0
        self.lives: int = 3
        self.level: int = 1
        self.message: Optional[str] = None
        self.message_timer: float = 0.0
    
    def get_font(self, size: int) -> pygame.font.Font:
        """Get or create a font of the specified size."""
        if size not in self.fonts:
            self.fonts[size] = pygame.font.Font(None, size)
        return self.fonts[size]
    
    def set_score(self, score: int) -> None:
        """Set the current score."""
        self.score = score
    
    def set_lives(self, lives: int) -> None:
        """Set the number of lives remaining."""
        self.lives = lives
    
    def set_level(self, level: int) -> None:
        """Set the current level."""
        self.level = level
    
    def show_message(self, message: str, duration: float = 2.0) -> None:
        """Show a temporary message on the HUD."""
        self.message = message
        self.message_timer = duration
    
    def update(self, dt: float) -> None:
        """Update HUD state."""
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = None
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the HUD on the given surface."""
        # Draw score
        score_text = self.get_font(36).render(f"Score: {self.score}", True, (255, 255, 255))
        surface.blit(score_text, (20, 20))
        
        # Draw lives
        lives_text = self.get_font(36).render(f"Lives: {self.lives}", True, (255, 255, 255))
        surface.blit(lives_text, (20, 70))
        
        # Draw level
        level_text = self.get_font(36).render(f"Level: {self.level}", True, (255, 255, 255))
        surface.blit(level_text, (20, 120))
        
        # Draw message if any
        if self.message and self.message_timer > 0:
            message_text = self.get_font(48).render(self.message, True, (255, 255, 255))
            text_rect = message_text.get_rect(center=(surface.get_width() // 2, 100))
            surface.blit(message_text, text_rect) 