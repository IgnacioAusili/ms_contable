import argparse
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


PAGE = Path(__file__).with_name("bootstrap-page.html").read_text(encoding="utf-8")

BRAND_LOGO = Path(__file__).resolve().parent.parent / "static" / "images" / "logo-160.svg"


def write_port(path, port):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(str(port), encoding="ascii")
    os.replace(temporary, path)


def read_state(path):
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(state, dict):
            return state
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        pass
    return {
        "state": "starting",
        "title": "Preparando el programa",
        "message": "La aplicación se abrirá en unos instantes.",
    }


class BootstrapServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def run_server(state_path, port_path, opened_path):
    terminal_response = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def send_content(self, status, content_type, content):
            encoded = content.encode("utf-8") if isinstance(content, str) else content
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store, max-age=0")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(encoded)

        def do_GET(self):
            if self.headers.get("Host") != f"127.0.0.1:{self.server.server_port}":
                self.send_content(403, "text/plain; charset=utf-8", "Acceso local únicamente.")
                return

            path = urlsplit(self.path).path
            if path == "/":
                self.send_content(200, "text/html; charset=utf-8", PAGE)
                opened_path.write_text("opened", encoding="ascii")
                return
            if path == "/brand.svg":
                try:
                    logo = BRAND_LOGO.read_bytes()
                except OSError:
                    self.send_content(404, "text/plain; charset=utf-8", "No encontrado.")
                    return
                self.send_content(200, "image/svg+xml", logo)
                return
            if path == "/status":
                state = read_state(state_path)
                self.send_content(
                    200,
                    "application/json; charset=utf-8",
                    json.dumps(state, ensure_ascii=False, separators=(",", ":")),
                )
                if state.get("state") in {"ready", "error"} and not terminal_response.is_set():
                    terminal_response.set()
                    threading.Timer(0.35, self.server.shutdown).start()
                return
            if path == "/favicon.ico":
                self.send_response(204)
                self.end_headers()
                return
            self.send_content(404, "text/plain; charset=utf-8", "No encontrado.")

        def log_message(self, format_string, *args):
            return

    server = BootstrapServer(("127.0.0.1", 0), Handler)
    write_port(port_path, server.server_port)
    timeout = threading.Timer(240, server.shutdown)
    timeout.daemon = True
    timeout.start()
    try:
        server.serve_forever(poll_interval=0.2)
    finally:
        timeout.cancel()
        server.server_close()
        for path in (state_path, port_path, opened_path):
            try:
                path.unlink()
            except FileNotFoundError:
                pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-file", required=True, type=Path)
    parser.add_argument("--port-file", required=True, type=Path)
    parser.add_argument("--opened-file", required=True, type=Path)
    arguments = parser.parse_args()
    run_server(
        arguments.state_file.resolve(),
        arguments.port_file.resolve(),
        arguments.opened_file.resolve(),
    )


if __name__ == "__main__":
    main()
