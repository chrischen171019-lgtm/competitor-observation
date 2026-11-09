"""Read existing local editions; never generate editorial claims."""
import re
from html import unescape, escape
from pathlib import Path

def make_reports(root):
    result = []
    labels = {'daily': '日报', 'weekly': '周报', 'monthly': '月报'}
    for kind, label in labels.items():
        for path in sorted((root / 'reports').glob(kind + '-????-??-??.html'), reverse=True):
            source = path.read_text()
            heading = re.search(r'<h1[^>]*>(.*?)</h1>', source, re.S)
            if not heading:
                continue
            title = unescape(re.sub('<[^>]+>', '', heading[1]))
            editorial = 'class="story"' in source
            if editorial:
                body = re.search(r'<main[^>]*>(.*?)</main>', source, re.S)[1]
                body = re.sub(r'<div class="top">.*?</div>', '', body, count=1, flags=re.S)
            else:
                # Raw collection logs remain available through the full report link.
                paragraphs = re.findall(r'<p>.*?</p>', source, re.S)[:2]
                health = re.search(r'<h2>本次来源检查</h2>(<ul>.*?</ul>)', source, re.S)
                body = '<header class="hero"><div class="eyebrow">本期概览</div><h2>' + title + '</h2></header>' + ''.join(paragraphs)
                body += '<div class="digest-pending"><strong>本期尚未整理为主题分析</strong><p>内容包含基线与历史补录，记录数不等于本周期发生的产品更新数。完整摘录与来源保留在原始报告中。</p></div>'
                if health:
                    body += '<details><summary>查看来源检查</summary>' + health[1] + '</details>'
            if editorial:
                hero = re.search(r'<header class="hero">.*?</header>', body, re.S)[0]
                hero = hero.replace(' · 竞品日报 · 编辑版', ' · 竞品日报').replace(' · 竞品周报 · 编辑版', ' · 竞品周报').replace(' · 竞品月报 · 编辑版', ' · 竞品月报')
                hero = hero.replace('<h1>', '<h2>').replace('</h1>', '</h2>')
                highlights = re.search(r'<section class="takeaways">.*?</section>', body, re.S)[0]
                stories = re.findall(r'<article class="story".*?</article>', body, re.S)
                groups = {}
                for story in stories:
                    topic = re.search(r'<div class="eyebrow">([^<]+)', story)[1].split(' / ')[0]
                    groups.setdefault(topic, []).append(story)
                outline = '<nav class="digest-outline" aria-label="本期版面"><h3>本期版面</h3>'
                pages = ''
                for no, (topic, articles) in enumerate(groups.items(), 1):
                    key = 'page-' + str(no)
                    outline += f'<a href="#{key}"><b>{no:02}</b><span>{escape(topic)}</span><small>{len(articles)} 篇</small></a>'
                    pages += f'<section class="digest-page" id="{key}"><header class="digest-page-heading"><b>{no:02}</b><h2>{escape(topic)}</h2></header><div class="digest-columns">' + ''.join(articles) + '</div></section>'
                outline += '</nav>'
                footer = re.search(r'<footer class="bottom">.*?</footer>', body, re.S)[0]
                body = '<section class="digest-front" aria-label="头版">' + hero + '<div class="digest-front-side">' + highlights + outline + '</div></section>' + pages + footer
            prefix = 'digest-' + path.stem + '-'
            body = re.sub(r'id="([^"]+)"', lambda m: 'id="' + prefix + m[1] + '"', body)
            def link(m):
                url = m[1]
                if url.startswith('#'):
                    url = '#' + prefix + url[1:]
                elif not re.match(r'(?:https?:|mailto:|/)', url):
                    url = '../reports/' + url
                return 'href="' + url + '"'
            body = re.sub(r'href="([^"]+)"', link, body)
            result.append(dict(id=path.stem, kind=kind, date=path.stem[len(kind)+1:], title=title, status='编辑版' if editorial else ('采集汇总 · 进行中' if kind != 'daily' else '采集汇总'), body=body, url='../reports/'+path.name, markdown='../reports/'+path.with_suffix('.md').name if path.with_suffix('.md').exists() else None))
    return result
