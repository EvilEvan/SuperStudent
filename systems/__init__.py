"""
Systems module for SuperStudent game.
Contains reusable services like particles, explosions, glass cracks, etc.
"""

from .particle import ParticlePool
from .explosion import ExplosionManager
from .glass_crack import GlassCrackManager
from .hud import HUD
from .multitouch import TouchManager
from .resource_manager import ResourceManager

__all__ = [
    'ParticlePool',
    'ExplosionManager',
    'GlassCrackManager',
    'HUD',
    'TouchManager',
    'ResourceManager'
] 