"""
SuperStudent - Resource Manager

This module handles the loading, caching, and unloading of game resources,
implementing lazy loading to improve performance and memory usage.
"""
import pygame

class ResourceManager:
    """
    Manages game resources including fonts, images, and sounds.
    Implements lazy loading and caching to improve performance.
    """
    
    def __init__(self):
        """Initialize the resource manager with empty caches."""
        self.fonts = {}
        self.images = {}
        self.sounds = {}
        self.display_mode = "DEFAULT"  # Default mode
        
    def set_display_mode(self, mode):
        """Set the current display mode which affects resource sizing."""
        if mode in ["DEFAULT", "QBOARD"]:
            self.display_mode = mode
            # Clear font cache when display mode changes
            self.fonts = {}
    
    def get_font(self, font_type, force_reload=False):
        """
        Get a font of the specified type, loading it if necessary.
        
        Args:
            font_type: String indicating which font to load ('small', 'large', etc.)
            force_reload: If True, reload the font even if it's cached
            
        Returns:
            A pygame Font object
        """
        from settings import FONT_SIZES
        
        # Create a cache key that includes the display mode
        cache_key = f"{self.display_mode}_{font_type}"
        
        # Return cached font if available and not forcing reload
        if cache_key in self.fonts and not force_reload:
            return self.fonts[cache_key]
        
        # Load font based on type and current display mode
        font_size = None
        if font_type in FONT_SIZES[self.display_mode]:
            font_size = FONT_SIZES[self.display_mode][font_type]
        else:
            # Default sizes if not specifically defined
            default_sizes = {
                "small": 36,
                "medium": 48,
                "large": 64,
                "title": 128
            }
            font_size = default_sizes.get(font_type, 36)  # Default to small font
        
        # Load the font and cache it
        font = pygame.font.Font(None, font_size)
        self.fonts[cache_key] = font
        return font
    
    def cleanup(self):
        """Release all loaded resources to free memory."""
        self.fonts = {}
        self.images = {}
        self.sounds = {}
    
    def unload_unused(self, used_keys):
        """
        Unload resources that aren't in the provided set of used keys.
        
        Args:
            used_keys: Set of resource keys that should be kept
        """
        # Unload unused fonts
        font_keys = list(self.fonts.keys())
        for key in font_keys:
            if key not in used_keys:
                del self.fonts[key]
        
        # Unload unused images
        image_keys = list(self.images.keys())
        for key in image_keys:
            if key not in used_keys:
                del self.images[key]
        
        # Unload unused sounds
        sound_keys = list(self.sounds.keys())
        for key in sound_keys:
            if key not in used_keys:
                del self.sounds[key] 