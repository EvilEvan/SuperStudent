# levels/clcase_level.py

import pygame
import random
import math

class CLCaseLevel: # Case/Lowercase Level
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
        self.sequence = []
        self.groups = []
        self.current_group_index = 0
        self.current_group = []
        self.items_to_target = []
        self.target_item = None
        self.target_display_item = None # For showing uppercase target
        self.items_on_screen = [] 
        self.items_spawned_in_group = 0
        self.items_destroyed_in_group = 0
        
        self.score = common_game_state.get("score", 0)
        self.overall_destroyed = common_game_state.get("overall_destroyed", 0)
        self.total_items_in_level = 0

        self.clock = self.pygame.time.Clock()
        self.FPS = self.game_globals.get("FPS", 60)
        self.stars = []

    def initialize_level(self):
        """Initialize or reset the state for the C/L Case level."""
        print("C/L Case Level: Initializing...")
        self.running = True
        
        self.sequence = self.game_globals["SEQUENCES"].get("clcase", list("abcdefghijklmnopqrstuvwxyz"))
        self.total_items_in_level = len(self.sequence)
        self.GROUP_SIZE = self.game_globals["GROUP_SIZE"]
        self.groups = [self.sequence[i:i+self.GROUP_SIZE] for i in range(0, len(self.sequence), self.GROUP_SIZE)]
        
        self.current_group_index = self.common_game_state.get("current_group_index", 0)
        self.common_game_state["current_group_index"] = self.current_group_index
        self.score = 0
        self.common_game_state["score"] = self.score
        self.overall_destroyed = 0
        self.common_game_state["overall_destroyed"] = self.overall_destroyed

        if self.current_group_index >= len(self.groups):
            self.running = False 
            return "WELL_DONE"

        self.current_group = self.groups[self.current_group_index]
        self.items_to_target = self.current_group.copy()
        if not self.items_to_target:
            self.running = False
            return "ERROR"
            
        self.target_item = self.items_to_target[0]
        self.target_display_item = self.target_item.upper() # Show target as uppercase
        
        self.items_on_screen = []
        self.items_spawned_in_group = 0
        self.items_destroyed_in_group = 0

        self.stars = []
        for _ in range(100):
            x = self.random.randint(0, self.WIDTH)
            y = self.random.randint(0, self.HEIGHT)
            radius = self.random.randint(1, 3)
            self.stars.append([x, y, radius, self.random.uniform(0.1, 0.5)]) 

        print(f"C/L Case Level: Group {self.current_group_index + 1}/{len(self.groups)}. Target: {self.target_display_item} (match {self.target_item})")
        return None

    def run(self):
        """Main loop for the C/L Case level."""
        init_status = self.initialize_level()
        if init_status: return init_status

        frame_count = 0
        while self.running:
            delta_time = self.clock.tick(self.FPS) / 1000.0

            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    self.running = False; return "QUIT"
                if event.type == self.pygame.KEYDOWN and event.key == self.pygame.K_ESCAPE:
                    self.running = False; return "LEVEL_MENU"
                status = self.handle_input(event)
                if status: return status

            self.update(delta_time, frame_count)
            self.draw()
            frame_count +=1

            if not self.items_to_target and not self.items_on_screen and self.items_spawned_in_group >= len(self.current_group):
                if self.current_group_index >= len(self.groups) - 1:
                    return "WELL_DONE"
        
        self.cleanup()
        return "LEVEL_MENU"

    def handle_input(self, event):
        """Handle player input for the C/L Case level."""
        if event.type == self.pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            item_hit = None
            for item_obj in self.items_on_screen:
                if item_obj["rect"].collidepoint(mx, my):
                    item_hit = item_obj
                    break
            
            if item_hit: # Player clicked on an item
                # For C/L Case, player sees uppercase target, but items are lowercase
                if item_hit["value"] == self.target_item: # Match against lowercase target
                    self.score += 10
                    self.overall_destroyed += 1
                    self.items_destroyed_in_group +=1
                    self.items_on_screen.remove(item_hit)
                    
                    self.particle_manager.create_explosion(item_hit["x"], item_hit["y"], 
                        color=self.random.choice(self.game_globals['FLAME_COLORS']))

                    if self.items_to_target:
                        self.items_to_target.pop(0)
                        if self.items_to_target:
                            self.target_item = self.items_to_target[0]
                            self.target_display_item = self.target_item.upper()
                        else: 
                            self.target_item = None
                            self.target_display_item = None
                else: 
                    self.game_globals['handle_misclick'](mx,my)
            else: 
                self.game_globals['handle_misclick'](mx,my)
        return None

    def update(self, delta_time, frame_count):
        """Update game state for the C/L Case level."""
        LETTER_SPAWN_INTERVAL = self.game_globals.get("LETTER_SPAWN_INTERVAL", 30)
        if self.items_spawned_in_group < len(self.current_group) and frame_count % LETTER_SPAWN_INTERVAL == 0:
            item_value = self.current_group[self.items_spawned_in_group] # Spawn lowercase
            font_to_use = self.fonts['TARGET_FONT']
            # Display items also in lowercase to match what is clicked
            text_surface = font_to_use.render(item_value, True, self.game_globals['WHITE'])
            text_rect = text_surface.get_rect()
            
            new_item = {
                "value": item_value, # Store the actual value (lowercase)
                "x": self.random.randint(50, self.WIDTH - 50),
                "y": self.random.randint(50, self.HEIGHT - 150),
                "dx": self.random.uniform(-1, 1) * 60, 
                "dy": self.random.uniform(-1, 1) * 60, 
                "surface": text_surface,
                "rect": text_rect,
            }
            new_item["rect"].topleft = (new_item["x"], new_item["y"])
            self.items_on_screen.append(new_item)
            self.items_spawned_in_group += 1

        for item_obj in self.items_on_screen:
            item_obj["x"] += item_obj["dx"] * delta_time
            item_obj["y"] += item_obj["dy"] * delta_time
            if item_obj["x"] < 0 or item_obj["x"] + item_obj["rect"].width > self.WIDTH:
                item_obj["dx"] *= -1
            if item_obj["y"] < 0 or item_obj["y"] + item_obj["rect"].height > self.HEIGHT - 100:
                item_obj["dy"] *= -1
            item_obj["rect"].topleft = (item_obj["x"], item_obj["y"])

        if not self.items_to_target and not self.items_on_screen and self.items_spawned_in_group >= len(self.current_group):
            if self.current_group_index < len(self.groups) - 1:
                self.current_group_index += 1
                self.common_game_state["current_group_index"] = self.current_group_index
                self.current_group = self.groups[self.current_group_index]
                self.items_to_target = self.current_group.copy()
                if self.items_to_target:
                    self.target_item = self.items_to_target[0]
                    self.target_display_item = self.target_item.upper()
                else:
                    self.target_item = None
                    self.target_display_item = None
                self.items_spawned_in_group = 0
                self.items_destroyed_in_group = 0
                print(f"C/L Case Level: Group {self.current_group_index + 1}. Target: {self.target_display_item}")

        for star in self.stars:
            star[2] = self.random.randint(1, 3); star[1] += star[3]
            if star[1] > self.HEIGHT: star[1] = 0; star[0] = self.random.randint(0, self.WIDTH)
        self.particle_manager.update(delta_time)

    def draw(self):
        """Draw all elements for the C/L Case level."""
        self.screen.fill(self.game_globals['BLACK'])
        for star in self.stars:
            self.pygame.draw.circle(self.screen, self.game_globals['WHITE'], (int(star[0]), int(star[1])), star[2])
        for item_obj in self.items_on_screen:
            self.screen.blit(item_obj["surface"], item_obj["rect"])
        self.particle_manager.draw(self.screen)
        self.game_globals['display_info'](
            self.score, "N/A", self.target_display_item, # Show uppercase target in HUD
            self.overall_destroyed, self.total_items_in_level, "clcase"
        )
        if 'draw_cracks' in self.game_globals: self.game_globals['draw_cracks'](self.screen)
        self.pygame.display.flip()

    def cleanup(self):
        print("C/L Case Level: Cleaning up..."); self.items_on_screen = []

def start_clcase_level_instance(screen, game_globals, common_game_state):
    level = CLCaseLevel(screen, game_globals, common_game_state)
    return level.run() 