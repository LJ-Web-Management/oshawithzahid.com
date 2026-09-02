# Osha With Zahid

Website for Zahid Presswala — OSHA 10/30 Authorized Outreach Trainer (Construction & General Industry).

## Structure

Plain static HTML/CSS/JS, no build step required.

- `index.html` — Home
- `about.html` — About Zahid
- `services.html` — Training programs
- `book.html` — Online booking (Calendly + Typeform)
- `contact.html` — Contact info & form
- `css/style.css`, `js/main.js` — shared styles/behavior
- `sitemap.xml`, `robots.txt` — SEO
- `404.html` — custom not-found page

## TODO before going live

1. **Calendly** — in `book.html`, replace the placeholder `data-url` on the
   `.calendly-inline-widget` div with Zahid's real Calendly scheduling link.
2. **Typeform** — in `book.html`, replace `REPLACE_WITH_TYPEFORM_ID` in the
   `data-tf-live` attribute with the real Typeform ID once provided.
3. Once both are live, remove the two `.embed-note` placeholder banners on
   `book.html`.
4. Add a real `images/og-cover.png` (1200x630) for social share previews —
   currently referenced but not included.
5. When ready for production, point the `oshawithzahid.com` DNS at GitHub
   Pages and add a `CNAME` file containing `oshawithzahid.com` to the repo
   root (not included yet since this deploy is for testing only).

## Local preview

Just open `index.html` in a browser, or serve the folder with any static
server, e.g. `python3 -m http.server`.

## Deployment

Deployed via GitHub Pages from the `main` branch, root folder.
