"""Serve this demo and the existing local TSRun checkout without copying it."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote,urlsplit
ROOT=Path(__file__).resolve().parents[1]
TSRUN=ROOT.parents[1]/'TSRun'
class Handler(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        name=unquote(urlsplit(path).path)
        base=TSRUN if name.startswith('/tsrun/') else ROOT
        rel=name[7:] if name.startswith('/tsrun/') else name.lstrip('/')
        target=(base/rel).resolve()
        if not target.is_relative_to(base.resolve()):return str(ROOT/'missing')
        return str(target)
    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        super().end_headers()
print('Sinistar cartridge demo: http://127.0.0.1:8768/web/',flush=True)
ThreadingHTTPServer(('127.0.0.1',8768),Handler).serve_forever()
