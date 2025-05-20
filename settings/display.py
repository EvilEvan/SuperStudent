"""
Display settings and detection for SuperStudent game.
"""

import pygame
import os
from typing import Tuple, Optional

# Default display mode
DEFAULT_MODE = (800, 600)

def detect_display_type() -> Tuple[int, int]:
    """
    Detect the appropriate display mode based on the system.
    Returns (width, height) tuple.
    """
    # Try to read from settings file first
    try:
        with open('display_settings.txt', 'r') as f:
            mode = f.read().strip()
            if mode:
                width, height = map(int, mode.split('x'))
                return (width, height)
    except (FileNotFoundError, ValueError):
        pass
    
    # Try to detect screen size
    try:
        info = pygame.display.Info()
        return (info.current_w, info.current_h)
    except:
        pass
    
    # Fall back to default
    return DEFAULT_MODE

def save_display_mode(width: int, height: int) -> None:
    """Save the display mode to settings file."""
    try:
        with open('display_settings.txt', 'w') as f:
            f.write(f"{width}x{height}")
    except:
        pass

def get_display_mode() -> Tuple[int, int]:
    """Get the current display mode."""
    try:
        return pygame.display.get_surface().get_size()
    except:
        return DEFAULT_MODE

def set_display_mode(width: int, height: int, fullscreen: bool = False) -> Optional[pygame.Surface]:
    """Set the display mode and return the surface."""
    try:
        flags = pygame.FULLSCREEN if fullscreen else 0
        surface = pygame.display.set_mode((width, height), flags)
        save_display_mode(width, height)
        return surface
    except:
        return None 