"""Inject Open Graph / Twitter link-preview tags into Streamlit's index.html.

Social crawlers don't run JavaScript, so tags set from Python at runtime never
reach them. Streamlit serves a static index.html, so we patch it once at startup.
Set SITE_URL to your public URL (e.g. https://dig.onrender.com) — preview
images must be absolute URLs.
"""
import logging
import os
import re
from html import escape
from pathlib import Path

log = logging.getLogger("seo")

TITLE = "Dig — deep research"
DESCRIPTION = "Ask once. Four AI agents search, read, write and critique — you get one sourced report with a score."
MARKER = "<!-- dig-og -->"


def _tags() -> str:
    base = os.getenv("SITE_URL", "").rstrip("/")
    image = f"{base}/app/static/og-image.png" if base else "app/static/og-image.png"
    meta = [
        ("name", "description", DESCRIPTION),
        ("property", "og:type", "website"),
        ("property", "og:site_name", "Dig"),
        ("property", "og:title", TITLE),
        ("property", "og:description", DESCRIPTION),
        ("property", "og:image", image),
        ("property", "og:image:width", "1200"),
        ("property", "og:image:height", "630"),
        ("name", "twitter:card", "summary_large_image"),
        ("name", "twitter:title", TITLE),
        ("name", "twitter:description", DESCRIPTION),
        ("name", "twitter:image", image),
    ]
    if base:
        meta.append(("property", "og:url", base))
    return MARKER + "".join(f'<meta {k}="{n}" content="{escape(v, quote=True)}">' for k, n, v in meta)


def inject() -> None:
    try:
        import streamlit

        index = Path(streamlit.__file__).parent / "static" / "index.html"
        html = index.read_text(encoding="utf-8")
        tags = _tags()
        if MARKER in html:  # refresh tags written by an earlier run
            html = re.sub(re.escape(MARKER) + r"(?:<meta [^>]*>)*", lambda _: tags, html, count=1)
        else:
            html = html.replace("</head>", tags + "</head>", 1)
        # Streamlit ships its own <title>; replace so crawlers see ours.
        html = re.sub(r"<title>.*?</title>", f"<title>{escape(TITLE)}</title>", html, count=1)
        index.write_text(html, encoding="utf-8")
    except Exception:  # never block the app over a preview tag
        log.exception("Could not inject link-preview tags")


if __name__ == "__main__":
    # Run before the server starts so even the very first crawler sees the tags:
    #   python seo.py && streamlit run app.py ...
    inject()
