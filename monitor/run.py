#!/usr/bin/env python3
"""Run collection and authenticated AIHOT synchronization on a fixed interval."""
import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from collect import ROOT, TZ, atomic
from sync_aihot import sync

def run_once(collect=True):
    with (ROOT/'data/observation-run.lock').open('w') as lock:
        try:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            return {'status':'skipped','reason':'another observation update is running'}
        result={'started_at':datetime.now(TZ).isoformat()}
        try:
            if collect:
                command=[sys.executable,str(ROOT/'monitor/collect.py')]
            else:
                command=[sys.executable,str(ROOT/'work/ui-prototype/build.py')]
            subprocess.run(command,cwd=ROOT,check=True,timeout=360)
            data=json.loads((ROOT/'outputs/monitor-data.json').read_text())
            result['collection']={'sources':len(data['source_status']),'errors':sum(s['status']=='error' for s in data['source_status'])}
            if os.environ.get('INGEST_TOKEN'):
                result['sync']=sync(data['events'],os.environ.get('AIHOT_API_BASE','http://127.0.0.1:3001'),os.environ['INGEST_TOKEN'],ROOT/'data/aihot-sync.json')
            else:
                result['sync']={'status':'not_configured'}
            result['status']='ok'
        except Exception as error:
            result.update(status='error',error=type(error).__name__)
        result['finished_at']=datetime.now(TZ).isoformat()
        atomic(ROOT/'data/observation-run.json',json.dumps(result,ensure_ascii=False,indent=2))
        return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--once',action='store_true')
    parser.add_argument('--no-collect',action='store_true')
    parser.add_argument('--interval',type=int,default=3600)
    args=parser.parse_args()
    if args.interval<300:parser.error('interval must be at least 300 seconds')
    while True:
        result=run_once(not args.no_collect)
        print(json.dumps(result,ensure_ascii=False),flush=True)
        if args.once:return 1 if result['status']=='error' else 0
        time.sleep(args.interval)

if __name__=='__main__':sys.exit(main())
