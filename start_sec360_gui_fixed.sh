#!/bin/bash
# Sec360 GUI Fix Script

echo "🔧 Applying Sec360 GUI fixes..."

# Set environment variables
export TK_SILENCE_DEPRECATION=1
export PYTHONPATH="${PYTHONPATH}:$(pwd)/core"

# Force proper display scaling
export QT_AUTO_SCREEN_SCALE_FACTOR=1
export QT_SCALE_FACTOR=1

echo "✅ Environment variables set"
echo "🚀 Starting Sec360 with GUI fixes..."

# Start with forced GUI refresh
python3 -c "
import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'
import sys
sys.path.append('core')
import sec360
app = sec360.Sec360App()
# Force GUI refresh
app.root.update()
app.root.lift()
app.run()
"
