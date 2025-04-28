"""
SuperStudent - Colors Level

This module contains the implementation of the colors level, where players
must identify and click on dots of the specified target color.
"""
import pygame
import random
import math
from enum import Enum, auto

# In the actual implementation, these would be imported from settings.py
from settings import (
    BLACK, WHITE, COLORS_LIST, COLOR_NAMES, CHECKPOINT_TRIGGER,
    DOT_RADIUS, DOT_SPEED_RANGE, DOT_SPEED_REDUCTION,
    MOTHER_RADIUS, VIBRATION_FRAMES, DISPERSE_FRAMES,
    ENABLE_COLLISION_GRID, COLLISION_GRID_SIZE, COLORS_COLLISION_DELAY
)

# In the actual implementation, these would be imported from utils modules
from utils.particle_system import ParticleSystem
from utils.effects import Effects, create_explosion


class DotsState(Enum):
    """States for the dots animation sequence."""
    MOTHER_VIBRATION = auto()   # Initial mother dot vibration
    WAITING_FOR_CLICK = auto()  # Waiting for click to start dispersion
    DISPERSION = auto()         # Mother dot dispersing into multiple dots
    GAMEPLAY = auto()           # Main gameplay with bouncing dots


class ColorsLevel:
    """Implementation of the colors level for the SuperStudent game."""
    
    def __init__(self, screen_width, screen_height, resource_manager, particle_system, effects):
        """Initialize the colors level.
        
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
            resource_manager: The resource manager for loading/unloading resources
            particle_system: The particle system for creating particles
            effects: The effects system for explosions, screen shake, etc.
        """
        self.width = screen_width
        self.height = screen_height
        self.center = (screen_width // 2, screen_height // 2)
        
        self.resource_manager = resource_manager
        self.particle_system = particle_system
        self.effects = effects
        
        # Level-specific state
        self.dots = []
        self.dots_state = DotsState.MOTHER_VIBRATION
        self.state_timer = VIBRATION_FRAMES
        self.mother_color = None
        self.mother_color_name = None
        self.disperse_particles = []
        
        # Target tracking
        self.used_colors = []
        self.target_dots_left = 10
        self.overall_destroyed = 0
        self.current_color_dots_destroyed = 0
        self.total_dots_destroyed = 0
        
        # Ghost notification for target color change
        self.ghost_notification = None
        
        # Grid for spatial partitioning (collision optimization)
        self.grid = {}
        self.grid_cell_size = COLLISION_GRID_SIZE
        
        # Collision control - now only enabled after first color change
        self.collision_enabled = False
        self.collision_timer = 0
        self.color_changed = False  # Track if first color change has occurred
        
        # Font caching
        self.small_font = None
        self.ghost_font = None
        
        # Flag to track initialization status
        self.initialized = False
        
    def initialize(self):
        """Initialize level-specific resources."""
        print("Colors Level: Initializing resources")
        
        # Set the current level in the resource manager
        self.resource_manager.set_current_level("COLORS_LEVEL")
        
        # Preload all fonts needed for this level
        level_resources = {
            "fonts": [
                ("small", False),
                ("large", False),
                ("medium", False)  # Used for HUD display
            ]
        }
        
        # Preload level resources
        self.resource_manager.preload_level_resources("COLORS_LEVEL", level_resources)
        
        # Get the fonts - they'll be automatically associated with this level
        self.small_font = self.resource_manager.get_font("small", False, "COLORS_LEVEL")
        self.ghost_font = self.resource_manager.get_font("large", False, "COLORS_LEVEL")
        
        # Select initial target color
        self._select_target_color()
        
        # Reset level state
        self.dots = []
        self.dots_state = DotsState.MOTHER_VIBRATION
        self.state_timer = VIBRATION_FRAMES
        self.disperse_particles = []
        self.ghost_notification = None
        self.grid = {}
        self.used_colors = []
        self.target_dots_left = 10
        self.overall_destroyed = 0
        self.current_color_dots_destroyed = 0
        self.total_dots_destroyed = 0
        self.collision_enabled = False
        self.collision_timer = 0
        self.color_changed = False
        
        # Print memory usage
        print(f"Colors Level: Resource stats after initialization: {self.resource_manager.get_resource_stats()}")
        
        self.initialized = True
        return True
        
    def update(self, delta_time):
        """Update level state based on current dot state."""
        if self.dots_state == DotsState.MOTHER_VIBRATION:
            # Handle mother dot vibration animation
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.dots_state = DotsState.WAITING_FOR_CLICK
                print("Colors Level: Transitioned to WAITING_FOR_CLICK state")
                
        elif self.dots_state == DotsState.DISPERSION:
            # Handle mother dot dispersion animation
            self.state_timer -= 1
            for p in self.disperse_particles:
                p["radius"] += p["speed"] * delta_time * 50  # Scale with delta time
                
            if self.state_timer <= 0:
                print("Colors Level: Dispersion complete, transitioning to GAMEPLAY")
                self._initialize_bouncing_dots()
                self.dots_state = DotsState.GAMEPLAY
                
        elif self.dots_state == DotsState.GAMEPLAY:
            # Update ghost notification if present
            if self.ghost_notification:
                self.ghost_notification["duration"] -= 1
                if self.ghost_notification["duration"] < 50:
                    self.ghost_notification["alpha"] -= 5
                if self.ghost_notification["duration"] <= 0:
                    self.ghost_notification = None
            
            # Check for dots stuck in center and clear them occasionally
            self._check_center_clusters()
            
            # Update dots movement and handle collisions
            self._update_dots(delta_time)
            
            # Check if we need to generate new dots
            if self.target_dots_left <= 0:
                print(f"Colors Level: No targets left, generating new dots. Collision enabled: {self.collision_enabled}")
                self._generate_new_dots()
                
        return True
        
    def draw(self, screen):
        """Draw the current state of the level."""
        # Get shake offset from effects system
        offset_x, offset_y = self.effects.get_shake_offset()
        
        # Fill background
        screen.fill(BLACK)
        
        # Draw based on current state
        if self.dots_state == DotsState.MOTHER_VIBRATION:
            # Draw vibrating mother dot
            vib_x = self.center[0] + random.randint(-6, 6) + offset_x
            vib_y = self.center[1] + random.randint(-6, 6) + offset_y
            pygame.draw.circle(screen, self.mother_color, (vib_x, vib_y), MOTHER_RADIUS)
            
            # Draw label
            label = self.small_font.render("Remember this color!", True, WHITE)
            label_rect = label.get_rect(center=(self.width // 2, self.height // 2 + MOTHER_RADIUS + 60))
            screen.blit(label, label_rect)
            
        elif self.dots_state == DotsState.WAITING_FOR_CLICK:
            # Draw mother dot waiting for click
            pygame.draw.circle(screen, self.mother_color, 
                              (self.center[0] + offset_x, self.center[1] + offset_y), 
                              MOTHER_RADIUS)
            
            # Draw labels
            label = self.small_font.render("Remember this color!", True, WHITE)
            label_rect = label.get_rect(center=(self.width // 2, self.height // 2 + MOTHER_RADIUS + 60))
            screen.blit(label, label_rect)
            
            prompt = self.small_font.render("Click to start!", True, (255, 255, 0))
            prompt_rect = prompt.get_rect(center=(self.width // 2, self.height // 2 + MOTHER_RADIUS + 120))
            screen.blit(prompt, prompt_rect)
            
        elif self.dots_state == DotsState.DISPERSION:
            # Draw dispersing particles
            for p in self.disperse_particles:
                x = int(self.center[0] + math.cos(p["angle"]) * p["radius"])
                y = int(self.center[1] + math.sin(p["angle"]) * p["radius"])
                pygame.draw.circle(screen, p["color"], (x + offset_x, y + offset_y), DOT_RADIUS)
                
        elif self.dots_state == DotsState.GAMEPLAY:
            # Draw background elements (handled by main game)
            
            # Draw all alive dots with screen shake offsets
            for dot in self.dots:
                if dot["alive"]:
                    pygame.draw.circle(
                        screen, 
                        dot["color"], 
                        (int(dot["x"] + offset_x), int(dot["y"] + offset_y)), 
                        dot["radius"]
                    )
            
            # Display reference target at top right
            pygame.draw.circle(screen, self.mother_color, (self.width - 60, 60), DOT_RADIUS)
            pygame.draw.rect(screen, WHITE, (self.width - 90, 30, 60, 60), 2)
            
            # Draw ghost notification if active
            if self.ghost_notification and self.ghost_notification["duration"] > 0:
                self._draw_ghost_notification(screen)
            
            # Display HUD info
            self._draw_hud(screen)
            
            # Draw collision status message if collisions are not yet enabled
            if not self.collision_enabled:
                indicator_text = self.small_font.render(
                    "Collisions will be enabled after first color change", 
                    True, 
                    (255, 255, 0)
                )
                text_rect = indicator_text.get_rect(center=(self.width // 2, 60))
                screen.blit(indicator_text, text_rect)
            
        # Draw explosions (handled by effects system)
        self.effects.draw_explosions(screen, offset_x, offset_y)
        
        pygame.display.flip()
        
    def handle_event(self, event):
        """Handle pygame events specific to this level."""
        if event.type == pygame.QUIT:
            return "QUIT"
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "LEVEL_MENU"
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            
            # Handle based on current state
            if self.dots_state == DotsState.WAITING_FOR_CLICK:
                # Start dispersion animation
                self.dots_state = DotsState.DISPERSION
                self.state_timer = DISPERSE_FRAMES
                self._initialize_dispersion()
                return None
                
            elif self.dots_state == DotsState.GAMEPLAY:
                # Handle dot clicking
                hit_target = False
                for dot in self.dots:
                    if dot["alive"]:
                        dist = math.hypot(mx - dot["x"], my - dot["y"])
                        if dist <= dot["radius"]:
                            hit_target = True
                            if dot["target"]:
                                self._handle_target_hit(dot)
                            break
                
                # Add crack on misclick
                if not hit_target:
                    self.effects.create_crack(mx, my)
                    
        return None
        
    def cleanup(self):
        """Clean up level-specific resources."""
        print("Colors Level: Cleanup")
        
        # Clear game objects
        self.dots = []
        self.disperse_particles = []
        self.ghost_notification = None
        
        # Release references to fonts
        self.small_font = None
        self.ghost_font = None
        
        # Unload level-specific resources through resource manager
        if self.resource_manager:
            self.resource_manager.unload_level_resources("COLORS_LEVEL")
            
            # Print memory stats after cleanup
            print(f"Colors Level: Resource stats after cleanup: {self.resource_manager.get_resource_stats()}")
        
        self.initialized = False
        return True
        
    def _initialize_dispersion(self):
        """Set up the mother dot dispersion animation."""
        self.disperse_particles = []
        for i in range(100):
            angle = random.uniform(0, 2 * math.pi)
            self.disperse_particles.append({
                "angle": angle,
                "radius": 0,
                "speed": random.uniform(15, 25),  # Increased from 12-18 to 15-25
                "color": self.mother_color if i < 25 else None,  # Will assign distractor colors below
            })
            
        # Assign distractor colors
        distractor_colors = [c for idx, c in enumerate(COLORS_LIST) if idx != self.color_idx]
        num_distractor_colors = len(distractor_colors)
        total_distractor_dots = 75
        dots_per_color = total_distractor_dots // num_distractor_colors
        extra = total_distractor_dots % num_distractor_colors
        idx = 25
        
        for color_idx, color in enumerate(distractor_colors):
            count = dots_per_color + (1 if color_idx < extra else 0)
            for _ in range(count):
                if idx < 100:
                    self.disperse_particles[idx]["color"] = color
                    idx += 1
                    
        print("Colors Level: Dispersion initialized with increased speed")
        
    def _initialize_bouncing_dots(self):
        """Initialize the bouncing dots after dispersion animation."""
        self.dots = []
        
        # Collisions are disabled until first color change
        self.collision_enabled = False
        self.color_changed = False
        
        print("Colors Level: Initializing dots with FORCED OUTER POSITIONING")
        
        # Count how many dots of each color we need to create
        target_colors_count = sum(1 for p in self.disperse_particles if p["color"] == self.mother_color)
        
        # Create positions around the outer part of the screen - avoid center completely
        margin = 80  # Keep away from edges
        center_x, center_y = self.center
        screen_radius = min(self.width, self.height) / 2 - margin
        min_dist_from_center = screen_radius * 0.5  # Start at least 50% away from center
        
        # Create dots with random positions around the outer area of the screen
        for i, p in enumerate(self.disperse_particles):
            # Generate a random angle and distance from center
            angle = random.uniform(0, 2 * math.pi)
            
            # Distance from center - force to be in the outer half of the screen
            distance = random.uniform(min_dist_from_center, screen_radius)
            
            # Calculate position
            x = center_x + math.cos(angle) * distance
            y = center_y + math.sin(angle) * distance
            
            # Ensure within screen bounds
            x = max(DOT_RADIUS + 10, min(self.width - DOT_RADIUS - 10, x))
            y = max(DOT_RADIUS + 10, min(self.height - DOT_RADIUS - 10, y))
            
            # Velocity directed away from center
            speed = random.uniform(6, 12)  # Relatively fast speed
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            
            color = p["color"]
            self.dots.append({
                "x": x, "y": y,
                "dx": dx, "dy": dy,
                "color": color,
                "radius": DOT_RADIUS,
                "target": color == self.mother_color,
                "alive": True,
            })
            
        # Clear dispersion particles
        self.disperse_particles = []
        
        # Sanity check logging
        alive_dots = sum(1 for d in self.dots if d["alive"])
        target_dots = sum(1 for d in self.dots if d["alive"] and d["target"])
        print(f"Colors Level: Created {alive_dots} total dots ({target_dots} targets)")
        self.target_dots_left = target_dots
        
    def _select_target_color(self):
        """Select the next target color, ensuring all colors are used before repeating."""
        # Get available colors (those not yet used in the current cycle)
        available_colors = [i for i in range(len(COLORS_LIST)) if i not in self.used_colors]
        
        # If all colors have been used, reset tracking
        if not available_colors:
            # Keep current color as used to avoid immediate repetition
            self.used_colors = [self.color_idx] if hasattr(self, 'color_idx') else []
            available_colors = [i for i in range(len(COLORS_LIST)) if i not in self.used_colors]
            
        # Select a random color from available colors
        self.color_idx = random.choice(available_colors)
        self.used_colors.append(self.color_idx)
        
        # Set the target color
        self.mother_color = COLORS_LIST[self.color_idx]
        self.mother_color_name = COLOR_NAMES[self.color_idx]
        
        print(f"Colors Level: Selected target color: {self.mother_color_name}")
        # Do NOT change color_changed flag here - this should only happen in _switch_target_color
        
    def _update_dots(self, delta_time):
        """Update all dots positions and handle collisions."""
        # Count alive dots for debugging
        alive_dots = sum(1 for d in self.dots if d["alive"])
        if alive_dots < 50 and random.random() < 0.01:  # Only print occasionally
            print(f"Colors Level: {alive_dots} alive dots, {self.target_dots_left} targets left, collisions {'enabled' if self.collision_enabled else 'disabled'}")
        
        # Clear the grid for spatial partitioning
        if ENABLE_COLLISION_GRID:
            self.grid = {}
            
        # Update dot positions and add to grid
        for dot in self.dots:
            if not dot["alive"]:
                continue
                
            # Apply center avoidance to prevent dots from heading toward center
            self._apply_center_avoidance(dot)
                
            # Update position with delta time
            dot["x"] += dot["dx"] * delta_time * 50  # Scale with delta time
            dot["y"] += dot["dy"] * delta_time * 50
            
            # Bounce off walls
            if dot["x"] - dot["radius"] < 0:
                dot["x"] = dot["radius"]
                dot["dx"] *= -1
            if dot["x"] + dot["radius"] > self.width:
                dot["x"] = self.width - dot["radius"]
                dot["dx"] *= -1
            if dot["y"] - dot["radius"] < 0:
                dot["y"] = dot["radius"]
                dot["dy"] *= -1
            if dot["y"] + dot["radius"] > self.height:
                dot["y"] = self.height - dot["radius"]
                dot["dy"] *= -1
                
            # Add to spatial grid for collision detection
            if ENABLE_COLLISION_GRID:
                grid_x = int(dot["x"] / self.grid_cell_size)
                grid_y = int(dot["y"] / self.grid_cell_size)
                
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        cell_key = (grid_x + i, grid_y + j)
                        if cell_key not in self.grid:
                            self.grid[cell_key] = []
                        self.grid[cell_key].append(dot)
        
        # Only check for collisions if they are enabled (after first color change)
        if not self.collision_enabled:
            return
            
        # Debuggable collision counter to verify collisions are actually happening
        collision_count = 0
        
        # Handle collisions using spatial partitioning
        if ENABLE_COLLISION_GRID:
            checked_pairs = set()
            
            for cell, dots_in_cell in self.grid.items():
                for i, dot1 in enumerate(dots_in_cell):
                    if not dot1["alive"]:
                        continue
                        
                    for j in range(i+1, len(dots_in_cell)):
                        dot2 = dots_in_cell[j]
                        if not dot2["alive"]:
                            continue
                            
                        # Create a unique pair ID (using object IDs)
                        pair_id = (id(dot1), id(dot2)) if id(dot1) < id(dot2) else (id(dot2), id(dot1))
                        
                        # Skip if this pair was already checked
                        if pair_id in checked_pairs:
                            continue
                            
                        checked_pairs.add(pair_id)
                        
                        # Check collision
                        collision_occurred = self._check_collision(dot1, dot2)
                        if collision_occurred:
                            collision_count += 1
        else:
            # Fallback to O(n²) collision detection if grid is disabled
            for i, dot1 in enumerate(self.dots):
                if not dot1["alive"]:
                    continue
                    
                for j, dot2 in enumerate(self.dots[i+1:], i+1):
                    if not dot2["alive"]:
                        continue
                        
                    collision_occurred = self._check_collision(dot1, dot2)
                    if collision_occurred:
                        collision_count += 1
        
        # Log collision count occasionally
        if collision_count > 0 and random.random() < 0.1:
            print(f"Colors Level: {collision_count} collisions detected this frame")
        
    def _apply_center_avoidance(self, dot):
        """Apply a force to prevent dots from moving toward the center - acts like a repulsive force."""
        center_x, center_y = self.center
        
        # Calculate vector from center to dot
        dx = dot["x"] - center_x
        dy = dot["y"] - center_y
        dist = math.hypot(dx, dy)
        
        # Skip if dot is far enough from center
        if dist > 250:
            return
            
        # Calculate normalized direction vector away from center
        if dist > 0:  # Avoid division by zero
            nx = dx / dist
            ny = dy / dist
        else:
            # If at center (extremely unlikely), move in random direction
            angle = random.uniform(0, 2 * math.pi)
            nx = math.cos(angle)
            ny = math.sin(angle)
            
        # Determine if dot is heading toward center
        # Calculate dot product of velocity and direction to center
        dot_product = dot["dx"] * -nx + dot["dy"] * -ny
        
        # If dot product is positive, the dot is moving toward center
        if dot_product > 0:
            # Calculate force intensity - stronger when closer to center and moving faster toward it
            force_intensity = max(0, (250 - dist) / 250 * dot_product * 2)
            
            # Apply repulsive force
            dot["dx"] += nx * force_intensity
            dot["dy"] += ny * force_intensity
            
            # If very close to center, apply emergency boost outward
            if dist < 100:
                emergency_force = (100 - dist) / 100 * 5
                dot["dx"] += nx * emergency_force
                dot["dy"] += ny * emergency_force
        
    def _check_collision(self, dot1, dot2):
        """Check for collision between two dots and handle if necessary.
        
        Returns:
            bool: True if a collision occurred and was handled, False otherwise.
        """
        # Calculate distance between centers
        dx = dot1["x"] - dot2["x"]
        dy = dot1["y"] - dot2["y"]
        distance = math.hypot(dx, dy)
        
        # Check for collision
        if distance < (dot1["radius"] + dot2["radius"]):
            # Normalize direction vector
            if distance > 0:  # Avoid division by zero
                nx = dx / distance
                ny = dy / distance
            else:
                nx, ny = 1, 0  # Default if dots are at same position
                if random.random() < 0.1:  # Only print occasionally for zero distance collisions
                    print(f"Colors Level: WARNING - Dots at same position. Colors: {dot1['color']} and {dot2['color']}")
                
            # Calculate relative velocity
            dvx = dot1["dx"] - dot2["dx"]
            dvy = dot1["dy"] - dot2["dy"]
            
            # Calculate velocity component along normal
            velocity_along_normal = dvx * nx + dvy * ny
            
            # Only separate if moving toward each other
            if velocity_along_normal < 0:
                # Separate dots to prevent sticking
                overlap = (dot1["radius"] + dot2["radius"]) - distance
                dot1["x"] += overlap/2 * nx
                dot1["y"] += overlap/2 * ny
                dot2["x"] -= overlap/2 * nx
                dot2["y"] -= overlap/2 * ny
                
                # Make separation more aggressive for zero or near-zero distances
                if distance < 5:
                    # Apply additional separation force
                    separation_boost = 5
                    dot1["x"] += separation_boost * nx
                    dot1["y"] += separation_boost * ny
                    dot2["x"] -= separation_boost * nx
                    dot2["y"] -= separation_boost * ny
                    
                    # Apply more random velocities to break clusters
                    dot1["dx"] = random.uniform(-8, 8)
                    dot1["dy"] = random.uniform(-8, 8)
                    dot2["dx"] = random.uniform(-8, 8)
                    dot2["dy"] = random.uniform(-8, 8)
                    if random.random() < 0.1:  # Only print occasionally
                        print(f"Colors Level: Applied emergency separation for very close dots")
                else:
                    # Standard collision response - swap velocities and reduce speed by 20%
                    temp_dx = dot1["dx"]
                    temp_dy = dot1["dy"]
                    
                    dot1["dx"] = dot2["dx"] * DOT_SPEED_REDUCTION
                    dot1["dy"] = dot2["dy"] * DOT_SPEED_REDUCTION
                    
                    dot2["dx"] = temp_dx * DOT_SPEED_REDUCTION
                    dot2["dy"] = temp_dy * DOT_SPEED_REDUCTION
                
                # Create small particle effect at collision point
                collision_x = (dot1["x"] + dot2["x"]) / 2
                collision_y = (dot1["y"] + dot2["y"]) / 2
                
                for _ in range(3):  # Create a few particles
                    self.particle_system.create_particle(
                        collision_x, 
                        collision_y,
                        random.choice([dot1["color"], dot2["color"]]),
                        random.randint(5, 10),
                        random.uniform(-2, 2), 
                        random.uniform(-2, 2),
                        10  # Short duration
                    )
                
                return True  # Collision occurred and was handled
            
        return False  # No collision or not moving toward each other
        
    def _handle_target_hit(self, dot):
        """Handle a target dot being hit."""
        dot["alive"] = False
        self.target_dots_left -= 1
        self.overall_destroyed += 1
        self.current_color_dots_destroyed += 1
        self.total_dots_destroyed += 1
        
        # Create explosion at dot position
        self.effects.create_explosion(
            dot["x"], dot["y"], 
            color=dot["color"], 
            max_radius=60, 
            duration=15
        )
        
        # Check if we need to switch target color
        if self.current_color_dots_destroyed >= 5:
            self._switch_target_color()
            
        # Check for checkpoint trigger
        if self.total_dots_destroyed % CHECKPOINT_TRIGGER == 0:
            return "CHECKPOINT"
            
        return None
        
    def _switch_target_color(self):
        """Switch to the next target color."""
        current_color = self.mother_color_name if hasattr(self, 'mother_color_name') else "None"
        self._select_target_color()
        self.current_color_dots_destroyed = 0
        
        # Mark that a color change has occurred and enable collisions if this is the first change
        if not self.color_changed:
            self.color_changed = True
            self.collision_enabled = True
            print(f"Colors Level: FIRST COLOR CHANGE from {current_color} to {self.mother_color_name}. COLLISIONS ENABLED.")
        else:
            print(f"Colors Level: Color changed from {current_color} to {self.mother_color_name}. Collisions already enabled.")
        
        # Setup ghost notification for new target color
        self.ghost_notification = {
            "color": self.mother_color,
            "duration": 100,
            "alpha": 255,
            "radius": 150,
            "text": self.mother_color_name
        }
        
        # Update target status for all dots
        for d in self.dots:
            if d["alive"]:
                d["target"] = (d["color"] == self.mother_color)
                
        # Update target_dots_left count
        self.target_dots_left = sum(1 for d in self.dots if d["target"] and d["alive"])
        
    def _generate_new_dots(self):
        """Generate new dots when all targets are destroyed."""
        new_dots_count = 10
        self.target_dots_left = new_dots_count
        
        # Select next target color
        self._select_target_color()
        
        # Setup ghost notification
        self.ghost_notification = {
            "color": self.mother_color,
            "duration": 100,
            "alpha": 255,
            "radius": 150,
            "text": self.mother_color_name
        }
        
        # Remove dead dots
        self.dots = [d for d in self.dots if d["alive"]]
        
        # Calculate how many new dots to create
        new_dots_needed = 100 - len(self.dots)
        
        # Count existing target dots
        existing_target_dots = sum(1 for d in self.dots if d["color"] == self.mother_color)
        target_dots_needed = new_dots_count - existing_target_dots
        target_dots_needed = max(0, target_dots_needed)
        
        # Generate new dots
        self._create_new_dots(new_dots_needed, target_dots_needed)
        
        # Update all dots' target status
        for d in self.dots:
            if d["color"] == self.mother_color:
                d["target"] = True
            else:
                d["target"] = False
                
        # Count and update actual target dots left
        self.target_dots_left = sum(1 for d in self.dots if d["target"] and d["alive"])
        
    def _create_new_dots(self, total_dots, target_dots):
        """Create new dots, ensuring proper spacing and target allocation."""
        print(f"Colors Level: Creating {total_dots} new dots ({target_dots} targets)")
        
        # Create positions around the outer part of the screen - avoid center completely
        margin = 80  # Keep away from edges
        center_x, center_y = self.center
        screen_radius = min(self.width, self.height) / 2 - margin
        min_dist_from_center = screen_radius * 0.5  # Start at least 50% away from center
        
        # Split screen into sectors to distribute dots evenly
        sectors = 8
        dots_per_sector = total_dots // sectors
        extra_dots = total_dots % sectors
        
        # Create dots with distributed positions around the screen
        for sector in range(sectors):
            # Calculate sector angle range
            sector_start_angle = sector * (2 * math.pi / sectors)
            sector_end_angle = (sector + 1) * (2 * math.pi / sectors)
            
            # How many dots to create in this sector
            dots_in_sector = dots_per_sector + (1 if sector < extra_dots else 0)
            
            # How many target dots to create in this sector
            target_dots_in_sector = min(target_dots, dots_in_sector)
            target_dots -= target_dots_in_sector
            
            for i in range(dots_in_sector):
                # Generate a random angle within this sector
                angle = random.uniform(sector_start_angle, sector_end_angle)
                
                # Distance from center - force to be in the outer half of the screen
                distance = random.uniform(min_dist_from_center, screen_radius)
                
                # Calculate position
                x = center_x + math.cos(angle) * distance
                y = center_y + math.sin(angle) * distance
                
                # Ensure within screen bounds
                x = max(DOT_RADIUS + 10, min(self.width - DOT_RADIUS - 10, x))
                y = max(DOT_RADIUS + 10, min(self.height - DOT_RADIUS - 10, y))
                
                # Velocity directed somewhat away from center, but with randomness
                speed = random.uniform(6, 12)
                angle_offset = random.uniform(-0.5, 0.5)  # Add some randomness to movement angle
                dx = math.cos(angle + angle_offset) * speed
                dy = math.sin(angle + angle_offset) * speed
                
                # Determine if target or distractor
                is_target = i < target_dots_in_sector
                
                # Set color based on target status
                if is_target:
                    color = self.mother_color
                else:
                    # Choose random distractor color
                    distractor_colors = [c for idx, c in enumerate(COLORS_LIST) if idx != self.color_idx]
                    color = random.choice(distractor_colors)
                
                # Add the new dot
                self.dots.append({
                    "x": x, "y": y,
                    "dx": dx, "dy": dy,
                    "color": color,
                    "radius": DOT_RADIUS,
                    "target": is_target,
                    "alive": True,
                })
        
    def _draw_ghost_notification(self, screen):
        """Draw the ghost notification for target color change."""
        # Create a semi-transparent surface
        ghost_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        ghost_surface.fill((0, 0, 0, 0))  # Transparent
        
        # Draw ghost dot
        alpha = min(255, self.ghost_notification["alpha"])
        ghost_color = self.ghost_notification["color"] + (alpha,)
        pygame.draw.circle(
            ghost_surface, 
            ghost_color, 
            (self.width // 2, self.height // 2), 
            self.ghost_notification["radius"]
        )
        
        # Add "Target Color:" label
        target_label = self.ghost_font.render("TARGET COLOR:", True, WHITE)
        target_label_rect = target_label.get_rect(
            center=(self.width // 2, self.height // 2 - self.ghost_notification["radius"] - 20)
        )
        ghost_surface.blit(target_label, target_label_rect)
        
        # Add color name
        ghost_text = self.ghost_font.render(
            self.ghost_notification["text"], 
            True, 
            self.ghost_notification["color"]
        )
        ghost_text_rect = ghost_text.get_rect(
            center=(self.width // 2, self.height // 2 + self.ghost_notification["radius"] + 30)
        )
        ghost_surface.blit(ghost_text, ghost_text_rect)
        
        # Apply the ghost surface
        screen.blit(ghost_surface, (0, 0))
        
    def _draw_hud(self, screen):
        """Draw the HUD information."""
        # Text color based on background
        text_color = WHITE  # Would be dynamic in full implementation
        
        # Score at top left
        score_text = self.small_font.render(f"Score: {self.overall_destroyed * 10}", True, text_color)
        screen.blit(score_text, (20, 20))
        
        # Target color below score
        target_color_text = self.small_font.render(f"Target Color: {self.mother_color_name}", True, text_color)
        screen.blit(target_color_text, (20, 60))
        
        # Target dots remaining
        dots_left_text = self.small_font.render(f"Remaining: {self.target_dots_left}", True, text_color)
        screen.blit(dots_left_text, (20, 100))
        
        # Next color progress
        next_color_text = self.small_font.render(
            f"Next color in: {5 - self.current_color_dots_destroyed} dots", 
            True, 
            text_color
        )
        screen.blit(next_color_text, (20, 140))
        
        # Progress on top right
        progress_text = self.small_font.render(f"Destroyed: {self.overall_destroyed}/∞", True, text_color)
        progress_rect = progress_text.get_rect(topright=(self.width - 20, 20))
        screen.blit(progress_text, progress_rect)
        
    def _check_center_clusters(self):
        """Check for and resolve dots stuck in the center."""
        # Run more frequently (about every 1-2 seconds)
        if random.random() > 0.04:
            return
            
        center_x, center_y = self.center
        center_dots = 0
        center_radius = 150  # Larger center area
        
        # Count dots in center
        for dot in self.dots:
            if not dot["alive"]:
                continue
                
            dist_to_center = math.hypot(dot["x"] - center_x, dot["y"] - center_y)
            if dist_to_center < center_radius:
                center_dots += 1
        
        # Lower threshold to 5 dots
        if center_dots > 5:
            print(f"Colors Level: Found {center_dots} dots near center - applying AGGRESSIVE separation")
            
            for dot in self.dots:
                if not dot["alive"]:
                    continue
                    
                dist_to_center = math.hypot(dot["x"] - center_x, dot["y"] - center_y)
                if dist_to_center < center_radius:
                    # Calculate angle from center to dot
                    angle = math.atan2(dot["y"] - center_y, dot["x"] - center_x)
                    
                    # Move dot much further outward from center
                    new_dist = center_radius * 2 + random.uniform(100, 200)
                    dot["x"] = center_x + math.cos(angle) * new_dist
                    dot["y"] = center_y + math.sin(angle) * new_dist
                    
                    # Ensure within screen bounds
                    dot["x"] = max(DOT_RADIUS + 10, min(self.width - DOT_RADIUS - 10, dot["x"]))
                    dot["y"] = max(DOT_RADIUS + 10, min(self.height - DOT_RADIUS - 10, dot["y"]))
                    
                    # Much faster outward velocity
                    speed = random.uniform(10, 15)
                    dot["dx"] = math.cos(angle) * speed
                    dot["dy"] = math.sin(angle) * speed 