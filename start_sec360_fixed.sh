#!/bin/bash
# Sec360 macOS Display Fix Script

echo "🍎 Applying macOS Display Fixes for Sec360..."

# Set environment variables for proper display
export TK_SILENCE_DEPRECATION=1
export PYTHONPATH="${PYTHONPATH}:$(pwd)/core"

# Force proper display scaling
export QT_AUTO_SCREEN_SCALE_FACTOR=1
export QT_SCALE_FACTOR=1

# Disable Retina scaling issues
export TK_USE_DEFAULT_THEME=1

echo "✅ Environment variables set"
echo "🚀 Starting Sec360 with display fixes..."

# Start Sec360 with fixes
python3 sec360.py
