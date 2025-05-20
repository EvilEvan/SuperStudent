# SuperStudent Game Entry Point

## Single Entry Point Requirement

The SuperStudent game should **only** be launched through `engine/engine.py`. This is a critical architectural requirement to ensure proper initialization and resource management.

## Correct Way to Run the Game

```python
# Correct way to run the game
from engine.engine import Engine

if __name__ == '__main__':
    engine = Engine()
    engine.run()
```

## Incorrect Ways to Run the Game

❌ **Do not** run the game by importing and executing other modules directly:

```python
# INCORRECT - Don't do this
import game_logic
game_logic.run_game()  # This will bypass important initialization

# INCORRECT - Don't do this
from screens.main_menu import MainMenu
menu = MainMenu()
menu.show()  # This will cause issues with game state management
```

## Why This Matters

1. **Resource Management**: The Engine class handles proper initialization and cleanup of game resources
2. **State Management**: Running through the engine ensures consistent game state
3. **Error Handling**: The engine provides centralized error handling and logging
4. **Performance**: The engine optimizes resource loading and memory management

## Implementation Details

The Engine class in `engine/engine.py` is responsible for:

- Initializing the game window and display
- Loading and managing game assets
- Setting up the game loop
- Handling input events
- Managing game state transitions
- Cleaning up resources on exit

## Testing

To verify that your code follows this requirement:

1. Run the import tests: `pytest tests/test_imports.py`
2. Check for stale imports: `python utils/import_checker.py`

## Common Issues

If you encounter import errors or initialization problems:

1. Make sure you're running the game through `engine/engine.py`
2. Check that all module imports are relative to the project root
3. Verify that the Engine class is properly initialized before any game logic runs 