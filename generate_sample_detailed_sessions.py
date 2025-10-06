#!/usr/bin/env python3
"""
Generate Detailed Sessions from Sample Files
"""

import json
import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from detailed_session_generator import DetailedSessionGenerator

def generate_detailed_sessions_from_samples():
    """Generate detailed sessions from sample files"""
    
    generator = DetailedSessionGenerator()
    
    # Sample files to process
    sample_files = [
        ("API Keys Sample", "data/samples/api_keys_sample.py"),
        ("PII Sample", "data/samples/pii_sample.py"),
        ("Medical Records Sample", "data/samples/medical_records_sample.py"),
        ("Internal Infrastructure Sample", "data/samples/internal_infrastructure_sample.py"),
        ("Compliance Sample", "data/samples/compliance_sample.py"),
    ]
    
    print("🚀 Generating detailed sessions from sample files...")
    
    for name, filepath in sample_files:
        try:
            # Read sample file content
            with open(filepath, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # Generate session ID
            session_id = f"sample_{name.lower().replace(' ', '_')}_{int(time.time())}"
            user_name = f"sample_user_{name.split()[0].lower()}"
            
            print(f"\n📝 Processing: {name}")
            print(f"   File: {filepath}")
            print(f"   Session ID: {session_id}")
            print(f"   User: {user_name}")
            
            # Generate detailed session
            detailed_session = generator.generate_detailed_session(
                session_id=session_id,
                user_name=user_name,
                code_content=code_content
            )
            
            if detailed_session:
                print(f"✅ Generated detailed session: {session_id}")
                
                # Generate and display summary
                summary = generator.generate_summary_report(session_id)
                print("📋 Summary:")
                print(summary)
                print("-" * 80)
            else:
                print(f"❌ Failed to generate detailed session for {name}")
                
        except Exception as e:
            print(f"❌ Error processing {name}: {e}")
    
    print(f"\n🎉 Detailed session generation complete!")
    print(f"📁 Detailed sessions saved in: detailed_sessions/")

if __name__ == "__main__":
    generate_detailed_sessions_from_samples()
