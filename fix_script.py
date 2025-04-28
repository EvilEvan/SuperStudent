def fix_indentation():
    # Read the original file
    with open("SuperStudent.py", 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Create a new file with fixed indentation
    with open("SuperStudent_fixed.py", 'w', encoding='utf-8') as fixed_file:
        # Keep track of indentation level
        current_block_level = 0
        in_function = False
        
        for i, line in enumerate(lines):
            # Skip empty lines
            if not line.strip():
                fixed_file.write(line)
                continue
            
            # Get the content without leading/trailing whitespace
            content = line.strip()
            
            # Calculate indentation based on line content and previous context
            indentation = ""
            if i in [391, 399]:  # Lines 392, 400
                # These are nested blocks
                indentation = "            "
            elif i in [407, 411, 415, 419, 446, 470, 483, 500, 501, 502, 507]:  # Other problematic lines
                indentation = "    "
            elif line.lstrip().startswith("#"):
                # Preserve indentation for comments based on context
                if current_block_level > 0:
                    indentation = "    " * current_block_level
            else:
                # For all other lines, preserve the original indentation
                indentation = line[:len(line) - len(line.lstrip())]
            
            # Write the fixed line to the new file
            fixed_file.write(indentation + content + "\n")
            
            # Update block tracking for next line
            if content.endswith(":"):
                current_block_level += 1
            elif content.startswith("def "):
                in_function = True
                current_block_level = 1
            elif content.startswith(("return", "break", "continue")) and in_function:
                current_block_level = max(1, current_block_level - 1)
    
    print("Fixed file created as SuperStudent_fixed.py")

if __name__ == "__main__":
    fix_indentation() 