"""
SuperStudent - Resource Manager

This module handles the loading, caching, and unloading of game resources,
implementing lazy loading to improve performance and memory usage.
"""
import pygame
import gc
import os
import time

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
        self.level_resources = {}  # Dictionary to track resources by level
        self.current_level = None  # Currently active level
        self.display_mode = "DEFAULT"  # Default mode
        self.memory_usage = 0  # Track approximate memory usage
        self.resource_stats = {
            "fonts": 0,
            "images": 0,
            "sounds": 0
        }  # Track resource counts
        
    def set_display_mode(self, mode):
        """Set the current display mode which affects resource sizing."""
        if mode in ["DEFAULT", "QBOARD"]:
            self.display_mode = mode
            # Clear font cache when display mode changes
            self.fonts = {}
            self.resource_stats["fonts"] = 0
    
    def get_font(self, font_type, force_reload=False, level=None):
        """
        Get a font of the specified type, loading it if necessary.
        
        Args:
            font_type: String indicating which font to load ('small', 'large', etc.)
            force_reload: If True, reload the font even if it's cached
            level: Optional level name to associate this resource with
            
        Returns:
            A pygame Font object
        """
        from settings import FONT_SIZES
        
        # Create a cache key that includes the display mode
        cache_key = f"{self.display_mode}_{font_type}"
        
        # Return cached font if available and not forcing reload
        if cache_key in self.fonts and not force_reload:
            # If a level is specified, add this resource to the level's resource list
            if level:
                self._register_resource_to_level(level, "fonts", cache_key)
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
        self.resource_stats["fonts"] += 1
        
        # Associate with level if specified
        if level:
            self._register_resource_to_level(level, "fonts", cache_key)
            
        return font
    
    def get_image(self, image_path, scale=None, level=None):
        """
        Load and cache an image.
        
        Args:
            image_path: Path to the image file
            scale: Optional tuple (width, height) to scale the image
            level: Optional level name to associate this resource with
            
        Returns:
            A pygame Surface object
        """
        # Create a cache key including scale information
        cache_key = image_path
        if scale:
            cache_key = f"{image_path}_scale_{scale[0]}x{scale[1]}"
            
        # Return cached image if available
        if cache_key in self.images:
            # Associate with level if specified
            if level:
                self._register_resource_to_level(level, "images", cache_key)
            return self.images[cache_key]
            
        # Check if file exists
        if not os.path.exists(image_path):
            print(f"Warning: Image file not found: {image_path}")
            # Create a small red square as a placeholder
            placeholder = pygame.Surface((32, 32))
            placeholder.fill((255, 0, 0))
            self.images[cache_key] = placeholder
            self.resource_stats["images"] += 1
            return placeholder
            
        # Load the image
        try:
            image = pygame.image.load(image_path).convert_alpha()
            
            # Scale if needed
            if scale:
                image = pygame.transform.scale(image, scale)
                
            # Cache and associate with level if specified
            self.images[cache_key] = image
            self.resource_stats["images"] += 1
            
            # Update approximate memory usage
            self._update_memory_usage(image.get_width() * image.get_height() * 4)  # 4 bytes per pixel (RGBA)
                
            if level:
                self._register_resource_to_level(level, "images", cache_key)
                
            return image
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            # Create a small red square as a placeholder
            placeholder = pygame.Surface((32, 32))
            placeholder.fill((255, 0, 0))
            self.images[cache_key] = placeholder
            return placeholder
    
    def get_sound(self, sound_path, level=None):
        """
        Load and cache a sound effect.
        
        Args:
            sound_path: Path to the sound file
            level: Optional level name to associate this resource with
            
        Returns:
            A pygame Sound object
        """
        # Return cached sound if available
        if sound_path in self.sounds:
            # Associate with level if specified
            if level:
                self._register_resource_to_level(level, "sounds", sound_path)
            return self.sounds[sound_path]
            
        # Check if file exists
        if not os.path.exists(sound_path):
            print(f"Warning: Sound file not found: {sound_path}")
            return None
            
        # Load the sound
        try:
            sound = pygame.mixer.Sound(sound_path)
            
            # Cache and associate with level if specified
            self.sounds[sound_path] = sound
            self.resource_stats["sounds"] += 1
            
            if level:
                self._register_resource_to_level(level, "sounds", sound_path)
                
            return sound
        except Exception as e:
            print(f"Error loading sound {sound_path}: {e}")
            return None
    
    def set_current_level(self, level_name):
        """
        Set the current active level - used for managing level-specific resources.
        
        Args:
            level_name: Name of the level (e.g., "COLORS_LEVEL")
        """
        if level_name != self.current_level:
            print(f"Resource Manager: Switching from level {self.current_level} to {level_name}")
            self.current_level = level_name
            
            # Initialize level resources if not already present
            if level_name and level_name not in self.level_resources:
                self.level_resources[level_name] = {
                    "fonts": set(),
                    "images": set(),
                    "sounds": set()
                }
    
    def _register_resource_to_level(self, level_name, resource_type, resource_key):
        """
        Register a resource as being used by a specific level.
        
        Args:
            level_name: Name of the level
            resource_type: Type of resource ("fonts", "images", "sounds")
            resource_key: Key for the resource in the corresponding cache
        """
        if level_name not in self.level_resources:
            self.level_resources[level_name] = {
                "fonts": set(),
                "images": set(),
                "sounds": set()
            }
            
        self.level_resources[level_name][resource_type].add(resource_key)
    
    def unload_level_resources(self, level_name):
        """
        Unload all resources associated with a specific level.
        
        Args:
            level_name: Name of the level to unload resources for
        """
        if level_name not in self.level_resources:
            return
            
        print(f"Resource Manager: Unloading resources for {level_name}")
        resources_to_keep = set()
        
        # Check if any resources are shared with other levels
        for other_level, resources in self.level_resources.items():
            if other_level != level_name and other_level == self.current_level:
                for resource_type in resources:
                    resources_to_keep.update(resources[resource_type])
        
        # Unload fonts that are only used by this level
        for font_key in list(self.level_resources[level_name]["fonts"]):
            if font_key not in resources_to_keep and font_key in self.fonts:
                del self.fonts[font_key]
                self.resource_stats["fonts"] -= 1
                
        # Unload images that are only used by this level
        for image_key in list(self.level_resources[level_name]["images"]):
            if image_key not in resources_to_keep and image_key in self.images:
                del self.images[image_key]
                self.resource_stats["images"] -= 1
                
        # Unload sounds that are only used by this level
        for sound_key in list(self.level_resources[level_name]["sounds"]):
            if sound_key not in resources_to_keep and sound_key in self.sounds:
                del self.sounds[sound_key]
                self.resource_stats["sounds"] -= 1
                
        # Clear the level's resource tracking
        del self.level_resources[level_name]
        
        # Force garbage collection to reclaim memory
        gc.collect()
        
        print(f"Resource Manager: After unloading level {level_name}, stats: {self.resource_stats}")
    
    def cleanup(self):
        """Release all loaded resources to free memory."""
        print("Resource Manager: Full cleanup of all resources")
        self.fonts = {}
        self.images = {}
        self.sounds = {}
        self.level_resources = {}
        self.resource_stats = {
            "fonts": 0,
            "images": 0,
            "sounds": 0
        }
        self.memory_usage = 0
        
        # Force garbage collection
        gc.collect()
    
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
                self.resource_stats["fonts"] -= 1
        
        # Unload unused images
        image_keys = list(self.images.keys())
        for key in image_keys:
            if key not in used_keys:
                del self.images[key]
                self.resource_stats["images"] -= 1
        
        # Unload unused sounds
        sound_keys = list(self.sounds.keys())
        for key in sound_keys:
            if key not in used_keys:
                del self.sounds[key]
                self.resource_stats["sounds"] -= 1
                
        # Force garbage collection
        gc.collect()
    
    def _update_memory_usage(self, bytes_delta):
        """
        Update the approximate memory usage tracking.
        
        Args:
            bytes_delta: Change in memory usage in bytes
        """
        self.memory_usage += bytes_delta
        
    def get_memory_usage(self):
        """
        Get the current approximate memory usage in MB.
        
        Returns:
            Memory usage in MB
        """
        return self.memory_usage / (1024 * 1024)
        
    def get_resource_stats(self):
        """
        Get statistics about loaded resources.
        
        Returns:
            Dictionary with resource statistics
        """
        return {
            "fonts": len(self.fonts),
            "images": len(self.images),
            "sounds": len(self.sounds),
            "memory_mb": self.get_memory_usage(),
            "level_resources": {level: {k: len(v) for k, v in resources.items()} 
                               for level, resources in self.level_resources.items()}
        }
        
    def preload_level_resources(self, level_name, resources_dict):
        """
        Preload a set of resources for a specific level.
        
        Args:
            level_name: Name of the level
            resources_dict: Dictionary of resources to load:
                {
                    "fonts": [("small", None), ("large", None)],  # (font_type, force_reload)
                    "images": [("path/to/image.png", (100, 100))],  # (path, scale)
                    "sounds": ["path/to/sound.wav"]  # path
                }
        """
        print(f"Resource Manager: Preloading resources for {level_name}")
        start_time = time.time()
        
        # Set the current level
        self.set_current_level(level_name)
        
        # Load fonts
        if "fonts" in resources_dict:
            for font_info in resources_dict["fonts"]:
                if isinstance(font_info, tuple) and len(font_info) == 2:
                    font_type, force_reload = font_info
                    self.get_font(font_type, force_reload, level_name)
                else:
                    self.get_font(font_info, False, level_name)
        
        # Load images
        if "images" in resources_dict:
            for image_info in resources_dict["images"]:
                if isinstance(image_info, tuple) and len(image_info) == 2:
                    path, scale = image_info
                    self.get_image(path, scale, level_name)
                else:
                    self.get_image(image_info, None, level_name)
        
        # Load sounds
        if "sounds" in resources_dict:
            for sound_path in resources_dict["sounds"]:
                self.get_sound(sound_path, level_name)
                
        # Print stats
        print(f"Resource Manager: Preloaded {level_name} resources in {time.time() - start_time:.2f}s")
        print(f"Resource Manager: Current stats: {self.resource_stats}") 