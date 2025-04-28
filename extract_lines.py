def extract_problematic_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Line numbers to check (in editor coordinates)
    problem_line_numbers = [392, 400, 408, 412, 416, 420, 423, 447, 471, 484, 501, 502, 503, 508]
    
    # Extract the problematic lines and surrounding context
    for i in sorted(problem_line_numbers):
        # Adjust to 0-based indexing
        line_idx = i - 1
        
        # Print line number and the line content
        if 0 <= line_idx < len(lines):
            print(f"Line {i}: {lines[line_idx].rstrip()}")
            
            # Print a few lines before and after for context
            start = max(0, line_idx - 2)
            end = min(len(lines), line_idx + 3)
            
            print("Context:")
            for j in range(start, end):
                if j == line_idx:
                    prefix = ">>> "  # Highlight the problematic line
                else:
                    prefix = "    "
                print(f"{prefix}Line {j+1}: {lines[j].rstrip()}")
            print("-" * 50)

if __name__ == "__main__":
    extract_problematic_lines("SuperStudent.py") 