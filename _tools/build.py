#!/usr/bin/env python3
"""Static site generator for oshawithzahid.com.

Sources live in _src/ (pages/ and guides/). Each source file starts with a
JSON front-matter block inside an HTML comment, followed by the page body.
Running this script writes finished HTML to the repo root, plus sitemap.xml,
llms.txt and llms-full.txt. GitHub Pages (Jekyll) ignores folders that start
with an underscore, so _src/ and _tools/ are never published.

Usage:  python3 _tools/build.py
"""

import datetime
import html
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"
SITE = "https://oshawithzahid.com"
GA_ID = "G-KH6SW3MELB"
PHONE = "(847) 863-4798"
PHONE_TEL = "+18478634798"
EMAIL = "zahidh786@gmail.com"
OSHA_VERIFY = "https://www.osha.gov/dte/outreach/outreach_trainers?page=0&last_name=Presswala"
OG_IMAGE = SITE + "/images/og-cover.png"

NAV = [
    ("home", "Home", ""),
    ("services", "Courses", "services.html"),
    ("guides", "Guides", "guides/"),
    ("about", "About", "about.html"),
    ("contact", "Contact", "contact.html"),
]

CATEGORIES = {
    "cards": "OSHA Cards",
    "hazards": "Hazards & Standards",
    "employers": "For Employers",
}

# Simple stroke icons (24x24, Lucide-style).
ICONS = {
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
    "shield": '<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z"/><path d="m9 12 2 2 4-4"/>',
    "hardhat": '<path d="M2 18h20"/><path d="M4 18v-3a8 8 0 0 1 16 0v3"/><path d="M10 7V5h4v2"/><path d="M10 7v5M14 7v5"/>',
    "factory": '<path d="M3 21V10l6 4V10l6 4V6l6-3v18z"/><path d="M7 17h2M12 17h2M17 17h2"/>',
    "map-pin": '<path d="M12 21s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M18 14a6.5 6.5 0 0 1 3.5 6"/>',
    "clipboard": '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V3h6v1"/><path d="m9 13 2 2 4-4"/>',
    "card": '<rect x="2.5" y="5" width="19" height="14" rx="2.5"/><circle cx="8" cy="11" r="2"/><path d="M5.5 16a3 3 0 0 1 5 0M14 10h4M14 13h3"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "book": '<path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v17H6.5A2.5 2.5 0 0 0 4 21.5z"/><path d="M4 21.5A2.5 2.5 0 0 1 6.5 19H20v3H6.5"/>',
    "alert": '<path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17.5v.01"/>',
    "ladder": '<path d="M7 2v20M17 2v20M7 6h10M7 11h10M7 16h10"/>',
    "zap": '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
    "scale": '<path d="M12 3v18M5 21h14M6 7h12"/><path d="m6 7-3 7a3 3 0 0 0 6 0zM18 7l-3 7a3 3 0 0 0 6 0z"/>',
    "monitor": '<rect x="2.5" y="4" width="19" height="13" rx="2"/><path d="M8 21h8M12 17v4"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "award": '<circle cx="12" cy="9" r="6"/><path d="m8.5 14-1.5 8 5-3 5 3-1.5-8"/>',
    "tool": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z"/>',
    "message": '<path d="M4 4h16v12H8l-4 4z"/>',
}

LOGO = ('<svg class="mark" viewBox="0 0 40 56" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
        '<defs><clipPath id="{cid}"><rect width="40" height="56"/></clipPath></defs>'
        '<path d="M9 0h22l9 9v47H0V9z" fill="#0A6B47"/><circle cx="20" cy="10" r="3.6" fill="#F2F1EB" stroke="#C8F23A" stroke-width="1.6"/>'
        '<path d="M9 19h22v5.5L17 37.5h14V43H9v-5.5L23 24.5H9z" fill="#F2F1EB"/><rect y="47" width="40" height="9" fill="#C8F23A"/>'
        '<g fill="#0D1A14" clip-path="url(#{cid})"><path d="M-12 56h3.5l9-9H-3z"/><path d="M-5 56h3.5l9-9H4z"/><path d="M2 56h3.5l9-9H11z"/>'
        '<path d="M9 56h3.5l9-9H18z"/><path d="M16 56h3.5l9-9H25z"/><path d="M23 56h3.5l9-9H32z"/><path d="M30 56h3.5l9-9H39z"/>'
        '<path d="M37 56h3.5l9-9H46z"/></g></svg>')


def icon(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def esc(s):
    return html.escape(s, quote=True)


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"\s*<!--(.*?)-->\s*", text, re.S)
    if not m:
        raise SystemExit(f"{path}: missing front matter")
    meta = json.loads(m.group(1))
    return meta, text[m.end():]


def slugify(s):
    s = re.sub(r"<[^>]+>", "", s).lower()
    s = re.sub(r"&[a-z]+;", "", s)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def strip_tags(s):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S)
    s = re.sub(r"<br\s*/?>|</(p|li|h[1-6]|tr|div|summary)>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n\n", s).strip()


def fmt_date(d):
    d = datetime.date.fromisoformat(d)
    return f"{d:%B} {d.day}, {d.year}"


def ld(obj):
    return ('<script type="application/ld+json">\n'
            + json.dumps(obj, indent=2, ensure_ascii=False).replace("</", "<\\/")
            + "\n</script>")


# ---------- Shared schema ----------

ORG_ID = SITE + "/#business"
PERSON_ID = SITE + "/#zahid"

PERSON = {
    "@type": "Person",
    "@id": PERSON_ID,
    "name": "Zahid Presswala",
    "jobTitle": "OSHA Authorized Outreach Trainer",
    "description": "OSHA-authorized Outreach Trainer for Construction and General Industry with 25+ years of field experience, based in Naperville, Illinois.",
    "url": SITE + "/about.html",
    "email": "mailto:" + EMAIL,
    "telephone": "+1-847-863-4798",
    "knowsLanguage": ["English", "Gujarati", "Urdu"],
    "knowsAbout": ["OSHA 10-Hour Construction", "OSHA 30-Hour Construction", "OSHA 10-Hour General Industry",
                   "OSHA 30-Hour General Industry", "Fall protection", "Hazard communication",
                   "Construction safety", "Workplace safety compliance"],
    "hasCredential": {
        "@type": "EducationalOccupationalCredential",
        "name": "OSHA Outreach Training Program Authorized Trainer (Construction and General Industry)",
        "recognizedBy": {"@type": "GovernmentOrganization", "name": "Occupational Safety and Health Administration", "url": "https://www.osha.gov"},
    },
    "worksFor": {"@id": ORG_ID},
    "sameAs": [OSHA_VERIFY],
}

BUSINESS = {
    "@type": ["ProfessionalService", "EducationalOrganization"],
    "@id": ORG_ID,
    "name": "Osha With Zahid",
    "alternateName": "Zahid Presswala OSHA Training",
    "url": SITE + "/",
    "logo": SITE + "/images/logo.png",
    "image": OG_IMAGE,
    "description": "OSHA-authorized Outreach training for Construction and General Industry: OSHA 10-Hour and 30-Hour courses delivered on-site or in group sessions, taught by Zahid Presswala in English, Gujarati, and Urdu.",
    "telephone": "+1-847-863-4798",
    "email": EMAIL,
    "priceRange": "$$",
    "founder": {"@id": PERSON_ID},
    "address": {"@type": "PostalAddress", "addressLocality": "Naperville", "addressRegion": "IL", "addressCountry": "US"},
    "areaServed": [
        {"@type": "City", "name": "Naperville, IL"},
        {"@type": "City", "name": "Chicago, IL"},
        {"@type": "AdministrativeArea", "name": "Chicagoland"},
        {"@type": "State", "name": "Illinois"},
        {"@type": "Country", "name": "United States"},
    ],
    "knowsLanguage": ["English", "Gujarati", "Urdu"],
    "sameAs": [OSHA_VERIFY],
    "hasOfferCatalog": {
        "@type": "OfferCatalog",
        "name": "OSHA Outreach Training Courses",
        "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Course", "name": n, "url": SITE + "/services.html#" + a}}
            for n, a in [("OSHA 10-Hour Construction", "c10"), ("OSHA 30-Hour Construction", "c30"),
                         ("OSHA 10-Hour General Industry", "gi10"), ("OSHA 30-Hour General Industry", "gi30")]
        ],
    },
}


# ---------- Layout pieces ----------

def head(meta, root, canonical):
    title = meta["title"]
    desc = meta["description"]
    og_type = meta.get("og_type", "website")
    robots = "noindex, follow" if meta.get("noindex") else "index, follow, max-image-preview:large, max-snippet:-1"
    extra = "\n".join(meta.get("_ld", []))
    article_meta = ""
    if og_type == "article":
        article_meta = (f'\n<meta property="article:published_time" content="{meta["published"]}">'
                        f'\n<meta property="article:modified_time" content="{meta["updated"]}">'
                        f'\n<meta property="article:author" content="Zahid Presswala">'
                        f'\n<meta property="article:section" content="{esc(CATEGORIES[meta["category"]])}">')
    canon = f'<link rel="canonical" href="{canonical}">\n' if canonical else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', '{GA_ID}');
</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#0b2a20">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{canon}<meta name="robots" content="{robots}">
<meta name="author" content="Zahid Presswala">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Osha With Zahid">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{esc(meta.get('og_title', title))}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical or SITE + '/'}">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Osha With Zahid: OSHA 10 and 30-Hour training with Zahid Presswala">{article_meta}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(meta.get('og_title', title))}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{OG_IMAGE}">
<link rel="icon" type="image/svg+xml" href="{root}favicon.svg">
<link rel="alternate" type="text/plain" title="LLM summary" href="{root}llms.txt">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}css/style.css">
{extra}
</head>"""


def header(active, root):
    current = ' aria-current="page"'
    links = "\n".join(
        f'      <a href="{root}{href or "index.html"}"{current if key == active else ""}>{label}</a>'
        for key, label, href in NAV
    )
    return f"""<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="container nav">
    <a href="{root}index.html" class="brand" aria-label="Osha With Zahid, home">
      {LOGO.format(cid="lh")}
      <span class="brand-name">Osha With Zahid<small>OSHA Authorized Outreach Trainer</small></span>
    </a>
    <nav class="nav-links" id="navLinks" aria-label="Primary">
{links}
    </nav>
    <div class="nav-cta">
      <a class="nav-phone" href="tel:{PHONE_TEL}">{icon("phone")}{PHONE}</a>
      <a href="{root}book.html" class="btn btn-primary btn-sm">Book training</a>
      <button class="nav-toggle" aria-label="Toggle menu" aria-expanded="false" aria-controls="navLinks">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</header>
"""


def footer(root, guides, extra_scripts=""):
    guide_links = "\n".join(
        f'          <li><a href="{root}guides/{g["slug"]}.html">{esc(g["short"])}</a></li>' for g in guides[:5]
    )
    return f"""
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <div class="footer-brand">{LOGO.format(cid="lf")}<span>Osha With Zahid</span></div>
        <p>OSHA 10 and 30-Hour Outreach training for Construction and General Industry, taught by Zahid Presswala. Based in Naperville, IL, serving Chicagoland and available on-site nationwide.</p>
        <p><a href="{OSHA_VERIFY}" target="_blank" rel="noopener">Verify Zahid on OSHA.gov &nearr;</a></p>
      </div>
      <div>
        <h4>Courses</h4>
        <ul>
          <li><a href="{root}services.html#c10">OSHA 10 Construction</a></li>
          <li><a href="{root}services.html#c30">OSHA 30 Construction</a></li>
          <li><a href="{root}services.html#gi10">OSHA 10 General Industry</a></li>
          <li><a href="{root}services.html#gi30">OSHA 30 General Industry</a></li>
          <li><a href="{root}book.html">Book a session</a></li>
        </ul>
      </div>
      <div>
        <h4>Guides</h4>
        <ul>
{guide_links}
          <li><a href="{root}guides/">All guides &rarr;</a></li>
        </ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul>
          <li><a href="tel:{PHONE_TEL}">{PHONE}</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li>Naperville, IL</li>
          <li><a href="{root}about.html">About Zahid</a></li>
          <li><a href="{root}contact.html">Contact page</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; <span data-year>{datetime.date.today().year}</span> Zahid Presswala. All rights reserved.</span>
      <span>Site by LJ Web Management</span>
    </div>
  </div>
</footer>

<script src="{root}js/main.js"></script>{extra_scripts}
</body>
</html>
"""


def breadcrumbs_ld(crumbs):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE + "/" + path}
            for i, (name, path) in enumerate(crumbs)
        ],
    }


def breadcrumbs_html(crumbs, root):
    items = []
    for i, (name, path) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            items.append(f'<li aria-current="page">{esc(name)}</li>')
        else:
            items.append(f'<li><a href="{root}{path or "index.html"}">{esc(name)}</a></li>')
    return f'<ol class="crumbs" aria-label="Breadcrumb">{"".join(items)}</ol>'


def faq_ld(faq):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
            for q, a in faq
        ],
    }


def faq_html(faq):
    items = "\n".join(
        f'  <details>\n    <summary>{esc(q)}</summary>\n    <div class="answer"><p>{a}</p></div>\n  </details>'
        for q, a in faq
    )
    return f'<div class="faq">\n{items}\n</div>'


def guide_card(g, root, heading="h3"):
    return f"""<a class="card guide-card reveal" href="{root}guides/{g['slug']}.html" data-category="{g['category']}">
  <div class="thumb {g.get('theme', 't1')}">{icon(g.get('icon', 'book'))}<span class="tag">{esc(CATEGORIES[g['category']])}</span></div>
  <div class="body">
    <{heading}>{esc(g['title'])}</{heading}>
    <p>{esc(g['description'])}</p>
    <div class="meta"><span>{g['read_min']} min read</span><span>Updated {fmt_date(g['updated'])}</span></div>
  </div>
</a>"""


def cta_band(root, title="Ready to get your crew trained?",
             text="Book OSHA 10 or 30-Hour training on-site at your location. One short form, and Zahid follows up to confirm the details."):
    return f"""<section class="section--tight">
  <div class="container">
    <div class="cta-band reveal">
      <div>
        <h2>{title}</h2>
        <p>{text}</p>
      </div>
      <div class="actions">
        <a href="{root}book.html" class="btn btn-hivis">Book a session {icon("arrow")}</a>
        <a href="tel:{PHONE_TEL}" class="btn btn-ghost-dark">{icon("phone")} {PHONE}</a>
      </div>
    </div>
  </div>
</section>"""


# ---------- Build ----------

def load_guides():
    guides = []
    for path in sorted((SRC / "guides").glob("*.html")):
        meta, body = parse(path)
        meta["slug"] = path.stem
        meta["body"] = body
        words = len(strip_tags(body + " ".join(a for _, a in meta.get("faq", []))).split())
        meta["read_min"] = max(3, math.ceil(words / 230))
        meta.setdefault("short", meta["title"])
        guides.append(meta)
    guides.sort(key=lambda g: (g.get("order", 99), g["title"]))
    return guides


def render_template(body, root, guides, meta):
    def repl(m):
        key, _, arg = m.group(1).partition(":")
        if key == "root":
            return root
        if key == "icon":
            return icon(arg)
        if key == "phone":
            return PHONE
        if key == "tel":
            return PHONE_TEL
        if key == "email":
            return EMAIL
        if key == "verify":
            return esc(OSHA_VERIFY)
        if key == "faq":
            return faq_html(meta["faq"])
        if key == "cta":
            return cta_band(root)
        if key == "crumbs":
            return breadcrumbs_html(meta["breadcrumbs"], root)
        if key == "guides":
            picked = guides if arg == "all" else [g for g in guides if g.get("featured")][: int(arg)]
            return "\n".join(guide_card(g, root) for g in picked)
        if key == "filters":
            btns = ['<button class="filter" data-filter="all" aria-pressed="true">All guides</button>']
            btns += [f'<button class="filter" data-filter="{k}" aria-pressed="false">{esc(v)}</button>' for k, v in CATEGORIES.items()]
            return '<div class="filters" role="group" aria-label="Filter guides by topic">' + "".join(btns) + "</div>"
        raise SystemExit(f"unknown template tag {m.group(0)}")
    return re.sub(r"\{\{([a-z]+(?::[a-z0-9-]+)?)\}\}", repl, body)


def build_page(path, guides):
    meta, body = parse(path)
    out = meta["out"]
    depth = out.count("/")
    root = "/" if meta.get("absolute") else "../" * depth
    url_path = "" if out == "index.html" else out.replace("index.html", "")
    canonical = None if meta.get("noindex") else f"{SITE}/{url_path}"

    lds = []
    if meta.get("schema") == "home":
        lds.append({"@context": "https://schema.org", "@graph": [
            BUSINESS, PERSON,
            {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "Osha With Zahid",
             "publisher": {"@id": ORG_ID}, "inLanguage": "en-US"},
        ]})
    elif meta.get("schema") == "about":
        lds.append({"@context": "https://schema.org", "@type": "ProfilePage", "url": canonical,
                    "mainEntity": PERSON, "about": {"@id": ORG_ID}})
    elif meta.get("schema") == "services":
        courses = []
        for cid, name, desc, hours, field in [
            ("c10", "OSHA 10-Hour Construction", "Entry-level OSHA Outreach course on recognizing and preventing common construction hazards, including the Focus Four. Ends with an official DOL wallet card.", 10, "Construction"),
            ("c30", "OSHA 30-Hour Construction", "In-depth OSHA Outreach course for supervisors, foremen, and workers with safety responsibility on construction sites. Ends with an official DOL wallet card.", 30, "Construction"),
            ("gi10", "OSHA 10-Hour General Industry", "Entry-level OSHA Outreach course for warehouse, manufacturing, and facility workers. Ends with an official DOL wallet card.", 10, "General Industry"),
            ("gi30", "OSHA 30-Hour General Industry", "Comprehensive OSHA Outreach course for supervisors and safety coordinators in general industry. Ends with an official DOL wallet card.", 30, "General Industry"),
        ]:
            courses.append({
                "@type": "Course", "@id": f"{SITE}/services.html#{cid}", "name": name, "description": desc,
                "url": f"{SITE}/services.html#{cid}", "provider": {"@id": ORG_ID},
                "educationalCredentialAwarded": f"DOL OSHA {hours}-Hour {field} wallet card",
                "inLanguage": ["en", "gu", "ur"], "teaches": f"OSHA {field} safety standards and hazard recognition",
                "timeRequired": f"PT{hours}H",
                "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "Onsite", "courseWorkload": f"PT{hours}H",
                                      "instructor": {"@id": PERSON_ID}, "location": {"@type": "Place", "name": "Your job site or a shared venue", "address": {"@type": "PostalAddress", "addressLocality": "Naperville", "addressRegion": "IL", "addressCountry": "US"}}},
                "offers": {"@type": "Offer", "category": "Paid", "url": SITE + "/book.html", "availability": "https://schema.org/InStock"},
            })
        lds.append({"@context": "https://schema.org", "@graph": [BUSINESS, PERSON] + courses})
    elif meta.get("schema") == "guides":
        lds.append({"@context": "https://schema.org", "@type": "CollectionPage", "name": meta["title"],
                    "url": canonical, "description": meta["description"],
                    "mainEntity": {"@type": "ItemList", "itemListElement": [
                        {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/guides/{g['slug']}.html", "name": g["title"]}
                        for i, g in enumerate(guides)]}})
    if meta.get("breadcrumbs"):
        lds.append(breadcrumbs_ld(meta["breadcrumbs"]))
    if meta.get("faq"):
        lds.append(faq_ld(meta["faq"]))
    meta["_ld"] = [ld(x) for x in lds]

    content = render_template(body, root, guides, meta)
    extra = meta.get("scripts", "")
    page = head(meta, root, canonical) + "\n" + header(meta.get("nav"), root) + content + footer(root, guides, extra)
    (ROOT / out).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / out).write_text(page, encoding="utf-8")
    return {"loc": canonical, "meta": meta, "text": strip_tags(content)} if canonical else None


def build_guide(g, guides):
    root = "../"
    canonical = f"{SITE}/guides/{g['slug']}.html"
    body = g["body"]

    # Give every h2 an id, and collect them for the table of contents.
    toc = []
    def h2(m):
        attrs, inner = m.group(1), m.group(2)
        idm = re.search(r'id="([^"]+)"', attrs)
        hid = idm.group(1) if idm else slugify(inner)
        toc.append((hid, re.sub(r"<[^>]+>", "", inner)))
        return f'<h2 id="{hid}">{inner}</h2>' if not idm else m.group(0)
    body = re.sub(r"<h2([^>]*)>(.*?)</h2>", h2, body)
    body = render_template(body, root, guides, g)

    crumbs = [("Home", ""), ("Guides", "guides/"), (g["short"], f"guides/{g['slug']}.html")]
    faq = g.get("faq", [])
    if faq:
        toc.append(("faq", "Frequently asked questions"))

    article_ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "@id": canonical + "#article",
        "headline": g["title"],
        "description": g["description"],
        "image": OG_IMAGE,
        "datePublished": g["published"],
        "dateModified": g["updated"],
        "author": {**PERSON, "worksFor": {"@type": "Organization", "name": "Osha With Zahid", "url": SITE + "/"}},
        "publisher": {"@type": "Organization", "@id": ORG_ID, "name": "Osha With Zahid", "url": SITE + "/",
                      "logo": {"@type": "ImageObject", "url": SITE + "/images/logo.png"}},
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "articleSection": CATEGORIES[g["category"]],
        "keywords": g.get("keywords", []),
        "inLanguage": "en-US",
        "wordCount": len(strip_tags(body).split()),
        "about": g.get("about", []),
        "isAccessibleForFree": True,
    }
    if g.get("answer"):
        article_ld["abstract"] = strip_tags(g["answer"])
    lds = [article_ld, breadcrumbs_ld(crumbs)]
    if faq:
        lds.append(faq_ld(faq))

    meta = {
        "title": g.get("seo_title", g["title"] + " | Osha With Zahid"),
        "og_title": g["title"],
        "description": g["description"],
        "og_type": "article",
        "published": g["published"],
        "updated": g["updated"],
        "category": g["category"],
        "_ld": [ld(x) for x in lds],
    }

    toc_html = "\n".join(f'          <li><a href="#{hid}">{esc(t)}</a></li>' for hid, t in toc)
    answer = ""
    if g.get("answer"):
        answer = f'<div class="answer-box"><span class="eyebrow">{icon("check-circle")} Quick answer</span><p>{g["answer"]}</p></div>'
    takeaways = ""
    if g.get("takeaways"):
        lis = "".join(f"<li>{icon('check')}<span>{t}</span></li>" for t in g["takeaways"])
        takeaways = f'<div class="takeaways"><h2 id="key-takeaways">Key takeaways</h2><ul>{lis}</ul></div>'
    faq_block = ""
    if faq:
        faq_block = f'<section class="article-faq"><h2 id="faq">Frequently asked questions</h2>\n{faq_html(faq)}</section>'
    sources = ""
    if g.get("sources"):
        lis = "".join(f'<li><a href="{esc(u)}" target="_blank" rel="noopener">{esc(t)}</a></li>' for t, u in g["sources"])
        sources = f'<div class="sources"><h2 id="sources">Sources &amp; further reading</h2><ul>{lis}</ul></div>'

    related = [x for x in guides if x["slug"] in g.get("related", [])]
    if len(related) < 3:
        related += [x for x in guides if x["slug"] != g["slug"] and x not in related and x["category"] == g["category"]]
        related += [x for x in guides if x["slug"] != g["slug"] and x not in related]
    related_html = "\n".join(guide_card(x, root) for x in related[:3])

    content = f"""<main id="main">
  <article>
  <header class="article-hero">
    <div class="container">
      {breadcrumbs_html(crumbs, root)}
      <span class="tag tag--green">{esc(CATEGORIES[g['category']])}</span>
      <h1 style="margin-top:16px">{esc(g['title'])}</h1>
      <p class="dek">{g['dek']}</p>
      <div class="byline">
        <span class="avatar" aria-hidden="true">ZP</span>
        <div class="who"><strong>By <a href="{root}about.html" rel="author">Zahid Presswala</a></strong>OSHA Authorized Outreach Trainer &middot; Updated <time datetime="{g['updated']}">{fmt_date(g['updated'])}</time> &middot; {g['read_min']} min read</div>
      </div>
    </div>
  </header>

  <div class="container article-layout">
    <div class="prose">
      {answer}
      {takeaways}
{body}
      {faq_block}
      {sources}
      <div class="author-box">
        <span class="avatar" aria-hidden="true">ZP</span>
        <div>
          <h3>About the author</h3>
          <p>Zahid Presswala is an OSHA-authorized Outreach Trainer for Construction and General Industry with more than 25 years of hands-on field experience. He teaches OSHA 10 and 30-Hour courses on-site across Chicagoland and beyond, in English, Gujarati, and Urdu.</p>
          <a href="{root}about.html">More about Zahid &rarr;</a> &nbsp; <a href="{esc(OSHA_VERIFY)}" target="_blank" rel="noopener">Verify on OSHA.gov &nearr;</a>
        </div>
      </div>
    </div>
    <aside class="article-aside" aria-label="On this page">
      <div class="sticky">
        <nav class="toc" aria-label="Table of contents">
          <h4>On this page</h4>
          <ol>
{toc_html}
          </ol>
        </nav>
        <div class="aside-cta">
          <h4>Train your crew with Zahid</h4>
          <p>OSHA 10 &amp; 30-Hour courses on-site at your location. Official DOL cards.</p>
          <a href="{root}book.html" class="btn btn-hivis btn-sm">Book a session {icon('arrow')}</a>
        </div>
      </div>
    </aside>
  </div>
  </article>

  <section class="section section--white">
    <div class="container">
      <div class="sec-head-row">
        <div class="sec-head"><span class="eyebrow">Keep reading</span><h2>Related guides</h2></div>
        <a href="{root}guides/" class="btn btn-ghost">All guides {icon('arrow')}</a>
      </div>
      <div class="grid grid-3">
{related_html}
      </div>
    </div>
  </section>

  {cta_band(root)}
</main>
"""
    page = head(meta, root, canonical) + "\n" + header("guides", root) + content + footer(root, guides)
    out = ROOT / "guides" / f"{g['slug']}.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page, encoding="utf-8")
    text = strip_tags(f"<p>{g.get('answer', '')}</p>" + body + "".join(f"<h3>{q}</h3><p>{a}</p>" for q, a in faq))
    return {"loc": canonical, "meta": g, "text": text}


def write_sitemap(entries):
    rows = []
    for e in entries:
        lastmod = e["meta"].get("updated", BUILD_DATE)
        prio = e["meta"].get("priority", "0.7")
        rows.append(f"  <url>\n    <loc>{e['loc']}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <priority>{prio}</priority>\n  </url>")
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(rows) + "\n</urlset>\n", encoding="utf-8")


def write_llms(pages, guides_out):
    intro = f"""# Osha With Zahid

> Osha With Zahid is the training business of Zahid Presswala, an OSHA-authorized Outreach Trainer for Construction and General Industry based in Naperville, Illinois. Zahid has 25+ years of hands-on field experience and teaches OSHA 10-Hour and 30-Hour Outreach courses on-site at job sites, shops, and offices across Chicagoland and nationwide, in English, Gujarati, and Urdu. Every course ends with an official U.S. Department of Labor (DOL) OSHA wallet card.

Key facts:
- Trainer: Zahid Presswala, OSHA Outreach Training Program authorized trainer (Construction and General Industry). Verify: {OSHA_VERIFY}
- Courses: OSHA 10-Hour Construction, OSHA 30-Hour Construction, OSHA 10-Hour General Industry, OSHA 30-Hour General Industry, plus custom safety workshops and toolbox talks.
- Format: in-person, on-site at the client's location or at a shared venue; group pricing available.
- Languages: English, Gujarati, Urdu.
- Service area: Naperville, Chicago and the Chicagoland suburbs, Illinois; on-site travel nationwide by arrangement.
- Booking: {SITE}/book.html
- Phone: +1 {PHONE}
- Email: {EMAIL}
"""
    lines = [intro, "## Main pages\n"]
    for e in pages:
        lines.append(f"- [{e['meta'].get('llms_title', e['meta']['title'])}]({e['loc']}): {e['meta']['description']}")
    lines.append("\n## Guides\n")
    for e in guides_out:
        g = e["meta"]
        lines.append(f"- [{g['title']}]({e['loc']}): {g['description']}")
    lines.append(f"\n## Optional\n\n- [Full text of all guides]({SITE}/llms-full.txt): plain-text version of every guide on this site.\n")
    (ROOT / "llms.txt").write_text("\n".join(lines), encoding="utf-8")

    full = [intro]
    for e in guides_out:
        g = e["meta"]
        full.append(f"\n---\n\n# {g['title']}\n\nURL: {e['loc']}\nAuthor: Zahid Presswala, OSHA Authorized Outreach Trainer\nUpdated: {g['updated']}\n\n{e['text']}\n")
    (ROOT / "llms-full.txt").write_text("\n".join(full), encoding="utf-8")


BUILD_DATE = datetime.date.today().isoformat()


def main():
    guides = load_guides()
    pages = [p for p in (build_page(path, guides) for path in sorted((SRC / "pages").glob("*.html"))) if p]
    pages.sort(key=lambda e: -float(e["meta"].get("priority", "0.5")))
    guides_out = [build_guide(g, guides) for g in guides]
    write_sitemap(pages + guides_out)
    write_llms(pages, guides_out)
    print(f"Built {len(pages)} pages and {len(guides_out)} guides.")


if __name__ == "__main__":
    main()
