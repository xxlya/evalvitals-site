#!/usr/bin/env python3
"""Wrap the artifact fragment into a standalone HTML document.

index.html is authored for the Artifact renderer, which supplies
<!doctype>/<head>/<body> and a CSS reset at publish time. Static hosting does
not, so this produces docs/index.html with those pieces filled in. Edit
index.html only; docs/ is generated.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "index.html"
DIST = ROOT / "docs"

DOMAIN = "evalvitals.com"
DESCRIPTION = (
    "EvalVitals diagnoses why an open-weight model fails, then verifies the "
    "repair against the unmodified baseline."
)
FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E"
    "%3Ctext y='.9em' font-size='90'%3E%F0%9F%A9%BA%3C/text%3E%3C/svg%3E"
)

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{favicon}">
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  * {{ margin: 0; padding: 0; }}
  img, svg {{ display: block; max-width: 100%; }}
  button, input, select, textarea {{ font: inherit; color: inherit; }}
  ul, ol {{ list-style: none; }}
  html {{ -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }}
  @media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def main() -> int:
    raw = SRC.read_text(encoding="utf-8")

    m = re.search(r"<title>(.*?)</title>", raw, re.S)
    title = m.group(1).strip() if m else "EvalVitals"
    body = raw.replace(m.group(0), "", 1) if m else raw

    DIST.mkdir(exist_ok=True)
    out = DIST / "index.html"
    out.write_text(
        TEMPLATE.format(
            title=title, description=DESCRIPTION, favicon=FAVICON, body=body.strip()
        ),
        encoding="utf-8",
    )
    # GitHub Pages otherwise runs the output through Jekyll.
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    # The custom domain is part of the build, not a file that happens to be
    # sitting in docs/. Deleting docs/ and rebuilding used to drop this and
    # silently unbind evalvitals.com.
    (DIST / "CNAME").write_text(DOMAIN + "\n", encoding="utf-8")

    kb = out.stat().st_size / 1024
    print(f"built {out}  ({kb:.1f} KB)")
    print(f"title: {title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
