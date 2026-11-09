"""Adapt collected evidence for the observation website without inventing summaries."""
from urllib.parse import urlsplit
from collect import stamp


def news_records(data, names):
    records = []
    for record in data.get('events', []):
        if record.get('category') not in ('news_lead', 'release'):
            continue
        if record.get('product') not in names:
            continue
        url = urlsplit(str(record.get('url') or ''))
        if url.scheme not in ('http', 'https') or not url.hostname or url.username or url.password:
            continue
        entry = dict(record)
        title = str(entry.get('title') or '').strip()
        if not title:
            continue
        parts = title.rsplit(' - ', 1)
        official = entry['category'] == 'release'
        publisher = names[entry['product']] if official else parts[-1] if len(parts) == 2 else '新闻检索来源'
        official_lead = not official and publisher == 'OpenAI'
        entry.update(
            published_at=stamp(entry.get('published_at')),
            publisher=publisher + ('（RSS 署名）' if official_lead else ''),
            kind='official' if official else 'official-lead' if official_lead else 'media',
            sourceLabel='官方发布' if official else '官方署名待核验' if official_lead else '媒体报道',
            topic='版本更新' if official else '产品相关报道',
            title=title if official else parts[0],
            preview=(str(entry.get('excerpt') or '')[:220] + ('…' if len(str(entry.get('excerpt') or '')) > 220 else '')) if official else '已收录发布标题。正文待核验，可查看采集证据或前往来源阅读。',
        )
        records.append(entry)
    return sorted(records, key=lambda entry: (entry.get('published_at') or '', entry['id']), reverse=True)
