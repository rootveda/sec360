#!/usr/bin/env python3
"""
Sec360 Fixed GUI - Forces proper display initialization
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
import time

# Force display settings
os.environ['TK_SILENCE_DEPRECATION'] = '1'

# Add core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

class Sec360FixedApp:
    def __init__(self):
        print("🚀 Starting Sec360 with fixed GUI...")
        
        # Create root window with explicit settings
        self.root = tk.Tk()
        self.root.title("Sec360 by Abhay - Advanced Code Security Analysis Platform")
        self.root.geometry("1400x900")
        
        # Force dark theme immediately
        self.root.configure(bg='#2b2b2b')
        
        # Force window to appear
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(lambda: self.root.attributes('-topmost', False))
        
        # Create main container
        self.main_frame = tk.Frame(self.root, bg='#2b2b2b')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add header
        self.create_header()
        
        # Add notebook for tabs
        self.create_notebook()
        
        # Force update
        self.root.update()
        
        print("✅ GUI initialized successfully")
    
    def create_header(self):
        """Create the header section"""
        header_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title = tk.Label(header_frame, 
                        text="🛡️ Sec360 by Abhay", 
                        font=('Arial', 24, 'bold'), 
                        bg='#2b2b2b', fg='#4CAF50')
        title.pack()
        
        subtitle = tk.Label(header_frame, 
                          text="Advanced Code Security Analysis Platform", 
                          font=('Arial', 14), 
                          bg='#2b2b2b', fg='#cccccc')
        subtitle.pack()
    
    def create_notebook(self):
        """Create the tabbed interface"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Practice Sessions Tab
        self.practice_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.practice_frame, text="🔒 Practice Sessions")
        self.setup_practice_tab()
        
        # Sessions Log Tab
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="📊 Sessions Log")
        self.setup_logs_tab()
        
        # Scoreboard Tab
        self.scoreboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.scoreboard_frame, text="🏆 Scoreboard")
        self.setup_scoreboard_tab()
    
    def setup_practice_tab(self):
        """Setup practice sessions tab"""
        # User input
        user_frame = tk.Frame(self.practice_frame, bg='#2b2b2b')
        user_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(user_frame, text="User ID:", 
                font=('Arial', 12), bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        
        self.user_entry = tk.Entry(user_frame, font=('Arial', 12), width=20,
                                  bg='#1e1e1e', fg='white', insertbackground='white')
        self.user_entry.pack(side=tk.LEFT, padx=10)
        
        # Start session button
        start_btn = tk.Button(user_frame, text="Start Session", 
                             font=('Arial', 12, 'bold'),
                             bg='#4CAF50', fg='white',
                             command=self.start_session)
        start_btn.pack(side=tk.LEFT, padx=10)
        
        # Chat area
        chat_frame = tk.Frame(self.practice_frame, bg='#2b2b2b')
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.chat_display = tk.Text(chat_frame, height=15, width=80,
                                   bg='#1e1e1e', fg='white', 
                                   insertbackground='white',
                                   font=('Consolas', 10))
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(chat_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_display.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.chat_display.yview)
        
        # Message input
        input_frame = tk.Frame(self.practice_frame, bg='#2b2b2b')
        input_frame.pack(fill=tk.X, pady=10)
        
        self.message_entry = tk.Entry(input_frame, font=('Arial', 12),
                                    bg='#1e1e1e', fg='white', insertbackground='white')
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        send_btn = tk.Button(input_frame, text="Send", 
                           font=('Arial', 12, 'bold'),
                           bg='#2196F3', fg='white',
                           command=self.send_message)
        send_btn.pack(side=tk.RIGHT)
        
        # Add welcome message
        self.chat_display.insert(tk.END, "Welcome to Sec360!\n")
        self.chat_display.insert(tk.END, "Enter your User ID and click 'Start Session' to begin.\n\n")
    
    def setup_logs_tab(self):
        """Setup sessions log tab"""
        info_label = tk.Label(self.logs_frame, 
                             text="📊 Sessions Log - View and analyze your practice sessions",
                             font=('Arial', 16), 
                             bg='#2b2b2b', fg='white')
        info_label.pack(pady=50)
        
        # Add log viewer button
        log_btn = tk.Button(self.logs_frame, text="Open Log Viewer", 
                           font=('Arial', 14, 'bold'),
                           bg='#FF9800', fg='white',
                           command=self.open_log_viewer)
        log_btn.pack(pady=20)
    
    def setup_scoreboard_tab(self):
        """Setup scoreboard tab"""
        info_label = tk.Label(self.scoreboard_frame, 
                             text="🏆 Scoreboard - View user rankings and statistics",
                             font=('Arial', 16), 
                             bg='#2b2b2b', fg='white')
        info_label.pack(pady=50)
        
        # Add scoreboard button
        score_btn = tk.Button(self.scoreboard_frame, text="Open Scoreboard", 
                             font=('Arial', 14, 'bold'),
                             bg='#9C27B0', fg='white',
                             command=self.open_scoreboard)
        score_btn.pack(pady=20)
    
    def start_session(self):
        """Start a practice session"""
        user_id = self.user_entry.get().strip()
        if not user_id:
            self.chat_display.insert(tk.END, "Please enter a User ID first.\n")
            return
        
        self.chat_display.insert(tk.END, f"Starting session for user: {user_id}\n")
        self.chat_display.insert(tk.END, "Session started! You can now send messages.\n\n")
    
    def send_message(self):
        """Send a message"""
        message = self.message_entry.get().strip()
        if not message:
            return
        
        self.chat_display.insert(tk.END, f"You: {message}\n")
        self.chat_display.insert(tk.END, f"AI: Analyzing your message...\n\n")
        
        self.message_entry.delete(0, tk.END)
        self.chat_display.see(tk.END)
    
    def open_log_viewer(self):
        """Open log viewer"""
        self.chat_display.insert(tk.END, "Opening Log Viewer...\n")
    
    def open_scoreboard(self):
        """Open scoreboard"""
        self.chat_display.insert(tk.END, "Opening Scoreboard...\n")
    
    def run(self):
        """Run the application"""
        print("🎯 Sec360 Fixed GUI is running!")
        print("📱 You should see the full interface with tabs and dark theme")
        self.root.mainloop()

if __name__ == "__main__":
    app = Sec360FixedApp()
    app.run()
