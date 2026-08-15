# Deployment Guide — GitHub Pages + Actions

Everything you need to publish updates automatically. This project is designed for GitHub Pages only.

---

## Enable GitHub Pages

1. Push the repository to GitHub.
2. On the repo page → **Settings → Pages**.
3. Under **Build and deployment**, set the **Source** dropdown to **GitHub Actions** (not a branch).
4. You don't need to choose a branch — the workflow in `.github/workflows/deploy.yml` produces the artifact itself.

That's it for enabling deployment.

---

## What the deploy pipeline does (in order)

Every push to `main`, or manual run via the Actions tab:

1. **Checkout** code
2. Install **Python 3.12**
3. Install **WeasyPrint system deps** (Pango, Cairo, GDK-Pixbuf)
4. `pip install -r requirements.txt`
5. **Validate content** via `src/validate.py`
   - Checks required fields on every artwork/project/exhibition
   - Verifies referenced images actually exist in the repo
   - Verifies project → artwork slug references are valid
   - Verifies CV selected_projects slugs resolve
   - **Fails the build** if any of the above are broken — the site never deploys half-broken content.
6. **Build site** via `src/build.py` → `public/` with:
   - All HTML routes (home, work, artwork pages, projects, about, exhibitions, CV, contact)
   - `sitemap.xml` + `robots.txt`
   - Copied static assets and images
   - CMS admin folder
7. **Generate PDFs** (inside build step) → `public/pdfs/`:
   - Full portfolio PDF (A3)
   - CV PDF (A4)
   - One PDF per published project (A3)
8. **Upload Pages artifact → deploy** via the official GitHub Pages actions.

The build takes about 2–3 minutes on GitHub free runners.

---

## First deployment checklist

Before you trigger the first build, make sure:

- [ ] Repository exists on GitHub, `main` branch has all your files.
- [ ] `public/` is gitignored (it is, by default). You don't commit the build output.
- [ ] `images/artworks/` has the files referenced by every published artwork. (Validation catches missing ones!)
- [ ] `content/settings/site.json` → update `base_url` to your canonical Pages URL once known (e.g. `https://yourname.github.io/abdullahi-ndagii`, no trailing slash) — this fixes OpenGraph previews and the sitemap.

---

## Manual deploy from a clean local checkout

If you ever want to test the full pipeline on your own machine before pushing:

```bash
git clone https://github.com/YOURNAME/abdullahi-ndagii
cd abdullahi-ndagii
python -m venv .venv && source .venv/bin/activate     # Linux/macOS
# or: .venv\Scripts\Activate.ps1                      # PowerShell
pip install -r requirements.txt

# Verify content validity
cd src && python validate.py && cd ..

# Produce public/ output
cd src && python build.py && cd ..

# Preview locally
python -m http.server --directory public 8080
```

If the local build fails, the GitHub build will fail too — fix the errors first.

---

## Custom domain (optional)

Using `abdullahi-ndagi-adamu.com` or similar?

1. Buy the domain from your registrar of choice (Namecheap, Porkbun, etc.).
2. GitHub repo → **Settings → Pages → Custom domain** — enter the domain name (e.g. `www.abdullahi-ndagi-adamu.com`).
3. At your registrar, configure DNS:

   | Type | Host | Value |
   |------|------|-------|
   | A    | `@`  | `185.199.108.153` |
   | A    | `@`  | `185.199.109.153` |
   | A    | `@`  | `185.199.110.153` |
   | A    | `@`  | `185.199.111.153` |
   | CNAME| `www`| `yourname.github.io.` |

   (Alternative: a single `CNAME` on the apex if your registrar supports `CNAME` flattening.)

4. Tick **Enforce HTTPS** after the certificate provisions (usually within a few minutes).
5. Update `content/settings/site.json` → `base_url` to the new canonical URL, and commit.

---

## Cancelling / re-running a build

Repo → **Actions** → click the latest workflow run → **Cancel workflow** or **Re-run all jobs**.

---

## Build failure triage

Failures almost always have helpful messages in the *Validate content* step. The format is always:

```
artwork[umbra]: missing required field 'year'     ← fix this artwork in CMS
project[what-we-carry]: references unknown artwork 'missing-slug'
```

Open the CMS → navigate to the file mentioned → fix the field → Publish again.

If a build fails **before** the deploy step, the previous deployment keeps running — visitors never see a broken site.

---

## Cache refresh / why isn't my change live yet?

GitHub Pages aggressively caches content. After a successful deploy:

1. Wait 1–2 minutes.
2. Hard-refresh in browser: Ctrl-F5 (Win/Linux), Cmd-Shift-R (Mac).
3. Check the GitHub Pages deployment log under Actions — it reports "Pages deployment successful" when the CDN nodes have it.

---

## Rollback to an older version

Every push to `main` produces a new deploy, and older deploys are kept for a while. To roll back:

1. Repo → **Actions** → find the green deploy you want → **Re-run all jobs** (re-deploys that exact build).
2. Or just `git revert` the commit that introduced the issue and push; a fresh build is produced.

---

## Exceeding the free tier limits?

GitHub Pages limits (as of 2025):
- Soft bandwidth cap: ~100 GB / month (should be fine for an artist portfolio).
- Actions minutes: ~2000 min / month on public repos (free tier). This build uses about 3 min per run → ~600 builds/month.

If you ever need more, Cloudflare Pages mirrors this workflow easily (just build the same `public/` folder) — but GitHub free tier is the starting recommendation.
