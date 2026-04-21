from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "online",
            "message": "OddsForge Bot API is reachable. Note: The trading bot itself should be run as a long-running process on a VPS or Docker host, not as a serverless function.",
            "bot_version": "1.0.0"
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
