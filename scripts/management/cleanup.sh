#!/bin/bash

# 🧹 Sec360 - Session Cleanup Script
# Usage: ./scripts/management/cleanup.sh

set -e

echo "🧹 Sec360 Session Cleanup Script"
echo "==============================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_status "Starting cleanup process..."

# Kill any running Sec360 processes
print_status "Stopping Sec360 processes..."
pkill -f sec360.py || echo "No Sec360 processes found"
pkill -f "python.*sec360" || echo "No Sec360 Python processes found"

# Kill any running Ollama processes (optional)
print_status "Checking Ollama processes..."
if pgrep -f ollama > /dev/null; then
    echo -e "${YELLOW}[WARNING]${NC} Ollama is still running. Do you want to stop it too?"
    echo "Press Enter to continue with Ollama running, or Ctrl+C to stop and restart Ollama manually"
    read -t 5 -n 1 || echo "Continuing with Ollama running..."
else
    print_status "Ollama not running (OK)"
fi

# Clean up session files
print_status "Cleaning session files..."

SESSION_DIR="core/logs/sessions"
if [ -d "$SESSION_DIR" ]; then
    # Count existing sessions
    SESSION_COUNT=$(find "$SESSION_DIR" -name "practice_*.json" | wc -l)
    
    if [ "$SESSION_COUNT" -gt 0 ]; then
        print_status "Found $SESSION_COUNT session files to clean"
        
        # Remove practice session files
        rm -f "$SESSION_DIR"/practice_*.json
        print_status "✅ Removed practice session files"
        
        # Remove active sessions file
        if [ -f "$SESSION_DIR/active_sessions.json" ]; then
            rm "$SESSION_DIR/active_sessions.json"
            print_status "✅ Removed active sessions file"
        fi
        
        # Remove any backup files
        rm -f "$SESSION_DIR"/*.backup
        rm -f "$SESSION_DIR"/*.bak
        
    else
        print_status "No session files found to clean"
    fi
else
    print_status "Session directory doesn't exist (creating empty directory)"
    mkdir -p "$SESSION_DIR"
fi

# Clean up log files
print_status "Cleaning log files..."

LOG_DIR="logs"
if [ -d "$LOG_DIR" ]; then
    # Clean application logs
    if [ -f "$LOG_DIR/application.log" ]; then
        size=$(du -h "$LOG_DIR/application.log" | cut -f1)
        print_status "Found application.log ($size)"
        
        # Keep only last 100 lines
        tail -100 "$LOG_DIR/application.log" > "$LOG_DIR/application.log.tmp"
        mv "$LOG_DIR/application.log.tmp" "$LOG_DIR/application.log"
        print_status "✅ Truncated application.log (kept last 100 lines)"
    fi
    
    # Clean any other log files
    find "$LOG_DIR" -name "*.log" -size +10M -exec truncate -s 1M {} \; 2>/dev/null || true
    print_status "✅ Cleaned large log files"
fi

# Clean up temporary files
print_status "Cleaning temporary files..."
rm -f *.tmp 2>/dev/null || true
rm -f *.temp 2>/dev/null || true
rm -f .DS_Store 2>/dev/null || true
print_status "✅ Cleaned temporary files"

# Clean up Python cache
print_status "Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
print_status "✅ Cleaned Python cache"

# Show directory sizes after cleanup
print_status "Checking directory sizes after cleanup..."
if [ -d "$SESSION_DIR" ]; then
    SESSION_SIZE=$(du -sh "$SESSION_DIR" 2>/dev/null | cut -f1 || echo "0B")
    print_status "Session directory size: $SESSION_SIZE"
fi

if [ -d "$LOG_DIR" ]; then
    LOG_SIZE=$(du -sh "$LOG_DIR" 2>/dev/null | cut -f1 || echo "0B")
    print_status "Log directory size: $LOG_SIZE"
fi

# Summary
echo ""
echo -e "${GREEN}✅ CLEANUP COMPLETED SUCCESSFULLY!${NC}"
echo ""
print_status "Summary:"
echo "  • Stopped Sec360 processes"
echo "  • Cleaned all session files"
echo "  • Truncated log files"
echo "  • Removed temporary files"
echo "  • Cleaned Python cache"

echo ""
print_status "You can now start Sec360 with: ./scripts/management/start.sh"

echo ""
echo -e "${YELLOW}💡 TIP:${NC} Run this script weekly to keep your Sec360 installation clean and performant."

exit 0
