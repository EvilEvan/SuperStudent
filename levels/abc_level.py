# levels/alphabet_level.py

import pygame
import random
import math

# TODO: Import necessary settings, utils, and other modules from the parent directory if needed
# Example: from ..settings import YOUR_SETTING

class AlphabetLevel:
    def __init__(self, screen, game_globals, common_game_state):
        self.screen = screen
        self.game_globals = game_globals
        self.common_game_state = common_game_state # Contains score, player_data etc.
        
        self.pygame = game_globals['pygame']
        self.random = game_globals['random']
        self.math = game_globals['math']
        
        self.WIDTH = game_globals['WIDTH']
        self.HEIGHT = game_globals['HEIGHT']
        self.fonts = game_globals['fonts']
        self.particle_manager = game_globals['particle_manager_global'] # Use the global one passed
        
        # Level-specific state
        self.running = False
        self.sequence = []
        self.groups = []
        self.current_group_index = 0
        self.current_group = []
        self.letters_to_target = []
        self.target_letter = None
        self.letters_on_screen = [] # Stores letter objects
        self.letters_spawned_in_group = 0
        self.letters_destroyed_in_group = 0
        
        self.score = common_game_state.get("score", 0)
        self.overall_destroyed = common_game_state.get("overall_destroyed", 0)
        self.total_items_in_level = 0

        self.clock = self.pygame.time.Clock()
        self.FPS = self.game_globals.get("FPS", 60) # Get FPS from globals or default

        # Placeholder for other necessary initializations
        self.stars = [] # Background stars
        self.player_x = self.common_game_state.get("player_data", {}).get("player_x", self.WIDTH // 2)
        self.player_y = self.common_game_state.get("player_data", {}).get("player_y", self.HEIGHT // 2)
        
        # Effects and UI elements specific to this level can be initialized here
        # For example, if there are unique particle effects or UI components

    def initialize_level(self):
        """Initialize or reset the state for the alphabet level."""
        print("Alphabet Level: Initializing...")
        self.running = True
        
        self.sequence = self.game_globals["SEQUENCES"].get("alphabet", list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
        self.total_items_in_level = len(self.sequence)
        self.GROUP_SIZE = self.game_globals["GROUP_SIZE"]
        self.groups = [self.sequence[i:i+self.GROUP_SIZE] for i in range(0, len(self.sequence), self.GROUP_SIZE)]
        
        self.current_group_index = self.common_game_state.get("current_group_index", 0)
        if self.current_group_index >= len(self.groups):
            print("Alphabet Level: All groups completed or invalid group index.")
            # Handle level completion or error
            self.running = False 
            return "WELL_DONE" # Or LEVEL_MENU

        self.current_group = self.groups[self.current_group_index]
        self.letters_to_target = self.current_group.copy()
        if not self.letters_to_target:
            print("Alphabet Level: Current group is empty.")
            self.running = False
            return "ERROR" # Or proceed to next group/level
            
        self.target_letter = self.letters_to_target[0]
        
        self.letters_on_screen = []
        self.letters_spawned_in_group = 0
        self.letters_destroyed_in_group = 0
        
        # Reset score if it's not meant to persist across levels or game modes
        # self.score = 0 
        # self.overall_destroyed = 0 # This might track total across all groups

        # Initialize background stars (example from SuperStudent_fixed.py)
        self.stars = []
        for _ in range(100):
            x = self.random.randint(0, self.WIDTH)
            y = self.random.randint(0, self.HEIGHT)
            radius = self.random.randint(1, 3) # Smaller stars
            self.stars.append([x, y, radius, self.random.uniform(0.1, 0.5)]) # Added speed for twinkling

        # TODO: Initialize other level-specific variables from the old game_loop related to alphabet mode
        print(f"Alphabet Level: Starting group {self.current_group_index + 1}/{len(self.groups)}. Target: {self.target_letter}")
        return None # Indicates successful initialization

    def run(self):
        """Main loop for the alphabet level."""
        init_status = self.initialize_level()
        if init_status: # e.g. "WELL_DONE" or "ERROR"
             return init_status # Return to main game manager

        frame_count = 0 # For letter spawning interval

        while self.running:
            delta_time = self.clock.tick(self.FPS) / 1000.0 # Delta time in seconds

            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    self.running = False
                    return "QUIT"
                if event.type == self.pygame.KEYDOWN and event.key == self.pygame.K_ESCAPE:
                    self.running = False
                    return "LEVEL_MENU" # Request to go back to level menu
                
                status = self.handle_input(event)
                if status: return status # e.g. CHECKPOINT, GAME_OVER

            self.update(delta_time, frame_count)
            self.draw()
            
            frame_count +=1

            # Check for level completion or other state changes
            if self.current_group_index >= len(self.groups) and not self.letters_on_screen and not self.letters_to_target:
                 print("Alphabet level fully completed!")
                 # self.game_globals['well_done_screen'](self.score) # Call global well_done_screen
                 return "WELL_DONE"


        self.cleanup()
        return "LEVEL_MENU" # Default return when loop exits normally (e.g. via ESC)

    def handle_input(self, event):
        """Handle player input for the alphabet level."""
        if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            letter_hit = None
            for letter_obj in self.letters_on_screen:
                if letter_obj["rect"].collidepoint(mx, my):
                    letter_hit = letter_obj
                    break
            
            if letter_hit:
                if letter_hit["value"] == self.target_letter:
                    self.score += 10
                    self.overall_destroyed += 1
                    self.letters_destroyed_in_group +=1
                    self.letters_on_screen.remove(letter_hit)
                    
                    self.game_globals['particle_manager'].create_explosion( # Using passed particle_manager
                        letter_hit["x"], letter_hit["y"], 
                        color=self.random.choice(self.game_globals['FLAME_COLORS']),
                        max_radius=60, duration=15
                    )

                    if self.letters_to_target:
                        self.letters_to_target.pop(0) # Remove current target
                        if self.letters_to_target:
                            self.target_letter = self.letters_to_target[0]
                        else: # Group cleared
                            self.target_letter = None 
                            if self.current_group_index < len(self.groups) -1:
                                # Checkpoint or transition to next group
                                if self.overall_destroyed % self.game_globals.get("CHECKPOINT_TRIGGER", 10) == 0:
                                     # Call global checkpoint_screen
                                     # continue_game = self.game_globals['checkpoint_screen']("alphabet")
                                     # if not continue_game: return "LEVEL_MENU"
                                     pass # Handled by main game loop or main.py
                                # self.go_to_next_group() # This logic will be in update()
                                pass
                            else: # All groups completed
                                 # self.game_globals['well_done_screen'](self.score)
                                 # self.running = False # Signal loop to end
                                 pass # Handled by main run loop condition
                else: # Hit wrong letter
                    self.game_globals['handle_misclick'](mx,my) # Use global misclick handler
                    # Potentially add game over condition from handle_misclick return
            else: # Clicked on empty space
                self.game_globals['handle_misclick'](mx,my)
        return None


    def update(self, delta_time, frame_count):
        """Update game state for the alphabet level."""
        # Spawn new letters from the current group
        LETTER_SPAWN_INTERVAL = self.game_globals.get("LETTER_SPAWN_INTERVAL", 30)
        if self.letters_spawned_in_group < len(self.current_group) and frame_count % LETTER_SPAWN_INTERVAL == 0:
            letter_value = self.current_group[self.letters_spawned_in_group]
            
            # Determine font and size (example)
            font_to_use = self.fonts['TARGET_FONT']
            text_surface = font_to_use.render(letter_value, True, self.game_globals['WHITE'])
            text_rect = text_surface.get_rect()
            
            new_letter = {
                "value": letter_value,
                "x": self.random.randint(50, self.WIDTH - 50),
                "y": self.random.randint(50, self.HEIGHT - 150), # Keep away from bottom HUD
                "dx": self.random.uniform(-1, 1) * 60, # pixels per second
                "dy": self.random.uniform(-1, 1) * 60, # pixels per second
                "surface": text_surface,
                "rect": text_rect,
                "font_size_key": "target" # For potential dynamic resizing
            }
            new_letter["rect"].topleft = (new_letter["x"], new_letter["y"])
            self.letters_on_screen.append(new_letter)
            self.letters_spawned_in_group += 1

        # Move letters
        for letter_obj in self.letters_on_screen:
            letter_obj["x"] += letter_obj["dx"] * delta_time
            letter_obj["y"] += letter_obj["dy"] * delta_time
            
            # Wall bounce
            if letter_obj["x"] < 0 or letter_obj["x"] + letter_obj["rect"].width > self.WIDTH:
                letter_obj["dx"] *= -1
            if letter_obj["y"] < 0 or letter_obj["y"] + letter_obj["rect"].height > self.HEIGHT - 100: # Avoid HUD
                letter_obj["dy"] *= -1
            
            letter_obj["rect"].topleft = (letter_obj["x"], letter_obj["y"])

        # Check if group is completed (all targets destroyed and all spawned items gone)
        if not self.letters_to_target and not self.letters_on_screen and self.letters_spawned_in_group >= len(self.current_group) :
            if self.current_group_index < len(self.groups) - 1:
                self.current_group_index += 1
                self.common_game_state["current_group_index"] = self.current_group_index # Update shared state
                # Reset for next group
                self.current_group = self.groups[self.current_group_index]
                self.letters_to_target = self.current_group.copy()
                self.target_letter = self.letters_to_target[0] if self.letters_to_target else None
                self.letters_spawned_in_group = 0
                self.letters_destroyed_in_group = 0
                print(f"Alphabet Level: Moving to group {self.current_group_index + 1}. Target: {self.target_letter}")
            else: # All groups done
                # This condition is also checked in run(), could consolidate
                self.running = False # Signal to stop the level loop

        # Update background stars (twinkling)
        for star in self.stars:
            star[2] = self.random.randint(1, 3) # Change size for twinkle
            star[1] += star[3] # Slow drift downwards
            if star[1] > self.HEIGHT:
                star[1] = 0
                star[0] = self.random.randint(0, self.WIDTH)
                
        # Update particle manager
        self.particle_manager.update(delta_time)


    def draw(self):
        """Draw all elements for the alphabet level."""
        self.screen.fill(self.game_globals['BLACK']) # Or current_background from game_globals

        # Draw stars
        for star in self.stars:
            self.pygame.draw.circle(self.screen, self.game_globals['WHITE'], (int(star[0]), int(star[1])), star[2])

        # Draw letters
        for letter_obj in self.letters_on_screen:
            self.screen.blit(letter_obj["surface"], letter_obj["rect"])
            
        # Draw particle effects
        self.particle_manager.draw(self.screen)

        # Draw HUD using the global display_info function
        current_ability = "N/A" # Alphabet level might not use abilities from the original list
        self.game_globals['display_info'](
            self.score, 
            current_ability, 
            self.target_letter, 
            self.overall_destroyed, 
            self.total_items_in_level, 
            "alphabet"
        )
        
        # Draw cracks if that system is global and managed outside
        if 'draw_cracks' in self.game_globals:
            self.game_globals['draw_cracks'](self.screen)


        self.pygame.display.flip()

    def cleanup(self):
        """Clean up resources used by the alphabet level."""
        print("Alphabet Level: Cleaning up...")
        self.letters_on_screen = []
        # Any other specific cleanup for this level

# This function will be called by the LEVEL_DISPATCHER
# It creates an instance of the level and runs it.
def start_alphabet_level_instance(screen, game_globals, common_game_state):
    level = AlphabetLevel(screen, game_globals, common_game_state)
    return level.run() 