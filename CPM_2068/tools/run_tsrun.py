"""Serve a CP/M TSRun page and read-only emulator/assets on localhost."""
import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote,urlsplit

ROOT=Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
    extensions_map={**SimpleHTTPRequestHandler.extensions_map,'.mjs':'text/javascript','.js':'text/javascript'}
    def do_GET(self):
        if urlsplit(self.path).path=='/config.json':
            data=json.dumps({'disk':self.server.disk.name,'cartridge':self.server.cartridge.name}).encode()
            self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
        super().do_GET()

    def translate_path(self,path):
        path=unquote(urlsplit(path).path)
        fixed={'/media/disk.dsk':self.server.disk,'/media/cpm.dck':self.server.cartridge}
        if path in fixed:return str(fixed[path])
        if path.startswith('/tsrun/'):
            base=self.server.tsrun;relative=path[len('/tsrun/'):]
            # Only runtime JS and the two explicitly selected ROMs are exposed.
            if relative not in ('roms/ts2068-0.rom','roms/ts2068-1.rom') and (not relative.endswith('.js') or '/' in relative):return str(ROOT/'web/tsrun/not-found')
        else:
            base=ROOT/'web/tsrun';relative=path.lstrip('/') or 'index.html'
        target=(base/relative).resolve()
        if not target.is_relative_to(base.resolve()):return str(ROOT/'web/tsrun/not-found')
        return str(target)

    def list_directory(self,path):
        self.send_error(404);return None

    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        super().end_headers()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tsrun',type=Path,default=ROOT/'../../TSRun')
    parser.add_argument('--disk',type=Path,default=ROOT/'build/infocom-cpm.dsk')
    parser.add_argument('--cartridge',type=Path,default=ROOT/'build/infocom-cpm.dck')
    parser.add_argument('--port',type=int,default=8770)
    args=parser.parse_args()
    for path in (args.disk,args.cartridge,args.tsrun/'machine.js',args.tsrun/'roms/ts2068-0.rom',args.tsrun/'roms/ts2068-1.rom'):
        if not path.is_file():parser.error('missing '+str(path))
    with ThreadingHTTPServer(('127.0.0.1',args.port),partial(Handler,directory=str(ROOT/'web/tsrun'))) as server:
        server.tsrun=args.tsrun.resolve();server.disk=args.disk.resolve();server.cartridge=args.cartridge.resolve()
        print(f'CP/M on TSRun: http://127.0.0.1:{args.port}/',flush=True)
        print('Disk edits stay in the browser. Download DSK or TAP before closing; source files are read-only.',flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass


if __name__=='__main__':main()
