# CMS Setup — Decap CMS + GitHub OAuth + Cloudflare Worker

A one-time setup so the artist can log in at `/admin/` and publish content without code.

---

## How it works (in plain terms)

- The CMS (Decap CMS) is a single HTML page that loads in the browser.
- To save edits, it needs to write to your GitHub repository.
- GitHub allows this via OAuth, but OAuth *can't* be done purely in the browser for security reasons.
- So we put a tiny free "messenger" in the middle — a Cloudflare Worker. It forwards OAuth tokens and nothing else. It costs $0 for this use case and has no moving parts once deployed.

---

## Step 1 — Create a GitHub OAuth application

You do this once in your GitHub account settings.

1. GitHub → click your avatar → **Settings** → (scroll the sidebar) **Developer settings** → **OAuth Apps** → **New OAuth App**.
2. Fill in:

   | Field                        | Value                                                                 |
   |------------------------------|-----------------------------------------------------------------------|
   | Application name             | *Abdullahi Ndagi Adamu Portfolio CMS* (or whatever you remember)     |
   | Homepage URL                 | Your live site URL, e.g. `https://yourname.github.io/abdullahi-ndagii`  |
   | Application description      | *(Optional)* CMS login for the artist portfolio.                     |
   | Authorization callback URL   | **You'll fill this in after Step 2**. For now, put a placeholder such as `http://localhost` — we come back here. |

3. Click **Register application**.

4. On the next screen you'll see:
   - **Client ID** — copy this somewhere safe (we call it `GH_CLIENT_ID`).
   - Click **Generate a new client secret** → copy that too (this is `GH_CLIENT_SECRET` — **never share or paste it publicly**).

Leave this tab open.

---

## Step 2 — Deploy the Cloudflare Worker OAuth gateway

We use an existing, well-audited open-source gateway for Netlify/Decap CMS called `GitHub-OAuth-Gateway-Cloudflare-Worker`.

### 2a. Create a Cloudflare account (free tier is enough)
1. Go to https://dash.cloudflare.com/sign-up and create an account. You don't need to add a domain; a free Workers subdomain works fine.

### 2b. Install Wrangler (Cloudflare's CLI)
On your local machine:
```bash
# Requires Node 18+
npm install -g wrangler
wrangler login
```

### 2c. Create the Worker
```bash
git clone https://github.com/roberttod/GitHub-OAuth-Gateway-Cloudflare-Worker oauth-worker
cd oauth-worker
```

Copy `wrangler.toml.example` to `wrangler.toml` and change `name = "oauth-gateway"` (or a name you'll remember).

### 2d. Add secrets to the Worker
```bash
wrangler secret put GH_CLIENT_ID
# paste the Client ID from GitHub

wrangler secret put GH_CLIENT_SECRET
# paste the Client Secret from GitHub

wrangler secret put ALLOWED_DOMAINS
# paste: yourname.github.io,localhost
# (comma separated, NO spaces between items)
```

### 2e. Publish the Worker
```bash
wrangler deploy
```
When it finishes, it prints a URL like:
```
https://oauth-gateway.YOURCLOUDFLAREUSERNAME.workers.dev
```
Copy this — we call it the **`base_url`** below.

### 2f. Return to the GitHub OAuth App and finish
Open the OAuth app page from Step 1, click **Edit**, and set:

**Authorization callback URL** → `https://oauth-gateway.YOURCLOUDFLAREUSERNAME.workers.dev/callback`

*(The `/callback` at the end is required!)*

Click **Update application**.

---

## Step 3 — Tell the CMS about your repo and worker

Open `admin/config.yml` in your repo and update the `backend` section:

```yaml
backend:
  name: github
  repo: YOUR_GITHUB_USERNAME/abdullahi-ndagii   # e.g. abdullahi65/abdullahi-ndagii
  branch: main
  base_url: "https://oauth-gateway.YOURCLOUDFLAREUSERNAME.workers.dev"   # ← your worker
  auth_endpoint: "auth"
  cms_label_prefix: "cms:"
```

Also update `media_folder` and `public_folder` if you're using a different upload directory (the default `images/uploads` works).

Commit and push the change.

---

## Step 4 — Test the CMS login

1. After the next build finishes, visit:
   `https://yourname.github.io/abdullahi-ndagii/admin/`
2. You should see a **Login with GitHub** button.
3. Click it → you'll be redirected to GitHub → Authorize → you land back in the CMS.
4. Open any collection, make a trivial edit (e.g. add a missing tag), and click Publish.
5. On GitHub, check the repo commits — you should see a new commit prefixed `cms:`.

If it works, the CMS is live.

---

## Step 5 — Local CMS testing (optional, for devs)

If you want to test the CMS locally without deploying the worker every time:

Terminal 1 — serve the built site:
```bash
cd public && python -m http.server 8081
```

Terminal 2 — run the Decap CMS local proxy:
```bash
npx decap-server
```

Open http://localhost:8081/admin/ — it bypasses OAuth entirely.

`admin/config.yml` already has `local_backend: true`.

---

## Adding additional CMS editors

1. Give them **write access** to the GitHub repository.
2. They use the same `/admin/` URL and log in with *their own* GitHub account. The Cloudflare Worker does not need any changes.

---

## Rotating secrets

If a secret leaks:

1. GitHub OAuth app → **Regenerate client secret**.
2. Update the Cloudflare Worker secret:
   ```bash
   wrangler secret put GH_CLIENT_SECRET
   ```

---

## Troubleshooting

| Symptom | Likely fix |
|---------|------------|
| CMS shows "Unable to authorize" / 404 | Double-check `base_url` in config.yml ends with **no trailing slash**, and GitHub callback URL ends with `/callback`. |
| CMS shows a plain "Log in with GitHub" but nothing happens | Check browser console for errors; this is almost always a missing `repo` in `backend:`, or repo name has a typo. |
| CMS says "No backend found" | Decap CMS couldn't load `config.yml`. Make sure `public/admin/config.yml` exists and YAML is valid. |
| Save fails silently with 409 | The CMS backend config is right, but the GitHub token lacks repo scope. De-authorize the OAuth app in GitHub → revoke → re-login. |
