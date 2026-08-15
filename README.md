# Abdullahi Ndagi Adamu — Visual Artist Portfolio

A production-ready, static artist portfolio and publishing system for Nigerian visual artist **Abdullahi Ndagi Adamu**.
Visual-first, fast, accessible, GitHub Pages-compatible, with a Git-based CMS (Decap CMS) and automatic PDF generation.

---

## Architecture

```
abdullahi-ndagii/
├── content/                    # Structured content (JSON) — edit via CMS or by hand
│   ├── artist/profile.json     # Biography, statement, contact, social links
│   ├── artworks/*.json         # One file per artwork (title, year, medium, image, description…)
│   ├── projects/*.json         # One file per body of work / series (Witness Series, What We Carry…)
│   ├── exhibitions/*.json      # Exhibition history entries
│   ├── cv/cv.json              # Education, workshops, residencies, awards, publications, collections…
│   └── settings/site.json      # Site title, nav, base URL, downloads footer
├── templates/                  # Jinja2 templates — one per route plus print layouts
│   ├── base.html               # Shared shell: header, footer, intro animation, nav
│   ├── index.html              # Home: hero artwork, selected works, featured project, about, exhibitions
│   ├── work.html, artwork.html, projects.html, project.html
│   ├── about.html, exhibitions.html, cv.html, contact.html
│   ├── pdf_portfolio.html      # A3 print portfolio layout
│   ├── pdf_cv.html             # A4 print CV layout
│   └── pdf_project.html        # A3 print project PDF layout
├── src/
│   ├── build.py                # Build script: validate → copy static → render HTML → PDFs
│   ├── validate.py             # Content validator (required fields, refs, image existence)
│   ├── pdf_generator.py        # WeasyPrint-based PDF generator
│   └── utils.py                # Shared helpers, paths, content loading
├── static/
│   ├── css/styles.css          # Full design system (charcoal/ash/bone, editorial, gallery-like)
│   ├── js/main.js              # Animated intro (social arrivals), nav toggle, scroll state, reveal
│   └── icons/*.svg
├── images/                     # All artwork/portrait/project images
│   ├── artist/, artworks/, projects/ (recommended convention)
│   └── uploads/                # Decap CMS upload target
├── admin/                      # Decap CMS (Netlify CMS rename): browser-based Git CMS
│   ├── index.html              # Loads decap-cms.js
│   └── config.yml              # Collections, fields, GitHub backend, media paths
├── docs/                       # Guides (see docs/)
│   ├── CONTENT_GUIDE.md        # For the artist: adding/editing content without code
│   ├── CMS_SETUP.md            # Decap + GitHub OAuth + Cloudflare Worker step-by-step
│   ├── DEPLOYMENT.md           # GitHub Pages + Actions + custom domain
│   └── PDF_GUIDE.md            # Design & page-break notes, sizes, fonts, manual generation
├── public/                     # Generated output (deployed to GitHub Pages) — do not edit by hand
├── .github/workflows/deploy.yml
├── requirements.txt            # Python deps (jinja2, weasyprint, pyyaml, pillow)
├── .gitignore
└── README.md                   # This file
```

### Key design choices
- **Static only.** No server, no database. Everything is generated into `public/` and shipped to GitHub Pages.
- **Content as data.** Everything (text, metadata, image paths) lives in small JSON files under `content/` so a human (or a CMS) can edit it.
- **Git-based CMS.** Decap CMS (the FOSS Netlify CMS) edits the JSON files directly via GitHub PR/commits — no third-party SaaS required.
- **PDFs from same content.** PDFs are generated at build time from the *same* content model as the website (print-optimized A3/A4 templates; not screenshots).
- **GitHub Actions + Pages.** Every push to `main` validates content, renders HTML, regenerates PDFs, and publishes.

---

## Local development

### 1. Requirements
- Python **3.11+** (for Jinja2 and WeasyPrint).
- (Optional) Node **18+** if you want to run the Decap CMS local proxy: `npx decap-server`.
- (Recommended) Python virtualenv/pyenv or `python -m venv .venv`.

### 2. Install
```powershell
# Windows PowerShell 5 / pwsh
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux / macOS:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

> **WeasyPrint system dependencies (Linux / macOS)**: WeasyPrint needs Pango / Cairo / GDK-Pixbuf.
> On Ubuntu: `sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 libffi-dev libcairo2`.
> On macOS (Homebrew): `brew install pango cairo gdk-pixbuf libffi`.
> On Windows, the pip wheel usually ships the DLLs automatically.

### 3. Build (the only required command)
```bash
cd src && python build.py
```
Produces `../public/` with the full site, PDFs, and static assets.

### 4. Preview
Any static server from `public/`:
```bash
# Python built-in
cd public && python -m http.server 8080
# then open http://localhost:8080/
```

### 5. Validate content only (useful in pre-commit hooks)
```bash
cd src && python validate.py
```

### 6. (Optional) Run the CMS locally
Decap CMS provides a local proxy that bypasses OAuth. Useful for testing content editing without deploying the OAuth worker:
```bash
# Terminal 1 (static server on port 8081 to match default decap server)
cd public && python -m http.server 8081
# Terminal 2 (Decap CMS local proxy)
npx decap-server
# Open http://localhost:8081/admin/
```
`admin/config.yml` already has `local_backend: true`.

---

## Content structure (adding/editing by hand)

Every piece of content is a JSON file under `content/`. If you're not using the CMS, simply edit them with any text editor.

- **Add an artwork** → create `content/artworks/<slug>.json` using an existing file as template. Drop the image in `images/artworks/`. Reference the image path from `image`.
- **Add a project / series** → create `content/projects/<slug>.json`. List the artwork slugs inside `artworks: []` to associate them.
- **Add an exhibition** → create `content/exhibitions/<slug>.json`.
- **Edit bio/statement/contact** → edit `content/artist/profile.json`.
- **Edit CV (education, workshops, publications…) → edit `content/cv/cv.json`.
- **Edit nav / footer downloads** → edit `content/settings/site.json`.

Then run `python src/build.py` (and commit the changes — GitHub Actions will publish them).

Full non-technical walkthrough: see [`docs/CONTENT_GUIDE.md`](docs/CONTENT_GUIDE.md).

---

## Routes

| Path                | Purpose                                           |
|---------------------|---------------------------------------------------|
| `/`                 | Home (editorial: hero, statement, works, project) |
| `/work.html`        | All works — projects + individual works grid      |
| `/work/<slug>.html` | Single artwork page + prev/next + related         |
| `/projects.html`    | Bodies of work list                               |
| `/projects/<slug>.html` | Single project: statements, context, gallery |
| `/about.html`       | Biography + statement + practice, enquiry areas   |
| `/exhibitions.html` | Full exhibition list                              |
| `/cv.html`          | CV web view + CV PDF download                     |
| `/contact.html`     | Email, phone, socials, downloads                  |
| `/admin/`           | Decap CMS content manager                         |

PDFs are generated into `public/pdfs/`:
- `abdullahi-ndagi-adamu-portfolio.pdf` — full A3 print portfolio
- `abdullahi-ndagi-adamu-cv.pdf` — A4 CV
- `project-<slug>.pdf` — one A3 PDF per published project

---

## CMS usage (Decap CMS)

`/admin/` provides a clean browser interface for editing content *without touching code*.
A one-time OAuth setup is required because the CMS needs to commit to GitHub on your behalf.

**Short version:**
1. Create a GitHub OAuth app (Settings → Developer settings).
2. Deploy the *free* Cloudflare Worker OAuth gateway documented in `docs/CMS_SETUP.md` (copy-paste, ~5 minutes).
3. Fill `backend.base_url` and `backend.repo` in `admin/config.yml`.
4. Push to `main`.

Full walkthrough: [`docs/CMS_SETUP.md`](docs/CMS_SETUP.md).

---

## Deployment (GitHub Pages + Actions)

Automatic on every push to `main`:
1. Install Python + system libs for WeasyPrint.
2. Install `requirements.txt`.
3. Run content validation (`src/validate.py`) — **build fails if content is broken** (missing required fields, missing images, unknown refs).
4. Build (`src/build.py`) → HTML, sitemap, robots.txt, PDFs.
5. Publish `public/` as a Pages artifact and deploy.

To enable:
1. In your GitHub repo → **Settings → Pages** → set *Build and deployment → Source* to **GitHub Actions**.
2. Push to `main`.

Complete guide: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) (custom domain, troubleshooting).

---

## PDF generation

PDFs are generated from **dedicated print templates** (not HTML screenshots), with:
- A3 page size for portfolio & project PDFs, A4 for CV.
- Careful page-break control (`page-break-inside: avoid` on artworks + entries).
- Artwork-first layout with captions kept on the same page as images.
- Consistent visual identity (same serif/sans pairing, charcoal/bone palette).

If WeasyPrint is unavailable (missing system deps), `pdf_generator.py` falls back to writing the rendered HTML alongside the PDFs so you can open/print manually or run inside CI where the deps are present.

Walkthrough: [`docs/PDF_GUIDE.md`](docs/PDF_GUIDE.md).

---

## Accessibility & performance targets

- Semantic HTML5 landmarks, visible focus rings, skip-link.
- Alt text is loaded from artwork descriptions; portraits & project images have required `alt` rendering.
- Reduced-motion queries fully disable the intro animation and reveal effects.
- Mobile nav toggle with `aria-expanded`, `aria-controls`, closes on link click.
- Responsive typography (clamp() on all sizes) — scales from mobile → 4K.
- Lazy loading on non-hero images, `decoding="async"`, no heavy JS framework.

---

## Image guidelines

- **JPEG / WebP** preferred for photographs and paintings; PNG for logos only.
- Recommended sizes:
  - **Artwork**: longest edge **2400 px** (good for A3 prints and retina screens). File size: ≤ 2 MB after compression.
  - **Thumbnail**: not strictly required; the CMS can fall back to the main image.
  - **Project hero/cover**: 16:9, longest edge ≥ **1920 px**.
  - **Portrait**: 4:5, ≥ 1200 px tall.
- Preserve original proportions — templates use `object-fit: contain` for single-artwork display and `cover` for grid thumbs (with generous safe aspect ratios so crops are minimal).
- Do NOT crop artwork images unless it is purely to remove a gallery mat or white edge.

---

## Troubleshooting

| Symptom                                                    | Fix                                                                                           |
|------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| `pip install weasyprint` fails on Windows / Linux / macOS  | Install system Pango/Cairo (under Local dev → WeasyPrint system dependencies above).          |
| PDF font looks blurry / missing                            | Google Fonts are loaded from CDN in the print HTML; verify CI has internet access.            |
| Build fails with 3+ content validation errors              | The error messages tell you which file/field is missing or references a non-existent image.   |
| Admin /admin says "Failed to load settings" / 404          | Make sure you're serving the built `public/admin/` folder (not repo root).                    |
| GitHub Pages shows 404                                     | 1) Pages → Source set to "GitHub Actions", 2) Wait 2–3 min for deploy, 3) try `yourname.github.io/repo/`. |

---

## License & credits

- Original developer-portfolio template by Muhammad Idris (Muhammad-Idris24.github.io) — data model and build approach repurposed significantly.
- Site code: © Abdullahi Ndagi Adamu.
- Artworks, texts, and images: © Abdullahi Ndagi Adamu, all rights reserved.
- Third-party: Decap CMS (MIT), Jinja2 (BSD-3), WeasyPrint (BSD-3), Cormorant Garamond + Inter (OFL).
