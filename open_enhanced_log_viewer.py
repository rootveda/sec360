#!/usr/bin/env python3
"""
Enhanced Log Viewer Launcher
Quick way to open the detailed log viewer
"""

import subprocess
import sys
import os

def main():
    print("🚀 Sec360 Enhanced Log Viewer Launcher")
    print("=" * 50)
    
    # Check if detailed sessions exist
    detailed_sessions_dir = "detailed_sessions"
    if not os.path.exists(detailed_sessions_dir):
        print("❌ No detailed sessions found!")
        print("💡 Run: python3 generate_sample_detailed_sessions.py")
        return
    
    # Count sessions
    session_files = [f for f in os.listdir(detailed_sessions_dir) if f.endswith('.json')]
    print(f"📊 Found {len(session_files)} detailed sessions")
    
    if len(session_files) == 0:
        print("❌ No detailed sessions found!")
        print("💡 Run: python3 generate_sample_detailed_sessions.py")
        return
    
    print("✅ Detailed sessions available!")
    print("🎯 Opening Enhanced Log Viewer...")
    print()
    
    try:
        # Launch the enhanced log viewer
        subprocess.run([sys.executable, "detailed_log_viewer.py"])
    except Exception as e:
        print(f"❌ Error opening log viewer: {e}")
        print("💡 Try running: python3 detailed_log_viewer.py")

if __name__ == "__main__":
    main()
