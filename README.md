# Osha With Zahid

Website for Zahid Presswala, OSHA 10/30 Authorized Outreach Trainer (Construction & General Industry).

## Structure

Static HTML/CSS/JS served by GitHub Pages. The published HTML is generated
from sources in `_src/` by a small Python script, and the generated files are
committed, so GitHub Pages needs no build step.

- `_src/pages/*.html`: source for the main pages (home, courses, about, book, contact, guides hub, 404)
- `_src/guides/*.html`: one file per guide/article
- `_tools/build.py`: generator (shared header/footer, schema markup, sitemap, llms.txt)
- `index.html`, `services.html`, `about.html`, `book.html`, `contact.html`, `404.html`, `guides/`: **generated, don't edit by hand**
- `css/style.css`, `js/main.js`: shared styles/behavior (edit directly)
- `images/`: site logo (`logo.svg`, `logo-reversed.svg`), Google logo (`logo.png`), favicons, and social share image (`og-cover.png`)
- `brand/logo/`: full logo kit (all versions in SVG and PNG, icons, social avatar, preview sheet)
- `robots.txt`: allows search engines and AI crawlers
- `sitemap.xml`, `llms.txt`, `llms-full.txt`: **generated**

Folders starting with `_` are ignored by GitHub Pages, so sources are never published.

## Editing

1. Edit a file in `_src/` (or add a new guide in `_src/guides/`).
2. Run `python3 _tools/build.py` (Python 3.8+, no dependencies).
3. Commit both the source and the generated files.

### Adding a guide

Copy an existing file in `_src/guides/` and rename it; the filename becomes
the URL (`_src/guides/my-topic.html` -> `/guides/my-topic.html`). The JSON
block at the top sets:

- `title`, `short` (used in breadcrumbs/footer), `seo_title`, `description`, `dek`
- `category`: `cards`, `hazards`, or `employers`
- `answer`: the "Quick answer" box (keep it to 2-3 sentences; this is what search engines and AI assistants quote)
- `takeaways`, `faq` (rendered on the page and as FAQPage schema), `sources`, `related`
- `featured: true` to show it on the home and about pages; `order` for sort order
- `published` / `updated` dates (update `updated` when you revise a guide)

The body is plain HTML. Every `<h2>` gets an id and appears in the table of contents automatically.

## SEO / AI search

- JSON-LD on every page: LocalBusiness/ProfessionalService + Person (home), ProfilePage (about),
  Course (courses), CollectionPage (guides), Article + FAQPage + BreadcrumbList (each guide).
- `llms.txt` / `llms-full.txt` give AI assistants a clean summary and the full text of every guide.
- Guides are written answer-first with a quick answer, key takeaways, and FAQs.

Booking is handled by the live Typeform (`01M1J0JJRFGA8YMZEB1KJYTSVG`) embedded on `book.html`.

## Local preview

`python3 -m http.server` from the repo root, then open http://localhost:8000.

## Deployment

Deployed via GitHub Pages from the `main` branch, root folder, with the custom domain in `CNAME`.
