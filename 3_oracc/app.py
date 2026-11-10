#!/usr/bin/env python3
"""Local-only interface for unified Oracc/eBL input → lemma resolution → KWIC."""
from __future__ import annotations
import argparse
import csv
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import StringIO
import json
from pathlib import Path
import sys
import subprocess
import re
import webbrowser
from urllib.parse import urlparse
from resolver_core import Resolver, ROOT, DATA, init_index


def make_handler(resolver):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            print('%s - %s' % (self.address_string(), format % args), flush=True)

        def send_json(self, value, status=200):
            raw=json.dumps(value,ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length',str(len(raw)))
            self.send_header('Cache-Control','no-store')
            self.end_headers()
            self.wfile.write(raw)

        def send_csv(self, text, filename):
            raw=('\ufeff'+text).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type','text/csv; charset=utf-8')
            self.send_header('Content-Disposition','attachment; filename="'+filename+'"')
            self.send_header('Content-Length',str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            path=urlparse(self.path).path
            if path=='/':
                raw=(ROOT/'index.html').read_bytes()
                self.send_response(200)
                self.send_header('Content-Type','text/html; charset=utf-8')
                self.send_header('Content-Length',str(len(raw)))
                self.send_header('Cache-Control','no-store')
                self.end_headers()
                self.wfile.write(raw)
            elif path=='/api/health':
                dictionary=resolver._dictionary()
                self.send_json({'status':'ok' if dictionary else 'dictionary-error',
                                'version':'v045-lookup-verified',
                                'dictionary_entries':len(dictionary.entries) if dictionary else 0,
                                'dictionary_error':resolver.dictionary_error if not dictionary else ''})
            else:
                self.send_error(404,'Not found')

        def do_POST(self):
            path=urlparse(self.path).path
            if path=='/api/save-csv':
                # On macOS show the system's Save dialog so the user chooses
                # an output folder. Else the browser's download handling applies.
                if sys.platform!='darwin':
                    return self.send_json({'browser_download':True})
                size=int(self.headers.get('Content-Length','0'))
                if size<1 or size>35000000:
                    return self.send_json({'error':'Invalid CSV size.'},400)
                filename=self.headers.get('X-Filename','oracc_ebl_results.csv')
                if not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}\.csv',filename):
                    return self.send_json({'error':'Invalid CSV filename.'},400)
                content=self.rfile.read(size)
                try:
                    # AppleScript file chooser; filename is strictly sanitized.
                    script='set chosenFile to choose file name with prompt "Save CSV results" default name "'+filename+'"'
                    run=subprocess.run(['osascript','-e',script,'-e','POSIX path of chosenFile'],
                            capture_output=True,text=True,timeout=300,check=False)
                    if run.returncode:
                        if '-128' in run.stderr or 'User canceled' in run.stderr:
                            return self.send_json({'cancelled':True})
                        return self.send_json({'browser_download':True})
                    destination=Path(run.stdout.strip())
                    destination.write_bytes(content)
                    return self.send_json({'saved':True})
                except (OSError,subprocess.TimeoutExpired):
                    return self.send_json({'browser_download':True})
            if path not in ('/api/candidates','/api/identify','/api/resolve','/api/search','/api/export','/api/text-id','/api/export-text-id','/api/suggestions','/api/online-word'):
                return self.send_error(404,'Not found')
            try:
                length=int(self.headers.get('Content-Length','0'))
                if length<2 or length>80000:
                    return self.send_json({'error':'Invalid request size.'},400)
                data=json.loads(self.rfile.read(length))
                if not isinstance(data,dict):
                    return self.send_json({'error':'JSON object required.'},400)
                if path=='/api/text-id':
                    result=resolver.text_id(data.get('text_id',''),data.get('project'))
                elif path=='/api/export-text-id':
                    text=resolver.text_id(data.get('text_id',''),data.get('project'))
                    if text.get('selection_required'):
                        raise ValueError('Choose the Oracc project before downloading.')
                    if text.get('error'):
                        raise ValueError(text['error'])
                    sio=StringIO(newline='')
                    writer=csv.writer(sio)
                    writer.writerow(['text_id','project','line','position','written_form','oracc_lemma','ebl_entries','mapping_status'])
                    for line in text['lines']:
                        for pos,word in enumerate(line['words'],1):
                            writer.writerow([text['text_id'],text['project'],line['line'],pos,word['form'],word['oracc'],
                                             ' | '.join(word['ebl']),word['status']])
                    return self.send_csv(sio.getvalue(), 'oracc_ebl_text_'+text['text_id']+'.csv')
                elif path=='/api/online-word':
                    result=resolver.online_dictionary_fallback(data.get('lemma',''))
                elif path=='/api/suggestions':
                    result=resolver.suggestions(data.get('ids',[]))
                elif path=='/api/candidates':
                    result={'queries':resolver.identify_unified(data.get('terms',[]))}
                elif path=='/api/identify':
                    result={'queries':resolver.identify(data.get('mode'), data.get('terms',[]))}
                elif path=='/api/resolve':
                    result=resolver.resolve(data.get('queries',[]))
                elif path=='/api/search':
                    result=resolver.search(data.get('queries',[]),data.get('context'),
                                           min(int(data.get('limit',300)),1000),int(data.get('offset',0)),
                                           data.get('source_scope','both'),source_offsets=data.get('source_offsets'))
                else:
                    result=resolver.search(data.get('queries',[]),data.get('context'),limit=10000,
                                           source_scope=data.get('source_scope','both'),
                                           source_offsets={'oracc':0,'ebl_korpus':0,'ebl_korpus_manuskripte':0})
                    sio=StringIO(newline='')
                    writer=csv.writer(sio)
                    keys=['source','text','line','manuscript','manuscript_line','period','full_line','keyword','highlighted_terms','source_url']
                    writer.writerow(keys)
                    for record in result['results']:
                        writer.writerow([(' '.join(w.get('form','') for w in record['words']) if k=='full_line' else ' | '.join(w.get('form','') for w in record['words'] if w.get('groups')) if k=='highlighted_terms' else record.get(k,'')) for k in keys])
                    raw=('\ufeff'+sio.getvalue()).encode('utf-8')
                    self.send_response(200)
                    self.send_header('Content-Type','text/csv; charset=utf-8')
                    self.send_header('Content-Disposition','attachment; filename="lemma_kwic_results.csv"')
                    self.send_header('X-Export-Truncated',
                        'true' if any(n > 10000 for n in result['source_kwic_counts'].values()) else 'false')
                    self.send_header('Content-Length',str(len(raw)))
                    self.end_headers()
                    self.wfile.write(raw)
                    return
                self.send_json(result)
            except (ValueError,KeyError,TypeError) as exc:
                self.send_json({'error':str(exc)},400)
            except Exception as exc:
                print('Request error:',repr(exc),file=sys.stderr,flush=True)
                self.send_json({'error':'The requested operation failed; check the Terminal log.'},500)
    return Handler


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port',type=int,default=8766)
    p.add_argument('--no-open',action='store_true')
    args=p.parse_args(argv)
    resolver=Resolver()
    dictionary=resolver._dictionary()
    if dictionary is None:
        raise SystemExit('eBL Dictionary loading failed: '
                         + str(DATA / "ebl_woerterbuch.jsonl.gz") + '\n'
                         + (resolver.dictionary_error or 'Missing or invalid data file.')
                         + '\nCheck the four files in digitale-methode/daten/.')
    print(f'eBL Dictionary ready: {len(dictionary.entries):,} entries',flush=True)
    init_index(progress=lambda m:print(m,flush=True))
    try:
        server=ThreadingHTTPServer(('127.0.0.1',args.port),make_handler(resolver))
    except OSError as exc:
        # Another version can still be listening on 8766. Do not silently open
        # that old version or exit: select an unused loopback port instead.
        if getattr(exc,'errno',None) not in (48,98,10048):
            raise
        print(f'Port {args.port} is already occupied; using another local port.',flush=True)
        server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(resolver))
    url=f'http://127.0.0.1:{server.server_port}/'
    print('Oracc → eBL → KWIC: '+url,flush=True)
    if not args.no_open:
        webbrowser.open_new_tab(url + '?build=v045-lookup-verified')
    try:
        server.serve_forever(poll_interval=.2)
    except KeyboardInterrupt:
        print('\nStopped.')
    finally:
        server.server_close()

if __name__=='__main__':
    main()
