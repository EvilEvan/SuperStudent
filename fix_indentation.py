def fix_indentation(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Note line numbers in Python are 0-indexed, so subtract 1 from the line numbers
    problem_lines = [
        391,  # line 392 in editor
        399,  # line 400 in editor
        407,  # line 408 in editor
        411,  # line 412 in editor
        415,  # line 416 in editor
        419,  # line 420 in editor
        446,  # line 447 in editor
        470,  # line 471 in editor
        483,  # line 484 in editor
        500,  # line 501 in editor
        501,  # line 502 in editor
        502,  # line 503 in editor
        507   # line 508 in editor
    ]
    
    # Fix each problem line by removing indentation
    for line_num in problem_lines:
        if line_num < len(lines):
            # Get the line content, strip all leading whitespace
            content = lines[line_num].lstrip()
            # Determine the appropriate indentation level
            if "glow_rect" in content or "shadow_rect" in content:
                # For nested loops/blocks
                indentation = "            "
            else:
                # For regular indentation
                indentation = "    "
            # Set the line with correct indentation
            lines[line_num] = indentation + content
    
    # Find and fix other potential indentation issues
    for i in range(420, 430):  # Check lines 421-430
        if i < len(lines) and lines[i].startswith("        #"):
            # Fix indentation of comments
            content = lines[i].lstrip()
            lines[i] = "    " + content
    
    # Save the fixed content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)
    
    print("Indentation fixed!")

if __name__ == "__main__":
    fix_indentation("SuperStudent.py") 