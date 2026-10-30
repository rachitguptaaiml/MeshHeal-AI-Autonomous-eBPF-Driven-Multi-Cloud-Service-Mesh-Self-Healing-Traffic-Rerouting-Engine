from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os

AUDIT_LOG_PATH = "audit_log.json"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        if os.path.exists(AUDIT_LOG_PATH):
            entries = []
            with open(AUDIT_LOG_PATH) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
            self.wfile.write(json.dumps(entries).encode())
        else:
            self.wfile.write(b"[]")

    def log_message(self, *args):
        pass  # silence logs

if __name__ == "__main__":
    print("Audit server running on http://localhost:5001/audit")
    HTTPServer(("localhost", 5001), Handler).serve_forever()