# levels/shapes_level.py

import pygame
import random
import math

class ShapesLevel:
    def __init__(self, screen, game_globals, common_game_state):
        self.screen = screen
        self.game_globals = game_globals
        self.common_game_state = common_game_state
        
        self.pygame = game_globals['pygame']
        self.random = game_globals['random']
        self.math = game_globals['math']
        
        self.WIDTH = game_globals['WIDTH']
        self.HEIGHT = game_globals['HEIGHT']
        self.fonts = game_globals['fonts']
        self.particle_manager = game_globals['particle_manager_global']
        
        self.running = False
        self.sequence = [] # Shape names
        self.groups = [] # Should be only one group for shapes usually
        self.current_group_index = 0 # Should always be 0 for shapes as implemented
        self.current_group = []
        self.items_to_target = []
        self.target_item = None # Current shape name to target
        self.items_on_screen = [] # Holds shape objects to be drawn/interacted with
        self.items_spawned_in_group = 0
        self.items_destroyed_in_group = 0
        
        self.score = common_game_state.get("score", 0)
        self.overall_destroyed = common_game_state.get("overall_destroyed", 0)
        self.total_items_in_level = 0

        self.clock = self.pygame.time.Clock()
        self.FPS = self.game_globals.get("FPS", 60)
        self.stars = []

        # Shapes-specific state
        self.shapes_completed_flag_path = self.game_globals.get("LEVEL_PROGRESS_PATH", "level_progress.txt")
        self.shapes_already_completed_once = False # Read from file
        self.shapes_first_round_this_session = True # Tracks if shapes have rained down once this game instance for this level call
        self.just_completed_level_session = False # Set to true when a round of shapes is cleared

    def _read_shapes_progress(self):
        try:
            with open(self.shapes_completed_flag_path, "r") as f:
                progress = f.read().strip()
                if "shapes_completed" in progress:
                    self.shapes_already_completed_once = True
        except FileNotFoundError:
            self.shapes_already_completed_once = False # Assume not completed if file not found
        except Exception as e:
            print(f"Error reading shapes progress: {e}")
            self.shapes_already_completed_once = False

    def _write_shapes_progress(self):
        try:
            with open(self.shapes_completed_flag_path, "w") as f:
                f.write("shapes_completed\n") # Mark as completed
                # Potentially add other progress data here if needed
        except Exception as e:
            print(f"Error writing shapes progress: {e}")

    def initialize_level(self):
        """Initialize or reset the state for the Shapes level."""
        print("Shapes Level: Initializing...")
        self.running = True
        self._read_shapes_progress()
        self.shapes_first_round_this_session = True # Reset for this play-through of the level
        self.just_completed_level_session = False
        
        self.sequence = self.game_globals["SEQUENCES"].get("shapes", ["Rectangle", "Square", "Circle", "Triangle", "Pentagon"])
        self.total_items_in_level = len(self.sequence) # All shapes need to be targeted once per round
        self.GROUP_SIZE = len(self.sequence) # For shapes, the group is all shapes
        self.groups = [self.sequence] # Only one group containing all shapes
        
        self.current_group_index = 0 # Always 0 for shapes
        self.common_game_state["current_group_index"] = self.current_group_index
        self.score = 0
        self.common_game_state["score"] = self.score
        self.overall_destroyed = 0 
        self.common_game_state["overall_destroyed"] = self.overall_destroyed

        self.current_group = self.groups[0]
        self.items_to_target = self.current_group.copy()
        self.random.shuffle(self.items_to_target) # Shuffle the order of shapes to target
        
        if not self.items_to_target:
            self.running = False; return "ERROR"
            
        self.target_item = self.items_to_target[0]
        
        self.items_on_screen = []
        self.items_spawned_in_group = 0 # Counts how many unique shapes have been spawned this round
        self.items_destroyed_in_group = 0 # Counts how many targets hit this round

        self.stars = [[self.random.randint(0, self.WIDTH), self.random.randint(0, self.HEIGHT), self.random.randint(1,3), self.random.uniform(0.1,0.5)] for _ in range(100)]
        print(f"Shapes Level: Starting round. Target: {self.target_item}. Previously completed: {self.shapes_already_completed_once}")
        return None

    def run(self):
        """Main loop for the Shapes level."""
        init_status = self.initialize_level()
        if init_status: return init_status

        frame_count = 0
        while self.running:
            delta_time = self.clock.tick(self.FPS) / 1000.0

            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT: self.running = False; return "QUIT"
                if event.type == self.pygame.KEYDOWN and event.key == self.pygame.K_ESCAPE: self.running = False; return "LEVEL_MENU"
                status = self.handle_input(event)
                if status: return status

            self.update(delta_time, frame_count)
            self.draw()
            frame_count +=1

            # Check for round completion
            if self.just_completed_level_session:
                 self.shapes_first_round_this_session = False # Mark that the first round has passed
                 self._write_shapes_progress() # Mark shapes as completed in the file
                 self.shapes_already_completed_once = True
                 # The original game_loop had a `restart_level = True` mechanism for shapes checkpoint.
                 # For now, we can return a specific status that main_game_loop can interpret.
                 # Or, the checkpoint screen itself dictates continuation.
                 print("Shapes level round completed!")
                 # if self.game_globals['checkpoint_screen']("shapes"):
                 #    self.initialize_level() # Re-initialize for another round
                 #    self.just_completed_level_session = False # Reset this flag
                 # else:
                 #    return "LEVEL_MENU" # User chose to go to menu from checkpoint
                 return "CHECKPOINT_SHAPES" # Special status for shapes checkpoint

        self.cleanup()
        return "LEVEL_MENU"

    def handle_input(self, event):
        """Handle player input for the Shapes level."""
        if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            item_hit = None
            for item_obj in self.items_on_screen:
                if item_obj["rect"].collidepoint(mx, my):
                    item_hit = item_obj
                    break
            
            if item_hit:
                if item_hit["value"] == self.target_item: # Shape name matches
                    self.score += 10
                    self.overall_destroyed += 1
                    self.items_destroyed_in_group +=1
                    self.items_on_screen.remove(item_hit) # Remove the clicked correct shape
                    
                    self.particle_manager.create_explosion(item_hit["x"], item_hit["y"], 
                        color=self.random.choice(self.game_globals['FLAME_COLORS']))

                    if self.items_to_target: # If there are still shapes to target in the list
                        self.items_to_target.pop(0) 
                        if self.items_to_target:
                            self.target_item = self.items_to_target[0]
                        else: # All shapes in the current shuffled list have been targeted
                            self.target_item = None 
                            self.just_completed_level_session = True # Mark round as complete
                else: 
                    self.game_globals['handle_misclick'](mx,my)
            else: 
                self.game_globals['handle_misclick'](mx,my)
        return None

    def update(self, delta_time, frame_count):
        """Update game state for the Shapes level."""
        # Spawn all shapes at once if it's the first round and they haven't been spawned
        if self.shapes_first_round_this_session and self.items_spawned_in_group == 0 and len(self.items_on_screen) == 0:
            all_shapes_in_sequence = self.game_globals["SEQUENCES"].get("shapes", []) 
            for shape_name in all_shapes_in_sequence:
                # TODO: Create actual shape drawing logic, not just text
                font_to_use = self.fonts['TARGET_FONT'] 
                text_surface = font_to_use.render(shape_name, True, self.game_globals['WHITE'])
                text_rect = text_surface.get_rect()
                new_shape = {
                    "value": shape_name, # Shape name
                    "x": self.random.randint(50, self.WIDTH - 50),
                    "y": self.random.randint(50, self.HEIGHT - 150),
                    "dx": self.random.uniform(-0.5, 0.5) * 60,
                    "dy": self.random.uniform(-0.5, 0.5) * 60,
                    "surface": text_surface, # Placeholder: should be a drawn shape
                    "rect": text_rect, # Collision rect
                    "type": "shape" # To differentiate from text items if needed
                }
                new_shape["rect"].center = (new_shape["x"], new_shape["y"])
                self.items_on_screen.append(new_shape)
            self.items_spawned_in_group = len(all_shapes_in_sequence) # All spawned
            # self.shapes_first_round_this_session = False # Mark that initial spawn happened - moved to after completion

        # Move items
        for item_obj in self.items_on_screen:
            item_obj["x"] += item_obj["dx"] * delta_time
            item_obj["y"] += item_obj["dy"] * delta_time
            if item_obj["x"] - item_obj["rect"].width/2 < 0 or item_obj["x"] + item_obj["rect"].width/2 > self.WIDTH:
                item_obj["dx"] *= -1
            if item_obj["y"] - item_obj["rect"].height/2 < 0 or item_obj["y"] + item_obj["rect"].height/2 > self.HEIGHT - 100:
                item_obj["dy"] *= -1
            item_obj["rect"].center = (item_obj["x"], item_obj["y"])
        
        for star in self.stars: star[2] = self.random.randint(1, 3); star[1] += star[3]; 
        if star[1] > self.HEIGHT: star[1] = 0; star[0] = self.random.randint(0, self.WIDTH)
        self.particle_manager.update(delta_time)

    def draw(self):
        """Draw all elements for the Shapes level."""
        self.screen.fill(self.game_globals['BLACK'])
        for star in self.stars: self.pygame.draw.circle(self.screen, self.game_globals['WHITE'], (int(star[0]), int(star[1])), star[2])
        
        for item_obj in self.items_on_screen:
            # TODO: Actual shape drawing logic based on item_obj["value"]
            # For now, it will blit the text surface created in update()
            self.screen.blit(item_obj["surface"], item_obj["rect"])
            
        self.particle_manager.draw(self.screen)
        self.game_globals['display_info'](self.score, "N/A", self.target_item, self.overall_destroyed, self.total_items_in_level, "shapes")
        if 'draw_cracks' in self.game_globals: self.game_globals['draw_cracks'](self.screen)
        self.pygame.display.flip()

    def cleanup(self):
        print("Shapes Level: Cleaning up..."); self.items_on_screen = []

def start_shapes_level_instance(screen, game_globals, common_game_state):
    level = ShapesLevel(screen, game_globals, common_game_state)
    return level.run() 