"""
SuperStudent - Main Entry Point

This is the main entry point for the SuperStudent game. It handles the game state
management and main loop, delegating to appropriate modules for screens and levels.
"""
import pygame
import sys
import time
from enum import Enum, auto

# Import utility modules
from utils.resource_manager import ResourceManager
from utils.particle_system import ParticleSystem
from utils.effects import Effects

# Import screens
from screens.welcome_screen import WelcomeScreen
# Import other screens as they are implemented
# from screens.level_menu import LevelMenu
# from screens.checkpoint_screen import CheckpointScreen
# from screens.game_over_screen import GameOverScreen
# from screens.well_done_screen import WellDoneScreen

# Import levels
# from levels.abc_level import AlphabetLevel
# from levels.numbers_level import NumbersLevel
from levels.shapes_level import ShapesLevel
from levels.colors_level import ColorsLevel

# Import settings
from settings import FPS, DISPLAY_MODES, DEBUG_MODE, SHOW_FPS

# Import new modular components
from game_setup import screen, WIDTH, HEIGHT, DISPLAY_MODE, resource_manager
from game_logic import game_loop
from engine.engine import run

class GameState(Enum):
    """Enum representing different game states."""
    WELCOME = auto()
    LEVEL_MENU = auto()
    ABC_LEVEL = auto()
    NUMBERS_LEVEL = auto()
    SHAPES_LEVEL = auto()
    CLCASE_LEVEL = auto()
    COLORS_LEVEL = auto()
    CHECKPOINT = auto()
    GAME_OVER = auto()
    WELL_DONE = auto()
    QUIT = auto()


class Game:
    """Main game class managing the game state and main loop."""
    
    def __init__(self):
        """Initialize game systems."""
        # Set up clock for timing
        self.clock = pygame.time.Clock()
        self.FPS = FPS
        self.last_time = time.time()
        
        # Initialize game state
        self.current_state = GameState.WELCOME
        self.running = True
        
        # Initialize utility systems
        self.resource_manager = resource_manager
        
        # Initialize particle system and effects (these will be properly sized after welcome screen)
        self.particle_system = ParticleSystem(WIDTH, HEIGHT)
        self.effects = Effects(WIDTH, HEIGHT)
        
        # Initialize screens and levels
        self.current_screen = None
        self.screens = {}
        self.levels = {}
        
        # Initialize the screens that are used right away
        self.screens[GameState.WELCOME] = WelcomeScreen(WIDTH, HEIGHT, self.resource_manager)
        # Other screens will be initialized on demand
        
        # Levels will be initialized on demand as they are selected
    
    def run(self):
        """Run the main game loop."""
        # Initialize first screen
        self._initialize_current()
        
        # Main game loop
        while self.running:
            # Calculate delta time since last frame
            current_time = time.time()
            delta_time = current_time - self.last_time
            self.last_time = current_time
            
            # Cap delta time to prevent large jumps during pauses
            delta_time = min(delta_time, 0.1)
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                
                # Pass event to current screen or level
                new_state = self._handle_event(event)
                if new_state:
                    self._change_state(new_state)
                    if not self.running:
                        break
            
            # Update current screen or level
            if self._update(delta_time):
                # Draw the current screen or level
                self._draw()
            
            # Cap the frame rate
            self.clock.tick(self.FPS)
        
        # Clean up and exit
        pygame.quit()
        sys.exit()
    
    def _initialize_current(self):
        """Initialize the current screen or level."""
        if self.current_state == GameState.WELCOME:
            # Initialize welcome screen if not already
            if not self.screens[GameState.WELCOME].initialized:
                self.screens[GameState.WELCOME].initialize()
            self.current_screen = self.screens[GameState.WELCOME]
            
        elif self.current_state == GameState.LEVEL_MENU:
            # Initialize level menu if needed
            if GameState.LEVEL_MENU not in self.screens:
                from screens.level_menu import LevelMenu
                self.screens[GameState.LEVEL_MENU] = LevelMenu(WIDTH, HEIGHT, self.resource_manager)
                self.screens[GameState.LEVEL_MENU].initialize()
            self.current_screen = self.screens[GameState.LEVEL_MENU]
            
        elif self.current_state == GameState.COLORS_LEVEL:
            # Initialize colors level if needed
            if GameState.COLORS_LEVEL not in self.levels:
                self.levels[GameState.COLORS_LEVEL] = ColorsLevel(
                    WIDTH, HEIGHT, 
                    self.resource_manager, 
                    self.particle_system, 
                    self.effects
                )
            # Always re-initialize the level when entering it
            self.levels[GameState.COLORS_LEVEL].initialize()
            self.current_screen = self.levels[GameState.COLORS_LEVEL]
            
        elif self.current_state == GameState.SHAPES_LEVEL:
            # Initialize shapes level if needed
            if GameState.SHAPES_LEVEL not in self.levels:
                self.levels[GameState.SHAPES_LEVEL] = ShapesLevel(
                    WIDTH, HEIGHT,
                    self.resource_manager,
                    self.particle_system,
                    self.effects
                )
            # Always re-initialize the level when entering it
            self.levels[GameState.SHAPES_LEVEL].initialize()
            self.current_screen = self.levels[GameState.SHAPES_LEVEL]
            
        # Handle other states as they are implemented
        else:
            print(f"Warning: Unhandled game state {self.current_state}")
            # Default to welcome screen
            self.current_state = GameState.WELCOME
            self.current_screen = self.screens[GameState.WELCOME]
            self.current_screen.initialize()
    
    def _update(self, delta_time):
        """Update the current screen or level."""
        # Update the current screen
        return self.current_screen.update(delta_time)
    
    def _draw(self):
        """Draw the current screen or level."""
        screen.fill((0, 0, 0))  # Clear screen
        
        # Draw the current screen
        self.current_screen.draw(screen)
        
        # Show FPS if in debug mode
        if DEBUG_MODE and SHOW_FPS:
            fps_text = f"FPS: {int(self.clock.get_fps())}"
            fps_surf = pygame.font.Font(None, 24).render(fps_text, True, (255, 255, 255))
            screen.blit(fps_surf, (10, 10))
        
        pygame.display.flip()
    
    def _handle_event(self, event):
        """
        Handle events for the current screen or level.
        
        Returns:
            New game state if a state change is requested, None otherwise
        """
        return self.current_screen.handle_event(event)
    
    def _change_state(self, new_state):
        """
        Change the current game state.
        
        Args:
            new_state: The new game state to change to
        """
        self.current_state = new_state
        self._initialize_current()

if __name__ == "__main__":
    pygame.init()
    run() 