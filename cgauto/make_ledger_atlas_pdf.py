#!/usr/bin/env python3
"""Render docs/LEDGER-MAP.md (the D-series atlas) as a readable PDF.

Converts the atlas's controlled markdown subset (##-sections, paragraphs,
bullet lists, 3-column pipe tables, **bold**, `code`) to XeLaTeX and compiles
with xelatex (same toolchain as make_bot_pdf.py; DejaVu fonts for full
Unicode: arrows, stars, math comparisons).

Usage:  python3 cgauto/make_ledger_atlas_pdf.py [out.pdf]
Default out: docs/D-series-atlas.pdf
"""
import os
import re
import subprocess
import sys
import shutil
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "LEDGER-MAP.md")
DEFAULT_OUT = os.path.join(ROOT, "docs", "D-series-atlas.pdf")

PREAMBLE = r"""
\documentclass[10pt,a4paper]{article}
\usepackage[margin=2.1cm,top=2.3cm,bottom=2.4cm]{geometry}
\usepackage{fontspec}
\setmainfont{DejaVu Serif}
\setsansfont{DejaVu Sans}
\setmonofont{DejaVu Sans Mono}[Scale=0.86]
\usepackage[table]{xcolor}
\usepackage{tocloft}
\setlength{\cftsecnumwidth}{2.2em}
\definecolor{arc}{HTML}{1A5276}
\definecolor{rulegray}{HTML}{B0BEC5}
\definecolor{rowgray}{HTML}{F4F6F7}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{array}
\usepackage[colorlinks=true,linkcolor=arc,urlcolor=arc]{hyperref}
\usepackage{sectsty}
\sectionfont{\color{arc}\sffamily\large}
\subsectionfont{\color{arc}\sffamily\normalsize}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\renewcommand{\arraystretch}{1.25}
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\sffamily\footnotesize\color{arc} Troll Farm — D-Series Atlas}
\fancyhead[R]{\sffamily\footnotesize\color{arc} 2026-07-27}
\fancyfoot[C]{\sffamily\footnotesize\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\begin{document}
"""

TITLE = r"""
{\centering
{\sffamily\bfseries\LARGE\color{arc} Troll Farm — The D-Series Atlas\par}
\vspace{4pt}
{\sffamily\large A reader's guide to every numbered experiment of the Legend top-3 cycle\par}
\vspace{2pt}
{\sffamily\small Snapshot 2026-07-27 \quad·\quad ledger vol 1+2 \quad·\quad
\texttt{docs/CONSTRAINTS.md} \quad·\quad \texttt{docs/STATE.md}\par}
\vspace{6pt}
{\color{rulegray}\hrule height 1.2pt}
\par}
\vspace{6pt}
\tableofcontents
\vspace{8pt}
{\color{rulegray}\hrule height 0.6pt}
\vspace{4pt}
"""


def unwrap(md_lines):
    """Join hard-wrapped continuation lines so inline spans never cross lines.

    A line continues the previous one when the previous is non-blank and the
    current line is indented plain text (not a header, bullet, table row, or
    blank line)."""
    logical = []
    for raw in md_lines:
        line = raw.rstrip("\n")
        stripped = line.strip()
        if (logical and stripped and not stripped.startswith(("#", "|", "- "))
                and logical[-1].strip()
                and not logical[-1].lstrip().startswith("|")):
            logical[-1] = logical[-1] + " " + stripped
        else:
            logical.append(line)
    return logical


def esc(text: str) -> str:
    """Escape LaTeX specials, then apply inline bold/code markup."""
    for ch, rep in [("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("$", r"\$"),
                    ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
                    ("~", r"\textasciitilde{}")]:
        text = text.replace(ch, rep)
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\\textit{\1}", text)
    text = re.sub(r"`([^`]+)`", r"\\texttt{\1}", text)
    return text


def convert(md_lines):
    out = []
    table = []
    in_list = False

    def flush_table():
        nonlocal table
        if not table:
            return
        header, rows = table[0], table[2:]  # row 1 is the |---| separator
        out.append(r"\begin{longtable}{>{\raggedright\arraybackslash}p{2.0cm}"
                   r">{\raggedright\arraybackslash}p{5.4cm}"
                   r">{\raggedright\arraybackslash}p{7.4cm}}")
        out.append(r"\toprule")
        out.append(" & ".join(rf"\textbf{{\sffamily {esc(c)}}}" for c in header) + r" \\")
        out.append(r"\midrule\endhead")
        for i, row in enumerate(rows):
            if i % 2 == 1:
                out.append(r"\rowcolor{rowgray}")
            out.append(" & ".join(esc(c) for c in row) + r" \\")
        out.append(r"\bottomrule")
        out.append(r"\end{longtable}")
        table = []

    def close_list():
        nonlocal in_list
        if in_list:
            out.append(r"\end{itemize}")
            in_list = False

    for raw in md_lines:
        line = raw.rstrip("\n")
        if line.startswith("|"):
            close_list()
            cells = [c.strip() for c in line.strip("|").split("|")]
            table.append(cells)
            continue
        flush_table()
        if line.startswith("# "):
            continue  # document title handled by TITLE block
        if line.startswith("## "):
            close_list()
            title = re.sub(r"^\d+\.\s*", "", line[3:])
            out.append(rf"\section{{{esc(title)}}}")
            continue
        if line.startswith("- "):
            if not in_list:
                out.append(r"\begin{itemize}\setlength\itemsep{2pt}")
                in_list = True
            out.append(rf"\item {esc(line[2:])}")
            continue
        if not line.strip():
            close_list()
            out.append("")
            continue
        out.append(esc(line))
    flush_table()
    close_list()
    return "\n".join(out)


def main():
    out_pdf = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    with open(SRC, encoding="utf-8") as f:
        md = f.readlines()
    body = convert(unwrap(md))
    tex = PREAMBLE + TITLE + body + "\n\\end{document}\n"
    with tempfile.TemporaryDirectory(prefix="atlas-") as tmp:
        tex_path = os.path.join(tmp, "atlas.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(tex)
        for _ in range(2):  # twice for TOC
            r = subprocess.run(["xelatex", "-interaction=nonstopmode", "atlas.tex"],
                               cwd=tmp, capture_output=True, text=True)
        pdf = os.path.join(tmp, "atlas.pdf")
        if not os.path.exists(pdf):
            sys.stderr.write(r.stdout[-3000:] + "\n" + r.stderr[-500:])
            sys.exit(1)
        shutil.copy(pdf, out_pdf)
    print(f"wrote {out_pdf} ({os.path.getsize(out_pdf)} bytes)")


if __name__ == "__main__":
    main()
