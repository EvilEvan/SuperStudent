"""
Resource manager for loading and caching game assets.
"""

import pygame
import os
from typing import Dict, Optional, Tuple

class ResourceManager:
    def __init__(self):
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[Tuple[str, int], pygame.font.Font] = {}
    
    def load_image(self, path: str) -> pygame.Surface:
        """Load and cache an image."""
        if path not in self.images:
            try:
                self.images[path] = pygame.image.load(path).convert_alpha()
            except pygame.error as e:
                print(f"Error loading image {path}: {e}")
                # Return a placeholder surface
                surf = pygame.Surface((32, 32))
                surf.fill((255, 0, 255))
                return surf
        return self.images[path]
    
    def load_sound(self, path: str) -> pygame.mixer.Sound:
        """Load and cache a sound."""
        if path not in self.sounds:
            try:
                self.sounds[path] = pygame.mixer.Sound(path)
            except pygame.error as e:
                print(f"Error loading sound {path}: {e}")
                # Return a silent sound
                return pygame.mixer.Sound(buffer=bytes([0] * 1000))
        return self.sounds[path]
    
    def get_font(self, name: str, size: int) -> pygame.font.Font:
        """Get or create a font."""
        key = (name, size)
        if key not in self.fonts:
            try:
                if name.lower() == 'default':
                    self.fonts[key] = pygame.font.Font(None, size)
                else:
                    self.fonts[key] = pygame.font.Font(name, size)
            except pygame.error as e:
                print(f"Error loading font {name}: {e}")
                # Fall back to default font
                self.fonts[key] = pygame.font.Font(None, size)
        return self.fonts[key]
    
    def clear_cache(self) -> None:
        """Clear all cached resources."""
        self.images.clear()
        self.sounds.clear()
        self.fonts.clear()
    
    def preload_directory(self, directory: str, extensions: Tuple[str, ...] = ('.png', '.jpg', '.wav', '.mp3')) -> None:
        """Preload all resources in a directory."""
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(extensions):
                    path = os.path.join(root, file)
                    if path.lower().endswith(('.png', '.jpg')):
                        self.load_image(path)
                    elif path.lower().endswith(('.wav', '.mp3')):
                        self.load_sound(path) 