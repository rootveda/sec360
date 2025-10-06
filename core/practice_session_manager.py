#!/usr/bin/env python3
"""
Sec360 Practice Session Manager
Handles practice session functionality with comprehensive tracking and analysis.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import time
import threading
from typing import Dict, List, Optional
from pathlib import Path

class PracticeSessionManager:
    """Manages practice session functionality with comprehensive tracking"""
    
    def __init__(self, main_app, ollama_client, analyzer, json_parser):
        self.main_app = main_app
        self.ollama_client = ollama_client
        self.analyzer = analyzer
        self.json_parser = json_parser
        
        # Session state variables
        self.session_active = False
        self.user_name = None
        self.session_start_time = None
        self.session_end_time = None
        self.session_id = None
        self.code_analyses = []
        self.total_tokens = 0
        self.message_count = 0
        
        # Conversation tracking for detailed log viewer
        self.conversations = []  # List of conversation entries
        
        # Global session tracking (one session per user)
        self.active_sessions = {}  # {user_name: session_data}
        
        # Duplicate code tracking (display purposes only)
        self.duplicate_analysis_count = 0
        self.unique_code_hashes = set()
        self.is_current_duplicate = False
        
        # Load existing active sessions on startup
        self._load_active_sessions()
        
        # Session timer settings
        self.session_timer_enabled = True  # Default: enabled
        self.session_timeout_minutes = 5    # Auto-end after 5 minutes
        self.session_timer = None          # Timer object
        
        # Analysis metrics tracking
        self.session_metrics = {
            'total_lines': 0,
            'total_sensitive_fields': 0,
            'total_sensitive_data': 0,
            'total_pii': 0,
            'total_hepa': 0,
            'total_medical': 0,
            'total_compliance_api': 0,
            'risk_scores': [],
            'analysis_count': 0,
            'current_tokens_per_sec': 0,
            'current_input_tokens': 0,
            'current_output_tokens': 0
        }
        
        # Thinking state management
        self.is_thinking = False
        self.stop_thinking = False
        self.thinking_thread = None
        
        # Real-time timer
        self.timer_running = False
        self.timer_thread = None
    
    def _load_active_sessions(self):
        """Load active sessions from existing session files"""
        try:
            sessions_dir = Path("core/logs/sessions")
            if not sessions_dir.exists():
                return
            
            for file_path in sessions_dir.glob("practice_*.json"):
                try:
                    with open(file_path, 'r') as f:
                        session_data = json.load(f)
                    
                    # Check if session is still active (no end time)
                    if 'session_end_time' not in session_data or not session_data.get('session_end_time'):
                        user_name = session_data.get('user_name')
                        if user_name:
                            # Check if session is recent (within last 24 hours)
                            session_start = session_data.get('session_start_time')
                            if session_start:
                                try:
                                    start_time = time.mktime(time.strptime(session_start, '%Y-%m-%d %H:%M:%S'))
                                    if time.time() - start_time < 86400:  # 24 hours
                                        self.active_sessions[user_name] = {
                                            'session_id': session_data.get('unique_session_id'),
                                            'start_time': start_time,
                                            'model': session_data.get('model', 'llama3.2:3b'),
                                            'manager_instance': self
                                        }
                                except Exception as e:
                                    print(f"Error parsing session time: {e}")
                                    
                except Exception as e:
                    print(f"Error loading session {file_path.name}: {e}")
                    
        except Exception as e:
            print(f"Error loading active sessions: {e}")
    
    def _save_active_sessions(self):
        """Save active sessions to a tracking file"""
        try:
            sessions_dir = Path("core/logs/sessions")
            sessions_dir.mkdir(parents=True, exist_ok=True)
            
            active_sessions_file = sessions_dir / "active_sessions.json"
            with open(active_sessions_file, 'w') as f:
                json.dump(self.active_sessions, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Error saving active sessions: {e}")
    
    def _track_code_analysis(self, code: str):
        """Track code analysis for duplicate detection (display purposes only)"""
        import hashlib
        
        # Create hash of the code (normalized)
        code_hash = hashlib.md5(code.strip().encode()).hexdigest()
        
        # Check if this code was analyzed before
        if code_hash in self.unique_code_hashes:
            self.duplicate_analysis_count += 1
            self.is_current_duplicate = True
        else:
            self.unique_code_hashes.add(code_hash)
            self.is_current_duplicate = False
    
    def start_session(self, user_id: str, model: str) -> bool:
        """Start a new practice session"""
        try:
            # Check if user already has an active session
            if user_id in self.active_sessions:
                return False  # User already has an active session
            
            # Set session variables
            self.session_active = True
            self.user_name = user_id
            self.session_start_time = time.time()
            self.session_id = f"practice_{user_id}_{int(self.session_start_time)}"
            self.code_analyses = []
            self.total_tokens = 0
            self.message_count = 0
            
            # Add to active sessions
            self.active_sessions[user_id] = {
                'session_id': self.session_id,
                'start_time': self.session_start_time,
                'model': model,
                'manager_instance': self
            }
            
            # Save active sessions
            self._save_active_sessions()
            
            # Start session timer if enabled
            self._start_session_timer()
            
            # Reset metrics
            self.session_metrics = {
                'total_lines': 0,
                'total_sensitive_fields': 0,
                'total_sensitive_data': 0,
                'total_pii': 0,
                'total_hepa': 0,
                'total_medical': 0,
                'total_compliance_api': 0,
                'risk_scores': [],
                'analysis_count': 0
            }
            
            # Reset duplicate tracking for new session
            self.duplicate_analysis_count = 0
            self.unique_code_hashes = set()
            self.is_current_duplicate = False
            
            # Update UI
            self._update_session_info(user_id, model)
            self._add_welcome_message(user_id)
            
            self._update_footer()
            
            # Start real-time timer
            self._start_timer()
            
            return True
            
        except Exception as e:
            print(f"Error starting practice session: {e}")
            return False
    
    def end_session(self) -> bool:
        """End the current practice session"""
        try:
            if not self.session_active:
                return False
            
            # Stop session timer
            self._stop_session_timer()
            
            # Set end time
            self.session_end_time = time.time()
            session_duration = self.session_end_time - self.session_start_time
            
            # Calculate final metrics
            final_metrics = self._calculate_final_metrics()
            
            # Create session data
            session_data = {
                "user_name": self.user_name,
                "session_start_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.session_start_time)),
                "session_end_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.session_end_time)),
                "session_duration": round(session_duration, 2),
                "token_count": self.total_tokens,
                "unique_session_id": self.session_id,
                "code_analyses": self.code_analyses.copy(),  # Make a copy to avoid potential reference issues
                "final_analysis_metrics": final_metrics,
                "message_count": self.message_count,
                "conversations": self.conversations.copy()  # Include conversation history
            }
            
            # Save session data
            self._save_session_data(session_data)
            
            # Trigger scoreboard refresh
            self._trigger_scoreboard_refresh()
            
            # Remove from active sessions
            if self.user_name in self.active_sessions:
                del self.active_sessions[self.user_name]
                self._save_active_sessions()
            
            # Stop timer
            self._stop_timer()
            
            # Clear chat display
            self.clear_chat()
            
            # Reset session state
            self.session_active = False
            self.user_name = None
            self.session_start_time = None
            self.session_end_time = None
            self.session_id = None
            
            # Reset metrics to 0
            self.code_analyses = []
            self.total_tokens = 0
            self.message_count = 0
            self.session_metrics = {
                'lines_of_code': 0,
                'sensitive_fields': 0,
                'sensitive_data': 0,
                'pii_count': 0,
                'hepa_count': 0,
                'medical_count': 0,
                'compliance_api_count': 0,
                'risk_scores': [],
                'analysis_count': 0,
                'total_lines': 0,
                'total_sensitive_fields': 0,
                'total_sensitive_data': 0,
                'total_pii_count': 0,
                'total_hepa_count': 0,
                'total_medical_count': 0,
                'total_compliance_api_count': 0,
                'current_tokens_per_sec': 0,
            'current_input_tokens': 0,
            'current_output_tokens': 0,
                'current_input_tokens': 0,
                'current_output_tokens': 0
            }
            
            return True
            
        except Exception as e:
            print(f"Error ending practice session: {e}")
            return False
    
    def _start_session_timer(self):
        """Start session timer for auto-timeout"""
        if not self.session_timer_enabled:
            return
            
        # Cancel any existing timer
        if self.session_timer:
            self.session_timer.cancel()
            
        # Start new timer (5 minutes * 60 seconds)
        import threading
        self.session_timer = threading.Timer(
            self.session_timeout_minutes * 60, 
            self._on_session_timeout
        )
        self.session_timer.daemon = True
        self.session_timer.start()
        
        print(f"Timer started: Auto-end in {self.session_timeout_minutes} minutes")
    
    def _stop_session_timer(self):
        """Stop session timer"""
        if self.session_timer:
            self.session_timer.cancel()
            self.session_timer = None
            print("Session timer stopped")
    
    def _on_session_timeout(self):
        """Handle session timeout - auto end session"""
        if not self.session_active:
            return
            
        print(f"⏰ Session timeout reached ({self.session_timeout_minutes} minutes)")
        
        # Auto-end session
        self.main_app.root.after(0, self._auto_end_session)
    
    def _auto_end_session(self):
        """Auto-end session from main thread"""
        try:
            if self.session_active:
                print("🔚 Auto-ending session due to timeout")
                
                # Show timeout message in chat
                self._add_ai_message(f"⏰ Session automatically ended after {self.session_timeout_minutes} minutes of inactivity.")
                
                # End session
                success = self.end_session()
                
                if success:
                    # Update UI exactly like manual end session
                    self.main_app.root.after(0, self._reset_ui_after_end)
                    
                    # Show popup notification
                    self.main_app.root.after(0, lambda: self.main_app.show_timer_end_notification())
                    
                    # Update sessions status
                    self.main_app.root.after(0, self.main_app.refresh_sessions_status)
                
        except Exception as e:
            print(f"Error auto-ending session: {e}")
    
    def _reset_ui_after_end(self):
        """Reset UI after session ends (used by both manual and auto-end)"""
        try:
            # Reset UI buttons
            self.main_app.practice_start_btn.config(state=tk.NORMAL)
            self.main_app.practice_end_btn.config(state=tk.DISABLED)
            self.main_app.practice_user_id_entry.config(state=tk.NORMAL)
            self.main_app.practice_model_combo.config(state=tk.NORMAL)
            
            # Clear session info
            self.main_app.practice_session_info_text.config(state=tk.NORMAL)
            self.main_app.practice_session_info_text.delete(1.0, tk.END)
            self.main_app.practice_session_info_text.insert(tk.END, "No active session")
            self.main_app.practice_session_info_text.config(state=tk.DISABLED)
            
            # Clear chat display
            self.main_app.practice_chat_display.config(state=tk.NORMAL)
            self.main_app.practice_chat_display.delete(1.0, tk.END)
            self.main_app.practice_chat_display.config(state=tk.DISABLED)
            
            # Update status
            self.main_app.practice_status_var.set("Ready to start practice session")
            
            # Update footer to show reset values
            self.main_app.practice_manager._update_footer()
            
            # Reset timer button state
            self.main_app.timer_enabled_var.set(True)  # Reset to default enabled
            self.main_app.timer_toggle_btn.config(text="⏰ Auto-end (5min)")
            
        except Exception as e:
            print(f"Error resetting UI: {e}")
    
    def toggle_session_timer(self, enabled: bool):
        """Toggle session timer on/off"""
        self.session_timer_enabled = enabled
        
        if enabled and self.session_active:
            # Restart timer if session is active
            self._start_session_timer()
            print(f"Timer enabled: Auto-end in {self.session_timeout_minutes} minutes")
        elif not enabled and self.session_timer:
            # Stop timer if session is active
            self._stop_session_timer()
            print("Timer disabled: Manual end required")
    
    def send_message(self, message: str, model: str) -> None:
        """Process and send a message in the practice session"""
        if not self.session_active:
            return
        
        if self.is_thinking:
            return  # Don't send if already thinking
        
        # Increment message count
        self.message_count += 1
        
        # Add user message to chat
        self._add_user_message(message)
        
        # Set thinking state
        self.is_thinking = True
        self.stop_thinking = False
        
        # Show thinking indicator
        self.main_app.root.after(0, self._show_thinking_indicator)
        
        # Detect if message contains code
        is_code = self._detect_code_in_message(message)
        
        if is_code:
            # Run code analysis in thread
            self.thinking_thread = threading.Thread(
                target=self._run_code_analysis_thread,
                args=(message, model),
                daemon=True
            )
            self.thinking_thread.start()
        else:
            # Run regular chat analysis in thread
            self.thinking_thread = threading.Thread(
                target=self._run_chat_analysis_thread,
                args=(message, model),
                daemon=True
            )
            self.thinking_thread.start()
    
    def _detect_code_in_message(self, message: str) -> bool:
        """Detect if message contains code"""
        import re
        
        # Minimum word requirement for code analysis
        words = message.strip().split()
        if len(words) < 3:  # Require at least 3 words for code analysis
            return False
        
        # Code indicators that should match as whole words or specific patterns
        code_patterns = [
            r'\bdef\s+',           # Python function definition
            r'\bclass\s+',         # Class definition
            r'\bimport\s+',        # Import statement
            r'\bfrom\s+',          # From import
            r'\bif\s+__name__',    # Python main check
            r'\bfunction\b',       # Function keyword
            r'\bvar\s+',           # Variable declaration
            r'\blet\s+',           # Let declaration
            r'\bconst\s+',         # Const declaration
            r'\bpublic\s+',        # Public keyword
            r'\bprivate\s+',       # Private keyword
            r'<\?php',             # PHP opening tag
            r'<script',            # Script tag
            r'<html',              # HTML tag
            r'\bSELECT\s+',       # SQL SELECT
            r'\bINSERT\s+',       # SQL INSERT
            r'\bUPDATE\s+',       # SQL UPDATE
            r'\bapi_key\b',       # API key (whole word)
            r'\bpassword\b',      # Password (whole word)
            r'\bsecret\b',        # Secret (whole word)
            r'\btoken\b',         # Token (whole word) - FIXED!
            r'\bcredentials\b'   # Credentials (whole word)
        ]
        
        message_lower = message.lower()
        for pattern in code_patterns:
            if re.search(pattern, message_lower):
                return True
        
        # Check for code-like patterns (multiple lines, indentation)
        lines = message.split('\n')
        if len(lines) > 2:
            indented_lines = sum(1 for line in lines if line.startswith('    ') or line.startswith('\t'))
            if indented_lines > 0:
                return True
        
        return False
    
    
    def _show_thinking_indicator(self):
        """Show thinking indicator in chat"""
        try:
            self.main_app.practice_chat_display.config(state=tk.NORMAL)
            self.main_app.practice_chat_display.insert(tk.END, f"\n🤖 AI: ", "ai_name")
            self.main_app.practice_chat_display.insert(tk.END, "Thinking...\n", "ai_response")
            self.main_app.practice_chat_display.see(tk.END)
            self.main_app.practice_chat_display.config(state=tk.DISABLED)
            
            # Enable stop button when AI starts thinking
            self.main_app.practice_stop_btn.config(state=tk.NORMAL)
        except Exception as e:
            print(f"Error showing thinking indicator: {e}")
    
    def _clear_thinking_indicator(self):
        """Clear thinking indicator from chat WITHOUT resetting formatting"""
        try:
            self.main_app.practice_chat_display.config(state=tk.NORMAL)
            
            # Don't modify existing content - just let the AI response overwrite it
            # The AI response will come right after the thinking message anyway
            pass
            
        except Exception as e:
            print(f"Error clearing thinking indicator: {e}")
        finally:
            self.main_app.practice_chat_display.config(state=tk.DISABLED)
            # Disable stop button when AI stops thinking
            self.main_app.practice_stop_btn.config(state=tk.DISABLED)
    
    def stop_thinking_process(self):
        """Stop the current thinking process"""
        if self.is_thinking:
            self.stop_thinking = True
            self.is_thinking = False
            
            # Provide user feedback
            self.main_app.practice_chat_display.config(state=tk.NORMAL)
            self.main_app.practice_chat_display.insert(tk.END, f"\n⏹️ User stopped AI response\n")
            self.main_app.practice_chat_display.see(tk.END)
            self.main_app.practice_chat_display.config(state=tk.DISABLED)
            
            # Clear thinking indicator and disable stop button
            self.main_app.root.after(0, self._clear_thinking_indicator)
    
    def _run_code_analysis_thread(self, code: str, model: str) -> None:
        """Run code analysis in a separate thread"""
        try:
            # Track code analysis for duplicate detection (display only)
            self._track_code_analysis(code)
            
            # Set model
            self.ollama_client.set_model(model)
            
            # Run analysis
            result = self.analyzer.analyze_code(code)
            
            if not self.stop_thinking and result.get('success', False):
                # Calculate tokens (rough estimate)
                estimated_tokens = len(code.split()) + len(result.get('raw_response', '').split())
                self.total_tokens += estimated_tokens
                
                # Handle result in main thread
                self.main_app.root.after(0, self._handle_code_analysis_result, result)
            
        except Exception as e:
            if not self.stop_thinking:
                error_msg = f"Analysis error: {str(e)}"
                self.main_app.root.after(0, self._handle_analysis_error, error_msg)
        finally:
            # Reset thinking state and clear thinking indicator
            self.is_thinking = False
            self.main_app.root.after(0, self._clear_thinking_indicator)
    
    def _run_chat_analysis_thread(self, message: str, model: str) -> None:
        """Run chat analysis in a separate thread"""
        try:
            # Set model
            self.ollama_client.set_model(model)
            
            # Create system prompt for security-focused chat
            system_prompt = """You are a helpful Security Mentor focused on preventing users from sharing sensitive data with LLMs.

**PRIMARY GOAL: Help users sanitize sensitive data before sharing with AI tools.**

When helping users practice secure coding, suggest these specific patterns:

1. **Replace sensitive field names** with generic alternatives:
   Original: "patient_id", "ssn", "diagnosis" 
   Secure: "user_id", "id_number", "condition"

2. **Use specific generic placeholders** instead of "placeholder_value":
   Good patterns: "value_001", "item_a", "standard_config", "default_type"
   Avoid: "placeholder_value" (too generic)

3. **Replace empty sensitive data** with defaults:
   Original: "", ""
   Secure: "standard_value", "default_option"

4. **Environment variables for secrets**:
   Original: password = "secret123"
   Secure: password = os.getenv("PASSWORD", "config_value")

Focus responses on:
- Specifically preventing sensitive data sharing with LLMs
- Using the exact placeholder patterns shown above
- Explaining WHY sanitization protects privacy
- Brief, actionable advice

Keep examples focused on removing sensitive patterns from code."""
            
            # Generate response
            full_prompt = f"{system_prompt}\n\nUser: {message}\n\nAssistant:"
            response_data = self.ollama_client.generate_response(full_prompt, stream=False)
            
            if not self.stop_thinking and response_data:
                # Extract response text and token info
                response_text = response_data.get('response', '')
                
                # Use Ollama's actual token counts
                prompt_tokens = response_data.get('total_duration', 0)  # This might not be tokens, let me check better field
                response_tokens = response_data.get('prompt_eval_count', 0)
                eval_tokens = response_data.get('eval_count', 0)
                total_tokens = response_tokens + eval_tokens
                
                self.total_tokens += total_tokens
                
                # Store processing time for tokens/sec calculation
                processing_duration = response_data.get('total_duration', 0)  # nanoseconds
                processing_time_sec = processing_duration / 1_000_000_000 if processing_duration > 0 else 0
                
                # Calculate tokens/sec for this interaction
                tokens_per_sec = total_tokens / processing_time_sec if processing_time_sec > 0 else 0
                # REMOVED: self.session_metrics['current_tokens_per_sec'] = tokens_per_sec  # This overwrites!
                
                # Handle response in main thread
                self.main_app.root.after(0, self._handle_chat_response, response_text)
            
        except Exception as e:
            if not self.stop_thinking:
                error_msg = f"Chat error: {str(e)}"
                self.main_app.root.after(0, self._handle_chat_error, error_msg)
        finally:
            # Reset thinking state and clear thinking indicator
            self.is_thinking = False
            self.main_app.root.after(0, self._clear_thinking_indicator)
    
    def _handle_chat_error(self, error_msg: str):
        """Handle chat error in main thread"""
        try:
            # Add error message
            self.main_app.practice_chat_display.config(state=tk.NORMAL)
            self.main_app.practice_chat_display.insert(tk.END, f"❌ Error: {error_msg}\n")
            self.main_app.practice_chat_display.see(tk.END)
            self.main_app.practice_chat_display.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Error handling chat error: {e}")
    
    def _handle_analysis_error(self, error_msg: str):
        """Handle analysis error in main thread"""
        try:
            # Add error message
            self.main_app.practice_chat_display.config(state=tk.NORMAL)
            self.main_app.practice_chat_display.insert(tk.END, f"❌ Analysis Error: {error_msg}\n")
            self.main_app.practice_chat_display.see(tk.END)
            self.main_app.practice_chat_display.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Error handling analysis error: {e}")
    
    def _start_timer(self):
        """Start the real-time timer"""
        if not self.timer_running:
            self.timer_running = True
            self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
            self.timer_thread.start()
    
    def _stop_timer(self):
        """Stop the real-time timer"""
        self.timer_running = False
        if self.timer_thread:
            self.timer_thread.join(timeout=1)
    
    def _timer_loop(self):
        """Timer loop for real-time updates"""
        while self.timer_running and self.session_active:
            try:
                # Update footer in main thread
                self.main_app.root.after(0, self._update_footer)
                time.sleep(1)  # Update every second
            except Exception as e:
                print(f"Timer error: {e}")
                break
    
    def _run_code_analysis(self, code: str, model: str) -> None:
        """Run code analysis using the main analysis system"""
        try:
            # Show analyzing message
            self._add_ai_message("Analyzing your code for security issues...")
            
            # Run analysis in thread
            analysis_thread = threading.Thread(
                target=self._code_analysis_thread,
                args=(code, model)
            )
            analysis_thread.daemon = True
            analysis_thread.start()
            
        except Exception as e:
            self._add_ai_message(f"Error analyzing code: {str(e)}")
    
    def _run_chat_analysis(self, message: str, model: str) -> None:
        """Run regular chat analysis"""
        try:
            # Check if message is too short for meaningful analysis
            words = message.strip().split()
            if len(words) < 3:
                self._add_ai_message(f"I see you've shared \"{message}\". For meaningful security analysis, please provide more context:\n\n• Share actual code snippets (3+ words)\n• Describe specific security concerns\n• Ask about security best practices\n\nI'm here to help with comprehensive security guidance!")
                return
            
            # Show analyzing message
            self._add_ai_message("Analyzing your message...")
            
            # Run analysis in thread
            analysis_thread = threading.Thread(
                target=self._chat_analysis_thread,
                args=(message, model)
            )
            analysis_thread.daemon = True
            analysis_thread.start()
            
        except Exception as e:
            self._add_ai_message(f"Error analyzing message: {str(e)}")
    
    def _code_analysis_thread(self, code: str, model: str) -> None:
        """Run code analysis in separate thread"""
        try:
            # Track code analysis for duplicate detection (display only)
            self._track_code_analysis(code)
            
            # Set model
            self.ollama_client.set_model(model)
            
            # Use main analysis system
            raw_result = self.analyzer.analyze_code(code, model)
            
            if raw_result and raw_result.get('success', False):
                # Use corrected analysis_table from OllamaAnalyzer (includes manual line count fix)
                analysis_table = raw_result.get('analysis_table', {})
                
                # Store analysis data
                analysis_data = {
                    'timestamp': time.time(),
                    'code_snippet': code[:200] + '...' if len(code) > 200 else code,
                    'analysis_result': analysis_table
                }
                self.code_analyses.append(analysis_data)
                
                # Update session metrics
                self._update_session_metrics(analysis_table)
                
                # Use actual token counts from Ollama if available
                if 'raw_response_data' in raw_result:
                    response_data = raw_result['raw_response_data']
                    prompt_tokens = response_data.get('prompt_eval_count', 0)
                    eval_tokens = response_data.get('eval_count', 0)
                    prompt_draft_tokens = response_data.get('prompt_draft_count', 0)
                    eval_draft_tokens = response_data.get('eval_draft_count', 0)
                    
                    # Include ALL tokens: input processing + output generation + drafts
                    total_input_tokens = prompt_tokens + prompt_draft_tokens
                    total_output_tokens = eval_tokens + eval_draft_tokens
                    actual_tokens = total_input_tokens + total_output_tokens
                    
                    
                    # DON'T add tokens here - they're already added in _handle_code_analysis_result
                    # self.total_tokens += actual_tokens  # COMMENTED OUT - duplicate counting
                    
                    # Store tokens/sec for code analysis
                    processing_duration = response_data.get('total_duration', 0)
                    processing_time_sec = processing_duration / 1_000_000_000 if processing_duration > 0 else 0
                    tokens_per_sec = actual_tokens / processing_time_sec if processing_time_sec > 0 else 0
                    # REMOVED: self.session_metrics['current_tokens_per_sec'] = tokens_per_sec  # This overwrites!
                else:
                    # Fallback: estimate tokens
                    estimated_tokens = len(code.split()) + len(raw_result['raw_response'].split())
                    self.total_tokens += estimated_tokens
                
                # Update UI in main thread (pass raw_result for token info)
                self.main_app.root.after(0, self._handle_code_analysis_result, raw_result)
            else:
                error_msg = "I couldn't analyze your code. Please try again."
                self.main_app.root.after(0, self._handle_chat_response, error_msg)
            
        except Exception as e:
            import traceback
            # Update analyses count even on error to track attempts
            self.session_metrics['analysis_count'] += 1
            error_msg = f"Error analyzing code: {str(e)}"
            self.main_app.root.after(0, self._handle_chat_response, error_msg)
    
    def _chat_analysis_thread(self, message: str, model: str) -> None:
        """Run chat analysis in separate thread"""
        try:
            # Set model
            self.ollama_client.set_model(model)
            
            # Create security analysis prompt
            system_prompt = f"""You are an AI Security Mentor. Analyze the user's message for potential security issues, sensitive data exposure, or security best practices. Provide helpful guidance and recommendations.

Focus on:
- Sensitive data exposure (passwords, API keys, personal info)
- Security vulnerabilities
- Best practices
- Compliance concerns (HIPAA, PCI-DSS, etc.)

Be educational and helpful, not just critical."""
            
            full_prompt = f"{system_prompt}\n\nUser message: {message}"
            
            # Get LLM response
            response_data = self.ollama_client.generate_response(full_prompt, stream=False)
            
            if not self.stop_thinking and response_data:
                # Extract response text
                ai_response = response_data.get('response', '')
                
                # Use actual token counts from Ollama
                prompt_tokens = response_data.get('prompt_eval_count', 0)
                eval_tokens = response_data.get('eval_count', 0)
                total_tokens = prompt_tokens + eval_tokens
                
                self.total_tokens += total_tokens
                
                # Store tokens/sec for code analysis
                processing_duration = response_data.get('total_duration', 0)  # nanoseconds
                processing_time_sec = processing_duration / 1_000_000_000 if processing_duration > 0 else 0
                tokens_per_sec = total_tokens / processing_time_sec if processing_time_sec > 0 else 0
                # REMOVED: self.session_metrics['current_tokens_per_sec'] = tokens_per_sec  # This overwrites!
            else:
                # Handle case when stop_thinking is True or response_data is None
                if self.stop_thinking:
                    ai_response = "Response stopped by user."
                else:
                    ai_response = "I'm sorry, I couldn't process your message. Please try again."
            
            # Update UI in main thread
            self.main_app.root.after(0, self._handle_chat_response, ai_response)
            
        except Exception as e:
            error_msg = f"Error analyzing message: {str(e)}"
            self.main_app.root.after(0, self._handle_chat_response, error_msg)
    
    def _handle_code_analysis_result(self, raw_result: Dict) -> None:
        """Handle code analysis result in main thread"""
        
        # Extract the analysis data for metrics
        if 'raw_response_data' in raw_result:
            response_data = raw_result['raw_response_data']
            
            # Get token counts from Ollama (confirmed fields)
            prompt_tokens = response_data.get('prompt_eval_count', 0)  # Input tokens (user prompt)
            eval_tokens = response_data.get('eval_count', 0)            # Output tokens (AI response)
            
            # Total tokens = input + output (no draft tokens in llama3.2:3b)
            actual_tokens = prompt_tokens + eval_tokens
            
            
            # Add tokens only ONCE in this handler (not in the thread)
            self.total_tokens += actual_tokens
            
            
            # Store tokens/sec for code analysis (for THIS interaction only)
            processing_duration = response_data.get('total_duration', 0)
            processing_time_sec = processing_duration / 1_000_000_000 if processing_duration > 0 else 0
            tokens_per_sec = actual_tokens / processing_time_sec if processing_time_sec > 0 else 0
            
            # Store individual token counts for footer display
            self.session_metrics['current_tokens_per_sec'] = tokens_per_sec
            self.session_metrics['current_input_tokens'] = prompt_tokens
            self.session_metrics['current_output_tokens'] = eval_tokens
        
        # Extract the actual analysis data from the result
        if 'analysis_table' in raw_result and raw_result['analysis_table']:
            actual_analysis_data = raw_result['analysis_table']
        else:
            actual_analysis_data = raw_result
        
        # Update session metrics with new analysis data
        self._update_session_metrics(actual_analysis_data)
        
        # Format analysis results
        analysis_summary = self._format_code_analysis_summary(actual_analysis_data)
        self._add_ai_message(analysis_summary)
        
        # Add secure coding suggestions with placeholders
        secure_suggestions = self._generate_secure_coding_suggestions(actual_analysis_data)
        if secure_suggestions:
            self._add_ai_message(secure_suggestions)
        
        # Update footer
        self._update_footer()
    
    def _generate_secure_coding_suggestions(self, analysis_data: Dict) -> str:
        """Generate secure coding suggestions with placeholder examples"""
        suggestions = []
        
        # Check if we have detected sensitive data
        has_sensitive_data = (
            analysis_data.get('sensitive_data', 0) > 0 or
            analysis_data.get('pii_count', 0) > 0 or
            analysis_data.get('hepa_count', 0) > 0 or
            analysis_data.get('medical_count', 0) > 0 or
            analysis_data.get('compliance_api_count', 0) > 0
        )
        
        if has_sensitive_data:
            suggestions.append("🔒 SECURE CODING SUGGESTIONS:")
            suggestions.append("")
            
            if analysis_data.get('compliance_api_count', 0) > 0:
                suggestions.append("API Keys & Secrets:")
                suggestions.append("❌ Vulnerable: api_key = \"sk-1234567890abcdef\"")
                suggestions.append("✅ Secure: api_key = os.getenv(\"API_KEY\", \"placeholder_value\")")
                suggestions.append("")
            
            if analysis_data.get('pii_count', 0) > 0:
                suggestions.append("Personal Information:")
                suggestions.append("❌ Vulnerable: user_email = \"john.doe@example.com\"")
                suggestions.append("✅ Secure: user_email = os.getenv(\"USER_EMAIL\", \"placeholder_email@example.com\")")
                suggestions.append("")
            
            if analysis_data.get('medical_count', 0) > 0:
                suggestions.append("Medical Records:")
                suggestions.append("❌ Vulnerable: patient_name = \"John Smith\"")
                suggestions.append("✅ Secure: patient_name = os.getenv(\"PATIENT_NAME\", \"placeholder_patient_name\")")
                suggestions.append("")
            
            suggestions.append("👆 Best Practices:")
            suggestions.append("• Use environment variables for all sensitive data")
            suggestions.append("• Replace hardcoded values with 'placeholder_value'")
            suggestions.append("• Never commit real secrets to version control")
            suggestions.append("• Implement proper data masking for user-facing content")
            
            return "\n".join(suggestions)
        
        return ""  # No suggestions if no sensitive data detected
    
    def _handle_chat_response(self, response: str) -> None:
        """Handle chat response in main thread"""
        # Add AI response
        self._add_ai_message(response)
        
        # Update footer
        self._update_footer()
    
    def _format_code_analysis_summary(self, analysis_data: Dict) -> str:
        """Format code analysis results for display"""
        lines = analysis_data.get('lines', 0)
        sensitive_fields = analysis_data.get('sensitive_fields', 0)
        sensitive_data = analysis_data.get('sensitive_data', 0)
        pii = analysis_data.get('pii', 0)
        medical = analysis_data.get('medical', 0)
        compliance_api = analysis_data.get('compliance_api', 0)
        risk_score = analysis_data.get('risk_score', 0)
        
        # Determine risk level
        if risk_score >= 101:
            risk_level = "CRITICAL"
        elif risk_score >= 100:
            risk_level = "HIGH"
        elif risk_score >= 80:
            risk_level = "MEDIUM"
        elif risk_score >= 20:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        # Get session totals
        session_totals = self._get_session_totals()
        avg_risk_score = self._get_average_risk_score()
        avg_risk_level = self._get_risk_level(avg_risk_score)
        
        # Add duplicate indicator if this is a duplicate analysis
        duplicate_indicator = "🔄 [DUPLICATE ANALYSIS]" if self.is_current_duplicate else ""
        
        summary = f"""Code Analysis Results:
{duplicate_indicator}
📊 Current Analysis:
• Lines of Code: {lines}
• Sensitive Fields: {sensitive_fields}
• Sensitive Data: {sensitive_data}
• PII Count: {pii}  
• Medical Data: {medical}
• API/Security: {compliance_api}
• Risk Score: {risk_score}/100 ({risk_level} RISK)

📈 Session Totals:
• Total Lines: {session_totals['total_lines']}
• Total Sensitive Fields: {session_totals['total_sensitive_fields']}
• Total Sensitive Data: {session_totals['total_sensitive_data']}
• Total PII: {session_totals['total_pii']}
• Total Medical: {session_totals['total_medical']}
• Total API/Security: {session_totals['total_compliance_api']}
• Average Risk Score: {avg_risk_score}/100 ({avg_risk_level} RISK)
• Total Analyses: {self.session_metrics['analysis_count']}
• Unique Code Analyses: {len(self.unique_code_hashes)}
• Duplicate Analyses: {self.duplicate_analysis_count}

"""
        
        if risk_score >= 80:
            summary += "🚨 HIGH RISK detected! Please review and address security issues."
        elif risk_score >= 60:
            summary += "⚠️ MEDIUM RISK detected. Consider security improvements."
        elif risk_score >= 30:
            summary += "🟢 LOW RISK detected. Good security practices observed."
        else:
            summary += "✅ MINIMAL RISK. Excellent security practices!"
        
        return summary
    
    def _update_session_metrics(self, analysis_data: Dict) -> None:
        """Update session metrics with new analysis data"""
        self.session_metrics['total_lines'] += analysis_data.get('lines', 0)
        self.session_metrics['total_sensitive_fields'] += analysis_data.get('sensitive_fields', 0)
        self.session_metrics['total_sensitive_data'] += analysis_data.get('sensitive_data', 0)
        self.session_metrics['total_pii'] += analysis_data.get('pii', 0)
        self.session_metrics['total_hepa'] += analysis_data.get('hepa', 0)
        self.session_metrics['total_medical'] += analysis_data.get('medical', 0)
        self.session_metrics['total_compliance_api'] += analysis_data.get('compliance_api', 0)
        self.session_metrics['risk_scores'].append(analysis_data.get('risk_score', 0))
        self.session_metrics['analysis_count'] += 1
    
    def _get_session_totals(self) -> Dict:
        """Get current session totals"""
        return {
            'total_lines': self.session_metrics['total_lines'],
            'total_sensitive_fields': self.session_metrics['total_sensitive_fields'],
            'total_sensitive_data': self.session_metrics['total_sensitive_data'],
            'total_pii': self.session_metrics['total_pii'],
            'total_medical': self.session_metrics['total_medical'],
            'total_compliance_api': self.session_metrics['total_compliance_api']
        }
    
    def _get_average_risk_score(self) -> float:
        """Get average risk score for the session"""
        if not self.session_metrics['risk_scores']:
            return 0.0
        return sum(self.session_metrics['risk_scores']) / len(self.session_metrics['risk_scores'])
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Get risk level based on score"""
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
    
    def _calculate_final_metrics(self) -> Dict:
        """Calculate final metrics for the session"""
        avg_risk_score = self._get_average_risk_score()
        avg_risk_level = self._get_risk_level(avg_risk_score)
        
        return {
            "total_lines": self.session_metrics['total_lines'],
            "total_sensitive_fields": self.session_metrics['total_sensitive_fields'],
            "total_sensitive_data": self.session_metrics['total_sensitive_data'],
            "total_pii": self.session_metrics['total_pii'],
            "total_hepa": self.session_metrics['total_hepa'],
            "total_medical": self.session_metrics['total_medical'],
            "total_compliance_api": self.session_metrics['total_compliance_api'],
            "average_risk_score": round(avg_risk_score, 2),
            "risk_level": avg_risk_level,
            "total_analyses": self.session_metrics['analysis_count']
        }
    
    def _save_session_data(self, session_data: Dict) -> None:
        """Save session data to JSON file"""
        try:
            # Create sessions directory
            sessions_dir = "core/logs/sessions"
            os.makedirs(sessions_dir, exist_ok=True)
            
            # Create filename
            filename = f"{sessions_dir}/{self.session_id}.json"
            
            # Save to JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            print(f"Practice session data saved to: {filename}")
            
            # Also save detailed analysis data to separate file
            self._save_analysis_details()
            
        except Exception as e:
            print(f"Error saving practice session data: {e}")
    
    def _save_analysis_details(self) -> None:
        """Save detailed analysis data to detailed_sessions folder for risk viewer"""
        try:
            if not self.code_analyses:
                return  # No analyses to save
            
            # Create detailed_sessions directory (where risk viewer looks)
            detailed_sessions_dir = "detailed_sessions"
            os.makedirs(detailed_sessions_dir, exist_ok=True)
            
            # Get final metrics for the session
            final_metrics = self._calculate_final_metrics()
            
            # Create detailed session data in the format expected by risk viewer
            detailed_session = {
                "session_id": self.session_id,
                "user_name": self.user_name,
                "session_start_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.session_start_time)),
                "session_end_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.session_end_time)),
                "session_duration": self.session_end_time - self.session_start_time,
                "analysis_timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "code_length": final_metrics.get('total_lines', 0),
                "risk_score": final_metrics.get('average_risk_score', 0),
                "risk_level": final_metrics.get('risk_level', 'UNKNOWN'),
                "sensitive_fields": final_metrics.get('total_sensitive_fields', 0),
                "sensitive_data": final_metrics.get('total_sensitive_data', 0),
                "pii_count": final_metrics.get('total_pii', 0),
                "medical_count": final_metrics.get('total_medical', 0),
                "hepa_count": final_metrics.get('total_hepa', 0),
                "api_security_count": final_metrics.get('total_compliance_api', 0),
                "current_analysis": {
                    "total_lines": final_metrics.get('total_lines', 0),
                    "total_sensitive_fields": final_metrics.get('total_sensitive_fields', 0),
                    "total_sensitive_data": final_metrics.get('total_sensitive_data', 0),
                    "total_pii": final_metrics.get('total_pii', 0),
                    "total_medical": final_metrics.get('total_medical', 0),
                    "total_hepa": final_metrics.get('total_hepa', 0),
                    "total_compliance_api": final_metrics.get('total_compliance_api', 0),
                    "average_risk_score": final_metrics.get('average_risk_score', 0),
                    "risk_level": final_metrics.get('risk_level', 'UNKNOWN'),
                    "total_analyses": final_metrics.get('total_analyses', 0),
                    "sensitive_fields": {"items": []},
                    "sensitive_data": {"items": []},
                    "pii": {"items": []},
                    "medical": {"items": []},
                    "api_security": {"items": []}
                },
                "session_totals": final_metrics,
                "code_content": "",
                "conversations": self.conversations.copy() if hasattr(self, 'conversations') else []
            }
            
            # Extract code content from analyses
            code_content = ""
            if self.code_analyses:
                code_content = self.code_analyses[0].get('code_snippet', '')
                detailed_session["code_content"] = code_content
            
            # Parse code content to extract sensitive items
            if code_content:
                sensitive_items = self._parse_sensitive_items_from_code(code_content, final_metrics)
                
                # Update current_analysis with parsed items
                detailed_session["current_analysis"]["sensitive_fields"]["items"] = sensitive_items.get('sensitive_fields', [])
                detailed_session["current_analysis"]["sensitive_data"]["items"] = sensitive_items.get('sensitive_data', [])
                detailed_session["current_analysis"]["pii"]["items"] = sensitive_items.get('pii', [])
                detailed_session["current_analysis"]["medical"]["items"] = sensitive_items.get('medical', [])
                detailed_session["current_analysis"]["api_security"]["items"] = sensitive_items.get('api_security', [])
            
            # Save to detailed_sessions directory with _detailed.json suffix
            detailed_filename = f"{detailed_sessions_dir}/{self.session_id}_detailed.json"
            with open(detailed_filename, 'w', encoding='utf-8') as f:
                json.dump(detailed_session, f, indent=2, ensure_ascii=False)
            
            print(f"Detailed session data saved to: {detailed_filename}")
            
        except Exception as e:
            print(f"Error saving detailed session data: {e}")
    
    def _parse_sensitive_items_from_code(self, code_content: str, final_metrics: Dict) -> Dict:
        """Parse code content to extract sensitive items for detailed analysis"""
        try:
            import re
            
            lines = code_content.split('\n')
            sensitive_items = {
                'sensitive_fields': [],
                'sensitive_data': [],
                'pii': [],
                'medical': [],
                'api_security': []
            }
            
            # Define patterns for different types of sensitive data
            patterns = {
                'pii': [
                    r'(?:ssn|social_security|date_of_birth|birth_date|phone|email|address|full_name|first_name|last_name)\s*[:=]\s*["\']([^"\']+)["\']',
                    r'["\']([0-9]{3}-[0-9]{2}-[0-9]{4})["\']',  # SSN pattern
                    r'["\']([0-9]{2}/[0-9]{2}/[0-9]{4})["\']',  # Date pattern
                    r'["\'](\([0-9]{3}\)\s*[0-9]{3}-[0-9]{4})["\']',  # Phone pattern
                ],
                'medical': [
                    r'(?:patient_id|medical_record|diagnosis|medication|allergy|blood_type|prescription|lab_result|medical_data)\s*[:=]\s*["\']([^"\']+)["\']',
                    r'["\'](PAT-[0-9]+)["\']',  # Patient ID pattern
                    r'["\'](MR-[0-9]+)["\']',   # Medical record pattern
                    r'["\'](RX-[0-9]+)["\']',   # Prescription pattern
                ],
                'api_security': [
                    r'(?:api_key|secret_key|password|token|auth|credential|private_key|encryption_key)\s*[:=]\s*["\']([^"\']+)["\']',
                    r'["\'](sk-[a-zA-Z0-9]+)["\']',  # API key pattern
                    r'["\'](Bearer\s+[a-zA-Z0-9]+)["\']',  # Bearer token pattern
                    r'["\'](-----BEGIN\s+PRIVATE\s+KEY-----[^"]+)["\']',  # Private key pattern
                ]
            }
            
            # Extract items from code
            for line_num, line in enumerate(lines, 1):
                line_lower = line.lower()
                
                # Check each category
                for category, pattern_list in patterns.items():
                    for pattern in pattern_list:
                        matches = re.findall(pattern, line, re.IGNORECASE)
                        for match in matches:
                            if isinstance(match, tuple):
                                match = match[0] if match[0] else match[1]
                            
                            # Truncate very long values
                            display_value = match[:50] + "..." if len(match) > 50 else match
                            
                            item = {
                                'name': display_value,
                                'line': line_num,
                                'category': category.title(),
                                'type': 'sensitive_data'
                            }
                            
                            # Add to appropriate category
                            if category == 'pii':
                                sensitive_items['pii'].append(item)
                            elif category == 'medical':
                                sensitive_items['medical'].append(item)
                            elif category == 'api_security':
                                sensitive_items['api_security'].append(item)
                            
                            # Also add to general sensitive_data
                            sensitive_items['sensitive_data'].append(item)
                
                # Extract field names (variable names)
                field_patterns = [
                    r'(?:patient_id|ssn|api_key|secret_key|password|token|email|phone|address|full_name|date_of_birth|diagnosis|medication|allergy|blood_type)',
                ]
                
                for pattern in field_patterns:
                    if re.search(pattern, line_lower):
                        # Extract the variable name
                        var_match = re.search(r'(\w+)\s*[:=]', line)
                        if var_match:
                            field_name = var_match.group(1)
                            item = {
                                'name': field_name,
                                'line': line_num,
                                'category': 'General',
                                'type': 'sensitive_field'
                            }
                            sensitive_items['sensitive_fields'].append(item)
            
            return sensitive_items
            
        except Exception as e:
            print(f"Error parsing sensitive items from code: {e}")
            return {
                'sensitive_fields': [],
                'sensitive_data': [],
                'pii': [],
                'medical': [],
                'api_security': []
            }
    
    def _update_session_info(self, user_id: str, model: str) -> None:
        """Update session information display"""
        session_start_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.session_start_time))
        session_info = f"""Session ID: {self.session_id}
User: {user_id}
Model: {model}
Start Time: {session_start_time_str}
Status: Active"""
        
        self.main_app.practice_session_info_text.config(state=tk.NORMAL)
        self.main_app.practice_session_info_text.delete(1.0, tk.END)
        self.main_app.practice_session_info_text.insert(tk.END, session_info)
        self.main_app.practice_session_info_text.config(state=tk.DISABLED)
    
    def _add_welcome_message(self, user_id: str) -> None:
        """Add welcome message to chat (limited to 10 lines)"""
        welcome_message = f"""Hello {user_id}! I'm your AI Security Mentor.

I can help you with:
• Analyzing code for security vulnerabilities
• Identifying sensitive data exposure
• Providing security best practices
• Compliance guidance (HIPAA, PCI-DSS, etc.)

Simply paste your code or describe your security questions, and I'll provide detailed analysis and recommendations.

Let's start with secure coding practices!"""
        
        self.main_app.practice_chat_display.config(state=tk.NORMAL)
        self.main_app.practice_chat_display.insert(tk.END, "AI Security Mentor: ", "ai_name")
        self._format_and_insert_ai_content(welcome_message)
        self.main_app.practice_chat_display.config(state=tk.DISABLED)
    
    def _add_user_message(self, message: str) -> None:
        """Add user message to chat and capture conversation"""
        # Add to UI
        self.main_app.practice_chat_display.config(state=tk.NORMAL)
        self.main_app.practice_chat_display.insert(tk.END, f"{self.user_name}: {message}\n", "user_name")
        self.main_app.practice_chat_display.config(state=tk.DISABLED)
        
        # Capture conversation data
        conversation_entry = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "user": self.user_name,
            "message": message,
            "message_type": "code_submission" if self._detect_code_in_message(message) else "text",
            "session_id": self.session_id
        }
        self.conversations.append(conversation_entry)
    
    def _add_ai_message(self, message: str) -> None:
        """Add AI message to chat with color coding and capture conversation"""
        # Add to UI
        self.main_app.practice_chat_display.config(state=tk.NORMAL)
        self.main_app.practice_chat_display.insert(tk.END, "AI Security Mentor: ", "ai_name")
        
        # Format and insert message with color coding
        self._format_and_insert_ai_content(message)
        self.main_app.practice_chat_display.see(tk.END)
        self.main_app.practice_chat_display.config(state=tk.DISABLED)
        
        # Capture AI conversation data
        conversation_entry = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "user": "AI Security Mentor",
            "message": message,
            "message_type": "analysis_response",
            "session_id": self.session_id
        }
        self.conversations.append(conversation_entry)
    
    def _format_and_insert_ai_content(self, message: str) -> None:
        """Format and insert AI message content with color coding"""
        lines = message.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                self.main_app.practice_chat_display.insert(tk.END, "\n")
                continue
                
            # Check for code-like content (contains specific patterns)
            if ('```' in line or 'def ' in line or (line.count('=') > 0 and not line.startswith('=')) or 
                'return ' in line or line.startswith('api_key') or line.startswith('password') or 
                line.startswith('TOKEN') or '_key' in line or 'secret' in line.lower()):
                # Code suggestion - orange
                self.main_app.practice_chat_display.insert(tk.END, line, "code_suggestion")
            elif ('tip:' in line.lower() or 'recommendation:' in line.lower() or 
                  'best practice:' in line.lower() or 'security tip:' in line.lower()):
                # Security tip - sky blue
                self.main_app.practice_chat_display.insert(tk.END, line, "security_tip")
            else:
                # Regular AI response - light green
                self.main_app.practice_chat_display.insert(tk.END, line, "ai_response")
            
            self.main_app.practice_chat_display.insert(tk.END, "\n")
    
    
    def _update_footer(self) -> None:
        """Update footer with session details"""
        try:
            if not self.session_active:
                footer_text = "Ready to start practice session"
            else:
                duration = time.time() - self.session_start_time
                
                # Get current tokens/sec from Ollama processing  
                current_tokens_per_sec = self.session_metrics.get('current_tokens_per_sec', 0)
                
                # Create detailed token breakdown like Ollama verbose output
                current_input_tokens = self.session_metrics.get('current_input_tokens', 0)
                current_output_tokens = self.session_metrics.get('current_output_tokens', 0)
                
                if current_input_tokens > 0 or current_output_tokens > 0:
                    token_breakdown = f"📥 Token Input: {current_input_tokens}  📤 Token Output: {current_output_tokens}  ⚡ Rate: {current_tokens_per_sec:.1f}/s"
                else:
                    token_breakdown = ""
                
                # Create brief analysis summary (remove commas from numbers)
                avg_risk = sum(self.session_metrics['risk_scores'])/len(self.session_metrics['risk_scores']) if self.session_metrics['risk_scores'] else 0
                analysis_summary = f"Lines: {self.session_metrics['total_lines']} Fields: {self.session_metrics['total_sensitive_fields']} Data: {self.session_metrics['total_sensitive_data']} Risk: {avg_risk:.1f}"
                
                if token_breakdown:
                    footer_text = f"Session Duration: {duration:.0f}s | Messages: {self.message_count} | Total Tokens: {self.total_tokens} | {token_breakdown} | Analyses: {self.session_metrics['analysis_count']} | {analysis_summary}"
                else:
                    footer_text = f"Session Duration: {duration:.0f}s | Messages: {self.message_count} | Total Tokens: {self.total_tokens} | Analyses: {self.session_metrics['analysis_count']} | {analysis_summary}"
            
            self.main_app.practice_token_details_var.set(footer_text)
        except Exception as e:
            print(f"Error updating footer: {e}")
    
    def clear_chat(self) -> None:
        """Clear the chat display"""
        self.main_app.practice_chat_display.config(state=tk.NORMAL)
        self.main_app.practice_chat_display.delete(1.0, tk.END)
        self.main_app.practice_chat_display.config(state=tk.DISABLED)
    
    def is_session_active(self) -> bool:
        """Check if session is currently active"""
        return self.session_active
    
    def _trigger_scoreboard_refresh(self):
        """Trigger scoreboard refresh if available"""
        try:
            # Check if main app has scoreboard viewer
            if hasattr(self.main_app, 'scoreboard_viewer') and self.main_app.scoreboard_viewer:
                self.main_app.scoreboard_viewer.refresh_data()
            elif hasattr(self.main_app, 'open_scoreboard'):
                # If scoreboard is not open, we can't refresh it directly
                # The scoreboard will pick up the new data on next auto-refresh
                pass
        except Exception as e:
            print(f"Could not refresh scoreboard: {e}")
    
    def is_user_session_active(self, user_id: str) -> bool:
        """Check if a specific user has an active session or existing session file"""
        # Check active sessions first
        if user_id in self.active_sessions:
            return True
        
        # Check for existing session files
        sessions_dir = Path("core/logs/sessions")
        if sessions_dir.exists():
            for file_path in sessions_dir.glob(f"practice_{user_id}_*.json"):
                try:
                    with open(file_path, 'r') as f:
                        session_data = json.load(f)
                    
                    # Check if session is recent (within last 24 hours)
                    session_start = session_data.get('session_start_time')
                    if session_start:
                        try:
                            start_time = time.mktime(time.strptime(session_start, '%Y-%m-%d %H:%M:%S'))
                            if time.time() - start_time < 86400:  # 24 hours
                                return True
                        except Exception:
                            pass
                except Exception:
                    pass
        
        return False
    
    def get_active_sessions(self) -> Dict:
        """Get all active sessions"""
        return self.active_sessions.copy()
    
    def end_user_session(self, user_id: str) -> bool:
        """End a specific user's session"""
        if user_id not in self.active_sessions:
            return False
        
        # If this is the current user's session, end it normally
        if self.user_name == user_id and self.session_active:
            result = self.end_session()
            return result
        
        # For other users, just remove from active sessions
        # (This is a simplified approach - in a real multi-user system,
        # you'd need to communicate with the actual session instance)
        del self.active_sessions[user_id]
        self._save_active_sessions()
        return True
    
    def force_end_all_sessions(self) -> int:
        """Force end all active sessions"""
        ended_count = 0
        user_ids = list(self.active_sessions.keys())
        
        # End current session if active
        if self.session_active:
            if self.end_session():
                ended_count += 1
        
        # Clear remaining active sessions
        remaining_count = len(self.active_sessions)
        self.active_sessions.clear()
        self._save_active_sessions()
        ended_count += remaining_count
        
        return ended_count
