#!/usr/bin/env python3
"""
Delete All Sessions Script for Sec360 by Abhay
This script safely deletes all existing practice sessions and related data.
"""

import os
import json
import shutil
from pathlib import Path
import sys

# Add core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

class SessionCleaner:
    def __init__(self):
        # Get project root directory
        self.project_root = Path(__file__).parent.parent.parent
        self.sessions_dir = self.project_root / "core" / "logs" / "sessions"
        self.active_sessions_file = self.project_root / "core" / "logs" / "sessions" / "active_sessions.json"
        
    def list_all_sessions(self):
        """List all existing sessions"""
        print("🔍 Scanning for existing sessions...")
        
        sessions_found = []
        
        # Check sessions directory
        if self.sessions_dir.exists():
            for file_path in self.sessions_dir.glob("practice_*.json"):
                if file_path.name != "active_sessions.json":  # Skip active sessions file
                    try:
                        with open(file_path, 'r') as f:
                            session_data = json.load(f)
                            sessions_found.append({
                                'file': file_path.name,
                                'user': session_data.get('user_name', 'Unknown'),
                                'duration': session_data.get('session_duration', 0),
                                'messages': session_data.get('message_count', 0),
                                'analyses': session_data.get('analysis_count', 0)
                            })
                    except Exception as e:
                        print(f"⚠️  Error reading {file_path.name}: {e}")
        
        return sessions_found
    
    def display_sessions(self, sessions):
        """Display all sessions in a formatted table"""
        if not sessions:
            print("✅ No practice sessions found.")
            return
        
        print(f"\n📊 Found {len(sessions)} practice session(s):")
        print("=" * 80)
        print(f"{'#':<3} {'Session File':<25} {'User':<15} {'Duration':<10} {'Messages':<9} {'Analyses':<9}")
        print("-" * 80)
        
        for i, session in enumerate(sessions, 1):
            duration_str = f"{session['duration']:.1f}s" if session['duration'] > 0 else "N/A"
            print(f"{i:<3} {session['file']:<25} {session['user']:<15} {duration_str:<10} {session['messages']:<9} {session['analyses']:<9}")
        
        print("=" * 80)
    
    def confirm_deletion(self, sessions):
        """Ask for confirmation before deletion"""
        if not sessions:
            return False
        
        print(f"\n⚠️  WARNING: This will permanently delete {len(sessions)} practice session(s).")
        print("📋 This includes:")
        print("   • All session data and analysis results")
        print("   • User progress and statistics")
        print("   • Risk scores and token counts")
        print("   • Session logs and timestamps")
        
        print("\n🔄 This action CANNOT be undone!")
        
        while True:
            response = input("\n❓ Are you sure you want to delete ALL sessions? (yes/no): ").lower().strip()
            if response in ['yes', 'y']:
                return True
            elif response in ['no', 'n']:
                return False
            else:
                print("Please enter 'yes' or 'no'")
    
    def delete_sessions(self, sessions):
        """Delete all session files"""
        if not sessions:
            print("✅ No sessions to delete.")
            return
        
        deleted_count = 0
        failed_count = 0
        
        print(f"\n🗑️  Deleting {len(sessions)} session(s)...")
        
        for session in sessions:
            file_path = self.sessions_dir / session['file']
            try:
                if file_path.exists():
                    file_path.unlink()  # Delete the file
                    deleted_count += 1
                    print(f"✅ Deleted: {session['file']}")
                else:
                    print(f"⚠️  File not found: {session['file']}")
            except Exception as e:
                failed_count += 1
                print(f"❌ Failed to delete {session['file']}: {e}")
        
        print(f"\n📊 Deletion Summary:")
        print(f"   ✅ Successfully deleted: {deleted_count}")
        print(f"   ❌ Failed to delete: {failed_count}")
        
        return deleted_count, failed_count
    
    def cleanup_active_sessions(self):
        """Clean up active sessions file"""
        print("\n🧹 Cleaning up active sessions...")
        
        if self.active_sessions_file.exists():
            try:
                # Reset active sessions to empty
                with open(self.active_sessions_file, 'w') as f:
                    json.dump({}, f, indent=2)
                print("✅ Active sessions file reset")
            except Exception as e:
                print(f"❌ Failed to reset active sessions: {e}")
        else:
            print("ℹ️  No active sessions file found")
    
    def cleanup_logs(self):
        """Clean up related log files"""
        print("\n🧹 Cleaning up related log files...")
        
        # Clean up application log
        app_log = self.project_root / "logs" / "application.log"
        if app_log.exists():
            try:
                app_log.unlink()
                print("✅ Deleted application.log")
            except Exception as e:
                print(f"❌ Failed to delete application.log: {e}")
        
        # Clean up Ollama log
        ollama_log = self.project_root / "logs" / "ollama.log"
        if ollama_log.exists():
            try:
                ollama_log.unlink()
                print("✅ Deleted ollama.log")
            except Exception as e:
                print(f"❌ Failed to delete ollama.log: {e}")
    
    def run(self):
        """Main execution function"""
        print("🛡️  Sec360 by Abhay - Session Cleaner")
        print("=" * 50)
        
        # Ensure sessions directory exists
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # List all sessions
        sessions = self.list_all_sessions()
        
        # Display sessions
        self.display_sessions(sessions)
        
        # Ask for confirmation
        if not self.confirm_deletion(sessions):
            print("\n❌ Deletion cancelled by user.")
            return
        
        # Delete sessions
        deleted_count, failed_count = self.delete_sessions(sessions)
        
        # Clean up active sessions
        self.cleanup_active_sessions()
        
        # Clean up logs
        self.cleanup_logs()
        
        # Final summary
        print(f"\n🎉 Session cleanup completed!")
        print(f"   📊 Sessions deleted: {deleted_count}")
        print(f"   🧹 Active sessions reset")
        print(f"   📝 Log files cleaned")
        
        if failed_count > 0:
            print(f"   ⚠️  {failed_count} file(s) could not be deleted")
        
        print("\n✅ All practice sessions have been permanently removed.")

def main():
    """Main function"""
    try:
        cleaner = SessionCleaner()
        cleaner.run()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
