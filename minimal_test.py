#!/usr/bin/env python3
"""
Minimal Tkinter test for Mac grey screen issue
"""

import tkinter as tk
import sys
import os

def test_minimal_gui():
    print("=== Minimal GUI Test ===")
    print(f"Python version: {sys.version}")
    print(f"Tkinter version: {tk.TkVersion}")
    print(f"Platform: {sys.platform}")
    
    # Test 1: Basic window
    print("\n1. Creating basic window...")
    root = tk.Tk()
    root.title("Basic Test")
    root.geometry("200x100")
    
    # Add a simple label
    label = tk.Label(root, text="Hello World!", font=('Arial', 14))
    label.pack(pady=20)
    
    print("2. Window created. If you see grey, it's a display issue.")
    print("3. Press Ctrl+C to close...")
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n4. Test completed.")
        root.destroy()

if __name__ == "__main__":
    test_minimal_gui()
