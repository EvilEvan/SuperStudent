"""

Super Student - Glass Shatter Display



Description:

    This game features a dynamic 'Glass Shatter Display' effect. When the player makes a mistake (such as a misclick or mistap), a crack appears on the screen at the point of error. After a certain number of cracks, the entire background 'shatters' with a visual effect, swapping the background color and creating glass particle effects. This mechanic provides immediate visual feedback for mistakes and adds a dramatic, interactive element to the gameplay experience.



Date: 2024-06-09

"""

import pygame
import random
import math

# Import level modules
from levels import alphabet_level
from levels import numbers_level
from levels import shapes_level
from levels import clcase_level
from levels import colors_level # This might be an issue if main.py also imports it.
from levels import abc_level
from levels import cl_case_letters

from settings import (
    COLORS_COLLISION_DELAY, DISPLAY_MODES, DEFAULT_MODE, DISPLAY_SETTINGS_PATH,
    LEVEL_PROGRESS_PATH, MAX_CRACKS, WHITE, BLACK, FLAME_COLORS, LASER_EFFECTS,
    LETTER_SPAWN_INTERVAL, SEQUENCES, GAME_MODES, GROUP_SIZE,
    SHAKE_DURATION_MISCLICK, SHAKE_MAGNITUDE_MISCLICK,
    GAME_OVER_CLICK_DELAY, GAME_OVER_COUNTDOWN_SECONDS,
    FPS, CHECKPOINT_TRIGGER # Added FPS and CHECKPOINT_TRIGGER
)


pygame.init()


# Allow only the necessary events (including multi-touch)
pygame.event.set_allowed([
    pygame.FINGERDOWN,
    pygame.FINGERUP,
    pygame.FINGERMOTION,
    pygame.QUIT,
    pygame.KEYDOWN,
    pygame.MOUSEBUTTONDOWN,
    pygame.MOUSEBUTTONUP,
])


# Get the screen size and initialize display in fullscreen
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Super Student")


# Function to determine initial display mode based on screen size
def detect_display_type():
    info = pygame.display.Info()
    screen_w, screen_h = info.current_w, info.current_h
    
    # If screen is larger than typical desktop monitors, assume it's a QBoard
    if screen_w >= 1920 and screen_h >= 1080:
        if screen_w > 2560 or screen_h > 1440:  # Larger than QHD is likely QBoard
            return "QBOARD"
    
    # Default to smaller format for typical monitors/laptops
    return "DEFAULT"


# Initialize with default mode first
DISPLAY_MODE = DEFAULT_MODE


# Try to load previous display mode setting
try:
    with open(DISPLAY_SETTINGS_PATH, "r") as f:
        loaded_mode = f.read().strip()
        if loaded_mode in DISPLAY_MODES:
            DISPLAY_MODE = loaded_mode
except:
    # If file doesn't exist or can't be read, use auto-detection
    DISPLAY_MODE = detect_display_type()


# Import ResourceManager
from utils.resource_manager import ResourceManager
from utils.particle_system import ParticleManager


# Initialize particle manager globally
particle_manager = None


def init_resources():
    """
    Initialize game resources based on the current display mode using ResourceManager.
    """
    global font_sizes, fonts, large_font, small_font, TARGET_FONT, TITLE_FONT
    global MAX_PARTICLES, MAX_EXPLOSIONS, MAX_SWIRL_PARTICLES, mother_radius
    global particle_manager
    
    # Import from settings
    from settings import FONT_SIZES, MAX_PARTICLES as PARTICLES_SETTINGS
    from settings import MAX_EXPLOSIONS as EXPLOSIONS_SETTINGS
    from settings import MAX_SWIRL_PARTICLES as SWIRL_SETTINGS
    from settings import MOTHER_RADIUS
    
    # Get resource manager singleton
    resource_manager = ResourceManager()
    
    # Set display mode in the resource manager
    resource_manager.set_display_mode(DISPLAY_MODE)
    
    # Initialize mode-specific settings from settings.py
    MAX_PARTICLES = PARTICLES_SETTINGS[DISPLAY_MODE]
    MAX_EXPLOSIONS = EXPLOSIONS_SETTINGS[DISPLAY_MODE]
    MAX_SWIRL_PARTICLES = SWIRL_SETTINGS[DISPLAY_MODE]
    mother_radius = MOTHER_RADIUS[DISPLAY_MODE]
    
    # Initialize font sizes from settings
    font_sizes = FONT_SIZES[DISPLAY_MODE]["regular"]
    
    # Get core resources
    resources = resource_manager.initialize_game_resources()
    
    # Assign resources to global variables for backward compatibility
    fonts = resources['fonts']
    large_font = resources['large_font']
    small_font = resources['small_font']
    TARGET_FONT = resources['target_font']
    TITLE_FONT = resources['title_font']
    
    # Initialize particle manager with display mode specific settings
    particle_manager = ParticleManager(max_particles=MAX_PARTICLES)
    particle_manager.set_culling_distance(WIDTH)  # Set culling distance based on screen size
    
    # Save display mode preference
    try:
        with open(DISPLAY_SETTINGS_PATH, "w") as f:
            f.write(DISPLAY_MODE)
    except:
        pass  # If can't write, silently continue
    
    print(f"Resources initialized for display mode: {DISPLAY_MODE}")
    
    return resource_manager


# Initialize resources with current mode
resource_manager = init_resources()


# OPTIMIZATION: Global particle system limits to prevent lag
PARTICLE_CULLING_DISTANCE = WIDTH  # Distance at which to cull offscreen particles
# Particle pool for object reuse
particle_pool = []
for _ in range(100):  # Pre-create some particles to reuse
    particle_pool.append({
        "x": 0, "y": 0, "color": (0,0,0), "size": 0, 
        "dx": 0, "dy": 0, "duration": 0, "start_duration": 0,
        "active": False
    })


# Global variables for effects and touches.
particles = []
shake_duration = 0
shake_magnitude = 10
active_touches = {}


# Declare explosions and lasers in global scope so they are available to all functions
explosions = []
lasers = []


# Glass cracking effect variables
glass_cracks = []
background_shattered = False
CRACK_DURATION = 600  # How long the shattered effect lasts (in frames)
shatter_timer = 0  # Timer for the shattered effect
opposite_background = BLACK  # Opposite of white
current_background = WHITE  # Start with white background for levels
game_over_triggered = False  # Flag to track if game over has been triggered
game_over_delay = 0  # Delay before showing game over screen to allow animation to play
GAME_OVER_DELAY_FRAMES = 60  # Number of frames to wait before showing game over


# Add this near the other global variables at the top
player_color_transition = 0
player_current_color = FLAME_COLORS[0]
player_next_color = FLAME_COLORS[1]


# Add global variables for charge-up effect
charging_ability = False
charge_timer = 0
charge_particles = []
ability_target = None


# Add at the top of the file with other global variables
swirl_particles = []
particles_converging = False
convergence_target = None
convergence_timer = 0


###############################################################################
#                              SCREEN FUNCTIONS                               #
###############################################################################

def welcome_screen():
    """Show the welcome screen with display size options."""
    global DISPLAY_MODE
    
    # Calculate scaling factor based on current screen size
    # This ensures welcome screen elements fit properly on any display
    base_height = 1080  # Base design height
    scale_factor = HEIGHT / base_height
    
    # Apply scaling to title and buttons
    title_offset = int(50 * scale_factor)
    button_width = int(200 * scale_factor)
    button_height = int(60 * scale_factor)
    button_spacing = int(20 * scale_factor)
    button_y_pos = int(200 * scale_factor)
    instruction_y_pos = int(150 * scale_factor)
    
    # Vivid bright colors for particles
    particle_colors = [
        (255, 0, 128),   # Bright pink
        (0, 255, 128),   # Bright green
        (128, 0, 255),   # Bright purple
        (255, 128, 0),   # Bright orange
        (0, 128, 255)    # Bright blue
    ]
    
    # Create dynamic gravitational particles
    particles = []
    for _ in range(120):
        angle = random.uniform(0, math.pi * 2)
        distance = random.uniform(200, max(WIDTH, HEIGHT))
        x = WIDTH // 2 + math.cos(angle) * distance
        y = HEIGHT // 2 + math.sin(angle) * distance
        size = random.randint(int(9 * scale_factor), int(15 * scale_factor))
        particles.append({
            "x": x,
            "y": y,
            "color": random.choice(particle_colors),
            "size": size,
            "orig_size": size,
            "angle": random.uniform(0, math.pi * 2),
            "speed": random.uniform(0.1, 0.5),
            "pulse_speed": random.uniform(0.02, 0.06),
            "pulse_factor": random.random()
        })


    # Button hover state and animation
    default_hover = False
    qboard_hover = False
    
    # Title animation parameters
    title_scale = 1.0
    title_scale_direction = 0.001
    title_colors = FLAME_COLORS.copy()
    current_color_idx = 0
    next_color_idx = 1
    color_transition = 0.0
    
    # Use scaled font size for title based on current display
    title_font_size = int(320 * scale_factor)  # Default title size times scale factor
    title_font = pygame.font.Font(None, title_font_size)
    
    # Create title rect for animation (we'll reuse this)
    title_text = "Super Student"
    title_rect_center = (WIDTH // 2, HEIGHT // 2 - title_offset)


    # Instructions
    display_text = small_font.render("Choose Display Size:", True, (255, 255, 255))
    display_rect = display_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + instruction_y_pos))
    
    # Create buttons for display size options
    default_button = pygame.Rect((WIDTH // 2 - button_width - button_spacing, HEIGHT // 2 + button_y_pos), (button_width, button_height))
    qboard_button = pygame.Rect((WIDTH // 2 + button_spacing, HEIGHT // 2 + button_y_pos), (button_width, button_height))
    
    # Auto-detected mode text
    auto_text = small_font.render(f"Auto-detected: {detect_display_type()}", True, (200, 200, 200))
    auto_rect = auto_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + button_y_pos + button_height + 30))
    
    # Scale collaboration font based on display size
    collab_font_size = int(100 * scale_factor)
    collab_font = pygame.font.Font(None, collab_font_size)
    
    sangsom_pulse = 0
    sangsom_pulse_dir = 0.02
    
    # For swirl effect around title
    swirl_particles = []
    swirl_angle = 0
    
    # --- Main welcome screen loop ---
    running = True
    clock = pygame.time.Clock()
    while running:
        # Handle events
        mx, my = pygame.mouse.get_pos()
        default_hover = default_button.collidepoint(mx, my)
        qboard_hover = qboard_button.collidepoint(mx, my)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if default_button.collidepoint(mx, my):
                    # Create click particles
                    for _ in range(15):
                        create_particle(
                            mx, my, 
                            random.choice([(0, 200, 255), (100, 230, 255)]), 
                            random.randint(5, 12),
                            random.uniform(-3, 3), 
                            random.uniform(-3, 3),
                            20
                        )
                    DISPLAY_MODE = "DEFAULT"
                    init_resources()
                    running = False
                elif qboard_button.collidepoint(mx, my):
                    # Create click particles
                    for _ in range(15):
                        create_particle(
                            mx, my, 
                            random.choice([(255, 0, 150), (255, 100, 180)]), 
                            random.randint(5, 12),
                            random.uniform(-3, 3), 
                            random.uniform(-3, 3),
                            20
                        )
                    DISPLAY_MODE = "QBOARD"
                    init_resources()
                    running = False
        
        # Clear screen
        screen.fill(BLACK)
        
        # Update and draw particles
        for particle in particles:
            # Orbital movement
            particle["angle"] += particle["speed"] * 0.01
            
            # Pulse size
            particle["pulse_factor"] += particle["pulse_speed"]
            if particle["pulse_factor"] > 1.0:
                particle["pulse_factor"] = 0.0
            
            pulse = math.sin(particle["pulse_factor"] * math.pi * 2) * 0.3 + 0.7
            current_size = particle["orig_size"] * pulse
            
            # Calculate position with slight orbital movement
            orbit_radius = math.sin(particle["angle"]) * 20
            x = particle["x"] + math.cos(particle["angle"]) * orbit_radius
            y = particle["y"] + math.sin(particle["angle"]) * orbit_radius
            
            pygame.draw.circle(screen, particle["color"], (int(x), int(y)), max(1, int(current_size)))
        
        # Update swirl effect
        swirl_angle += 0.02
        if random.random() < 0.1 and len(swirl_particles) < 30:
            radius = random.uniform(100, 200) * scale_factor
            angle = random.uniform(0, math.pi * 2)
            swirl_particles.append({
                "radius": radius,
                "angle": angle,
                "speed": random.uniform(0.01, 0.03),
                "color": random.choice(particle_colors),
                "size": random.randint(4, 8),
                "life": random.randint(50, 150)
            })
        
        # Update and draw swirl particles
        for i, p in enumerate(swirl_particles):
            p["angle"] += p["speed"]
            p["life"] -= 1
            
            x = title_rect_center[0] + math.cos(p["angle"]) * p["radius"]
            y = title_rect_center[1] + math.sin(p["angle"]) * p["radius"]
            
            alpha = min(255, p["life"] * 2)
            color = (p["color"][0], p["color"][1], p["color"][2])
            
            pygame.draw.circle(screen, color, (int(x), int(y)), p["size"])
            
            # Remove dead particles
            if p["life"] <= 0:
                swirl_particles[i] = None
        
        swirl_particles = [p for p in swirl_particles if p is not None]
        
        # Title color transition animation
        color_transition += 0.005
        if color_transition >= 1.0:
            color_transition = 0.0
            current_color_idx = next_color_idx
            next_color_idx = (next_color_idx + 1) % len(title_colors)
        
        # Blend between current and next color
        r = int(title_colors[current_color_idx][0] * (1 - color_transition) + title_colors[next_color_idx][0] * color_transition)
        g = int(title_colors[current_color_idx][1] * (1 - color_transition) + title_colors[next_color_idx][1] * color_transition)
        b = int(title_colors[current_color_idx][2] * (1 - color_transition) + title_colors[next_color_idx][2] * color_transition)
        title_color = (r, g, b)
        
        # Remove title breathing animation
        # Draw title with depth/glow effect with updated color
    shadow_color = (20, 20, 20)
    for depth in range(1, 0, -1):
        shadow = title_font.render(title_text, True, shadow_color)
        shadow_rect = shadow.get_rect(center=(title_rect_center[0] + depth, title_rect_center[1] + depth))
        screen.blit(shadow, shadow_rect)
        
    glow_colors = [(r//2, g//2, b//2), (r//3, g//3, b//3)]
    for i, glow_color in enumerate(glow_colors):
        glow = title_font.render(title_text, True, glow_color)
        offset = i + 1
        for dx, dy in [(-offset,0), (offset,0), (0,-offset), (0,offset)]:
            glow_rect = glow.get_rect(center=(title_rect_center[0] + dx, title_rect_center[1] + dy))
            screen.blit(glow, glow_rect)
            
    highlight_color = (min(r+80, 255), min(g+80, 255), min(b+80, 255))
    shadow_color = (max(r-90, 0), max(g-90, 0), max(b-90, 0))
    mid_color = (max(r-40, 0), max(g-40, 0), max(b-40, 0))
        
    highlight = title_font.render(title_text, True, highlight_color)
    highlight_rect = highlight.get_rect(center=(title_rect_center[0] - 4, title_rect_center[1] - 4))
    screen.blit(highlight, highlight_rect)
        
    mid_tone = title_font.render(title_text, True, mid_color)
    mid_rect = mid_tone.get_rect(center=(title_rect_center[0] + 2, title_rect_center[1] + 2))
    screen.blit(mid_tone, mid_rect)
        
    inner_shadow = title_font.render(title_text, True, shadow_color)
    inner_shadow_rect = inner_shadow.get_rect(center=(title_rect_center[0] + 4, title_rect_center[1] + 4))
    screen.blit(inner_shadow, inner_shadow_rect)
        
    title = title_font.render(title_text, True, title_color)
    title_rect = title.get_rect(center=title_rect_center)
    screen.blit(title, title_rect)
        
    # Draw instructions
    # Draw instructions
    screen.blit(display_text, display_rect)
    # Draw buttons with hover effects

    # Default button
    hover_expansion = 3 if default_hover else 0
    hover_button = pygame.Rect(
        default_button.x - hover_expansion, 
        default_button.y - hover_expansion, 
        default_button.width + hover_expansion*2, 
        default_button.height + hover_expansion*2
    )
    pygame.draw.rect(screen, (20, 20, 20), hover_button)
    glow_intensity = 6 if default_hover else 5
    for i in range(1, glow_intensity):
        default_rect = pygame.Rect(
            hover_button.x - i, 
            hover_button.y - i, 
            hover_button.width + 2*i, 
            hover_button.height + 2*i
        )
        glow_color = (0, 200+min(55, i*10), 255) if default_hover else (0, 200, 255)
        pygame.draw.rect(screen, glow_color, default_rect, 1)
    pygame.draw.rect(screen, (0, 200, 255), hover_button, 2)
    default_text = small_font.render("Default", True, WHITE)
    default_text_rect = default_text.get_rect(center=hover_button.center)
    screen.blit(default_text, default_text_rect)
    
    # QBoard button
    hover_expansion = 3 if qboard_hover else 0
    hover_button = pygame.Rect(
        qboard_button.x - hover_expansion, 
        qboard_button.y - hover_expansion, 
        qboard_button.width + hover_expansion*2, 
        qboard_button.height + hover_expansion*2
    )
    pygame.draw.rect(screen, (20, 20, 20), hover_button)
    glow_intensity = 6 if qboard_hover else 5
    for i in range(1, glow_intensity):
        qboard_rect = pygame.Rect(
            hover_button.x - i, 
            hover_button.y - i, 
            hover_button.width + 2*i, 
            hover_button.height + 2*i
        )
        glow_color = (255, min(100, i*20), 150+min(30, i*5)) if qboard_hover else (255, 0, 150)
        pygame.draw.rect(screen, glow_color, qboard_rect, 1)
    pygame.draw.rect(screen, (255, 0, 150), hover_button, 2)
    qboard_text = small_font.render("QBoard", True, WHITE)
    qboard_text_rect = qboard_text.get_rect(center=hover_button.center)
    screen.blit(qboard_text, qboard_text_rect)
    
    # Auto-detected mode indicator
    screen.blit(auto_text, auto_rect)
    
    # SANGSOM animation
    sangsom_pulse += sangsom_pulse_dir
    if sangsom_pulse > 1.0 or sangsom_pulse < 0.0:
        sangsom_pulse_dir *= -1
        
    bright_yellow = (255, 255, 0)
    lite_yellow = (255, 255, 150)
    sangsom_color = tuple(int(bright_yellow[i] * (1 - sangsom_pulse) + lite_yellow[i] * sangsom_pulse) for i in range(3))
    
    # Draw collaboration text with pulsing SANGSOM
    collab_text1 = collab_font.render("In collaboration with ", True, WHITE)
    collab_text2 = collab_font.render("SANGSOM", True, sangsom_color)
    collab_text3 = collab_font.render(" Kindergarten", True, WHITE)
    
    collab_rect1 = collab_text1.get_rect()
    collab_rect1.right = WIDTH // 2 - collab_text2.get_width() // 2
    collab_rect1.centery = HEIGHT // 2 + int(350 * scale_factor)
    
    collab_rect2 = collab_text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + int(350 * scale_factor)))
    
    collab_rect3 = collab_text3.get_rect()
    collab_rect3.left = collab_rect2.right
    collab_rect3.centery = HEIGHT // 2 + int(350 * scale_factor)
    
    screen.blit(collab_text1, collab_rect1)
    screen.blit(collab_text2, collab_rect2)
    screen.blit(collab_text3, collab_rect3)
    
    # Creator text
    creator_text = small_font.render("Created by Teacher Evan and Teacher Lee", True, WHITE)
    creator_rect = creator_text.get_rect(center=(WIDTH // 2, HEIGHT - 40))
    screen.blit(creator_text, creator_rect)
    
    # Update display and maintain frame rate
    pygame.display.flip()
    clock.tick(60)
    """Draws a button with a neon glow effect."""
    # Fill the button with a dark background
    pygame.draw.rect(screen, (20, 20, 20), rect)
    # Draw a neon glow border by drawing multiple expanding outlines
    for i in range(1, 6):
        neon_rect = pygame.Rect(rect.x - i, rect.y - i, rect.width + 2*i, rect.height + 2*i)
        pygame.draw.rect(screen, base_color, neon_rect, 1)
    # Draw a solid border
    pygame.draw.rect(screen, base_color, rect, 2)

def level_menu():
    """Display the Level Options screen to choose the mission using a cyberpunk neon display."""
    running = True
    clock = pygame.time.Clock()
    # Button dimensions and positions (arranged in two rows)
    button_width = 300
    button_height = 80
    abc_rect = pygame.Rect((WIDTH // 2 - button_width - 20, HEIGHT // 2 - button_height - 10), (button_width, button_height))
    num_rect = pygame.Rect((WIDTH // 2 + 20, HEIGHT // 2 - button_height - 10), (button_width, button_height))
    shapes_rect = pygame.Rect((WIDTH // 2 - button_width - 20, HEIGHT // 2 + 10), (button_width, button_height))
    clcase_rect = pygame.Rect((WIDTH // 2 + 20, HEIGHT // 2 + 10), (button_width, button_height))
    colors_rect = pygame.Rect((WIDTH // 2 - 150, HEIGHT // 2 + 120), (300, 80))  # Add a new Colors button

    # Set up smooth color transition variables for the title
    color_transition = 0.0
    current_color = FLAME_COLORS[0]
    next_color = FLAME_COLORS[1]

    # Vivid bright colors for particles - similar to welcome screen
    particle_colors = [
        (255, 0, 128),   # Bright pink
        (0, 255, 128),   # Bright green
        (128, 0, 255),   # Bright purple
        (255, 128, 0),   # Bright orange
        (0, 128, 255)    # Bright blue
    ]

    # Create OUTWARD moving particles (reverse of welcome screen)
    repel_particles = []
    for _ in range(700):
        # Start particles near center
        angle = random.uniform(0, math.pi * 2)
        distance = random.uniform(10, 100)  # Close to center
        x = WIDTH // 2 + math.cos(angle) * distance
        y = HEIGHT // 2 + math.sin(angle) * distance
        repel_particles.append({
            "x": x,
            "y": y,
            "color": random.choice(particle_colors),
            "size": random.randint(5, 7),
            "speed": random.uniform(3.0, 6.0),
            "angle": angle  # Store the angle for outward movement
        })

    # Brief delay so that time-based effects start smoothly
    pygame.time.delay(100)

    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if abc_rect.collidepoint(mx, my):
                    return "alphabet"
                elif num_rect.collidepoint(mx, my):
                    return "numbers"
                elif shapes_rect.collidepoint(mx, my):
                    return "shapes"
                elif clcase_rect.collidepoint(mx, my):
                    return "clcase"
                elif colors_rect.collidepoint(mx, my):  # Handle Colors button click
                    return "colors"

        # Draw the outward moving particles
        for particle in repel_particles:
            # Move particles AWAY from center
            particle["x"] += math.cos(particle["angle"]) * particle["speed"]
            particle["y"] += math.sin(particle["angle"]) * particle["speed"]

            # Reset particles that move off screen
            if (particle["x"] < 0 or particle["x"] > WIDTH or
                particle["y"] < 0 or particle["y"] > HEIGHT):
                # New angle for variety
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(5, 50)  # Start close to center , was 50
                particle["x"] = WIDTH // 2 + math.cos(angle) * distance
                particle["y"] = HEIGHT // 2 + math.sin(angle) * distance
                particle["angle"] = angle
                particle["color"] = random.choice(particle_colors)
                particle["size"] = random.randint(13, 17)
                particle["speed"] = random.uniform(1.0, 3.0)

            # Draw the particle
            pygame.draw.circle(screen, particle["color"],
                              (int(particle["x"]), int(particle["y"])),
                              particle["size"])

        # Update title color transition
        color_transition += 0.01
        if color_transition >= 1:
            color_transition = 0
            current_color = next_color
            next_color = random.choice(FLAME_COLORS)
        r = int(current_color[0] * (1 - color_transition) + next_color[0] * color_transition)
        g = int(current_color[1] * (1 - color_transition) + next_color[1] * color_transition)
        b = int(current_color[2] * (1 - color_transition) + next_color[2] * color_transition)
        title_color = (r, g, b)

        # Draw title
        title_text = small_font.render("Choose Mission:", True, title_color)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
        screen.blit(title_text, title_rect)

        # Draw the A B C button with a neon cyberpunk look
        draw_neon_button(abc_rect, (255, 0, 150))
        abc_text = small_font.render("A B C", True, WHITE)
        abc_text_rect = abc_text.get_rect(center=abc_rect.center)
        screen.blit(abc_text, abc_text_rect)

        # Draw the 1 2 3 button with a neon cyberpunk look
        draw_neon_button(num_rect, (0, 200, 255))
        num_text = small_font.render("1 2 3", True, WHITE)
        num_text_rect = num_text.get_rect(center=num_rect.center)
        screen.blit(num_text, num_text_rect)

        # Draw the Shapes button with a neon cyberpunk look
        draw_neon_button(shapes_rect, (0, 255, 0))
        shapes_text = small_font.render("Shapes", True, WHITE)
        shapes_text_rect = shapes_text.get_rect(center=shapes_rect.center)
        screen.blit(shapes_text, shapes_text_rect)

        # Draw the new C/L Case Letters button
        draw_neon_button(clcase_rect, (255, 255, 0))
        clcase_text = small_font.render("C/L Case", True, WHITE)
        clcase_text_rect = clcase_text.get_rect(center=clcase_rect.center)
        screen.blit(clcase_text, clcase_text_rect)

        # Draw the new Colors button with a neon rainbow look
        draw_neon_button(colors_rect, (128, 0, 255))
        colors_text = small_font.render("Colors", True, WHITE)
        colors_text_rect = colors_text.get_rect(center=colors_rect.center)
        screen.blit(colors_text, colors_text_rect)

        pygame.display.flip()
        clock.tick(60)

###############################################################################
#                          GAME LOGIC & EFFECTS                               #
###############################################################################

# Map mode strings to level module functions (will be updated to classes later)
LEVEL_DISPATCHER = {
    "alphabet": abc_level.start_alphabet_level_instance,
    "numbers": numbers_level.start_numbers_level_instance,
    "shapes": shapes_level.start_shapes_level_instance,
    "clcase": cl_case_letters.start_clcase_level_instance,
    "colors": colors_level.start_colors_level_instance, # Updated
}

def game_loop(mode):
    global screen, WIDTH, HEIGHT, SEQUENCES, GROUP_SIZE, LEVEL_PROGRESS_PATH, FLAME_COLORS, FPS, CHECKPOINT_TRIGGER # Make sure these are accessible
    global small_font, large_font, TARGET_FONT, TITLE_FONT # Fonts
    global particle_manager # Managers
    global shake_duration, shake_magnitude, particles, active_touches, explosions, lasers, player_color_transition, player_current_color, player_next_color, charging_ability, charge_timer, charge_particles, ability_target, swirl_particles, particles_converging, convergence_target, convergence_timer, glass_cracks, background_shattered, shatter_timer, mother_radius, game_over_triggered, game_over_delay, color_idx, color_sequence, next_color_index, target_dots_left
    
    # Reset global effects that could persist between levels (existing code for this part can remain for now)
    shake_duration = 0
    shake_magnitude = 0
    # particles = [] # This should be managed by the level or particle_manager
    # explosions = [] # Managed by effects system or particle_manager
    # lasers = [] # Managed by effects system or particle_manager
    active_touches = {}  # Clear any lingering active touches
    # glass_cracks = [] # Reset glass cracks - should be managed by an effects system
    # background_shattered = False  # Reset shattered state - effects system
    # mother_radius = 90 # Default radius for mother dot in Colors level - should be level specific
    # color_sequence = [] # Level specific
    # color_idx = 0 # Level specific
    # next_color_index = 0 # Level specific
    # convergence_timer = 0 # Effect specific
    # charge_timer = 0 # Effect specific
    # convergence_target = None # Effect specific
    # player_color_transition = 0 # Player/Effect specific
    # player_current_color = FLAME_COLORS[0]  # Player/Effect specific
    # player_next_color = FLAME_COLORS[1]     # Player/Effect specific
    # charging_ability = False # Player/Ability specific
    # charge_particles = [] # Effect specific
    # ability_target = None # Player/Ability specific
    # swirl_particles = [] # Effect specific
    # particles_converging = False # Effect specific
    # game_over_triggered = False # Game state specific
    # game_over_delay = 0 # Game state specific

    # Create a context dictionary to pass necessary game variables and functions
    game_globals = {
        "screen": screen, 
        "pygame": pygame,
        "random": random,
        "math": math,
        "WIDTH": WIDTH,
        "HEIGHT": HEIGHT,
        "SEQUENCES": SEQUENCES,
        "GROUP_SIZE": GROUP_SIZE,
        "LEVEL_PROGRESS_PATH": LEVEL_PROGRESS_PATH,
        "FLAME_COLORS": FLAME_COLORS,
        "FPS": FPS,
        "CHECKPOINT_TRIGGER": CHECKPOINT_TRIGGER,
        "WHITE": WHITE,
        "BLACK": BLACK,
        "fonts": fonts, # Already there
        "particle_manager_global": particle_manager_global, # Already there
        "handle_misclick": handle_misclick,
        "display_info": display_info,
        "draw_cracks": draw_cracks,
        # Add resource_manager and effects_manager
        "resource_manager": resource_manager,
        "effects_manager": effects_manager,
        "settings": settings # Pass the whole module for now, ColorsLevel uses many settings
    }
    
    common_game_state = {
        "score": 0, 
        "overall_destroyed": 0,
        "total_letters": 0, # Example
        "current_group_index": 0,
        "active_touches": active_touches, # Pass the reference to the global one
        "explosions": explosions, # Pass reference
        "lasers": lasers, # Pass reference
        "glass_cracks": glass_cracks, # Pass reference
        "background_shattered": background_shattered, # Pass reference
        "game_over_triggered": game_over_triggered, # Pass reference
        "player_data": { # Placeholder for player related state
            "player_x": WIDTH // 2,
            "player_y": HEIGHT // 2,
        }
        # ... other per-level state that might be reset ...
    }

    if mode in LEVEL_DISPATCHER:
        level_runner = LEVEL_DISPATCHER[mode]
        # The level runner is expected to be a function that takes (screen, game_globals, common_game_state)
        # and contains its own game loop, returning a status (e.g., True to restart level, False to go to menu)
        print(f"Dispatching to level: {mode}")
        return level_runner(screen, game_globals, common_game_state) 
    else:
        print(f"Error: Unknown game mode '{mode}'")
        # Fallback or error handling, e.g., return to menu
        # return level_menu() # Or some other appropriate action
        return False # Indicate an error / do not restart

    # The original game_loop's extensive logic (if/elif for modes, the main while running loop)
    # will be progressively removed from here and migrated into the respective level files/classes.
    # For now, this function primarily acts as a dispatcher.

def create_aoe(x, y, letters, target_letter):
    """Handles Area of Effect ability (placeholder/unused currently)."""
    # This function seems unused based on the event loop logic.
    # If intended, it would need integration into the event handling.
    global letters_destroyed # Needs access to modify this counter
    create_explosion(x, y, max_radius=350, duration=40) # Bigger AOE explosion
    destroyed_count_in_aoe = 0
    for letter_obj in letters[:]:
        distance = math.hypot(letter_obj["x"] - x, letter_obj["y"] - y)
        if distance < 200: # AOE radius
             # Optional: Check if it's the target letter or destroy any letter?
             # if letter_obj["value"] == target_letter:
                create_explosion(letter_obj["x"], letter_obj["y"], duration=20) # Smaller explosions for hit targets
                # Add particles, etc.
                letters.remove(letter_obj)
                destroyed_count_in_aoe += 1

    letters_destroyed += destroyed_count_in_aoe # Update the counter for the current group


def display_info(score, ability, target_letter, overall_destroyed, total_letters, mode):
    """Displays the HUD elements (Score, Ability, Target, Progress)."""
    # Determine text color based on background
    text_color = BLACK if current_background == WHITE else WHITE
    
    # Different layout for colors mode to prevent overlap
    if mode == "colors":
        # Score at top left
        score_text = small_font.render(f"Score: {score}", True, text_color)
        screen.blit(score_text, (20, 20))
        
        # Target color below score
        target_color_text = small_font.render(f"Target Color: {target_letter}", True, text_color)
        screen.blit(target_color_text, (20, 60))
        
        # Target dots remaining below target color
        if 'target_dots_left' in globals():
            dots_left_text = small_font.render(f"Remaining: {target_dots_left}", True, text_color)
            screen.blit(dots_left_text, (20, 100))
        
        # Next color progress below remaining dots
        if 'current_color_dots_destroyed' in globals():
            next_color_text = small_font.render(f"Next color in: {5 - current_color_dots_destroyed} dots", True, text_color)
            screen.blit(next_color_text, (20, 140))
        
        # Progress on top right
        progress_text = small_font.render(f"Destroyed: {overall_destroyed}/{total_letters}", True, text_color)
        progress_rect = progress_text.get_rect(topright=(WIDTH - 20, 20))
        screen.blit(progress_text, progress_rect)
        
        return  # Exit early for colors mode
    
    # Standard layout for other modes
    score_text = small_font.render(f"Score: {score}", True, text_color)
    screen.blit(score_text, (20, 20))
    
    ability_text = small_font.render(f"Ability: {ability.capitalize()}", True, text_color)
    ability_rect = ability_text.get_rect(topleft=(20, 60))
    screen.blit(ability_text, ability_rect)

    # Right-aligned elements
    display_target = target_letter
    if (mode == "alphabet" or mode == "clcase") and target_letter == "a":
        display_target = "α"
    elif mode == "clcase":
        display_target = target_letter.upper()

    target_text = small_font.render(f"Target: {display_target}", True, text_color)
    target_rect = target_text.get_rect(topright=(WIDTH - 20, 20))
    screen.blit(target_text, target_rect)

    progress_text = small_font.render(f"Destroyed: {overall_destroyed}/{total_letters}", True, text_color)
    progress_rect = progress_text.get_rect(topright=(WIDTH - 20, 60))
    screen.blit(progress_text, progress_rect)


def well_done_screen(score):
    """Screen shown after completing all targets in a mode."""
    flash = True
    flash_count = 0
    running = True
    clock = pygame.time.Clock()
    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()
            # Force click to continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                running = False
                return True  # Return True to indicate we should go back to level menu

        # Display "Well Done!" message
        well_done_font = fonts[2] # Use one of the preloaded larger fonts
        well_done_text = well_done_font.render("Well Done!", True, WHITE)
        well_done_rect = well_done_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(well_done_text, well_done_rect)

        # Display final score
        score_text = small_font.render(f"Final Score: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        screen.blit(score_text, score_rect)


        # Flashing "Click for Next Mission" text
        next_player_color = random.choice(FLAME_COLORS) if flash else BLACK
        next_player_text = small_font.render("Click for Next Mission", True, next_player_color)
        next_player_rect = next_player_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70))
        screen.blit(next_player_text, next_player_rect)

        pygame.display.flip()
        flash_count += 1
        if flash_count % 30 == 0: # Flash every half second
            flash = not flash
        clock.tick(60)
    return False # Should not be reached if click is required

def apply_explosion_effect(x, y, explosion_radius, letters):
    """Pushes nearby letters away from an explosion center."""
    for letter in letters:
        dx = letter["x"] - x
        dy = letter["y"] - y
        dist_sq = dx*dx + dy*dy
        if dist_sq < explosion_radius * explosion_radius and dist_sq > 0:
            dist = math.sqrt(dist_sq)
            # Force is stronger closer to the center
            force = (1 - (dist / explosion_radius)) * 15 # Adjust force multiplier as needed
            # Apply force directly to velocity
            letter["dx"] += (dx / dist) * force
            letter["dy"] += (dy / dist) * force
            # Ensure the item can bounce after being pushed
            letter["can_bounce"] = True


def checkpoint_screen(mode=None):
    """Display the checkpoint screen after every 10 targets with options."""
    global color_idx, color_sequence, next_color_index, target_dots_left, used_colors  # Add used_colors to globals
    running = True
    clock = pygame.time.Clock()
    color_transition = 0.0
    current_color = FLAME_COLORS[0]
    next_color = FLAME_COLORS[1]

    # Store original color information if in colors mode to continue properly
    original_color_idx = color_idx if mode == "colors" else 0
    original_color_sequence = color_sequence[:] if mode == "colors" and 'color_sequence' in globals() else None
    original_next_color_index = next_color_index if mode == "colors" and 'next_color_index' in globals() else 0
    original_target_dots_left = target_dots_left if mode == "colors" and 'target_dots_left' in globals() else 10
    original_used_colors = used_colors[:] if mode == "colors" and 'used_colors' in globals() else []  # Store used_colors state

    # Button dimensions and positions
    button_width = 300
    button_height = 80
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    continue_rect = pygame.Rect((center_x - button_width - 20, center_y + 50), (button_width, button_height))
    menu_rect = pygame.Rect((center_x + 20, center_y + 50), (button_width, button_height))

    # Restore checkpoint screen swirling particles
    swirling_particles = []
    for _ in range(150):  # Restore to 150
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(100, max(WIDTH, HEIGHT) * 0.6) # Start further out
        angular_speed = random.uniform(0.01, 0.03) * random.choice([-1, 1]) # Slower swirl
        radius = random.randint(5, 10)
        color = random.choice(FLAME_COLORS)
        swirling_particles.append({
            "angle": angle, "distance": distance, "angular_speed": angular_speed,
            "radius": radius, "color": color
        })

    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: pygame.quit(); exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if continue_rect.collidepoint(mx, my):
                    if mode == "colors":
                        # Restore original color state and target dots
                        color_idx = original_color_idx
                        target_dots_left = original_target_dots_left
                        # Also restore the color sequence if it exists
                        if original_color_sequence is not None:
                            color_sequence = original_color_sequence
                        # Restore position in sequence
                        if 'next_color_index' in globals():
                            next_color_index = original_next_color_index
                        # Restore used_colors tracking
                        if original_used_colors:
                            used_colors = original_used_colors
                    return True  # Continue game or restart colors level
                elif menu_rect.collidepoint(mx, my):
                    return False  # Return to level menu

        # Update and draw swirling particles
        for particle in swirling_particles:
            particle["angle"] += particle["angular_speed"]
            x = center_x + particle["distance"] * math.cos(particle["angle"])
            y = center_y + particle["distance"] * math.sin(particle["angle"])
            pygame.draw.circle(screen, particle["color"], (int(x), int(y)), particle["radius"])
            if particle["distance"] > max(WIDTH, HEIGHT) * 0.8:
                 particle["distance"] = random.uniform(50, 200)

        # Smooth color transition for heading
        color_transition += 0.02
        if color_transition >= 1:
            color_transition = 0
            current_color = next_color
            next_color = random.choice(FLAME_COLORS)
        r = int(current_color[0] * (1 - color_transition) + next_color[0] * color_transition)
        g = int(current_color[1] * (1 - color_transition) + next_color[1] * color_transition)
        b = int(current_color[2] * (1 - color_transition) + next_color[2] * color_transition)
        heading_color = (r, g, b)

        # Draw heading
        checkpoint_font = fonts[2]
        checkpoint_text = checkpoint_font.render("Checkpoint!", True, heading_color)
        checkpoint_rect = checkpoint_text.get_rect(center=(center_x, center_y - 150))
        screen.blit(checkpoint_text, checkpoint_rect)

        # Additional message
        subtext = small_font.render("Well done! You've completed this task!", True, WHITE)
        subtext_rect = subtext.get_rect(center=(center_x, center_y - 100))
        screen.blit(subtext, subtext_rect)

        # Draw buttons with neon effect
        draw_neon_button(continue_rect, (0, 255, 0)) # Green for continue
        draw_neon_button(menu_rect, (255, 165, 0))   # Orange for menu

        # Change button text based on mode
        if mode == "shapes":
            cont_text = small_font.render("Replay Level", True, WHITE)
        else:
            cont_text = small_font.render("Continue", True, WHITE)
        menu_text = small_font.render("Level Select", True, WHITE)
        screen.blit(cont_text, cont_text.get_rect(center=continue_rect.center))
        screen.blit(menu_text, menu_text.get_rect(center=menu_rect.center))

        pygame.display.flip()
        clock.tick(60)

def create_player_trail(x, y):
    """Creates trail particles behind the (currently static) player position."""
    # This might be less useful if the player doesn't move, but kept for potential future use.
    for _ in range(1): # Reduce particle count for static player
        create_particle(
            x + random.uniform(-10, 10),  # Spawn around center
            y + random.uniform(-10, 10),
            random.choice(FLAME_COLORS),
            random.randint(2, 4),
            random.uniform(-0.2, 0.2),  # Slow drift
            random.uniform(-0.2, 0.2),
            20  # Shorter duration
        )

# Restore charge particle count for charge-up effect
def start_charge_up_effect(player_x, player_y, target_x, target_y):
    global charging_ability, charge_timer, charge_particles, ability_target
    charging_ability = True
    charge_timer = 45
    ability_target = (target_x, target_y)
    charge_particles = []
    for _ in range(150):  # Restore to 150
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x, y = random.uniform(0, WIDTH), random.uniform(-100, -20)
        elif side == 'bottom':
            x, y = random.uniform(0, WIDTH), random.uniform(HEIGHT + 20, HEIGHT + 100)
        elif side == 'left':
            x, y = random.uniform(-100, -20), random.uniform(0, HEIGHT)
        else: # right
            x, y = random.uniform(WIDTH + 20, WIDTH + 100), random.uniform(0, HEIGHT)

        charge_particles.append({
            "type": "materializing",
            "x": x, "y": y,
            "target_x": player_x, # Target is the player center (orb)
            "target_y": player_y - 80, # Target orb position
            "color": random.choice(FLAME_COLORS),
            "size": random.uniform(1, 3), "max_size": random.uniform(4, 8), # Slightly larger max
            "speed": random.uniform(1.0, 3.0), # Start with some speed
            "opacity": 0, "max_opacity": random.randint(180, 255),
            "materialize_time": random.randint(10, 25), # Faster materialization
            "delay": random.randint(0, 15), # Shorter stagger
            "acceleration": random.uniform(0.1, 0.4), # Higher acceleration
            "wobble_angle": random.uniform(0, 2 * math.pi),
            "wobble_speed": random.uniform(0.1, 0.3),
            "wobble_amount": random.uniform(1.0, 3.0), # Slightly more wobble
            "trail": random.random() < 0.5 # More trails
        })

# Restore swirl particle count for create_swirl_particles
def create_swirl_particles(center_x, center_y, radius=None, count=None):  # Make parameters adjustable
    """Creates particles that swirl around a center point."""
    global swirl_particles
    
    # Set default values based on display mode
    if radius is None:
        radius = 150 if DISPLAY_MODE == "QBOARD" else 80
    
    if count is None:
        count = 50 if DISPLAY_MODE == "QBOARD" else 30
    
    # Limit count to MAX_SWIRL_PARTICLES
    count = min(count, MAX_SWIRL_PARTICLES)
    
    swirl_particles = []
    current_time_ms = pygame.time.get_ticks()
    
    for _ in range(count):
        # Create a particle with randomized properties and initial angle
        swirl_particles.append({
            "angle": random.uniform(0, math.pi * 2),
            "rotation_speed": random.uniform(0.02, 0.04) * (1 if random.random() > 0.5 else -1),
            "base_distance": random.uniform(0.7, 1.0) * radius,  # Vary distance from center
            "distance": 0,  # Will be calculated each frame
            "color": random.choice(FLAME_COLORS),
            "radius": random.randint(4, 8) if DISPLAY_MODE == "DEFAULT" else random.randint(6, 12),
            "pulse_speed": random.uniform(0.5, 1.5),
            "pulse_offset": random.uniform(0, math.pi * 2),
            "convergence": False
        })

def update_swirl_particles(center_x, center_y):
    """Updates and draws swirling particles, handles convergence."""
    global swirl_particles, particles_converging, convergence_timer, convergence_target

    # Add occasional new particles if count is low
    if len(swirl_particles) < 30 and random.random() < 0.1:
         create_swirl_particles(center_x, center_y, count=10) # Add a few more

    current_time_ms = pygame.time.get_ticks() # Use milliseconds for smoother pulsing
    particles_to_remove = []

    for particle in swirl_particles:
        if particles_converging and convergence_target:
            # --- Convergence Logic ---
            target_x, target_y = convergence_target
            # Calculate vector towards target
            dx = target_x - (center_x + particle["distance"] * math.cos(particle["angle"]))
            dy = target_y - (center_y + particle["distance"] * math.sin(particle["angle"]))
            dist_to_target = math.hypot(dx, dy)

            if dist_to_target > 15: # Move until close
                # Move particle directly towards target
                move_speed = 8 # Adjust convergence speed
                particle["angle"] = math.atan2(dy, dx) # Point towards target (less relevant now)
                # Update distance directly based on speed towards target
                particle["distance"] = max(0, particle["distance"] - move_speed) # Move inward
                # Or update x/y directly:
                # current_x = center_x + particle["distance"] * math.cos(particle["angle"])
                # current_y = center_y + particle["distance"] * math.sin(particle["angle"])
                # current_x += (dx / dist_to_target) * move_speed
                # current_y += (dy / dist_to_target) * move_speed
                # # Recalculate angle/distance if needed, or just use x/y (simpler)
                # particle["x"] = current_x # Need to store x/y if not using angle/dist
                # particle["y"] = current_y

            else:
                # Particle reached target, mark for removal and explosion
                particles_to_remove.append(particle)
                continue
        else:
            # --- Normal Swirling Motion ---
            particle["angle"] += particle["rotation_speed"]
            # Pulsing distance effect
            pulse = math.sin(current_time_ms * 0.001 * particle["pulse_speed"] + particle["pulse_offset"]) * 20 # Pulse magnitude
            particle["distance"] = particle["base_distance"] + pulse


        # Calculate particle position (common for both modes)
        x = center_x + particle["distance"] * math.cos(particle["angle"])
        y = center_y + particle["distance"] * math.sin(particle["angle"])

        # Draw particle with glow effect
        glow_radius = particle["radius"] * 1.5
        glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*particle["color"], 60), (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surface, (int(x - glow_radius), int(y - glow_radius)))

        # Draw main particle
        pygame.draw.circle(screen, particle["color"], (int(x), int(y)), particle["radius"])


    # --- Handle Removed Particles (Reached Convergence Target) ---
    if particles_to_remove and convergence_target:
        target_x, target_y = convergence_target
        for particle in particles_to_remove:
            if particle in swirl_particles: # Ensure it wasn't already removed
                 swirl_particles.remove(particle)

            # Create mini-explosion effect at convergence point
            for _ in range(3): # Fewer particles per mini-explosion
                explosion_color = particle["color"]
                create_particle(
                    target_x + random.uniform(-5, 5),  # Slight spread
                    target_y + random.uniform(-5, 5),
                    explosion_color,
                    random.uniform(8, 16),  # Smaller explosion particles
                    random.uniform(-1.5, 1.5),
                    random.uniform(-1.5, 1.5),
                    random.randint(20, 40)
                )

        # Add a small shockwave effect once when particles hit
        if random.random() < 0.5: # Chance to add shockwave
             create_explosion(target_x, target_y, color=random.choice(FLAME_COLORS), max_radius=100, duration=20)


    # --- Reset Convergence State ---
    if particles_converging:
        convergence_timer -= 1
        if convergence_timer <= 0 or not swirl_particles: # Stop if timer runs out or no particles left
            particles_converging = False
            convergence_target = None
            # Optionally regenerate particles if too few remain
            if len(swirl_particles) < 20:
                 create_swirl_particles(center_x, center_y, count=30) # Regenerate some


def trigger_particle_convergence(target_x, target_y):
    """Triggers swirling particles to converge toward a target point."""
    global particles_converging, convergence_target, convergence_timer
    if not particles_converging: # Prevent re-triggering while already converging
        particles_converging = True
        convergence_target = (target_x, target_y)
        convergence_timer = 30  # Duration for convergence (frames)

        # Optional: Add a visual pulse from center towards target
        # dx = target_x - (WIDTH // 2)
        # dy = target_y - (HEIGHT // 2)
        # dist = math.hypot(dx, dy)
        # if dist > 0:
        #     for i in range(5):
        #         particles.append({
        #             "x": WIDTH // 2, "y": HEIGHT // 2,
        #             "color": random.choice(FLAME_COLORS),
        #             "size": random.uniform(4, 8),
        #             "dx": (dx / dist) * (5 + i), # Pulse outwards towards target
        #             "dy": (dy / dist) * (5 + i),
        #             "duration": 15, "start_duration": 15
        #         })

def get_particle_from_pool():
    """Legacy function that now uses the particle manager."""
    return particle_manager.get_particle()

def release_particle(particle):
    """Legacy function that now uses the particle manager."""
    particle_manager.release_particle(particle)

def create_particle(x, y, color, size, dx, dy, duration):
    """Legacy function that now uses the particle manager."""
    return particle_manager.create_particle(x, y, color, size, dx, dy, duration)

def create_crack(x, y):
    """Creates a crack effect at the given position."""
    global glass_cracks, background_shattered, shatter_timer, opposite_background, current_background, game_over_triggered, game_over_delay
    
    # Create a new crack with random properties
    segments = random.randint(4, 8)  # Number of line segments in the crack
    length = random.randint(40, 80)  # Length of each segment
    spread_angle = random.uniform(10, 40)  # Max deviation angle between segments
    
    # Start with a random direction
    main_angle = random.uniform(0, 360)
    
    # Generate crack segments
    points = [(x, y)]  # Start point
    current_angle = main_angle
    
    for _ in range(segments):
        # Vary the angle slightly
        angle_variation = random.uniform(-spread_angle, spread_angle)
        current_angle += angle_variation
        
        # Calculate next point
        rad_angle = math.radians(current_angle)
        segment_length = random.uniform(0.7, 1.3) * length
        next_x = points[-1][0] + math.cos(rad_angle) * segment_length
        next_y = points[-1][1] + math.sin(rad_angle) * segment_length
        
        points.append((next_x, next_y))
    
    # Add thin branches occasionally
    if random.random() < 0.7:  # 70% chance to add branches
        num_branches = random.randint(1, 3)
        branch_points = []
        
        for _ in range(num_branches):
            # Pick a random segment to branch from
            branch_from = random.randint(0, len(points) - 2)
            branch_angle = current_angle + random.uniform(30, 150)  # Significant deviation
            
            # Create branch segments
            branch_segments = random.randint(2, 4)
            branch_points.append([points[branch_from]])  # Start point
            current_branch_angle = branch_angle
            
            for _ in range(branch_segments):
                angle_variation = random.uniform(-spread_angle, spread_angle)
                current_branch_angle += angle_variation
                
                rad_angle = math.radians(current_branch_angle)
                segment_length = random.uniform(0.4, 0.7) * length  # Branches are shorter
                next_x = branch_points[-1][-1][0] + math.cos(rad_angle) * segment_length
                next_y = branch_points[-1][-1][1] + math.sin(rad_angle) * segment_length
                
                branch_points[-1].append((next_x, next_y))
    else:
        branch_points = []
    
    # Determine the effective background and crack color for drawing
    effective_background = opposite_background if background_shattered else current_background
    draw_crack_color = WHITE if effective_background == BLACK else BLACK
    
    # Add the crack
    glass_cracks.append({
        "points": points,
        "branches": branch_points,
        "width": random.uniform(1, 3),  # Line width
        "alpha": 200,  # Starting opacity
        "color": draw_crack_color
    })
    
    # Check if we've reached the maximum number of cracks to shatter
    if len(glass_cracks) >= MAX_CRACKS and not game_over_triggered:
        # Swap backgrounds
        background_shattered = True
        shatter_timer = CRACK_DURATION
        
        # Swap current and opposite backgrounds
        current_background, opposite_background = opposite_background, current_background
        
        # Set flag for game over but with delay to show animation first
        game_over_triggered = True
        game_over_delay = GAME_OVER_DELAY_FRAMES
        
        # Create shatter particles
        shatter_count = 200  # More particles for dramatic effect
        for _ in range(shatter_count):
            # Create glass particle
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 10)
            create_particle(
                WIDTH/2 + random.uniform(-WIDTH/3, WIDTH/3),  # Spread across screen
                HEIGHT/2 + random.uniform(-HEIGHT/3, HEIGHT/3),
                (200, 200, 200),  # Glass color
                random.uniform(5, 15),  # Size
                math.cos(angle) * speed,  # X velocity
                math.sin(angle) * speed,  # Y velocity
                random.randint(60, 120)  # Longer duration for animation to be visible
            )

def draw_cracks(surface):
    """Draws all cracks on the surface."""
    global glass_cracks, background_shattered, shatter_timer, opposite_background, current_background
    
    # If screen is shattered, count down the timer
    if background_shattered:
        # Fill with opposite background color
        surface.fill(opposite_background)
        
        # Decrease timer
        shatter_timer -= 1
        if shatter_timer <= 0:
            # Reset shattered state but keep cracks (cracks are reset in create_crack)
            background_shattered = False
            
            # Switch the background colors
            current_background, opposite_background = opposite_background, current_background
            
            # # If we have enough cracks, clear them to start fresh (REMOVED - Handled in create_crack)
            # if len(glass_cracks) >= MAX_CRACKS:
            #     glass_cracks = []
    
    # Determine the effective background and crack color for drawing
    effective_background = opposite_background if background_shattered else current_background
    draw_crack_color = WHITE if effective_background == BLACK else BLACK
    
    # Draw all cracks
    for crack in glass_cracks:
        # Draw main segments
        for i in range(len(crack["points"]) - 1):
            pygame.draw.line(
                surface, 
                draw_crack_color, # Use dynamic color
                crack["points"][i], 
                crack["points"][i+1], 
                int(crack["width"])
            )
        
        # Draw branches
        for branch in crack["branches"]:
            for i in range(len(branch) - 1):
                pygame.draw.line(
                    surface, 
                    draw_crack_color, # Use dynamic color
                    branch[i], 
                    branch[i+1], 
                    int(crack["width"] * 0.7)  # Branches are thinner
                )

def create_explosion(x, y, color=None, max_radius=270, duration=30):
    """Adds an explosion effect to the list, with a limit for performance."""
    global shake_duration, explosions
    
    # Limit number of explosions for performance
    if len(explosions) >= MAX_EXPLOSIONS:
        # If we've reached the limit, replace the oldest explosion
        oldest_explosion = min(explosions, key=lambda exp: exp["duration"])
        explosions.remove(oldest_explosion)
    
    if color is None:
        color = random.choice(FLAME_COLORS)
        
    explosions.append({
        "x": x,
        "y": y,
        "radius": 10, # Start small
        "color": color,
        "max_radius": max_radius,
        "duration": duration,
        "start_duration": duration # Store initial duration for fading
    })
    
    shake_duration = max(shake_duration, 10) # Trigger screen shake, don't override longer shakes

def handle_misclick(x, y):
    """Handle a click that wasn't on a valid target."""
    global shake_duration, shake_magnitude
    shake_duration = SHAKE_DURATION_MISCLICK
    shake_magnitude = SHAKE_MAGNITUDE_MISCLICK
    create_crack(x, y)

def draw_explosion(explosion, offset_x=0, offset_y=0):
    """Draws a single explosion frame, expanding and fading."""
    # Expand radius towards max_radius
    explosion["radius"] += (explosion["max_radius"] - explosion["radius"]) * 0.1 # Smoother expansion
    # Calculate alpha based on remaining duration
    alpha = max(0, int(255 * (explosion["duration"] / explosion["start_duration"])))
    color = (*explosion["color"][:3], alpha) # Add alpha to color
    radius = int(explosion["radius"])
    # Apply shake offset
    draw_x = int(explosion["x"] + offset_x)
    draw_y = int(explosion["y"] + offset_y)

    # Draw using SRCALPHA surface for transparency
    if radius > 0:
        explosion_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(explosion_surf, color, (radius, radius), radius)
        screen.blit(explosion_surf, (draw_x - radius, draw_y - radius))

def create_flame_effect(start_x, start_y, end_x, end_y):
    """Creates a laser/flame visual effect between two points."""
    global lasers
    # Always use flamethrower effect for now
    effect = LASER_EFFECTS[0] # Force flamethrower
    lasers.append({
        "start_pos": (start_x, start_y),
        "end_pos": (end_x, end_y),
        "colors": effect["colors"],
        "widths": effect["widths"], # Used by draw_flamethrower indirectly
        "duration": 10, # Short duration visual effect
        "type": effect["type"],
    })

def draw_flamethrower(laser, offset_x=0, offset_y=0):
    """Draws a flamethrower style effect using circles along a line."""
    start_x, start_y = laser["start_pos"]
    end_x, end_y = laser["end_pos"]
    dx = end_x - start_x
    dy = end_y - start_y
    length = math.hypot(dx, dy)
    if length == 0: return # Avoid division by zero

    angle = math.atan2(dy, dx)
    num_circles = int(length / 10) # Draw a circle every 10 pixels

    for i in range(num_circles):
        # Interpolate position along the line
        ratio = i / num_circles
        x = start_x + dx * ratio
        y = start_y + dy * ratio
        # Vary radius and color for flame effect
        radius = random.randint(20, 40 + int(20 * (1-ratio))) # Wider near start
        color = random.choice(laser["colors"])
        # Apply shake offset
        draw_x = int(x + offset_x)
        draw_y = int(y + offset_y)
        # Draw with alpha for softer edges (optional)
        flame_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(flame_surf, (*color, 180), (radius, radius), radius)
        screen.blit(flame_surf, (draw_x - radius, draw_y - radius))

def game_over_screen():
    """Screen shown when player breaks the screen completely."""
    flash = True
    flash_count = 0
    running = True
    clock = pygame.time.Clock()
    
    # Add click delay timer (5 seconds at 60 fps = 300 frames)
    click_delay = GAME_OVER_CLICK_DELAY
    click_enabled = False
    countdown_seconds = GAME_OVER_COUNTDOWN_SECONDS
    
    # Calculate sad face dimensions (70% of screen)
    face_radius = min(WIDTH, HEIGHT) * 0.35  # 70% diameter, so 35% radius
    face_center_x = WIDTH // 2
    face_center_y = HEIGHT // 2 - 50  # Slight offset to make room for text
    
    # Eye dimensions
    eye_radius = face_radius * 0.15
    eye_offset_x = face_radius * 0.2
    eye_offset_y = face_radius * 0.1
    
    # Mouth dimensions
    mouth_width = face_radius * 0.6
    mouth_height = face_radius * 0.3
    mouth_offset_y = face_radius * 0.15
    
    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()
            # Force click to continue, but only after delay expires
            if event.type == pygame.MOUSEBUTTONDOWN and click_enabled:
                running = False
                # Reset game state for next play
                global glass_cracks, background_shattered, game_over_triggered
                glass_cracks = []
                background_shattered = False
                game_over_triggered = False
                return True  # Return True to indicate we should go back to level menu
        
        # Draw sad face (70% of screen)
        pygame.draw.circle(screen, WHITE, (face_center_x, face_center_y), int(face_radius), 5)
        
        # Draw eyes (X marks)
        left_eye_x = face_center_x - eye_offset_x
        right_eye_x = face_center_x + eye_offset_x
        eye_y = face_center_y - eye_offset_y
        
        # Left eye X
        pygame.draw.line(screen, WHITE, 
                        (left_eye_x - eye_radius, eye_y - eye_radius),
                        (left_eye_x + eye_radius, eye_y + eye_radius), 5)
        pygame.draw.line(screen, WHITE, 
                        (left_eye_x - eye_radius, eye_y + eye_radius),
                        (left_eye_x + eye_radius, eye_y - eye_radius), 5)
        
        # Right eye X
        pygame.draw.line(screen, WHITE, 
                        (right_eye_x - eye_radius, eye_y - eye_radius),
                        (right_eye_x + eye_radius, eye_y + eye_radius), 5)
        pygame.draw.line(screen, WHITE, 
                        (right_eye_x - eye_radius, eye_y + eye_radius),
                        (right_eye_x + eye_radius, eye_y - eye_radius), 5)
        
        # Draw sad mouth (upside down arc)
        mouth_rect = pygame.Rect(
            face_center_x - mouth_width // 2,
            face_center_y + mouth_offset_y,
            mouth_width,
            mouth_height
        )
        pygame.draw.arc(screen, WHITE, mouth_rect, 0, math.pi, 5)
        
        # Display "You broke the screen!" message
        game_over_font = fonts[2]  # Use one of the preloaded larger fonts
        game_over_text = game_over_font.render("You broke the screen!", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + face_radius + 50))
        screen.blit(game_over_text, game_over_rect)
        
        # Flashing "NEXT PLAYER!" text alternating between RED and WHITE
        next_player_color = (255, 0, 0) if flash else (255, 255, 255)  # RED and WHITE
        next_player_text = fonts[0].render("NEXT PLAYER!", True, next_player_color)
        next_player_rect = next_player_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + face_radius + 120))
        screen.blit(next_player_text, next_player_rect)
        
        # Update and display click delay countdown
        if click_delay > 0:
            click_delay -= 1
            current_second = countdown_seconds - (click_delay // 60)
            countdown_text = small_font.render(f"Please wait {max(1, current_second + 1)}...", True, (150, 150, 150))
            click_rect = countdown_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + face_radius + 180))
            screen.blit(countdown_text, click_rect)
        else:
            click_enabled = True
            click_text = small_font.render("Click to continue", True, (150, 150, 150))
            click_rect = click_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + face_radius + 180))
            screen.blit(click_text, click_rect)
        
        pygame.display.flip()
        flash_count += 1
        if flash_count % 15 == 0:  # Flash faster (twice per second)
            flash = not flash
        clock.tick(60)
    
    return False  # Should not be reached if click is required

if __name__ == "__main__":
    welcome_screen()
    current_mode = None 
    while True:
        if not current_mode: 
            current_mode = level_menu()
        
        if current_mode is None: 
            print("Exiting via level menu.")
            break
        
        status = game_loop(current_mode) 
        
        print(f"Level '{current_mode}' returned status: {status}")

        if status == "QUIT":
            print("Quit status received. Exiting game.")
            break
        elif status == "LEVEL_MENU":
            current_mode = None # Go back to level menu
            continue
        elif status == "WELL_DONE":
            # Call the global well_done_screen if it exists and is appropriate here
            # For now, just print and go back to menu
            if 'well_done_screen' in game_globals_for_main_loop: # Requires game_globals to be accessible
                 game_globals_for_main_loop['well_done_screen'](0) # Assuming score 0 or get it from somewhere
            else:
                 print("Well Done screen function not found in this context.")
            print(f"Level '{current_mode}' completed (WELL_DONE). Returning to menu.")
            current_mode = None
            continue
        elif status == "ERROR":
            print(f"Level '{current_mode}' reported an error. Returning to menu.")
            current_mode = None
            continue
        elif status == "CHECKPOINT_SHAPES":
            print(f"Checkpoint for Shapes level. Showing checkpoint screen.")
            # Assuming checkpoint_screen is globally accessible or part of a context
            # And that it returns True to continue the level, False to go to menu.
            if 'checkpoint_screen' in game_globals_for_main_loop:
                if game_globals_for_main_loop['checkpoint_screen']("shapes"):
                    # User chose to continue shapes level, current_mode remains "shapes"
                    print("Continuing Shapes level after checkpoint.")
                    # The ShapesLevel run method will call initialize_level() again.
                    # No need to re-call game_loop(current_mode) immediately, 
                    # the loop will continue with current_mode = "shapes"
                else:
                    print("User chose menu from shapes checkpoint.")
                    current_mode = None # Go to level menu
            else:
                print("Checkpoint screen function not found. Returning to menu.")
                current_mode = None
            continue
        elif status is False and (current_mode == "shapes" or current_mode == "colors"): # Legacy handling
            print(f"Legacy restart for {current_mode}. This logic needs an update. Returning to menu.")
            current_mode = None
            continue
        elif status is None:
             print(f"Warning: Level '{current_mode}' returned None status. Returning to menu.")
             current_mode = None
             continue
        else: # Unknown status or a boolean True that might have meant restart in old code
            print(f"Unknown or unhandled status '{status}' from level '{current_mode}'. Returning to menu.")
            current_mode = None
            continue

    print("Game exited.")
    pygame.quit()

# It would be better if game_globals were properly scoped or passed to where __main__ can use it.
# For now, this is a conceptual placeholder for accessing functions like well_done_screen/checkpoint_screen.
# A proper game manager class would handle this more cleanly.
game_globals_for_main_loop = {
    "well_done_screen": well_done_screen, 
    "checkpoint_screen": checkpoint_screen
} if 'well_done_screen' in globals() and 'checkpoint_screen' in globals() else {}