"""PDF generation for the artist portfolio.

Generates three types of PDFs:
1. Full Artist Portfolio (selected works + bio + statement + CV)
2. Artist CV
3. Individual Project PDFs

Uses WeasyPrint for high-quality print output.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from utils import (
    CONTENT_DIR,
    PUBLIC_DIR,
    ROOT,
    TEMPLATES_DIR,
    ensure_pdfs_dir,
    load_all_json,
    load_json,
)

try:
    from weasyprint import CSS, HTML  # type: ignore
except (ImportError, OSError, Exception):  # pragma: no cover
    print("WARNING: weasyprint not available — skipping PDF generation.", file=sys.stderr)
    HTML = None  # type: ignore
    CSS = None  # type: ignore


def _nl2br(value: str) -> str:
    import markupsafe
    if not value:
        return ""
    escaped = markupsafe.escape(value)
    return markupsafe.Markup("<br>\n").join(escaped.splitlines())


def _date_display(value: str) -> str:
    from datetime import datetime
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%B %Y")
    except ValueError:
        return value


def _jinja_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader([str(TEMPLATES_DIR), str(ROOT)]),
        autoescape=select_autoescape(enabled_extensions=("html", "xml")),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["nl2br"] = _nl2br
    env.filters["date_display"] = _date_display
    return env


def _collect_context() -> dict[str, Any]:
    site = load_json(CONTENT_DIR / "settings" / "site.json")
    artist = load_json(CONTENT_DIR / "artist" / "profile.json")
    artworks = sorted(
        [a for a in load_all_json(CONTENT_DIR / "artworks") if a.get("published", True)],
        key=lambda a: (a.get("order", 999), a.get("year", 0)),
    )
    projects = sorted(
        [p for p in load_all_json(CONTENT_DIR / "projects") if p.get("published", True)],
        key=lambda p: (p.get("order", 999),),
    )
    exhibitions = sorted(
        load_all_json(CONTENT_DIR / "exhibitions"),
        key=lambda e: (e.get("order", 999),),
    )
    cv = load_json(CONTENT_DIR / "cv" / "cv.json")

    # Attach artwork lookup by slug for projects
    artwork_by_slug = {a["slug"]: a for a in artworks}
    for proj in projects:
        proj["artworks_objects"] = [
            artwork_by_slug[s] for s in proj.get("artworks", []) if s in artwork_by_slug
        ]

    return {
        "site": site,
        "artist": artist,
        "artworks": artworks,
        "projects": projects,
        "exhibitions": exhibitions,
        "cv": cv,
        "base_href": ROOT.as_uri() + "/",
        "ROOT": ROOT,
    }


def _render(template_name: str, context: dict[str, Any]) -> str:
    env = _jinja_env()
    template = env.get_template(template_name)
    return template.render(**context)


def _fallback_pdf(html_text: str, output_path: Path) -> None:
    """Create a usable PDF when WeasyPrint's native libraries are unavailable."""
    from html.parser import HTMLParser
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    from xml.sax.saxutils import escape

    class TextExtractor(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.parts: list[str] = []
            self.ignored_depth = 0
        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            if tag in {"head", "style", "script"}:
                self.ignored_depth += 1
                return
            if self.ignored_depth:
                return
            if tag in {"h1", "h2", "h3", "p", "li", "div", "br"}:
                self.parts.append("\n")
        def handle_endtag(self, tag: str) -> None:
            if tag in {"head", "style", "script"} and self.ignored_depth:
                self.ignored_depth -= 1
        def handle_data(self, data: str) -> None:
            if self.ignored_depth:
                return
            text = data.strip()
            if text:
                self.parts.append(text.replace("—", "-").replace("–", "-").replace("•", "-").replace("·", "-").replace("©", "Copyright") + " ")

    parser = TextExtractor()
    parser.feed(html_text)
    lines = [" ".join(line.split()) for line in "".join(parser.parts).splitlines()]
    lines = [line for line in lines if line]
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title", parent=styles["Heading1"], fontName="Helvetica", fontSize=22, leading=27, textColor=HexColor("#1a1917"), spaceAfter=12)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.5, leading=14, textColor=HexColor("#1a1917"), spaceAfter=5)
    story = [Paragraph(escape(lines[0] if lines else "Artist document"), title)]
    story.extend(Paragraph(escape(line), body) for line in lines[1:])
    SimpleDocTemplate(str(output_path), pagesize=A4, leftMargin=22 * mm, rightMargin=22 * mm, topMargin=20 * mm, bottomMargin=18 * mm).build(story)
    print(f"  [OK] {output_path.relative_to(ROOT)} (ReportLab fallback)")


def _to_pdf(html_text: str, output_path: Path, css_path: Path | None = None) -> None:
    if HTML is None:
        _fallback_pdf(html_text, output_path)
        return
        print(f"  weasyprint not installed — writing HTML instead: {output_path.with_suffix('.html')}")
        output_path.with_suffix(".html").write_text(html_text, encoding="utf-8")
        return
    html = HTML(string=html_text, base_url=str(ROOT))
    stylesheets = []
    if css_path and css_path.exists():
        stylesheets.append(CSS(filename=str(css_path)))
    html.write_pdf(str(output_path), stylesheets=stylesheets or None)
    print(f"  [OK] {output_path.relative_to(ROOT)}")


def generate_portfolio_pdf() -> None:
    pdfs = ensure_pdfs_dir()
    output = pdfs / "abdullahi-ndagi-adamu-portfolio.pdf"
    ctx = _collect_context()
    html_text = _render("pdf_portfolio.html", ctx)
    _to_pdf(html_text, output)


def generate_cv_pdf() -> None:
    pdfs = ensure_pdfs_dir()
    output = pdfs / "abdullahi-ndagi-adamu-cv.pdf"
    ctx = _collect_context()
    html_text = _render("pdf_cv.html", ctx)
    _to_pdf(html_text, output)


def generate_project_pdfs() -> None:
    pdfs = ensure_pdfs_dir()
    ctx = _collect_context()
    for proj in ctx["projects"]:
        slug = proj["slug"]
        output = pdfs / f"project-{slug}.pdf"
        html_text = _render("pdf_project.html", {**ctx, "project": proj})
        _to_pdf(html_text, output)


def generate_all() -> None:
    print("Generating PDFs…")
    generate_portfolio_pdf()
    generate_cv_pdf()
    generate_project_pdfs()


if __name__ == "__main__":
    generate_all()
