#!/usr/bin/env python3
"""
Detailed Log Viewer Parser for Sec360 by Abhay
Parses detailed session files and displays comprehensive analysis
"""

import json
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Dict, List, Any
import sys

class DetailedLogViewer:
    """Log viewer that reads from detailed sessions folder"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sec360 by Abhay - Detailed Log Viewer")
        self.root.geometry("1400x900")
        
        self.detailed_sessions_dir = Path("detailed_sessions")
        self.session_data = {}
        self.current_session = None
        
        self.setup_ui()
        self.load_sessions()
    
    def setup_ui(self):
        """Setup the user interface"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="Detailed Log Viewer", 
                               font=('Arial', 24, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Comprehensive Session Analysis", 
                                  font=('Arial', 16))
        subtitle_label.pack()
        
        # Session selection
        session_frame = ttk.LabelFrame(main_frame, text="Session Selection")
        session_frame.pack(fill=tk.X, pady=(0, 10))
        
        session_select_frame = ttk.Frame(session_frame)
        session_select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(session_select_frame, text="Select Session:").pack(side=tk.LEFT)
        
        self.session_var = tk.StringVar()
        self.session_combo = ttk.Combobox(session_select_frame, textvariable=self.session_var, 
                                         state="readonly", width=60)
        self.session_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.session_combo.bind('<<ComboboxSelected>>', self.on_session_selected)
        
        # Create main content area with side panel
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Left panel - Conversations
        left_panel = ttk.LabelFrame(content_frame, text="💬 Session Conversations")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Conversations treeview
        conv_columns = ('Timestamp', 'User', 'Message', 'Type')
        self.conversations_tree = ttk.Treeview(left_panel, columns=conv_columns, show='headings', height=20)
        
        self.conversations_tree.heading('Timestamp', text='Timestamp')
        self.conversations_tree.heading('User', text='User')
        self.conversations_tree.heading('Message', text='Message')
        self.conversations_tree.heading('Type', text='Type')
        
        self.conversations_tree.column('Timestamp', width=120)
        self.conversations_tree.column('User', width=80)
        self.conversations_tree.column('Message', width=250)
        self.conversations_tree.column('Type', width=80)
        
        conv_v_scrollbar = ttk.Scrollbar(left_panel, orient=tk.VERTICAL, command=self.conversations_tree.yview)
        conv_h_scrollbar = ttk.Scrollbar(left_panel, orient=tk.HORIZONTAL, command=self.conversations_tree.xview)
        self.conversations_tree.configure(yscrollcommand=conv_v_scrollbar.set, xscrollcommand=conv_h_scrollbar.set)
        
        self.conversations_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        conv_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        conv_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Right panel - Analysis details
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Session info frame
        info_frame = ttk.LabelFrame(right_panel, text="Session Information")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=6, wrap=tk.WORD)
        self.info_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Analysis results frame
        analysis_frame = ttk.LabelFrame(right_panel, text="📊 Current Analysis")
        analysis_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.analysis_text = tk.Text(analysis_frame, height=8, wrap=tk.WORD, 
                                   font=('Courier', 10))
        self.analysis_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Detailed breakdown frame with light label color
        breakdown_frame = ttk.LabelFrame(right_panel, text="🔍 Detailed Breakdown")
        breakdown_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure light text color for the breakdown frame label
        style = ttk.Style()
        style.configure("Light.TLabelframe.Label", foreground="#87CEEB")  # Light sky blue color
        breakdown_frame.configure(style="Light.TLabelframe")
        
        # Create treeview for detailed breakdown
        columns = ('Type', 'Name', 'Line', 'Category', 'Risk Score')
        self.breakdown_tree = ttk.Treeview(breakdown_frame, columns=columns, show='headings', height=8)
        
        # Configure dark font color for table text and light color for headers
        tree_style = ttk.Style()
        tree_style.configure("Treeview", foreground="#2c3e50", font=('Arial', 9))  # Dark blue-gray text
        tree_style.configure("Treeview.Heading", foreground="#87CEEB", font=('Arial', 9, 'bold'))  # Light sky blue for headers
        
        # Configure columns
        self.breakdown_tree.heading('Type', text='Type')
        self.breakdown_tree.heading('Name', text='Name')
        self.breakdown_tree.heading('Line', text='Line')
        self.breakdown_tree.heading('Category', text='Category')
        self.breakdown_tree.heading('Risk Score', text='Risk Score')
        
        self.breakdown_tree.column('Type', width=80)
        self.breakdown_tree.column('Name', width=120)
        self.breakdown_tree.column('Line', width=60)
        self.breakdown_tree.column('Category', width=120)
        self.breakdown_tree.column('Risk Score', width=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(breakdown_frame, orient=tk.VERTICAL, command=self.breakdown_tree.yview)
        h_scrollbar = ttk.Scrollbar(breakdown_frame, orient=tk.HORIZONTAL, command=self.breakdown_tree.xview)
        self.breakdown_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.breakdown_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configure tag colors
        self.breakdown_tree.tag_configure('sensitive_field', background='#fff3cd')
        self.breakdown_tree.tag_configure('sensitive_data', background='#f8d7da')
        self.breakdown_tree.tag_configure('pii', background='#d1ecf1')
        self.breakdown_tree.tag_configure('medical', background='#d4edda')
        self.breakdown_tree.tag_configure('api_security', background='#fce4ec')
        
        # Configure conversation tag colors (chat bubble styling)
        self.conversations_tree.tag_configure('user_message', background='#e3f2fd', foreground='#1565c0')
        self.conversations_tree.tag_configure('ai_message', background='#f3e5f5', foreground='#7b1fa2')
        self.conversations_tree.tag_configure('code_message', background='#fff3e0', foreground='#ef6c00')
        self.conversations_tree.tag_configure('system_message', background='#e8f5e8', foreground='#2e7d32')
    
    def load_sessions(self):
        """Load all detailed sessions"""
        self.session_data = {}
        sessions = []
        
        if not self.detailed_sessions_dir.exists():
            self.info_text.insert(tk.END, "No detailed sessions directory found.")
            return
        
        # Look for detailed session files
        for file_path in self.detailed_sessions_dir.glob("*_detailed.json"):
            session_id = file_path.stem.replace("_detailed", "")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    self.session_data[session_id] = session_data
                    
                    # Extract user info for display
                    user_name = session_data.get('user_name', 'Unknown')
                    session_start = session_data.get('session_start_time', 'Unknown')
                    display_name = f"{session_id} ({user_name} - {session_start})"
                    sessions.append((display_name, session_id))
                    
            except Exception as e:
                print(f"Error loading detailed session {session_id}: {e}")
        
        # Sort sessions by start time (newest first)
        sessions.sort(key=lambda x: self.session_data[x[1]].get('session_start_time', ''), reverse=True)
        
        # Populate combobox
        self.session_id_mapping = {display_name: session_id for display_name, session_id in sessions}
        self.session_combo['values'] = [display_name for display_name, _ in sessions]
        
        if sessions:
            # Select the most recent session by default
            self.session_var.set(sessions[0][0])
            self.on_session_selected()
        else:
            self.session_var.set("No detailed sessions found")
            self.session_combo['values'] = ["No detailed sessions found"]
            self.info_text.insert(tk.END, "No detailed sessions found in detailed_sessions directory.")
    
    def on_session_selected(self, event=None):
        """Handle session selection"""
        display_name = self.session_var.get()
        
        if display_name and hasattr(self, 'session_id_mapping'):
            session_id = self.session_id_mapping.get(display_name)
            
            if session_id and session_id in self.session_data:
                self.current_session = session_id
                self.display_session_info()
                self.display_analysis_results()
                self.display_detailed_breakdown()
                self.display_conversations()
    
    def display_session_info(self):
        """Display session information"""
        if not self.current_session:
            return
        
        session_data = self.session_data[self.current_session]
        
        info = f"Session ID: {session_data.get('session_id', 'Unknown')}\n"
        info += f"User: {session_data.get('user_name', 'Unknown')}\n"
        info += f"Start Time: {session_data.get('session_start_time', 'Unknown')}\n"
        info += f"End Time: {session_data.get('session_end_time', 'Unknown')}\n"
        info += f"Duration: {session_data.get('session_duration', 0):.1f} seconds\n"
        info += f"Code Length: {session_data.get('code_length', 0)} lines\n"
        info += f"Model Used: {session_data.get('model_used', 'Unknown')}\n"
        info += f"Analysis Timestamp: {session_data.get('analysis_timestamp', 'Unknown')}\n"
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info)
    
    def display_analysis_results(self):
        """Display current analysis results"""
        if not self.current_session:
            return
        
        session_data = self.session_data[self.current_session]
        current_analysis = session_data.get('current_analysis', {})
        
        analysis = f"📊 Current Analysis:\n"
        analysis += f"• Lines of Code: {current_analysis.get('lines_of_code', 0)}\n"
        analysis += f"• Sensitive Fields: {current_analysis.get('sensitive_fields', {}).get('count', 0)} [including All fields value]\n"
        analysis += f"• Sensitive Data: {current_analysis.get('sensitive_data', {}).get('count', 0)} [including All data value]\n"
        analysis += f"• PII Count: {current_analysis.get('pii', {}).get('count', 0)} [including All PII Name]\n"
        analysis += f"• Medical Data: {current_analysis.get('medical', {}).get('count', 0)} [including All Medical Name]\n"
        analysis += f"• API/Security: {current_analysis.get('api_security', {}).get('count', 0)} [including All API/Security Name]\n"
        analysis += f"• Risk Score: {current_analysis.get('risk_score', 0)}/100 ({current_analysis.get('risk_level', 'UNKNOWN')} RISK)\n"
        
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, analysis)
    
    def calculate_item_risk_score(self, item_type: str, category: str) -> float:
        """Calculate risk score for individual item"""
        try:
            # Base scores for different item types
            base_scores = {
                'sensitive_field': 0.1,
                'sensitive_data': 8.0
            }
            
            # Category multipliers
            category_multipliers = {
                'pii': 1.0,
                'medical': 1.2,
                'hepa': 1.1,
                'api_security': 0.9,
                'general': 1.0
            }
            
            # Get base score
            base_score = base_scores.get(item_type.lower(), 0.1)
            
            # Get category multiplier
            category_lower = category.lower() if category else 'general'
            multiplier = category_multipliers.get(category_lower, 1.0)
            
            # Calculate final score
            final_score = base_score * multiplier
            
            return round(final_score, 1)
            
        except Exception as e:
            print(f"Error calculating item risk score: {e}")
            return 0.1
    
    def display_detailed_breakdown(self):
        """Display detailed breakdown in treeview"""
        # Clear existing items
        for item in self.breakdown_tree.get_children():
            self.breakdown_tree.delete(item)
        
        if not self.current_session:
            return
        
        session_data = self.session_data[self.current_session]
        current_analysis = session_data.get('current_analysis', {})
        
        # Add sensitive fields
        sensitive_fields = current_analysis.get('sensitive_fields', {}).get('items', [])
        for field in sensitive_fields:
            risk_score = self.calculate_item_risk_score('sensitive_field', field.get('category', 'General'))
            self.breakdown_tree.insert('', tk.END, values=(
                'Sensitive Field',
                field['name'],
                field['line'],
                field['category'],
                f"{risk_score}"
            ), tags=['sensitive_field'])
        
        # Add sensitive data
        sensitive_data = current_analysis.get('sensitive_data', {}).get('items', [])
        for data in sensitive_data:
            risk_score = self.calculate_item_risk_score('sensitive_data', data.get('category', 'General'))
            self.breakdown_tree.insert('', tk.END, values=(
                'Sensitive Data',
                data['name'],
                data['line'],
                data['category'],
                f"{risk_score}"
            ), tags=['sensitive_data'])
        
        # Add PII items
        pii_items = current_analysis.get('pii', {}).get('items', [])
        for pii in pii_items:
            risk_score = self.calculate_item_risk_score('sensitive_data', 'PII')
            self.breakdown_tree.insert('', tk.END, values=(
                'PII',
                pii['name'],
                pii['line'],
                pii['category'],
                f"{risk_score}"
            ), tags=['pii'])
        
        # Add Medical items
        medical_items = current_analysis.get('medical', {}).get('items', [])
        for medical in medical_items:
            risk_score = self.calculate_item_risk_score('sensitive_data', 'Medical')
            self.breakdown_tree.insert('', tk.END, values=(
                'Medical',
                medical['name'],
                medical['line'],
                medical['category'],
                f"{risk_score}"
            ), tags=['medical'])
        
        # Add API/Security items
        api_items = current_analysis.get('api_security', {}).get('items', [])
        for api in api_items:
            risk_score = self.calculate_item_risk_score('sensitive_data', 'API/Security')
            self.breakdown_tree.insert('', tk.END, values=(
                'API/Security',
                api['name'],
                api['line'],
                api['category'],
                f"{risk_score}"
            ), tags=['api_security'])
    
    def display_conversations(self):
        """Display session conversations in chat bubble + timeline format"""
        # Clear existing items
        for item in self.conversations_tree.get_children():
            self.conversations_tree.delete(item)
        
        if not self.current_session:
            return
        
        session_data = self.session_data[self.current_session]
        
        # Get conversation data from session
        conversations = session_data.get('conversations', [])
        
        if not conversations:
            # Fallback to sample data if no conversations found
            conversations = [
                {
                    'timestamp': session_data.get('session_start_time', 'Unknown'),
                    'user': session_data.get('user_name', 'Unknown'),
                    'message': 'Started practice session',
                    'message_type': 'session_start'
                },
                {
                    'timestamp': session_data.get('analysis_timestamp', 'Unknown'),
                    'user': session_data.get('user_name', 'Unknown'),
                    'message': f"Submitted code for analysis",
                    'message_type': 'code_submission'
                },
                {
                    'timestamp': session_data.get('analysis_timestamp', 'Unknown'),
                    'user': 'AI Security Mentor',
                    'message': f"Analyzed {session_data.get('code_length', 0)} lines of code",
                    'message_type': 'analysis_response'
                },
                {
                    'timestamp': session_data.get('session_end_time', 'Unknown'),
                    'user': session_data.get('user_name', 'Unknown'),
                    'message': 'Completed session analysis',
                    'message_type': 'session_end'
                }
            ]
        
        # Display conversations with chat bubble styling
        for conv in conversations:
            timestamp = conv.get('timestamp', 'Unknown')
            user = conv.get('user', 'Unknown')
            message = conv.get('message', '')
            message_type = conv.get('message_type', 'text')
            
            # Format message for display
            display_message = message
            if len(message) > 100:
                display_message = message[:100] + "..."
            
            # Determine tag based on message type and user
            if user == "AI Security Mentor":
                tag = "ai_message"
            elif message_type == "code_submission":
                tag = "code_message"
            elif message_type == "session_start" or message_type == "session_end":
                tag = "system_message"
            else:
                tag = "user_message"
            
            self.conversations_tree.insert('', tk.END, values=(
                timestamp,
                user,
                display_message,
                message_type
            ), tags=(tag,))
    
    def run(self):
        """Start the detailed log viewer"""
        self.root.mainloop()

def main():
    """Main function to run the detailed log viewer"""
    viewer = DetailedLogViewer()
    viewer.run()

if __name__ == "__main__":
    main()
