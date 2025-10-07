#!/usr/bin/env python3
"""
Sec360 Web Interface - Alternative to Tkinter for Mac display issues
"""

import os
import sys
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

# Add core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

class Sec360WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Sec360 by Abhay - Web Interface</title>
                <style>
                    body { 
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: #1a1a1a; 
                        color: white; 
                        margin: 0; 
                        padding: 20px;
                    }
                    .container { max-width: 1200px; margin: 0 auto; }
                    .header { text-align: center; margin-bottom: 30px; }
                    .title { font-size: 2.5em; color: #4CAF50; margin-bottom: 10px; }
                    .subtitle { font-size: 1.2em; color: #ccc; }
                    .status { background: #2a2a2a; padding: 20px; border-radius: 8px; margin: 20px 0; }
                    .success { color: #4CAF50; }
                    .info { color: #2196F3; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 class="title">🛡️ Sec360 by Abhay</h1>
                        <p class="subtitle">Advanced Code Security Analysis Platform</p>
                    </div>
                    
                    <div class="status">
                        <h2>✅ System Status</h2>
                        <p class="success">• Sec360 Web Interface: Running</p>
                        <p class="success">• Python Backend: Active</p>
                        <p class="info">• Port: 8080</p>
                        <p class="info">• Platform: macOS (M4 Optimized)</p>
                    </div>
                    
                    <div class="status">
                        <h2>🎯 Features Available</h2>
                        <p>• Real-time code analysis with AI</p>
                        <p>• Security mentoring and risk scoring</p>
                        <p>• Practice sessions and compliance checking</p>
                        <p>• Cross-platform compatibility</p>
                    </div>
                    
                    <div class="status">
                        <h2>📝 Note</h2>
                        <p>This web interface is an alternative to the Tkinter GUI due to macOS display compatibility issues.</p>
                        <p>The full functionality is available through the command line interface.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_web_interface():
    """Start the web interface server"""
    server = HTTPServer(('localhost', 8080), Sec360WebHandler)
    print("🌐 Starting Sec360 Web Interface...")
    print("📱 Open your browser to: http://localhost:8080")
    print("🛑 Press Ctrl+C to stop")
    
    # Open browser automatically
    threading.Timer(1.0, lambda: webbrowser.open('http://localhost:8080')).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Web interface stopped")
        server.shutdown()

if __name__ == "__main__":
    start_web_interface()
