"""Main build script for the Abdullahi Ndagi Adamu artist portfolio.

Pipeline:
1. Validate content (fail on errors).
2. Ensure clean public/ output folder.
3. Copy static assets (css, js, icons, images, admin CMS, favicon).
4. Load content files (artist, artworks, projects, exhibitions, cv, settings).
5. Render every page using Jinja2 templates.
6. Generate sitemap.xml and robots.txt.
7. Generate PDFs (portfolio, cv, each project).

Output directory: public/
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from utils import (
    CONTENT_DIR,
    PUBLIC_DIR,
    ROOT,
    TEMPLATES_DIR,
    copy_static_assets,
    ensure_public_dir,
    load_all_json,
    load_json,
    write_text,
)

from validate import validate_all


# ---------- Jinja environment ----------

def jinja_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader([str(TEMPLATES_DIR), str(ROOT)]),
        autoescape=select_autoescape(enabled_extensions=("html", "xml")),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["nl2br"] = _nl2br
    env.filters["date_display"] = _date_display
    return env


def _nl2br(value: str) -> str:
    import markupsafe
    if not value:
        return ""
    escaped = markupsafe.escape(value)
    return markupsafe.Markup("<br>\n").join(escaped.splitlines())


def _date_display(value: str) -> str:
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%B %Y")
    except ValueError:
        return value


# ---------- Content loading ----------

def load_site_context() -> dict[str, Any]:
    site = load_json(CONTENT_DIR / "settings" / "site.json")
    artist = load_json(CONTENT_DIR / "artist" / "profile.json")

    artworks_all = load_all_json(CONTENT_DIR / "artworks")
    artworks = sorted(
        [a for a in artworks_all if a.get("published", True)],
        key=lambda a: (a.get("order", 999), a.get("year", 0)),
        reverse=False,
    )
    featured_artworks = [a for a in artworks if a.get("featured", False)]

    projects_all = load_all_json(CONTENT_DIR / "projects")
    projects = sorted(
        [p for p in projects_all if p.get("published", True)],
        key=lambda p: (p.get("order", 999),),
    )

    exhibitions = sorted(
        load_all_json(CONTENT_DIR / "exhibitions"),
        key=lambda e: (e.get("order", 999), -int(e.get("year", 0))),
    )

    cv = load_json(CONTENT_DIR / "cv" / "cv.json")

    artwork_by_slug = {a["slug"]: a for a in artworks}
    project_by_slug = {p["slug"]: p for p in projects}

    for proj in projects:
        proj["artworks_objects"] = [
            artwork_by_slug[s] for s in proj.get("artworks", []) if s in artwork_by_slug
        ]

    for art in artworks:
        project_slug = art.get("project") or art.get("series_project")
        if project_slug and project_slug in project_by_slug:
            art["project_object"] = project_by_slug[project_slug]

    return {
        "site": site,
        "artist": artist,
        "artworks": artworks,
        "featured_artworks": featured_artworks,
        "projects": projects,
        "exhibitions": exhibitions,
        "cv": cv,
        "artwork_by_slug": artwork_by_slug,
        "project_by_slug": project_by_slug,
        "current_year": datetime.now(tz=UTC).year,
        "build_time": datetime.now(tz=UTC).isoformat(),
    }


# ---------- Rendering ----------

def render_page(env: Environment, template_name: str, filename: str, page_ctx: dict[str, Any]) -> None:
    template = env.get_template(template_name)
    html = template.render(**page_ctx)
    write_text(PUBLIC_DIR / filename, html)


def render_all_pages(ctx: dict[str, Any]) -> None:
    env = jinja_env()
    common = {
        "site": ctx["site"],
        "artist": ctx["artist"],
        "current_year": ctx["current_year"],
        "cv": ctx["cv"],
        "exhibitions": ctx["exhibitions"],
        "projects": ctx["projects"],
        "artworks": ctx["artworks"],
        "project_by_slug": ctx["project_by_slug"],
        "artwork_by_slug": ctx["artwork_by_slug"],
    }

    def _page(name: str, title: str, description: str, path: str, **extra: Any) -> dict[str, Any]:
        page_ctx = {
            **common,
            "page_title": title,
            "page_description": description,
            "page_path": path,
            "active": path.replace(".html", "") if path.endswith(".html") else path,
        }
        page_ctx.update(extra)
        return page_ctx

    # Home
    hero = ctx["featured_artworks"][0] if ctx["featured_artworks"] else (ctx["artworks"][0] if ctx["artworks"] else None)
    featured_project = next((p for p in ctx["projects"] if p["slug"] == "what-we-carry"), ctx["projects"][0] if ctx["projects"] else None)
    render_page(env, "index.html", "index.html", _page(
        "home",
        f"{ctx['artist']['full_name']} — {ctx['artist']['professional_title']}",
        ctx["site"]["site_description"],
        "index.html",
        hero_artwork=hero,
        selected_works=ctx["featured_artworks"][:6] or ctx["artworks"][:6],
        featured_project=featured_project,
        selected_exhibitions=ctx["exhibitions"][:3],
    ))

    # Work index
    render_page(env, "work.html", "work.html", _page(
        "work",
        "Work — " + ctx["artist"]["full_name"],
        f"Selected paintings and mixed-media works by {ctx['artist']['full_name']}.",
        "work.html",
        artworks=ctx["artworks"],
        projects=ctx["projects"],
    ))

    # Individual artwork pages
    for i, art in enumerate(ctx["artworks"]):
        slug = art["slug"]
        prev_art = ctx["artworks"][i - 1] if i > 0 else ctx["artworks"][-1]
        next_art = ctx["artworks"][i + 1] if i + 1 < len(ctx["artworks"]) else ctx["artworks"][0]
        related = [a for a in ctx["artworks"] if a["slug"] != slug and a.get("series") == art.get("series")][:3]
        render_page(env, "artwork.html", f"work/{slug}.html", _page(
            f"work/{slug}",
            f"{art['title']} — {ctx['artist']['full_name']}",
            art.get("description") or f"{art['title']}, {art.get('year', '')} — {ctx['artist']['full_name']}",
            f"work/{slug}.html",
            artwork=art,
            prev_artwork=prev_art,
            next_artwork=next_art,
            related_works=related,
        ))

    # Projects index
    render_page(env, "projects.html", "projects.html", _page(
        "projects",
        "Projects — " + ctx["artist"]["full_name"],
        f"Bodies of work and long-form projects by {ctx['artist']['full_name']}.",
        "projects.html",
        projects=ctx["projects"],
    ))

    # Individual project pages
    for proj in ctx["projects"]:
        slug = proj["slug"]
        render_page(env, "project.html", f"projects/{slug}.html", _page(
            f"projects/{slug}",
            f"{proj['title']} — {ctx['artist']['full_name']}",
            proj.get("summary") or f"{proj['title']}, a project by {ctx['artist']['full_name']}",
            f"projects/{slug}.html",
            project=proj,
        ))

    # About
    render_page(env, "about.html", "about.html", _page(
        "about",
        "About — " + ctx["artist"]["full_name"],
        f"Biography and artist statement of {ctx['artist']['full_name']}.",
        "about.html",
    ))

    # Exhibitions
    render_page(env, "exhibitions.html", "exhibitions.html", _page(
        "exhibitions",
        "Exhibitions — " + ctx["artist"]["full_name"],
        f"Selected exhibitions, anthologies, and public presentations by {ctx['artist']['full_name']}.",
        "exhibitions.html",
    ))

    # CV
    render_page(env, "cv.html", "cv.html", _page(
        "cv",
        "CV — " + ctx["artist"]["full_name"],
        f"Education, workshops, publications, and CV for {ctx['artist']['full_name']}.",
        "cv.html",
    ))

    # Contact
    render_page(env, "contact.html", "contact.html", _page(
        "contact",
        "Contact — " + ctx["artist"]["full_name"],
        f"Contact {ctx['artist']['full_name']} for commissions, exhibitions, and press enquiries.",
        "contact.html",
    ))

    print("  [OK] All HTML pages rendered.")


def generate_sitemap_and_robots(ctx: dict[str, Any]) -> None:
    base_url = (ctx["site"].get("base_url") or "").rstrip("/")
    pages = [
        "index.html",
        "work.html",
        "projects.html",
        "about.html",
        "exhibitions.html",
        "cv.html",
        "contact.html",
    ]
    pages += [f"work/{a['slug']}.html" for a in ctx["artworks"]]
    pages += [f"projects/{p['slug']}.html" for p in ctx["projects"]]

    base_for_print = base_url or "https://example.com"
    entries = [f"  <url><loc>{base_for_print}/{p}</loc></url>" for p in pages]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(entries) + "\n</urlset>\n"
    write_text(PUBLIC_DIR / "sitemap.xml", sitemap)

    robots = f"User-agent: *\nAllow: /\n\nSitemap: {base_for_print}/sitemap.xml\n"
    write_text(PUBLIC_DIR / "robots.txt", robots)
    print("  [OK] sitemap.xml + robots.txt generated.")


# ---------- Main ----------

def main() -> int:
    print(f"Abdullahi Ndagi Adamu — Portfolio Build\nBuild timestamp: {datetime.now(tz=UTC).isoformat()}")
    print("-" * 60)

    errors = validate_all()
    if errors:
        print(f"\nBUILD FAILED: {len(errors)} content validation error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("  [OK] Content validation passed.")

    ensure_public_dir()
    copy_static_assets()
    print("  [OK] Static assets copied to public/.")

    ctx = load_site_context()
    render_all_pages(ctx)
    generate_sitemap_and_robots(ctx)

    # Import and run PDF generator
    try:
        import pdf_generator
        pdf_generator.generate_all()
    except Exception as pdf_err:
        print(f"  [WARN] PDF generation skipped: {pdf_err}")

    print("-" * 60)
    print(f"Build complete. Output: {PUBLIC_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
