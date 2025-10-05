#!/usr/bin/env python3
"""
Scoreboard Launcher for Sec360 by Abhay
Launches the live scoreboard viewer
"""

import sys
import os
from pathlib import Path

# Get the project root directory (where this script is located)
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Add core directory to path
sys.path.append(os.path.join(project_root, 'core'))

if __name__ == "__main__":
    try:
        # Change to the project root directory for proper file access
        os.chdir(project_root)
        
        # Add core directory to path
        core_path = os.path.join(project_root, 'core')
        sys.path.insert(0, core_path)
        
        # Import the scoreboard viewer directly
        import importlib.util
        scoreboard_file = os.path.join(core_path, 'scoreboard', 'scoreboard_viewer.py')
        spec = importlib.util.spec_from_file_location("scoreboard_viewer", scoreboard_file)
        scoreboard_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scoreboard_module)
        
        scoreboard = scoreboard_module.ScoreboardViewer()
        scoreboard.run()
    except Exception as e:
        print(f"Error starting scoreboard: {e}")
        import traceback
        traceback.print_exc()
