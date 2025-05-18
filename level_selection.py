import pygame
import random
import math

# Assume these will be passed or imported from a central place:
# screen, WIDTH, HEIGHT, FLAME_COLORS, BLACK, WHITE, small_font

def draw_neon_button_level_select(screen, rect, base_color): # Renamed to avoid conflict if another file has a similar one
    """Draws a button with a neon glow effect."""
    pygame.draw.rect(screen, (20, 20, 20), rect)
    for i in range(1, 6):
        neon_rect = pygame.Rect(rect.x - i, rect.y - i, rect.width + 2*i, rect.height + 2*i)
        pygame.draw.rect(screen, base_color, neon_rect, 1)
    pygame.draw.rect(screen, base_color, rect, 2)

def level_menu_content(screen, WIDTH, HEIGHT, FLAME_COLORS, BLACK, WHITE, get_small_font_func):
    """Display the Level Options screen to choose the mission using a cyberpunk neon display."""
    small_font = get_small_font_func()
    running = True
    clock = pygame.time.Clock()
    
    button_width = 300
    button_height = 80
    abc_rect = pygame.Rect((WIDTH // 2 - button_width - 20, HEIGHT // 2 - button_height - 10), (button_width, button_height))
    num_rect = pygame.Rect((WIDTH // 2 + 20, HEIGHT // 2 - button_height - 10), (button_width, button_height))
    shapes_rect = pygame.Rect((WIDTH // 2 - button_width - 20, HEIGHT // 2 + 10), (button_width, button_height))
    clcase_rect = pygame.Rect((WIDTH // 2 + 20, HEIGHT // 2 + 10), (button_width, button_height))
    colors_rect = pygame.Rect((WIDTH // 2 - 150, HEIGHT // 2 + 120), (300, 80))

    color_transition = 0.0
    current_color = FLAME_COLORS[0]
    next_color = FLAME_COLORS[1]

    particle_colors = [
        (255, 0, 128), (0, 255, 128), (128, 0, 255),
        (255, 128, 0), (0, 128, 255)
    ]

    repel_particles = []
    for _ in range(700): # Reduced from 700 to manage particle load, was 700
        angle = random.uniform(0, math.pi * 2)
        distance = random.uniform(10, 100)
        x = WIDTH // 2 + math.cos(angle) * distance
        y = HEIGHT // 2 + math.sin(angle) * distance
        repel_particles.append({
            "x": x, "y": y, "color": random.choice(particle_colors),
            "size": random.randint(5, 7), "speed": random.uniform(3.0, 6.0),
            "angle": angle
        })

    pygame.time.delay(100)

    selected_level = None
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
                    selected_level = "alphabet"
                    running = False
                elif num_rect.collidepoint(mx, my):
                    selected_level = "numbers"
                    running = False
                elif shapes_rect.collidepoint(mx, my):
                    selected_level = "shapes"
                    running = False
                elif clcase_rect.collidepoint(mx, my):
                    selected_level = "clcase"
                    running = False
                elif colors_rect.collidepoint(mx, my):
                    selected_level = "colors"
                    running = False
        
        if not running: # Exit loop if a level was selected
            break

        for particle in repel_particles:
            particle["x"] += math.cos(particle["angle"]) * particle["speed"]
            particle["y"] += math.sin(particle["angle"]) * particle["speed"]

            if (particle["x"] < 0 or particle["x"] > WIDTH or
                particle["y"] < 0 or particle["y"] > HEIGHT):
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(5, 50)
                particle["x"] = WIDTH // 2 + math.cos(angle) * distance
                particle["y"] = HEIGHT // 2 + math.sin(angle) * distance
                particle["angle"] = angle
                particle["color"] = random.choice(particle_colors)
                particle["size"] = random.randint(13, 17)
                particle["speed"] = random.uniform(1.0, 3.0)

            pygame.draw.circle(screen, particle["color"],
                              (int(particle["x"]), int(particle["y"])),
                              particle["size"])

        color_transition += 0.01
        if color_transition >= 1:
            color_transition = 0
            current_color = next_color
            next_color = random.choice(FLAME_COLORS)
        r = int(current_color[0] * (1 - color_transition) + next_color[0] * color_transition)
        g = int(current_color[1] * (1 - color_transition) + next_color[1] * color_transition)
        b = int(current_color[2] * (1 - color_transition) + next_color[2] * color_transition)
        title_color = (r, g, b)

        title_text_surf = small_font.render("Choose Mission:", True, title_color) # Renamed
        title_rect = title_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
        screen.blit(title_text_surf, title_rect)

        draw_neon_button_level_select(screen, abc_rect, (255, 0, 150))
        abc_text_surf = small_font.render("A B C", True, WHITE) # Renamed
        abc_text_rect = abc_text_surf.get_rect(center=abc_rect.center)
        screen.blit(abc_text_surf, abc_text_rect)

        draw_neon_button_level_select(screen, num_rect, (0, 200, 255))
        num_text_surf = small_font.render("1 2 3", True, WHITE) # Renamed
        num_text_rect = num_text_surf.get_rect(center=num_rect.center)
        screen.blit(num_text_surf, num_text_rect)

        draw_neon_button_level_select(screen, shapes_rect, (0, 255, 0))
        shapes_text_surf = small_font.render("Shapes", True, WHITE) # Renamed
        shapes_text_rect = shapes_text_surf.get_rect(center=shapes_rect.center)
        screen.blit(shapes_text_surf, shapes_text_rect)

        draw_neon_button_level_select(screen, clcase_rect, (255, 255, 0))
        clcase_text_surf = small_font.render("C/L Case", True, WHITE) # Renamed
        clcase_text_rect = clcase_text_surf.get_rect(center=clcase_rect.center)
        screen.blit(clcase_text_surf, clcase_text_rect)

        draw_neon_button_level_select(screen, colors_rect, (128, 0, 255))
        colors_text_surf = small_font.render("Colors", True, WHITE) # Renamed
        colors_text_rect = colors_text_surf.get_rect(center=colors_rect.center)
        screen.blit(colors_text_surf, colors_text_rect)

        pygame.display.flip()
        clock.tick(60)
        
    return selected_level 