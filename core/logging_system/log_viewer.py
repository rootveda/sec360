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
        columns = ('Timestamp', 'Flag Type', 'Content', 'Risk Score', 'Context')
        self.log_tree = ttk.Treeview(logs_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.log_tree.heading('Timestamp', text='Timestamp')
        self.log_tree.heading('Flag Type', text='Flag Type')
        self.log_tree.heading('Content', text='Content')
        self.log_tree.heading('Risk Score', text='Risk Score')
        self.log_tree.heading('Context', text='Context')
        
        self.log_tree.column('Timestamp', width=150)
        self.log_tree.column('Flag Type', width=100)
        self.log_tree.column('Content', width=200)
        self.log_tree.column('Risk Score', width=80)
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
        
        # Risk calculation section (moved up)
        calc_frame = ttk.LabelFrame(main_frame, text="📊 Risk Score Calculation")
        calc_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Risk calculation display
        self.calc_text = tk.Text(calc_frame, height=20, wrap=tk.WORD, font=('TkDefaultFont', 12, 'bold'),
                                bg="#f8f9fa", fg="#000000", relief=tk.SUNKEN, bd=1)
        self.calc_text.pack(fill=tk.X, pady=(2, 0))
        
        # Configure text tags for color coding
        self.calc_text.tag_configure("header", foreground="#2c3e50", font=('TkDefaultFont', 12, 'bold'))
        self.calc_text.tag_configure("category", foreground="#8e44ad", font=('TkDefaultFont', 11, 'bold'))
        self.calc_text.tag_configure("calculation", foreground="#27ae60", font=('TkDefaultFont', 11))
        self.calc_text.tag_configure("score", foreground="#e74c3c", font=('TkDefaultFont', 11, 'bold'))
        self.calc_text.tag_configure("items", foreground="#3498db", font=('TkDefaultFont', 10))
        self.calc_text.tag_configure("summary", foreground="#f39c12", font=('TkDefaultFont', 11, 'bold'))
        
        # Initial message
        self.calc_text.insert(tk.END, "Select a session to see detailed risk score calculation...")
        self.calc_text.config(state=tk.DISABLED)
        
        # Footer frame for color legend
        footer_frame = ttk.LabelFrame(main_frame, text="Risk Categories & Levels Legend")
        footer_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Create legend content
        legend_frame = ttk.Frame(footer_frame)
        legend_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Risk Categories section
        categories_frame = ttk.Frame(legend_frame)
        categories_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(categories_frame, text="Risk Categories:", font=('TkDefaultFont', 9, 'bold')).pack(anchor=tk.W)
        
        categories_content = ttk.Frame(categories_frame)
        categories_content.pack(fill=tk.X, pady=(2, 0))
        
        # PII category
        pii_frame = ttk.Frame(categories_content)
        pii_frame.pack(side=tk.LEFT, padx=(0, 15))
        pii_label = tk.Label(pii_frame, text="🔴 PII", bg="#ffe6e6", fg="#cc0000", font=('TkDefaultFont', 8))
        pii_label.pack(side=tk.LEFT)
        ttk.Label(pii_frame, text="Personal Information", font=('TkDefaultFont', 8)).pack(side=tk.LEFT, padx=(2, 0))
        
        # Medical category
        medical_frame = ttk.Frame(categories_content)
        medical_frame.pack(side=tk.LEFT, padx=(0, 15))
        medical_label = tk.Label(medical_frame, text="🟢 Medical", bg="#e6ffe6", fg="#006600", font=('TkDefaultFont', 8))
        medical_label.pack(side=tk.LEFT)
        ttk.Label(medical_frame, text="HIPAA Data", font=('TkDefaultFont', 8)).pack(side=tk.LEFT, padx=(2, 0))
        
        # HEPA category
        hepa_frame = ttk.Frame(categories_content)
        hepa_frame.pack(side=tk.LEFT, padx=(0, 15))
        hepa_label = tk.Label(hepa_frame, text="🔵 HEPA", bg="#e6f3ff", fg="#003366", font=('TkDefaultFont', 8))
        hepa_label.pack(side=tk.LEFT)
        ttk.Label(hepa_frame, text="Healthcare Data", font=('TkDefaultFont', 8)).pack(side=tk.LEFT, padx=(2, 0))
        
        # API/Security category
        api_frame = ttk.Frame(categories_content)
        api_frame.pack(side=tk.LEFT, padx=(0, 15))
        api_label = tk.Label(api_frame, text="🟠 API/Security", bg="#fff0e6", fg="#cc6600", font=('TkDefaultFont', 8))
        api_label.pack(side=tk.LEFT)
        ttk.Label(api_frame, text="Credentials & Keys", font=('TkDefaultFont', 8)).pack(side=tk.LEFT, padx=(2, 0))
        
        # Risk Levels section
        levels_frame = ttk.Frame(legend_frame)
        levels_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        ttk.Label(levels_frame, text="Risk Levels:", font=('TkDefaultFont', 9, 'bold')).pack(anchor=tk.E)
        
        levels_content = ttk.Frame(levels_frame)
        levels_content.pack(fill=tk.X, pady=(2, 0))
        
        # Low risk
        low_frame = ttk.Frame(levels_content)
        low_frame.pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Label(low_frame, text="Low (0-29)", font=('TkDefaultFont', 8)).pack(side=tk.RIGHT)
        low_label = tk.Label(low_frame, text="🟢", bg="#e6ffe6", fg="#006600", font=('TkDefaultFont', 8))
        low_label.pack(side=tk.RIGHT, padx=(2, 0))
        
        # Medium risk
        medium_frame = ttk.Frame(levels_content)
        medium_frame.pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Label(medium_frame, text="Medium (30-59)", font=('TkDefaultFont', 8)).pack(side=tk.RIGHT)
        medium_label = tk.Label(medium_frame, text="🟡", bg="#fff8dc", fg="#b8860b", font=('TkDefaultFont', 8))
        medium_label.pack(side=tk.RIGHT, padx=(2, 0))
        
        # High risk
        high_frame = ttk.Frame(levels_content)
        high_frame.pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Label(high_frame, text="High (60-79)", font=('TkDefaultFont', 8)).pack(side=tk.RIGHT)
        high_label = tk.Label(high_frame, text="🔴", bg="#ffe6e6", fg="#cc0000", font=('TkDefaultFont', 8))
        high_label.pack(side=tk.RIGHT, padx=(2, 0))
        
        # Critical risk
        critical_frame = ttk.Frame(levels_content)
        critical_frame.pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Label(critical_frame, text="Critical (80-100)", font=('TkDefaultFont', 8)).pack(side=tk.RIGHT)
        critical_label = tk.Label(critical_frame, text="🚨", bg="#ffcccc", fg="#990000", font=('TkDefaultFont', 8))
        critical_label.pack(side=tk.RIGHT, padx=(2, 0))
        
        # Session Statistics section (moved to footer)
        stats_frame = ttk.LabelFrame(main_frame, text="Session Statistics")
        stats_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.stats_text = tk.Text(stats_frame, height=6, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.X, padx=5, pady=5)
    
    def load_sessions(self):
        """Load all available sessions"""
        self.session_data = {}
        sessions = []
        
        # Look for session files in sessions directory
        # Get project root directory (go up from core/logging_system/)
        project_root = Path(__file__).parent.parent.parent
        sessions_dir = project_root / "core" / "logs" / "sessions"
        if sessions_dir.exists():
            # Look for practice session files that have corresponding details files
            for file_path in sessions_dir.glob("practice_*.json"):
                session_id = file_path.stem
                
                # Skip details files
                if session_id.endswith("_details"):
                    continue
                
                # Only include sessions that have detailed analysis data
                details_file = sessions_dir / f"{session_id}_details.json"
                if not details_file.exists():
                    continue
                
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
                self.info_text.insert(tk.END, f"No sessions found in {sessions_dir} directory.")
        
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
                self.update_risk_calculation()
    
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
            
            # Add detailed risk breakdown if available
            risk_breakdown = self._get_detailed_risk_breakdown(session_data.get('unique_session_id', self.current_session))
            if risk_breakdown:
                info += f"\n🔍 Detailed Risk Breakdown:\n"
                info += risk_breakdown
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info)
    
    def _get_detailed_risk_breakdown(self, session_id: str) -> str:
        """Get detailed risk breakdown from analysis details file"""
        try:
            # Get project root directory
            project_root = Path(__file__).parent.parent.parent
            details_file = project_root / "core" / "logs" / "sessions" / f"{session_id}_details.json"
            
            if not details_file.exists():
                return ""  # No detailed data available
            
            with open(details_file, 'r', encoding='utf-8') as f:
                details_data = json.load(f)
            
            analyses = details_data.get('analyses', [])
            if not analyses:
                return ""
            
            # Aggregate data from all analyses
            breakdown = ""
            total_risk_score = 0
            analysis_count = 0
            
            # Category totals
            category_totals = {
                'pii': {'fields': 0, 'data': 0, 'items': []},
                'medical': {'fields': 0, 'data': 0, 'items': []},
                'hepa': {'fields': 0, 'data': 0, 'items': []},
                'compliance_api': {'fields': 0, 'data': 0, 'items': []}
            }
            
            for analysis in analyses:
                analysis_details = analysis.get('analysis_details', {})
                flagged_items = analysis_details.get('flagged_items', [])
                
                total_risk_score += analysis.get('risk_score', 0)
                analysis_count += 1
                
                # Process flagged items
                for item in flagged_items:
                    item_type = item.get('type', '')
                    item_name = item.get('name', '')
                    item_category = item.get('category', '').lower()
                    
                    if item_category in category_totals:
                        if item_type == 'sensitive_field':
                            category_totals[item_category]['fields'] += 1
                        elif item_type == 'sensitive_data':
                            category_totals[item_category]['data'] += 1
                        
                        category_totals[item_category]['items'].append({
                            'type': item_type,
                            'name': item_name,
                            'line': item.get('line', 0)
                        })
            
            if analysis_count == 0:
                return ""
            
            avg_risk_score = total_risk_score / analysis_count
            
            # Build breakdown text
            breakdown += f"Average Risk Score: {avg_risk_score:.1f}/100\n\n"
            
            # Category breakdown
            breakdown += "📊 Category Contributions:\n"
            
            category_names = {
                'pii': 'PII Data',
                'medical': 'Medical Data', 
                'hepa': 'HEPA Data',
                'compliance_api': 'API/Security Data'
            }
            
            category_multipliers = {
                'pii': 1.0,
                'medical': 1.2,
                'hepa': 1.1,
                'compliance_api': 0.9
            }
            
            for category, data in category_totals.items():
                if data['fields'] > 0 or data['data'] > 0:
                    total_items = data['fields'] + data['data']
                    multiplier = category_multipliers.get(category, 1.0)
                    base_score = total_items * 5 * multiplier
                    
                    breakdown += f"• {category_names.get(category, category.title())} ({data['fields']} fields + {data['data']} instances): {base_score:.1f} points\n"
                    
                    # Show individual items
                    if data['items']:
                        breakdown += f"  - Fields: "
                        fields = [item['name'] for item in data['items'] if item['type'] == 'sensitive_field']
                        if fields:
                            breakdown += f"{', '.join(fields[:3])}"  # Show first 3
                            if len(fields) > 3:
                                breakdown += f" (+{len(fields)-3} more)"
                        breakdown += "\n"
                        
                        breakdown += f"  - Data: "
                        data_items = [item['name'] for item in data['items'] if item['type'] == 'sensitive_data']
                        if data_items:
                            # Truncate long data values
                            display_data = []
                            for item in data_items[:2]:  # Show first 2
                                if len(item) > 20:
                                    display_data.append(item[:17] + "...")
                                else:
                                    display_data.append(item)
                            breakdown += f"{', '.join(display_data)}"
                            if len(data_items) > 2:
                                breakdown += f" (+{len(data_items)-2} more)"
                        breakdown += "\n"
            
            breakdown += f"\n📈 Risk Calculation:\n"
            breakdown += f"• Base score: Fields × 0.1 + Data × 8\n"
            breakdown += f"• Category multipliers applied (Medical: 1.2x, HEPA: 1.1x, PII: 1.0x, API: 0.9x)\n"
            breakdown += f"• Line count normalization applied\n"
            breakdown += f"• Final score capped at 100\n"
            
            return breakdown
            
        except Exception as e:
            print(f"Error loading detailed risk breakdown: {e}")
            return ""
    
    def display_session_logs(self):
        """Display session logs in treeview"""
        # Clear existing items
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
        
        if not self.current_session:
            return
        
        session_data = self.session_data[self.current_session]
        
        # Try to load detailed flagged items first
        detailed_items = self._load_detailed_flagged_items(session_data.get('unique_session_id', self.current_session))
        
        if detailed_items:
            # Display individual flagged items
            for item in detailed_items:
                timestamp = item.get('timestamp', 'Unknown')
                item_type = item.get('type', 'Unknown')
                item_name = item.get('name', 'Unknown')
                category = item.get('category', 'Unknown')
                line = item.get('line', 0)
                
                # Calculate risk score for this item
                risk_score = self._calculate_item_risk_score(item)
                
                # Format display
                if item_type == 'sensitive_field':
                    content = f"Field: {item_name}"
                    flag_type = f"{category}_FIELD"
                elif item_type == 'sensitive_data':
                    # Truncate long data values
                    display_name = item_name[:30] + "..." if len(item_name) > 30 else item_name
                    content = f"Data: {display_name}"
                    flag_type = f"{category}_DATA"
                else:
                    content = f"{item_type}: {item_name}"
                    flag_type = category
                
                context = f"Line {line}" if line > 0 else "Unknown line"
                
                self.log_tree.insert('', tk.END, values=(
                    timestamp,
                    flag_type,
                    content,
                    f"{risk_score:.1f}",
                    context
                ), tags=[category.lower()])
                
                # Configure tag colors for new types
                self.log_tree.tag_configure("analysis", background="#e6f3ff", foreground="#003366")    # Light blue for analyses
                self.log_tree.tag_configure("session", background="#f0f8ff", foreground="#4169e1")    # Light blue for session info
                self.log_tree.tag_configure("metrics", background="#fff8dc", foreground="#b8860b")   # Light yellow for metrics
                self.log_tree.tag_configure("pii", background="#ffe6e6", foreground="#cc0000")       # Light red for PII
                self.log_tree.tag_configure("medical", background="#e6ffe6", foreground="#006600")   # Light green for medical
                self.log_tree.tag_configure("hepa", background="#e6f3ff", foreground="#003366")      # Light blue for HEPA
                self.log_tree.tag_configure("compliance_api", background="#fff0e6", foreground="#cc6600")  # Light orange for API
                
                # Refresh the tree to ensure items are visible
                self.log_tree.update()
    
    def _load_detailed_flagged_items(self, session_id: str) -> List[Dict]:
        """Load detailed flagged items from analysis details file"""
        try:
            # Get project root directory
            project_root = Path(__file__).parent.parent.parent
            details_file = project_root / "core" / "logs" / "sessions" / f"{session_id}_details.json"
            
            if not details_file.exists():
                return []
            
            with open(details_file, 'r', encoding='utf-8') as f:
                details_data = json.load(f)
            
            analyses = details_data.get('analyses', [])
            flagged_items = []
            
            for analysis in analyses:
                analysis_details = analysis.get('analysis_details', {})
                items = analysis_details.get('flagged_items', [])
                
                for item in items:
                    # Add timestamp and analysis context to each item
                    flagged_item = item.copy()
                    flagged_item['timestamp'] = analysis.get('timestamp', 0)
                    flagged_item['analysis_risk_score'] = analysis.get('risk_score', 0)
                    flagged_items.append(flagged_item)
            
            return flagged_items
            
        except Exception as e:
            print(f"Error loading detailed flagged items: {e}")
            return []
    
    def _calculate_item_risk_score(self, item: Dict) -> float:
        """Calculate risk score for individual flagged item"""
        try:
            item_type = item.get('type', '')
            category = item.get('category', '').lower()
            
            # Base score by type
            if item_type == 'sensitive_field':
                base_score = 5.0
            elif item_type == 'sensitive_data':
                base_score = 8.0
            else:
                base_score = 3.0
            
            # Category multipliers
            category_multipliers = {
                'pii': 1.0,
                'medical': 1.2,
                'hepa': 1.1,
                'compliance_api': 0.9
            }
            
            multiplier = category_multipliers.get(category, 1.0)
            risk_score = base_score * multiplier
            
            # Cap at reasonable individual item score
            return min(risk_score, 15.0)
            
        except Exception as e:
            print(f"Error calculating item risk score: {e}")
            return 5.0
    
    def update_risk_calculation(self):
        """Update the risk calculation display for the selected session"""
        try:
            if not self.current_session:
                self.calc_text.config(state=tk.NORMAL)
                self.calc_text.delete(1.0, tk.END)
                self.calc_text.insert(tk.END, "Select a session to see detailed risk score calculation...")
                self.calc_text.config(state=tk.DISABLED)
                return
            
            session_data = self.session_data[self.current_session]
            
            # Try to load detailed analysis data
            detailed_items = self._load_detailed_flagged_items(session_data.get('unique_session_id', self.current_session))
            
            if not detailed_items:
                # Fallback to basic calculation from session data
                self._show_basic_risk_calculation(session_data)
                return
            
            # Calculate detailed risk breakdown
            self._show_detailed_risk_calculation(detailed_items, session_data)
            
        except Exception as e:
            print(f"Error updating risk calculation: {e}")
            self.calc_text.config(state=tk.NORMAL)
            self.calc_text.delete(1.0, tk.END)
            self.calc_text.insert(tk.END, f"Error calculating risk score: {str(e)}")
            self.calc_text.config(state=tk.DISABLED)
    
    def _show_basic_risk_calculation(self, session_data):
        """Show basic risk calculation from session data"""
        self.calc_text.config(state=tk.NORMAL)
        self.calc_text.delete(1.0, tk.END)
        
        # Get basic metrics
        final_metrics = session_data.get('final_analysis_metrics', {})
        total_lines = final_metrics.get('total_lines', 0)
        total_fields = final_metrics.get('total_sensitive_fields', 0)
        total_data = final_metrics.get('total_sensitive_data', 0)
        avg_risk_score = final_metrics.get('average_risk_score', 0)
        risk_level = final_metrics.get('risk_level', 'Unknown')
        
        self.calc_text.insert(tk.END, "📊 Basic Risk Calculation:\n\n", "header")
        self.calc_text.insert(tk.END, f"• Total Lines Analyzed: {total_lines}\n", "calculation")
        self.calc_text.insert(tk.END, f"• Sensitive Fields Found: {total_fields}\n", "calculation")
        self.calc_text.insert(tk.END, f"• Sensitive Data Instances: {total_data}\n", "calculation")
        self.calc_text.insert(tk.END, f"• Total Items: {total_fields + total_data}\n\n", "calculation")
        
        if total_fields + total_data > 0:
            # Basic calculation
            base_score = (total_fields * 0.1) + (total_data * 8)
            self.calc_text.insert(tk.END, f"• Base Score: ({total_fields} fields × 0.1) + ({total_data} data × 8) = {base_score} points\n", "calculation")
            self.calc_text.insert(tk.END, f"• Line Normalization: Applied for {total_lines} lines\n", "calculation")
            self.calc_text.insert(tk.END, f"• Final Risk Score: {avg_risk_score:.1f}/100 ({risk_level.upper()})\n\n", "score")
            self.calc_text.insert(tk.END, f"Note: Detailed breakdown available for sessions with flagged items data.", "items")
        else:
            self.calc_text.insert(tk.END, f"• No sensitive data detected\n", "calculation")
            self.calc_text.insert(tk.END, f"• Risk Score: {avg_risk_score:.1f}/100 ({risk_level.upper()})", "score")
        self.calc_text.config(state=tk.DISABLED)
    
    def _show_detailed_risk_calculation(self, detailed_items, session_data):
        """Show detailed risk calculation from flagged items"""
        self.calc_text.config(state=tk.NORMAL)
        self.calc_text.delete(1.0, tk.END)
        
        # Aggregate data by category
        category_data = {
            'pii': {'fields': 0, 'data': 0, 'items': []},
            'medical': {'fields': 0, 'data': 0, 'items': []},
            'hepa': {'fields': 0, 'data': 0, 'items': []},
            'compliance_api': {'fields': 0, 'data': 0, 'items': []}
        }
        
        total_risk_score = 0
        analysis_count = 0
        
        for item in detailed_items:
            item_type = item.get('type', '')
            item_name = item.get('name', '')
            item_category = item.get('category', '').lower()
            
            if item_category in category_data:
                if item_type == 'sensitive_field':
                    category_data[item_category]['fields'] += 1
                elif item_type == 'sensitive_data':
                    category_data[item_category]['data'] += 1
                
                category_data[item_category]['items'].append({
                    'type': item_type,
                    'name': item_name,
                    'line': item.get('line', 0)
                })
            
            total_risk_score += item.get('analysis_risk_score', 0)
            analysis_count += 1
        
        # Get session metrics
        final_metrics = session_data.get('final_analysis_metrics', {})
        avg_risk_score = final_metrics.get('average_risk_score', 0)
        risk_level = final_metrics.get('risk_level', 'Unknown')
        total_lines = final_metrics.get('total_lines', 0)
        
        # Build calculation text with color coding
        self.calc_text.insert(tk.END, "📊 Detailed Risk Calculation:\n\n", "header")
        self.calc_text.insert(tk.END, "Session Overview:\n", "header")
        self.calc_text.insert(tk.END, f"• Total Lines: {total_lines}\n", "calculation")
        self.calc_text.insert(tk.END, f"• Analyses: {analysis_count}\n", "calculation")
        self.calc_text.insert(tk.END, f"• Final Score: {avg_risk_score:.1f}/100 ({risk_level.upper()})\n\n", "score")
        
        self.calc_text.insert(tk.END, "Category Breakdown:\n", "header")
        
        category_names = {
            'pii': 'PII Data',
            'medical': 'Medical Data',
            'hepa': 'HEPA Data',
            'compliance_api': 'API/Security Data'
        }
        
        category_multipliers = {
            'pii': 1.0,
            'medical': 1.2,
            'hepa': 1.1,
            'compliance_api': 0.9
        }
        
        total_base_score = 0
        
        for category, data in category_data.items():
            if data['fields'] > 0 or data['data'] > 0:
                fields_score = data['fields'] * 0.1
                data_score = data['data'] * 8
                category_base = fields_score + data_score
                multiplier = category_multipliers.get(category, 1.0)
                category_score = category_base * multiplier
                total_base_score += category_score
                
                self.calc_text.insert(tk.END, f"• {category_names.get(category, category.title())}:\n", "category")
                self.calc_text.insert(tk.END, f"  - Fields: {data['fields']} × 0.1 = {fields_score} points\n", "calculation")
                self.calc_text.insert(tk.END, f"  - Data: {data['data']} × 8 = {data_score} points\n", "calculation")
                self.calc_text.insert(tk.END, f"  - Subtotal: {category_base} × {multiplier} = {category_score:.1f} points\n", "score")
                
                # Show specific items
                if data['items']:
                    self.calc_text.insert(tk.END, f"  - Items: ", "calculation")
                    item_names = [item['name'][:15] + "..." if len(item['name']) > 15 else item['name'] 
                                for item in data['items'][:3]]
                    self.calc_text.insert(tk.END, f"{', '.join(item_names)}", "items")
                    if len(data['items']) > 3:
                        self.calc_text.insert(tk.END, f" (+{len(data['items'])-3} more)", "items")
                    self.calc_text.insert(tk.END, "\n")
                self.calc_text.insert(tk.END, "\n")
        
        self.calc_text.insert(tk.END, f"Calculation Summary:\n", "summary")
        self.calc_text.insert(tk.END, f"• Base Score: {total_base_score:.1f} points\n", "calculation")
        self.calc_text.insert(tk.END, f"• Line Normalization: Applied for {total_lines} lines\n", "calculation")
        self.calc_text.insert(tk.END, f"• Final Score: {avg_risk_score:.1f}/100\n", "score")
        self.calc_text.insert(tk.END, f"• Risk Level: {risk_level.upper()}\n\n", "score")
        self.calc_text.insert(tk.END, f"Multipliers: Medical (1.2x), HEPA (1.1x), PII (1.0x), API (0.9x)", "calculation")
        self.calc_text.config(state=tk.DISABLED)
    
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
    project_root = Path(__file__).parent.parent.parent
    logs_dir = project_root / "core" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Start the log viewer
    viewer = LogViewer()
    viewer.run()
