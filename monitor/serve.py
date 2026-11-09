#!/usr/bin/env python3
"""Read-only loopback API and artifact preview; no collection via HTTP."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit,unquote,parse_qs
import argparse,json,mimetypes
ROOT=Path(__file__).resolve().parents[1]
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  route=urlsplit(self.path);path=unquote(route.path)
  if path=='/':
   self.send_response(302);self.send_header('Location','/outputs/competitor-research-complete.html');self.end_headers();return
  if path in ['/api/status','/api/events','/api/reports']:
   file=ROOT/'outputs/monitor-data.json'
   if not file.exists():self.send_error(503,'Run collector first');return
   data=json.loads(file.read_text())
   if path=='/api/status':value={k:data[k] for k in ['generated_at','mode','source_status']}
   elif path=='/api/reports':value=data['archives']
   else:
    value=data['events'];query=parse_qs(route.query)
    for key in ['product','category']:
     if key in query:value=[x for x in value if x.get(key)==query[key][0]]
   self.reply(json.dumps(value,ensure_ascii=False).encode(),'application/json; charset=utf-8');return
  candidate=(ROOT/path.lstrip('/')).resolve()
  if not any(candidate.is_relative_to(ROOT/folder) for folder in ['outputs','reports']):self.send_error(403);return
  if not candidate.is_file() or candidate.suffix not in ['.html','.json','.md'] :self.send_error(404);return
  self.reply(candidate.read_bytes(),(mimetypes.guess_type(str(candidate))[0] or 'text/plain')+'; charset=utf-8')
 def reply(self,body,content_type):
  self.send_response(200);self.send_header('Content-Type',content_type);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(body)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8765);args=parser.parse_args()
 print(f'Local preview: http://127.0.0.1:{args.port}',flush=True)
 ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
