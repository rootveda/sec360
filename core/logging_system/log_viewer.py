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
        self.root.title("Sec360 by Abhay - Risk Viewer")
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
        self.log_tree = ttk.Treeview(logs_frame, columns=columns, show='headings', height=10)
        
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
        
        # Risk calculation section (moved up and expanded)
        calc_frame = ttk.LabelFrame(main_frame, text="📊 Risk Score Calculation & Analysis")
        calc_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Risk calculation display (expanded)
        self.calc_text = tk.Text(calc_frame, height=10, wrap=tk.WORD, font=('TkDefaultFont', 11, 'bold'),
                                bg="#f8f9fa", fg="#000000", relief=tk.SUNKEN, bd=1)
        self.calc_text.pack(fill=tk.BOTH, expand=True, pady=(2, 0))
        
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
        
        # Create a simple text widget for the footer content
        footer_text = tk.Text(footer_frame, height=8, wrap=tk.WORD, font=('TkDefaultFont', 10),
                             bg="#f8f9fa", fg="#2c3e50", relief=tk.SUNKEN, bd=1)
        footer_text.pack(fill=tk.X, padx=8, pady=8)
        
        # Transposed layout - each section side by side
        footer_text.insert(tk.END, "Risk Categories: ", "header")
        footer_text.insert(tk.END, "🔴 PII ", "pii")
        footer_text.insert(tk.END, "🟢 Medical ", "medical")
        footer_text.insert(tk.END, "🔵 HEPA ", "hepa")
        footer_text.insert(tk.END, "🟠 API/Security\n", "api")
        
        footer_text.insert(tk.END, "Risk Score Details: ", "header")
        footer_text.insert(tk.END, "🟢 LOW(0-29) ", "low")
        footer_text.insert(tk.END, "🟡 MEDIUM(30-59) ", "medium")
        footer_text.insert(tk.END, "🔴 HIGH(60-79) ", "high")
        footer_text.insert(tk.END, "🚨 CRITICAL(80-100)\n", "critical")
        
        footer_text.insert(tk.END, "Risk Calculation Formula: ", "header")
        footer_text.insert(tk.END, "Fields×0.1 ", "formula")
        footer_text.insert(tk.END, "Data×8.0 ", "formula")
        footer_text.insert(tk.END, "Medical(1.2x) ", "formula")
        footer_text.insert(tk.END, "HEPA(1.1x) ", "formula")
        footer_text.insert(tk.END, "PII(1.0x) ", "formula")
        footer_text.insert(tk.END, "API(0.9x)\n", "formula")
        
        footer_text.insert(tk.END, "Line Factor: ", "header")
        footer_text.insert(tk.END, "min(1.0, max(0.1, lines/100))", "formula")
        
        # Configure text tags for color coding with larger fonts for better readability
        footer_text.tag_configure("header", foreground="#2c3e50", font=('TkDefaultFont', 12, 'bold'))
        footer_text.tag_configure("pii", foreground="#cc0000", font=('TkDefaultFont', 11, 'bold'))
        footer_text.tag_configure("medical", foreground="#006600", font=('TkDefaultFont', 11, 'bold'))
        footer_text.tag_configure("hepa", foreground="#003366", font=('TkDefaultFont', 11, 'bold'))
        footer_text.tag_configure("api", foreground="#cc6600", font=('TkDefaultFont', 11, 'bold'))
        footer_text.tag_configure("low", foreground="#006600", font=('TkDefaultFont', 11, 'bold'))
        footer_text.tag_configure("medium", foreground="#b8860b", font=('TkDefaultFont', 11, 'bold'))
        footer_text.tag_configure("high", foreground="#cc0000", font=('TkDefaultFont', 11, 'bold'))
        footer_text.tag_configure("critical", foreground="#990000", font=('TkDefaultFont', 11, 'bold'))
        footer_text.tag_configure("formula", foreground="#34495e", font=('TkDefaultFont', 11))
        
        footer_text.config(state=tk.DISABLED)
        
    
    def load_sessions(self):
        """Load all available sessions from detailed_sessions folder"""
        self.session_data = {}
        sessions = []
        
        # Look for session files in detailed_sessions directory
        # Get project root directory (go up from core/logging_system/)
        project_root = Path(__file__).parent.parent.parent
        sessions_dir = project_root / "detailed_sessions"
        if sessions_dir.exists():
            # Look for detailed session files
            for file_path in sessions_dir.glob("*_detailed.json"):
                session_id = file_path.stem.replace("_detailed", "")
                
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
                    print(f"Error loading detailed session file {file_path}: {e}")
            
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
        """Load detailed flagged items from detailed sessions"""
        try:
            # Debug logging
            print(f"DEBUG: Looking for detailed session file for session_id: {session_id}")
            
            # Get project root directory
            project_root = Path(__file__).parent.parent.parent
            detailed_sessions_dir = project_root / "detailed_sessions"
            
            print(f"DEBUG: Detailed sessions directory: {detailed_sessions_dir}")
            
            if not detailed_sessions_dir.exists():
                print("DEBUG: Detailed sessions directory does not exist")
                return []
            
            # Look for detailed session file
            detailed_file = detailed_sessions_dir / f"{session_id}_detailed.json"
            
            print(f"DEBUG: Looking for file: {detailed_file}")
            
            if not detailed_file.exists():
                print("DEBUG: Detailed session file does not exist")
                return []
            
            print("DEBUG: Detailed session file found, loading...")
            
            with open(detailed_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Get flagged items from the detailed session data
            flagged_items = []
            
            # Get current analysis flagged items
            current_analysis = session_data.get('current_analysis', {})
            
            # Get sensitive fields
            sensitive_fields = current_analysis.get('sensitive_fields', {}).get('items', [])
            for field in sensitive_fields:
                flagged_item = field.copy()
                flagged_item['type'] = 'sensitive_field'
                flagged_item['timestamp'] = session_data.get('analysis_timestamp', 'Unknown')
                flagged_items.append(flagged_item)
            
            # Get sensitive data
            sensitive_data = current_analysis.get('sensitive_data', {}).get('items', [])
            for data in sensitive_data:
                flagged_item = data.copy()
                flagged_item['type'] = 'sensitive_data'
                flagged_item['timestamp'] = session_data.get('analysis_timestamp', 'Unknown')
                flagged_items.append(flagged_item)
            
            # Get PII items
            pii_items = current_analysis.get('pii', {}).get('items', [])
            for pii in pii_items:
                flagged_item = pii.copy()
                flagged_item['type'] = 'sensitive_field'
                flagged_item['category'] = 'PII'
                flagged_item['timestamp'] = session_data.get('analysis_timestamp', 'Unknown')
                flagged_items.append(flagged_item)
            
            # Get Medical items
            medical_items = current_analysis.get('medical', {}).get('items', [])
            for medical in medical_items:
                flagged_item = medical.copy()
                flagged_item['type'] = 'sensitive_field'
                flagged_item['category'] = 'Medical'
                flagged_item['timestamp'] = session_data.get('analysis_timestamp', 'Unknown')
                flagged_items.append(flagged_item)
            
            # Get API/Security items
            api_security_items = current_analysis.get('api_security', {}).get('items', [])
            for api in api_security_items:
                flagged_item = api.copy()
                flagged_item['type'] = 'sensitive_field'
                flagged_item['category'] = 'API/Security'
                flagged_item['timestamp'] = session_data.get('analysis_timestamp', 'Unknown')
                flagged_items.append(flagged_item)
            
            print(f"DEBUG: Found {len(flagged_items)} flagged items")
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
                base_score = 0.1
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
            return 0.1
    
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
        """Show basic risk calculation from detailed session data"""
        self.calc_text.config(state=tk.NORMAL)
        self.calc_text.delete(1.0, tk.END)
        
        # Get metrics from detailed session data structure
        current_analysis = session_data.get('current_analysis', {})
        total_lines = current_analysis.get('lines_of_code', 0)
        total_fields = current_analysis.get('sensitive_fields', {}).get('count', 0)
        total_data = current_analysis.get('sensitive_data', {}).get('count', 0)
        avg_risk_score = current_analysis.get('risk_score', 0)
        risk_level = current_analysis.get('risk_level', 'Unknown')
        
        # Get category counts
        pii_count = current_analysis.get('pii', {}).get('count', 0)
        medical_count = current_analysis.get('medical', {}).get('count', 0)
        hepa_count = current_analysis.get('hepa', {}).get('count', 0)
        api_security_count = current_analysis.get('api_security', {}).get('count', 0)
        
        self.calc_text.insert(tk.END, "📊 Risk Score Analysis & Calculation:\n\n", "header")
        
        # Risk metrics overview
        self.calc_text.insert(tk.END, "📈 Risk Metrics Overview:\n", "category")
        self.calc_text.insert(tk.END, f"• Total Lines Analyzed: {total_lines}\n", "calculation")
        self.calc_text.insert(tk.END, f"• Sensitive Fields Found: {total_fields}\n", "calculation")
        self.calc_text.insert(tk.END, f"• Sensitive Data Instances: {total_data}\n", "calculation")
        self.calc_text.insert(tk.END, f"• Total Risk Items: {total_fields + total_data}\n", "calculation")
        self.calc_text.insert(tk.END, f"• PII Count: {pii_count}\n", "calculation")
        self.calc_text.insert(tk.END, f"• Medical Data: {medical_count}\n", "calculation")
        self.calc_text.insert(tk.END, f"• HEPA Count: {hepa_count}\n", "calculation")
        self.calc_text.insert(tk.END, f"• API/Security: {api_security_count}\n\n", "calculation")
        
        if total_fields + total_data > 0:
            # Detailed risk calculation
            self.calc_text.insert(tk.END, "🧮 Risk Calculation Breakdown:\n", "category")
            
            # Field risk calculation
            field_risk = min(60, total_fields * 0.1)
            self.calc_text.insert(tk.END, f"• Field Risk: min(60, {total_fields} × 0.1) = {field_risk}\n", "calculation")
            
            # Data risk calculation
            data_risk = min(60, total_data * 8.0)
            self.calc_text.insert(tk.END, f"• Data Risk: min(60, {total_data} × 8.0) = {data_risk}\n", "calculation")
            
            # Line factor calculation
            line_factor = max(0.7, min(1.0, 1.0 - (0.001 * total_lines / 100)))
            self.calc_text.insert(tk.END, f"• Line Factor: max(0.7, min(1.0, 1.0 - (0.001 × {total_lines} / 100))) = {line_factor:.3f}\n", "calculation")
            
            # Base score calculation
            base_score = (field_risk + data_risk) * line_factor
            self.calc_text.insert(tk.END, f"• Base Score: ({field_risk} + {data_risk}) × {line_factor:.3f} = {base_score:.1f}\n", "calculation")
            
            # Category score calculation
            category_score = pii_count + medical_count + hepa_count + api_security_count
            self.calc_text.insert(tk.END, f"• Category Score: {pii_count} + {medical_count} + {hepa_count} + {api_security_count} = {category_score}\n", "calculation")
            
            # Final risk score
            final_score = min(100, int(base_score + category_score))
            self.calc_text.insert(tk.END, f"• Final Risk Score: min(100, int({base_score:.1f} + {category_score})) = {final_score}/100 ({risk_level.upper()})\n\n", "score")
            
            # Risk level analysis (aligned with RiskCalculator thresholds)
            self.calc_text.insert(tk.END, "🎯 Risk Level Analysis:\n", "category")
            if avg_risk_score >= 101:
                self.calc_text.insert(tk.END, f"• Risk Level: CRITICAL ({risk_level.upper()})\n", "score")
                self.calc_text.insert(tk.END, f"• Recommendation: Immediate action required\n", "items")
                self.calc_text.insert(tk.END, f"• Priority: Critical security review needed\n", "items")
            elif avg_risk_score >= 100:
                self.calc_text.insert(tk.END, f"• Risk Level: HIGH ({risk_level.upper()})\n", "score")
                self.calc_text.insert(tk.END, f"• Recommendation: Address security issues urgently\n", "items")
                self.calc_text.insert(tk.END, f"• Priority: High\n", "items")
            elif avg_risk_score >= 80:
                self.calc_text.insert(tk.END, f"• Risk Level: MEDIUM ({risk_level.upper()})\n", "score")
                self.calc_text.insert(tk.END, f"• Recommendation: Address security issues\n", "items")
                self.calc_text.insert(tk.END, f"• Priority: Review and remediate\n", "items")
            elif avg_risk_score >= 20:
                self.calc_text.insert(tk.END, f"• Risk Level: LOW ({risk_level.upper()})\n", "score")
                self.calc_text.insert(tk.END, f"• Recommendation: Monitor and improve\n", "items")
                self.calc_text.insert(tk.END, f"• Priority: Good security practices\n", "items")
            else:
                self.calc_text.insert(tk.END, f"• Risk Level: MINIMAL ({risk_level.upper()})\n", "score")
                self.calc_text.insert(tk.END, f"• Recommendation: Excellent security\n", "items")
                self.calc_text.insert(tk.END, f"• Priority: Maintain current practices\n", "items")
            
            self.calc_text.insert(tk.END, f"\n💡 Note: For detailed field names and data values, use the Enhanced Log Viewer.", "items")
        else:
            self.calc_text.insert(tk.END, f"• No sensitive data detected\n", "calculation")
            self.calc_text.insert(tk.END, f"• Risk Score: {avg_risk_score:.1f}/100 ({risk_level.upper()})\n", "score")
            self.calc_text.insert(tk.END, f"• Status: Clean code - no security risks identified", "items")
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
        
        # Get session metrics - try both locations
        final_metrics = session_data.get('final_analysis_metrics', {})
        if not final_metrics:
            # If final_analysis_metrics is empty, try reading from root level
            final_metrics = {
                'total_lines': session_data.get('code_length', 0),
                'average_risk_score': session_data.get('risk_score', 0),
                'risk_level': session_data.get('risk_level', 'Unknown'),
                'total_analyses': session_data.get('current_analysis', {}).get('total_analyses', 0)
            }
        
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
                    # Show ALL items, not just first 3
                    item_names = []
                    for item in data['items']:
                        item_name = item.get('name', 'Unknown')
                        # Truncate very long names but show more than 15 chars
                        if len(item_name) > 25:
                            item_name = item_name[:25] + "..."
                        item_names.append(item_name)
                    
                    self.calc_text.insert(tk.END, f"{', '.join(item_names)}", "items")
                    self.calc_text.insert(tk.END, f" ({len(data['items'])} total)", "items")
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
