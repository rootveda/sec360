#!/usr/bin/env python3
"""
Quick display test after changing settings
"""

import tkinter as tk

def test_display():
    print("🖥️ Testing display after settings change...")
    
    root = tk.Tk()
    root.title("Display Test")
    root.geometry("400x300")
    root.configure(bg='#2b2b2b')
    
    # Add visible content
    frame = tk.Frame(root, bg='#2b2b2b')
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    title = tk.Label(frame, text="✅ Display Test", 
                    font=('Arial', 20, 'bold'), 
                    bg='#2b2b2b', fg='#4CAF50')
    title.pack(pady=20)
    
    message = tk.Label(frame, text="If you can see this text clearly,\nyour display settings are fixed!", 
                     font=('Arial', 12), 
                     bg='#2b2b2b', fg='white',
                     justify=tk.CENTER)
    message.pack(pady=20)
    
    button = tk.Button(frame, text="Test Button", 
                      font=('Arial', 14),
                      bg='#2196F3', fg='white',
                      command=lambda: print("✅ Button works!"))
    button.pack(pady=20)
    
    print("📱 Window should appear with dark background and white text")
    print("🛑 Press Ctrl+C to close")
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n✅ Test completed")
        root.destroy()

if __name__ == "__main__":
    test_display()
