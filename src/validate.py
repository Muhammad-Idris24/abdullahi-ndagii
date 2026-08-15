"""Content validation for the artist portfolio.

Validates:
- Required fields are present on every record.
- Referenced images exist on disk.
- Internal references (artwork slugs, project slugs) are resolvable.
- No duplicate slugs within a collection.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from utils import CONTENT_DIR, IMAGES_DIR, load_all_json, load_json, ROOT


ARTWORK_REQUIRED = [
    "slug",
    "title",
    "year",
    "medium",
    "dimensions",
    "image",
    "published",
]

PROJECT_REQUIRED = [
    "slug",
    "title",
    "year",
    "summary",
    "artworks",
    "published",
]

EXHIBITION_REQUIRED = [
    "slug",
    "title",
    "year",
    "city",
    "country",
    "role",
    "published",
]

ARTIST_REQUIRED = [
    "full_name",
    "professional_title",
    "biography",
    "artist_statement",
    "contact",
]


def _check_required(record: dict[str, Any], required: list[str], source: str) -> list[str]:
    errors = []
    for field in required:
        if field not in record or record[field] in (None, "", []):
            if field in ("artist_note", "project", "series"):
                continue
            errors.append(f"{source}: missing or empty required field '{field}'")
    return errors


def _image_exists(rel_path: str) -> bool:
    if not rel_path:
        return True
    candidate = ROOT / rel_path
    return candidate.exists() and candidate.is_file()


def validate_artworks() -> list[str]:
    errors: list[str] = []
    artworks = load_all_json(CONTENT_DIR / "artworks")
    seen_slugs: set[str] = set()
    for art in artworks:
        source = f"artwork[{art.get('slug', '?')}]"
        errors.extend(_check_required(art, ARTWORK_REQUIRED, source))

        slug = art.get("slug", "")
        if slug in seen_slugs:
            errors.append(f"{source}: duplicate slug '{slug}'")
        seen_slugs.add(slug)

        for field in ("image", "thumbnail", "portrait"):
            path = art.get(field)
            if path and not _image_exists(path):
                errors.append(f"{source}: {field} image not found: {path}")
    return errors


def validate_projects(artwork_slugs: set[str]) -> list[str]:
    errors: list[str] = []
    projects = load_all_json(CONTENT_DIR / "projects")
    seen_slugs: set[str] = set()
    for proj in projects:
        source = f"project[{proj.get('slug', '?')}]"
        errors.extend(_check_required(proj, PROJECT_REQUIRED, source))

        slug = proj.get("slug", "")
        if slug in seen_slugs:
            errors.append(f"{source}: duplicate slug '{slug}'")
        seen_slugs.add(slug)

        for art_slug in proj.get("artworks", []) or []:
            if art_slug not in artwork_slugs:
                errors.append(f"{source}: references unknown artwork '{art_slug}'")

        for field in ("featured_image",):
            path = proj.get(field)
            if path and not _image_exists(path):
                errors.append(f"{source}: {field} image not found: {path}")

        for img in proj.get("project_images", []) or []:
            path = img.get("src") if isinstance(img, dict) else img
            if path and not _image_exists(path):
                errors.append(f"{source}: project image not found: {path}")
    return errors


def validate_exhibitions() -> list[str]:
    errors: list[str] = []
    exhibitions = load_all_json(CONTENT_DIR / "exhibitions")
    seen_slugs: set[str] = set()
    for exh in exhibitions:
        source = f"exhibition[{exh.get('slug', '?')}]"
        errors.extend(_check_required(exh, EXHIBITION_REQUIRED, source))
        slug = exh.get("slug", "")
        if slug in seen_slugs:
            errors.append(f"{source}: duplicate slug '{slug}'")
        seen_slugs.add(slug)
    return errors


def validate_artist() -> list[str]:
    errors: list[str] = []
    profile_path = CONTENT_DIR / "artist" / "profile.json"
    if not profile_path.exists():
        return ["artist/profile.json: file missing"]
    profile = load_json(profile_path)
    errors.extend(_check_required(profile, ARTIST_REQUIRED, "artist.profile"))

    portrait = profile.get("portrait")
    if portrait and not _image_exists(portrait):
        errors.append(f"artist.profile: portrait image not found: {portrait}")

    contact = profile.get("contact") or {}
    if not contact.get("email") and not contact.get("phone"):
        errors.append("artist.profile: at least one contact (email/phone) required")
    return errors


def validate_cv(project_slugs: set[str]) -> list[str]:
    errors: list[str] = []
    cv_path = CONTENT_DIR / "cv" / "cv.json"
    if not cv_path.exists():
        return ["cv/cv.json: file missing"]
    cv = load_json(cv_path)
    for field in ("education", "workshops", "residencies", "awards", "grants", "talks", "publications", "collections"):
        if not isinstance(cv.get(field, []), list):
            errors.append(f"cv: {field} must be a list")
    for slug in cv.get("selected_projects", []) or []:
        if slug not in project_slugs:
            errors.append(f"cv: selected_projects references unknown project '{slug}'")
    return errors


def validate_all() -> list[str]:
    errors: list[str] = []
    errors.extend(validate_artist())
    errors.extend(validate_artworks())

    artwork_slugs = {a["slug"] for a in load_all_json(CONTENT_DIR / "artworks") if "slug" in a}
    errors.extend(validate_projects(artwork_slugs))

    project_slugs = {p["slug"] for p in load_all_json(CONTENT_DIR / "projects") if "slug" in p}
    errors.extend(validate_exhibitions())
    errors.extend(validate_cv(project_slugs))
    return errors


def main() -> int:
    print("Validating content…")
    errors = validate_all()
    if errors:
        print(f"\nFound {len(errors)} content issue(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("Content is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
