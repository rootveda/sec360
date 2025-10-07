#!/usr/bin/env python3
"""
Sec360 with forced display settings
"""

import os
import sys
import tkinter as tk

# Force display settings
os.environ['TK_SILENCE_DEPRECATION'] = '1'

# Add core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

def force_display_settings():
    """Force proper display settings for Mac"""
    print("=== Forcing Display Settings ===")
    
    # Create root with explicit settings
    root = tk.Tk()
    root.title("Sec360 by Abhay - Advanced Code Security Analysis Platform")
    root.geometry("1400x900")
    
    # Force dark theme
    root.configure(bg='#2b2b2b')
    
    # Add test content
    frame = tk.Frame(root, bg='#2b2b2b')
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    title = tk.Label(frame, text="Sec360 by Abhay", 
                    font=('Arial', 24, 'bold'), 
                    bg='#2b2b2b', fg='white')
    title.pack(pady=20)
    
    subtitle = tk.Label(frame, text="Advanced Code Security Analysis Platform", 
                       font=('Arial', 14), 
                       bg='#2b2b2b', fg='#cccccc')
    subtitle.pack(pady=10)
    
    test_button = tk.Button(frame, text="Test Button", 
                           font=('Arial', 12),
                           bg='#4CAF50', fg='white',
                           command=lambda: print("Button clicked!"))
    test_button.pack(pady=20)
    
    print("If you see this content, GUI is working!")
    print("If still grey, it's a macOS display issue.")
    
    root.mainloop()

if __name__ == "__main__":
    force_display_settings()
