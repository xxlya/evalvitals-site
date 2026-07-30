#!/usr/bin/env python3
"""Render the served site to PDF.

Two things break a naive export:

1. Sections start at opacity:0 and are revealed on scroll. Printing without
   triggering them yields blank pages, so reduced-motion is emulated (the page
   then reveals everything on load) and every block is force-shown as a
   belt-and-braces check.
2. The sticky top bar would reprint over the content on every page break, and
   cards would be sliced across pages.

Usage:  python3 export_pdf.py [url] [outfile]
"""
from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080/"
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "evalvitals.pdf").resolve()

PRINT_CSS = """
  /* Chrome must not repeat the floating bar on every page. */
  .topbar { position: static !important; backdrop-filter: none !important;
            background: transparent !important; border-bottom: 0 !important; }
  .topbar::after { display: none !important; }

  /* Nothing may be mid-animation, whatever the media emulation did. */
  .reveal, .reveal.in { opacity: 1 !important; transform: none !important;
                        transition: none !important; }

  /* Keep individual figures, cards and rows whole, but let a section itself
     flow across a break — forcing whole sections onto fresh pages left half a
     page empty each time and inflated the document by several pages. */
  figure, .readout, .hl, .io > div, .term, table.cmp, .split, .papers > div,
  .rung { break-inside: avoid; page-break-inside: avoid; }
  h1, h2, h3 { break-after: avoid; page-break-after: avoid; }
  section.row { padding: 2.2rem 0; }

  /* Give the sheet a little breathing room at the edges. */
  .wrap { max-width: none; padding: 0 0.4in; }
"""


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 1600})
        # Screen media keeps the real design; reduced-motion makes the page
        # render every section immediately instead of waiting for scroll.
        page.emulate_media(media="screen", color_scheme="light", reduced_motion="reduce")
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(2500)

        page.add_style_tag(content=PRINT_CSS)
        page.evaluate(
            "document.querySelectorAll('.reveal').forEach(e => e.classList.add('in'))"
        )
        # Walk the page so anything lazy has definitely resolved.
        page.evaluate("""async () => {
            const step = window.innerHeight;
            for (let y = 0; y < document.body.scrollHeight; y += step) {
                window.scrollTo(0, y);
                await new Promise(r => setTimeout(r, 60));
            }
            window.scrollTo(0, 0);
        }""")
        page.wait_for_timeout(1200)

        hidden = page.eval_on_selector_all(
            ".reveal:not(.in)", "els => els.length"
        )
        if hidden:
            print(f"WARNING: {hidden} block(s) still hidden — PDF may be incomplete")

        page.pdf(
            path=str(OUT),
            format="A4",
            print_background=True,
            margin={"top": "0.5in", "bottom": "0.5in", "left": "0.35in", "right": "0.35in"},
            prefer_css_page_size=False,
        )
        browser.close()

    print(f"wrote {OUT}  ({OUT.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
