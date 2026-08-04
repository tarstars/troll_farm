#!/usr/bin/env python3
"""Build and validate the exact readable Troll Farm bot manual."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import markdown
from pygments.formatters import HtmlFormatter


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "local_codex_1/readable-orchard-code-cost/e7a-without-orchard-readable.rs"
MANUAL = ROOT / "docs/manuals/readable-no-orchard-rust-manual-2026-08-04.md"
PDF = ROOT / "docs/manuals/readable-no-orchard-rust-manual-2026-08-04.pdf"
BUILD_DIR = ROOT / "local_codex_1/readable-no-orchard-manual"
HTML = BUILD_DIR / "readable-no-orchard-rust-manual-2026-08-04.html"
INDEX = BUILD_DIR / "source-index.json"
EXPECTED_SHA256 = "98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_index() -> dict[str, object]:
    raw = SOURCE.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(f"source hash changed: {digest}")
    text = raw.decode("utf-8")
    lines = text.splitlines()
    symbols: list[dict[str, object]] = []
    symbol_pattern = re.compile(
        r"^\s*(?:#\[.*?\]\s*)?(?:pub\s+)?"
        r"(?P<kind>type|const|struct|enum|trait|fn)\s+"
        r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
    )
    for line_no, line in enumerate(lines, 1):
        match = symbol_pattern.search(line)
        if match:
            symbols.append(
                {
                    "kind": match.group("kind"),
                    "name": match.group("name"),
                    "line": line_no,
                    "declaration": line.strip(),
                }
            )
    code_lines = sum(
        1 for line in lines if line.strip() and not line.lstrip().startswith("//")
    )
    payload = {
        "schema": 1,
        "source": str(SOURCE.relative_to(ROOT)),
        "sha256": digest,
        "bytes": len(raw),
        "physical_lines": len(lines),
        "code_lines": code_lines,
        "symbols": symbols,
    }
    INDEX.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def render_html(index: dict[str, object]) -> None:
    source = MANUAL.read_text(encoding="utf-8")
    body = markdown.markdown(
        source,
        extensions=["extra", "codehilite", "toc", "sane_lists"],
        extension_configs={"toc": {"permalink": "¶", "toc_depth": "1-3"}},
    )
    pygments_css = HtmlFormatter(style="friendly").get_style_defs(".codehilite")
    css = f"""
@page {{ size: A4; margin: 18mm 16mm 19mm 17mm; }}
@page :first {{ margin: 0; }}
* {{ box-sizing: border-box; }}
html {{ font-size: 10.2pt; }}
body {{ font-family: 'Noto Sans', 'DejaVu Sans', sans-serif; color: #17202a;
       line-height: 1.48; margin: 0; }}
h1, h2, h3, h4 {{ color: #102a43; page-break-after: avoid; line-height: 1.18; }}
h1 {{ font-size: 23pt; border-bottom: 2px solid #2f80a7; padding-bottom: 5px;
     margin-top: 1.1em; }}
h2 {{ font-size: 16pt; margin-top: 1.25em; }}
h3 {{ font-size: 12.5pt; margin-top: 1.1em; }}
h4 {{ font-size: 10.5pt; }}
p, li {{ orphans: 3; widows: 3; }}
a {{ color: #176b87; text-decoration: none; }}
code {{ font-family: 'Noto Sans Mono', 'DejaVu Sans Mono', monospace; font-size: 8.8pt;
       background: #edf2f7; padding: 0.08em 0.25em; border-radius: 2px; }}
pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #f6f8fa;
      border-left: 3px solid #2f80a7; padding: 8px 10px; page-break-inside: avoid; }}
pre code {{ background: transparent; padding: 0; font-size: 8.1pt; }}
table {{ width: 100%; border-collapse: collapse; margin: 0.8em 0 1.1em;
        page-break-inside: avoid; font-size: 9pt; }}
th {{ background: #d9edf3; text-align: left; }}
th, td {{ border: 1px solid #aab7c4; padding: 5px 6px; vertical-align: top; }}
blockquote {{ margin: 0.8em 0; padding: 0.45em 0.9em; background: #fff7df;
             border-left: 4px solid #e1a928; }}
.title-page {{ height: 297mm; padding: 38mm 24mm 24mm; color: white;
              background: linear-gradient(145deg, #102a43 0%, #176b87 62%, #3bb3b0 100%);
              page-break-after: always; }}
.title-page h1 {{ color: white; border: 0; font-size: 34pt; max-width: 155mm; margin: 0; }}
.title-page h2 {{ color: #d9f0f0; font-size: 18pt; font-weight: 400; max-width: 150mm; }}
.title-page p {{ max-width: 145mm; font-size: 12pt; }}
.title-page code {{ background: rgba(255,255,255,.14); color: white; }}
.chapter {{ page-break-before: always; }}
.callout {{ background: #eaf7f4; border: 1px solid #8ac9be; padding: 8px 10px;
           margin: 0.8em 0; page-break-inside: avoid; }}
.warning {{ background: #fff0ef; border-color: #db8882; }}
.small {{ font-size: 8.5pt; color: #536471; }}
.flow {{ font-family: 'Noto Sans Mono', 'DejaVu Sans Mono', monospace; white-space: pre-wrap;
        background: #eef6fa; border: 1px solid #a9c9d8; padding: 10px;
        page-break-inside: avoid; }}
hr {{ border: 0; border-top: 1px solid #b9c5ce; margin: 1.4em 0; }}
{pygments_css}
"""
    metadata = (
        f"Source SHA-256: {index['sha256']} · "
        f"{index['code_lines']} code lines · generated manual build"
    )
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Troll Farm bot: Rust from zero</title>
<style>{css}</style></head><body>{body}
<p class="small">{metadata}</p></body></html>"""
    HTML.write_text(html, encoding="utf-8")


def render_pdf() -> None:
    browser = next(
        (
            shutil.which(name)
            for name in ("google-chrome", "chromium", "chromium-browser")
            if shutil.which(name)
        ),
        None,
    )
    if browser is None:
        raise SystemExit("no Chromium-compatible browser found")
    with tempfile.TemporaryDirectory(prefix="troll-farm-manual-chrome-") as profile:
        command = [
            browser,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--user-data-dir={profile}",
            f"--print-to-pdf={PDF}",
            HTML.resolve().as_uri(),
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-pdf", action="store_true")
    args = parser.parse_args()
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    PDF.parent.mkdir(parents=True, exist_ok=True)
    index = source_index()
    render_html(index)
    if not args.no_pdf:
        render_pdf()
    print(
        f"source={index['sha256']} symbols={len(index['symbols'])} "
        f"html={HTML.relative_to(ROOT)} "
        f"pdf={'skipped' if args.no_pdf else PDF.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
