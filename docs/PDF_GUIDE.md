# PDF Guide — layout, sizes, page breaks & regeneration

This project generates **three kinds of PDFs** automatically on every build. They are written from dedicated print-optimized HTML/CSS templates (not web screenshots).

| PDF | Page size | Source template | Output path in build |
|-----|-----------|-----------------|----------------------|
| Artist Portfolio | A3 landscape-ready | `templates/pdf_portfolio.html` | `public/pdfs/abdullahi-ndagi-adamu-portfolio.pdf` |
| Artist CV | A4 portrait | `templates/pdf_cv.html` | `public/pdfs/abdullahi-ndagi-adamu-cv.pdf` |
| Per-project PDF (one per published project) | A3 | `templates/pdf_project.html` | `public/pdfs/project-<slug>.pdf` |

---

## What's inside each PDF

### 1. Artist Portfolio PDF (A3)
1. Cover page: mark / monogram, artist name, title, date, copyright.
2. Biography + Artist statement + Contact block.
3. Each featured artwork (up to the first 12 published) on its own page with title, year, medium, dimensions, series, and description as caption. No awkward splits across pages — each artwork is `page-break-inside: avoid`.
4. Projects summary — one per section.
5. CV highlights (exhibitions, education, workshops, publications).
6. Footer line with name + year.

### 2. Artist CV PDF (A4)
Tight CV layout, designed to print cleanly: name, contact, practice statement, then exhibitions / projects / education / residencies / awards / grants / workshops / talks / publications / collections in lists.

### 3. Project PDF (A3, per project)
1. Cover: year, artist name, project title, subtitle, summary, featured image.
2. Project statement, cultural background, artist statement (each its own section if present).
3. Project images (process / documentation).
4. Each artwork in the project, one per page, with caption kept with the image.

---

## Page break rules

The goal is that **artworks never split awkwardly across pages**.

We handle this through:
- `@page` margins set explicitly (22–20 mm for A3, 20–22 mm for A4 CV).
- Each artwork in the PDF is `page-break-before: always` and `page-break-inside: avoid`. The artwork image is constrained to `max-height: 200 mm` inside the page so the caption always fits.
- CV sections and project sections use `page-break-inside: avoid` on each list item so a single role is never cut in half.
- The portfolio cover forces `page-break-after: always`.

If you see a stray split (e.g. a tall thin painting whose caption is pushed onto the next page), the fix is almost always to adjust `max-height` on the relevant image rule in the corresponding PDF template's `<style>` block.

---

## Fonts

The PDFs use Google Fonts loaded over HTTPS at render time:
- **Cormorant Garamond** — display (serif, editorial).
- **Inter** — body and meta information.

This matches the website exactly. The WeasyPrint render in CI fetches them. If you're rendering offline on an air-gapped machine, download both families as local font files and `@font-face` them in the template styles — but the default setup is what we recommend.

---

## Manual PDF generation (local)

```bash
# With the virtualenv active, from repository root:
cd src && python pdf_generator.py
```

If `weasyprint` is installed and its system dependencies (Pango/Cairo) are present, you get real PDFs. Otherwise the script writes the same content as `.html` alongside the expected `.pdf` so you can open/print-to-PDF manually via Chrome for a quick preview.

---

## Making small layout tweaks

All three PDF templates live in `templates/` and are **self-contained HTML with inline CSS**. Edit them just like a web page.

- Want a different cover? Change the `.cover` block in `pdf_portfolio.html`.
- Want more/fewer artworks in the portfolio? Change `artworks[:12]` in `pdf_generator.py`.
- Want to switch Portfolio or Project PDFs to A4? Change the `@page size` at the top of the template's `<style>`.
- Want to add a gallery to the CV PDF? Copy one of the `cv-block` patterns from `pdf_portfolio.html` into `pdf_cv.html`.

Save your edits → run `cd src && python build.py` → check the new PDFs in `public/pdfs/`.

---

## Image sizing for good-quality prints

The PDFs reuse the same image files as the website. For crisp A3 prints:
- Longest edge ≥ **2400 px** is ideal.
- JPEG at quality 85–90 is fine; avoid PNG for paintings (it's unnecessarily large).
- Anything above 300 dpi in "effective resolution" on the printed page is indistinguishable to the eye — the layout constraints (max image height) are usually the binding factor, not the source file.

If you're delivering the PDF to a gallery or press and you know it will be printed, export your master files at 300 dpi effective size for the target print dimensions and swap them in the CMS / images folder; the build picks them up automatically.

---

## Color management / grayscale

The website and PDF templates are **full color** by design. Should you need a "print-friendlier" grayscale variant later:
- Duplicate the templates with a `-bw` suffix, add `filter: grayscale(1)` on `body img`, and add a second PDF-generation call in `pdf_generator.py`.

---

## Verifying page breaks before sending to a gallery / printer

1. Build → open the PDF in your OS PDF viewer.
2. Scroll through slowly and check:
   - Does every artwork fit on the page you expected it to?
   - Are any captions orphaned (image at end of a page, caption at the top of the next)?
   - Are the very last lines of the CV or project statement visible?
3. Zoom to "Actual Size" and visually verify the print margins.

All layout changes should be tested locally before pushing — GitHub Actions will rebuild PDFs automatically, but you want to make sure the page breaks are correct first.

---

## Automatically keeping PDFs in sync

Because PDFs are generated inside the same build step as the HTML website, the following is already guaranteed:
- If the artist edits an artwork title in the CMS, both the website **and** every PDF (portfolio + relevant project PDF) update on the next build.
- If the artist updates their biography, the portfolio PDF cover and CV PDF both update automatically.
- Adding a new project automatically produces a new `project-<slug>.pdf` and adds it to the downloads footer if configured.

No manual PDF uploads. Ever.
