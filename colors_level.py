import pygame
import random
import math

# MAX_CRACKS would be imported from settings or passed if create_crack is externalized further
# from settings import MAX_CRACKS 

def run_colors_level(
    screen, WIDTH, HEIGHT, BLACK, WHITE, FLAME_COLORS,
    get_small_font_func, get_mother_radius_func, get_colors_collision_delay_func,
    create_explosion_func, 
    # handle_misclick_func, # handle_misclick logic will be internal or use create_crack_func
    create_crack_func, # New: direct crack creation
    checkpoint_screen_func,
    draw_cracks_func, draw_explosion_func, display_info_func, create_particle_func,
    game_over_screen_func,
    get_shake_vars_func, set_shake_vars_func,
    get_game_over_vars_func, set_game_over_vars_func,
    get_background_vars_func, set_background_vars_func, # For background state
    get_explosions_list_func, 
    get_active_touches_func, # Removed clear_active_touches_func, manage locally or via main loop
    get_glass_cracks_list_func, # get a mutable list
    settings_max_cracks # Pass MAX_CRACKS from settings
):
    """Runs the 'Colors' game level."""
    
    small_font = get_small_font_func()
    mother_radius = get_mother_radius_func()
    COLORS_COLLISION_DELAY = get_colors_collision_delay_func()
    
    COLORS_LIST = [
        (0, 0, 255), (255, 0, 0), (0, 200, 0),
        (255, 255, 0), (128, 0, 255),
    ]
    color_names = ["Blue", "Red", "Green", "Yellow", "Purple"]
    
    level_state = {
        "color_idx": random.randint(0, len(COLORS_LIST) - 1),
        "used_colors": [],
        "mother_color": None, "mother_color_name": "",
        "current_color_dots_destroyed": 0,
        "total_dots_destroyed": 0, # For checkpoint logic
        "target_dots_left": 10, 
        "score": 0,
        "overall_destroyed_count_for_display_info": 0,
        "ghost_notification": None,
        "dots_before_checkpoint": 0,
        "collision_enabled": False,
        "collision_delay_counter": 0,
        "dots": [],
        "checkpoint_trigger": 10,
    }
    level_state["used_colors"].append(level_state["color_idx"])
    level_state["mother_color"] = COLORS_LIST[level_state["color_idx"]]
    level_state["mother_color_name"] = color_names[level_state["color_idx"]]

    active_touches = get_active_touches_func() 
    explosions_list_ref = get_explosions_list_func() 
    glass_cracks_list_ref = get_glass_cracks_list_func()

    center = (WIDTH // 2, HEIGHT // 2)
    vibration_frames = 30
    clock = pygame.time.Clock()

    for _ in range(vibration_frames): # Corrected loop variable
        screen.fill(BLACK)
        vib_x = center[0] + random.randint(-6, 6)
        vib_y = center[1] + random.randint(-6, 6)
        pygame.draw.circle(screen, level_state["mother_color"], (vib_x, vib_y), mother_radius)
        label = small_font.render("Remember this color!", True, WHITE)
        label_rect = label.get_rect(center=(WIDTH // 2, HEIGHT // 2 + mother_radius + 60))
        screen.blit(label, label_rect)
        pygame.display.flip()
        clock.tick(50)

    waiting_for_dispersion = True
    while waiting_for_dispersion:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: pygame.quit(); return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                waiting_for_dispersion = False
        screen.fill(BLACK)
        pygame.draw.circle(screen, level_state["mother_color"], center, mother_radius)
        label = small_font.render("Remember this color!", True, WHITE)
        label_rect = label.get_rect(center=(WIDTH // 2, HEIGHT // 2 + mother_radius + 60))
        screen.blit(label, label_rect)
        prompt = small_font.render("Click to start!", True, (255, 255, 0))
        prompt_rect = prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + mother_radius + 120))
        screen.blit(prompt, prompt_rect)
        pygame.display.flip()
        clock.tick(50)

    disperse_particles_anim = []
    disperse_frames = 30
    for i in range(100):
        angle = random.uniform(0, 2 * math.pi)
        disperse_particles_anim.append({
            "angle": angle, "radius": 0, "speed": random.uniform(12, 18),
            "color": level_state["mother_color"] if i < 25 else None,
        })
    distractor_colors_list = [c for idx, c in enumerate(COLORS_LIST) if idx != level_state["color_idx"]]
    num_distractor_colors = len(distractor_colors_list)
    total_distractor_dots = 75
    dots_per_dist_color = total_distractor_dots // num_distractor_colors if num_distractor_colors > 0 else 0
    extra_dist_dots = total_distractor_dots % num_distractor_colors if num_distractor_colors > 0 else 0
    d_idx = 25
    for c_idx, color_val in enumerate(distractor_colors_list):
        count = dots_per_dist_color + (1 if c_idx < extra_dist_dots else 0)
        for _ in range(count):
            if d_idx < 100:
                disperse_particles_anim[d_idx]["color"] = color_val; d_idx += 1
    
    for _ in range(disperse_frames): # Corrected loop variable
        screen.fill(BLACK)
        for p_anim in disperse_particles_anim:
            p_anim["radius"] += p_anim["speed"]
            x_anim = int(center[0] + math.cos(p_anim["angle"]) * p_anim["radius"])
            y_anim = int(center[1] + math.sin(p_anim["angle"]) * p_anim["radius"])
            if p_anim["color"]:
                 pygame.draw.circle(screen, p_anim["color"], (x_anim, y_anim), 24)
        pygame.display.flip()
        clock.tick(50)
    
    level_state["dots"] = []
    for i in range(100):
        dot_color = disperse_particles_anim[i]["color"] if i < len(disperse_particles_anim) and disperse_particles_anim[i]["color"] else random.choice(COLORS_LIST)
        angle = random.uniform(0, 2 * math.pi)
        spread_radius_factor = 0.4 
        max_spread_radius = min(WIDTH, HEIGHT) * spread_radius_factor
        start_dist = random.uniform(mother_radius * 1.5, max_spread_radius) # Adjusted min spread
        x = center[0] + math.cos(angle) * start_dist + random.uniform(-50,50)
        y = center[1] + math.sin(angle) * start_dist + random.uniform(-50,50)
        x = max(24, min(WIDTH - 24, x)); y = max(24, min(HEIGHT - 24, y))
        level_state["dots"].append({
            "x": x, "y": y, "dx": random.uniform(-6, 6), "dy": random.uniform(-6, 6),
            "color": dot_color, "radius": 24,
            "target": True if dot_color == level_state["mother_color"] else False,
            "alive": True,
        })
    
    running = True
    while running:
        current_shake_duration, current_shake_magnitude = get_shake_vars_func()
        game_over_triggered, game_over_delay = get_game_over_vars_func()
        bg_vars_main = get_background_vars_func(False) # Main state, mutable
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False; pygame.quit(); return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False; pygame.quit(); return False
            
            event_pos = None; is_touch = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                event_pos = pygame.mouse.get_pos()
            elif event.type == pygame.FINGERDOWN:
                event_pos = (event.x * WIDTH, event.y * HEIGHT); is_touch = True
                active_touches[event.finger_id] = event_pos

            if event_pos:
                mx, my = event_pos; hit_target_flag = False
                for dot in level_state["dots"]:
                    if dot["alive"] and math.hypot(mx - dot["x"], my - dot["y"]) <= dot["radius"]:
                        hit_target_flag = True
                        if dot["target"]:
                            dot["alive"] = False
                            level_state["target_dots_left"] -= 1
                            level_state["score"] += 10
                            level_state["overall_destroyed_count_for_display_info"] += 1
                            level_state["current_color_dots_destroyed"] += 1
                            level_state["total_dots_destroyed"] += 1
                            create_explosion_func(explosions_list_ref, dot["x"], dot["y"], color=dot["color"], max_radius=60, duration=15)
                            
                            if level_state["current_color_dots_destroyed"] >= 5:
                                available_indices = [i for i in range(len(COLORS_LIST)) if i not in level_state["used_colors"]]
                                if not available_indices:
                                    level_state["used_colors"] = [level_state["color_idx"]]
                                    available_indices = [i for i in range(len(COLORS_LIST)) if i not in level_state["used_colors"]]
                                if available_indices:
                                    level_state["color_idx"] = random.choice(available_indices)
                                    level_state["used_colors"].append(level_state["color_idx"])
                                    level_state["mother_color"] = COLORS_LIST[level_state["color_idx"]]
                                    level_state["mother_color_name"] = color_names[level_state["color_idx"]]
                                    level_state["current_color_dots_destroyed"] = 0
                                    level_state["ghost_notification"] = {"color": level_state["mother_color"], "duration": 100, "alpha": 255, "radius": 150, "text": level_state["mother_color_name"]}
                                    for d_update in level_state["dots"]:
                                        if d_update["alive"]: d_update["target"] = (d_update["color"] == level_state["mother_color"])
                                    level_state["target_dots_left"] = sum(1 for d_sum in level_state["dots"] if d_sum["target"] and d_sum["alive"])
                            
                            if level_state["total_dots_destroyed"] > 0 and level_state["total_dots_destroyed"] % level_state["checkpoint_trigger"] == 0:
                                level_state["dots_before_checkpoint"] = level_state["target_dots_left"]
                                if not checkpoint_screen_func("colors", level_state): return False 
                                level_state["target_dots_left"] = level_state["dots_before_checkpoint"]
                                level_state["ghost_notification"] = {"color": level_state["mother_color"], "duration": 100, "alpha": 255, "radius": 150, "text": level_state["mother_color_name"]}
                        break 
                
                if not hit_target_flag:
                    # Simplified handle_misclick internal logic for colors_level
                    current_shake_duration = 10 # SHAKE_DURATION_MISCLICK
                    current_shake_magnitude = 5 # SHAKE_MAGNITUDE_MISCLICK
                    set_shake_vars_func(current_shake_duration, current_shake_magnitude)
                    
                    # Direct call to create_crack_func, which updates game_over_triggered via set_game_over_vars_func
                    create_crack_func(
                        glass_cracks_list_ref, mx, my, 
                        bg_vars_main, # Pass the whole dict
                        set_background_vars_func, # Allow create_crack to update background state
                        set_game_over_vars_func, # Allow create_crack to update game over state
                        settings_max_cracks,
                        explosions_list_ref, # create_explosion_func is also available if create_crack needs it
                        create_particle_func # Pass particle creator for shatter
                    )
                    # Re-fetch game_over_vars as they might have been changed
                    game_over_triggered, game_over_delay = get_game_over_vars_func()


            elif event.type == pygame.FINGERUP: # No is_touch check needed if FINGERUP
                if event.finger_id in active_touches:
                    del active_touches[event.finger_id]
        
        game_over_triggered, game_over_delay = get_game_over_vars_func() # Re-fetch
        if game_over_triggered:
            if game_over_delay > 0:
                game_over_delay -= 1; set_game_over_vars_func(game_over_triggered, game_over_delay)
            else:
                # Pass all necessary screen parameters to game_over_screen_func
                if game_over_screen_func(screen, WIDTH, HEIGHT, BLACK, WHITE, get_small_font_func, lambda: get_game_over_vars_func()[0]): # Example of passing a getter for a font
                    running = False; break
                else: # Should not be reached if click required
                    running = False; break 
        
        for dot in level_state["dots"]:
            if not dot["alive"]: continue
            dot["x"] += dot["dx"]; dot["y"] += dot["dy"]
            if dot["x"] - dot["radius"] < 0: dot["x"] = dot["radius"]; dot["dx"] *= -1
            if dot["x"] + dot["radius"] > WIDTH: dot["x"] = WIDTH - dot["radius"]; dot["dx"] *= -1
            if dot["y"] - dot["radius"] < 0: dot["y"] = dot["radius"]; dot["dy"] *= -1
            if dot["y"] + dot["radius"] > HEIGHT: dot["y"] = HEIGHT - dot["radius"]; dot["dy"] *= -1
        
        if not level_state["collision_enabled"]:
            level_state["collision_delay_counter"] += 1
            if level_state["collision_delay_counter"] >= COLORS_COLLISION_DELAY:
                level_state["collision_enabled"] = True; level_state["collision_delay_counter"] = 0
                for dot in level_state["dots"]:
                    if dot["alive"]: create_particle_func(dot["x"], dot["y"], dot["color"], dot["radius"] * 1.5, 0, 0, 15)
        
        if level_state["collision_enabled"]:
            for i, dot1 in enumerate(level_state["dots"]):
                if not dot1["alive"]: continue
                for j, dot2 in enumerate(level_state["dots"][i+1:], i+1):
                    if not dot2["alive"]: continue
                    dx_col = dot1["x"] - dot2["x"]; dy_col = dot1["y"] - dot2["y"]
                    distance = math.hypot(dx_col, dy_col)
                    if distance < (dot1["radius"] + dot2["radius"]):
                        nx, ny = (dx_col / distance, dy_col / distance) if distance > 0 else (1,0)
                        dvx = dot1["dx"] - dot2["dx"]; dvy = dot1["dy"] - dot2["dy"]
                        if dvx * nx + dvy * ny < 0:
                            overlap = (dot1["radius"] + dot2["radius"]) - distance
                            dot1["x"] += overlap/2 * nx; dot1["y"] += overlap/2 * ny
                            dot2["x"] -= overlap/2 * nx; dot2["y"] -= overlap/2 * ny
                            temp_dx, temp_dy = dot1["dx"], dot1["dy"]
                            dot1["dx"], dot1["dy"] = dot2["dx"] * 0.8, dot2["dy"] * 0.8
                            dot2["dx"], dot2["dy"] = temp_dx * 0.8, temp_dy * 0.8
                            for _ in range(3):
                                create_particle_func((dot1["x"] + dot2["x"]) / 2, (dot1["y"] + dot2["y"]) / 2, random.choice([dot1["color"], dot2["color"]]), random.randint(5, 10), random.uniform(-2,2), random.uniform(-2,2), 10)

        # Drawing section
        current_shake_duration, current_shake_magnitude = get_shake_vars_func()
        offset_x, offset_y = (random.randint(-current_shake_magnitude, current_shake_magnitude), random.randint(-current_shake_magnitude, current_shake_magnitude)) if current_shake_duration > 0 else (0,0)
        if current_shake_duration > 0: set_shake_vars_func(current_shake_duration - 1, current_shake_magnitude)

        bg_vars_draw = get_background_vars_func(True)
        screen.fill(bg_vars_draw["opposite_background"] if bg_vars_draw["background_shattered"] else bg_vars_draw["current_background"])
        draw_cracks_func(screen, glass_cracks_list_ref, bg_vars_draw["background_shattered"], bg_vars_draw["current_background"], bg_vars_draw["opposite_background"])

        for dot in level_state["dots"]:
            if dot["alive"]: pygame.draw.circle(screen, dot["color"], (int(dot["x"] + offset_x), int(dot["y"] + offset_y)), dot["radius"])
        
        current_explosions_list = explosions_list_ref[:]
        for exp_item in current_explosions_list:
            if exp_item["duration"] > 0:
                draw_explosion_func(screen, exp_item, offset_x, offset_y)
                # Duration decrement should be handled by draw_explosion_func or a shared update_effects func
            # else:
            #    if exp_item in explosions_list_ref: explosions_list_ref.remove(exp_item) # Also should be handled by an update_effects

        display_info_func(level_state["score"], "color", level_state["mother_color_name"], level_state["overall_destroyed_count_for_display_info"], level_state["target_dots_left"], "colors", level_state["current_color_dots_destroyed"], 5)
        pygame.draw.circle(screen, level_state["mother_color"], (WIDTH - 60, 60), 24)
        pygame.draw.rect(screen, WHITE, (WIDTH - 90, 30, 60, 60), 2)
        
        if not level_state["collision_enabled"]:
            screen.blit(small_font.render(f"Collisions in: {(COLORS_COLLISION_DELAY - level_state['collision_delay_counter']) // 50}s", True, WHITE), (10, HEIGHT - 30))
        
        if level_state["ghost_notification"] and level_state["ghost_notification"]["duration"] > 0:
            ghost_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            alpha = min(255, level_state["ghost_notification"]["alpha"])
            pygame.draw.circle(ghost_surf, level_state["ghost_notification"]["color"] + (alpha,), (WIDTH//2, HEIGHT//2), level_state["ghost_notification"]["radius"])
            ghost_font_render = pygame.font.Font(None, 48) # Should be passed or initialized once
            label_s = ghost_font_render.render("TARGET COLOR:", True, WHITE)
            label_r = label_s.get_rect(center=(WIDTH//2, HEIGHT//2 - level_state["ghost_notification"]["radius"] - 20))
            ghost_surf.blit(label_s, label_r)
            text_s = ghost_font_render.render(level_state["ghost_notification"]["text"], True, level_state["ghost_notification"]["color"])
            text_r = text_s.get_rect(center=(WIDTH//2, HEIGHT//2 + level_state["ghost_notification"]["radius"] + 30))
            ghost_surf.blit(text_s, text_r)
            screen.blit(ghost_surf, (0,0))
            level_state["ghost_notification"]["duration"] -= 1
            if level_state["ghost_notification"]["duration"] < 50: level_state["ghost_notification"]["alpha"] -= 5
        
        pygame.display.flip()
        clock.tick(50)
        
        if level_state["target_dots_left"] <= 0:
            new_dots_target_count = 10
            available_indices_regen = [i for i in range(len(COLORS_LIST)) if i not in level_state["used_colors"]]
            if not available_indices_regen:
                level_state["used_colors"] = [level_state["color_idx"]]
                available_indices_regen = [i for i in range(len(COLORS_LIST)) if i not in level_state["used_colors"]]
            if available_indices_regen:
                level_state["color_idx"] = random.choice(available_indices_regen)
                level_state["used_colors"].append(level_state["color_idx"])
                level_state["mother_color"] = COLORS_LIST[level_state["color_idx"]]
                level_state["mother_color_name"] = color_names[level_state["color_idx"]]
            
            level_state["ghost_notification"] = {"color": level_state["mother_color"], "duration": 100, "alpha": 255, "radius": 150, "text": level_state["mother_color_name"]}
            level_state["collision_enabled"] = False; level_state["collision_delay_counter"] = 0
            level_state["dots"] = [d for d in level_state["dots"] if d["alive"]]
            
            current_targets_alive = sum(1 for d in level_state["dots"] if d["color"] == level_state["mother_color"] and d["alive"])
            needed_target_colored_dots = max(0, new_dots_target_count - current_targets_alive)
            
            dots_to_add_count = 100 - len(level_state["dots"])

            for i_regen in range(dots_to_add_count):
                x_n, y_n = random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50) # Simplified placement
                
                new_dot_color_val = level_state["mother_color"] if i_regen < needed_target_colored_dots else random.choice([c for idx, c in enumerate(COLORS_LIST) if idx != level_state["color_idx"]] or [level_state["mother_color"]])
                is_target = new_dot_color_val == level_state["mother_color"]
                
                level_state["dots"].append({"x":x_n, "y":y_n, "dx":random.uniform(-6,6), "dy":random.uniform(-6,6), "color":new_dot_color_val, "radius":24, "target":is_target, "alive":True})

            current_target_dots_total = 0
            for d_scan in level_state["dots"]:
                if d_scan["alive"]:
                    d_scan["target"] = (d_scan["color"] == level_state["mother_color"])
                    if d_scan["target"]: current_target_dots_total +=1
            level_state["target_dots_left"] = current_target_dots_total
            
    return False 