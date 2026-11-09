"""Send news evidence to AIHOT's authenticated ingestion endpoint.

Reviews and issues retain their independent identity in the observation store.
The default command only previews counts; --send enables the local bridge.
"""
import argparse
import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from collect import ROOT, atomic, stamp


def batches(events):
    sources = defaultdict(list)
    for event in events:
        if event.get('category') not in ('news_lead', 'release'):
            continue
        url = urlsplit(str(event.get('url') or ''))
        if url.scheme not in ('http', 'https') or not url.hostname or url.username or url.password:
            continue
        if not event.get('source_id') or not str(event.get('title') or '').strip():
            continue
        classification = event.get('classification')
        sources[event['source_id']].append({
            'title': event['title'],
            'url': event['url'],
            'publishedAt': stamp(event.get('published_at')),
            'raw': {
                '_aihot': {'baseline': classification == '首次采集基线', 'backfill': classification == '历史补录'},
                'observation': {key: event.get(key) for key in ('id', 'product', 'category', 'excerpt', 'first_seen', 'source_updated_at', 'verification')},
            },
        })
    for source_id, items in sources.items():
        for offset in range(0, len(items), 50):
            yield {'sourceId': source_id, 'sourceName': source_id, 'items': items[offset:offset + 50]}


def fingerprint(item):
    return hashlib.sha256(json.dumps(item, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def sync(events, base, token, state_path):
    target = urlsplit(base)
    if target.scheme not in ('http', 'https') or not target.hostname or target.username or target.password or target.query or target.fragment:
        raise ValueError('AIHOT_API_BASE must be an HTTP(S) origin without credentials or query parameters')
    if target.scheme == 'http' and target.hostname not in ('127.0.0.1', 'localhost', '::1', 'api'):
        raise ValueError('Use HTTPS for a remote AIHOT endpoint')
    if len(token) < 16:
        raise ValueError('INGEST_TOKEN must contain at least 16 characters')
    state_path = Path(state_path)
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    # A different destination must receive its own complete synchronization.
    destination = base.rstrip('/')
    saved = state.get(destination, {})
    sent = created = 0
    for batch in batches(events):
        pending = [item for item in batch['items'] if saved.get(item['raw']['observation']['id']) != fingerprint(item)]
        if not pending:
            continue
        body = dict(batch, items=pending)
        request = Request(destination + '/api/ingest/items', data=json.dumps(body, ensure_ascii=False).encode(), method='POST', headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
        with urlopen(request, timeout=45) as response:
            result = json.load(response)
        if result.get('ok') is not True or not isinstance(result.get('created'), int):
            raise RuntimeError('AIHOT did not acknowledge this batch')
        for item in pending:
            saved[item['raw']['observation']['id']] = fingerprint(item)
        state[destination] = saved
        atomic(state_path, json.dumps(state, ensure_ascii=False))
        sent += len(pending)
        created += result['created']
    return {'sent': sent, 'created': created}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--send', action='store_true')
    args = parser.parse_args()
    data = json.loads((ROOT / 'outputs/monitor-data.json').read_text())
    if not args.send:
        payloads = list(batches(data['events']))
        print(json.dumps({'mode': 'preview', 'batches': len(payloads), 'items': sum(len(batch['items']) for batch in payloads)}))
        return
    result = sync(data['events'], os.environ.get('AIHOT_API_BASE', 'http://127.0.0.1:3001'), os.environ.get('INGEST_TOKEN', ''), ROOT / 'data/aihot-sync.json')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
