#!/usr/bin/env python3
"""
Detailed Session Generator for Sec360 by Abhay
Creates comprehensive session files with all analysis details
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from core.analysis.ollama_analyzer import OllamaAnalyzer
from core.analysis.json_parser import JsonParser

class DetailedSessionGenerator:
    """Generate detailed session files with comprehensive analysis data"""
    
    def __init__(self):
        self.analyzer = OllamaAnalyzer()
        self.json_parser = JsonParser()
        self.detailed_sessions_dir = Path("detailed_sessions")
        self.detailed_sessions_dir.mkdir(exist_ok=True)
    
    def generate_detailed_session(self, session_id: str, user_name: str, code_content: str, 
                                 session_start_time: str = None, session_end_time: str = None) -> Dict:
        """Generate a detailed session file with comprehensive analysis"""
        
        if not session_start_time:
            session_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not session_end_time:
            session_end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Analyze the code
        print(f"🔍 Analyzing code for session: {session_id}")
        analysis_result = self.analyzer.analyze_code(code_content)
        
        if not analysis_result or not analysis_result.get('success', False):
            print(f"❌ Analysis failed for session: {session_id}")
            return None
        
        analysis_table = analysis_result.get('analysis_table', {})
        
        # Extract detailed information
        lines_of_code = analysis_table.get('lines', 0)
        sensitive_fields = analysis_table.get('sensitive_fields', 0)
        sensitive_data = analysis_table.get('sensitive_data', 0)
        pii_count = analysis_table.get('pii', 0)
        medical_count = analysis_table.get('medical', 0)
        hepa_count = analysis_table.get('hepa', 0)
        compliance_api_count = analysis_table.get('compliance_api', 0)
        risk_score = analysis_table.get('risk_score', 0)
        
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
        
        # Parse analysis details for flagged items
        analysis_details = analysis_table.get('analysis_details', {})
        flagged_items = analysis_details.get('flagged_items', [])
        
        # Categorize flagged items
        sensitive_fields_list = []
        sensitive_data_list = []
        pii_items = []
        medical_items = []
        api_security_items = []
        
        for item in flagged_items:
            item_type = item.get('type', 'unknown')
            item_name = item.get('name', 'Unknown')
            item_category = item.get('category', 'Unknown')
            item_line = item.get('line', 0)
            
            item_data = {
                'name': item_name,
                'line': item_line,
                'category': item_category,
                'type': item_type
            }
            
            if item_type == 'sensitive_field':
                sensitive_fields_list.append(item_data)
            elif item_type == 'sensitive_data':
                sensitive_data_list.append(item_data)
            
            # Categorize by category
            if item_category.upper() in ['PII', 'PERSONAL']:
                pii_items.append(item_data)
            elif item_category.upper() in ['MEDICAL', 'HEALTH', 'HIPAA']:
                medical_items.append(item_data)
            elif item_category.upper() in ['API', 'SECURITY', 'COMPLIANCE', 'TOKEN', 'KEY']:
                api_security_items.append(item_data)
        
        # Create detailed session data
        detailed_session = {
            "session_id": session_id,
            "user_name": user_name,
            "session_start_time": session_start_time,
            "session_end_time": session_end_time,
            "session_duration": 0,  # Will be calculated if needed
            "code_content": code_content,
            "code_length": len(code_content.split('\n')),
            "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model_used": "llama3.2:3b",
            
            # Conversation history
            "conversations": [
                {
                    "timestamp": session_start_time,
                    "user": user_name,
                    "message": f"Started practice session",
                    "message_type": "session_start",
                    "session_id": session_id
                },
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "user": user_name,
                    "message": f"Submitted code for analysis:\n{code_content[:200]}{'...' if len(code_content) > 200 else ''}",
                    "message_type": "code_submission",
                    "session_id": session_id
                },
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "user": "AI Security Mentor",
                    "message": f"Analysis complete. Found {sensitive_fields} sensitive fields and {sensitive_data} sensitive data instances. Risk score: {risk_score}/100 ({risk_level} RISK).",
                    "message_type": "analysis_response",
                    "session_id": session_id
                },
                {
                    "timestamp": session_end_time,
                    "user": user_name,
                    "message": "Completed session analysis",
                    "message_type": "session_end",
                    "session_id": session_id
                }
            ],
            
            # Current Analysis
            "current_analysis": {
                "lines_of_code": lines_of_code,
                "sensitive_fields": {
                    "count": sensitive_fields,
                    "items": sensitive_fields_list
                },
                "sensitive_data": {
                    "count": sensitive_data,
                    "items": sensitive_data_list
                },
                "pii": {
                    "count": pii_count,
                    "items": pii_items
                },
                "medical": {
                    "count": medical_count,
                    "items": medical_items
                },
                "hepa": {
                    "count": hepa_count,
                    "items": []  # Will be populated if needed
                },
                "api_security": {
                    "count": compliance_api_count,
                    "items": api_security_items
                },
                "risk_score": risk_score,
                "risk_level": risk_level
            },
            
            # Raw analysis data
            "raw_analysis": analysis_table,
            "flagged_items": flagged_items,
            
            # Analysis summary
            "analysis_summary": {
                "total_lines": lines_of_code,
                "total_sensitive_fields": sensitive_fields,
                "total_sensitive_data": sensitive_data,
                "total_pii": pii_count,
                "total_medical": medical_count,
                "total_hepa": hepa_count,
                "total_api_security": compliance_api_count,
                "average_risk_score": risk_score,
                "risk_level": risk_level
            }
        }
        
        # Save detailed session file
        detailed_file_path = self.detailed_sessions_dir / f"{session_id}_detailed.json"
        with open(detailed_file_path, 'w', encoding='utf-8') as f:
            json.dump(detailed_session, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Detailed session saved: {detailed_file_path}")
        return detailed_session
    
    def generate_summary_report(self, session_id: str) -> str:
        """Generate a formatted summary report"""
        
        detailed_file_path = self.detailed_sessions_dir / f"{session_id}_detailed.json"
        
        if not detailed_file_path.exists():
            return "❌ Detailed session file not found"
        
        with open(detailed_file_path, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        current_analysis = session_data.get('current_analysis', {})
        
        # Format the summary
        summary = f"""📊 Current Analysis:
• Lines of Code: {current_analysis.get('lines_of_code', 0)}
• Sensitive Fields: {current_analysis.get('sensitive_fields', {}).get('count', 0)} [including All fields value]
• Sensitive Data: {current_analysis.get('sensitive_data', {}).get('count', 0)} [including All data value]
• PII Count: {current_analysis.get('pii', {}).get('count', 0)} [including All PII Name]
• Medical Data: {current_analysis.get('medical', {}).get('count', 0)} [including All Medical Name]
• API/Security: {current_analysis.get('api_security', {}).get('count', 0)} [including All API/Security Name]
• Risk Score: {current_analysis.get('risk_score', 0)}/100 ({current_analysis.get('risk_level', 'UNKNOWN')} RISK)

🔍 Detailed Breakdown:
"""
        
        # Add detailed field information
        sensitive_fields = current_analysis.get('sensitive_fields', {}).get('items', [])
        if sensitive_fields:
            summary += "\n📋 Sensitive Fields:\n"
            for field in sensitive_fields:
                summary += f"  • {field['name']} (Line {field['line']}, Category: {field['category']})\n"
        
        # Add detailed data information
        sensitive_data = current_analysis.get('sensitive_data', {}).get('items', [])
        if sensitive_data:
            summary += "\n🔒 Sensitive Data:\n"
            for data in sensitive_data:
                summary += f"  • {data['name']} (Line {data['line']}, Category: {data['category']})\n"
        
        # Add PII information
        pii_items = current_analysis.get('pii', {}).get('items', [])
        if pii_items:
            summary += "\n👤 PII Items:\n"
            for pii in pii_items:
                summary += f"  • {pii['name']} (Line {pii['line']})\n"
        
        # Add Medical information
        medical_items = current_analysis.get('medical', {}).get('items', [])
        if medical_items:
            summary += "\n🏥 Medical Items:\n"
            for medical in medical_items:
                summary += f"  • {medical['name']} (Line {medical['line']})\n"
        
        # Add API/Security information
        api_items = current_analysis.get('api_security', {}).get('items', [])
        if api_items:
            summary += "\n🔐 API/Security Items:\n"
            for api in api_items:
                summary += f"  • {api['name']} (Line {api['line']})\n"
        
        return summary

def main():
    """Test the detailed session generator"""
    generator = DetailedSessionGenerator()
    
    # Test with sample code
    test_code = '''# Sample API Keys and Tokens
def authenticate_user():
    api_key = "sk-1234567890abcdef"
    secret_key = "a1b2c3d4e5f6g7h8"
    bearer_token = "Bearer abcdef123456"
    
    return {"status": "authenticated"}

def process_data():
    user_email = "john.doe@example.com"
    phone_number = "+1-555-123-4567"
    
    return {"processed": True}'''
    
    # Generate detailed session
    session_id = f"test_detailed_{int(time.time())}"
    user_name = "test_user"
    
    print("🚀 Generating detailed session...")
    detailed_session = generator.generate_detailed_session(
        session_id=session_id,
        user_name=user_name,
        code_content=test_code
    )
    
    if detailed_session:
        print("\n📋 Summary Report:")
        summary = generator.generate_summary_report(session_id)
        print(summary)
        
        print(f"\n✅ Detailed session file created: detailed_sessions/{session_id}_detailed.json")
    else:
        print("❌ Failed to generate detailed session")

if __name__ == "__main__":
    main()
