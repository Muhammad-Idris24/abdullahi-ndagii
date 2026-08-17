"""Shared utilities for the Abdullahi Ndagi Adamu portfolio build system."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

CONTENT_DIR = ROOT / "content"
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"
IMAGES_DIR = ROOT / "images"
PUBLIC_DIR = ROOT / "public"
ADMIN_DIR = ROOT / "admin"


def slugify(value: str) -> str:
    """Convert a string to a URL-safe slug."""
    value = value.strip().lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_-]+", "-", value)
    return value.strip("-")


def load_json(path: Path) -> dict[str, Any]:
    """Load and parse a JSON file, with clear error on failure."""
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc


def load_all_json(directory: Path) -> list[dict[str, Any]]:
    """Load every JSON file in a directory into a list."""
    if not directory.exists():
        return []
    items = []
    for path in sorted(directory.glob("*.json")):
        items.append(load_json(path))
    return items


def ensure_public_dir() -> None:
    """Ensure the public output directory exists and is clean of stale generated pages."""
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    for suffix in ("*.html", "*.xml", "*.txt"):
        for path in PUBLIC_DIR.glob(suffix):
            path.unlink()
    for generated_dir in (PUBLIC_DIR / "work", PUBLIC_DIR / "projects", PUBLIC_DIR / "pdfs"):
        if generated_dir.exists():
            shutil.rmtree(generated_dir)


def copy_static_assets() -> None:
    """Copy static directories into the public output folder."""
    for src, name in (
        (STATIC_DIR, "static"),
        (IMAGES_DIR, "images"),
        (ADMIN_DIR, "admin"),
    ):
        dst = PUBLIC_DIR / name
        if dst.exists():
            shutil.rmtree(dst)
        if src.exists():
            shutil.copytree(src, dst)

    favicon = ROOT / "favicon.ico"
    if favicon.exists():
        shutil.copy(favicon, PUBLIC_DIR / "favicon.ico")


def ensure_pdfs_dir() -> Path:
    pdfs = PUBLIC_DIR / "pdfs"
    pdfs.mkdir(parents=True, exist_ok=True)
    # Remove obsolete HTML fallbacks from earlier builds so downloads always
    # correspond to the PDF links published by the site.
    for stale_html in pdfs.glob("*.html"):
        stale_html.unlink()
    return pdfs


def write_text(path: Path, content: str) -> None:
    """Write UTF-8 text to a file, ensuring the parent directory exists."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(content)
