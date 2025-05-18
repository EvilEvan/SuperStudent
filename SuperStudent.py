"""
Super Student - Glass Shatter Display

Description:
    This game features a dynamic 'Glass Shatter Display' effect. When the player makes a mistake (such as a misclick or mistap), a crack appears on the screen at the point of error. After a certain number of cracks, the entire background 'shatters' with a visual effect, swapping the background color and creating glass particle effects. This mechanic provides immediate visual feedback for mistakes and adds a dramatic, interactive element to the gameplay experience.

Date: 2024-06-09
"""
import pygame
import random
import math
from settings import (
    COLORS_COLLISION_DELAY, DISPLAY_MODES, DEFAULT_MODE, DISPLAY_SETTINGS_PATH,
    LEVEL_PROGRESS_PATH, MAX_CRACKS, WHITE, BLACK, FLAME_COLORS, LASER_EFFECTS,
    LETTER_SPAWN_INTERVAL, SEQUENCES, GAME_MODES, GROUP_SIZE,
    SHAKE_DURATION_MISCLICK, SHAKE_MAGNITUDE_MISCLICK,
    GAME_OVER_CLICK_DELAY, GAME_OVER_COUNTDOWN_SECONDS,
    DEBUG_MODE, SHOW_FPS 
)
from welcome_display import welcome_screen_content
from level_selection import level_menu_content
from colors_level import run_colors_level # Import for colors level

pygame.init()

pygame.event.set_allowed([
    pygame.FINGERDOWN,
    pygame.FINGERUP,
    pygame.FINGERMOTION,
    pygame.QUIT,
    pygame.KEYDOWN,
    pygame.MOUSEBUTTONDOWN,
    pygame.MOUSEBUTTONUP,
])

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Super Student")

def detect_display_type():
    info = pygame.display.Info()
    screen_w, screen_h = info.current_w, info.current_h
    if screen_w >= 1920 and screen_h >= 1080:
        if screen_w > 2560 or screen_h > 1440: 
            return "QBOARD"
    return "DEFAULT"

DISPLAY_MODE = DEFAULT_MODE
try:
    with open(DISPLAY_SETTINGS_PATH, "r") as f:
        loaded_mode = f.read().strip()
        if loaded_mode in DISPLAY_MODES:
            DISPLAY_MODE = loaded_mode
except:
    DISPLAY_MODE = detect_display_type()

from utils.resource_manager import ResourceManager
from utils.particle_system import ParticleManager # ParticleManager is used

particle_manager = None 

def init_resources():
    global font_sizes, fonts, large_font, small_font, TARGET_FONT, TITLE_FONT
    global MAX_PARTICLES, MAX_EXPLOSIONS, MAX_SWIRL_PARTICLES, mother_radius
    global particle_manager 
    from settings import FONT_SIZES, MAX_PARTICLES as PARTICLES_SETTINGS
    from settings import MAX_EXPLOSIONS as EXPLOSIONS_SETTINGS
    from settings import MAX_SWIRL_PARTICLES as SWIRL_SETTINGS
    from settings import MOTHER_RADIUS
    resource_manager = ResourceManager()
    resource_manager.set_display_mode(DISPLAY_MODE)
    MAX_PARTICLES = PARTICLES_SETTINGS[DISPLAY_MODE]
    MAX_EXPLOSIONS = EXPLOSIONS_SETTINGS[DISPLAY_MODE]
    MAX_SWIRL_PARTICLES = SWIRL_SETTINGS[DISPLAY_MODE]
    mother_radius = MOTHER_RADIUS[DISPLAY_MODE]
    font_sizes = FONT_SIZES[DISPLAY_MODE]["regular"]
    resources = resource_manager.initialize_game_resources()
    fonts = resources['fonts']
    large_font = resources['large_font']
    small_font = resources['small_font']
    TARGET_FONT = resources['target_font']
    TITLE_FONT = resources['title_font']
    particle_manager = ParticleManager(max_particles=MAX_PARTICLES)
    particle_manager.set_culling_distance(WIDTH)
    try:
        with open(DISPLAY_SETTINGS_PATH, "w") as f:
            f.write(DISPLAY_MODE)
    except:
        pass
    print(f"Resources initialized for display mode: {DISPLAY_MODE}")
    return resource_manager

resource_manager = init_resources()

def get_small_font():
    return small_font
def get_debug_settings():
    return DEBUG_MODE, SHOW_FPS
def get_display_mode():
    return DISPLAY_MODE
def set_current_display_mode(mode):
    global DISPLAY_MODE
    DISPLAY_MODE = mode

# Helpers for level modules
def get_mother_radius():
    return mother_radius
def get_colors_collision_delay():
    return COLORS_COLLISION_DELAY

def get_shake_variables():
    return shake_duration, shake_magnitude
def set_shake_variables(duration, magnitude):
    global shake_duration, shake_magnitude
    shake_duration = duration
    shake_magnitude = magnitude
def get_game_over_variables():
    return game_over_triggered, game_over_delay
def set_game_over_variables(triggered, delay):
    global game_over_triggered, game_over_delay
    game_over_triggered = triggered
    game_over_delay = delay
def get_background_variables(read_only=False): # read_only unused for now
    return {
        "background_shattered": background_shattered,
        "current_background": current_background,
        "opposite_background": opposite_background,
        "shatter_timer": shatter_timer
    }
def set_background_variables(is_shattered, current_bg, opposite_bg, timer_val):
    global background_shattered, current_background, opposite_background, shatter_timer
    background_shattered = is_shattered
    current_background = current_bg
    opposite_background = opposite_bg
    shatter_timer = timer_val
def get_explosions_list_ref():
    return explosions
def get_active_touches_ref():
    return active_touches
def get_glass_cracks_list_ref():
    return glass_cracks


PARTICLE_CULLING_DISTANCE = WIDTH
particle_pool = [] # This seems to be legacy, ParticleManager is used
for _ in range(100): 
    particle_pool.append({
        "x": 0, "y": 0, "color": (0,0,0), "size": 0, 
        "dx": 0, "dy": 0, "duration": 0, "start_duration": 0,
        "active": False
    })

particles = [] # Main particle list used by charge_up_effect, etc. ParticleManager handles its own.
shake_duration = 0
shake_magnitude = 10
active_touches = {}
explosions = []
lasers = []
glass_cracks = []
background_shattered = False
CRACK_DURATION = 600
shatter_timer = 0
opposite_background = BLACK
current_background = WHITE
game_over_triggered = False
game_over_delay = 0
GAME_OVER_DELAY_FRAMES = 60
player_color_transition = 0
player_current_color = FLAME_COLORS[0]
player_next_color = FLAME_COLORS[1]
charging_ability = False
charge_timer = 0
charge_particles = []
ability_target = None
swirl_particles = []
particles_converging = False
convergence_target = None
convergence_timer = 0

###############################################################################
#                              SCREEN FUNCTIONS                               #
###############################################################################
# welcome_screen is in welcome_display.py
# level_menu is in level_selection.py

###############################################################################
#                          GAME LOGIC & EFFECTS                               #
###############################################################################

def game_loop(mode):
    global shake_duration, shake_magnitude, particles, active_touches, explosions, lasers, player_color_transition, player_current_color, player_next_color, charging_ability, charge_timer, charge_particles, ability_target, swirl_particles, particles_converging, convergence_target, convergence_timer, glass_cracks, background_shattered, shatter_timer, mother_radius, game_over_triggered, game_over_delay
    # color_idx, color_sequence, next_color_index, target_dots_left are now managed by colors_level.py

    shake_duration = 0; shake_magnitude = 0; particles = []; explosions = []; lasers = []
    active_touches.clear() # Clear the global dict
    glass_cracks.clear() # Clear the global list
    background_shattered = False; shatter_timer = 0
    # mother_radius is set in init_resources and accessed by get_mother_radius for colors_level
    convergence_timer = 0; charge_timer = 0; convergence_target = None; player_color_transition = 0
    player_current_color = FLAME_COLORS[0]; player_next_color = FLAME_COLORS[1]
    charging_ability = False; charge_particles = []; ability_target = None; swirl_particles = []
    particles_converging = False; game_over_triggered = False; game_over_delay = 0
    
    # Specific reset for colors_level variables, if they were ever global here
    # These are now handled within run_colors_level's level_state
    # global color_idx, color_sequence, next_color_index, target_dots_left 
    # color_idx = 0; color_sequence = []; next_color_index = 0; # target_dots_left handled by colors_level

    try:
        with open(LEVEL_PROGRESS_PATH, "r") as f:
            progress = f.read().strip()
            shapes_completed = "shapes_completed" in progress
    except:
        shapes_completed = False
    shapes_first_round_completed = False

    if mode == "colors":
        return run_colors_level(
            screen, WIDTH, HEIGHT, BLACK, WHITE, FLAME_COLORS,
            get_small_font, get_mother_radius, get_colors_collision_delay,
            create_explosion, 
            create_crack, # Passing the main create_crack directly
            checkpoint_screen,
            draw_cracks, draw_explosion, display_info, particle_manager.create_particle,
            game_over_screen,
            get_shake_variables, set_shake_variables,
            get_game_over_variables, set_game_over_variables,
            get_background_variables, set_background_variables,
            get_explosions_list_ref, 
            get_active_touches_ref,
            get_glass_cracks_list_ref,
            MAX_CRACKS 
        )

    # --- Logic for other game modes (alphabet, numbers, shapes, clcase) below ---
    sequence = SEQUENCES.get(mode, SEQUENCES["alphabet"])
    groups = [sequence[i:i+GROUP_SIZE] for i in range(0, len(sequence), GROUP_SIZE)]
    current_group_index = 0
    if not groups: 
        print(f"Error: No groups for mode {mode}.")
        return False 
    current_group = groups[current_group_index]
    letters_to_target = current_group.copy()
    if not letters_to_target:
        print(f"Error: Current group is empty for mode {mode}.")
        return False
    target_letter = letters_to_target[0]
    TOTAL_LETTERS = len(sequence)
    total_destroyed = 0; overall_destroyed = 0; running = True; clock = pygame.time.Clock()
    stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(2, 4)] for _ in range(100)]
    letters = []; letters_spawned = 0; letters_destroyed = 0
    last_checkpoint_triggered = 0; checkpoint_waiting = False; checkpoint_delay_frames = 0
    just_completed_level = False; score = 0
    abilities = ["laser", "aoe", "charge_up"]; current_ability = "laser"
    game_started = False; last_click_time = 0
    player_x = WIDTH // 2; player_y = HEIGHT // 2 # Player position (center target)
    # player_color_index = 0 # Seems unused
    # click_cooldown = 0 # Seems unused
    mouse_down = False; mouse_press_time = 0; click_count = 0
    letters_to_spawn = current_group.copy(); frame_count = 0

    # --- Main Game Loop (for non-colors modes) ---
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False; break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: pygame.quit(); exit()
                if event.key == pygame.K_SPACE:
                    current_ability = abilities[(abilities.index(current_ability) + 1) % len(abilities)]
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not mouse_down:
                    mouse_press_time = pygame.time.get_ticks()
                    mouse_down = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                release_time = pygame.time.get_ticks()
                mouse_down = False
                duration = release_time - mouse_press_time
                if duration <= 1000: 
                    click_count += 1
                    if not game_started: game_started = True
                    else:
                        click_x, click_y = pygame.mouse.get_pos()
                        last_click_time = release_time
                        hit_target = False
                        for letter_obj in letters[:]:
                            if letter_obj["rect"].collidepoint(click_x, click_y):
                                hit_target = True
                                if letter_obj["value"] == target_letter:
                                    score += 10
                                    create_explosion(letter_obj["x"], letter_obj["y"])
                                    create_flame_effect(player_x, player_y - 80, letter_obj["x"], letter_obj["y"])
                                    trigger_particle_convergence(letter_obj["x"], letter_obj["y"])
                                    apply_explosion_effect(letter_obj["x"], letter_obj["y"], 150, letters)
                                    for i in range(20):
                                        particle_manager.create_particle(
                                            letter_obj["x"], letter_obj["y"],
                                            random.choice(FLAME_COLORS),
                                            random.randint(40, 80),
                                            random.uniform(-2, 2), random.uniform(-2, 2), 20
                                        )
                                    letters.remove(letter_obj)
                                    letters_destroyed += 1
                                    if target_letter in letters_to_target:
                                        letters_to_target.remove(target_letter)
                                    if letters_to_target: target_letter = letters_to_target[0]
                                    # else: # Group finished, handled later
                                    break 
                                else: # Clicked wrong target
                                    shake_duration = 5; shake_magnitude = 3
                        if not hit_target and game_started:
                            handle_misclick(click_x, click_y)
            elif event.type == pygame.FINGERDOWN:
                touch_id = event.finger_id
                touch_x, touch_y = event.x * WIDTH, event.y * HEIGHT
                active_touches[touch_id] = (touch_x, touch_y)
                if not game_started: game_started = True
                else:
                    hit_target = False
                    for letter_obj in letters[:]:
                        if letter_obj["rect"].collidepoint(touch_x, touch_y):
                            hit_target = True
                            if letter_obj["value"] == target_letter:
                                score += 10
                                create_explosion(letter_obj["x"], letter_obj["y"])
                                create_flame_effect(player_x, player_y - 80, letter_obj["x"], letter_obj["y"])
                                trigger_particle_convergence(letter_obj["x"], letter_obj["y"])
                                apply_explosion_effect(letter_obj["x"], letter_obj["y"], 150, letters)
                                for i in range(20):
                                     particle_manager.create_particle(
                                        letter_obj["x"], letter_obj["y"],
                                        random.choice(FLAME_COLORS),
                                        random.randint(40, 80),
                                        random.uniform(-2, 2), random.uniform(-2, 2), 20
                                    )
                                letters.remove(letter_obj)
                                letters_destroyed += 1
                                if target_letter in letters_to_target:
                                    letters_to_target.remove(target_letter)
                                if letters_to_target: target_letter = letters_to_target[0]
                                break
                            else: # Touched wrong target
                                shake_duration = 5; shake_magnitude = 3
                    if not hit_target and game_started:
                        handle_misclick(touch_x, touch_y)
            elif event.type == pygame.FINGERUP:
                touch_id = event.finger_id
                if touch_id in active_touches: del active_touches[touch_id]

        if game_started:
            if letters_to_spawn and frame_count % LETTER_SPAWN_INTERVAL == 0:
                item_value = letters_to_spawn.pop(0)
                letter_obj = { "value": item_value, "x": random.randint(50, WIDTH - 50), "y": -50, 
                               "rect": pygame.Rect(0,0,0,0), "size": 120, 
                               "dx": random.choice([-1,-0.5,0.5,1])*1.5, "dy": random.choice([1,1.5])*1.5,
                               "can_bounce": False, "mass": random.uniform(40,60) }
                letters.append(letter_obj); letters_spawned += 1
        
        offset_x, offset_y = (random.randint(-shake_magnitude,shake_magnitude), random.randint(-shake_magnitude,shake_magnitude)) if shake_duration > 0 else (0,0)
        if shake_duration > 0: shake_duration -=1

        if game_over_triggered:
            if game_over_delay > 0: game_over_delay -= 1
            else:
                game_started = False
                if game_over_screen(): running = False; break
                else: running = False; break 
        
        screen.fill(opposite_background if background_shattered else current_background)
        draw_cracks(screen)

        for star in stars:
            x, y, radius = star; y += 1
            pygame.draw.circle(screen, (200,200,200), (x+offset_x, y+offset_y), radius)
            if y > HEIGHT+radius: y = random.randint(-50,-10); x = random.randint(0,WIDTH)
            star[1]=y; star[0]=x
        
        update_swirl_particles(player_x, player_y)

        player_color_transition += 0.02
        if player_color_transition >= 1:
            player_color_transition = 0
            current_idx = FLAME_COLORS.index(player_current_color)
            player_current_color = FLAME_COLORS[current_idx]
            player_next_color = FLAME_COLORS[(current_idx+1)%len(FLAME_COLORS)]
        r_pc = int(player_current_color[0]*(1-player_color_transition) + player_next_color[0]*player_color_transition)
        g_pc = int(player_current_color[1]*(1-player_color_transition) + player_next_color[1]*player_color_transition)
        b_pc = int(player_current_color[2]*(1-player_color_transition) + player_next_color[2]*player_color_transition)
        center_target_color = (r_pc,g_pc,b_pc)

        if mode == "shapes":
            val, sz = target_letter, 500; pos_s = (player_x+offset_x, player_y+offset_y)
            rect_s = pygame.Rect(pos_s[0]-int(sz*1.5)//2, pos_s[1]-sz//2, int(sz*1.5), sz)
            if val=="Rectangle": pygame.draw.rect(screen,center_target_color,rect_s,8)
            elif val=="Square": sq_rect=pygame.Rect(pos_s[0]-sz//2,pos_s[1]-sz//2,sz,sz); pygame.draw.rect(screen,center_target_color,sq_rect,8)
            elif val=="Circle": pygame.draw.circle(screen,center_target_color,pos_s,sz//2,8)
            elif val=="Triangle": pts=[(pos_s[0],pos_s[1]-sz//2),(pos_s[0]-sz//2,pos_s[1]+sz//2),(pos_s[0]+sz//2,pos_s[1]+sz//2)]; pygame.draw.polygon(screen,center_target_color,pts,8)
            elif val=="Pentagon": pts=[]; r_sz=sz//2; [pts.append((pos_s[0]+r_sz*math.cos(math.radians(72*i-90)),pos_s[1]+r_sz*math.sin(math.radians(72*i-90)))) for i in range(5)]; pygame.draw.polygon(screen,center_target_color,pts,8)
        else:
            player_font = pygame.font.Font(None, 900)
            disp_char = target_letter.upper() if mode=="clcase" else ("α" if mode=="alphabet" and target_letter=="a" else target_letter)
            player_text_surf = player_font.render(disp_char,True,center_target_color)
            player_rect = player_text_surf.get_rect(center=(player_x+offset_x,player_y+offset_y))
            screen.blit(player_text_surf,player_rect)

        for letter_obj in letters[:]:
            letter_obj["x"]+=letter_obj["dx"]; letter_obj["y"]+=letter_obj["dy"]
            if not letter_obj["can_bounce"] and letter_obj["y"] > HEIGHT//5: letter_obj["can_bounce"]=True
            if letter_obj["can_bounce"]:
                damp=0.8; sz_l=letter_obj.get("size",50)/2
                if letter_obj["x"]<=0+sz_l: letter_obj["x"]=0+sz_l; letter_obj["dx"]=abs(letter_obj["dx"])*damp
                elif letter_obj["x"]>=WIDTH-sz_l: letter_obj["x"]=WIDTH-sz_l; letter_obj["dx"]=-abs(letter_obj["dx"])*damp
                if letter_obj["y"]<=0+sz_l: letter_obj["y"]=0+sz_l; letter_obj["dy"]=abs(letter_obj["dy"])*damp
                elif letter_obj["y"]>=HEIGHT-sz_l: 
                    letter_obj["y"]=HEIGHT-sz_l; letter_obj["dy"]=-abs(letter_obj["dy"])*damp
                    letter_obj["dx"]*=damp; letter_obj["dx"]+=random.uniform(0.1,0.3) if letter_obj["x"]<WIDTH/2 else -random.uniform(0.1,0.3)
            
            draw_x, draw_y = int(letter_obj["x"]+offset_x), int(letter_obj["y"]+offset_y)
            if mode == "shapes":
                val, sz = letter_obj["value"], letter_obj["size"]; pos_ls=(draw_x,draw_y)
                if val=="Rectangle": rect_ls=pygame.Rect(pos_ls[0]-int(sz*1.5)//2,pos_ls[1]-sz//2,int(sz*1.5),sz); letter_obj["rect"]=rect_ls; pygame.draw.rect(screen,center_target_color,rect_ls,6)
                elif val=="Square": rect_ls=pygame.Rect(pos_ls[0]-sz//2,pos_ls[1]-sz//2,sz,sz); letter_obj["rect"]=rect_ls; pygame.draw.rect(screen,center_target_color,rect_ls,6)
                elif val=="Circle": rect_ls=pygame.Rect(pos_ls[0]-sz//2,pos_ls[1]-sz//2,sz,sz); letter_obj["rect"]=rect_ls; pygame.draw.circle(screen,center_target_color,pos_ls,sz//2,6)
                elif val=="Triangle": pts_ls=[(pos_ls[0],pos_ls[1]-sz//2),(pos_ls[0]-sz//2,pos_ls[1]+sz//2),(pos_ls[0]+sz//2,pos_ls[1]+sz//2)]; letter_obj["rect"]=pygame.Rect(pos_ls[0]-sz//2,pos_ls[1]-sz//2,sz,sz); pygame.draw.polygon(screen,center_target_color,pts_ls,6)
                elif val=="Pentagon": pts_ls=[]; r_sz_ls=sz//2; [pts_ls.append((pos_ls[0]+r_sz_ls*math.cos(math.radians(72*i-90)),pos_ls[1]+r_sz_ls*math.sin(math.radians(72*i-90)))) for i in range(5)]; letter_obj["rect"]=pygame.Rect(pos_ls[0]-sz//2,pos_ls[1]-sz//2,sz,sz); pygame.draw.polygon(screen,center_target_color,pts_ls,6)
            else:
                disp_val = "α" if mode=="clcase" and letter_obj["value"]=="a" else letter_obj["value"]
                text_surf = TARGET_FONT.render(disp_val,True,center_target_color)
                text_rect_ls = text_surf.get_rect(center=(draw_x,draw_y)); letter_obj["rect"]=text_rect_ls; screen.blit(text_surf,text_rect_ls)

        for i, l1 in enumerate(letters):
            for j in range(i+1,len(letters)):
                l2=letters[j]; dx_c=l2["x"]-l1["x"]; dy_c=l2["y"]-l1["y"]; dist_sq=dx_c*dx_c+dy_c*dy_c
                r1=l1.get("size",TARGET_FONT.get_height())/1.8; r2=l2.get("size",TARGET_FONT.get_height())/1.8
                min_dist_sq=(r1+r2)**2
                if dist_sq < min_dist_sq and dist_sq > 0:
                    dist_c=math.sqrt(dist_sq); nx_c,ny_c=dx_c/dist_c,dy_c/dist_c
                    overlap=(r1+r2)-dist_c; total_mass=l1["mass"]+l2["mass"]; push=overlap/total_mass
                    l1["x"]-=nx_c*push*l2["mass"]; l1["y"]-=ny_c*push*l2["mass"]
                    l2["x"]+=nx_c*push*l1["mass"]; l2["y"]+=ny_c*push*l1["mass"]
                    dvx_c,dvy_c=l1["dx"]-l2["dx"],l1["dy"]-l2["dy"]; dot_prod=dvx_c*nx_c+dvy_c*ny_c
                    impulse=(2*dot_prod)/total_mass; bounce=0.85
                    l1["dx"]-=impulse*l2["mass"]*nx_c*bounce; l1["dy"]-=impulse*l2["mass"]*ny_c*bounce
                    l2["dx"]+=impulse*l1["mass"]*nx_c*bounce; l2["dy"]+=impulse*l1["mass"]*ny_c*bounce
        
        for laser in lasers[:]:
            if laser["duration"]>0: 
                if laser["type"]=="flamethrower": draw_flamethrower(laser,offset_x,offset_y)
                laser["duration"]-=1
            else: lasers.remove(laser)
        for explosion in explosions[:]:
            if explosion["duration"]>0: draw_explosion(explosion,offset_x,offset_y); explosion["duration"]-=1
            else: explosions.remove(explosion)

        if charging_ability:
            charge_timer -=1; overlay_s=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); overlay_s.fill((0,0,0,100)); screen.blit(overlay_s,(0,0))
            for p_charge in charge_particles[:]:
                if p_charge["delay"]>0: p_charge["delay"]-=1; continue
                if p_charge["type"]=="materializing":
                    if p_charge["materialize_time"]>0:
                        p_charge["materialize_time"]-=1; ratio=1-(p_charge["materialize_time"]/15)
                        p_charge["opacity"]=int(p_charge["max_opacity"]*ratio); p_charge["size"]=p_charge["max_size"]*ratio
                        wob_x=math.cos(p_charge["wobble_angle"])*p_charge["wobble_amount"]; wob_y=math.sin(p_charge["wobble_angle"])*p_charge["wobble_amount"]
                        p_charge["wobble_angle"]+=p_charge["wobble_speed"]
                        p_surf=pygame.Surface((p_charge["size"]*2,p_charge["size"]*2),pygame.SRCALPHA)
                        pygame.draw.circle(p_surf,(*p_charge["color"],p_charge["opacity"]),(p_charge["size"],p_charge["size"]),p_charge["size"])
                        screen.blit(p_surf,(int(p_charge["x"]+wob_x-p_charge["size"]+offset_x),int(p_charge["y"]+wob_y-p_charge["size"]+offset_y)))
                        continue
                    else: p_charge["type"]="accelerating"
                if p_charge["type"]=="accelerating":
                    dx_ca,dy_ca=p_charge["target_x"]-p_charge["x"],p_charge["target_y"]-p_charge["y"]; dist_ca=math.hypot(dx_ca,dy_ca)
                    if dist_ca > 5:
                        p_charge["speed"]+=p_charge["acceleration"]*(1+(400-min(400,dist_ca))/1000)
                        norm_dx_ca,norm_dy_ca=dx_ca/dist_ca,dy_ca/dist_ca
                        p_charge["x"]+=norm_dx_ca*p_charge["speed"]; p_charge["y"]+=norm_dy_ca*p_charge["speed"]
                        if p_charge["trail"] and random.random()<0.4: particle_manager.create_particle(p_charge["x"],p_charge["y"],p_charge["color"],p_charge["size"]/2,-norm_dx_ca*0.5,-norm_dy_ca*0.5,50)
                        draw_x_ca,draw_y_ca=int(p_charge["x"]+offset_x),int(p_charge["y"]+offset_y); glow_sz_ca=p_charge["size"]*1.5
                        glow_s_ca=pygame.Surface((glow_sz_ca*2,glow_sz_ca*2),pygame.SRCALPHA); pygame.draw.circle(glow_s_ca,(*p_charge["color"],70),(glow_sz_ca,glow_sz_ca),glow_sz_ca); screen.blit(glow_s_ca,(int(draw_x_ca-glow_sz_ca),int(draw_y_ca-glow_sz_ca)))
                        p_s_ca=pygame.Surface((p_charge["size"]*2,p_charge["size"]*2),pygame.SRCALPHA); pygame.draw.circle(p_s_ca,(*p_charge["color"],p_charge["opacity"]),(p_charge["size"],p_charge["size"]),p_charge["size"]); screen.blit(p_s_ca,(int(draw_x_ca-p_charge["size"]),int(draw_y_ca-p_charge["size"])))
                    else:
                        for _ in range(3): particles.append({"x":p_charge["target_x"],"y":p_charge["target_y"],"color":p_charge["color"],"size":random.uniform(12,24),"dx":random.uniform(-2,2),"dy":random.uniform(-2,2),"duration":20})
                        charge_particles.remove(p_charge)
            orb_x,orb_y=player_x+offset_x,player_y-80+offset_y; energy_rad=20+(30-charge_timer)*1.5; pulse_orb=abs(math.sin(pygame.time.get_ticks()*0.01))*15
            for i in range(3):
                factor=1-(i*0.25); color_orb=FLAME_COLORS[int((pygame.time.get_ticks()*0.01+i*2)%len(FLAME_COLORS))]; rad_orb=(energy_rad+pulse_orb)*factor; alpha_orb=int(200*factor)
                glow_s_orb=pygame.Surface((rad_orb*2,rad_orb*2),pygame.SRCALPHA); pygame.draw.circle(glow_s_orb,(*color_orb,alpha_orb),(rad_orb,rad_orb),rad_orb); screen.blit(glow_s_orb,(int(orb_x-rad_orb),int(orb_y-rad_orb)))
            pygame.draw.circle(screen,(255,255,255),(int(orb_x),int(orb_y)),int(energy_rad/3))
            if charge_timer <= 0:
                charging_ability=False
                if ability_target:
                    create_explosion(ability_target[0],ability_target[1]); create_flame_effect(player_x,player_y-80,ability_target[0],ability_target[1])
                    for _ in range(40): particles.append({"x":ability_target[0],"y":ability_target[1],"color":random.choice(FLAME_COLORS),"size":random.randint(40,80),"dx":random.uniform(-4,4),"dy":random.uniform(-4,4),"duration":100})
                    ability_target=None
        
        particle_manager.update()
        particle_manager.draw(screen,offset_x,offset_y)
        display_info(score, current_ability, target_letter, overall_destroyed + letters_destroyed, TOTAL_LETTERS, mode)
        pygame.display.flip(); clock.tick(50); frame_count+=1
        overall_destroyed = total_destroyed + letters_destroyed
        if checkpoint_waiting:
            if checkpoint_delay_frames <= 0 and len(explosions)<=1 and len(lasers)<=1 and not particles_converging:
                checkpoint_waiting=False; game_started=False
                if not checkpoint_screen(mode): running=False; break
                else: # Continue pressed
                    if mode=="shapes": return True # Restart shapes
                    else: game_started=True
            else: checkpoint_delay_frames-=1
        elif overall_destroyed > 0 and overall_destroyed % 10 == 0 and overall_destroyed // 10 > last_checkpoint_triggered and not just_completed_level:
            last_checkpoint_triggered = overall_destroyed // 10; checkpoint_waiting = True; checkpoint_delay_frames = 60

        if not letters and not letters_to_spawn and not letters_to_target: # Changed to check letters_to_target directly
            total_destroyed += letters_destroyed; current_group_index += 1; just_completed_level = True
            if mode=="shapes" and not shapes_first_round_completed:
                shapes_first_round_completed=True; current_group_index=0; current_group=groups[current_group_index]
                letters_to_spawn=current_group.copy(); letters_to_target=current_group.copy()
                if letters_to_target: target_letter=letters_to_target[0]
                letters_destroyed=0; letters_spawned=0; just_completed_level=False; game_started=True
                last_checkpoint_triggered=overall_destroyed//10
            elif current_group_index < len(groups):
                current_group=groups[current_group_index]; letters_to_spawn=current_group.copy(); letters_to_target=current_group.copy()
                if letters_to_target: target_letter=letters_to_target[0]
                else: print(f"Warning: Group {current_group_index} empty."); running=False; break
                letters_destroyed=0; letters_spawned=0; just_completed_level=False; game_started=True
                last_checkpoint_triggered=overall_destroyed//10
            else: # Level finished
                if mode=="shapes": # shapes level completion is handled differently
                    if shapes_first_round_completed: # Ensure both rounds are done
                        # This block will now be reached only after the *second* round of shapes is done.
                        try: with open(LEVEL_PROGRESS_PATH,"w") as f: f.write("shapes_completed")
                        except: pass
                        pygame.time.delay(500)
                        if checkpoint_screen(mode): return True # Restart shapes
                        else: return False # To menu
                else: # For other levels
                    pygame.time.delay(500)
                    # Re-evaluating checkpoint logic for end of non-shapes levels
                    # Instead of directly showing well_done_screen, show checkpoint screen
                    if not checkpoint_screen(mode): # If Menu selected from checkpoint
                        running = False # Go to menu
                    else: # If Continue selected
                        # This implies the level (e.g. alphabet) is done. For now, go to menu.
                        # Future: could go to next level in a sequence if designed.
                        running = False 
                break # Exit game loop for this level
    
    # This section for shapes completion check needs to be accurate
    if mode == "shapes" and shapes_first_round_completed and not letters and not letters_to_spawn and not letters_to_target:
        # This is redundant if the logic above inside the main while loop's "Level finished" handles it.
        # Let's ensure it's correctly handled there.
        # If this point is reached, it means the while loop terminated for shapes mode after 2nd round.
        # The `return True` or `return False` from checkpoint_screen would have already exited.
        # This specific check here might be obsolete due to changes above.
        pass

    return True if running == False else False # This return is a bit confusing. game_loop should return True if going to menu, False if quit.
                                            # Let's simplify: return True to go to menu, False if full quit.
                                            # The current uses of 'return False' within game_loop (e.g. for colors) mean "go to menu"
                                            # So, this final return should align. If running is False, it implies menu/level change.

# ... (rest of the functions: create_aoe, display_info, well_done_screen, etc.)
// ... existing code ...
def create_particle(x, y, color, size, dx, dy, duration):
    """Legacy function that now uses the particle manager."""
    # This function is called by create_crack and charge_up_effect directly using `particles.append`.
    # It should be updated to use particle_manager.create_particle consistently if `particles` list is to be deprecated.
    # For now, particle_manager is used in some places, `particles.append` in others.
    # This specific function, if kept, should also use the manager.
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
    # Call the refactored welcome screen
    selected_mode = welcome_screen_content(
        screen,
        WIDTH, HEIGHT,
        FLAME_COLORS, BLACK, WHITE,
        init_resources, # Pass the function itself
        get_small_font, # Pass the helper
        detect_display_type, # Pass the function itself
        get_debug_settings, # Pass the helper
        get_display_mode, # Pass the helper
        set_current_display_mode # Pass the helper
    )
    # DISPLAY_MODE is updated by set_current_display_mode via welcome_screen_content
    # init_resources() is also called within welcome_screen_content after mode selection
    
    # Original main loop continues after welcome screen
    while True:
        # Call the refactored level menu
        mode = level_menu_content(
            screen,
            WIDTH, HEIGHT,
            FLAME_COLORS, BLACK, WHITE,
            get_small_font # Pass the helper function
        )
        if mode is None: # If level_menu_content exits early (e.g. QUIT event)
            break
        
        # Run the game loop and check its return value
        restart_level = game_loop(mode)
        
        # If game_loop returns True, restart the level for shapes level or colors level
        while restart_level and (mode == "shapes" or mode == "colors"):
            restart_level = game_loop(mode)