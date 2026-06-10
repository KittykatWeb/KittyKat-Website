import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from http.server import BaseHTTPRequestHandler

from compiler import compile_route
from config import CSS_FILE, SOURCE_FILE, STYLES_DIR


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]

        if path.startswith("/api"):
            path = path[4:] or "/"

        css_path = f"/{STYLES_DIR}/{CSS_FILE}"
        if path == css_path:
            try:
                _, compiled = compile_route(SOURCE_FILE, "/")
                body = compiled["stylesheet"]
                content_type = "text/css"
            except FileNotFoundError:
                self.send_error(404, "site.kkat not found")
                return
        else:
            try:
                body, _ = compile_route(SOURCE_FILE, path)
                content_type = "text/html"
            except FileNotFoundError:
                self.send_error(404, "site.kkat not found")
                return
            except ValueError as error:
                self.send_error(500, str(error))
                return

            if body is None:
                self.send_error(404, "Page not found")
                return

        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
