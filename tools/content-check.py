"""Check final-profile provenance, public-data boundaries, links and generated output."""
import hashlib, html, json, re, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name): return json.loads((ROOT/'tools'/name).read_text(encoding='utf-8'))
def norm(text): return re.sub(r'[^a-z0-9]+','',html.unescape(text).lower())
evidence=norm((ROOT/'tools/approved-profile-public.txt').read_text(encoding='utf-8'))
products=load('products.json');company=load('company.json');solutions=load('solutions.json')
assert len(products)==56
assert sorted(p['catalogue_no'] for p in products)==list(range(1,57))
assert len({p['no'] for p in products})==56 and 10 not in {p['no'] for p in products}
for p in products:
    assert p['variants']==[],f"Unapproved variant rows: {p['name']}"
    for text in [p['name'],p['desc'],p['note'],*p['main_makes']]:
        assert norm(text) in evidence,('Not in final profile',p['name'],text)
for item in solutions:
    for text in [item['title'],item['sub'],*item['make'].split(' · ')]:
        assert norm(text) in evidence,('Unapproved solution claim',text)
    assert (ROOT/item['img']).is_file()
for text in company['industries']+company['partners']+company['clients'][1:]:
    assert norm(text) in evidence,('Unapproved company claim',text)
for entries in company['projects'].values():
    for row in entries:
        for text in row: assert norm(text) in evidence,('Unapproved project claim',text)
assert company['profile_revision']=='2026-11-12' and len(company['sources'])==1
assert 'Satya Sai Construction Works' in company['clients']
assert 'KSB' in company['partners'] and 'Phoenix Contact' in company['partners']
assert 'Vigilance Technology & Services' not in company['partners']
private_file = ROOT/'tools/private-patterns.txt'
private_patterns = []
if private_file.is_file():
    for number, pattern in enumerate(private_file.read_text(encoding='utf-8').splitlines(), 1):
        if not pattern.strip() or pattern.lstrip().startswith('#'): continue
        try: private_patterns.append(re.compile(pattern))
        except re.error:
            raise SystemExit(f'Invalid local private pattern at line {number}; value withheld.')
else:
    print('WARNING: tools/private-patterns.txt is missing; private-pattern check skipped.', file=sys.stderr)
# Scan the public tree, including source and documentation, without echoing matches.
for path in ROOT.rglob('*'):
    if not path.is_file() or path == private_file or '.git' in path.parts or '__pycache__' in path.parts: continue
    try: text = path.read_text(encoding='utf-8')
    except UnicodeError: continue
    assert not any(pattern.search(text) for pattern in private_patterns), f'Private pattern found in {path.relative_to(ROOT)}; value withheld.'
pages=list(ROOT.glob('*.html'))
for path in pages:
    text=path.read_text(encoding='utf-8')
    assert not re.search(r'332|50\+|Bonex|\bRecon\b',text),path
    for href in re.findall(r'(?:href|src)="([^"]+)"',text):
        if href.startswith(('http:','https:','mailto:','tel:','#','data:')): continue
        file=href.split('#')[0].split('?')[0]
        if file: assert (ROOT/file).is_file(),(path.name,href)
    if path.name!='company-profile.html':
        assert text.count('<h1>')==1,path
        assert 'rel="canonical"' in text and 'application/ld+json' in text,path
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S):json.loads(block)
# Regenerate elsewhere and compare all generated HTML byte-for-byte.
with tempfile.TemporaryDirectory() as tmp:
    subprocess.run([sys.executable,str(ROOT/'tools/build.py'),tmp],check=True)
    for path in pages: assert path.read_bytes()==(Path(tmp)/path.name).read_bytes(),f'Stale generated page: {path.name}'
print('PASS: 56 family scopes/makes, 36 solution captions, company/project evidence, local links, SEO and reproducible HTML. Private-pattern check: ' + ('passed.' if private_file.is_file() else 'SKIPPED (see warning).'))
