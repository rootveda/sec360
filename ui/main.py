#!/usr/bin/env python3
"""
Sec360 by Abhay - Advanced Code Security Analysis Platform
A Zen-inspired application for practicing secure coding
Created by Abhay - Integrates all components: monitoring, scoring, LLM integration, and log viewing
"""

import os
import sys
import json
import time
import datetime
import threading
from typing import Dict, List, Optional
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import subprocess

# Add core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from detection.data_monitor import DataLeakMonitor
from scoring.scoring_system import ScoringSystem
from llm.ollama_client import OllamaClient, LLMSafetyTrainer
from logging_system.log_viewer import LogViewer
from scoreboard.scoreboard_viewer import ScoreboardViewer

class Sec360App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sec360 by Abhay - Advanced Code Security Analysis Platform")
        self.root.geometry("1400x900")
        
        # Initialize components
        self.monitor = DataLeakMonitor()
        self.scoring_system = ScoringSystem()
        self.ollama_client = OllamaClient()
        self.trainer = LLMSafetyTrainer(self.ollama_client)
        
        # Session variables
        self.current_user = None
        self.current_session_id = None
        self.session_logs = []
        self.total_flags_detected = 0
        self.total_messages_analyzed = 0
        self.active_sessions = {}  # Track active sessions by user
        
        self.setup_ui()
        self.check_ollama_status()
        self.load_existing_active_sessions()
        
    
    
    
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame - match log viewer exactly
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Practice tab - match log viewer styling exactly
        self.practice_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.practice_frame, text="Practice Session")
        self.setup_practice_tab()
        
        # Sample Code tab - clean default styling
        self.sample_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sample_frame, text="Sample Code")
        self.setup_sample_tab()
        
        # Logs tab - clean default styling
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="Session Logs")
        self.setup_logs_tab()
        
        # Statistics tab - clean default styling
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        self.setup_stats_tab()
    
        # Active Sessions tab - show session status
        self.sessions_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sessions_frame, text="Active Sessions")
        self.setup_sessions_tab()
    
    def setup_practice_tab(self):
        """Setup the practice session tab"""
        # Top frame for session controls - match log viewer exactly
        top_frame = ttk.Frame(self.practice_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # User ID input - match log viewer exactly
        ttk.Label(top_frame, text="User:").pack(side=tk.LEFT)
        self.user_id_var = tk.StringVar()
        self.user_id_entry = ttk.Entry(top_frame, textvariable=self.user_id_var, width=20)
        self.user_id_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        # Model selection - match log viewer exactly
        ttk.Label(top_frame, text="Model:").pack(side=tk.LEFT)
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(top_frame, textvariable=self.model_var, width=15)
        self.model_combo['values'] = ['llama3.2:3b']
        self.model_combo.pack(side=tk.LEFT, padx=(5, 10))
        
        # Start session button - match log viewer exactly
        self.start_btn = ttk.Button(top_frame, text="Start Session", command=self.start_session)
        self.start_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # End session button - match log viewer exactly
        self.end_btn = ttk.Button(top_frame, text="End Session", command=self.end_session, state=tk.DISABLED)
        self.end_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Session info frame - match log viewer exactly
        info_frame = ttk.LabelFrame(self.practice_frame, text="Session Information")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.session_info_text = tk.Text(info_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.session_info_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Chat frame - match log viewer exactly
        chat_frame = ttk.LabelFrame(self.practice_frame, text="Chat with AI Security Mentor")
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        # Chat display - match log viewer exactly
        self.chat_display = scrolledtext.ScrolledText(chat_frame, height=20, wrap=tk.WORD, state=tk.DISABLED, font=("Arial", 12))
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure text tags - match log viewer exactly (NO custom fonts)
        self.chat_display.tag_configure("user_name", foreground="#FFD700")  # Gold for user names
        self.chat_display.tag_configure("ai_name", foreground="#00FFFF")    # Cyan for AI names
        self.chat_display.tag_configure("flagged", foreground="red")
        self.chat_display.tag_configure("no_flags", foreground="green")
        
        # AI response formatting tags for better readability
        self.chat_display.tag_configure("section_header", foreground="#FF6B6B", font=("Arial", 11, "bold"))  # Light red/coral
        self.chat_display.tag_configure("risk_item", foreground="#FFA500")  # Orange for risk items
        self.chat_display.tag_configure("solution_header", foreground="#4ECDC4", font=("Arial", 11, "bold"))  # Teal
        self.chat_display.tag_configure("code_block", foreground="#98FB98", background="#2D2D2D", font=("Courier", 10))  # Light green code
        self.chat_display.tag_configure("best_practice", foreground="#87CEEB")  # Sky blue for best practices
        self.chat_display.tag_configure("warning", foreground="#FFD700", font=("Arial", 10, "bold"))  # Gold for warnings
        self.chat_display.tag_configure("example_header", foreground="#DDA0DD", font=("Arial", 11, "bold"))  # Plum for examples
        
        # Input frame - match log viewer exactly
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.message_var = tk.StringVar()
        self.message_entry = tk.Text(input_frame, height=8, wrap=tk.WORD)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.message_entry.bind('<Control-Return>', self.send_message)
        
        # Send button - match log viewer exactly
        self.send_btn = ttk.Button(input_frame, text="Send", command=self.send_message)
        self.send_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Clear button - match log viewer exactly
        self.clear_btn = ttk.Button(input_frame, text="Clear Chat", command=self.clear_chat)
        self.clear_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Status frame - match log viewer exactly
        status_frame = ttk.Frame(self.practice_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to start practice session")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT)
        
        # Flag counter frame (center) - match log viewer exactly
        self.flag_counter_var = tk.StringVar()
        self.flag_counter_var.set("")
        self.flag_counter_label = ttk.Label(status_frame, textvariable=self.flag_counter_var)
        self.flag_counter_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Token details frame (right side) - match log viewer exactly
        self.token_details_var = tk.StringVar()
        self.token_details_var.set("")
        self.token_details_label = ttk.Label(status_frame, textvariable=self.token_details_var)
        self.token_details_label.pack(side=tk.RIGHT)
    
    def setup_sample_tab(self):
        """Setup the sample code tab"""
        # Sample code selection - match log viewer exactly
        selection_frame = ttk.Frame(self.sample_frame)
        selection_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(selection_frame, text="Select Sample Code:").pack(side=tk.LEFT)
        self.sample_var = tk.StringVar()
        self.sample_combo = ttk.Combobox(selection_frame, textvariable=self.sample_var, width=30)
        self.sample_combo['values'] = [
            "API Keys and Tokens",
            "Personal Identifiable Information (PII)",
            "Medical Records and Health Information",
            "Internal Infrastructure and Hostnames",
            "Compliance and Regulatory Data"
        ]
        self.sample_combo.pack(side=tk.LEFT, padx=(5, 10))
        self.sample_combo.bind('<<ComboboxSelected>>', self.show_sample_code)
        
        # Load button - match log viewer exactly
        ttk.Button(selection_frame, text="Load Sample", command=self.load_sample_code).pack(side=tk.LEFT)
        
        # Sample code display - match log viewer exactly
        self.sample_display = scrolledtext.ScrolledText(self.sample_frame, wrap=tk.WORD)
        self.sample_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Instructions
        instructions = """
Instructions for Sample Code:
1. Select a sample code file from the dropdown (shows code in viewer)
2. Review the code and identify potential data leaks
3. EDIT the code to remove sensitive information (API keys, PII, etc.)
4. Click "Load Sample" to copy your edited code to Practice tab chat input
5. Ask the AI Security Mentor to help fix any remaining issues
6. The system will monitor your input for flagged content
7. Check the Session Logs tab to see what was flagged
8. Review your score in the Statistics tab

Remember: This is a practice exercise. The sample code contains intentional data leaks
for educational purposes. In real scenarios, never share such sensitive information.

IMPORTANT: Edit the code to remove sensitive data before loading to chat!
        """
        
        self.sample_display.insert(tk.END, instructions)
        # Keep it editable for user to modify sample code
    
    def setup_logs_tab(self):
        """Setup the logs tab"""
        # Log viewer frame - match log viewer exactly
        self.log_viewer_frame = ttk.Frame(self.logs_frame)
        self.log_viewer_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instructions = """
Session Logs:
- View flagged content from your practice sessions
- Analyze patterns in your data sharing behavior
- Identify areas for improvement
- Export logs for further analysis

Click "Open Log Viewer" to access the detailed log viewer interface.
        """
        
        instructions_label = ttk.Label(self.logs_frame, text=instructions, wraplength=600)
        instructions_label.pack(pady=20)
        
        # Open log viewer button
        ttk.Button(self.logs_frame, text="Open Log Viewer", command=self.open_log_viewer).pack(pady=10)
        
        # Open scoreboard button
        ttk.Button(self.logs_frame, text="🏆 Open Live Scoreboard", command=self.open_scoreboard).pack(pady=5)
    
    def setup_stats_tab(self):
        """Setup the statistics tab"""
        # Statistics display - match log viewer exactly
        self.stats_display = scrolledtext.ScrolledText(self.stats_frame, wrap=tk.WORD)
        self.stats_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Refresh button
        ttk.Button(self.stats_frame, text="Refresh Statistics", command=self.refresh_statistics).pack(pady=5)
        
        # Load initial statistics
        self.refresh_statistics()
    
    def setup_sessions_tab(self):
        """Setup the active sessions tab"""
        # Title
        title_label = ttk.Label(self.sessions_frame, text="Session Status Overview", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Sessions display
        self.sessions_display = scrolledtext.ScrolledText(self.sessions_frame, wrap=tk.WORD, height=20)
        self.sessions_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control frame
        control_frame = ttk.Frame(self.sessions_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Refresh button
        ttk.Button(control_frame, text="Refresh Status", command=self.refresh_sessions_status).pack(side=tk.LEFT, padx=5)
        
        # Force end button
        ttk.Button(control_frame, text="Force End All Sessions", command=self.force_end_all_sessions).pack(side=tk.LEFT, padx=5)
        
        # Load initial status
        self.refresh_sessions_status()
    
    def check_ollama_status(self):
        """Check Ollama status and update UI"""
        if self.ollama_client.check_ollama_status():
            models = self.ollama_client.get_available_models()
            self.model_combo['values'] = models
            if models:
                self.model_combo.set(models[0])
            self.status_var.set("Ollama is running")
        else:
            self.status_var.set("Ollama is not running. Please start Ollama service.")
    
    def start_session(self):
        """Start a new practice session"""
        user_id = self.user_id_var.get().strip()
        model_name = self.model_var.get()
        
        if not user_id:
            messagebox.showerror("Error", "Please enter a User name")
            return
        
        if not model_name:
            messagebox.showerror("Error", "Please select a model")
            return
        
        # Check if user already has any session
        if self.check_existing_user_session(user_id):
            messagebox.showerror(
                "User Already Exists", 
                f"User '{user_id}' already has a session.\n\n"
                "Please use a different user name."
            )
            return
        
        # Start practice session
        if self.trainer.start_practice_session(user_id, model_name):
            self.current_user = user_id
            self.current_session_id = self.trainer.current_session_id
            
            # Track active session
            self.active_sessions[user_id.lower()] = {
                'session_id': self.current_session_id,
                'start_time': time.time()
            }
            self.session_logs = []
            
            # Log session start
            self.monitor._log_session_activity(
                f"Practice session started for user: {user_id}",
                self.current_session_id,
                0,
                0
            )
            
            # Update UI
            self.start_btn.config(state=tk.DISABLED)
            self.end_btn.config(state=tk.NORMAL)
            self.user_id_entry.config(state=tk.DISABLED)
            self.model_combo.config(state=tk.DISABLED)
            
            # Update session info
            info = f"User: {user_id}\nModel: {model_name}\nSession ID: {self.current_session_id}\nStatus: Active"
            self.session_info_text.config(state=tk.NORMAL)
            self.session_info_text.delete(1.0, tk.END)
            self.session_info_text.insert(tk.END, info)
            self.session_info_text.config(state=tk.DISABLED)
            
            # Clear chat first
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.insert(tk.END, "Sec360 by Abhay - Practice session started. You can now chat with your AI Security Mentor.\n\n")
            # Auto-scroll to bottom
            self.chat_display.see(tk.END)
            self.chat_display.config(state=tk.DISABLED)
            
            # Send initial greeting from AI Security Mentor
            self.send_initial_greeting(user_id)
            
            self.status_var.set(f"Session started for user: {user_id}")
        else:
            messagebox.showerror("Error", "Failed to start practice session")
    
    def check_existing_user_session(self, user_id: str) -> bool:
        """Check if user already has any session (active or completed)"""
        try:
            # First check in-memory active sessions
            if user_id.lower() in self.active_sessions:
                return True
            
            # Then check session files for ANY session with this user
            logs_dir = os.path.join(os.path.dirname(__file__), '..', 'core', 'logs')
            if not os.path.exists(logs_dir):
                return False
                
            # Check for ANY session files with this user (active or completed)
            for filename in os.listdir(logs_dir):
                if filename.startswith('session_') and filename.endswith('.json'):
                    if user_id.lower() in filename.lower():
                        return True  # User has any session, block new session
            return False
        except Exception:
            return False
    
    def is_session_active(self, session_file: str) -> bool:
        """Check if a session file represents an active session"""
        try:
            import time
            current_time = time.time()
            
            # First check if session was properly ended by looking at last log entry
            with open(session_file, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
                if lines:
                    try:
                        last_log = json.loads(lines[-1])
                        content = last_log.get('content', '').lower()
                        input_preview = last_log.get('input_preview', '').lower()
                        
                        # If last entry is session end, it's not active
                        # Check both content and input_preview fields
                        if ('session completed' in content or 
                            'session ended' in content or 
                            'session force-ended' in content or
                            'session completed' in input_preview or 
                            'session ended' in input_preview or 
                            'session force-ended' in input_preview):
                            return False
                    except json.JSONDecodeError:
                        pass  # Continue to file time check
            
            # Check file modification time (if modified within last 4 hours, consider active)
            file_mtime = os.path.getmtime(session_file)
            if current_time - file_mtime < 14400:  # 4 hours (was 2 hours)
                return True
            
            return False
        except Exception:
            return True  # If can't determine, assume active for safety
    
    def load_existing_active_sessions(self):
        """Load existing active sessions on startup"""
        try:
            logs_dir = os.path.join(os.path.dirname(__file__), '..', 'core', 'logs')
            if not os.path.exists(logs_dir):
                return
                
            for filename in os.listdir(logs_dir):
                if filename.startswith('session_') and filename.endswith('.json'):
                    filepath = os.path.join(logs_dir, filename)
                    if self.is_session_active(filepath):
                        # Extract user from filename
                        # Format: session_session_username_timestamp.json
                        parts = filename.replace('.json', '').split('_')
                        if len(parts) >= 3:
                            user_id = parts[2]  # username is the 3rd part
                            if user_id and user_id not in self.active_sessions:
                                self.active_sessions[user_id.lower()] = {
                                    'session_id': filename.replace('.json', ''),
                                    'start_time': os.path.getmtime(filepath)
                                }
        except Exception as e:
            print(f"Error loading existing sessions: {e}")
    
    def force_end_user_session(self, user_id: str):
        """Force end an existing user session"""
        try:
            logs_dir = os.path.join(os.path.dirname(__file__), '..', 'core', 'logs')
            if not os.path.exists(logs_dir):
                return
                
            # Find the active session file for this user
            session_file = None
            for filename in os.listdir(logs_dir):
                if filename.startswith('session_') and filename.endswith('.json'):
                    if user_id.lower() in filename.lower():
                        filepath = os.path.join(logs_dir, filename)
                        if self.is_session_active(filepath):
                            session_file = filepath
                            break
            
            if session_file:
                # Load session data to get session ID
                try:
                    with open(session_file, 'r') as f:
                        lines = [line.strip() for line in f if line.strip()]
                        if lines:
                            first_log = json.loads(lines[0])
                            session_id = first_log.get('session_id', '')
                            
                            # Create session end entry
                            import time
                            end_entry = {
                                'session_id': session_id,
                                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + time.strftime('%f')[-3:],
                                'flag_type': 'NO_FLAGS', 
                                'content': f'Session force-ended for user: {user_id} (admin action)',
                                'confidence': 1.0,
                                'position': [0, 0],
                                'context': 'Session terminated by force end all sessions',
                                'input_preview': f'Session force-ended for user: {user_id} (admin action)',
                                'potential_flags': 0
                            }
                            
                            # Append the end entry to the session file
                            with open(session_file, 'a') as f:
                                f.write('\n' + json.dumps(end_entry))
                                
                except Exception as e:
                    print(f"Error writing session end entry: {e}")
                
                # Remove from active sessions tracking
                if user_id.lower() in self.active_sessions:
                    del self.active_sessions[user_id.lower()]
                
                print(f"Force-ended session for user: {user_id}")
            else:
                print(f"No active session found for user: {user_id}")
                
        except Exception as e:
            print(f"Error force-ending session for user {user_id}: {e}")
    
    def end_session(self):
        """End the current practice session"""
        if not self.current_session_id:
            return
        
        # Log session end
        self.monitor._log_session_activity(
            f"Session completed for user: {self.current_user}",
            self.current_session_id,
            0,
            0
        )
        
        # Remove from active sessions tracking
        if self.current_user and self.current_user.lower() in self.active_sessions:
            del self.active_sessions[self.current_user.lower()]
        
        # End session
        session_data = self.trainer.end_session()
        
        # Calculate score (but don't show popup)
        if self.session_logs:
            session_score = self.scoring_system.calculate_session_score(
                self.session_logs, 
                self.current_user,
                [self.sample_var.get()] if self.sample_var.get() else []
            )
            
            # Score is calculated and saved, but no popup is shown
            # Users can view their scores in the Statistics tab or Scoreboard
        
        # Clear chat display
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.insert(tk.END, "Session ended. Chat cleared.\n")
        # Auto-scroll to bottom
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Clear input
        self.message_entry.delete(1.0, tk.END)
        
        # Clear session information
        self.session_info_text.config(state=tk.NORMAL)
        self.session_info_text.delete(1.0, tk.END)
        self.session_info_text.insert(tk.END, "No active session")
        self.session_info_text.config(state=tk.DISABLED)
        
        # Reset UI
        self.start_btn.config(state=tk.NORMAL)
        self.end_btn.config(state=tk.DISABLED)
        self.user_id_entry.config(state=tk.NORMAL)
        self.model_combo.config(state=tk.NORMAL)
        
        self.current_user = None
        self.current_session_id = None
        self.session_logs = []
        self.total_flags_detected = 0
        self.total_messages_analyzed = 0
        
        # Clear flag counter
        self.flag_counter_var.set("")
        
        self.status_var.set("Session ended. Chat cleared. Ready to start new session.")
    
    def send_initial_greeting(self, user_id: str):
        """Send initial greeting from AI Assistant when session starts"""
        greeting_message = f"""Hello {user_id}! Welcome to Sec360 by Abhay - your advanced code security analysis session. I'm your AI Security Mentor, here to help you learn how to write secure code and avoid data leaks when using AI tools.

🎯 **How to Use This Practice Module:**

1. **Sample Code Practice:**
   - Go to the "Sample Code" tab
   - Select a sample code file from the dropdown
   - Review the code and identify potential data leaks
   - Edit the code to remove sensitive information (API keys, PII, etc.)
   - Click "Load Sample" to copy your edited code to this chat
   - Ask me to help fix any remaining issues

2. **Code Analysis:**
   - Share any code you're working on
   - I'll analyze it for potential security issues
   - I'll provide suggestions for secure coding practices
   - I'll help you understand what information should not be shared

3. **Learning Objectives:**
   - Identify common data leak patterns
   - Learn secure coding practices
   - Understand compliance requirements
   - Practice with real-world scenarios

4. **Scoring System:**
   - Your session will be scored based on flagged content
   - Check the "Session Logs" tab to see what was flagged
   - Review your score in the "Statistics" tab
   - Aim for zero flags in your final code!

Ready to start? Feel free to ask me questions or share code for analysis!"""
        
        # Add greeting to chat display
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"AI Security Mentor: ", "ai_name")
        self._format_ai_response(greeting_message)
        # Auto-scroll to bottom
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Add to conversation history
        self.trainer.conversation_history.append({"role": "assistant", "content": greeting_message})
    
    def _is_code_like_input(self, user_input: str) -> bool:
        """Check if input looks like code or contains sensitive patterns"""
        input_lower = user_input.lower().strip()
        
        # Skip very short inputs (likely just greetings)
        if len(input_lower) < 10:
            return False
        
        # Skip common greetings and conversational phrases
        greetings = [
            "hello", "hi", "hey", "how are you", "thanks", "thank you",
            "good morning", "good afternoon", "good evening", "bye", "goodbye",
            "what", "how", "why", "when", "where", "who", "can you", "could you",
            "please", "help", "assist", "explain", "tell me", "show me", "analyze"
        ]
        
        for greeting in greetings:
            if input_lower.startswith(greeting):
                return False
        
        # Check for minimum line count (at least 30 lines for meaningful code)
        lines = user_input.split("\n")
        if len(lines) < 30:
            return False
        
        # Check for code-like patterns
        code_indicators = [
            "def ", "class ", "function", "import ", "from ", "return ",
            "if ", "for ", "while ", "try:", "except:", "with ",
            "api_key", "password", "secret", "token", "key",
            "database", "server", "host", "port", "url",
            "email", "phone", "address", "name", "ssn",
            "patient", "medical", "diagnosis", "prescription"
        ]
        
        for indicator in code_indicators:
            if indicator in input_lower:
                return True
        
        # Check for indentation (Python code)
        indented_lines = [line for line in lines if line.startswith("    ") or line.startswith("\t")]
        if len(indented_lines) > 5:  # At least 5 indented lines
            return True
        
        # Check for code structure (functions, classes, etc.)
        code_structure_count = 0
        for line in lines:
            line_stripped = line.strip()
            if (line_stripped.startswith("def ") or 
                line_stripped.startswith("class ") or 
                line_stripped.startswith("import ") or 
                line_stripped.startswith("from ") or
                line_stripped.startswith("if ") or
                line_stripped.startswith("for ") or
                line_stripped.startswith("while ") or
                line_stripped.startswith("try:") or
                line_stripped.startswith("except:") or
                line_stripped.startswith("with ")):
                code_structure_count += 1
        
        if code_structure_count >= 3:  # At least 3 code structure elements
            return True
        
        return False
    
    def send_message(self, event=None):
        """Send a message to the AI Security Mentor"""
        if not self.current_session_id:
            messagebox.showerror("Error", "No active session")
            return
        
        message = self.message_entry.get(1.0, tk.END).strip()
        if not message:
            return
        
        # Monitor the message for data leaks
        flagged_items = self.monitor.analyze_input(message, self.current_session_id)
        
        # Add to session logs
        for item in flagged_items:
            self.session_logs.append({
                "session_id": self.current_session_id,
                "timestamp": item.timestamp.isoformat(),
                "flag_type": item.flag_type.value,
                "content": item.content,
                "confidence": item.confidence,
                "position": item.position,
                "context": item.context
            })
        
        # Display user message (enable temporarily to insert)
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{self.current_user}: ", "user_name")
        self.chat_display.insert(tk.END, f"{message}\n")
        
        # Show flagged items if any (only for code-like input)
        if flagged_items:
            self.chat_display.insert(tk.END, f"⚠️  FLAGGED: {len(flagged_items)} potential data leaks detected\n", "flagged")
            for item in flagged_items:
                self.chat_display.insert(tk.END, f"   - {item.flag_type.value}: {item.content}\n", "flagged")
        elif self._is_code_like_input(message):
            # Only show "NO FLAGS" for code-like input
            self.chat_display.insert(tk.END, f"✅ NO FLAGS DETECTED (0)\n", "no_flags")
        
        # Get AI Security Mentor response
        response, token_info = self.trainer.send_message(message, self.current_user)
        
        # Display AI Security Mentor response with color formatting
        self.chat_display.insert(tk.END, f"AI Security Mentor: ", "ai_name")
        self._format_ai_response(response)
        
        # Auto-scroll to bottom
        self.chat_display.see(tk.END)
        
        # Update token details in status bar if available
        if token_info:
            eval_duration = token_info['eval_duration']/1000000000
            load_duration = token_info['load_duration']/1000000000
            total_duration = token_info['total_duration']/1000000000
            tokens_per_second = token_info['completion_tokens'] / eval_duration if eval_duration > 0 else 0
            
            token_text = f"📊 {token_info['prompt_tokens']}→{token_info['completion_tokens']} ({token_info['total_tokens']} total) | {token_info['model']} | {eval_duration:.2f}s | {tokens_per_second:.1f} tok/s"
            self.token_details_var.set(token_text)
        else:
            self.token_details_var.set("")
        
        # Disable chat display again
        self.chat_display.config(state=tk.DISABLED)
        
        # Clear input
        self.message_entry.delete(1.0, tk.END)
        
        # Update counters (only for code-like input)
        if self._is_code_like_input(message):
            self.total_messages_analyzed += 1
            if flagged_items:
                self.total_flags_detected += len(flagged_items)
        
        # Update status
        if flagged_items:
            self.status_var.set(f"⚠️  {len(flagged_items)} data leaks detected in last message")
        else:
            self.status_var.set("Message sent successfully")
        
        # Update flag counter with session totals (only if we have analyzed messages)
        if self.total_messages_analyzed > 0:
            if self.total_flags_detected > 0:
                self.flag_counter_var.set(f"🚨 {self.total_flags_detected} out of {self.total_messages_analyzed} detected")
            else:
                self.flag_counter_var.set(f"✅ {self.total_flags_detected} out of {self.total_messages_analyzed} detected")
        else:
            self.flag_counter_var.set("")
    
    def clear_chat(self):
        """Clear the chat display"""
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the chat history?"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.insert(tk.END, "Chat cleared. Ready for new conversation.\n")
            # Auto-scroll to bottom
            self.chat_display.see(tk.END)
            self.chat_display.config(state=tk.DISABLED)
    
    
    def show_sample_code(self, event=None):
        """Show sample code in viewer (dropdown selection)"""
        sample_name = self.sample_var.get()
        if not sample_name:
            return
        
        # Map sample names to files
        sample_files = {
            "API Keys and Tokens": "api_keys_sample.py",
            "Personal Identifiable Information (PII)": "pii_sample.py",
            "Medical Records and Health Information": "medical_records_sample.py",
            "Internal Infrastructure and Hostnames": "internal_infrastructure_sample.py",
            "Compliance and Regulatory Data": "compliance_sample.py"
        }
        
        filename = sample_files.get(sample_name)
        if filename:
            filepath = os.path.join("data", "samples", filename)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Show in sample display (editable for user to modify)
                self.sample_display.config(state=tk.NORMAL)
                self.sample_display.delete(1.0, tk.END)
                self.sample_display.insert(tk.END, content)
                # Keep it editable - don't disable
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load sample code: {e}")
    
    def load_sample_code(self, event=None):
        """Load edited sample code into practice tab chat input (button click)"""
        sample_name = self.sample_var.get()
        if not sample_name:
            messagebox.showwarning("Warning", "Please select a sample code first")
            return
        
        # Get the edited content from the sample display
        edited_content = self.sample_display.get(1.0, tk.END).strip()
        
        if not edited_content:
            messagebox.showwarning("Warning", "No content to load. Please select a sample code first.")
            return
        
        # Load the edited content into chat input for practice
        self.message_entry.delete(1.0, tk.END)
        self.message_entry.insert(1.0, edited_content)
        
        # Switch to practice tab to show the loaded content
        self.notebook.select(0)  # Practice tab is index 0
        
        messagebox.showinfo("Sample Loaded", f"Edited sample code '{sample_name}' loaded into chat input. You can now send it to the AI Security Mentor for analysis.")
    
    def open_log_viewer(self):
        """Open the log viewer in a separate window"""
        try:
            # Start log viewer in a separate process
            subprocess.Popen([sys.executable, "core/logging_system/log_viewer.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open log viewer: {e}")
    
    def open_scoreboard(self):
        """Open the live scoreboard in a separate window"""
        try:
            # Get the project root directory
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # Use the scoreboard launcher script
            launcher_script = os.path.join(project_root, "scoreboard_launcher.py")
            
            if os.path.exists(launcher_script):
                # Start scoreboard viewer using the launcher
                subprocess.Popen([sys.executable, launcher_script], 
                               cwd=project_root)
                print("Scoreboard launched successfully")
            else:
                # Fallback to direct scoreboard viewer
                scoreboard_script = os.path.join(project_root, "core", "scoreboard", "scoreboard_viewer.py")
                if os.path.exists(scoreboard_script):
                    subprocess.Popen([sys.executable, scoreboard_script], 
                                   cwd=project_root)
                    print("Scoreboard launched successfully (fallback)")
                else:
                    messagebox.showerror("Error", "Scoreboard launcher not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open scoreboard: {e}")
            print(f"Scoreboard launch error: {e}")
    
    def refresh_statistics(self):
        """Refresh statistics display"""
        self.stats_display.delete(1.0, tk.END)
        
        # Get overall statistics
        stats = self.scoring_system.get_statistics()
        
        if "message" in stats:
            self.stats_display.insert(tk.END, stats["message"])
        else:
            self.stats_display.insert(tk.END, "=== Overall Statistics ===\n")
            self.stats_display.insert(tk.END, f"Total Sessions: {stats['total_sessions']}\n")
            self.stats_display.insert(tk.END, f"Total Users: {stats['total_users']}\n")
            self.stats_display.insert(tk.END, f"Average Score: {stats['average_score']:.1f}\n")
            self.stats_display.insert(tk.END, f"Best Score: {stats['best_overall_score']:.1f}\n")
            self.stats_display.insert(tk.END, f"Worst Score: {stats['worst_overall_score']:.1f}\n\n")
            
            self.stats_display.insert(tk.END, "=== Score Distribution ===\n")
            for level, count in stats['score_distribution'].items():
                self.stats_display.insert(tk.END, f"{level}: {count}\n")
            
    def refresh_sessions_status(self):
        """Refresh sessions status display"""
        self.sessions_display.delete(1.0, tk.END)
        
        # Get all session files
        logs_dir = os.path.join(os.path.dirname(__file__), '..', 'core', 'logs')
        if not os.path.exists(logs_dir):
            self.sessions_display.insert(tk.END, "No logs directory found.\n")
            return
        
        # Find all session files
        session_files = []
        for filename in os.listdir(logs_dir):
            if filename.startswith('session_') and filename.endswith('.json'):
                session_files.append(os.path.join(logs_dir, filename))
        
        if not session_files:
            self.sessions_display.insert(tk.END, "No session files found.\n")
            return
        
        # Sort by modification time (newest first)
        session_files.sort(key=os.path.getmtime, reverse=True)
        
        # Display session status
        self.sessions_display.insert(tk.END, "=== Session Status Overview ===\n\n")
        
        active_count = 0
        inactive_count = 0
        
        for session_file in session_files:
            filename = os.path.basename(session_file)
            # Extract user from filename: session_session_username_timestamp.json
            parts = filename.replace('.json', '').split('_')
            if len(parts) >= 3:
                user_id = parts[2]
                session_id = filename.replace('.json', '')
            else:
                user_id = "unknown"
                session_id = filename.replace('.json', '')
            
            # Check if session is active
            is_active = self.is_session_active(session_file)
            status = "🟢 ACTIVE" if is_active else "🔴 INACTIVE"
            
            if is_active:
                active_count += 1
            else:
                inactive_count += 1
            
            # Get file modification time
            import time
            file_mtime = os.path.getmtime(session_file)
            mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_mtime))
            
            # Get session duration if available
            duration = self.get_session_duration(session_file)
            
            self.sessions_display.insert(tk.END, f"User: {user_id}\n")
            self.sessions_display.insert(tk.END, f"Session ID: {session_id}\n")
            self.sessions_display.insert(tk.END, f"Status: {status}\n")
            self.sessions_display.insert(tk.END, f"Last Modified: {mod_time}\n")
            if duration:
                self.sessions_display.insert(tk.END, f"Duration: {duration}\n")
            self.sessions_display.insert(tk.END, f"File: {filename}\n")
            self.sessions_display.insert(tk.END, "-" * 50 + "\n\n")
        
        # Summary
        self.sessions_display.insert(tk.END, f"=== Summary ===\n")
        self.sessions_display.insert(tk.END, f"Total Sessions: {len(session_files)}\n")
        self.sessions_display.insert(tk.END, f"Active Sessions: {active_count}\n")
        self.sessions_display.insert(tk.END, f"Inactive Sessions: {inactive_count}\n")
        
        if active_count > 0:
            self.sessions_display.insert(tk.END, f"\n⚠️  {active_count} user(s) have active sessions and cannot start new ones.\n")
            self.sessions_display.insert(tk.END, "Users must end their current session before starting a new one.\n")
    
    def get_session_duration(self, session_file: str) -> str:
        """Get session duration from log file"""
        try:
            with open(session_file, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
                if len(lines) < 2:
                    return None
                
                # Get first and last timestamps
                first_log = json.loads(lines[0])
                last_log = json.loads(lines[-1])
                
                first_time = datetime.datetime.fromisoformat(first_log['timestamp'])
                last_time = datetime.datetime.fromisoformat(last_log['timestamp'])
                
                duration = last_time - first_time
                total_seconds = int(duration.total_seconds())
                
                if total_seconds < 60:
                    return f"{total_seconds} seconds"
                elif total_seconds < 3600:
                    minutes = total_seconds // 60
                    seconds = total_seconds % 60
                    return f"{minutes}m {seconds}s"
                else:
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    return f"{hours}h {minutes}m"
        except Exception:
            return None
    
    def force_end_all_sessions(self):
        """Force end all active sessions"""
        response = messagebox.askyesno(
            "Force End All Sessions",
            "This will force end ALL active sessions.\n\n"
            "Are you sure you want to continue?\n"
            "This action cannot be undone."
        )
        
        if not response:
            return
        
        # Find all active sessions
        logs_dir = os.path.join(os.path.dirname(__file__), '..', 'core', 'logs')
        if not os.path.exists(logs_dir):
            messagebox.showwarning("Error", "Logs directory not found")
            return
        
        ended_count = 0
        for filename in os.listdir(logs_dir):
            if filename.startswith('session_') and filename.endswith('.json'):
                filepath = os.path.join(logs_dir, filename)
                if self.is_session_active(filepath):
                    # Extract user from filename: handle both formats
                    # Expected: session_session_USERNAME_TIMESTAMP.json
                    # Malformed: session_session_session_USERNAME_TIMESTAMP.json  
                    parts = filename.replace('.json', '').split('_')
                    user_id = None
                    
                    if len(parts) >= 4:
                        # Check if it's the standard format
                        if parts[0] == 'session' and parts[1] == 'session':
                            if len(parts) == 4:  # session_session_USERNAME_TIMESTAMP
                                user_id = parts[2]
                            elif len(parts) >= 5 and parts[2] == 'session':  # malformed with extra 'session'
                                user_id = parts[3]
                            else:  # other standard format
                                user_id = parts[2]
                    
                    if user_id:
                        print(f"Force ending session for user: {user_id} from file: {filename}")
                        self.force_end_user_session(user_id)
                        ended_count += 1
                    else:
                        print(f"Skipping file with unexpected format: {filename} (parts: {parts})")
        
        # Clear active sessions tracking
        self.active_sessions.clear()
        
        # Refresh display
        self.refresh_sessions_status()
        
        messagebox.showinfo(
            "Sessions Ended",
            f"Force ended {ended_count} active session(s).\n\n"
            "All users can now start new sessions."
        )
        
        # Get leaderboard
        leaderboard = self.scoring_system.get_leaderboard()
        if leaderboard:
            self.stats_display.insert(tk.END, "\n=== Leaderboard ===\n")
            for i, user in enumerate(leaderboard, 1):
                self.stats_display.insert(tk.END, 
                    f"{i}. {user['user_id']}: {user['average_score']:.1f} "
                    f"({user['total_sessions']} sessions)\n")
    
    def _format_ai_response(self, response: str):
        """Format AI response with color coding for better readability"""
        import re
        
        lines = response.split('\n')
        
        for line in lines:
            line_with_newline = line + '\n'
            
            # Section headers (bold text with **text:** pattern)
            if re.match(r'^\*\*[^*]+:\*\*', line):
                self.chat_display.insert(tk.END, line_with_newline, "section_header")
            
            # Risk items (numbered items starting with numbers)
            elif re.match(r'^\s*\d+\.\s+\*\*', line):
                self.chat_display.insert(tk.END, line_with_newline, "risk_item")
            
            # Solution headers (like "Practical Solutions:")
            elif "Solutions:" in line or "Practices:" in line or "Example:" in line:
                self.chat_display.insert(tk.END, line_with_newline, "solution_header")
            
            # Code blocks (lines with ```python or indented code)
            elif line.strip().startswith('```') or (line.startswith('    ') and any(keyword in line for keyword in ['import', 'def', '=', 'return', 'print'])):
                self.chat_display.insert(tk.END, line_with_newline, "code_block")
            
            # Best practices (bullet points with *)
            elif re.match(r'^\s*\*\s+', line):
                self.chat_display.insert(tk.END, line_with_newline, "best_practice")
            
            # Warnings and important notes
            elif any(keyword in line.lower() for keyword in ['warning', 'important', 'note:', 'caution']):
                self.chat_display.insert(tk.END, line_with_newline, "warning")
            
            # Example headers
            elif "Example" in line and ":" in line:
                self.chat_display.insert(tk.END, line_with_newline, "example_header")
            
            # Default text
            else:
                self.chat_display.insert(tk.END, line_with_newline)
        
        # Add extra newline for spacing
        self.chat_display.insert(tk.END, "\n")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("core/logs", exist_ok=True)
    os.makedirs("core", exist_ok=True)
    
    # Start the application
    app = Sec360App()
    app.run()
