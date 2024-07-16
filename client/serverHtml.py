import http.server
import socketserver

PORT = 8000
DIRECTORY = "."

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ["/StreamTranscription", "/StreamTranscription/"]:
            self.path = "index.html"
        return super().do_GET()

    def translate_path(self, path):
        # Adjust the path to serve files from the DIRECTORY
        path = super().translate_path(path)
        return path.replace("/StreamTranscription", DIRECTORY, 1)

with socketserver.TCPServer(("", PORT), MyHttpRequestHandler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
