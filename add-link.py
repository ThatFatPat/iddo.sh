#!/usr/bin/env python3
"""Add a link to the iddo.sh links section.

Usage:
  ./add-link.py <url> <title> [description]

Examples:
  ./add-link.py https://example.com "Cool Article"
  ./add-link.py https://example.com "Cool Article" "A short note about why it's interesting"
"""

import sys
import json
import re
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
LINKS_FILE = SCRIPT_DIR / "links.json"
HTML_FILE  = SCRIPT_DIR / "index.html"

START_MARKER = "<!-- LINKS_START -->"
END_MARKER   = "<!-- LINKS_END -->"


def usage():
    print(__doc__)
    sys.exit(1)


def load_links():
    return json.loads(LINKS_FILE.read_text())


def save_links(links):
    LINKS_FILE.write_text(json.dumps(links, indent=2) + "\n")


def render_links(links):
    if not links:
        return ""
    lines = []
    for link in reversed(links):  # newest first
        desc_html = f'\n        <span class="desc">{escape(link["desc"])}</span>' if link.get("desc") else ""
        lines.append(
            f'        <li class="link-item">\n'
            f'          <a href="{escape(link["url"])}" target="_blank" rel="noopener noreferrer">{escape(link["title"])}</a>'
            f'{desc_html}\n'
            f'          <span class="meta">{link["date"]}</span>\n'
            f'        </li>'
        )
    return "\n" + "\n".join(lines) + "\n      "


def escape(text):
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def update_html(links):
    html = HTML_FILE.read_text()
    pattern = re.compile(
        rf"({re.escape(START_MARKER)}).*?({re.escape(END_MARKER)})",
        re.DOTALL,
    )
    replacement = rf"\1{render_links(links)}\2"
    updated, count = pattern.subn(replacement, html)
    if count == 0:
        print("Error: could not find LINKS_START/LINKS_END markers in index.html", file=sys.stderr)
        sys.exit(1)
    HTML_FILE.write_text(updated)


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        usage()

    url, title = args[0], args[1]
    desc = args[2] if len(args) >= 3 else ""

    if not url.startswith(("http://", "https://")):
        print(f"Error: URL must start with http:// or https://", file=sys.stderr)
        sys.exit(1)

    links = load_links()
    links.append({
        "url":   url,
        "title": title,
        "desc":  desc,
        "date":  str(date.today()),
    })
    save_links(links)
    update_html(links)

    print(f"Added: {title}")
    print(f"  URL:  {url}")
    if desc:
        print(f"  Note: {desc}")
    print(f"Total links: {len(links)}")


if __name__ == "__main__":
    main()
