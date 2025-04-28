def main():
    # Read the file
    with open("SuperStudent.py", 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Check the indentation around line 428
    # Lines 428-432 seem to be part of a different block that needs 8 spaces
    for i in range(427, 433):
        if i < len(lines) and lines[i].strip():
            content = lines[i].lstrip()
            lines[i] = '    ' + content  # 4 spaces for this block
    
    # Line 428-443 need to be indented with 8 spaces (they're in a block)
    for i in range(428, 444):
        if i < len(lines) and lines[i].strip():
            content = lines[i].lstrip()
            lines[i] = '        ' + content  # 8 spaces for nested blocks
    
    # Similar blocks that need specific indentation
    # Default button block (lines ~428-447)
    for i in range(428, 447):
        if i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith('#'):
            content = lines[i].lstrip()
            lines[i] = '        ' + content  # 8 spaces
    
    # QBoard button block (lines ~451-471)
    for i in range(451, 471):
        if i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith('#'):
            content = lines[i].lstrip()
            lines[i] = '        ' + content  # 8 spaces
    
    # Fix lines explicitly known to have issues
    problem_lines = {
        392: 8,   # screen.blit(shadow, shadow_rect)
        400: 12,  # screen.blit(glow, glow_rect)
        408: 4,   # screen.blit(highlight, highlight_rect)
        412: 4,   # screen.blit(mid_tone, mid_rect)
        416: 4,   # screen.blit(inner_shadow, inner_shadow_rect)
        420: 4,   # screen.blit(title, title_rect)
        423: 4,   # Draw instructions
        424: 4,   # screen.blit(display_text, display_rect)
        426: 4,   # Draw buttons with hover effects
        427: 4,   # Default button
        447: 4,   # default_text_rect
        450: 4,   # QBoard button
        471: 4,   # qboard_text_rect
        474: 4,   # Auto-detected mode indicator
        475: 4,   # screen.blit(auto_text, auto_rect)
        477: 4,   # SANGSOM animation
        478: 4,   # sangsom_pulse
        479: 4,   # if sangsom_pulse
        483: 4,   # bright_yellow
        484: 4,   # lite_yellow
        485: 4,   # sangsom_color
        488: 4,   # Draw collaboration text
        489: 4,   # collab_text1
        490: 4,   # collab_text2
        491: 4,   # collab_text3
        493: 4,   # collab_rect1
        494: 4,   # collab_rect1.right
        495: 4,   # collab_rect1.centery
        497: 4,   # collab_rect2
        499: 4,   # collab_rect3
        500: 4,   # collab_rect3.left
        501: 4,   # collab_rect3.centery
        503: 4,   # screen.blit(collab_text1
        504: 4,   # screen.blit(collab_text2
        505: 4,   # screen.blit(collab_text3
        507: 4,   # Creator text
        508: 4,   # creator_text
        509: 4,   # creator_rect
        510: 4,   # screen.blit(creator_text
        512: 4,   # Update display
        513: 4,   # pygame.display.flip()
        514: 4,   # clock.tick(60)
    }
    
    # Fix the indentation for explicit problem lines
    for line_num, spaces in problem_lines.items():
        index = line_num - 1  # Convert to 0-based index
        if index < len(lines):
            content = lines[index].lstrip()
            lines[index] = ' ' * spaces + content
    
    # Write the fixed content back to a new file
    with open("SuperStudent_fixed.py", 'w', encoding='utf-8') as file:
        file.writelines(lines)
    
    print("Fixed file created as SuperStudent_fixed.py")

if __name__ == "__main__":
    main() 