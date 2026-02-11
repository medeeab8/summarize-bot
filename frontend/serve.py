import http.server
import socketserver
from pathlib import Path

PORT = 5173

class FrontendHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), FrontendHandler) as httpd:
        print(f"Serving frontend at http://localhost:{PORT}")
        httpd.serve_forever()
