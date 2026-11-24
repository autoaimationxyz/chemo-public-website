"""Check final-profile provenance, public-data boundaries, links and generated output."""
import argparse, hashlib, html, json, re, subprocess, sys, tempfile
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--require-private',action='store_true',help='Fail if the local private-pattern file is missing.')
args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[1]
def load(name): return json.loads((ROOT/'tools'/name).read_text(encoding='utf-8'))
def norm(text): return re.sub(r'[^a-z0-9]+','',html.unescape(text).lower())
spaced_letters=re.compile(r'(?<![A-Za-z])(?:[A-Za-z][ \t]+){3,}[A-Za-z](?![A-Za-z])')
assert not spaced_letters.search((ROOT/'tools/approved-profile-public.txt').read_text(encoding='utf-8')), 'Literal letter spacing remains in the approved reference.'
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
assert company['bank_details']=='INCLUDE', 'This approved build includes the profile banking details.'
assert set(company['profile_pages'])=={str(n) for n in range(1,24)}
assert company['pan']['number'] in company['profile_pages']['3']
assert company['pan']['registered_on'] in company['profile_pages']['4']
for bank in company['banking_audit']['banks']:
    for value in bank.values(): assert norm(value) in norm(company['profile_pages']['3'])
assert norm(company['banking_audit']['auditor']) in norm(company['profile_pages']['3'])
private_file = ROOT/'tools/private-patterns.txt'
private_patterns = []
if private_file.is_file():
    for number, pattern in enumerate(private_file.read_text(encoding='utf-8').splitlines(), 1):
        if not pattern.strip() or pattern.lstrip().startswith('#'): continue
        try: private_patterns.append(re.compile(pattern))
        except re.error:
            raise SystemExit(f'Invalid local private pattern at line {number}; value withheld.')
else:
    print('SKIPPED – tools/private-patterns.txt missing',flush=True)
    if args.require_private:
        raise SystemExit('Required private-pattern check cannot run. Create the local file before pushing.')
# Scan the public tree, including source and documentation, without echoing matches.
for path in ROOT.rglob('*'):
    if not path.is_file() or path == private_file or '.git' in path.parts or '__pycache__' in path.parts: continue
    try: text = path.read_text(encoding='utf-8')
    except UnicodeError: continue
    assert not any(pattern.search(text) for pattern in private_patterns), f'Private pattern found in {path.relative_to(ROOT)}; value withheld.'
pages=list(ROOT.glob('*.html'))
# Design is the approved 7ba7c25 layout; content is the final company profile.
design=load('design-baseline.json')
for relative,expected in design['assets'].items():
    data=(ROOT/relative).read_bytes()
    if Path(relative).suffix in ['.css','.js','.svg','.md','.html']: data=data.replace(b"\r\n",b"\n")
    assert hashlib.sha256(data).hexdigest()==expected,f'Approved design asset changed: {relative}'
about_text=norm(html.unescape(re.sub(r'<[^>]+>',' ',(ROOT/'about.html').read_text(encoding='utf-8'))))
solutions_text=norm(html.unescape(re.sub(r'<[^>]+>',' ',(ROOT/'solutions.html').read_text(encoding='utf-8'))))
copy=company['approved_content']
for text in copy['about_paragraphs']+[copy['vision'],copy['mission_intro']]+copy['mission_commitments']+copy['team_bios']:
    assert norm(text) in evidence, 'Company text is not from the final profile'
    assert norm(text) in about_text, 'Missing approved company text on About'
for text in [row[1] for row in copy['how_we_work']]+copy['execution_steps']+copy['why_work_with_us']:
    assert norm(text) in evidence, 'Execution text is not from the final profile'
    assert norm(text) in solutions_text, 'Missing execution text in Solutions'
assert norm(company['pan']['number']) in about_text
assert norm(company['pan']['note']) in about_text
for bank in company['banking_audit']['banks']:
    for value in bank.values(): assert norm(value) in about_text, 'Missing banking detail on About'
assert norm(company['banking_audit']['auditor']) in about_text
registrations=(ROOT/'certifications.html').read_text(encoding='utf-8')
assert company['pan']['number'] in registrations and company['pan']['registered_on'] in registrations
registration_text=norm(html.unescape(re.sub(r'<[^>]+>',' ',registrations)))
for identifier in re.findall(r'\b(?:\d{2}/\d{2}/\d{4}|[A-Z0-9][A-Z0-9/-]*\d[A-Z0-9/-]*)\b',company['profile_pages']['4']):
    assert norm(identifier) in registration_text,f'Missing registration identifier from profile page 4'
for path in pages:
    text=path.read_text(encoding='utf-8')
    assert not re.search(r'\bSECTION\s+0|INSIDE THIS PROFILE|profile-index|profile-transcript|09\s*·\s*OUR SOLUTIONS',html.unescape(text),re.I),f'PDF page structure appears in {path.name}'
    assert not spaced_letters.search(html.unescape(text)),f'Literal letter spacing remains in {path.name}'
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
print('PASS: 56 family scopes/makes, 36 solution captions, company/project evidence, local links, SEO and reproducible HTML.')
if private_file.is_file():
    print(f'Private-pattern check: PASSED ({len(private_patterns)} patterns)')
