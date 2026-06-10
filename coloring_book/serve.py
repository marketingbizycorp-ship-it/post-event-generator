#!/usr/bin/env python3
"""Serve the K-Pop Demon Hunters coloring book on localhost.

Builds the pages if they're missing, then starts a tiny local web server
(standard library only) and opens the book in your browser.

Usage:
    python coloring_book/serve.py                # http://localhost:8000
    python coloring_book/serve.py --port 9000    # pick a port
    python coloring_book/serve.py --no-browser   # don't auto-open
"""

from __future__ import annotations

import argparse
import http.server
import os
import socketserver
import threading
import webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))


def _ensure_built():
    """Build the book the first time (or if pages are missing)."""
    book = os.path.join(HERE, "coloring-book.html")
    pages = os.path.join(HERE, "pages")
    if os.path.exists(book) and os.path.isdir(pages) and os.listdir(pages):
        return
    import generate  # local module, same directory
    print("Pages not found — building them first...")
    generate.build()


class Handler(http.server.SimpleHTTPRequestHandler):
    """Serve from the coloring_book directory; default to the index page."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=HERE, **kwargs)

    # Quieter logging.
    def log_message(self, fmt, *args):
        pass


def main():
    ap = argparse.ArgumentParser(description="Serve the coloring book locally.")
    ap.add_argument("--port", type=int, default=8000, help="port (default 8000)")
    ap.add_argument("--no-browser", action="store_true",
                    help="don't open a browser automatically")
    args = ap.parse_args()

    _ensure_built()

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", args.port), Handler) as httpd:
        url = f"http://localhost:{args.port}/index.html"
        print(f"\n  K-Pop Demon Hunters coloring book is live!")
        print(f"  ➜  {url}")
        print(f"  ➜  full printable book: http://localhost:{args.port}/coloring-book.html")
        print(f"\n  Press Ctrl+C to stop.\n")
        if not args.no_browser:
            threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Stopped. Bye!")


if __name__ == "__main__":
    main()
