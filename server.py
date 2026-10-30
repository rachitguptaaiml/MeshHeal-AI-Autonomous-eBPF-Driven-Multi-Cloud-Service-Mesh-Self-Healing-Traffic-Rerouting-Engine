from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ['/pay', '/pay.html', '/']:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            with open('pay.html', 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            req = urllib.request.Request(
                f'http://localhost:8080{self.path}',
                data=body,
                headers={'Content-Type': 'application/json'}
            )
            resp = urllib.request.urlopen(req)
            data = resp.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, ngrok-skip-browser-warning')
        self.end_headers()

    def log_message(self, *args): pass

if __name__ == '__main__':
    print('Server on http://localhost:8081')
    print('Phone: http://192.168.1.39:8081/pay')
    HTTPServer(('0.0.0.0', 8081), Handler).serve_forever()