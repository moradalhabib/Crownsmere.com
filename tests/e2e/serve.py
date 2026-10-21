#!/usr/bin/env python3
"""Local Crownsmere QA server.

The production HTML includes Content-Security-Policy: upgrade-insecure-requests.
WebKit upgrades localhost HTTP CSS/JS requests when it sees that production-only
directive, leaving test pages unstyled. Strip only this directive when serving
test HTML on localhost. The committed published HTML is never changed.
"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path.cwd().resolve()


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = unquote(urlsplit(self.path).path)
        if path == "/" or path.endswith("/"):
            path += "index.html"
        if path.endswith(".html"):
            resolved = (ROOT / path.lstrip("/")).resolve()
            if resolved != ROOT and ROOT in resolved.parents and resolved.is_file():
                content = resolved.read_bytes().replace(b"upgrade-insecure-requests", b"")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
        super().do_GET()


if __name__ == "__main__":
    print("Crownsmere QA HTTP server:127.0.0.1:8765", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
