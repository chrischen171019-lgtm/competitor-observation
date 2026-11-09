"""Structural regression for the generated workbench and its embedded editions."""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import json,re,subprocess,tempfile
R=Path(__file__).resolve().parents[2]
class Document(HTMLParser):
 def __init__(self,source):
  super().__init__();self.ids=[];self.refs=[];self.hashes=[];self.files=[];self.nav=[];self.feed(source)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  for key in ('aria-controls','aria-labelledby'):
   self.refs+=a.get(key,'').split()
  if tag=='a':
   url=a.get('href','')
   if url.startswith('#'):self.hashes.append(url[1:])
   elif url and not re.match(r'(?:https?:|mailto:|data:)',url):self.files.append(url.split('#')[0])
   if 'data-section' in a:self.nav.append(a['data-section'])
s=(R/'outputs/competitor-ui-prototype.html').read_text();d=Document(s)
assert not [k for k,n in Counter(d.ids).items() if n>1], 'Duplicate HTML IDs'
assert all(x in d.ids for x in d.refs), set(d.refs)-set(d.ids)
routes={'section-updates','section-digest','section-feedback','section-strategy'}|{'product-'+k for k in ['notebook','ima','lexiang','weknora','chatgpt','workbuddy','doubao','patsnap','xinghe']}
assert all(x in d.ids or x in routes for x in d.hashes),set(d.hashes)-set(d.ids)-routes
assert d.nav==['competitors','updates','digest','feedback','strategy'],d.nav
assert 'site-reports' not in d.ids and 'site-discover' not in d.ids
for url in d.files:assert (R/'outputs'/url).resolve().exists(),url
source=(R/'outputs/competitor-research-complete.html').read_text()
assert re.findall(r'data:image/[^"]+',source)==re.findall(r'data:image/[^"]+',s),'Screenshots changed'
reports=json.loads((R/'outputs/prototype-news.json').read_text())['reports']
for report in reports:
 rd=Document(report['body']);assert len(rd.ids)==len(set(rd.ids));assert all(x in rd.ids for x in rd.hashes)
 for url in rd.files+[report['url']]+([report['markdown']] if report['markdown'] else []):assert (R/'outputs'/url).resolve().exists(),url
node='/Users/chris/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
for script in re.findall(r'<script[^>]*>(.*?)</script>',s,re.S):
 with tempfile.NamedTemporaryFile(suffix='.js') as f:
  f.write(script.encode());f.flush();subprocess.run([node,'--check',f.name],check=True)
print('PASS: five navigation entries, removed panels, unique IDs, ARIA references, anchors, local report links, screenshots and embedded JavaScript syntax.')
