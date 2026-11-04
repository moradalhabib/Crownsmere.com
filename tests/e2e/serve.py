#!/usr/bin/env python3
"""Local Crownsmere QA server.

The production HTML includes Content-Security-Policy: upgrade-insecure-requests.
WebKit upgrades localhost HTTP CSS/JS requests when it sees that production-only
directive, leaving test pages unstyled. Strip only this directive when serving
test HTML on localhost. The committed published HTML is never changed.
"""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path.cwd().resolve()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Both HTML and static assets must come from the selected QA root.
        # SimpleHTTPRequestHandler otherwise defaults to the process cwd.
        super().__init__(*args, directory=str(ROOT), **kwargs)

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
    parser = argparse.ArgumentParser(description="Local-only Crownsmere E2E server")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--root", default=".", help="Working directory to serve; defaults to current project")
    args = parser.parse_args()
    ROOT = Path(args.root).resolve()
    if not ROOT.is_dir():
        parser.error("Site root directory does not exist")
    # Full production CSP is kept in GitHub; this HTTP test server strips only the
    # upgrade directive, which would otherwise force Safari to request HTTPS
    # assets from an HTTP-only local server.
    print(f"Crownsmere QA HTTP server:127.0.0.1:{args.port} root={ROOT}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
