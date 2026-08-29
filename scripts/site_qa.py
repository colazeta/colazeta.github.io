#!/usr/bin/env python3
"""Static QA for the personal research portfolio."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
import sys

ROOT = Path(__file__).resolve().parents[1]
BANNED = (
    "wowchemy",
    "googletagmanager.com",
    "google-analytics.com",
    "cdn-cookieyes.com",
    "fonts.googleapis.com",
    "fonts.gstatic.com",
)
REQUIRED = (
    "index.html",
    "en/index.html",
    "it/index.html",
    "de/index.html",
    "cv/index.html",
    "privacy/index.html",
    "terms/index.html",
    "404.html",
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if tag in {"a", "link"} and data.get("href"):
            self.links.append(("href", data["href"] or ""))
        if tag in {"img", "script", "source"} and data.get("src"):
            self.links.append(("src", data["src"] or ""))


def resolve_local(page: Path, raw: str) -> Path | None:
    raw = raw.strip()
    if not raw or raw.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    parsed = urlparse(raw)
    if parsed.scheme or parsed.netloc:
        return None
    path = unquote(parsed.path)
    if not path:
        return None
    candidate = ROOT / path.lstrip("/") if path.startswith("/") else page.parent / path
    if path.endswith("/") or candidate.is_dir():
        candidate = candidate / "index.html"
    elif not candidate.suffix and not candidate.exists():
        candidate = candidate / "index.html"
    return candidate.resolve()


def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            errors.append(f"missing required page: {rel}")

    html_files = sorted(ROOT.rglob("*.html"))
    for page in html_files:
        text = page.read_text(encoding="utf-8")
        lower = text.lower()
        rel = page.relative_to(ROOT)
        for marker in BANNED:
            if marker in lower:
                errors.append(f"{rel}: banned legacy/third-party marker: {marker}")

        parser = LinkParser()
        parser.feed(text)
        for kind, raw in parser.links:
            target = resolve_local(page, raw)
            if target is None:
                continue
            try:
                target.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"{rel}: {kind} escapes repository root: {raw}")
                continue
            if not target.exists():
                errors.append(f"{rel}: broken local {kind}: {raw} -> {target.relative_to(ROOT)}")

    for lang in ("en", "it", "de"):
        page = ROOT / lang / "index.html"
        if not page.exists():
            continue
        text = page.read_text(encoding="utf-8")
        for marker in ('class="skip-link"', 'id="current"', 'id="methods"', 'id="public-projects"', 'id="profiles"'):
            if marker not in text:
                errors.append(f"{lang}/index.html: missing structural marker {marker}")

    cv = ROOT / "cv/index.html"
    if cv.exists():
        text = cv.read_text(encoding="utf-8")
        for phrase in ("Research and professional appointments", "Selected publications and research reports", "Selected conference presentations"):
            if phrase not in text:
                errors.append(f"cv/index.html: missing CV section: {phrase}")

    if errors:
        print("SITE QA FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"SITE QA PASSED: {len(html_files)} HTML files checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
