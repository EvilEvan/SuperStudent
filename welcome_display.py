import pygame
import random
import math

# Imports that will be needed from the main file or a new 'core' module
# For now, assume they are passed or will be imported from a central place
# screen, WIDTH, HEIGHT, FLAME_COLORS, BLACK, WHITE, init_resources, small_font, detect_display_type, DEBUG_MODE, SHOW_FPS

def welcome_screen_content(screen, WIDTH, HEIGHT, FLAME_COLORS, BLACK, WHITE, init_resources_func, get_small_font_func, detect_display_type_func, get_debug_settings_func, get_display_mode_func, set_display_mode_func):
    """Show the welcome screen with display size options."""
    
    # Get necessary resources/settings via passed functions
    small_font = get_small_font_func()
    DEBUG_MODE, SHOW_FPS = get_debug_settings_func()
    # DISPLAY_MODE will be managed by the set_display_mode_func and get_display_mode_func

    # Calculate scaling factor based on current screen size
    base_height = 1080
    scale_factor = HEIGHT / base_height
    
    title_offset = int(50 * scale_factor)
    button_width = int(200 * scale_factor)
    button_height = int(60 * scale_factor)
    button_spacing = int(20 * scale_factor)
    button_y_pos = int(200 * scale_factor)
    instruction_y_pos = int(150 * scale_factor)
    
    particle_colors = [
        (255, 0, 128), (0, 255, 128), (128, 0, 255),
        (255, 128, 0), (0, 128, 255)
    ]
    
    particles = []
    for _ in range(120):
        angle = random.uniform(0, math.pi * 2)
        distance = random.uniform(200, max(WIDTH, HEIGHT) * 0.4)
        x = WIDTH // 2 + math.cos(angle) * distance
        y = HEIGHT // 2 + math.sin(angle) * distance
        size = random.randint(int(9 * scale_factor), int(15 * scale_factor))
        particles.append({
            "x": x, "y": y, "color": random.choice(particle_colors),
            "size": size, "orig_size": size, "angle": angle,
            "orbit_speed": random.uniform(0.0005, 0.002),
            "orbit_distance": distance,
            "pulse_speed": random.uniform(0.02, 0.06),
            "pulse_factor": random.random()
        })
    
    default_hover = False
    qboard_hover = False
    
    default_button = pygame.Rect((WIDTH // 2 - button_width - button_spacing, HEIGHT // 2 + button_y_pos), (button_width, button_height))
    qboard_button = pygame.Rect((WIDTH // 2 + button_spacing, HEIGHT // 2 + button_y_pos), (button_width, button_height))
    
    color_transition = 0.0
    color_transition_speed = 0.01
    current_color = random.choice(FLAME_COLORS)
    next_color = random.choice(FLAME_COLORS)
    
    collab_font_size = int(100 * scale_factor)
    collab_font = pygame.font.Font(None, collab_font_size)
    
    title_font_size = int(320 * scale_factor)
    title_font = pygame.font.Font(None, title_font_size)
    
    title_offset_y = 0
    title_float_speed = 0.002
    title_float_direction = 1
    
    detected_display = detect_display_type_func()
    
    running = True
    clock = pygame.time.Clock()
    last_time = pygame.time.get_ticks()
    
    new_display_mode = None

    while running:
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - last_time) / 1000.0
        last_time = current_time
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if default_button.collidepoint(mx, my):
                    new_display_mode = "DEFAULT"
                    set_display_mode_func(new_display_mode)
                    init_resources_func()
                    running = False
                elif qboard_button.collidepoint(mx, my):
                    new_display_mode = "QBOARD"
                    set_display_mode_func(new_display_mode)
                    init_resources_func()
                    running = False
        
        mx, my = pygame.mouse.get_pos()
        default_hover = default_button.collidepoint(mx, my)
        qboard_hover = qboard_button.collidepoint(mx, my)
        
        color_transition += color_transition_speed * delta_time * 60
        if color_transition >= 1.0:
            color_transition = 0.0
            current_color = next_color
            next_color = random.choice([c for c in FLAME_COLORS if c != current_color])
        
        r = int(current_color[0] * (1 - color_transition) + next_color[0] * color_transition)
        g = int(current_color[1] * (1 - color_transition) + next_color[1] * color_transition)
        b = int(current_color[2] * (1 - color_transition) + next_color[2] * color_transition)
        title_color = (r, g, b)
        
        title_offset_y += title_float_direction * title_float_speed * delta_time * 60
        if abs(title_offset_y) > 10:
            title_float_direction *= -1
        
        for particle in particles:
            particle["angle"] += particle["orbit_speed"] * delta_time * 60
            particle["x"] = WIDTH // 2 + math.cos(particle["angle"]) * particle["orbit_distance"]
            particle["y"] = HEIGHT // 2 + math.sin(particle["angle"]) * particle["orbit_distance"]
            
            particle["pulse_factor"] += particle["pulse_speed"] * delta_time * 60
            if particle["pulse_factor"] > 1.0: particle["pulse_factor"] = 0.0
            pulse = 0.7 + 0.3 * math.sin(particle["pulse_factor"] * math.pi * 2)
            particle["size"] = particle["orig_size"] * pulse
        
        screen.fill(BLACK)
        
        for particle in particles:
            pygame.draw.circle(screen, particle["color"],
                             (int(particle["x"]), int(particle["y"])),
                             int(particle["size"]))
        
        title_rect_center = (WIDTH // 2, HEIGHT // 2 - title_offset + title_offset_y)
        
        title_text_val = "Super Student" # Renamed from title_text to avoid conflict
        shadow_color_val = (20, 20, 20) # Renamed
        for depth in range(1, 0, -1): # Adjusted range
            shadow = title_font.render(title_text_val, True, shadow_color_val)
            shadow_rect = shadow.get_rect(center=(title_rect_center[0] + depth, title_rect_center[1] + depth))
            screen.blit(shadow, shadow_rect)
        
        glow_colors = [(r//2, g//2, b//2), (r//3, g//3, b//3)]
        for i, glow_color in enumerate(glow_colors):
            glow = title_font.render(title_text_val, True, glow_color)
            offset = i + 1
            for dx, dy in [(-offset,0), (offset,0), (0,-offset), (0,offset)]:
                glow_rect = glow.get_rect(center=(title_rect_center[0] + dx, title_rect_center[1] + dy))
                screen.blit(glow, glow_rect)
        
        highlight_color = (min(r+80, 255), min(g+80, 255), min(b+80, 255))
        shadow_color_title = (max(r-90, 0), max(g-90, 0), max(b-90, 0)) # Renamed
        mid_color = (max(r-40, 0), max(g-40, 0), max(b-40, 0))
        
        highlight = title_font.render(title_text_val, True, highlight_color)
        highlight_rect = highlight.get_rect(center=(title_rect_center[0] - 4, title_rect_center[1] - 4))
        screen.blit(highlight, highlight_rect)
        
        mid_tone = title_font.render(title_text_val, True, mid_color)
        mid_rect = mid_tone.get_rect(center=(title_rect_center[0] + 2, title_rect_center[1] + 2))
        screen.blit(mid_tone, mid_rect)
        
        inner_shadow = title_font.render(title_text_val, True, shadow_color_title)
        inner_shadow_rect = inner_shadow.get_rect(center=(title_rect_center[0] + 4, title_rect_center[1] + 4))
        screen.blit(inner_shadow, inner_shadow_rect)
        
        title_surf = title_font.render(title_text_val, True, title_color) # Renamed
        title_rect = title_surf.get_rect(center=title_rect_center)
        screen.blit(title_surf, title_rect)
        
        display_text_surf = small_font.render("Choose Display Size:", True, WHITE) # Renamed
        display_rect = display_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + instruction_y_pos))
        screen.blit(display_text_surf, display_rect)
        
        pygame.draw.rect(screen, (20, 20, 20), default_button)
        glow_intensity_default = 6 if default_hover else 5 # Renamed
        for i in range(1, glow_intensity_default): # Use renamed var
            multiplier = 1.5 if default_hover else 1.0
            alpha_factor = (1 - i/glow_intensity_default) * multiplier # Use renamed var
            glow_color_default = (0, min(int(200 + 55 * default_hover * alpha_factor), 255), 255) # Renamed
            default_rect_glow = pygame.Rect(default_button.x - i, default_button.y - i, default_button.width + 2*i, default_button.height + 2*i) 
            pygame.draw.rect(screen, glow_color_default, default_rect_glow, 1) # Use renamed var
        border_width_default = 3 if default_hover else 2 # Renamed
        pygame.draw.rect(screen, (0, 200, 255), default_button, border_width_default) # Use renamed var
        default_text_surf = small_font.render("Default", True, WHITE) 
        default_text_rect = default_text_surf.get_rect(center=default_button.center)
        screen.blit(default_text_surf, default_text_rect)
        
        pygame.draw.rect(screen, (20, 20, 20), qboard_button)
        glow_intensity_qboard = 6 if qboard_hover else 5 # Renamed
        for i in range(1, glow_intensity_qboard): # Use renamed var
            multiplier = 1.5 if qboard_hover else 1.0
            alpha_factor = (1 - i/glow_intensity_qboard) * multiplier # Use renamed var
            glow_color_qboard = (min(int(255 * multiplier * alpha_factor), 255), 0, min(int(150 * multiplier * alpha_factor), 255)) # Renamed
            qboard_rect_glow = pygame.Rect(qboard_button.x - i, qboard_button.y - i, qboard_button.width + 2*i, qboard_button.height + 2*i)
            pygame.draw.rect(screen, glow_color_qboard, qboard_rect_glow, 1) # Use renamed var
        border_width_qboard = 3 if qboard_hover else 2 # Renamed
        pygame.draw.rect(screen, (255, 0, 150), qboard_button, border_width_qboard) # Use renamed var
        qboard_text_surf = small_font.render("QBoard", True, WHITE) 
        qboard_text_rect = qboard_text_surf.get_rect(center=qboard_button.center)
        screen.blit(qboard_text_surf, qboard_text_rect)
        
        auto_text_color = (200, 200, 200)
        if detected_display == "DEFAULT" and default_hover:
            pulse_auto = 0.5 + 0.5 * math.sin(current_time * 0.005) # Renamed
            auto_text_color = (0, int(200 + 55 * pulse_auto), 255) # Use renamed var
        elif detected_display == "QBOARD" and qboard_hover:
            pulse_auto = 0.5 + 0.5 * math.sin(current_time * 0.005) # Renamed
            auto_text_color = (255, 0, int(150 * pulse_auto)) # Use renamed var
        
        auto_text_surf = small_font.render(f"Auto-detected: {detected_display}", True, auto_text_color) 
        auto_rect = auto_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + button_y_pos + button_height + 30))
        screen.blit(auto_text_surf, auto_rect)
        
        pulse_factor_sangsom = 0.5 + 0.5 * math.sin(current_time * 0.002) 
        bright_yellow = (255, 255, 0)
        lite_yellow = (255, 255, 150)
        sangsom_color = tuple(int(bright_yellow[j] * (1 - pulse_factor_sangsom) + lite_yellow[j] * pulse_factor_sangsom) for j in range(3))
        
        collab_text1_surf = collab_font.render("In collaboration with ", True, WHITE) 
        collab_text2_surf = collab_font.render("SANGSOM", True, sangsom_color) 
        collab_text3_surf = collab_font.render(" Kindergarten", True, WHITE) 
        
        collab_rect1 = collab_text1_surf.get_rect()
        collab_rect1.right = WIDTH // 2 - collab_text2_surf.get_width() // 2
        collab_rect1.centery = HEIGHT // 2 + int(350 * scale_factor)
        
        collab_rect2 = collab_text2_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + int(350 * scale_factor)))
        
        collab_rect3 = collab_text3_surf.get_rect()
        collab_rect3.left = collab_rect2.right
        collab_rect3.centery = HEIGHT // 2 + int(350 * scale_factor)
        
        screen.blit(collab_text1_surf, collab_rect1)
        screen.blit(collab_text2_surf, collab_rect2)
        screen.blit(collab_text3_surf, collab_rect3)
        
        creator_float = 2 * math.sin(current_time * 0.001)
        creator_text_surf = small_font.render("Created by Teacher Evan and Teacher Lee", True, WHITE) 
        creator_rect = creator_text_surf.get_rect(center=(WIDTH // 2, HEIGHT - 40 + creator_float))
        screen.blit(creator_text_surf, creator_rect)
        
        if DEBUG_MODE and SHOW_FPS:
            fps = int(clock.get_fps())
            fps_text_surf = small_font.render(f"FPS: {fps}", True, WHITE) 
            screen.blit(fps_text_surf, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    return new_display_mode # Return the selected mode or None if exited early 