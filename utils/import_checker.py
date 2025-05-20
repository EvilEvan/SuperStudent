import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple

class ImportChecker:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.module_mapping: Dict[str, str] = {
            'alphabet_level': 'abc_level',
            'clcase_level': 'cl_case_letters',
            # Add more mappings as needed
        }
        self.imports: Dict[str, Set[str]] = {}
        self.issues: List[Tuple[str, str]] = []

    def check_file(self, file_path: Path) -> None:
        """Check a single file for import issues."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            file_imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        file_imports.add(name.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        file_imports.add(node.module)
            
            self.imports[str(file_path)] = file_imports
            
            # Check for stale imports
            for imp in file_imports:
                if imp in self.module_mapping:
                    self.issues.append((
                        str(file_path),
                        f"Stale import detected: '{imp}' should be '{self.module_mapping[imp]}'"
                    ))
        
        except Exception as e:
            self.issues.append((str(file_path), f"Error parsing file: {str(e)}"))

    def check_directory(self) -> None:
        """Check all Python files in the directory for import issues."""
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.py'):
                    self.check_file(Path(root) / file)

    def get_issues(self) -> List[Tuple[str, str]]:
        """Return all detected issues."""
        return self.issues

def main():
    """Main function to run the import checker."""
    checker = ImportChecker('.')
    checker.check_directory()
    
    issues = checker.get_issues()
    if issues:
        print("\nImport Issues Found:")
        for file_path, message in issues:
            print(f"\n{file_path}:")
            print(f"  {message}")
        exit(1)
    else:
        print("No import issues found.")

if __name__ == '__main__':
    main() 