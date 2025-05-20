"""
Multi-touch system for handling touch and mouse input.
"""

import pygame
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Touch:
    id: int
    pos: Tuple[float, float]
    is_down: bool
    is_move: bool

class TouchManager:
    def __init__(self):
        self.active_touches: Dict[int, Touch] = {}
        self.next_touch_id: int = 0
    
    def handle_event(self, event: pygame.event.Event) -> Optional[Touch]:
        """Handle a pygame event and return a Touch object if relevant."""
        if event.type in (pygame.FINGERDOWN, pygame.MOUSEBUTTONDOWN):
            touch_id = self.next_touch_id
            self.next_touch_id += 1
            pos = (event.x * pygame.display.get_surface().get_width(),
                  event.y * pygame.display.get_surface().get_height())
            touch = Touch(touch_id, pos, True, False)
            self.active_touches[touch_id] = touch
            return touch
            
        elif event.type in (pygame.FINGERUP, pygame.MOUSEBUTTONUP):
            touch_id = event.finger_id if hasattr(event, 'finger_id') else 0
            if touch_id in self.active_touches:
                touch = self.active_touches[touch_id]
                touch.is_down = False
                return touch
                
        elif event.type in (pygame.FINGERMOTION, pygame.MOUSEMOTION):
            touch_id = event.finger_id if hasattr(event, 'finger_id') else 0
            if touch_id in self.active_touches:
                pos = (event.x * pygame.display.get_surface().get_width(),
                      event.y * pygame.display.get_surface().get_height())
                touch = self.active_touches[touch_id]
                touch.pos = pos
                touch.is_move = True
                return touch
        
        return None
    
    def get_touch(self, touch_id: int) -> Optional[Touch]:
        """Get a touch by its ID."""
        return self.active_touches.get(touch_id)
    
    def get_active_touches(self) -> Dict[int, Touch]:
        """Get all active touches."""
        return self.active_touches.copy()
    
    def clear_touches(self) -> None:
        """Clear all active touches."""
        self.active_touches.clear()
        self.next_touch_id = 0 