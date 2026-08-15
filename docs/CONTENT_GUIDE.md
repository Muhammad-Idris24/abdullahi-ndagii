# Content Guide — for the artist

*You don't need to know how to code. You can manage everything in your portfolio from a browser.*

---

## First-time quick start

1. Go to your portfolio website and add `/admin/` to the end of the address bar (e.g. `https://yourname.github.io/abdullahi-ndagii/admin/`).
2. Log in with your GitHub account when asked.
3. You're in! On the left you'll see:
   - **Site Settings** — title, navigation, downloads in the footer
   - **Artist Profile** — your bio, statement, contact details, portrait, socials
   - **Artworks** — every individual painting
   - **Projects / Series** — bodies of work like *Witness Series*, *What We Carry*
   - **Exhibitions** — shows and anthologies
   - **CV Data** — education, workshops, publications…

---

## Adding a new artwork

1. From the CMS menu, click **Artworks → New Artwork**.
2. Fill the fields:

   | Field          | What it means                                                                 |
   |----------------|-------------------------------------------------------------------------------|
   | **Slug**       | Short URL-friendly name. Use lowercase and hyphens, e.g. `timeless` or `hands-of-creation`. *Once published, don't change this or external links will break.* |
   | **Title**      | The name of the piece — exactly as you want it written.                      |
   | **Year**       | Year you finished it, e.g. `2025`.                                            |
   | **Medium**     | Materials, e.g. *Acrylic and Spray Paint on Canvas*.                         |
   | **Dimensions** | Inches usually, e.g. `24 x 36 inches`.                                        |
   | **Series**     | If this work belongs to a larger series, write it here e.g. `Witness Series`. |
   | **Artwork Image** | Upload the highest-quality file you have (JPEG or WebP, at least 2000px on the long side). |
   | **Description**| A short text the viewer reads under the image. Write what feels right — your words, your voice. |
   | **Artist Note**| Optional — a personal note, memory, or commentary on the work.               |
   | **Featured**   | Tick if you want this piece to appear on the homepage "Selected Works".      |
   | **Order**      | Smaller numbers appear first. `1` comes before `2`.                           |
   | **Published**   | Untick if you want to save it without it appearing on the live website.      |
   | **Tags**       | Optional keywords for your own sorting later.                                |

3. Click **Save** at the top, then **Publish**.

> After publishing, GitHub will rebuild your website automatically (about 2 minutes). Refresh the live site to see the changes.

---

## Editing an artwork

1. **Artworks → click the piece → edit fields → Save / Publish.**

The old version stays live until you click Publish.

---

## Unpublishing / deleting

- To hide temporarily: open the work, untick **Published**, then Save/Publish. The work stays in the CMS but disappears from the website.
- To delete: open the work, click the **⋮ menu → Delete Entry.** Confirm. You can always restore a previous version through GitHub if you need to later.

---

## Adding a project / body of work

1. **Projects → New Project.**
2. Fields you'll usually fill:
   - **Title** — e.g. `What We Carry`.
   - **Year / Range** — `2024 — Present` or just `2025`.
   - **Summary** — one or two short sentences for project cards and lists.
   - **Project Statement**, **Cultural Background**, **Artist Statement** — long-form writing. Write freely; the project page gives each its own section with a side table of contents.
   - **Included Artworks** — type the *slug* of each work in the order you want them to appear, e.g. `umbra`, `timeless`, `hands-of-creation`. (The slug is the first field of each Artwork entry.)
   - **Featured / Cover Image** — a hero image that represents the project on its cover.
   - **Order** — `1` for your most prominent project.
3. Publish.

---

## Changing your bio or statement

1. **Artist Profile → Artist Profile** (it's a single entry, click it).
2. Edit Biography, Artist Statement, Portrait, Contact, Social Links directly.
3. Publish. The About page and homepage update automatically.

---

## Adding an exhibition

1. **Exhibitions → New Exhibition.**
2. Title, Year, City, Country, and Role (Participating Artist / Selected Artist…) are the minimum you need to show a line on the Exhibitions page and CV.
3. Publish.

---

## Updating your CV (education, workshops, awards, etc.)

1. **CV Data → Curriculum Vitae** (a single entry).
2. Each section — Education, Residencies, Awards, Grants, Workshops, Talks, Publications, Collections — is a list you can add rows to.
3. Save/Publish. Changes appear on `/cv.html` and in the CV PDF and Portfolio PDF on the next build.

---

## Changing navigation or footer downloads

1. **Site Settings → Site / Navigation.**
2. Edit the list of nav items or footer download items.
3. Publish.

*If you add a brand-new page that doesn't exist yet, ask your developer friend — the CMS edits content, not routes.*

---

## What happens when I click "Publish"?

Decap CMS saves your changes into your GitHub repository as commits on the `main` branch. That triggers a GitHub Actions build:

```
Content updated in CMS
      ↓
GitHub commit created
      ↓
GitHub Actions runs validation (checks required fields)
      ↓
Website regenerated into static HTML
      ↓
PDFs regenerated (Portfolio, CV, per-project)
      ↓
Everything deployed to GitHub Pages
```

You'll see the update on the live site within ~2 minutes, most of which is GitHub Pages caching.

---

## Image tips — do's and don'ts

Do:
- Save JPEGs at quality 85-90.
- Keep original proportions; do not crop the painting itself.
- Keep the canvas edge visible in the photograph if the edge is part of the work.
- Use descriptive filenames: `genesis-in-chaos.jpg`, not `IMG_0247_final_final.jpg`.

Don't:
- Upload phone screenshots; share proper camera scans/photos.
- Apply text, watermarks, or decorative frames to the artwork image itself — the website adds caption text.
- Upload 20 MB raw files. Resize to 2400 px on the long side first (that's already very high quality).

---

## I want to make edits without using the website CMS

If you prefer to work on your own computer, any text editor will do. The files you want are under the `content/` folder in the repository:

```
content/artist/profile.json          — Bio + contact
content/artworks/<slug>.json         — One per artwork
content/projects/<slug>.json         — One per project
content/exhibitions/<slug>.json      — One per exhibition
content/cv/cv.json                   — CV data
content/settings/site.json           — Navigation / site title
```

And images go in:
```
images/artist/abdullahi-portrait.jpeg
images/artworks/<slug>.jpeg
images/projects/<slug>-<number>.jpeg
```

After making changes, commit them and push to GitHub. GitHub Actions will rebuild everything for you.

---

## Something looks wrong?

- If the page *doesn't change* after you publish: wait two minutes, then do a hard refresh (Ctrl+F5 on Windows, Cmd+Shift+R on Mac).
- If the build shows a red X in GitHub Actions: open the failing run — the validator tells you *exactly* which field is missing in which file (e.g. "artwork[umbra]: missing required field 'year'"). You can fix it in the CMS and publish again.
- If a PDF looks wrong (wrong page break, etc.): contact the developer — the templates can be tweaked, we just need to see which piece is causing it.
