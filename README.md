# evalvitals-site

The EvalVitals landing page. Live at
**https://xxlya.github.io/evalvitals-site/**

## Layout

    index.html      the page (edit this)
    build.py        wraps index.html into a standalone document -> docs/
    export_pdf.py   renders the served page to PDF
    docs/           generated; GitHub Pages serves from here

`index.html` is authored as a fragment — no `<!doctype>`, `<head>` or `<body>`,
because it doubles as a Claude Artifact, where those are supplied by the
renderer. `build.py` fills them in for static hosting.

## Working on it

```bash
python3 build.py            # regenerate docs/
cd docs && python3 -m http.server 8080
```

Then commit and push; Pages redeploys from `docs/` on the default branch.

## PDF

```bash
python3 export_pdf.py http://localhost:8080/ EvalVitals.pdf
```

Needs the local server running. The page reveals sections on scroll, so the
exporter emulates reduced-motion and force-shows every block first — otherwise
the PDF comes out blank.
