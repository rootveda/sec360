#!/usr/bin/env python3
"""
Sec360 Scoreboard Viewer - Core Implementation
"""

import tkinter as tk
from tkinter import ttk
import json
import os
import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class UserScoreboardEntry:
    user_id: str
    session_name: str
    total_code_lines: int
    detected_flags: int
    total_potential_flags: int
    risk_score: int
    score: float
    session_duration: float
    most_common_flag: str
    completion_rate: float
    penalty_info: str
    points: float  # Points with decimal precision
    session_type: str  # 'analysis' or 'practice'

class ScoreboardViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sec360 by Abhay - Live Scoreboard")
        self.root.geometry("1400x900")
        # Use default ttk styling (no custom colors)
        
        self.session_data = {}
        self.user_stats = {}
        self.refresh_interval = 30000  # 30 seconds
        
        self.setup_ui()
        self.load_data()
        self.start_auto_refresh()
        
    # Using default ttk styling (no custom theme)
        
    def setup_ui(self):
        """Setup the user interface"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="Live Scoreboard", 
                               font=('Arial', 24, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="All Security Champions", 
                                  font=('Arial', 16))
        subtitle_label.pack()
        
        # Stats summary
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        self.setup_stats_summary(stats_frame)
        
        # Scoreboard table
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        self.setup_scoreboard_table(table_frame)
        
        # Footer
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Column explanations
        explanations_frame = ttk.Frame(footer_frame)
        explanations_frame.pack(fill=tk.X, pady=(0, 10))
        
        explanations_text = """
🏆 Rank = User position | 👤 User = Session participant | 📊 Lines of Code = Total lines analyzed | 🚨 Sensitive Data = Found sensitive data instances | 
⚠️ Sensitive Fields = Total sensitive field patterns | 🎯 Risk Score = AI-calculated risk assessment (0=minimal, 100=high risk) | 🎯 Points = Performance points (0-1000 scale, higher=better security) | 
🎯 Top Flag = User's highest count flag (e.g., PII: 9) | ⏱️ Duration = Total session time
        """
        
        explanations_label = ttk.Label(explanations_frame, text=explanations_text.strip(), 
                                     font=('Arial', 12), wraplength=1200)
        explanations_label.pack()
        
        # Status and refresh
        status_frame = ttk.Frame(footer_frame)
        status_frame.pack(fill=tk.X)
        
        self.last_update_label = ttk.Label(status_frame, text="Last Updated: Never", 
                                          font=('Arial', 12))
        self.last_update_label.pack(side=tk.LEFT)
        
        refresh_btn = ttk.Button(status_frame, text="🔄 Refresh Now", 
                                command=self.refresh_data)
        refresh_btn.pack(side=tk.RIGHT)
        
    def setup_stats_summary(self, parent):
        """Setup statistics summary at the top"""
        summary_frame = ttk.Frame(parent)
        summary_frame.pack(fill=tk.X)
        
        self.total_users_label = ttk.Label(summary_frame, text="Total Users: 0", 
                                          font=('Arial', 12))
        self.total_users_label.pack(side=tk.LEFT, padx=(0, 30))
        
        self.top_performer_label = ttk.Label(summary_frame, text="Top Performer: None (0 pts)", 
                                            font=('Arial', 12))
        self.top_performer_label.pack(side=tk.LEFT, padx=(0, 30))
        
        self.top_flag_label = ttk.Label(summary_frame, text="Top Flag: None (0)", 
                                        font=('Arial', 12))
        self.top_flag_label.pack(side=tk.LEFT)
        
    def setup_scoreboard_table(self, parent):
        """Setup the main scoreboard table"""
        columns = ('Rank', 'User', 'Lines of Code', 'Sensitive Data', 'Sensitive Fields', 'Risk Score', 'Points', 'Top Flag', 'Duration')
        self.scoreboard_tree = ttk.Treeview(parent, columns=columns, show='headings', 
                                          height=20)
        
        # Configure columns
        self.scoreboard_tree.heading('Rank', text='🏆 Rank')
        self.scoreboard_tree.heading('User', text='👤 User')
        self.scoreboard_tree.heading('Lines of Code', text='📊 Lines of Code')
        self.scoreboard_tree.heading('Sensitive Data', text='🚨 Sensitive Data')
        self.scoreboard_tree.heading('Sensitive Fields', text='⚠️ Sensitive Fields')
        self.scoreboard_tree.heading('Risk Score', text='🎯 Risk Score')
        self.scoreboard_tree.heading('Points', text='🎯 Points')
        self.scoreboard_tree.heading('Top Flag', text='🎯 Top Flag')
        self.scoreboard_tree.heading('Duration', text='⏱️ Duration')
        
        # Set column widths
        self.scoreboard_tree.column('Rank', width=60, anchor='center')
        self.scoreboard_tree.column('User', width=120, anchor='w')
        self.scoreboard_tree.column('Lines of Code', width=100, anchor='center')
        self.scoreboard_tree.column('Sensitive Data', width=120, anchor='center')
        self.scoreboard_tree.column('Sensitive Fields', width=120, anchor='center')
        self.scoreboard_tree.column('Risk Score', width=100, anchor='center')
        self.scoreboard_tree.column('Points', width=80, anchor='center')
        self.scoreboard_tree.column('Top Flag', width=120, anchor='center')
        self.scoreboard_tree.column('Duration', width=100, anchor='center')
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.scoreboard_tree.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.scoreboard_tree.xview)
        self.scoreboard_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.scoreboard_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configure row colors
        self.scoreboard_tree.tag_configure('gold', background='#FFD700', foreground='#000000')
        self.scoreboard_tree.tag_configure('silver', background='#C0C0C0', foreground='#000000')
        self.scoreboard_tree.tag_configure('bronze', background='#CD7F32', foreground='#ffffff')
        self.scoreboard_tree.tag_configure('top10', background='#4CAF50', foreground='#ffffff')
        self.scoreboard_tree.tag_configure('normal', background='#2d2d2d', foreground='#ffffff')
        
    def load_data(self):
        """Load session data from log files"""
        self.session_data = {}
        logs_dir = Path("core/logs")
        
        if not logs_dir.exists():
            return
            
        # Load analysis sessions (session_*.json)
        for file_path in logs_dir.glob("session_*.json"):
            session_id = file_path.stem  # Keep the full session ID including "session_"
            try:
                with open(file_path, 'r') as f:
                    logs = []
                    for line in f:
                        if line.strip():
                            logs.append(json.loads(line.strip()))
                    self.session_data[session_id] = logs
            except Exception as e:
                print(f"Error loading session {session_id}: {e}")
        
        # Load practice sessions (practice_*.json)
        sessions_dir = logs_dir / "sessions"
        if sessions_dir.exists():
            for file_path in sessions_dir.glob("practice_*.json"):
                session_id = file_path.stem
                try:
                    with open(file_path, 'r') as f:
                        session_data = json.load(f)
                        # Convert practice session to scoreboard format
                        self.session_data[session_id] = [session_data]
                except Exception as e:
                    print(f"Error loading practice session {session_id}: {e}")
                
        self.calculate_user_stats()
        self.update_scoreboard()
        
    def calculate_user_stats(self):
        """Calculate comprehensive user statistics with duplicate prevention"""
        self.user_stats = {}
        seen_users = set()  # Track users to prevent duplicates
        
        for session_id, logs in self.session_data.items():
            if not logs:
                continue
                
            user_id = self.extract_user_id(session_id)
            
            # Skip if user already exists (prevent duplicates)
            if user_id in seen_users:
                continue
            seen_users.add(user_id)
            
            # Determine session type
            session_type = "practice" if session_id.startswith("practice_") else "analysis"
            
            # Check if session is completed
            if session_type == "practice":
                # For practice sessions, check if it has end time
                if not self.is_practice_session_completed(logs[0]):
                    continue
            else:
                # For analysis sessions, check if it has session end marker
                if not self.is_session_completed(logs):
                    continue  # Skip active/incomplete sessions
            
            # Calculate stats based on session type
            if session_type == "practice":
                total_code_lines, detected_flags, total_potential_flags, risk_score, session_duration, most_common_flag, completion_rate, penalty_info = self.calculate_practice_stats(logs[0])
            else:
                total_code_lines = self.count_code_lines(logs)
                detected_flags = self.count_unique_detected_flags(logs)
                total_potential_flags = self.count_potential_flags(logs)
                risk_score = self.calculate_risk_score(logs)
                session_duration = self.calculate_session_duration(logs)
                most_common_flag = self.get_most_common_flag_type(logs)
                completion_rate = self.calculate_completion_rate(logs)
                penalty_info = "N/A"
            
            # Calculate score and points
            score, penalty_info = self.calculate_advanced_score(logs, total_code_lines, risk_score)
            
            # Calculate points based on session type and data
            points = self.calculate_points(session_type, logs, total_code_lines, risk_score, session_duration)
            
            entry = UserScoreboardEntry(
                user_id=user_id,
                session_name=session_id,
                total_code_lines=total_code_lines,
                detected_flags=detected_flags,
                total_potential_flags=total_potential_flags,
                risk_score=risk_score,
                score=score,
                session_duration=session_duration,
                most_common_flag=most_common_flag,
                completion_rate=completion_rate,
                penalty_info=penalty_info,
                points=points,
                session_type=session_type
            )
            
            self.user_stats[user_id] = [entry]  # Single entry per user
    
    def is_practice_session_completed(self, session_data: Dict) -> bool:
        """Check if a practice session is completed (has end time)"""
        if not session_data:
            return False
        return 'session_end_time' in session_data and session_data.get('session_end_time') is not None
    
    def calculate_practice_stats(self, session_data: Dict) -> tuple:
        """Calculate stats for practice session"""
        try:
            final_metrics = session_data.get('final_analysis_metrics', {})
            
            total_code_lines = final_metrics.get('total_lines', 0)
            detected_flags = final_metrics.get('total_sensitive_fields', 0)
            total_potential_flags = final_metrics.get('total_sensitive_data', 0)
            risk_score = final_metrics.get('average_risk_score', 0)
            session_duration = session_data.get('session_duration', 0) / 60  # Convert to minutes
            
            # Calculate the most common flag from practice session analysis metrics
            flag_counts = {}
            flag_counts['PII'] = final_metrics.get('total_pii_count', final_metrics.get('total_pii', 0))  # Support both key formats
            flag_counts['HEPA'] = final_metrics.get('total_hepa_count', final_metrics.get('total_hepa', 0))
            flag_counts['MEDICAL'] = final_metrics.get('total_medical_count', final_metrics.get('total_medical', 0))
            flag_counts['COMPLIANCE/API'] = final_metrics.get('total_compliance_api_count', final_metrics.get('total_compliance_api', 0))
            
            # Find the flag with highest count
            max_flag_type = max(flag_counts.keys(), key=lambda k: flag_counts[k])
            max_count = flag_counts[max_flag_type]
            
            if max_count > 0:
                most_common_flag = f"{max_flag_type}: {max_count}"
            else:
                most_common_flag = "NO_FLAGS: 0"
                
            completion_rate = 100.0  # Practice sessions are always completed
            penalty_info = "Practice Session"
            
            return total_code_lines, detected_flags, total_potential_flags, risk_score, session_duration, most_common_flag, completion_rate, penalty_info
            
        except Exception as e:
            print(f"Error calculating practice stats: {e}")
            return 0, 0, 0, 0, 0, "Unknown", 0, "Error"
    
    def is_session_completed(self, logs: List[Dict]) -> bool:
        """Check if a session is completed (has session end marker)"""
        if not logs:
            return False
        
        # Check the last log entry for session completion markers
        last_log = logs[-1]
        content = last_log.get('content', '').lower()
        input_preview = last_log.get('input_preview', '').lower()
        
        # Check for session completion markers
        completion_markers = [
            'session completed',
            'session ended',
            'session force-ended'
        ]
        
        for marker in completion_markers:
            if marker in content or marker in input_preview:
                return True
        
        return False
            
    def extract_user_id(self, session_id: str) -> str:
        """Extract clean user ID from session ID"""
        # Handle session IDs like "session_alex_1759325887" or "practice_Alice_1759455000"
        # Remove the filename extension if present
        session_id = session_id.replace('.json', '')
        
        parts = session_id.split('_')
        
        # Handle different session ID formats:
        # session_user_timestamp -> user
        # session_session_user_timestamp -> user (double session prefix)
        # practice_user_timestamp -> user
        if len(parts) >= 4 and parts[0] == 'session' and parts[1] == 'session':
            # Format: session_session_user_timestamp
            user_part = parts[2]  # The user name part
            return user_part
        elif len(parts) >= 3 and parts[0] == 'session':
            # Format: session_user_timestamp
            user_part = parts[1]  # The user name part
            return user_part
        elif len(parts) >= 3 and parts[0] == 'practice':
            # Format: practice_user_timestamp
            user_part = parts[1]  # The user name part
            return user_part
        else:
            return session_id
        
    def count_code_lines(self, logs: List[Dict]) -> int:
        """Count unique lines of code analyzed (prevents duplicate counting)"""
        unique_code_lines = set()  # Use set to track unique lines
        
        for log in logs:
            input_preview = log.get('input_preview', '')
            
            # Skip session start/end messages
            if any(msg in input_preview.lower() for msg in ['session started', 'session completed', 'practice session']):
                continue
                
            # Only process substantial input (more than 100 characters)
            if len(input_preview) < 100:
                continue
            
            # Split input_preview into lines
            lines = input_preview.split('\n')
            
            for line in lines:
                line = line.strip()
                if self.is_code_line(line) and line:  # Only non-empty code lines
                    # Create a normalized version for comparison
                    normalized_line = self.normalize_code_line(line)
                    unique_code_lines.add(normalized_line)
                    
        return len(unique_code_lines)
        
    def normalize_code_line(self, line: str) -> str:
        """Normalize code line to detect duplicates"""
        import re
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', line.strip())
        
        # Remove comments (lines starting with # or //)
        if normalized.startswith('#') or normalized.startswith('//'):
            return normalized
        
        # For variable assignments, normalize variable names
        # e.g., "api_key = 'sk-123'" becomes "VAR = 'sk-123'"
        if '=' in normalized and not normalized.startswith('if') and not normalized.startswith('for'):
            parts = normalized.split('=', 1)
            if len(parts) == 2:
                var_part = parts[0].strip()
                value_part = parts[1].strip()
                
                # Extract variable name (before any brackets or dots)
                var_name = re.split(r'[\[\.]', var_part)[0].strip()
                
                # If it looks like a variable assignment, normalize it
                if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var_name):
                    return f"VAR = {value_part}"
        
        # For function calls, normalize function names
        # e.g., "authenticate_user()" becomes "FUNC()"
        if '(' in normalized and ')' in normalized:
            func_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\(', normalized)
            if func_match:
                return re.sub(r'^[a-zA-Z_][a-zA-Z0-9_]*', 'FUNC', normalized)
        
        return normalized
        
    def count_potential_flags(self, logs: List[Dict]) -> int:
        """Count potential flags using the new two-tier system:
        1. Potential flags: Count all sensitive fields regardless of value
        2. Detected flags: Count only fields with actual sensitive data"""
        
        # Get the original sample code from the log with the longest input_preview (likely the code)
        original_sample_code = ""
        max_length = 0
        for log in logs:
            input_preview = log.get('input_preview', '')
            if input_preview and input_preview.strip() and len(input_preview) > max_length:
                # Skip session start/end messages
                if not any(msg in input_preview.lower() for msg in ['session started', 'session completed', 'practice session']):
                    original_sample_code = input_preview
                    max_length = len(input_preview)
        
        if not original_sample_code:
            # Fallback: count from detected flags if no input_preview
            return self.count_unique_detected_flags(logs)
        
        # Check if input_preview is truncated (ends with "...")
        if original_sample_code.endswith("..."):
            # Input was truncated, we need to get the full original sample code
            # Try to identify which sample file this came from and get the full content
            original_sample_code = self._get_original_sample_code(original_sample_code)
        
        # Check if this is the original sample code or edited code
        # If it's edited code, we need to get the original sample code
        if self._is_edited_code(original_sample_code):
            # This is edited code, get the original sample code
            original_sample_code = self._get_original_sample_code(original_sample_code)
        
        if not original_sample_code:
            # Fallback: count from detected flags if no original sample found
            return self.count_unique_detected_flags(logs)
        
        # Use the data monitor to count potential flags (field-based counting)
        # Add project root to path for imports
        import sys
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))
        
        from core.detection.data_monitor import DataLeakMonitor
        monitor = DataLeakMonitor()
        
        # Count potential flags using the new field-based method
        potential_flags = monitor._count_potential_flags(original_sample_code)
        
        return potential_flags
        
    def _is_edited_code(self, code: str) -> bool:
        """Check if the code appears to be edited (has empty strings for sensitive data)"""
        # Look for patterns that indicate edited code
        edited_indicators = [
            'api_key = ""',
            'secret_key = ""',
            'jwt_token = ""',
            'password = ""',
            'token = ""'
        ]
        
        for indicator in edited_indicators:
            if indicator in code:
                return True
        return False
        
    def _get_original_sample_code(self, edited_code: str) -> str:
        """Get the original sample code based on the edited code"""
        from pathlib import Path
        
        # Try to identify which sample code this is based on the structure
        if 'authenticate_user' in edited_code and 'make_api_call' in edited_code:
            # This looks like the API keys sample
            sample_file = Path('data/samples/api_keys_sample.py')
            if sample_file.exists():
                with open(sample_file, 'r') as f:
                    return f.read()
        
        elif 'process_user_data' in edited_code and 'create_user_profile' in edited_code:
            # This looks like the PII sample
            sample_file = Path('data/samples/pii_sample.py')
            if sample_file.exists():
                with open(sample_file, 'r') as f:
                    return f.read()
        
        elif 'patient_name' in edited_code and 'medical_history' in edited_code:
            # This looks like the medical records sample
            sample_file = Path('data/samples/medical_records_sample.py')
            if sample_file.exists():
                with open(sample_file, 'r') as f:
                    return f.read()
        
        elif 'internal' in edited_code.lower() and 'hostname' in edited_code.lower():
            # This looks like the internal infrastructure sample
            sample_file = Path('data/samples/internal_infrastructure_sample.py')
            if sample_file.exists():
                with open(sample_file, 'r') as f:
                    return f.read()
        
        elif 'compliance' in edited_code.lower() and 'audit' in edited_code.lower():
            # This looks like the compliance sample
            sample_file = Path('data/samples/compliance_sample.py')
            if sample_file.exists():
                with open(sample_file, 'r') as f:
                    return f.read()
        
        return ""
        
    def count_unique_detected_flags(self, logs: List[Dict]) -> int:
        """Count detected flags with proper handling of repeated submissions"""
        seen_field_content_pairs = set()
        detected_flags_count = 0
        
        # Process all logs to count all detected flags
        # Repeated submissions should result in more detected flags
        for log in logs:
            content = log.get('content', '')
            flag_type = log.get('flag_type', 'UNKNOWN')
            context = log.get('context', '')
            
            # Only count actual detected flags (not NO_FLAGS)
            if content and content.strip() and flag_type != 'NO_FLAGS':
                # Extract field name from context (e.g., "first_name = John" -> "first_name")
                field_name = "unknown"
                if " = " in context:
                    field_name = context.split(" = ")[0].strip()
                
                # Create unique identifier for field-content pair
                field_content_key = f"{field_name}:{content.lower().strip()}"
                
                # Skip if we've seen this exact field-content pair before
                if field_content_key in seen_field_content_pairs:
                    continue
                
                # Check for partial matches only within the same field context
                is_duplicate = False
                normalized_content = content.lower().strip()
                
                for seen_pair in seen_field_content_pairs:
                    seen_field, seen_content = seen_pair.split(":", 1)
                    if (seen_field == field_name and 
                        (normalized_content in seen_content or seen_content in normalized_content) and 
                        len(normalized_content) > 3):
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    seen_field_content_pairs.add(field_content_key)
                    detected_flags_count += 1
                    
        return detected_flags_count
        
    def _normalize_input_for_grouping(self, input_preview: str) -> str:
        """Normalize input preview for grouping repeated submissions"""
        # Remove timestamps, session IDs, and other dynamic content
        normalized = input_preview
        
        # Remove common dynamic patterns
        patterns_to_remove = [
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+',  # Timestamps
            r'session_\w+_\d+',  # Session IDs
            r'Practice session started for user: \w+',  # Session start messages
            r'Session completed for user: \w+',  # Session end messages
        ]
        
        for pattern in patterns_to_remove:
            normalized = re.sub(pattern, '', normalized)
        
        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
        
    def calculate_session_duration(self, logs: List[Dict]) -> float:
        """Calculate session duration in minutes based on actual session start and end times"""
        if not logs:
            return 0.001  # Minimum duration for empty sessions
            
        try:
            # Look for session start and end logs with explicit timing
            session_start_time = None
            session_end_time = None
            
            # Check for session start/end logs first
            for log in logs:
                content = log.get('content', '').lower()
                if 'session started' in content or 'practice session started' in content:
                    session_start_time = datetime.datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
                elif 'session ended' in content or 'session completed' in content:
                    session_end_time = datetime.datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
            
            # If we have explicit start and end times, use them
            if session_start_time and session_end_time:
                duration_seconds = (session_end_time - session_start_time).total_seconds()
                duration_minutes = duration_seconds / 60.0
                return min(round(duration_minutes, 4), 480.0)  # Cap at 8 hours
            
            # Fallback: Use first and last log timestamps
            if len(logs) >= 2:
                start_time = datetime.datetime.fromisoformat(logs[0]['timestamp'].replace('Z', '+00:00'))
                end_time = datetime.datetime.fromisoformat(logs[-1]['timestamp'].replace('Z', '+00:00'))
                duration_seconds = (end_time - start_time).total_seconds()
                duration_minutes = duration_seconds / 60.0
                return min(round(duration_minutes, 4), 480.0)
            
            # Single log session - estimate based on log count
            estimated_duration_seconds = max(0.06, len(logs) * 0.1)  # 0.06 seconds = 0.001 minutes
            estimated_duration_minutes = estimated_duration_seconds / 60.0
            return min(round(estimated_duration_minutes, 4), 480.0)
            
        except Exception as e:
            print(f"Error calculating duration: {e}")
            # Return estimated duration based on log count for error cases
            estimated_duration_seconds = max(0.06, len(logs) * 0.1)
            estimated_duration_minutes = estimated_duration_seconds / 60.0
            return max(0.001, min(round(estimated_duration_minutes, 4), 480.0))
        
    def is_code_line(self, line: str) -> bool:
        """Determine if a line looks like code"""
        if not line or len(line) < 3:
            return False
            
        code_patterns = [
            r'^\s*(def|class|import|from|if|for|while|try|except|with|return)\s+',
            r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*[:=]',
            r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\(',
            r'^\s*["\'].*["\']\s*$',
            r'^\s*[{}[\]();,]\s*$',
            r'^\s*#.*$',
            r'^\s*//.*$'
        ]
        
        for pattern in code_patterns:
            if re.match(pattern, line):
                return True
                
        return False
        
    def calculate_risk_score(self, logs: List[Dict]) -> int:
        """Calculate risk score based on detected sensitive data"""
        if not logs:
            return 0
            
        # Count different types of sensitive data
        pii_count = sum(1 for log in logs if log.get('flag_type') == 'PII')
        api_count = sum(1 for log in logs if log.get('flag_type') in ['API_KEY', 'SECRET', 'TOKEN'])
        medical_count = sum(1 for log in logs if log.get('flag_type') == 'MEDICAL')
        compliance_count = sum(1 for log in logs if log.get('flag_type') == 'COMPLIANCE')
        
        # Calculate risk score (0-100)
        base_risk = min(pii_count * 15 + api_count * 12 + medical_count * 10 + compliance_count * 8, 80)
        
        # Add penalty for high volume of sensitive data
        total_sensitive = len([log for log in logs if log.get('flag_type') != 'NO_FLAGS'])
        if total_sensitive > 10:
            base_risk += 20
        elif total_sensitive > 5:
            base_risk += 10
            
        return min(base_risk, 100)
    
    def calculate_advanced_score(self, logs: List[Dict], total_code_lines: int, risk_score: int) -> Tuple[float, str]:
        """Calculate advanced score based on risk score, cleaning performance, and duration"""
        if not logs:
            return 0.0, "No data"
            
        # Count potential flags (what should be flagged)
        unique_potential_flags = self.count_potential_flags(logs)
        
        # Count detected flags (what was actually flagged) with improved deduplication
        unique_detected_flags = self.count_unique_detected_flags(logs)
        
        # Calculate session duration in minutes
        session_duration = self.calculate_session_duration(logs)
        
        # Multi-factor scoring system using risk score
        score = self._calculate_multi_factor_score_with_risk(
            total_code_lines, 
            unique_potential_flags, 
            unique_detected_flags, 
            risk_score,
            session_duration
        )
        
        # Calculate penalty information
        penalty_info = self._calculate_penalty_info(unique_detected_flags, unique_potential_flags, session_duration)
        
        return round(score, 1), penalty_info
    
    def calculate_points(self, session_type: str, logs: List[Dict], total_code_lines: int, risk_score: int, session_duration: float) -> float:
        """Calculate points based on report analysis metrics (NEW SYSTEM)"""
        
        if session_type == "practice":
            # Practice session using NEW report-based calculation
            if len(logs) > 0 and isinstance(logs[0], dict):
                session_data = logs[0]
                final_metrics = session_data.get('final_analysis_metrics', {})
                
                # Extract metrics from final analysis report
                total_lines = final_metrics.get('total_lines', total_code_lines)
                sensitive_data = final_metrics.get('total_sensitive_data', 0)
                duration_minutes = session_duration / 60  # Convert to minutes
                
                return self._calculate_report_based_points(total_lines, sensitive_data, risk_score, duration_minutes)
        
        else:
            # Analysis session using NEW report-based calculation
            # For analysis sessions, we need to estimate sensitive data from flags
            total_flags = sum(log.get('potential_flags', 0) for log in logs)
            sensitive_data = total_flags  # Use total flags as proxy for sensitive data
            duration_minutes = session_duration / 60
            
            return self._calculate_report_based_points(total_code_lines, sensitive_data, risk_score, duration_minutes)
    
    def _calculate_report_based_points(self, total_lines: int, sensitive_data: int, risk_score: int, duration_minutes: float) -> float:
        """
        NEW REPORT-BASED POINTS CALCULATION
        
        Formula: Base + Data Quality + Risk Assessment + Efficiency + Lines Bonus
        
        Args:
            total_lines: Number of lines analyzed
            sensitive_data: Count of sensitive data found
            risk_score: Risk assessment (0-100)
            duration_minutes: Session duration in minutes
        
        Returns:
            float: Total points based on report analysis
        """
        
        # CRITICAL: Users must analyze substantial code to earn points
        if total_lines < 5:
            return 0.0  # Insufficient code analysis = No points earned
        
        # Discourage minimal effort submissions
        if total_lines < 10:
            # Give reduced points for very small code snippets
            lines_penalty = (total_lines - 4) * 5.0  # Penalty reduces with more lines
        
        # 1. Base Points (completion bonus)
        base_points = 25.0
        
        # 2. Data Quality Points (based on sensitive data density)
        data_density = sensitive_data / total_lines
        if data_density <= 0.05:  # ≤ 5% = Excellent
            data_points = 50.0
        elif data_density <= 0.10:  # 5-10% = Good
            data_points = 40.0
        elif data_density <= 0.20:  # 10-20% = Average
            data_points = 25.0
        elif data_density <= 0.30:  # 20-30% = Poor
            data_points = 10.0
        else:  # > 30% = Very Poor
            data_points = 0.0
        
        # 3. Risk Assessment Points (lower risk = higher points, severe penalty)
        risk_points = max(0.0, 100.0 - risk_score * 1.2)
        
        # 4. Efficiency Points (optimal session duration)
        if duration_minutes <= 1.0:  # Too fast
            efficiency_points = 10.0
        elif duration_minutes <= 5.0:  # Ideal range
            efficiency_points = 25.0
        elif duration_minutes <= 10.0:  # Good
            efficiency_points = 20.0
        elif duration_minutes <= 15.0:  # Acceptable
            efficiency_points = 15.0
        else:  # Too slow
            efficiency_points = 5.0
        
        # 5. Lines Bonus (substantial code analysis)
        lines_bonus = min(total_lines / 50.0, 20.0)
        
        # Calculate total points
        total_points = base_points + data_points + risk_points + efficiency_points + lines_bonus
        
        # Apply penalty for minimal code submissions
        if total_lines < 10:
            total_points -= lines_penalty
            total_points = max(total_points, 0.0)  # Don't go below 0
        
        # Cap at maximum (0-1000 range)
        return min(total_points, 1000.0)
    
    def _calculate_penalty_info(self, detected_flags: int, potential_flags: int, duration_minutes: float) -> str:
        """Calculate penalty information for display"""
        penalties = []
        
        # Check for repeated submissions penalty
        if detected_flags > potential_flags and potential_flags > 0:
            submission_ratio = detected_flags / potential_flags
            if submission_ratio > 2.0:
                penalties.append("Heavy Repeated Submissions")
            elif submission_ratio > 1.0:
                penalties.append("Repeated Submissions")
        
        # Check for time penalties
        if duration_minutes < 1:
            penalties.append("Too Fast")
        elif duration_minutes > 30:
            penalties.append("Too Slow")
        
        # Check for unedited sample code
        if potential_flags > 0 and detected_flags >= potential_flags * 0.9:
            penalties.append("Unedited Sample")
        
        if not penalties:
            return "None"
        
        return ", ".join(penalties)
    
    def _calculate_multi_factor_score_with_risk(self, code_lines: int, potential_flags: int, detected_flags: int, risk_score: int, duration_minutes: float) -> float:
        """Calculate score based on risk score, cleaning performance, and duration"""
        
        # Empty sessions (no code, no flags, no meaningful activity) should get 0 score
        if code_lines == 0 and potential_flags == 0 and detected_flags == 0:
            return 0.0
        
        # Factor 1: Risk Score Impact (40% weight)
        # Higher risk score = more potential for security issues = more points for cleaning
        if risk_score == 0:
            risk_factor_score = 100.0  # No risk = perfect score
        elif risk_score < 30:
            risk_factor_score = 90.0   # Low risk
        elif risk_score < 60:
            risk_factor_score = 70.0   # Medium risk
        elif risk_score < 80:
            risk_factor_score = 50.0   # High risk
        else:
            risk_factor_score = 30.0   # Very high risk
        
        # Factor 2: Cleaning Performance (40% weight)
        # How well did the user clean sensitive data?
        if potential_flags == 0:
            # No sensitive data to clean - this should only happen if there's actual code
            if code_lines > 0:
                cleaning_score = 100.0  # Clean code with no sensitive data
            else:
                cleaning_score = 0.0  # No code, no cleaning to evaluate
        else:
            # Handle repeated submissions
            if detected_flags > potential_flags:
                submission_ratio = detected_flags / potential_flags
                if submission_ratio > 2.0:
                    cleaning_score = 0.0  # Heavy repeated submissions
                else:
                    cleaning_score = max(0.0, 50.0 - (submission_ratio - 1.0) * 25.0)
            else:
                # Normal cleaning performance
                cleaning_rate = (potential_flags - detected_flags) / potential_flags
                cleaning_score = cleaning_rate * 100
        
        # Factor 3: Time Efficiency (20% weight)
        # Reasonable time spent = good, too fast or too slow = penalty
        if duration_minutes < 1:
            time_score = 20.0  # Too fast, might not have thought about it
        elif duration_minutes < 5:
            time_score = 80.0  # Good pace
        elif duration_minutes < 15:
            time_score = 100.0  # Optimal time
        elif duration_minutes < 30:
            time_score = 70.0  # A bit slow
        else:
            time_score = 40.0  # Too slow
        
        # Calculate weighted final score
        final_score = (
            risk_factor_score * 0.40 +    # 40% weight
            cleaning_score * 0.40 +       # 40% weight
            time_score * 0.20             # 20% weight
        )
        
        # Apply minimum thresholds
        # Users with very little code or no challenge should not get high scores
        if code_lines < 5 and potential_flags < 3:
            final_score = min(final_score, 60.0)  # Cap at 60% for trivial sessions
        
        # Ensure score is between 0 and 100
        return max(0.0, min(100.0, final_score))
    
    def _calculate_multi_factor_score(self, code_lines: int, potential_flags: int, detected_flags: int, duration_minutes: float) -> float:
        """Calculate score based on four factors: code lines, potential flags, detected flags, and duration"""
        
        # Empty sessions (no code, no flags, no meaningful activity) should get 0 score
        if code_lines == 0 and potential_flags == 0 and detected_flags == 0:
            return 0.0
        
        # Factor 1: Code Complexity (30% weight)
        # More code lines = higher complexity = more effort required
        if code_lines == 0:
            complexity_score = 0.0
        elif code_lines < 10:
            complexity_score = 20.0  # Low complexity
        elif code_lines < 30:
            complexity_score = 50.0  # Medium complexity
        elif code_lines < 100:
            complexity_score = 80.0  # High complexity
        else:
            complexity_score = 100.0  # Very high complexity
        
        # Factor 2: Cleaning Performance (40% weight)
        # How well did the user clean sensitive data?
        if potential_flags == 0:
            # No sensitive data to clean - this should only happen if there's actual code
            if code_lines > 0:
                cleaning_score = 100.0  # Clean code with no sensitive data
            else:
                cleaning_score = 0.0  # No code, no cleaning to evaluate
        else:
            # Handle repeated submissions
            if detected_flags > potential_flags:
                submission_ratio = detected_flags / potential_flags
                if submission_ratio > 2.0:
                    cleaning_score = 0.0  # Heavy repeated submissions
                else:
                    cleaning_score = max(0.0, 50.0 - (submission_ratio - 1.0) * 25.0)
            else:
                # Normal cleaning performance
                cleaning_rate = (potential_flags - detected_flags) / potential_flags
                cleaning_score = cleaning_rate * 100
        
        # Factor 3: Challenge Level (20% weight)
        # Higher potential flags = higher challenge = more points for success
        if potential_flags == 0:
            if code_lines > 0:
                challenge_score = 50.0  # Clean code is still a challenge
            else:
                challenge_score = 0.0  # No challenge if no code
        elif potential_flags < 5:
            challenge_score = 20.0  # Low challenge
        elif potential_flags < 15:
            challenge_score = 50.0  # Medium challenge
        elif potential_flags < 30:
            challenge_score = 80.0  # High challenge
        else:
            challenge_score = 100.0  # Very high challenge
        
        # Factor 4: Time Efficiency (10% weight)
        # Reasonable time spent = good, too fast or too slow = penalty
        if duration_minutes < 1:
            time_score = 20.0  # Too fast, might not have thought about it
        elif duration_minutes < 5:
            time_score = 80.0  # Good pace
        elif duration_minutes < 15:
            time_score = 100.0  # Optimal time
        elif duration_minutes < 30:
            time_score = 70.0  # A bit slow
        else:
            time_score = 40.0  # Too slow
        
        # Calculate weighted final score
        final_score = (
            complexity_score * 0.30 +    # 30% weight
            cleaning_score * 0.40 +      # 40% weight
            challenge_score * 0.20 +     # 20% weight
            time_score * 0.10            # 10% weight
        )
        
        # Apply minimum thresholds
        # Users with very little code or no challenge should not get high scores
        if code_lines < 5 and potential_flags < 3:
            final_score = min(final_score, 60.0)  # Cap at 60% for trivial sessions
        
        # Ensure score is between 0 and 100
        return max(0.0, min(100.0, final_score))
        
    def is_unedited_sample_code(self, logs: List[Dict]) -> bool:
        """Check if this session contains unedited sample code with improved detection"""
        if not logs:
            return False
        
        # Group logs by input to detect repeated submissions
        input_groups = {}
        for log in logs:
            input_preview = log.get('input_preview', '')
            if input_preview and len(input_preview) > 100:
                normalized_input = self._normalize_input_for_grouping(input_preview)
                if normalized_input not in input_groups:
                    input_groups[normalized_input] = []
                input_groups[normalized_input].append(log)
        
        # Check for repeated submissions of the same code
        has_repeated_submissions = any(len(group) > 1 for group in input_groups.values())
        
        # Check if there are many flags (typical of sample code)
        flag_count = sum(1 for log in logs if log.get('flag_type', 'UNKNOWN') != 'NO_FLAGS')
        has_many_flags = flag_count >= 10  # Sample code typically has 10+ flags
        
        # Check if contexts contain sample code patterns
        contexts = [log.get('context', '') for log in logs if log.get('context')]
        sample_code_indicators = 0
        
        if contexts:
            # Look for sample code indicators in contexts
            for context in contexts:
                context_lower = context.lower()
                # Check for common sample code patterns
                if any(indicator in context_lower for indicator in [
                    'sample code', 'api key', 'patient', 'medical', 'ssn', 
                    'password', 'secret', 'token', 'def ', 'class ', 'import '
                ]):
                    sample_code_indicators += 1
            
            # If most contexts contain sample code patterns, this is likely sample code
            has_sample_patterns = sample_code_indicators >= len(contexts) * 0.7  # 70% have patterns
        else:
            has_sample_patterns = False
        
        # This is unedited sample code if:
        # - Has many flags with sample code patterns
        # - User didn't clean anything (detected flags close to potential flags)
        potential_flags = self.count_potential_flags(logs)
        detected_flags = self.count_unique_detected_flags(logs)
        
        # If user cleaned significantly, don't consider it unedited
        if potential_flags > 0 and detected_flags < potential_flags * 0.7:
            return False
            
        return has_many_flags and has_sample_patterns
        
    def is_critical_line(self, line: str) -> bool:
        """Determine if a line contains critical/sensitive data patterns"""
        # Use the same patterns as the data monitor for consistency
        critical_patterns = [
            # API keys and tokens
            r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
            r'(?i)(access[_-]?token|token)\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
            r'(?i)(secret[_-]?key|secretkey)\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
            r'(?i)(bearer[_-]?token)\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
            # PII data
            r'(?i)(ssn|social[_-]?security)\s*[:=]\s*["\']?(\d{3}-?\d{2}-?\d{4})["\']?',
            r'(?i)(credit[_-]?card|cc)\s*[:=]\s*["\']?(\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})["\']?',
            r'(?i)(email)\s*[:=]\s*["\']?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})["\']?',
            r'(?i)(phone|telephone)\s*[:=]\s*["\']?(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})["\']?',
            # Medical data
            r'(?i)(patient[_-]?name|patient_name)\s*[:=]\s*["\']?([a-zA-Z\s]+)["\']?',
            r'(?i)(medical[_-]?record|medical_record)\s*[:=]\s*["\']?([a-zA-Z0-9\s]+)["\']?',
            r'(?i)(diagnosis|illness|disease)\s*[:=]\s*["\']?([a-zA-Z\s]+)["\']?',
            r'(?i)(health[_-]?insurance|insurance[_-]?id)\s*[:=]\s*["\']?([a-zA-Z0-9]+)["\']?',
            # Internal infrastructure
            r'(?i)(hostname|host|server|database|db)\s*[:=]\s*["\']?([a-zA-Z0-9.-]+)["\']?',
            r'(?i)(192\.168\.|10\.|172\.)',
            r'(?i)(localhost|internal|corp|company)',
            # General sensitive patterns
            r'["\'][a-zA-Z0-9]{20,}["\']',
            r'["\'][0-9]{3}-?[0-9]{2}-?[0-9]{4}["\']',
            r'["\'][0-9]{4}[-\\s]?[0-9]{4}[-\\s]?[0-9]{4}[-\\s]?[0-9]{4}["\']',
            r'["\'][a-zA-Z0-9.-]+\.(com|org|net|local|internal)["\']',
            r'["\'][a-zA-Z0-9.-]+\.amazonaws\.com["\']'
        ]
        
        line_lower = line.lower()
        for pattern in critical_patterns:
            if re.search(pattern, line_lower):
                return True
                
        return False
        
    def get_most_common_flag_type(self, logs: List[Dict]) -> str:
        """Get the most common security flag type in session (excluding NO_FLAGS)"""
        flag_counts = defaultdict(int)
        
        for log in logs:
            flag_type = log.get('flag_type', 'UNKNOWN')
            # Only count actual security flags, exclude NO_FLAGS
            if flag_type != 'NO_FLAGS':
                flag_counts[flag_type] += 1
            
        if not flag_counts:
            return "NO_FLAGS: 0"  # Only if no security flags found
            
        most_common = max(flag_counts.items(), key=lambda x: x[1])
        return f"{most_common[0]}: {most_common[1]}"  # Format: "PII: 9"
        
    def calculate_completion_rate(self, logs: List[Dict]) -> float:
        """Calculate completion rate"""
        if not logs:
            return 0.0
            
        return 100.0 if len(logs) > 5 else (len(logs) / 5) * 100
        
    def update_scoreboard(self):
        """Update the scoreboard display"""
        for item in self.scoreboard_tree.get_children():
            self.scoreboard_tree.delete(item)
            
        all_entries = []
        for user_sessions in self.user_stats.values():
            all_entries.extend(user_sessions)
            
        all_entries.sort(key=lambda x: (x.points, -x.session_duration), reverse=True)
        all_users = all_entries  # Show all users instead of limiting to 50
        
        self.update_summary_stats(all_entries)
        
        for rank, entry in enumerate(all_users, 1):
            if rank == 1:
                tag = 'gold'
            elif rank == 2:
                tag = 'silver'
            elif rank == 3:
                tag = 'bronze'
            elif rank <= 10:
                tag = 'top10'
            else:
                tag = 'normal'
                
            # Format duration with microseconds precision
            if entry.session_duration < 0.01:  # Less than 0.01 minutes (0.6 seconds)
                duration_str = f"{entry.session_duration*60:.3f}s"  # Show in seconds with milliseconds
            else:
                duration_str = f"{entry.session_duration:.4f}m"  # Show in minutes with 4 decimal places
                
            self.scoreboard_tree.insert('', 'end', values=(
                f"#{rank}",
                entry.user_id,
                entry.total_code_lines,
                entry.total_potential_flags,  # Sensitive Data (correct mapping)
                entry.detected_flags,  # Sensitive Fields (correct mapping)
                entry.risk_score,
                f"{entry.points:.3f}",  # Format points to 3 decimal places
                entry.most_common_flag,
                duration_str
            ), tags=(tag,))
            
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.last_update_label.config(text=f"Last Updated: {current_time}")
        
    def update_summary_stats(self, all_entries: List[UserScoreboardEntry]):
        """Update summary statistics"""
        if not all_entries:
            self.total_users_label.config(text="Total Users: 0")
            self.top_performer_label.config(text="Top Performer: None (0 pts)")
            self.top_flag_label.config(text="Top Flag: None (0)")
            return
            
        unique_users = len(set(entry.user_id for entry in all_entries))
        top_performer = max(all_entries, key=lambda x: x.points)
        
        # Calculate top flag across all sessions
        top_flag_info = self.calculate_top_flag_across_sessions()
        
        self.total_users_label.config(text=f"Total Users: {unique_users}")
        
        # Format top performer with points
        self.top_performer_label.config(text=f"Top Performer: {top_performer.user_id} ({top_performer.points} pts)")
        
        # Format top flag with count
        if top_flag_info:
            flag_name, count = top_flag_info
            self.top_flag_label.config(text=f"Top Flag: {flag_name} ({count})")
        else:
            self.top_flag_label.config(text="Top Flag: None (0)")
            
    def calculate_top_flag_across_sessions(self) -> tuple:
        """Calculate the most common flag type across all sessions"""
        flag_counts = defaultdict(int)
        
        for session_id, logs in self.session_data.items():
            # Check if this is a practice session (single log with analysis metrics)
            if len(logs) == 1 and isinstance(logs[0], dict) and 'final_analysis_metrics' in logs[0]:
                # Practice session - use final_analysis_metrics
                final_metrics = logs[0].get('final_analysis_metrics', {})
                flag_counts['PII'] += final_metrics.get('total_pii', 0)
                flag_counts['HEPA'] += final_metrics.get('total_hepa', 0)
                flag_counts['MEDICAL'] += final_metrics.get('total_medical', 0)
                flag_counts['COMPLIANCE/API'] += final_metrics.get('total_compliance_api', 0)
            else:
                # Regular analysis session - use individual flag logs
                for log in logs:
                    flag_type = log.get('flag_type', 'UNKNOWN')
                    if flag_type != 'NO_FLAGS' and flag_type != 'UNKNOWN':
                        flag_counts[flag_type] += 1
        
        # Remove flags with zero counts
        flag_counts = {k: v for k, v in flag_counts.items() if v > 0}
        
        if not flag_counts:
            return None
            
        most_common_flag = max(flag_counts.items(), key=lambda x: x[1])
        return most_common_flag
        
    def refresh_data(self):
        """Refresh data and update display"""
        self.load_data()
        
    def start_auto_refresh(self):
        """Start automatic refresh timer"""
        self.refresh_data()
        self.root.after(self.refresh_interval, self.start_auto_refresh)
        
    def run(self):
        """Start the scoreboard viewer"""
        self.root.mainloop()

def main():
    """Main function to run the scoreboard viewer"""
    try:
        scoreboard = ScoreboardViewer()
        scoreboard.run()
    except Exception as e:
        print(f"Error starting scoreboard: {e}")

if __name__ == "__main__":
    main()
