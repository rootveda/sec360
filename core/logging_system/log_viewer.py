#!/usr/bin/env python3
"""
Log Viewer for Sec360 by Abhay
Provides an isolated interface to view and analyze user session logs
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
from typing import List, Dict, Optional
import webbrowser
from pathlib import Path

class LogViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sec360 by Abhay - Log Viewer")
        self.root.geometry("1200x800")
        
        self.session_data = {}
        self.current_session = None
        self._initializing = True  # Flag to prevent trace callbacks during setup
        
        self.setup_ui()
        self.clear_session_display()  # Initialize with empty display
        self.load_sessions()
        self._initializing = False  # Enable trace callbacks after setup
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame for session selection
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Session selection
        ttk.Label(top_frame, text="Select Session:").pack(side=tk.LEFT)
        self.session_var = tk.StringVar()
        self.session_combo = ttk.Combobox(top_frame, textvariable=self.session_var, width=30)
        self.session_combo.pack(side=tk.LEFT, padx=(5, 10))
        self.session_combo.bind('<<ComboboxSelected>>', self.on_session_selected)
        self.session_combo.bind('<Return>', self.on_session_selected)  # Enter key
        # self.session_var.trace('w', self._on_session_var_changed)  # Text change - disabled
        
        # Refresh button
        ttk.Button(top_frame, text="Refresh", command=self.load_sessions).pack(side=tk.LEFT)
        
        # Export button
        ttk.Button(top_frame, text="Export Session", command=self.export_session).pack(side=tk.LEFT, padx=(5, 0))
        
        # Session info frame
        info_frame = ttk.LabelFrame(main_frame, text="Session Information")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=6, wrap=tk.WORD)
        self.info_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Logs frame
        logs_frame = ttk.LabelFrame(main_frame, text="Flagged Content")
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for logs
        columns = ('Timestamp', 'Flag Type', 'Content', 'Confidence', 'Context')
        self.log_tree = ttk.Treeview(logs_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.log_tree.heading('Timestamp', text='Timestamp')
        self.log_tree.heading('Flag Type', text='Flag Type')
        self.log_tree.heading('Content', text='Content')
        self.log_tree.heading('Confidence', text='Confidence')
        self.log_tree.heading('Context', text='Context')
        
        self.log_tree.column('Timestamp', width=150)
        self.log_tree.column('Flag Type', width=100)
        self.log_tree.column('Content', width=200)
        self.log_tree.column('Confidence', width=80)
        self.log_tree.column('Context', width=400)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(logs_frame, orient=tk.VERTICAL, command=self.log_tree.yview)
        h_scrollbar = ttk.Scrollbar(logs_frame, orient=tk.HORIZONTAL, command=self.log_tree.xview)
        self.log_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click event
        self.log_tree.bind('<Double-1>', self.on_log_double_click)
        
        # Bottom frame for statistics
        stats_frame = ttk.LabelFrame(main_frame, text="Session Statistics")
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_text = tk.Text(stats_frame, height=8, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.X, padx=5, pady=5)
    
    def load_sessions(self):
        """Load all available sessions"""
        self.session_data = {}
        sessions = []
        
        # Look for session files in sessions directory
        sessions_dir = Path("core/logs/sessions")
        if sessions_dir.exists():
            # Look for practice session files
            for file_path in sessions_dir.glob("practice_*.json"):
                session_id = file_path.stem
                
                try:
                    with open(file_path, 'r') as f:
                        session_data = json.load(f)
                        # Store the entire session data
                        self.session_data[session_id] = session_data
                        
                        # Extract user info for display
                        user_name = session_data.get('user_name', 'Unknown')
                        session_start = session_data.get('session_start_time', 'Unknown')
                        display_name = f"{session_id} ({user_name} - {session_start})"
                        sessions.append((display_name, session_id))
                        
                except Exception as e:
                    print(f"Error loading session {session_id}: {e}")
            
            # Look for legacy session_*.json files (if they exist)
            for file_path in sessions_dir.glob("session_*.json"):
                session_id = file_path.stem.replace("session_", "")
                
                try:
                    with open(file_path, 'r') as f:
                        session_data = json.load(f)
                        self.session_data[session_id] = session_data
                        
                        user_name = session_data.get('user_name', 'Unknown')
                        session_start = session_data.get('session_start_time', 'Unknown')
                        display_name = f"{session_id} ({user_name} - {session_start})"
                        sessions.append((display_name, session_id))
                        
                except Exception as e:
                    print(f"Error loading legacy session {session_id}: {e}")
        
        # Sort sessions by timestamp (newest first) - extract timestamp from filename
        sessions.sort(key=lambda x: x[1].split('_')[-1] if '_' in x[1] else x[1], reverse=True)
        
        # Update combobox with display names
        session_display_names = [session[0] for session in sessions]
        self.session_combo['values'] = session_display_names
        
        # Always leave dropdown empty initially, regardless of session count
        self.session_combo.set("")
        self.current_session = None
        
        if sessions:
            # Store mapping for on_session_selected
            self.session_id_mapping = {display: session_id for display, session_id in sessions}
        else:
            # No sessions found
            self.session_id_mapping = {}
            if hasattr(self, 'info_text'):
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, "No sessions found in core/logs/sessions directory.")
        
        # Clear session display
        self.clear_session_display()
    
    def on_session_selected(self, event=None):
        """Handle session selection"""
        display_name = self.session_var.get()
        
        if display_name and hasattr(self, 'session_id_mapping'):
            session_id = self.session_id_mapping.get(display_name)
            
            if session_id and session_id in self.session_data:
                self.current_session = session_id
                self.display_session_info()
                self.display_session_logs()
                self.display_session_stats()
    
    def select_session_by_value(self, display_name):
        """Manually select a session by setting both variable and combobox"""
        self.session_var.set(display_name)
        self.session_combo.set(display_name)  # Force combobox display update
        self.on_session_selected()
    
    def _on_session_var_changed(self, *args):
        """Wrapper for session variable change trace that respects initialization flag"""
        # Trace callback disabled to prevent conflicts
        pass
    
    def display_session_info(self):
        """Display session information"""
        if not self.current_session:
            return
        
        session_data = self.session_data[self.current_session]
        if not session_data:
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "No data found for this session.")
            return
        
        # Extract session info from the structured data
        info = f"Session ID: {session_data.get('unique_session_id', self.current_session)}\n"
        info += f"User: {session_data.get('user_name', 'Unknown')}\n"
        info += f"Start Time: {session_data.get('session_start_time', 'Unknown')}\n"
        info += f"End Time: {session_data.get('session_end_time', 'Unknown')}\n"
        info += f"Duration: {session_data.get('session_duration', 0):.1f} seconds\n"
        info += f"Message Count: {session_data.get('message_count', 0)}\n"
        info += f"Token Count: {session_data.get('token_count', 0)}\n"
        
        # Add final analysis metrics if available
        if 'final_analysis_metrics' in session_data:
            metrics = session_data['final_analysis_metrics']
            info += f"\nAnalysis Results:\n"
            info += f"Lines Analyzed: {metrics.get('total_lines', 0)}\n"
            info += f"Sensitive Fields: {metrics.get('total_sensitive_fields', 0)}\n"
            info += f"Sensitive Data: {metrics.get('total_sensitive_data', 0)}\n"
            info += f"Risk Score: {metrics.get('average_risk_score', 0):.1f}/100\n"
            info += f"Risk Level: {metrics.get('risk_level', 'Unknown')}\n"
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info)
    
    def display_session_logs(self):
        """Display session logs in treeview"""
        # Clear existing items
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
        
        if not self.current_session:
            return
        
        session_data = self.session_data[self.current_session]
        
        if 'code_analyses' in session_data and session_data['code_analyses']:
            # Show individual code analyses from practice sessions
            row_num = 1
            for analysis in session_data['code_analyses']:
                timestamp = analysis.get('timestamp', session_data.get('session_start_time', 'Unknown'))
                analysis_result = analysis.get('analysis_result', {})
                
                # Create summary row for this analysis
                self.log_tree.insert('', tk.END, values=(
                    timestamp,
                    "CODE_ANALYSIS",
                    f"Lines: {analysis_result.get('lines_of_code', 'N/A')}, Risk: {analysis_result.get('risk_score', 'N/A')}/100",
                    f"{analysis_result.get('confidence', 1.0):.2f}",
                    f"Analysis #{row_num}"
                ), tags=["analysis"])
                
                row_num += 1
        else:
            # For legacy format or if no analyses, show basic session info
            self.log_tree.insert('', tk.END, values=(
                session_data.get('session_start_time', 'Unknown'),
                "SESSION_SUMMARY",
                f"Duration: {session_data.get('session_duration', 0):.1f}s, Messages: {session_data.get('message_count', 0)}",
                "1.00",
                "Session Overview"
            ), tags=["session"])
            
            # Show final metrics if available
            if 'final_analysis_metrics' in session_data:
                metrics = session_data['final_analysis_metrics']
                self.log_tree.insert('', tk.END, values=(
                    session_data.get('session_end_time', 'Unknown'),
                    "FINAL_METRICS",
                    f"Lines: {metrics.get('total_lines', 0)}, Risk: {metrics.get('average_risk_score', 0):.1f}/100",
                    "1.00",
                    "Final Results"
                ), tags=["metrics"])
        
        # Configure tag colors for new types
        self.log_tree.tag_configure("analysis", background="#e6f3ff", foreground="#003366")    # Light blue for analyses
        self.log_tree.tag_configure("session", background="#f0f8ff", foreground="#4169e1")    # Light blue for session info
        self.log_tree.tag_configure("metrics", background="#fff8dc", foreground="#b8860b")   # Light yellow for metrics
    
    def display_session_stats(self):
        """Display session statistics"""
        if not self.current_session:
            return
        
        session_data = self.session_data[self.current_session]
        
        # Build statistics from session data
        stats_text = ""
        
        # Basic session stats
        stats_text += f"📊 Session Statistics:\n"
        stats_text += f"Duration: {session_data.get('session_duration', 0):.1f} seconds\n"
        stats_text += f"Messages: {session_data.get('message_count', 0)}\n"
        stats_text += f"Tokens: {session_data.get('token_count', 0)}\n\n"
        
        # Analysis statistics
        if 'final_analysis_metrics' in session_data:
            metrics = session_data['final_analysis_metrics']
            stats_text += f"🔍 Analysis Metrics:\n"
            stats_text += f"Total Analyses: {metrics.get('total_analyses', 0)}\n"
            stats_text += f"Lines Analyzed: {metrics.get('total_lines', 0)}\n"
            stats_text += f"Sensitive Fields: {metrics.get('total_sensitive_fields', 0)}\n"
            stats_text += f"Sensitive Data: {metrics.get('total_sensitive_data', 0)}\n"
            stats_text += f"PII Count: {metrics.get('total_pii', 0)}\n"
            stats_text += f"Medical Count: {metrics.get('total_medical', 0)}\n"
            stats_text += f"API/Security Count: {metrics.get('total_compliance_api', 0)}\n"
            stats_text += f"Average Risk Score: {metrics.get('average_risk_score', 0):.1f}/100\n"
            stats_text += f"Risk Level: {metrics.get('risk_level', 'Unknown')}\n\n"
            
            # Calculate score based on risk
            risk_score = metrics.get('average_risk_score', 0)
            if risk_score >= 80:
                score = 20
                score_desc = "Critical Risk"
            elif risk_score >= 60:
                score = 40
                score_desc = "High Risk"
            elif risk_score >= 40:
                score = 60
                score_desc = "Medium Risk"
            elif risk_score >= 20:
                score = 80
                score_desc = "Low Risk"
            else:
                score = 100
                score_desc = "Minimal Risk"
            
            stats_text += f"🎯 Security Score: {score}/100 ({score_desc})\n"
        else:
            stats_text += "No analysis metrics available\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_text)
    
    def clear_session_display(self):
        """Clear all session display areas when no session is selected"""
        # Clear info text
        if hasattr(self, 'info_text'):
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "Please select a session from the dropdown above.")
        
        # Clear log tree
        if hasattr(self, 'log_tree'):
            for item in self.log_tree.get_children():
                self.log_tree.delete(item)
        
        # Clear stats text
        if hasattr(self, 'stats_text'):
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "No session selected. Select a session to view statistics.")
    
    def on_log_double_click(self, event):
        """Handle double-click on log entry"""
        selection = self.log_tree.selection()
        if selection:
            item = self.log_tree.item(selection[0])
            values = item['values']
            
            # Create detailed view window
            detail_window = tk.Toplevel(self.root)
            detail_window.title("Log Detail")
            detail_window.geometry("600x400")
            
            detail_text = tk.Text(detail_window, wrap=tk.WORD)
            detail_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            detail_info = f"Timestamp: {values[0]}\n"
            detail_info += f"Flag Type: {values[1]}\n"
            detail_info += f"Content: {values[2]}\n"
            detail_info += f"Confidence: {values[3]}\n"
            detail_info += f"Context: {values[4]}\n"
            
            detail_text.insert(tk.END, detail_info)
            detail_text.config(state=tk.DISABLED)
    
    def export_session(self):
        """Export current session to file"""
        if not self.current_session:
            messagebox.showwarning("Warning", "No session selected")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialname=f"session_{self.current_session}.json"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.session_data[self.current_session], f, indent=2)
                messagebox.showinfo("Success", f"Session exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export session: {e}")
    
    def run(self):
        """Start the log viewer"""
        self.root.mainloop()

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("core/logs", exist_ok=True)
    
    # Start the log viewer
    viewer = LogViewer()
    viewer.run()
