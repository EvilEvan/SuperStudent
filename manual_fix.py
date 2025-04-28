def main():
    # Read the file
    with open("SuperStudent.py", 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Define the fixed section
    fixed_section = """    # Default button
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
    clock.tick(60)"""
    
    # Replace the section
    start_line = 427 - 1  # Convert to 0-based index
    end_line = 514
    
    # Keep everything before the problematic section
    new_lines = lines[:start_line]
    
    # Add the fixed section
    new_lines.extend(fixed_section.split('\n'))
    new_lines = [line + '\n' for line in new_lines]
    
    # Add everything after the problematic section
    new_lines.extend(lines[end_line:])
    
    # Also fix other known issues
    # Line 392 - screen.blit(shadow, shadow_rect)
    if 391 < len(new_lines):
        new_lines[391] = "        screen.blit(shadow, shadow_rect)\n"
    
    # Line 400 - screen.blit(glow, glow_rect)
    if 399 < len(new_lines):
        new_lines[399] = "            screen.blit(glow, glow_rect)\n"
    
    # Other specific fixes for lines that might have indentation issues
    indentation_fixes = {
        407: "    screen.blit(highlight, highlight_rect)\n",
        411: "    screen.blit(mid_tone, mid_rect)\n",
        415: "    screen.blit(inner_shadow, inner_shadow_rect)\n",
        419: "    screen.blit(title, title_rect)\n",
        422: "    # Draw instructions\n",
        423: "    screen.blit(display_text, display_rect)\n",
    }
    
    for line_idx, fixed_line in indentation_fixes.items():
        if line_idx < len(new_lines):
            new_lines[line_idx] = fixed_line
    
    # Write the fixed content to a new file
    with open("SuperStudent_fixed.py", 'w', encoding='utf-8') as file:
        file.writelines(new_lines)
    
    print("Fixed file created as SuperStudent_fixed.py")

if __name__ == "__main__":
    main() 