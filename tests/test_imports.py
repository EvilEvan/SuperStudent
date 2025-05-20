import pytest
import importlib
import os
from pathlib import Path

def get_python_files(directory: str) -> list:
    """Get all Python files in the given directory and its subdirectories."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def test_all_modules_importable():
    """Test that all Python modules can be imported."""
    root_dir = Path(__file__).parent.parent
    python_files = get_python_files(str(root_dir))
    
    for file_path in python_files:
        # Convert file path to module path
        rel_path = os.path.relpath(file_path, str(root_dir))
        module_path = rel_path.replace(os.path.sep, '.').replace('.py', '')
        
        # Skip test files and __init__ files
        if 'test_' in module_path or '__init__' in module_path:
            continue
            
        try:
            importlib.import_module(module_path)
        except ImportError as e:
            pytest.fail(f"Failed to import {module_path}: {str(e)}")

def test_engine_entry_point():
    """Test that the engine module can be imported and has required attributes."""
    try:
        from engine.engine import Engine
        assert hasattr(Engine, 'run'), "Engine class should have a 'run' method"
    except ImportError as e:
        pytest.fail(f"Failed to import engine module: {str(e)}")

def test_critical_modules():
    """Test that critical game modules can be imported."""
    critical_modules = [
        'engine.engine',
        'game_logic',
        'game_setup',
        'settings'
    ]
    
    for module_name in critical_modules:
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            pytest.fail(f"Failed to import critical module {module_name}: {str(e)}") 