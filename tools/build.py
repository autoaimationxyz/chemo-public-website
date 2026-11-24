#!/usr/bin/env python3
"""Generates the static Chemotech International site.

Usage:  python3 tools/build.py .

Content sources (edit these, then re-run):
  tools/products.json   56 approved families and main makes (final 12 November 2026 PDF only)
  tools/solutions.json  solution photos, captions, makes and linked product numbers
  this file             page copy, clients, partners, registrations, contact details
"""
import hashlib, html, json, os, re, sys
from urllib.parse import quote as url_quote
from pathlib import Path

OUT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
E = html.escape
SITE_URL = "https://autoaimationxyz.github.io/chemo-public-website/"

# Set to False to hide per-variant makes on the public site (main makes still show).
SHOW_VARIANT_MAKES = True


NAV = [
    ("index.html", "Home"),
    ("solutions.html", "Solutions"),
    ("products.html", "Products"),
    ("projects.html", "Projects"),
    ("about.html", "About"),
    ("contact.html", "Contact"),
]

def arrow_svg(direction="right"):
    paths = {"right": "M4 12h16m-6-6 6 6-6 6", "up-right": "M6 18 18 6M6 6h12v12", "down": "M12 4v16m-6-6 6 6 6-6"}
    return f'<svg class="arrow arrow--{direction}" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="{paths[direction]}"/></svg>'


ARROW = arrow_svg()
ARROW_UP_RIGHT = arrow_svg("up-right")
ARROW_DOWN = arrow_svg("down")

ICONS = {
    "electrical": '<rect x="4" y="3" width="16" height="18"/><path d="M13 6.5 9.5 12h4L11 17.5"/>',
    "switch": '<rect x="5" y="3" width="14" height="18"/><circle cx="12" cy="9" r="2.6"/><path d="M12 11.6V17M9 17h6"/>',
    "cable": '<path d="M3 6h7a3.5 3.5 0 0 1 0 7H7a3.5 3.5 0 0 0 0 7h14"/><circle cx="3" cy="6" r="1"/>',
    "power": '<rect x="3" y="7" width="15" height="10"/><path d="M18 10h2.5v4H18"/><path d="M11 8.8 8.6 12h3.6L10 15.2"/>',
    "automation": '<rect x="7" y="7" width="10" height="10"/><rect x="10" y="10" width="4" height="4"/><path d="M9.5 3v4M14.5 3v4M9.5 17v4M14.5 17v4M3 9.5h4M3 14.5h4M17 9.5h4M17 14.5h4"/>',
    "water": '<path d="M12 3c-4 5-6.2 8.2-6.2 11.2a6.2 6.2 0 0 0 12.4 0C18.2 11.2 16 8 12 3z"/><path d="M9 15a3 3 0 0 0 3 3"/>',
    "chemicals": '<path d="M9 3h6M10 3v6.2l-5.3 8.9A2 2 0 0 0 6.4 21h11.2a2 2 0 0 0 1.7-2.9L14 9.2V3"/><path d="M7.4 15h9.2"/>',
    "location": '<path d="M20 10c0 6-8 11-8 11S4 16 4 10a8 8 0 1 1 16 0z"/><circle cx="12" cy="10" r="2.5"/>',
    "building": '<path d="M4 21V8.5L12 3l8 5.5V21"/><path d="M2.5 21h19M9.5 21v-5.5h5V21M8 10.5h2M14 10.5h2"/>',
    "ict": '<rect x="3" y="4" width="18" height="12"/><path d="M8 20h8M12 16v4M7 8h4M7 11h7"/>',
    "service": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3.5 17.5l3 3 5.8-5.8a4 4 0 0 0 5.4-5.4l-2.6 2.6-2.9-2.9z"/>',
}


def icon(key, cls="vicon"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.5" stroke-linecap="square" aria-hidden="true">{ICONS[key]}</svg>')


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------
PRODUCTS = json.loads(Path(HERE, "products.json").read_text(encoding="utf-8"))
SOLUTIONS = json.loads(Path(HERE, "solutions.json").read_text(encoding="utf-8"))
COMPANY = json.loads(Path(HERE, "company.json").read_text(encoding="utf-8"))
INBOX = COMPANY["contacts"]["primary_email"]

# 8 product categories, as colour-keyed in the 2026 company profile (product numbers in order)
CATEGORIES = [
    ("pd", "Power Distribution", range(1, 10), "electrical", "HT and LT panels, MCC, synchronising and APFC panels, transformers, substations and multi-brand DG sets."),
    ("sw", "Switchgear & Controls", range(11, 17), "switch", "Breakers, earth-leakage protection, DBs, changeovers, contactors, relays, indication and metering."),
    ("cl", "Cabling, Lighting & Safety", range(17, 27), "cable", "Power and control cables, wires, accessories, LED and street lighting, fans, earthing, fire alarm and PA."),
    ("pb", "Power Backup & Energy", range(27, 34), "power", "Online UPS and data-centre power, batteries, stabilisers, harmonic filters, EMS, solar and EV charging."),
    ("au", "Automation & Instrumentation", [34, 35, 36, 37, 38, 57], "automation", "Motors, drives, PLC / HMI / SCADA, plant automation, flow / level / pressure instruments and water quality analysers."),
    ("wp", "Water & Process", range(39, 47), "water", "WTP, ETP, STP, RO / DM / UF plants, components and O&M, steam and piping, process chemicals and hygiene."),
    ("bi", "Building & ICT", range(47, 55), "building", "BMS, lifts, AC and ventilation, LED video walls, pre-fab structures, networking, CCTV and IT."),
    ("sv", "Services", range(55, 57), "service", "Licensed electrical installation, testing, commissioning, O&M and annual maintenance contracts."),
]
CAT_BY_NO = {}
for cid, _, rng, _, _ in CATEGORIES:
    for n in rng:
        CAT_BY_NO[n] = cid
CAT = {c[0]: c for c in CATEGORIES}

for p in PRODUCTS:
    p["cat"] = CAT_BY_NO[p["no"]]
    imgs = [dict(src=s["img"], title=s["title"], sub=s["sub"], make=s["make"]) for s in SOLUTIONS if p["no"] in s["products"]]
    # Only final-profile solution captions are approved.
    p["images"] = imgs
    if not SHOW_VARIANT_MAKES:
        for v in p["variants"]:
            v["makes"] = []

N_PRODUCTS = len(PRODUCTS)
N_VARIANTS = sum(len(p["variants"]) for p in PRODUCTS)
N_MAKES = len({m for p in PRODUCTS for v in p["variants"] for m in v["makes"]} | {m for p in PRODUCTS for m in p["main_makes"]})
assert N_PRODUCTS == 56
assert N_VARIANTS == 0, "The final profile approves family scopes, not individual variant rows"

INDUSTRIES = COMPANY["industries"]

CLIENTS = COMPANY["clients"]
PARTNERS = COMPANY["partners"]

SERVICES = ["Engineering & technical solution design", "Equipment selection & supply", "System integration",
            "Installation", "Testing & commissioning", "Troubleshooting",
            "Preventive maintenance & O&M support", "After-sales service & plant improvement"]

def phone_links(numbers):
    return [("+" + re.sub(r"\D", "", number), number) for number in numbers]


PHONES_PATNA = phone_links(COMPANY["contacts"]["offices"]["patna"]["phones"])
PHONES_DELHI = phone_links(COMPANY["contacts"]["offices"]["delhi"]["phones"])
PHONES_GENERAL = phone_links(COMPANY["contacts"]["general_phones"])


def split_variant(name):
    """'Group – Type' split on en dashes, keeping numeric ranges like '30 – 200 mm' intact."""
    safe = re.sub(r"(\d) – (\d)", lambda m: m.group(1) + "\x00" + m.group(2), name)
    parts = [x.replace("\x00", " – ") for x in safe.split(" – ")]
    return (" – ".join(parts[:-1]), parts[-1]) if len(parts) > 1 else ("", name)


def tile_names(p):
    """Short variant labels for the spec-sheet tile (single-item groups keep their full name)."""
    rows = [split_variant(v["name"]) + (v["name"],) for v in p["variants"] if v["name"]]
    size = {}
    for g, _, _ in rows:
        size[g] = size.get(g, 0) + 1
    return [full if (not g or size[g] == 1) else n for g, n, full in rows] or [p["name"]]


def sol(slug):
    return next(s for s in SOLUTIONS if s["img"].endswith("/" + slug + ".jpg"))


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------
def header(active):
    links = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == active else ""
        links.append(f'<a href="{href}"{cur}>{label}</a>')
    qcur = ' aria-current="page"' if active == "quote.html" else ""
    links.append(f'<a class="btn" href="quote.html"{qcur}>Request Quote</a>')
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<div class="topbar" role="region" aria-label="Company coverage and email">
  <div class="wrap">
    <div class="topbar__group">
      <span class="topbar__countries">INDIA · NEPAL · BHUTAN</span>
      <span class="topbar__hide-sm">Patna · Delhi</span>
    </div>
    <div class="topbar__group">
      <a href="mailto:{INBOX}">{INBOX}</a>
    </div>
  </div>
</div>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html" aria-label="Chemotech International, home">
      <img src="assets/img/chemotech-logo.png" width="1820" height="300" alt="Chemotech International – a Clean and Conditioning Company">
    </a>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Open menu">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h12"/></svg>
    </button>
    <nav class="nav" id="site-nav" aria-label="Main">
      {"".join(links)}
    </nav>
  </div>
</header>"""


def footer():
    phones = "".join(f'<li><a href="tel:{a}">{b}</a></li>' for a, b in PHONES_GENERAL)
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-top">
      <div class="footer-brand">
        <div class="logo-tile"><img src="assets/img/chemotech-logo.png" width="1820" height="300" alt="Chemotech International" loading="lazy"></div>
        <p class="tagline">…a Clean and Conditioning company</p>
        <p>Electrical Works &amp; Panels · Earthing &amp; Lightning Protection · UPS &amp; DG Sets · VFD, PLC &amp; SCADA Automation · Water &amp; Wastewater Treatment · Solar &amp; EV Charging · Building &amp; ICT Systems</p>
      </div>
      <div>
        <h2>Explore</h2>
        <ul><li><a href="solutions.html">Solutions &amp; Services</a></li><li><a href="products.html">Product catalogue</a></li><li><a href="projects.html">Projects &amp; Clients</a></li></ul>
      </div>
      <div>
        <h2>Company</h2>
        <ul><li><a href="about.html">About Chemotech</a></li><li><a href="certifications.html">Licences &amp; Registrations</a></li><li><a href="contact.html">Contact &amp; offices</a></li><li><a href="quote.html">Request a Quote</a></li></ul>
      </div>
      <div>
        <h2>Reach us</h2>
        <ul>
          {phones}
          <li><a href="mailto:{INBOX}">{INBOX}</a></li>

        </ul>
      </div>
    </div>
  </div>
  <div class="wrap footer-bottom">
    <span>© <span data-year>2026</span> Chemotech International. All rights reserved.</span>
    <span>Est. 2014–15 · Serving India, Nepal &amp; Bhutan</span>
  </div>
</footer>"""


def contact_actions():
    message = url_quote("Hello Chemotech, I have an enquiry about \u2026")
    return f'''<nav class="contact-actions" aria-label="Quick contact">
  <a class="contact-actions__whatsapp" href="https://wa.me/919899982418?text={message}" target="_blank" rel="noopener noreferrer">WhatsApp</a>
  <a class="contact-actions__call" href="tel:+919899982418">Call</a>
</nav>'''


def contact_stylesheet():
    version = hashlib.sha256(Path(HERE, "../assets/css/contact-actions.css").read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:12]
    return f'<link rel="stylesheet" href="assets/css/contact-actions.css?v={version}">'


def page(filename, title, description, body, extra_scripts=""):
    full_title = "Chemotech International" if filename == "index.html" else f"{title} · Chemotech International"
    with open(os.path.join(HERE, "../assets/css/immersive.css"), "rb") as theme:
        theme_version = hashlib.sha256(theme.read().replace(b"\r\n", b"\n")).hexdigest()[:12]
    with open(os.path.join(HERE, "../assets/css/profile.css"), "rb") as profile_theme:
        profile_version = hashlib.sha256(profile_theme.read().replace(b"\r\n", b"\n").replace(b"\r\n", b"\n")).hexdigest()[:12]
    base_version = hashlib.sha256(Path(HERE, "../assets/css/style.css").read_text(encoding="utf-8").encode("utf-8")).hexdigest()[:12]
    modern_version = hashlib.sha256(Path(HERE, "../assets/css/modern.css").read_text(encoding="utf-8").encode("utf-8")).hexdigest()[:12]
    main_version = hashlib.sha256(Path(HERE, "../assets/js/main.js").read_text(encoding="utf-8").encode("utf-8")).hexdigest()[:12]
    schema = json.dumps({"@context":"https://schema.org", "@type":"Organization", "name":"Chemotech International", "url":SITE_URL, "logo":SITE_URL+"assets/img/chemotech-logo.png", "email":INBOX, "telephone":COMPANY["contacts"]["general_phones"], "areaServed":COMPANY["countries"]}).replace("</", "<\\/")
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{full_title}</title>
<meta name="description" content="{E(description)}">
<meta name="theme-color" content="#00008B">
<script type="application/ld+json">{schema}</script>
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{E(description)}">
<link rel="canonical" href="{SITE_URL}{filename}">
<meta property="og:url" content="{SITE_URL}{filename}">
<meta property="og:site_name" content="Chemotech International">
<meta name="twitter:card" content="summary">
<meta property="og:type" content="website">
<meta property="og:image" content="{SITE_URL}assets/img/chemotech-logo.png">
<link rel="icon" type="image/png" href="favicon.png">
<link rel="stylesheet" href="assets/css/style.css?v={base_version}">
<link rel="stylesheet" href="assets/css/modern.css?v={modern_version}">
<link rel="stylesheet" href="assets/css/immersive.css?v={theme_version}">
<link rel="stylesheet" href="assets/css/profile.css?v={profile_version}">
{contact_stylesheet()}
</head>
<body>
{header(filename)}
<main id="main">
{body}
</main>
{footer()}
{contact_actions()}
<script defer src="assets/js/main.js?v={main_version}"></script>
{extra_scripts}
</body>
</html>
"""
    with open(os.path.join(OUT, filename), "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)


def page_hero(crumb, title, text, tag=None):
    t = f'<span class="tag">{tag}</span>' if tag else ""
    return f"""<section class="page-hero on-navy">
  <div class="wrap">
    <div class="crumbs"><a href="index.html">Home</a><span aria-hidden="true">/</span><span>{crumb}</span></div>
    {t}
    <h1>{title}</h1>
    <p>{text}</p>
  </div>
  <div class="page-hero__rule"></div>
</section>"""


def cta(*args, **kwargs):
    return '<nav class="wrap section-nav" aria-label="Enquiries"><a href="quote.html">Request a quote</a><a href="contact.html">Contact</a></nav>'


def industries_list():
    return "".join(f'<li{" class=\"is-key\"" if "Government" in n else ""}><span class="list-number" aria-hidden="true">{i:02d}</span><span class="list-copy">{E(n)}</span></li>' for i, n in enumerate(INDUSTRIES, 1))


def office_cards():
    pp = '<ul class="contact-methods">' + "".join(f'<li><a href="tel:{a}">{b}</a></li>' for a, b in PHONES_PATNA) + '</ul>'
    dp = '<ul class="contact-methods">' + "".join(f'<li><a href="tel:{a}">{b}</a></li>' for a, b in PHONES_DELHI) + '</ul>'
    def email_links(office):
        return '<ul class="contact-methods">' + ''.join('<li><a href="mailto:' + E(email) + '">' + E(email).replace('@', '<wbr>@') + '</a></li>' for email in COMPANY["contacts"]["offices"][office]["emails"]) + '</ul>'
    ep, ed = email_links("patna"), email_links("delhi")
    return f"""<div class="offices">
      <article class="office" id="office-patna">
        <span class="tag">Head office · Bihar</span>
        <div class="office-heading">{icon("location")}<h2>Patna</h2></div>
        <address>Pratiksha Bhawan, Maurya Vihar Colony,<br>Near Bihar Urology Centre, Transport Nagar,<br>Patna, Bihar – 800026</address>
        <dl>
          <dt>Phone</dt><dd>{pp}</dd>
          <dt>Email</dt><dd>{ep}</dd>
        </dl>
        <div class="gstin"><span class="gstin__label">GSTIN · Bihar</span><span class="gstin__number">10AATFC8340G1ZJ</span></div>
      </article>
      <article class="office" id="office-delhi">
        <span class="tag">Branch office · Delhi</span>
        <div class="office-heading">{icon("location")}<h2>Delhi</h2></div>
        <address>Maya Garden, Ground Floor, Kh. No. 44/18 &amp; 44/19,<br>Gate No. 02, Inderprastha (IP) Colony, Block-C,<br>Village Burari, North Delhi – 110084</address>
        <dl>
          <dt>Phone</dt><dd>{dp}</dd>
          <dt>Email</dt><dd>{ed}</dd>
        </dl>
        <div class="gstin"><span class="gstin__label">GSTIN · Delhi</span><span class="gstin__number">07AATFC8340G1Z6</span></div>
      </article>
    </div>"""


# --------------------------------------------------------------------------
# HOME
# --------------------------------------------------------------------------
def product_specs(p):
    return [("Approved product scope", p["desc"])]













# --------------------------------------------------------------------------
# ABOUT
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# PRODUCTS (interactive catalogue)
# --------------------------------------------------------------------------


def products():
    counts = {c[0]: sum(1 for p in PRODUCTS if p["cat"] == c[0]) for c in CATEGORIES}
    chips = f'<button class="chip chip--all" type="button" data-cat="all" aria-pressed="true">All products <span>{N_PRODUCTS}</span></button>' + "".join(
        f'<button class="chip c-{c[0]}" type="button" data-cat="{c[0]}" aria-pressed="false">{E(c[1])} <span>{counts[c[0]]}</span></button>' for c in CATEGORIES)

    make_count = {}
    for p in PRODUCTS:
        for m in set(p["main_makes"]) | {m for v in p["variants"] for m in v["makes"]}:
            make_count[m] = make_count.get(m, 0) + 1
    make_opts = "".join(f'<option value="{E(m)}">{E(m)} ({n})</option>' for m, n in sorted(make_count.items(), key=lambda x: x[0].lower()))

    cards = []
    for p in PRODUCTS:
        c = CAT[p["cat"]]
        if p["images"]:
            im = p["images"][0]
            badge = f'<span class="count-badge">{len(p["images"])} photos</span>' if len(p["images"]) > 1 else ""
            media = f'<img src="{im["src"]}" alt="" loading="lazy" width="640" height="480">{badge}'
        else:
            media = f'<div class="equipment-tile"><span class="equipment-no">{p["no"]:02d} / {E(c[1])}</span><span>{E(p["name"])}</span></div>'
        cards.append(f"""<article class="pcard c-{p['cat']}" data-no="{p['no']}" id="product-{p['no']}">
        <button class="pcard__open" type="button" aria-haspopup="dialog">
          <div class="pcard__media">{media}</div>
          <div class="pcard__body">
            <div class="pcard__meta"><span>{E(c[1])}</span><span>Product scope</span></div>
            <h3>{E(p['name'])}</h3>
            <p>{E(p['desc'])}</p>
            <span class="pcard__discover">Scope &amp; main makes {ARROW_UP_RIGHT}</span>
          </div>
        </button>
        <div class="pcard__foot">
          <button class="add-btn" type="button" data-add="{p['no']}" aria-pressed="false"><span class="ic-off">+ Add to enquiry</span><span class="ic-on">&check; Added</span></button></div>
      </article>""")

    data = {
        "redirects": {"10": 9},
        "categories": [{"id": c[0], "name": c[1], "blurb": c[1], "icon": icon(c[3], "")} for c in CATEGORIES],
        "products": [{"no": p["no"], "catalogue_no": p["catalogue_no"], "name": p["name"], "cat": p["cat"], "desc": p["desc"], "note": p["note"],
                      "main": p["main_makes"], "variants": p["variants"], "images": p["images"], "specs": product_specs(p), "application": p["desc"], "illustration": ""} for p in PRODUCTS],

    }
    data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    body = f"""
<section class="catalogue-hero"><div class="wrap"><div class="crumbs"><a href="index.html">Home</a><span aria-hidden="true">/</span><span>Products</span></div><h1>Our Product Range</h1><p>{N_PRODUCTS} product families · 300+ variants. Search by equipment, specification or make.</p><a class="text-link" href="solutions.html">Need help defining the system? Explore solutions {ARROW}</a></div></section>
<div class="cat-toolbar" role="search" aria-label="Filter products">
  <div class="wrap">
    <div class="cat-row">
      <div class="searchbox">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>
        <label class="visually-hidden" for="cat-search">Search products, scopes and makes</label>
        <input id="cat-search" type="search" placeholder="Search e.g. 11 kV VCB, MBBR, Kirloskar, CCTV" autocomplete="off">
      </div>
      <div>
        <label class="visually-hidden" for="cat-make">Filter by make</label>
        <select id="cat-make"><option value="">All makes ({len(make_count)})</option>{make_opts}</select>
      </div>
      <span class="cat-count" id="cat-count" aria-live="polite"><b>{N_PRODUCTS}</b> matching products</span>
    </div>
    <div class="chips-row" role="group" aria-label="Product categories">{chips}</div>
  </div>
</div>

<section class="section" id="catalogue" style="padding-top:36px">
  <div class="wrap">
    <div class="cat-intro">
      <h2 id="cat-title">All products</h2>
      <button class="link-btn" type="button" data-reset>Reset filters</button>
      <p id="cat-title-note">Select a product to see its scope and main makes. Detailed options are available on request.</p>
    </div>
    <p class="catalogue-guidance">Main makes shown are indicative; the complete product &amp; make list is available on request.</p>
    <div class="pgrid" id="product-grid">{"".join(cards)}</div>
    <div class="catalogue-more"><button class="btn btn--ghost" id="show-more" type="button" aria-controls="product-grid" hidden>Show more products</button><p id="catalogue-progress" aria-live="polite"></p></div>
    <div class="empty-state" id="cat-empty" hidden>
      <b>No products match these filters</b>
      <p>Try a shorter search, another make, or all categories. If you can't find the item, share your requirement with our team.</p>
      <div class="btn-row"><button class="btn btn--ghost" type="button" data-reset>Clear filters</button><a class="btn" href="contact.html">Ask us</a></div>
    </div>
  </div>
</section>

{cta("Have your equipment shortlist ready?", "Build your enquiry", "quote.html", "contact.html", "Ask a question")}

<div class="tray" id="tray" hidden>
  <div class="tray__in">
    <span class="tray__count"><b id="tray-count">0</b><span class="tray__long" id="tray-label">products in your enquiry</span><span class="tray__short">in enquiry</span></span>
    <div class="tray__list" id="tray-list" tabindex="0" role="region" aria-label="Products in your enquiry"></div>
    <div class="tray__actions"><button class="link-btn" type="button" id="tray-clear">Clear</button><a class="btn btn--green" href="quote.html">Request quote {ARROW}</a></div>
  </div>
</div>
<dialog class="pdialog" id="pdialog" aria-label="Product details"></dialog>
<script type="application/json" id="catalogue-data">{data_json}</script>"""
    page("products.html", "Our Products",
         f"Chemotech International product catalogue: {N_PRODUCTS} product families with 300+ variants across power distribution, switchgear, cabling, power backup, automation, water & process, building & ICT and services.",
         body, '<script src="assets/js/catalogue.js?v=' + hashlib.sha256(Path(HERE, "../assets/js/catalogue.js").read_text(encoding="utf-8").encode("utf-8")).hexdigest()[:12] + '"></script>')


# --------------------------------------------------------------------------
# COMPANY PROFILE
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# CERTIFICATIONS
# --------------------------------------------------------------------------
def certifications():
    body = f"""
{page_hero("Licences & Registrations", "Licences &amp; Registrations", "Electrical Contractor Licences – Bihar &amp; Delhi · Building Construction Department, Govt. of Bihar · Haryana Engineering Works Portal, Govt. of Haryana", "Licences &amp; registrations")}

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="tag">Electrical contractor licences</span>
      <h2>Electrical Contractor Licences</h2>
    </div>
    <div class="lic-cards">
      <article class="lic">
        <header><small>Govt. of NCT of Delhi · Labour Department</small><h3>Delhi – Licence to Electrical Contractors</h3></header>
        <dl>
          <dt>Application No.</dt><dd class="mono">50590000009296</dd>
          <dt>Valid</dt><dd>16/06/2025 – 15/06/2050</dd>
          <dt>Premises</dt><dd>Burari, Delhi – 110084</dd>
          <dt>Represented by</dt><dd>Tapan Kumar Jha, Partner</dd>
        </dl>
      </article>
      <article class="lic">
        <header><small>Govt. of Bihar · Electrical Licensing Board, Patna</small><h3>Bihar – Electrical Contractor Licence</h3></header>
        <dl>
          <dt>Registration No.</dt><dd class="mono">50/2025</dd>
          <dt>File ref.</dt><dd class="mono">IV-03(72)/2025</dd>
          <dt>Valid</dt><dd>08/07/2025 – 07/07/2030</dd>
          <dt>Licensee</dt><dd>Tapan Kumar Jha, Partner</dd>
          <dt>Test equipment</dt><dd>Insulation Megger &amp; Earth Tester (National)</dd>
        </dl>
      </article>
    </div>
  </div>
</section>

<section class="section section--tight section--wash">
  <div class="wrap">
    <div class="section-head" style="margin-bottom:24px">
      <span class="tag">Contractor registrations</span>
      <h2>Contractor Registration</h2>
    </div>
    <div class="stack" style="gap:12px">
      <div class="reg-banner" style="background:var(--paper)">
        <div><h3>Building Construction Department, Govt. of Bihar</h3><p>Registration No. <b>3260569</b> · Valid 08/07/2026 – 07/07/2031</p></div>
        <span class="class">Class 3</span>
      </div>
      <div class="reg-banner" style="background:var(--paper);border-left-color:var(--green)">
        <div><h3>Haryana Engineering Works Portal, Govt. of Haryana</h3><p>Contractor ID <b>2026R31684</b> · Dated 26/10/2026</p></div>
        <span class="class" style="background:var(--green);color:var(--navy-deep)">Haryana</span>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="tag">Tax &amp; business registrations</span>
      <h2>Tax &amp; Business Registrations</h2>
    </div>
    <div class="table-wrap" tabindex="0" role="region" aria-label="Registration details table">
      <table class="data">
        <thead><tr><th scope="col">Registration</th><th scope="col">Number</th><th scope="col">Registered on</th></tr></thead>
        <tbody>
          <tr><th scope="row">GST – Bihar</th><td class="mono">10AATFC8340G1ZJ</td><td>21/06/2024</td></tr>
          <tr><th scope="row">GST – Delhi</th><td class="mono">07AATFC8340G1Z6</td><td>01/06/2024</td></tr>
          <tr><th scope="row">PAN</th><td class="mono">{E(COMPANY['pan']['number'])}</td><td>{E(COMPANY['pan']['registered_on'])}</td></tr>
          <tr><th scope="row">Udyam (MSME) – Micro</th><td class="mono">UDYAM-BR-26-0136033</td><td>10/07/2024</td></tr>
          <tr><th scope="row">Firm Registration – Bihar</th><td class="mono">F2600000083<small>Register No. F000233/2026 · Indian Partnership Act, 1932</small></td><td>21/04/2026</td></tr>
        </tbody>
      </table>
    </div>

  </div>
</section>
{cta("Check the credentials for your scope.", "Discuss your requirements", "contact.html")}"""
    page("certifications.html", "Licences & Registrations",
         "Chemotech International licences and registrations: Delhi and Bihar electrical contractor licences, BCD Bihar Class 3, Haryana Engineering Works Portal, GST, PAN, Udyam MSME and firm registration.",
         body)


# --------------------------------------------------------------------------
# CONTACT & QUOTE
# --------------------------------------------------------------------------
def status_box():
    return f"""<div class="form-status" role="status" hidden>
        <b>Your email app should now open with the message ready to send.</b>
        Press send there to reach us. If nothing opened, email <a href="mailto:{INBOX}">{INBOX}</a> or call +91 98999 82418.
      </div>"""


def field(id_, label, kind="text", required=False, opt=False, attrs="", msg="", full_label=None):
    req = " required" if required else ""
    o = ' <span class="opt">(optional)</span>' if opt else ""
    dmsg = f' data-msg="{msg}"' if msg else ""
    dl = E(full_label or label)
    if kind == "textarea":
        ctl = f'<textarea id="{id_}" name="{id_}" data-label="{dl}"{req}{dmsg} {attrs}></textarea>'
    else:
        ctl = f'<input id="{id_}" name="{id_}" type="{kind}" data-label="{dl}"{req}{dmsg} {attrs}>'
    err = f'<span class="err" data-err-for="{id_}" aria-live="polite"></span>' if required else ""
    return f'<div class="field"><label for="{id_}">{label}{o}</label>{ctl}{err}</div>'


def contact():
    body = f"""
{page_hero("Contact", "Talk to our engineers", "Discuss your project with our team in Patna or Delhi. Share your site, scope and priorities so we can help you select the right approach.", "Contact us")}
<nav class="section-nav wrap" aria-label="Contact options"><a href="#enquiry">Write an enquiry</a><a href="#office-patna">Patna office</a><a href="#office-delhi">Delhi office</a></nav>

<section class="section">
  <div class="wrap">
    {office_cards()}
    <div class="btn-row mt-md">
      <a class="text-link" href="https://www.google.com/maps/search/?api=1&amp;query=Pratiksha+Bhawan+Maurya+Vihar+Colony+Transport+Nagar+Patna+800026" target="_blank" rel="noopener">Patna office on map {ARROW}</a>
      <span aria-hidden="true" class="muted">·</span>
      <a class="text-link" href="https://www.google.com/maps/search/?api=1&amp;query=Inderprastha+Colony+Burari+Delhi+110084" target="_blank" rel="noopener">Delhi office on map {ARROW}</a>
    </div>
  </div>
</section>

<section class="section section--wash">
  <div class="wrap form-layout">
    <form class="form" id="enquiry" data-mailto="Website enquiry" data-recipient="{INBOX}" novalidate>
      <noscript><p>This draft form needs JavaScript. Email <a href="mailto:{INBOX}">{INBOX}</a> or call +91 98999 82418.</p></noscript>
      <fieldset>
        <legend>Prepare your enquiry</legend><p class="form-explainer">This form prepares a draft. Send it from your email app, or copy the message into your email service.</p>
        <div class="row">
          {field("name", "Your name", required=True, attrs='autocomplete="name"', msg="Please enter your name.", full_label="Name")}
          {field("company", "Company", opt=True, attrs='autocomplete="organization"')}
        </div>
        <div class="row">
          {field("email", "Email", "email", required=True, attrs='autocomplete="email"', msg="Please enter a valid email address.")}
          {field("phone", "Phone", "tel", opt=True, attrs='autocomplete="tel"')}
        </div>
        <div class="field">
          <label for="office">Office to contact</label>
          <select id="office" name="office" data-label="Office">
            <option>Not sure</option>
            <option>Head office – Patna</option>
            <option>Delhi office</option>
          </select>
        </div>
        {field("message", "Message", "textarea", required=True, msg="Please tell us how we can help.")}
      </fieldset>
      {status_box()}
      <div class="form-foot">
        <div class="btn-row form-actions"><button class="btn" type="submit">Prepare message {ARROW}</button><button class="btn btn--ghost" type="button" data-copy-message>Copy message</button></div>
        <small>Opens your email app with the message filled in, addressed to {INBOX}.</small>
      </div>
    </form>
    <div class="aside" role="region" aria-label="Enquiry help">
      <div class="aside-card">
        <h2>Need a price?</h2>
        <p>Pick products in the catalogue, then use the quote form to share quantities and site location. It helps us respond faster with the right technical offer.</p>
        <a class="btn btn--ghost" href="products.html" style="justify-self:start">Browse products {ARROW}</a>
      </div>
    </div>
  </div>
</section>"""
    page("contact.html", "Contact",
         f"Contact Chemotech International: head office in Patna, Bihar and branch office in Burari, Delhi. Phone +91 98999 82418, {INBOX}.",
         body)


def quote():
    checks = "".join(f'<label><input type="checkbox" name="category" value="{E(c[1])}">{E(c[1])}</label>' for c in CATEGORIES)
    body = f"""
{page_hero("Request Quote", "Request a quote", "Share your equipment, scope and site details. Prepare an email enquiry for our team to review and discuss with you.", "Quotation")}

<script type="application/json" id="product-index">{json.dumps({str(p["no"]): {"name": p["name"], "catalogue_no": p["catalogue_no"]} for p in PRODUCTS}, ensure_ascii=False).replace("</", "<\\/")}</script>
<section class="section section--wash">
  <div class="wrap form-layout">
    <form class="form" data-mailto="Quote request" data-recipient="{INBOX}" novalidate>
      <fieldset>
        <legend>1 · Your details</legend><noscript><p>Email <a href="mailto:{INBOX}">{INBOX}</a> or call +91 98999 82418. Enable JavaScript to prepare a draft here.</p></noscript><p class="form-explainer">Prepare your enquiry here, then send it from your email app. You can also copy the draft into your email service.</p>
        <div class="row">
          {field("name", "Your name", required=True, attrs='autocomplete="name"', msg="Please enter your name.", full_label="Name")}
          {field("company", "Company / organisation", required=True, attrs='autocomplete="organization"', msg="Please enter your company or organisation.", full_label="Company")}
        </div>
        <div class="row">
          {field("email", "Email", "email", required=True, attrs='autocomplete="email"', msg="Please enter a valid email address.")}
          {field("phone", "Phone", "tel", required=True, attrs='autocomplete="tel"', msg="Please enter a phone number.")}
        </div>
      </fieldset>
      <fieldset>
        <legend>2 · What do you need?</legend>
        <div class="picked" id="picked" hidden>
          <p><b>From the catalogue:</b> these products will be included in your request.</p>
          <ul></ul>
        </div>
        <p id="picked-notice" class="selection-notice" role="status" aria-live="polite"></p>
        <a class="text-link quote-catalogue-link" id="quote-catalogue-link" href="products.html">Browse products to add to your enquiry {ARROW}</a>
        <input type="hidden" id="picked-input" data-label="Catalogue products">
        <div class="checks" role="group" aria-label="Categories" data-label="Categories">{checks}</div>
      </fieldset>
      <fieldset>
        <legend>3 · Scope</legend>
        {field("requirement", "Quantities, ratings and details", "textarea", required=True, msg="Please describe what you need.", attrs='placeholder="Enter equipment, quantity, required ratings and site conditions"', full_label="Requirement")}
        <div class="row">
          {field("site", "Site location", required=True, msg="Please enter the site location.", attrs='placeholder="City, state, country"', full_label="Site location")}
          <div class="field">
            <label for="timeline">Required by</label>
            <select id="timeline" name="timeline" data-label="Required by">
              <option>Not sure yet</option>
              <option>Within 1 month</option>
              <option>1 – 3 months</option>
              <option>3 – 6 months</option>
              <option>Budgetary quote only</option>
            </select>
          </div>
        </div>
        <div class="row">
          <div class="field">
            <label for="service">Scope of work</label>
            <select id="service" name="service" data-label="Scope of work">
              <option>Please advise on scope</option>
              <option>Supply only</option>
              <option>Supply &amp; installation</option>
              <option>Turnkey (design to commissioning)</option>
              <option>Service / AMC</option>
            </select>
          </div>
          {field("makes", "Preferred makes", opt=True, attrs='placeholder="e.g. Delta, Kirloskar, L&amp;T"', full_label="Preferred makes")}
        </div>
      </fieldset>
      {status_box()}
      <div class="form-foot">
        <div class="btn-row form-actions"><button class="btn" type="submit">Prepare quote email {ARROW}</button><button class="btn btn--ghost" type="button" data-copy-message>Copy enquiry</button></div>
        <small>Opens your email app with your request filled in. Attach drawings, BOQs or datasheets there before sending.</small>
      </div>
    </form>
    <div class="aside" role="region" aria-label="Enquiry help">
      <div class="aside-card">
        <h2>What happens next</h2>
        <ol>
          <li><span class="list-copy">We review your requirement and operating conditions.</span></li>
          <li><span class="list-copy">Our team may contact you for site details or drawings.</span></li>
          <li><span class="list-copy">You receive a technical and commercial offer.</span></li>
        </ol>
      </div>
      <div class="aside-card">
        <h2>Prefer to call?</h2>
        <a class="big-phone" href="tel:+919899982418">+91 98999 82418</a>
        <a class="text-link" href="contact.html">All office contacts {ARROW}</a>
        <a href="mailto:{INBOX}">{INBOX}</a>
      </div>
      <div class="aside-card">
        <h2>Pick from the catalogue</h2>
        <p>Open any product in our <a href="products.html">catalogue</a> and choose &ldquo;Add to enquiry&rdquo;. Your picks appear in this form.</p>
      </div>
    </div>
  </div>
</section>"""
    page("quote.html", "Request Quote",
         "Request a quotation from Chemotech International for panels, transformers, DG sets, UPS, VFD, PLC, SCADA, water treatment plants, hygiene stations, pre-fab structures, networking and CCTV.",
         body)



def profile_section(number, title, anchor):
    text=COMPANY["profile_pages"][str(number)]
    headings={'COMPANY DETAI LS','OF F ICES & GST REGISTRATIONS','BANKING & AUDIT','Head Office – Bihar','Delhi Office','Our Vision','Our Mission','We Value','TEAM','DESIGN','EXECUTION','Why Work With Us','Key Clients','Power & LED Display Projects','Automation, SCADA & WTP Instrumentation','Industrial Clients – VFD, PLC & Automation','Power & Electrical','Water & Wastewater','Automation & Instrumentation','Building, Energy & ICT'}
    replacements={'COMPANY DETAI LS':'COMPANY DETAILS','OF F ICES & GST REGISTRATIONS':'OFFICES & GST REGISTRATIONS','WE WI L L':'WE WILL','SAL ES, DESIGN & SERVICE TEAM':'SALES, DESIGN & SERVICE TEAM','END-TO-END, HANDL ED SEAML ESSLY':'END-TO-END, HANDLED SEAMLESSLY'}
    chunks=[];pending=[]
    def flush():
        if pending: chunks.append('<p>'+E(' '.join(pending))+'</p>');pending.clear()
    for line in text.splitlines():
        label=replacements.get(line,line)
        if line in headings or line in replacements:
            flush();chunks.append('<h3>'+E(label)+'</h3>')
        elif re.match(r'^(Name of the|Type of Company|Partners |Year of|PAN No\.|Phone |Email |HDFC Bank|A/c No\.|IFSC |Auditor |34\+|29\+|19\+|8\+|21 yrs|8 yrs|5 yrs|Since 2014|Ours is|We are passionate|CHEMOTECH is tough)',line):
            flush();pending.append(label)
        elif number==1:
            flush();chunks.append('<p>'+E(label)+'</p>')
        else: pending.append(label)
    flush()
    return f'<section class="section" id="{anchor}"><div class="wrap"><h2>{E(title)}</h2><div class="profile-transcript">{"".join(chunks)}</div></div></section>'

def profile_page(filename, title, sections):
    body=f'<section class="page-hero"><div class="wrap"><h1>{E(title)}</h1></div></section>'
    body+=''.join(profile_section(*section) for section in sections)
    page(filename,title,title+' · Chemotech International',body)

def home():
    profile_page('index.html','Chemotech International',[(1,'Company Profile','what-we-do'),(2,'Index · At a Glance','at-a-glance')])

def about():
    profile_page('about.html','About Chemotech',[(3,'Key Information','company-details'),(5,'Quality Policy','quality'),(6,'Vision, Mission & Values','vision'),(7,'About Chemotech','approach'),(8,'Our Team','team'),(9,'How We Work','how-we-work'),(10,'Our Execution Approach','execution')])

def solutions():
    body='<section class="page-hero"><div class="wrap"><h1>Our Solutions</h1></div></section>'
    for n,title,cid in [(16,'Power Backup, Generation & Power Quality','pd'),(17,'Automation, Instrumentation & Water','au'),(18,'Instrumentation & Control Rooms','instrumentation'),(19,'Building, Hygiene & Structures','bi'),(20,'Power, Energy & Water Plants','wp'),(21,'Process, Hygiene & Insulated Panels','process')]:
        body+=profile_section(n,title,cid)
        photos=[x for x in SOLUTIONS if x['group']==title]
        body+='<div class="wrap application-gallery">'+''.join(f'<a class="application-photo" href="products.html#p-{x["products"][0]}"><img src="{E(x["img"])}" alt="{E(x["title"])}" loading="lazy" width="{x["w"]}" height="{x["h"]}"><span><b>{E(x["title"])}</b><small>{E(x["make"])}</small></span></a>' for x in photos)+'</div>'
    body+=profile_section(22,'Our OEM Partners','partners')
    body+='<nav class="section-nav wrap" aria-label="Product categories">'+''.join(f'<a href="products.html#cat-{c[0]}">{E(c[1])}</a>' for c in CATEGORIES)+'</nav>'
    page('solutions.html','Our Solutions','Our Solutions · Chemotech International',body)

def projects():
    profile_page('projects.html','Our Clients',[(23,'Our Clients','clients'),(11,'Our Presence','presence')])
    legacy='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url=projects.html"><title>Company information</title>'+contact_stylesheet()+'</head><body><p><a href="projects.html">Our Clients</a> · <a href="about.html#company-details">Key Information</a></p><script>var h=location.hash;location.replace(h==="#partners"?"solutions.html#partners":h==="#company-details"?"about.html#company-details":"projects.html"+h)</script>'+contact_actions()+'</body></html>'
    Path(OUT,'company-profile.html').write_text(legacy,encoding='utf-8',newline='\n')

home(); about(); solutions(); products(); projects(); certifications(); contact(); quote()
print(f"built: {N_PRODUCTS} products, {N_VARIANTS} variants, {N_MAKES} makes, {len(SOLUTIONS)} solution photos")
