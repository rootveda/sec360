#!/usr/bin/env python3
"""
Generate Detailed Sessions for Existing Practice Sessions
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from detailed_session_generator import DetailedSessionGenerator

def generate_detailed_sessions_for_existing():
    """Generate detailed sessions for existing practice sessions"""
    
    generator = DetailedSessionGenerator()
    
    # Load existing practice sessions
    sessions_dir = Path("core/logs/sessions")
    detailed_sessions_dir = Path("detailed_sessions")
    
    print("🔍 Scanning existing practice sessions...")
    
    practice_files = list(sessions_dir.glob("practice_*.json"))
    print(f"Found {len(practice_files)} practice session files")
    
    for practice_file in practice_files:
        session_id = practice_file.stem
        
        # Skip if detailed session already exists
        detailed_file = detailed_sessions_dir / f"{session_id}_detailed.json"
        if detailed_file.exists():
            print(f"⏭️  Skipping {session_id} (detailed session already exists)")
            continue
        
        try:
            # Load practice session data
            with open(practice_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            user_name = session_data.get('user_name', 'Unknown')
            session_start_time = session_data.get('session_start_time', 'Unknown')
            session_end_time = session_data.get('session_end_time', 'Unknown')
            
            # Get code analyses and final metrics
            code_analyses = session_data.get('code_analyses', [])
            final_analysis_metrics = session_data.get('final_analysis_metrics', {})
            conversations = session_data.get('conversations', [])
            
            # Check if we have any analysis data (either from code_analyses or final_analysis_metrics)
            has_code_analyses = bool(code_analyses)
            has_final_metrics = bool(final_analysis_metrics)
            
            if not has_code_analyses and not has_final_metrics:
                print(f"⚠️  No analysis data found for {session_id}")
                continue
            
            # Extract code content from analyses or conversations
            code_snippet = ""
            if has_code_analyses:
                # Extract code content from the first analysis
                first_analysis = code_analyses[0]
                code_snippet = first_analysis.get('code_snippet', '')
            elif has_final_metrics and conversations:
                # Extract code content from conversations if code_analyses is empty
                for conv in conversations:
                    if conv.get('message_type') == 'code_submission':
                        code_snippet = conv.get('message', '')
                        break
            
            if not code_snippet or len(code_snippet.strip()) < 10:
                print(f"⚠️  No meaningful code content found for {session_id}")
                continue
            
            print(f"📝 Generating detailed session for {session_id} (User: {user_name})")
            
            # Generate detailed session
            detailed_session = generator.generate_detailed_session(
                session_id=session_id,
                user_name=user_name,
                code_content=code_snippet,
                session_start_time=session_start_time,
                session_end_time=session_end_time
            )
            
            if detailed_session:
                print(f"✅ Generated detailed session: {session_id}")
                
                # Generate and display summary
                summary = generator.generate_summary_report(session_id)
                print("📋 Summary:")
                print(summary)
                print("-" * 80)
            else:
                print(f"❌ Failed to generate detailed session for {session_id}")
                
        except Exception as e:
            print(f"❌ Error processing {session_id}: {e}")
    
    print(f"\n🎉 Detailed session generation complete!")
    print(f"📁 Detailed sessions saved in: {detailed_sessions_dir}")

if __name__ == "__main__":
    generate_detailed_sessions_for_existing()
