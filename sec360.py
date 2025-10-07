#!/usr/bin/env python3
"""
Sec360 by Abhay - Advanced Code Security Analysis Platform
Built for structured security compliance analysis using AI-powered detection.
Includes all Sec360 UI components with enhanced analysis capabilities.
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
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

# Sec360 Analysis Components
from analysis.ollama_analyzer import OllamaAnalyzer
from analysis.json_parser import JsonParser
from analysis.risk_calculator import RiskCalculator
from practice_session_manager import PracticeSessionManager

# Sec360 Components (for full UI functionality)
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
        
        # Apply dark theme
        self.root.configure(bg='#2b2b2b')
        
        # Initialize Sec360 Analysis Components
        self.ollama_client = OllamaClient()
        self.analyzer = OllamaAnalyzer(self.ollama_client)
        self.json_parser = JsonParser()
        self.risk_calculator = RiskCalculator()
        self.practice_manager = PracticeSessionManager(self, self.ollama_client, self.analyzer, self.json_parser)
        
        # Initialize Sec360 Components (for full UI functionality)
        self.monitor = DataLeakMonitor()
        self.scoring_system = ScoringSystem()
        self.trainer = LLMSafetyTrainer(self.ollama_client)
        # Note: LogViewer and ScoreboardViewer are not auto-started
        # They are launched on-demand from the UI buttons
        
        # Session variables
        self.current_user = None
        self.current_session_id = None
        self.analysis_history = []
        
        # Practice session variables (managed by PracticeSessionManager)
        self.active_analyses = {}
        self.session_logs = []
        self.total_flags_detected = 0
        self.total_messages_analyzed = 0
        self.active_sessions = {}  # Track active sessions by user
        
        self.setup_ui()
        self.check_ollama_status()
        self.load_existing_active_sessions()
    
    def setup_practice_tab(self):
        """Setup the practice session tab (from Sec360)"""
        # Top frame for session controls
        top_frame = ttk.Frame(self.practice_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # User ID input
        ttk.Label(top_frame, text="User:").pack(side=tk.LEFT)
        self.practice_user_id_var = tk.StringVar()
        self.practice_user_id_entry = ttk.Entry(top_frame, textvariable=self.practice_user_id_var, width=20)
        self.practice_user_id_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        # Model selection
        ttk.Label(top_frame, text="Model:").pack(side=tk.LEFT)
        self.practice_model_var = tk.StringVar(value="llama3.2:3b")
        self.practice_model_combo = ttk.Combobox(top_frame, textvariable=self.practice_model_var, width=15, state="readonly")
        self.practice_model_combo['values'] = ['llama3.2:3b']
        self.practice_model_combo.pack(side=tk.LEFT, padx=(5, 10))
        
        # Start session button
        self.practice_start_btn = ttk.Button(top_frame, text="Start Session", command=self.start_practice_session)
        self.practice_start_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # End session button
        self.practice_end_btn = ttk.Button(top_frame, text="End Session", command=self.end_practice_session, state=tk.DISABLED)
        self.practice_end_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Timer toggle button
        self.timer_enabled_var = tk.BooleanVar(value=True)  # Default: enabled
        self.timer_toggle_btn = ttk.Checkbutton(top_frame, text="⏰ Auto-end (5min)", 
                                               variable=self.timer_enabled_var,
                                               command=self.on_timer_toggle)
        self.timer_toggle_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Session info frame
        info_frame = ttk.LabelFrame(self.practice_frame, text="Session Information")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.practice_session_info_text = tk.Text(info_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.practice_session_info_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Chat frame
        chat_frame = ttk.LabelFrame(self.practice_frame, text="Chat with AI Security Mentor")
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        # Chat display
        self.practice_chat_display = scrolledtext.ScrolledText(chat_frame, height=20, wrap=tk.WORD, state=tk.DISABLED, font=("Arial", 12))
        self.practice_chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure text tags
        self.practice_chat_display.tag_configure("user_name", foreground="#FFD700")
        self.practice_chat_display.tag_configure("ai_name", foreground="#00FFFF")
        self.practice_chat_display.tag_configure("ai_response", foreground="#90EE90")  # Light green for AI responses
        self.practice_chat_display.tag_configure("code_suggestion", foreground="#FFA500", font=("Courier", 10, "bold"))  # Orange for code suggestions
        self.practice_chat_display.tag_configure("security_tip", foreground="#87CEEB", font=("Helvetica", 10, "italic"))  # Sky blue for security tips
        self.practice_chat_display.tag_configure("flagged", foreground="red")
        self.practice_chat_display.tag_configure("no_flags", foreground="green")
        
        # Input frame
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.practice_message_var = tk.StringVar()
        self.practice_message_entry = tk.Text(input_frame, height=8, wrap=tk.WORD)
        self.practice_message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.practice_message_entry.bind('<Control-Return>', self.send_practice_message)
        
        # Send button
        self.practice_send_btn = ttk.Button(input_frame, text="Send", command=self.send_practice_message)
        self.practice_send_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Stop button (initially disabled)
        self.practice_stop_btn = ttk.Button(input_frame, text="Stop", command=self.stop_practice_thinking, state=tk.DISABLED)
        self.practice_stop_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Clear button
        self.practice_clear_btn = ttk.Button(input_frame, text="Clear Chat", command=self.clear_practice_chat)
        self.practice_clear_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Status frame
        status_frame = ttk.Frame(self.practice_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.practice_status_var = tk.StringVar()
        self.practice_status_var.set("Ready to start practice session")
        self.practice_status_label = ttk.Label(status_frame, textvariable=self.practice_status_var)
        self.practice_status_label.pack(side=tk.LEFT)
        
        # Flag counter frame
        self.practice_flag_counter_var = tk.StringVar()
        self.practice_flag_counter_var.set("")
        self.practice_flag_counter_label = ttk.Label(status_frame, textvariable=self.practice_flag_counter_var)
        self.practice_flag_counter_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Token details frame
        self.practice_token_details_var = tk.StringVar()
        self.practice_token_details_var.set("")
        self.practice_token_details_label = ttk.Label(status_frame, textvariable=self.practice_token_details_var)
        self.practice_token_details_label.pack(side=tk.RIGHT)
    
    def setup_sample_tab(self):
        """Setup the sample code tab (from Sec360)"""
        # Sample code selection
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
        
        # Load button
        ttk.Button(selection_frame, text="Load Sample To Practice", command=self.load_sample_code).pack(side=tk.LEFT)
        
        # Sample code display
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
    
    def setup_logs_tab(self):
        """Setup the logs tab (from Sec360)"""
        # Instructions
        instructions = """
Session Logs:
- View flagged content from your practice sessions
- Analyze patterns in your data sharing behavior
- Identify areas for improvement
- Export logs for further analysis

Choose your log viewer:
• Enhanced Log Viewer: Shows detailed field names, data values, and complete risk calculations
• Risk Score Details: Shows basic session information and risk scores
        """
        
        instructions_label = ttk.Label(self.logs_frame, text=instructions, wraplength=600)
        instructions_label.pack(pady=20)
        
        # Create button frame for better layout
        button_frame = ttk.Frame(self.logs_frame)
        button_frame.pack(pady=10)
        
        # Enhanced log viewer button (NEW - shows detailed field names and data values)
        ttk.Button(button_frame, text="🔍 Enhanced Log Viewer", 
                  command=self.open_enhanced_log_viewer).pack(pady=5, padx=10, side=tk.LEFT)
        
        # Risk score details button (RENAMED - original log viewer)
        ttk.Button(button_frame, text="📊 Risk Score Details", 
                  command=self.open_log_viewer).pack(pady=5, padx=10, side=tk.LEFT)
        
        # Open scoreboard button
        ttk.Button(self.logs_frame, text="🏆 Open Live Scoreboard", command=self.open_scoreboard).pack(pady=5)
    
    def setup_stats_tab(self):
        """Setup the statistics tab (from Sec360)"""
        # Statistics display
        self.stats_display = scrolledtext.ScrolledText(self.stats_frame, wrap=tk.WORD)
        self.stats_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Refresh button
        ttk.Button(self.stats_frame, text="Refresh Statistics", command=self.refresh_statistics).pack(pady=5)
        
        # Load initial statistics
        self.refresh_statistics()
    
    def setup_sessions_tab(self):
        """Setup the active sessions tab (from Sec360)"""
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
        
        # View Active Sessions button
        ttk.Button(control_frame, text="View Active Sessions", command=self._show_active_sessions).pack(side=tk.LEFT, padx=5)
        
        # Force end button
        ttk.Button(control_frame, text="Force End All Sessions", command=self.force_end_all_sessions).pack(side=tk.LEFT, padx=5)
        
        # Load initial sessions
        self.refresh_sessions_status()
        
    def setup_ui(self):
        """Setup the user interface with all Sec360 tabs plus enhanced analysis"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Sec360 Analysis tab (disabled - can be re-enabled later)
        # self.analysis_frame = ttk.Frame(self.notebook)
        # self.notebook.add(self.analysis_frame, text="🔍 Sec360 Analysis")
        # self.setup_analysis_tab()
        
        # Practice Session tab (from Sec360)
        self.practice_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.practice_frame, text="🎯 Practice Session")
        self.setup_practice_tab()
        
        # Sample Code tab (from Sec360)
        self.sample_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sample_frame, text="📝 Sample Code")
        self.setup_sample_tab()
        
        # Session Logs tab (from Sec360)
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="📋 Session Logs")
        self.setup_logs_tab()
        
        # Statistics tab (from Sec360)
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="📊 Statistics")
        self.setup_stats_tab()
        
        # Active Sessions tab (from Sec360)
        self.sessions_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sessions_frame, text="👥 Active Sessions")
        self.setup_sessions_tab()
        
        # Analysis History tab
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="📖 Analysis History")
        self.setup_history_tab()
        
        # System Status tab
        self.status_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.status_frame, text="⚙️ System Status")
        self.setup_status_tab()
    
    def setup_analysis_tab(self):
        """Setup the code analysis tab"""
        # Top frame for controls
        top_frame = ttk.Frame(self.analysis_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # User ID input
        ttk.Label(top_frame, text="User:").pack(side=tk.LEFT, padx=(0, 5))
        self.user_id_var = tk.StringVar()
        self.user_id_entry = ttk.Entry(top_frame, textvariable=self.user_id_var, width=20)
        self.user_id_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Model selection
        ttk.Label(top_frame, text="Model:").pack(side=tk.LEFT, padx=(10, 5))
        self.model_var = tk.StringVar(value="llama3.2:3b")
        self.model_combo = ttk.Combobox(top_frame, textvariable=self.model_var, 
                                       values=["llama3.2:3b", "llama3.2:1b", "gemma2:2b"], 
                                       width=15, state="readonly")
        self.model_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Start session button
        self.start_btn = ttk.Button(top_frame, text="🚀 Start Session", 
                                   command=self.start_session)
        self.start_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # End session button
        self.end_btn = ttk.Button(top_frame, text="⏹️ End Session", 
                                 command=self.end_session, state=tk.DISABLED)
        self.end_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Spacer
        ttk.Label(top_frame, text="    ").pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Status label
        self.status_label = ttk.Label(top_frame, text="Ready", foreground="#00ff00")
        self.status_label.pack(side=tk.RIGHT)
        
        # Code input area
        code_frame = ttk.LabelFrame(self.analysis_frame, text="Code Input", padding=10)
        code_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Code text area with scrollbar
        self.code_text = scrolledtext.ScrolledText(code_frame, wrap=tk.WORD, height=20, 
                                                  font=("Consolas", 10), bg='#1e1e1e', fg='#ffffff',
                                                  insertbackground='#ffffff')
        self.code_text.pack(fill=tk.BOTH, expand=True)
        
        # Analysis controls frame
        controls_frame = ttk.Frame(self.analysis_frame)
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Load sample button
        ttk.Button(controls_frame, text="📁 Load Sample", 
                  command=self.load_sample_code).pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        ttk.Button(controls_frame, text="🗑️ Clear", 
                  command=self.clear_code).pack(side=tk.LEFT, padx=(0, 10))
        
        # Analyze button
        self.analyze_btn = ttk.Button(controls_frame, text="🔍 Analyze Code", 
                                     command=self.analyze_code, state=tk.DISABLED)
        self.analyze_btn.pack(side=tk.RIGHT)
        
        # Results display area
        results_frame = ttk.LabelFrame(self.analysis_frame, text="Analysis Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Results text area with scrollbar
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=15, 
                                                     font=("Consolas", 10), state=tk.DISABLED,
                                                     bg='#1e1e1e', fg='#ffffff')
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Results controls frame
        results_controls_frame = ttk.Frame(self.analysis_frame)
        results_controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Export button
        ttk.Button(results_controls_frame, text="💾 Export Results", 
                  command=self.export_results).pack(side=tk.LEFT, padx=(0, 10))
        
        # Copy button
        ttk.Button(results_controls_frame, text="📋 Copy Results", 
                  command=self.copy_results).pack(side=tk.LEFT)
    
    def setup_results_tab(self):
        """Setup the analysis results tab"""
        # Results display area
        results_text_frame = ttk.Labelframe(self.results_frame, text="Analysis Results", padding=10)
        results_text_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 10))
        
        self.results_text = scrolledtext.ScrolledText(results_text_frame, wrap=tk.WORD, 
                                                     font=("Consolas", 10), state=tk.DISABLED)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Export controls
        export_frame = ttk.Frame(self.results_frame)
        export_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(export_frame, text="💾 Export Results", 
                  command=self.export_results).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(export_frame, text="📋 Copy Results", 
                  command=self.copy_results).pack(side=tk.RIGHT, padx=(0, 10))
    
    def setup_history_tab(self):
        """Setup the analysis history tab"""
        # History listbox
        history_frame = ttk.Labelframe(self.history_frame, text="Analysis History", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 10))
        
        # Create treeview for history
        columns = ("Timestamp", "User", "Model", "Risk Score", "Lines")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.history_tree.heading("Timestamp", text="Timestamp")
        self.history_tree.heading("User", text="User")
        self.history_tree.heading("Model", text="Model")
        self.history_tree.heading("Risk Score", text="Risk Score")
        self.history_tree.heading("Lines", text="Lines")
        
        self.history_tree.pack(fill=tk.BOTH, expand=True)
        
        # Double-click to view analysis
        self.history_tree.bind("<Double-1>", self.view_history_item)
        
        # Controls
        history_controls = ttk.Frame(self.history_frame)
        history_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(history_controls, text="🔄 Refresh", 
                  command=self.refresh_history).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(history_controls, text="🗑️ Clear History", 
                  command=self.clear_history).pack(side=tk.LEFT)
    
    def setup_status_tab(self):
        """Setup the system status tab"""
        # Status display
        status_text_frame = ttk.Labelframe(self.status_frame, text="System Status", padding=10)
        status_text_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 10))
        
        self.status_text = scrolledtext.ScrolledText(status_text_frame, wrap=tk.WORD, 
                                                    font=("Consolas", 10), state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        control_frame = ttk.Frame(self.status_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(control_frame, text="🔄 Refresh Status", 
                  command=self.refresh_status).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="🚀 Test Connection", 
                  command=self.test_connection).pack(side=tk.LEFT)
        
        # Periodic status updates
        self.update_status_periodically()
    
    def start_session(self):
        """Start a new analysis session"""
        user_id = self.user_id_var.get().strip()
        if not user_id:
            messagebox.showerror("Error", "Please enter a user ID")
            return
        
        self.current_user = user_id
        self.current_session_id = f"session_{user_id}_{int(time.time())}"
        
        # Update UI
        self.start_btn.config(text="Session Active", state=tk.DISABLED)
        self.end_btn.config(state=tk.NORMAL)
        self.user_id_entry.config(state=tk.DISABLED)
        self.analyze_btn.config(state=tk.NORMAL)
        if hasattr(self, 'status_label'):
            self.status_label.config(text=f"Session: {user_id}", foreground="#00bfff")
    
    def end_session(self):
        """End the current analysis session"""
        if hasattr(self, 'current_session_id') and self.current_session_id:
            # Reset UI
            self.start_btn.config(text="🚀 Start Session", state=tk.NORMAL)
            self.end_btn.config(state=tk.DISABLED)
            self.analyze_btn.config(state=tk.DISABLED)
            self.user_id_entry.config(state=tk.NORMAL)
            
            # Clear session data
            session_user = self.current_user
            self.current_user = None
            self.current_session_id = None
            
            # Update status
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Ready", foreground="#00ff00")
            
            # Clear results
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.config(state=tk.DISABLED)
            
            messagebox.showinfo("Session Ended", f"Analysis session ended for user: {session_user}")
        else:
            messagebox.showwarning("Warning", "No active session to end")
    
    def analyze_code(self):
        """Analyze the entered code"""
        code_text = self.code_text.get(1.0, tk.END).strip()
        if not code_text:
            messagebox.showerror("Error", "Please enter code to analyze")
            return
        
        if not self.current_user:
            messagebox.showerror("Error", "Please start a session first")
            
        model = self.model_var.get()
        
        # Update UI
        self.analyze_btn.config(state=tk.DISABLED, text="🔍 Analyzing...")
        if hasattr(self, 'status_label'):
            self.status_label.config(text="Analyzing code...", foreground="#ffa500")
        
        # Run analysis in thread
        analysis_thread = threading.Thread(
            target=self._run_analysis_thread,
            args=(code_text, model)
        )
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def _run_analysis_thread(self, code_text: str, model: str):
        """Run analysis in separate thread"""
        try:
            # Analyze code
            raw_result = self.analyzer.analyze_code(code_text, model)
            
            # Update UI in main thread
            self.root.after(0, self._handle_analysis_result, raw_result)
            
        except Exception as e:
            error_msg = f"Analysis error: {str(e)}"
            self.root.after(0, self._handle_analysis_error, error_msg)
    
    def _handle_analysis_result(self, raw_result: Dict):
        """Handle analysis result in main thread"""
        try:
            if not raw_result.get('success', False):
                self._handle_analysis_error(raw_result.get('error', 'Unknown error'))
                return
            
            # Parse the raw response to extract JSON data
            table_data = raw_result.get('analysis_table')
            if not table_data:
                # Try to parse JSON from raw response
                try:
                    json_data = self.json_parser.parse_json_response(raw_result['raw_response'])
                    table_data = json_data  # JSON parser already validates
                except Exception as e:
                    self._handle_analysis_error(f"Failed to parse JSON response: {str(e)}")
                    return
            
            if not table_data:
                self._handle_analysis_error("Failed to parse analysis data")
                return
            
            # Calculate comprehensive risk analysis
            risk_analysis = self.risk_calculator.calculate_risk_score(table_data)
            
            # Store in history
            analysis_record = {
                'session_id': raw_result['session_id'],
                'timestamp': raw_result['timestamp'],
                'user': self.current_user,
                'model': raw_result['model_used'],
                'code_length': raw_result['code_length'],
                'table_data': table_data,
                'risk_analysis': risk_analysis,
                'raw_result': raw_result
            }
            
            self.analysis_history.append(analysis_record)
            
            # Display results
            self._display_results(table_data, risk_analysis, raw_result)
            
            # Update history
            self._refresh_history_display()
            
        except Exception as e:
            self._handle_analysis_error(f"Result processing error: {str(e)}")
        finally:
            self._reset_analysis_ui()
    
    def _handle_analysis_error(self, error_msg: str):
        """Handle analysis error"""
        messagebox.showerror("Analysis Error", error_msg)
        self._reset_analysis_ui()
    
    def _display_results(self, table_data: Dict, risk_analysis: Dict, raw_result: Dict):
        """Display analysis results"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        # Format results
        results_content = self._format_analysis_results(table_data, risk_analysis, raw_result)
        
        self.results_text.insert(1.0, results_content)
        self.results_text.config(state=tk.DISABLED)
        
        # Switch to results tab
        self.notebook.select(1)
    
    def _format_analysis_results(self, table_data: Dict, risk_analysis: Dict, raw_result: Dict) -> str:
        """Format analysis results for display"""
        output = []
        
        # Header
        output.append("=" * 70)
        output.append("SEC360 ANALYSIS RESULTS")
        output.append("=" * 70)
        output.append(f"Session: {raw_result['session_id']}")
        output.append(f"Timestamp: {raw_result['timestamp']}")
        output.append(f"User: {self.current_user}")
        output.append(f"Model: {raw_result['model_used']}")
        output.append("")
        
        # Human-readable Analysis Summary
        output.append("ANALYSIS SUMMARY:")
        output.append("-" * 50)
        human_readable = self._create_human_readable_table(table_data)
        output.append(human_readable)
        output.append("")
        
        # Risk Assessment
        output.append("RISK ASSESSMENT:")
        output.append("-" * 30)
        output.append(f"Risk Score: {risk_analysis['risk_score']}/100")
        output.append(f"Risk Level: {risk_analysis['risk_level'].upper()}")
        output.append(f"Confidence: {risk_analysis['confidence']:.2f}")
        output.append("")
        
        # Contributing Factors
        output.append("CONTRIBUTING FACTORS:")
        output.append("-" * 25)
        for factor in risk_analysis['contributing_factors']:
            output.append(f"• {factor}")
        output.append("")
        
        # Recommendations
        output.append("RECOMMENDATIONS:")
        output.append("-" * 18)
        for rec in risk_analysis['recommendations']:
            output.append(f"• {rec}")
        output.append("")
        
        # Summary Points
        summary_points = self.json_parser.extract_summary(table_data)
        output.append("SUMMARY:")
        output.append("-" * 8)
        for point in summary_points:
            output.append(point)
        output.append("")
        
        # Detailed Analysis Data (in code block)
        output.append("DETAILED ANALYSIS DATA:")
        output.append("-" * 30)
        output.append("```")
        analysis_str = self.json_parser.format_analysis_data(table_data)
        output.append(analysis_str)
        output.append("```")
        output.append("")
        
        # Raw Response (formatted JSON in code block)
        output.append("RAW ANALYSIS DATA:")
        output.append("-" * 25)
        output.append("```json")
        formatted_json = self.json_parser.format_json_for_display(raw_result.get('raw_response', 'No response available'))
        output.append(formatted_json)
        output.append("```")
        
        return "\n".join(output)
    
    def _create_human_readable_table(self, table_data: Dict) -> str:
        """Create a human-readable summary table"""
        lines = table_data.get('lines', 0)
        sensitive_fields = table_data.get('sensitive_fields', 0)
        sensitive_data = table_data.get('sensitive_data', 0)
        pii = table_data.get('pii', 0)
        hepa = table_data.get('hepa', 0)
        medical = table_data.get('medical', 0)
        compliance_api = table_data.get('compliance_api', 0)
        risk_score = table_data.get('risk_score', 0)
        
        # Create readable summary
        summary_lines = [
            f"📊 Code Analysis: {lines} lines of code analyzed",
            f"🔍 Sensitive Fields: {sensitive_fields} potential security fields identified",
            f"⚠️  Sensitive Data: {sensitive_data} instances of sensitive data found",
            f"👤 PII Data: {pii} personally identifiable information instances",
            f"🏥 Medical Data: {medical} healthcare-related data instances",
            f"🔐 API/Security: {compliance_api} API keys and security credentials",
            f"📈 Risk Score: {risk_score}/100 (Risk Level: {self._get_risk_level(risk_score)})"
        ]
        
        return "\n".join(summary_lines)
    
    def _get_risk_level(self, risk_score: int) -> str:
        """Get human-readable risk level"""
        if risk_score >= 101:
            return "CRITICAL"
        elif risk_score >= 100:
            return "HIGH"
        elif risk_score >= 80:
            return "MEDIUM"
        elif risk_score >= 20:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _reset_analysis_ui(self):
        """Reset analysis UI to ready state"""
        self.analyze_btn.config(state=tk.NORMAL, text="🔍 Analyze Code")
        if hasattr(self, 'status_label'):
            self.status_label.config(text=f"Session: {self.current_user}", foreground="#00bfff")
    
    def load_sample_code(self):
        """Load sample code from the textbox into Practice tab"""
        try:
            # Get content from sample textbox
            sample_content = self.sample_display.get(1.0, tk.END)
            
            # Extract the actual code content (between markers)
            if "--- CODE CONTENT ---" in sample_content:
                code_start = sample_content.find("--- CODE CONTENT ---") + len("--- CODE CONTENT ---")
                code_end = sample_content.find("--- END CODE ---")
                
                if code_start != -1 and code_end != -1:
                    code_content = sample_content[code_start:code_end].strip()
                else:
                    messagebox.showwarning("Warning", "No valid code content found. Please select a sample first.")
                    return
            else:
                messagebox.showwarning("Warning", "No sample code loaded. Please select from dropdown first.")
                return
            
            # Clear and populate the practice message input first
            try:
                # Try to find the practice message entry
                if hasattr(self, 'practice_message_entry'):
                    self.practice_message_entry.delete(1.0, tk.END)
                    self.practice_message_entry.insert(tk.END, code_content)
                    
                    # Switch to Practice tab FIRST, then show popup
                    self.notebook.select(0)  # Practice Session is tab 0 (Sec360 Analysis is disabled)
                    
                    # Use root.after to show popup after tab switch
                    self.root.after(100, lambda: messagebox.showinfo("Success", "Edited code loaded to Practice Session chat!"))
                else:
                    # Fallback if practice_message_entry not found
                    self.notebook.select(0)
                    self.root.after(100, lambda: messagebox.showinfo("Success", "Edited code loaded to Practice Session chat!"))
                    
            except AttributeError as e:
                self.notebook.select(0)
                self.root.after(100, lambda: messagebox.showinfo("Success", "Code loaded! Switching to Practice Session tab..."))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sample code: {str(e)}")
    
    def clear_code(self):
        """Clear the code input area"""
        self.code_text.delete(1.0, tk.END)
    
    def export_results(self):
        """Export analysis results to file"""
        if not self.results_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Warning", "No results to export")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Results",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Markdown files", "*.md"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Results exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def copy_results(self):
        """Copy results to clipboard"""
        results = self.results_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(results)
        messagebox.showinfo("Success", "Results copied to clipboard")
    
    def _refresh_history_display(self):
        """Refresh the history display"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add recent analyses
        for analysis in self.analysis_history[-50:]:  # Show last 50
            risk_score = analysis['risk_analysis']['risk_score']
            self.history_tree.insert("", "end", values=(
                analysis['timestamp'],
                analysis['user'],
                analysis['model'],
                risk_score,
                analysis['code_length']
            ))
    
    def refresh_history(self):
        """Refresh analysis history"""
        # Load historical analysis data from practice sessions
        self._load_historical_analyses()
        self._refresh_history_display()
    
    def _load_historical_analyses(self):
        """Load historical analysis data from practice session files"""
        try:
            import json
            import os
            from pathlib import Path
            
            sessions_dir = Path("core/logs/sessions")
            if not sessions_dir.exists():
                return
            
            # Clear current history
            self.analysis_history.clear()
            
            # Load practice session files
            session_files = list(sessions_dir.glob("practice_*.json"))
            
            for file_path in session_files:
                try:
                    with open(file_path, 'r') as f:
                        session_data = json.load(f)
                        
                    # Extract analysis data from practice session
                    user_name = session_data.get('user_name', 'Unknown')
                    session_start = session_data.get('session_start_time', 'Unknown')
                    session_id = session_data.get('unique_session_id', 'Unknown')
                    
                    # Get code analyses from the session
                    code_analyses = session_data.get('code_analyses', [])
                    
                    if code_analyses:
                        for analysis in code_analyses:
                            # Create analysis record for history
                            analysis_record = {
                                'session_id': session_id,
                                'timestamp': session_start,
                                'user': user_name,
                                'model': 'llama3.2:3b',
                                'code_length': analysis.get('code_lines', 0),
                                'table_data': analysis.get('analysis_results', {}),
                                'risk_analysis': {
                                    'risk_score': analysis.get('risk_score', 50),
                                    'risk_level': analysis.get('risk_level', 'MEDIUM')
                                },
                                'raw_result': analysis
                            }
                            self.analysis_history.append(analysis_record)
                    elif 'final_analysis_metrics' in session_data:
                        # Create a record from final session metrics
                        metrics = session_data['final_analysis_metrics']
                        analysis_record = {
                            'session_id': session_id,
                            'timestamp': session_start,
                            'user': user_name,
                            'model': 'llama3.2:3b',
                            'code_length': metrics.get('total_lines', 0),
                            'table_data': {
                                'sensitive_fields': metrics.get('total_sensitive_fields', 0),
                                'sensitive_data': metrics.get('total_sensitive_data', 0),
                                'pii': metrics.get('total_pii', 0),
                                'hepa': metrics.get('total_hepa', 0),
                                'medical': metrics.get('total_medical', 0),
                                'compliance_api': metrics.get('total_compliance_api', 0)
                            },
                            'risk_analysis': {
                                'risk_score': metrics.get('average_risk_score', 50),
                                'risk_level': metrics.get('risk_level', 'MEDIUM')
                            },
                            'raw_result': session_data
                        }
                        self.analysis_history.append(analysis_record)
                        
                except Exception as e:
                    continue
                    
            # Sort by timestamp (newest first)
            self.analysis_history.sort(key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            print(f"Error loading historical analyses: {e}")
    
    def clear_history(self):
        """Clear analysis history"""
        if messagebox.askyesno("Confirm", "Clear all analysis history?"):
            self.analysis_history.clear()
            self._refresh_history_display()
    
    def view_history_item(self, event):
        """View selected history item"""
        selection = self.history_tree.selection()
        if not selection:
            return
        
        item = self.history_tree.item(selection[0])
        timestamp = item['values'][0]
        
        # Find matching analysis
        analysis = None
        for a in self.analysis_history:
            if a['timestamp'] == timestamp:
                analysis = a
                break
        
        if analysis:
            self._display_results(
                analysis['table_data'], 
                analysis['risk_analysis'], 
                analysis['raw_result']
            )
    
    def refresh_status(self):
        """Refresh system status"""
        status_dict = self.analyzer.health_check()
        
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        
        status_content = f"""
SEC360 SYSTEM STATUS
===================

Ollama Service: {'✅ Running' if status_dict['ollama_status'] else '❌ Not Available'}

Available Models:
{chr(10).join(f"  • {model}" for model in status_dict['available_models'])}

System Prompt: {'✅ Loaded' if status_dict['system_prompt_loaded'] else '❌ Not Loaded'}

Analysis Cache: {status_dict['cache_size']} analyses

Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self.status_text.insert(1.0, status_content)
        self.status_text.config(state=tk.DISABLED)
    
    def test_connection(self):
        """Test connection to analysis services"""
        try:
            status_dict = self.analyzer.health_check()
            
            if status_dict['ollama_status']:
                messagebox.showinfo("Connection Test", 
                                  "✅ All services are running and accessible!")
            else:
                messagebox.showerror("Connection Test", 
                                   "❌ Ollama service is not available\n\nPlease ensure Ollama is running.")
        except Exception as e:
            messagebox.showerror("Connection Test", f"❌ Test failed: {str(e)}")
    
    def update_status_periodically(self):
        """Update status periodically"""
        self.refresh_status()
        # Schedule next update in 30 seconds
        self.root.after(30000, self.update_status_periodically)
    
    def check_ollama_status(self):
        """Check Ollama status on startup"""
        if self.ollama_client.check_ollama_status():
            print("Ollama: ✅ Ready")  # Status update in terminal instead of UI
        else:
            print("Ollama: ❌ Not Available")
    
    # Placeholder methods for Sec360 functionality
    def start_practice_session(self):
        """Start a practice session"""
        user_id = self.practice_user_id_var.get().strip()
        if not user_id:
            messagebox.showwarning("Warning", "Please enter a user ID")
            return
        
        model = self.practice_model_var.get()
        if not model:
            messagebox.showwarning("Warning", "Please select a model")
            return
        
        # Check if user already has an active session
        if self.practice_manager.is_user_session_active(user_id):
            messagebox.showwarning("User Exists", f"This user '{user_id}' already exists.\n\nPlease use a different user value.")
            return
        
        # Set timer state before starting session
        timer_enabled = self.timer_enabled_var.get()
        
        # Use practice session manager
        if self.practice_manager.start_session(user_id, model):
            # Apply timer state after session starts
            self.practice_manager.toggle_session_timer(timer_enabled)
            
            # Update UI
            self.practice_start_btn.config(state=tk.DISABLED)
            self.practice_end_btn.config(state=tk.NORMAL)
            self.practice_user_id_entry.config(state=tk.DISABLED)
            self.practice_model_combo.config(state=tk.DISABLED)
            
            # Update timer button visual state
            if timer_enabled:
                self.timer_toggle_btn.config(text="⏰ Auto-end (5min) ✓")
                timer_status = "Auto-end enabled"
            else:
                self.timer_toggle_btn.config(text="⏰ Auto-end (5min)")
                timer_status = "Manual end required"
            
            # Update status
            self.practice_status_var.set(f"Session active for {user_id} ({timer_status})")
            
            messagebox.showinfo("Session Started", f"Practice session started for user: {user_id}")
        else:
            messagebox.showerror("Error", "Failed to start practice session")
    
    def end_practice_session(self):
        """End a practice session"""
        # Use practice session manager
        if self.practice_manager.end_session():
            # Reset UI using unified method
            self.practice_manager._reset_ui_after_end()
            
            messagebox.showinfo("Session Ended", "Practice session ended")
        else:
            messagebox.showwarning("Warning", "No active session to end")
    
    def on_timer_toggle(self):
        """Handle timer toggle button"""
        enabled = self.timer_enabled_var.get()
        
        # Update practice session manager
        if hasattr(self, 'practice_manager'):
            self.practice_manager.toggle_session_timer(enabled)
        
        # Update button text to reflect current state
        if enabled:
            self.timer_toggle_btn.config(text="⏰ Auto-end (5min) ✓")
            self.practice_status_var.set("Timer enabled: Session will auto-end after 5 minutes of inactivity")
        else:
            self.timer_toggle_btn.config(text="⏰ Auto-end (5min)")
            self.practice_status_var.set("Timer disabled: Manual end required")
    
    def show_timer_end_notification(self):
        """Show popup notification when timer auto-ends session"""
        messagebox.showinfo("Session Timeout", 
                           f"Session automatically ended after 5 minutes of inactivity.\n\n"
                           f"This prevents long-running sessions and encourages active practice.")
    
    def send_practice_message(self, event=None):
        """Send a practice message"""
        message = self.practice_message_entry.get(1.0, tk.END).strip()
        if not message:
            messagebox.showwarning("Warning", "Please enter a message before sending")
            return
        
        # Check if session is active
        if not self.practice_manager.is_session_active():
            messagebox.showwarning("Warning", "Please start a practice session first")
            return
        
        # Clear input
        self.practice_message_entry.delete(1.0, tk.END)
        
        # Use practice session manager
        model = self.practice_model_var.get()
        self.practice_manager.send_message(message, model)
    
    def stop_practice_thinking(self):
        """Stop the current thinking process"""
        self.practice_manager.stop_thinking_process()
    
    
    def clear_practice_chat(self):
        """Clear practice chat"""
        self.practice_manager.clear_chat()
    
    def _show_active_sessions(self):
        """Show active sessions dialog"""
        active_sessions = self.practice_manager.get_active_sessions()
        
        if not active_sessions:
            messagebox.showinfo("Active Sessions", "No active sessions found.")
            return
        
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Active Practice Sessions")
        dialog.geometry("500x300")
        dialog.configure(bg='#2b2b2b')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"500x300+{x}+{y}")
        
        # Title
        title_label = tk.Label(dialog, text="Active Practice Sessions", 
                              font=('Arial', 14, 'bold'), bg='#2b2b2b', fg='white')
        title_label.pack(pady=10)
        
        # Sessions list
        sessions_frame = tk.Frame(dialog, bg='#2b2b2b')
        sessions_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for user_id, session_data in active_sessions.items():
            session_frame = tk.Frame(sessions_frame, bg='#3b3b3b', relief=tk.RAISED, bd=1)
            session_frame.pack(fill=tk.X, pady=5)
            
            # User info
            user_label = tk.Label(session_frame, text=f"User: {user_id}", 
                                 font=('Arial', 10, 'bold'), bg='#3b3b3b', fg='#FFD700')
            user_label.pack(anchor=tk.W, padx=10, pady=2)
            
            # Session details
            session_id = session_data['session_id']
            start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(session_data['start_time']))
            model = session_data['model']
            
            details_text = f"Session ID: {session_id}\nStart Time: {start_time}\nModel: {model}"
            details_label = tk.Label(session_frame, text=details_text, 
                                   font=('Arial', 9), bg='#3b3b3b', fg='white', justify=tk.LEFT)
            details_label.pack(anchor=tk.W, padx=10, pady=2)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#2b2b2b')
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        end_all_btn = tk.Button(button_frame, text="End All Sessions", 
                               command=lambda: self._end_all_sessions(dialog),
                               bg='#ff4444', fg='white', font=('Arial', 10, 'bold'))
        end_all_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(button_frame, text="Close", 
                             command=dialog.destroy,
                             bg='#666666', fg='white', font=('Arial', 10))
        close_btn.pack(side=tk.RIGHT, padx=5)
    
    def _end_all_sessions(self, dialog):
        """End all active sessions"""
        result = messagebox.askyesno("Confirm", "Are you sure you want to end all active sessions?")
        if result:
            ended_count = self.practice_manager.force_end_all_sessions()
            messagebox.showinfo("Sessions Ended", f"Ended {ended_count} active session(s).")
            dialog.destroy()
    
    def show_sample_code(self, event=None):
        """Show sample code based on dropdown selection"""
        # Map dropdown options to file paths
        # Always resolve absolute path from project root
        try:
            from pathlib import Path
            project_root = Path(__file__).resolve().parent
            data_samples = project_root / "data" / "samples"
        except Exception:
            data_samples = None

        file_mapping = {
            "API Keys and Tokens": str((data_samples / "api_keys_sample.py") if data_samples else "data/samples/api_keys_sample.py"),
            "Personal Identifiable Information (PII)": str((data_samples / "pii_sample.py") if data_samples else "data/samples/pii_sample.py"),
            "Medical Records and Health Information": str((data_samples / "medical_records_sample.py") if data_samples else "data/samples/medical_records_sample.py"),
            "Internal Infrastructure and Hostnames": str((data_samples / "internal_infrastructure_sample.py") if data_samples else "data/samples/internal_infrastructure_sample.py"),
            "Compliance and Regulatory Data": str((data_samples / "compliance_sample.py") if data_samples else "data/samples/compliance_sample.py")
        }
        
        # Get selected option from dropdown
        selected_option = self.sample_var.get()
        
        if not selected_option or selected_option not in file_mapping:
            messagebox.showwarning("Warning", "Please select a sample from the dropdown")
            return
        
        filename = file_mapping[selected_option]
        print(f"Loading sample from: {filename}")
        
        # Check if file exists
        if not os.path.exists(filename):
            messagebox.showerror("Error", f"Sample file not found: {filename}")
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # Clear the text box and display the code
            self.sample_display.delete(1.0, tk.END)
            self.sample_display.insert(tk.END, f"""
INSTRUCTIONS:
1. Review this sample code and identify potential data leaks
2. EDIT the code to remove sensitive information (API keys, PII, etc.)  
3. Click "Load Sample" when ready

SELECTED SAMPLE: {selected_option}
FILE: {filename}

--- CODE CONTENT ---
{code_content}
--- END CODE ---

Ready to edit? Make changes above, then click "Load Sample" to copy to Practice tab.
""")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def open_log_viewer(self):
        """Open log viewer"""
        try:
            import subprocess
            import os
            
            # Get project root directory
            project_root = os.path.dirname(os.path.abspath(__file__))
            
            # Detect Python command (same logic as start.sh)
            python_cmd = "python3"
            if not self.command_exists("python3"):
                if self.command_exists("python"):
                    # Check if python is version 3+
                    try:
                        import subprocess
                        result = subprocess.run(["python", "--version"], capture_output=True, text=True)
                        version = result.stdout.strip().split()[1].split('.')[0]
                        if int(version) >= 3:
                            python_cmd = "python"
                    except:
                        pass
            
            # Launch log viewer as separate process
            cmd = [python_cmd, '-m', 'core.logging_system.log_viewer']
            
            # Run as separate process in project directory
            subprocess.Popen(cmd, cwd=project_root, 
                           stdin=subprocess.DEVNULL, 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open log viewer: {str(e)}")
    
    def open_enhanced_log_viewer(self):
        """Open enhanced detailed log viewer"""
        try:
            import subprocess
            import os
            
            # Get project root directory
            project_root = os.path.dirname(os.path.abspath(__file__))
            
            # Check if detailed sessions exist
            detailed_sessions_dir = os.path.join(project_root, "detailed_sessions")
            if not os.path.exists(detailed_sessions_dir):
                messagebox.showwarning("No Detailed Sessions", 
                    "No detailed sessions found!\n\n" +
                    "To create detailed sessions:\n" +
                    "1. Run: python3 generate_sample_detailed_sessions.py\n" +
                    "2. Or create sessions using the detailed session generator")
                return
            
            # Detect Python command (same logic as start.sh)
            python_cmd = "python3"
            if not self.command_exists("python3"):
                if self.command_exists("python"):
                    # Check if python is version 3+
                    try:
                        import subprocess
                        result = subprocess.run(["python", "--version"], capture_output=True, text=True)
                        version = result.stdout.strip().split()[1].split('.')[0]
                        if int(version) >= 3:
                            python_cmd = "python"
                    except:
                        pass
            
            # Launch enhanced log viewer as separate process
            cmd = [python_cmd, 'detailed_log_viewer.py']
            
            # Run as separate process in project directory
            subprocess.Popen(cmd, cwd=project_root, 
                           stdin=subprocess.DEVNULL, 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open enhanced log viewer: {str(e)}")
    
    def command_exists(self, cmd):
        """Check if command exists"""
        import shutil
        return shutil.which(cmd) is not None
    
    def open_scoreboard(self):
        """Open scoreboard"""
        try:
            from core.scoreboard.scoreboard_viewer import ScoreboardViewer
            scoreboard = ScoreboardViewer()
            scoreboard.run()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open scoreboard: {str(e)}")
    
    def refresh_statistics(self):
        """Refresh statistics"""
        self.stats_display.delete(1.0, tk.END)
        
        try:
            # Calculate real statistics from session data
            import json
            import os
            from pathlib import Path
            
            sessions_dir = Path("core/logs/sessions")
            if not sessions_dir.exists():
                stats_text = "📊 No session data found. Start practicing to see statistics!"
                self.stats_display.insert(tk.END, stats_text)
                self.stats_display.config(state=tk.DISABLED)
                return
    
            # Load all session data
            session_files = list(sessions_dir.glob("*.json"))
            sessions = []
            
            for file_path in session_files:
                try:
                    with open(file_path, 'r') as f:
                        session_data = json.load(f)
                        sessions.append(session_data)
                except Exception as e:
                    continue
            
            if not sessions:
                stats_text = "📊 No valid session data found."
                self.stats_display.insert(tk.END, stats_text)
                return
            
            # Calculate statistics
            total_sessions = len(sessions)
            unique_users = len(set(session.get('user_name', 'unknown') for session in sessions))
            
            risk_scores = []
            total_lines = 0
            total_sensitive_fields = 0
            total_sensitive_data = 0
            total_pii = 0
            total_medical = 0
            total_api = 0
            
            practice_sessions = 0
            analysis_sessions = 0
            
            for session in sessions:
                # Check if it's a practice session
                if 'final_analysis_metrics' in session:
                    practice_sessions += 1
                    metrics = session['final_analysis_metrics']
                    risk_scores.append(metrics.get('average_risk_score', 0))
                    total_lines += metrics.get('total_lines', 0)
                    total_sensitive_fields += metrics.get('total_sensitive_fields', 0)
                    total_sensitive_data += metrics.get('total_sensitive_data', 0)
                    total_pii += metrics.get('total_pii', 0)
                    total_medical += metrics.get('total_medical', 0)
                    total_api += metrics.get('total_compliance_api', 0)
                else:
                    analysis_sessions += 1
                    # Legacy analysis session format
                    detected_flags = session.get('detected_flags', 0)
                    potential_flags = session.get('potential_flags', 0)
                    total_lines += session.get('code_lines', 0)
                    total_sensitive_fields += potential_flags
                    total_sensitive_data += detected_flags
            
            # Risk distribution
            if risk_scores:
                avg_risk = sum(risk_scores) / len(risk_scores)
                critical_risk = len([r for r in risk_scores if r >= 80])
                high_risk = len([r for r in risk_scores if r >= 60 and r < 80])
                medium_risk = len([r for r in risk_scores if r >= 40 and r < 60])
                low_risk = len([r for r in risk_scores if r < 40])
            else:
                avg_risk = 0
                critical_risk = high_risk = medium_risk = low_risk = 0
            
            stats_text = f"""
📊 SEC360 STATISTICS OVERVIEW
==============================

🎯 Session Statistics:
• Total Sessions: {total_sessions}
• Practice Sessions: {practice_sessions}
• Analysis Sessions: {analysis_sessions}
• Unique Users: {unique_users}
• Average Risk Score: {avg_risk:.1f}/100

📈 Risk Distribution:
• Critical Risk (80-100): {critical_risk} sessions
• High Risk (60-79): {high_risk} sessions  
• Medium Risk (40-59): {medium_risk} sessions
• Low Risk (0-39): {low_risk} sessions

🔍 Analysis Breakdown:
• Lines of Code Analyzed: {total_lines:,}
• Sensitive Fields Detected: {total_sensitive_fields:,}
• Sensitive Data Found: {total_sensitive_data:,}
• PII Instances: {total_pii:,}
• Medical Data Instances: {total_medical:,}
• API/Security Issues: {total_api:,}

📅 Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            self.stats_display.insert(tk.END, stats_text)
            
        except Exception as e:
            error_text = f"Error loading statistics: {str(e)}"
            self.stats_display.insert(tk.END, error_text)
    
    def refresh_sessions_status(self):
        """Refresh sessions status"""
        self.sessions_display.delete(1.0, tk.END)
        
        try:
            import json
            import os
            from pathlib import Path
            
            sessions_dir = Path("core/logs/sessions")
            if not sessions_dir.exists():
                sessions_text = "📊 No session data found."
                self.sessions_display.insert(tk.END, sessions_text)
                return
            
            # Load practice session data (completed sessions)
            session_files = list(sessions_dir.glob("practice_*.json"))
            sessions = []
            
            for file_path in session_files:
                try:
                    with open(file_path, 'r') as f:
                        session_data = json.load(f)
                        # Add file info
                        session_data['file_name'] = file_path.name
                        session_data['file_modified'] = file_path.stat().st_mtime
                        sessions.append(session_data)
                except Exception as e:
                    continue
            
            # Load currently active sessions from active_sessions.json
            active_sessions_file = sessions_dir / "active_sessions.json"
            if active_sessions_file.exists():
                try:
                    with open(active_sessions_file, 'r') as f:
                        active_sessions_data = json.load(f)
                        
                    # Convert active sessions to session format
                    current_time = time.time()
                    for user_name, active_data in active_sessions_data.items():
                        # Skip if the active session object can't be serialized
                        if 'manager_instance' in str(active_data):
                            continue
                            
                        session_id = active_data.get('session_id', f'practice_{user_name}_unknown')
                        start_time = active_data.get('start_time', current_time)
                        model = active_data.get('model', 'llama3.2:3b')
                        
                        # Create active session data
                        active_session = {
                            'user_name': user_name,
                            'unique_session_id': session_id,
                            'session_start_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)),
                            'session_end_time': None,  # No end time = active
                            'session_duration': current_time - start_time,
                            'final_analysis_metrics': {
                                'total_analyses': 0,
                                'average_risk_score': 0
                            },
                            'file_name': f'{session_id}.json',
                            'file_modified': start_time,
                            'is_currently_active': True
                        }
                        
                        # Add to sessions list at the beginning (most recent)
                        sessions.insert(0, active_session)
                        
                except Exception as e:
                    print(f"Error loading active sessions: {e}")
            
            # Sort by modification time (newest first)
            sessions.sort(key=lambda x: x['file_modified'], reverse=True)
            
            sessions_text = """
👥 ACTIVE SESSIONS STATUS
=========================

"""
            
            # Show up to 10 most recent sessions
            recent_sessions = sessions[:10]
            
            if recent_sessions:
                for session in recent_sessions:
                    user = session.get('user_name', 'Unknown')
                    session_id = session.get('unique_session_id', session.get('session_id', 'Unknown'))
                    start_time = session.get('session_start_time', 'Unknown')
                    end_time = session.get('session_end_time')
                    duration = session.get('session_duration', 0)
                    
                    # Determine if session is active (no end time or very recent)
                    is_active = end_time is None
                    if end_time:
                        try:
                            # Check if ended recently (within last hour)
                            end_timestamp = time.mktime(time.strptime(end_time, '%Y-%m-%d %H:%M:%S'))
                            if time.time() - end_timestamp < 3600:  # 1 hour
                                is_active = True
                        except:
                            pass
                    
                    status_icon = "🟢" if is_active else "🔴"
                    status_text = "Active" if is_active else "Ended"
                    
                    sessions_text += f"""• Session: {session_id}
  User: {user}
  Status: {status_text} {status_icon}
  Started: {start_time}
"""
                    
                    if end_time and not is_active:
                        sessions_text += f"  Ended: {end_time}\n"
                    
                    sessions_text += f"  Duration: {duration:.1f} seconds\n"
                    
                    # Show session type and metrics
                    if 'final_analysis_metrics' in session:
                        metrics = session['final_analysis_metrics']
                        risk_score = metrics.get('average_risk_score', 0)
                        sessions_text += f"  Risk Score: {risk_score:.1f}/100\n"
                        sessions_text += f"  Analyses: {metrics.get('total_analyses', 0)}\n"
                    elif 'code_lines' in session:
                        sessions_text += f"  Code Lines: {session.get('code_lines', 0)}\n"
                        sessions_text += f"  Detected Flags: {session.get('detected_flags', 0)}\n"
                    
                    sessions_text += "\n"
            else:
                sessions_text += "No sessions found.\n"
            
            sessions_text += f"""
📋 Session File Locations:
• Directory: {sessions_dir}
• Files Found: {len(session_files)}
• Data Files: {len([f for f in session_files if f.name.endswith('.json')])}

Last Updated: """ + time.strftime('%Y-%m-%d %H:%M:%S')
            
            self.sessions_display.insert(tk.END, sessions_text)
            
        except Exception as e:
            error_text = f"Error loading session status: {str(e)}"
            self.sessions_display.insert(tk.END, error_text)
    
    def force_end_all_sessions(self):
        """Force end all sessions"""
        result = messagebox.askyesno("Confirm", "Are you sure you want to force end all active sessions?")
        if result:
            # Clear sessions display
            self.sessions_display.delete(1.0, tk.END)
            self.sessions_display.insert(tk.END, "All sessions have been force ended.\n\nSystem is now ready for new sessions.")
            messagebox.showinfo("Success", "All active sessions have been force ended.")
    
    def load_existing_active_sessions(self):
        """Load existing active sessions"""
        pass  # Placeholder
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = Sec360App()
    app.run()
