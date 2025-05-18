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
    DOT_RADIUS, DOT_CLICK_RADIUS, DOT_SPEED_RANGE, DOT_SPEED_REDUCTION,
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
        """Handle pygame events specific to this level.
        
        Returns:
            New game state string if level should exit, None to continue
        """
        if event.type == pygame.QUIT:
            return "QUIT"
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "LEVEL_MENU"
            
        # Handle state-specific events
        if self.dots_state == DotsState.WAITING_FOR_CLICK:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Start dispersion animation
                self.dots_state = DotsState.DISPERSION
                self.state_timer = DISPERSE_FRAMES
                self._initialize_dispersion()
                return None
                
        elif self.dots_state == DotsState.GAMEPLAY:
            # Handle clicking on dots during gameplay
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                hit_target = False
                
                # Check if any dot was hit
                for dot in self.dots:
                    if dot["alive"]:
                        dist = math.hypot(mx - dot["x"], my - dot["y"])
                        if dist <= DOT_CLICK_RADIUS:  # Use larger non-visible click radius
                            hit_target = True
                            if dot["target"]:
                                result = self._handle_target_hit(dot)
                                if result == "CHECKPOINT":
                                    # Store current state before checkpoint
                                    dots_before_checkpoint = self.target_dots_left
                                    
                                    # Trigger checkpoint screen
                                    return "CHECKPOINT"
                            break
                
                # Add crack on misclick
                if not hit_target:
                    if self.effects.create_crack(mx, my):
                        # Returns True if max cracks reached, trigger shatter
                        self.effects.shatter_screen()
                        return "GAME_OVER"
            
            # Handle touch events (for mobile/tablet)
            elif event.type == pygame.FINGERDOWN:
                # Convert touch coordinates to screen coordinates
                touch_x = event.x * self.width
                touch_y = event.y * self.height
                hit_target = False
                
                # Check if any dot was hit
                for dot in self.dots:
                    if dot["alive"]:
                        dist = math.hypot(touch_x - dot["x"], touch_y - dot["y"])
                        if dist <= DOT_CLICK_RADIUS:  # Use larger non-visible click radius
                            hit_target = True
                            if dot["target"]:
                                result = self._handle_target_hit(dot)
                                if result == "CHECKPOINT":
                                    # Store current state before checkpoint
                                    dots_before_checkpoint = self.target_dots_left
                                    
                                    # Trigger checkpoint screen
                                    return "CHECKPOINT"
                            break
                
                # Add crack on mistouch
                if not hit_target:
                    if self.effects.create_crack(touch_x, touch_y):
                        # Returns True if max cracks reached, trigger shatter
                        self.effects.shatter_screen()
                        return "GAME_OVER"
                        
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
        """Initialize bouncing dots based on disperse particles."""
        self.dots = []
        
        # Store initial positions temporarily to check spacing
        initial_positions = []
        min_spacing = 48  # Minimum space between dot centers (2x radius)
        
        # First calculate initial positions from disperse particles
        for p in self.disperse_particles:
            x = int(self.center[0] + math.cos(p["angle"]) * p["radius"])
            y = int(self.center[1] + math.sin(p["angle"]) * p["radius"])
            
            # Add some random offset to prevent dots from being perfectly aligned
            x += random.randint(-20, 20)
            y += random.randint(-20, 20)
            
            # Ensure positions stay within screen bounds
            x = max(DOT_RADIUS, min(self.width - DOT_RADIUS, x))
            y = max(DOT_RADIUS, min(self.height - DOT_RADIUS, y))
            
            initial_positions.append((x, y, p["color"]))
        
        # Create dots with proper spacing
        for i, (x, y, color) in enumerate(initial_positions):
            # Check spacing with existing dots
            valid_position = True
            max_attempts = 10
            
            for attempt in range(max_attempts):
                valid_position = True
                
                # Check distance to all dots already created
                for existing_dot in self.dots:
                    dist = math.hypot(x - existing_dot["x"], y - existing_dot["y"])
                    if dist < min_spacing:
                        valid_position = False
                        # Move position slightly for next attempt
                        angle = random.uniform(0, math.pi * 2)
                        x += math.cos(angle) * 10
                        y += math.sin(angle) * 10
                        # Keep in bounds
                        x = max(DOT_RADIUS, min(self.width - DOT_RADIUS, x))
                        y = max(DOT_RADIUS, min(self.height - DOT_RADIUS, y))
                        break
                
                if valid_position:
                    break
            
            # Get velocity components scaled appropriately for delta time
            # These will be multiplied by delta_time in the update method
            min_speed, max_speed = DOT_SPEED_RANGE
            dx = random.uniform(min_speed, max_speed)
            dy = random.uniform(min_speed, max_speed)
            
            # Randomly flip direction
            if random.random() < 0.5:
                dx = -dx
            if random.random() < 0.5:
                dy = -dy
                
            # Create the dot
            self.dots.append({
                "x": x,
                "y": y,
                "dx": dx,
                "dy": dy,
                "color": color,
                "radius": DOT_RADIUS,
                "target": color == self.mother_color,
                "alive": True
            })
        
        # Count target dots
        self.target_dots_left = sum(1 for d in self.dots if d["target"] and d["alive"])
        print(f"Colors Level: {len(self.dots)} dots initialized, {self.target_dots_left} targets")
        
    def _select_target_color(self):
        """Select the next target color, ensuring all colors are used before repeating."""
        # Get available colors (those not yet used in the current cycle)
        available_colors = [i for i in range(len(COLORS_LIST)) if i not in self.used_colors]
        
        # If all colors have been used, reset tracking but keep the current color as used
        # to avoid immediate repetition of the same color
        if not available_colors:
            # Keep current color as used to avoid immediate repetition
            self.used_colors = [self.color_idx] if hasattr(self, 'color_idx') else []
            available_colors = [i for i in range(len(COLORS_LIST)) if i not in self.used_colors]
        
        # If we still have no available colors (should be impossible), just pick randomly
        if not available_colors:
            self.color_idx = random.randint(0, len(COLORS_LIST) - 1)
        else:
            # Select a random color from available colors
            self.color_idx = random.choice(available_colors)
            
        # Mark this color as used
        if self.color_idx not in self.used_colors:
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
                
            # Update position with delta time scaling for consistent speed regardless of frame rate
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
                
            # Add to spatial grid for collision detection - optimized to only add to current cell
            if ENABLE_COLLISION_GRID:
                grid_x = int(dot["x"] / self.grid_cell_size)
                grid_y = int(dot["y"] / self.grid_cell_size)
                cell_key = (grid_x, grid_y)
                if cell_key not in self.grid:
                    self.grid[cell_key] = []
                self.grid[cell_key].append(dot)
        
        # Only check for collisions if they are enabled (after first color change)
        if not self.collision_enabled:
            return
            
        # Debuggable collision counter to verify collisions are actually happening
        collision_count = 0
        
        # Handle collisions using spatial partitioning - optimized to check only neighboring cells
        if ENABLE_COLLISION_GRID:
            # Process each cell 
            for (gx, gy), dots_in_cell in self.grid.items():
                # Check collisions within this cell (all pairs)
                for i, dot1 in enumerate(dots_in_cell):
                    if not dot1["alive"]:
                        continue
                        
                    # First check collisions within same cell
                    for j in range(i+1, len(dots_in_cell)):
                        dot2 = dots_in_cell[j]
                        if not dot2["alive"]:
                            continue
                            
                        # Check collision
                        if self._check_collision(dot1, dot2):
                            collision_count += 1
                    
                    # Then check with neighboring cells - but only in "forward" direction to avoid duplicate checks
                    # This creates a pattern where we only check 4 of the 8 neighbors:
                    # [ ][↘][ ]
                    # [ ][C ][→]
                    # [ ][ ][ ]
                    # Where C is the current cell
                    neighbors = [
                        (gx+1, gy),   # right
                        (gx+1, gy+1), # bottom-right
                        (gx, gy+1),   # bottom
                        (gx-1, gy+1)  # bottom-left
                    ]
                    
                    for nx, ny in neighbors:
                        neighbor_key = (nx, ny)
                        if neighbor_key in self.grid:
                            for dot2 in self.grid[neighbor_key]:
                                if not dot2["alive"]:
                                    continue
                                
                                # Check collision
                                if self._check_collision(dot1, dot2):
                                    collision_count += 1
        else:
            # Fallback to O(n²) collision detection if grid is disabled
            for i, dot1 in enumerate(self.dots):
                if not dot1["alive"]:
                    continue
                    
                for j, dot2 in enumerate(self.dots[i+1:], i+1):
                    if not dot2["alive"]:
                        continue
                        
                    if self._check_collision(dot1, dot2):
                        collision_count += 1
        
        # Log collision count occasionally
        if collision_count > 0 and random.random() < 0.1:
            print(f"Colors Level: {collision_count} collisions detected this frame")
        
    def _apply_center_avoidance(self, dot):
        """Apply center avoidance force to prevent dots from clustering in the center."""
        # Calculate distance from center
        dx = dot["x"] - self.width // 2
        dy = dot["y"] - self.height // 2
        distance = math.hypot(dx, dy)
        
        # Only apply if dot is close to center
        center_avoidance_radius = 150  # Distance from center where avoidance starts
        if distance < center_avoidance_radius:
            # Normalize vector away from center
            if distance > 0:  # Avoid division by zero
                nx = dx / distance
                ny = dy / distance
            else:
                # If exactly at center (shouldn't happen often), use random direction
                angle = random.uniform(0, math.pi * 2)
                nx = math.cos(angle)
                ny = math.sin(angle)
            
            # Apply stronger force the closer to center (inverse proportion to distance)
            # Use a curve that increases rapidly as we get very close to center
            # Goes from 0 at edge of avoidance radius to 1 at center
            force_magnitude = 1 - (distance / center_avoidance_radius)
            
            # Square the magnitude to make it increase faster near the center
            force_magnitude = force_magnitude * force_magnitude
            
            # Scale the maximum force (adjust this value as needed)
            max_force = 0.5  # Maximum velocity adjustment per frame
            
            # Apply to velocity
            dot["dx"] += nx * force_magnitude * max_force
            dot["dy"] += ny * force_magnitude * max_force
            
            # Ensure the dot isn't moving too slowly, which could cause it to get stuck
            min_speed = 1.0  # Minimum speed to maintain
            current_speed = math.hypot(dot["dx"], dot["dy"])
            if current_speed < min_speed:
                # Scale up speed while maintaining direction
                speed_ratio = min_speed / max(0.1, current_speed)  # Avoid division by 0
                dot["dx"] *= speed_ratio
                dot["dy"] *= speed_ratio

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
                # Separate dots to prevent sticking - scale separation force by how close they are
                overlap = (dot1["radius"] + dot2["radius"]) - distance
                separation_factor = 1.0
                
                # Make separation more aggressive for zero or near-zero distances
                if distance < 5:
                    # Apply additional separation force based on closeness
                    separation_factor = 2.0 + (5 - distance) * 0.5  # More separation for closer dots
                    
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
                
                # Apply separation forces
                dot1["x"] += overlap/2 * nx * separation_factor
                dot1["y"] += overlap/2 * ny * separation_factor
                dot2["x"] -= overlap/2 * nx * separation_factor
                dot2["y"] -= overlap/2 * ny * separation_factor
                
                # Add a small random component to velocities to prevent dots from getting stuck
                dot1["dx"] += random.uniform(-0.1, 0.1)
                dot1["dy"] += random.uniform(-0.1, 0.1)
                dot2["dx"] += random.uniform(-0.1, 0.1)
                dot2["dy"] += random.uniform(-0.1, 0.1)
                
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
        """Generate new dots after all targets have been cleared."""
        # Select a new target color
        self._switch_target_color()
        
        # Set target count for new generation
        new_dots_count = 10
        target_dots_needed = new_dots_count
        
        # Remove any dead dots from the list
        self.dots = [d for d in self.dots if d["alive"]]
        
        # Count how many target dots we already have (dots with the current target color)
        existing_target_dots = sum(1 for d in self.dots if d["color"] == self.mother_color)
        target_dots_needed = max(0, new_dots_count - existing_target_dots)
        
        # Calculate how many new dots we need to create (aiming for 100 total alive dots)
        alive_dots = len(self.dots)
        desired_total = 100
        new_dots_needed = max(0, desired_total - alive_dots)
        
        # Create the new dots - first ensure we have enough target dots
        self._create_new_dots(
            total_dots=new_dots_needed,
            target_dots=target_dots_needed
        )
        
        # Reset collision if needed
        if not self.collision_enabled:
            print("Colors Level: Note - collisions are still disabled until first color change")
        
        # Update target count
        self.target_dots_left = sum(1 for d in self.dots if d["target"] and d["alive"])
        print(f"Colors Level: Generated new dots. Now have {len(self.dots)} dots with {self.target_dots_left} targets")
        
        # Create a ghost notification to remind of the current target color
        self.ghost_notification = {
            "color": self.mother_color,
            "duration": 100,
            "alpha": 255,
            "radius": 150,
            "text": self.mother_color_name
        }
        
    def _create_new_dots(self, total_dots, target_dots):
        """Create new dots, ensuring proper spacing and target allocation."""
        # Limit target_dots to total_dots
        target_dots = min(target_dots, total_dots)
        
        # Track how many of each we've created
        targets_created = 0
        distractors_created = 0
        
        # Calculate minimum spacing between dots
        min_spacing = DOT_RADIUS * 2.5  # A bit more than 2x radius to avoid immediate collisions
        
        for i in range(total_dots):
            # Try to find a position that doesn't overlap with existing dots
            max_attempts = 20  # Limit attempts to prevent infinite loops
            valid_position = False
            x, y = 0, 0
            
            for _ in range(max_attempts):
                # Pick a position away from the center
                center_x = self.width // 2
                center_y = self.height // 2
                
                # Use polar coordinates to ensure more even distribution
                distance = random.uniform(150, min(self.width, self.height) / 2 - 50)
                angle = random.uniform(0, math.pi * 2)
                
                # Convert to cartesian coordinates
                x = center_x + math.cos(angle) * distance
                y = center_y + math.sin(angle) * distance
                
                # Add some random jitter
                x += random.uniform(-20, 20)
                y += random.uniform(-20, 20)
                
                # Ensure within screen bounds
                x = max(DOT_RADIUS + 10, min(self.width - DOT_RADIUS - 10, x))
                y = max(DOT_RADIUS + 10, min(self.height - DOT_RADIUS - 10, y))
                
                # Check distance from all existing dots
                valid_position = True
                for existing_dot in self.dots:
                    distance = math.hypot(x - existing_dot["x"], y - existing_dot["y"])
                    if distance < min_spacing:
                        valid_position = False
                        break
                        
                if valid_position:
                    break
            
            # Generate velocity components scaled appropriately for delta time
            # These will be multiplied by delta_time in the update method
            min_speed, max_speed = DOT_SPEED_RANGE
            dx = random.uniform(min_speed, max_speed)
            dy = random.uniform(min_speed, max_speed)
            
            # Randomly flip direction
            if random.random() < 0.5:
                dx = -dx
            if random.random() < 0.5:
                dy = -dy
            
            # Determine if this dot is a target or distractor
            is_target = (targets_created < target_dots)
            
            # Set color based on target status
            if is_target:
                color = self.mother_color
                targets_created += 1
            else:
                # Choose random distractor color
                distractor_colors = [c for idx, c in enumerate(COLORS_LIST) if idx != self.color_idx]
                color = random.choice(distractor_colors)
                distractors_created += 1
            
            # Add the new dot
            self.dots.append({
                "x": x, "y": y,
                "dx": dx, "dy": dy,
                "color": color,
                "radius": DOT_RADIUS,
                "target": is_target,
                "alive": True,
            })
        
        print(f"Colors Level: Created {targets_created} targets and {distractors_created} distractors")
        
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
        """Draw HUD elements including score and target indicators."""
        # Display score
        score_text = self.small_font.render(f"Score: {self.overall_destroyed * 10}", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))
        
        # Display target count
        target_text = self.small_font.render(f"Targets: {self.target_dots_left}", True, (255, 255, 255))
        screen.blit(target_text, (20, 60))
        
        # Display current target color reference with improved accessibility
        # Draw target dot
        pygame.draw.circle(screen, self.mother_color, (self.width - 60, 60), DOT_RADIUS)
        
        # Add target label
        target_label = self.small_font.render("TARGET", True, (255, 255, 255))
        target_label_rect = target_label.get_rect(center=(self.width - 60, 30))
        screen.blit(target_label, target_label_rect)
        
        # Add color name for colorblind accessibility
        color_name = self.small_font.render(self.mother_color_name, True, (255, 255, 255))
        color_name_rect = color_name.get_rect(center=(self.width - 60, 100))
        screen.blit(color_name, color_name_rect)
        
        # Add outline rectangle
        pygame.draw.rect(screen, (255, 255, 255), (self.width - 110, 20, 100, 90), 2)
        
        # If collisions aren't enabled yet, show countdown
        if not self.collision_enabled:
            collision_text = self.small_font.render(
                "Collisions enabled after first color change", 
                True, 
                (255, 255, 0)
            )
            screen.blit(collision_text, (self.width // 2 - collision_text.get_width() // 2, self.height - 40))
        
    def _check_center_clusters(self):
        """Check for dots clustered in the center and move them if necessary."""
        center_x = self.width // 2
        center_y = self.height // 2
        center_radius = 100  # Area to check for clusters
        
        # Only run this check occasionally (every 30 frames or so)
        if random.random() < 0.033:  # ~1/30 chance each frame
            # Count dots in center
            dots_in_center = []
            for dot in self.dots:
                if dot["alive"]:
                    dist = math.hypot(dot["x"] - center_x, dot["y"] - center_y)
                    if dist < center_radius:
                        dots_in_center.append(dot)
            
            # If we have too many dots in center, try to break them up
            if len(dots_in_center) > 5:  # Threshold for intervention
                print(f"Colors Level: {len(dots_in_center)} dots detected in center - applying dispersal")
                
                # Apply stronger dispersal to all dots in center
                for dot in dots_in_center:
                    # Calculate direction away from center
                    dx = dot["x"] - center_x
                    dy = dot["y"] - center_y
                    distance = math.hypot(dx, dy)
                    
                    # Apply a strong outward force
                    if distance > 0:
                        nx = dx / distance
                        ny = dy / distance
                    else:
                        # Random direction if exactly at center
                        angle = random.uniform(0, math.pi * 2)
                        nx = math.cos(angle)
                        ny = math.sin(angle)
                    
                    # Apply strong impulse
                    impulse = random.uniform(5, 10)  # Strong push
                    dot["dx"] = nx * impulse
                    dot["dy"] = ny * impulse
                    
                    # Also physically move the dot a bit to help break any exact overlaps
                    dot["x"] += nx * random.uniform(5, 15)
                    dot["y"] += ny * random.uniform(5, 15) 

    def resume_from_checkpoint(self):
        """Resume level after returning from checkpoint screen."""
        # Show a ghost notification to remind of the current target color
        self.ghost_notification = {
            "color": self.mother_color,
            "duration": 100,
            "alpha": 255,
            "radius": 150,
            "text": self.mother_color_name
        }
        
        # Make sure collision state is preserved (should be enabled after first color change)
        if self.color_changed and not self.collision_enabled:
            self.collision_enabled = True
            print("Colors Level: Restoring collision state to enabled after checkpoint")
            
        # Count current targets to ensure state is consistent
        self.target_dots_left = sum(1 for d in self.dots if d["target"] and d["alive"])
        print(f"Colors Level: Resuming from checkpoint with {self.target_dots_left} targets remaining") 

def start_colors_level_instance(screen, game_globals, common_game_state):
    """Wrapper to instantiate and run the ColorsLevel."""
    pygame_instance = game_globals['pygame']
    clock = pygame_instance.time.Clock()
    FPS = game_globals.get("FPS", 60)

    width = game_globals['WIDTH']
    height = game_globals['HEIGHT']
    resource_manager = game_globals['resource_manager']
    particle_system = game_globals['particle_manager_global'] # ColorsLevel expects this name
    effects = game_globals['effects_manager']

    level_instance = ColorsLevel(width, height, resource_manager, particle_system, effects)
    
    if not level_instance.initialize():
        print("Error: ColorsLevel failed to initialize.")
        return "ERROR" # Or LEVEL_MENU

    running = True
    level_status = None
    last_status_from_handler = None

    while running:
        delta_time = clock.tick(FPS) / 1000.0

        for event in pygame_instance.event.get():
            status = level_instance.handle_event(event)
            if status:
                last_status_from_handler = status
                if status in ["QUIT", "LEVEL_MENU", "CHECKPOINT", "GAME_OVER"]:
                    running = False
                    level_status = status
                    break
        if not running: break

        if not level_instance.update(delta_time):
            # According to ColorsLevel.update, it always returns True.
            # If it were to return False, it might mean an internal stop condition.
            print("ColorsLevel.update returned False. Exiting level.")
            running = False
            level_status = "LEVEL_MENU" # Default exit status
            break
        
        level_instance.draw(screen)
        # pygame.display.flip() is called within level_instance.draw()

    level_instance.cleanup()
    
    # Prioritize status from event handler if it caused exit
    final_status = level_status if level_status else last_status_from_handler
    return final_status if final_status else "LEVEL_MENU" # Default if no specific exit