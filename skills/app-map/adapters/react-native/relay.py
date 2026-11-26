"""Host relay between the screenshot driver and the app's JS helper (appMapShots.js).

The driver (XCUITest or the Android instrumented test) takes a screenshot, then calls
`GET /snap?id=<shot>`; the relay queues the request, the helper (polling `GET /poll`) measures the
map's components and posts `SHOT RECT` lines to `POST /rects?id=<shot>`, and the relay returns
them to the driver, which logs them like its own. Usage: relay.py <map dir> [--port 8765]
"""
import json
import os
import queue
import re
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PENDING = queue.Queue()
RESULTS = {}
DONE = threading.Condition()


def map_classes(map_dir):
    """Every box name in the map's diagrams: what the helper measures."""
    names = set()
    for name in os.listdir(map_dir):
        if name.endswith('.md'):
            with open(os.path.join(map_dir, name), encoding='utf-8') as handle:
                for block in re.findall(r'```mermaid\n(.*?)```', handle.read(), re.S):
                    names.update(re.findall(r'^\s*class (\w+)', block, re.M))
                    names.update(re.findall(r'participant \w+ as (\w+)', block))
    return sorted(names)


class Handler(BaseHTTPRequestHandler):
    names = []

    def log_message(self, *args):
        pass

    def _send(self, status, body=b'', kind='text/plain'):
        self.send_response(status)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)
        if url.path == '/poll':
            try:
                shot = PENDING.get(timeout=5)
            except queue.Empty:
                return self._send(204)
            return self._send(200, json.dumps({'id': shot, 'names': self.names}).encode(), 'application/json')
        if url.path == '/snap':
            shot = query.get('id', [''])[0]
            with DONE:
                RESULTS.pop(shot, None)
            PENDING.put(shot)
            with DONE:
                DONE.wait_for(lambda: shot in RESULTS, timeout=15)
                lines = RESULTS.pop(shot, None)
            if lines is None:
                print(f'relay: no answer from the app for {shot} (is the debug build running?)', flush=True)
                return self._send(504)
            rects = [item for item in lines.splitlines() if item.startswith('SHOT RECT ')]
            seen = [item for item in lines.splitlines() if item.startswith('SHOT SEEN ')]
            print(f'relay: {shot}: {len(rects)} components', flush=True)
            for item in seen:
                print('relay: ' + item, flush=True)
            return self._send(200, '\n'.join(rects).encode())
        return self._send(404)

    def do_POST(self):
        url = urlparse(self.path)
        if url.path == '/rects':
            shot = parse_qs(url.query).get('id', [''])[0]
            length = int(self.headers.get('Content-Length') or 0)
            body = self.rfile.read(length).decode('utf-8', errors='replace')
            with DONE:
                RESULTS[shot] = body
                DONE.notify_all()
            return self._send(200)
        return self._send(404)


def main():
    args = sys.argv[1:]
    port = 8765
    if '--port' in args:
        at = args.index('--port')
        port = int(args[at + 1])
        del args[at:at + 2]
    if not args:
        sys.exit(__doc__)
    Handler.names = map_classes(args[0])
    print(f'relay: listening on {port}, {len(Handler.names)} classes from the map', flush=True)
    ThreadingHTTPServer(('0.0.0.0', port), Handler).serve_forever()


if __name__ == '__main__':
    main()
