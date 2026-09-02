# Osha With Zahid

Website for Zahid Presswala, OSHA 10/30 Authorized Outreach Trainer (Construction & General Industry).

## Structure

Plain static HTML/CSS/JS, no build step required.

- `index.html`: Home
- `about.html`: About Zahid
- `services.html`: Training programs
- `book.html`: Online booking (single Typeform popup covering the request and scheduling)
- `contact.html`: Contact info & form
- `css/style.css`, `js/main.js`: shared styles/behavior
- `sitemap.xml`, `robots.txt`: SEO
- `404.html`: custom not-found page

## TODO before going live

1. Add a real `images/og-cover.png` (1200x630) for social share previews.
   Currently referenced but not included.
2. When ready for production, point the `oshawithzahid.com` DNS at GitHub
   Pages and add a `CNAME` file containing `oshawithzahid.com` to the repo
   root (not included yet since this deploy is for testing only).

Booking is handled entirely by the live Typeform popup
(`01M1J0JJRFGA8YMZEB1KJYTSVG`) on `book.html`, which covers both the
training request and scheduling in one form.

## Local preview

Just open `index.html` in a browser, or serve the folder with any static
server, e.g. `python3 -m http.server`.

## Deployment

Deployed via GitHub Pages from the `main` branch, root folder.
