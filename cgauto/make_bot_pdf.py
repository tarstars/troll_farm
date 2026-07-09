#!/usr/bin/env python3
"""Generate a syntax-highlighted PDF reference of the current Troll Farm bot.

Renders the modular bot source (rust/src/botmain.rs + botmain/*.rs) as one
navigable PDF: a title page + architecture description + table of contents +
each module syntax-highlighted (minted/Pygments) with line numbers.

Toolchain: xelatex -shell-escape + minted + DejaVu Sans Mono (handles the
Unicode box-drawing chars in the comments and page-breaks long files).

Usage:  uv run --no-sync python cgauto/make_bot_pdf.py [out.pdf]
Default out: docs/troll-farm-bot.pdf
"""
import os, re, subprocess, sys, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = "/tmp/claude-1001/-home-tarstars-prj-troll-farm/402b95ba-f2eb-4014-9080-85c2c1e9d9a7/scratchpad/botpdf"

# reading order + one-line role of each module
MODULES = [
    ("rust/src/botmain.rs",
     "Entry point — CG protocol I/O parsing, the per-turn decide loop, and all tuning constants."),
    ("rust/src/botmain/state.rs",
     "Core types (State, Troll, Tree) + shared helpers (BFS distances, tie-break salts)."),
    ("rust/src/botmain/tactics.rs",
     "L1 tactics — builds the per-turn Plan: phase selection, farm geometry (farm_d, front-door), constants."),
    ("rust/src/botmain/planner.rs",
     "L2 planner — the joint TASK manager: candidates() produces per-troll value-banded tasks, "
     "assign_resolved() matches them conflict-free, race/sticky/yield refinements."),
    ("rust/src/botmain/motion.rs",
     "L3 motion — the joint MOVE solver: chooses landing cells jointly (swaps/chains), shuffle-invariant; watchdog."),
    ("rust/src/botmain/ownership.rs",
     "Ownership pressure telemetry (@TFOWN/@TFPRESS) — the parked total-map-value-ownership diagnostic."),
]


def tex_escape(s):
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"),
                 ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"),
                 ("^", r"\textasciicircum{}")]:
        s = s.replace(a, b)
    return s


def version():
    m = re.search(r'const VERSION: &str = "([^"]+)"', open(os.path.join(ROOT, "rust/src/botmain.rs")).read())
    return m.group(1) if m else "?"


DESCRIPTION = r"""
\section*{What this is}
The \textbf{Troll Farm} bot for the CodinGame Spring Challenge 2026 (2-player,
simultaneous-move resource game: harvest fruit and fell trees for wood; final
score is \texttt{fruit + 4*wood}). This document is a syntax-highlighted
reference of the live bot's Rust source.

\section*{Architecture --- a three-layer activity manager}
Each turn, \texttt{decide\_elite} runs three layers over the parsed \texttt{State}:
\begin{itemize}
  \item \textbf{L1 tactics} (\texttt{tactics.rs}) builds a \texttt{Plan}: which phase
        we are in, farm geometry (map-distance \texttt{farm\_d}, the front-door farm
        anchor), and the tuning it exposes to L2.
  \item \textbf{L2 planner} (\texttt{planner.rs}) is the \emph{task manager}.
        \texttt{candidates()} \emph{produces} each troll's viable tasks as
        \texttt{(target, value)} candidates, where the old sequential-cascade branch
        hierarchy becomes value \textbf{bands} (spaced $\gg$ any ETA, so priority never
        inverts; ETA differentiates within a band). \texttt{assign\_resolved()}
        \emph{matches} tasks to trolls jointly --- exhaustive over per-troll top-K,
        maximizing total value, forbidding conflicting claims, with a canonical
        tie-break. Refinements: a \texttt{race()} check (skip trees an enemy fells
        first), STICKY targets (anti-flap), and a task-interference yield pass.
  \item \textbf{L3 motion} (\texttt{motion.rs}) jointly chooses this turn's landing
        cells (swaps and chains through moving teammates), \textbf{shuffle-invariant}:
        the plan depends on the objective, never on iteration order.
\end{itemize}
The design principle throughout is that ``a troll misbehaving'' is really the task
manager producing the wrong task \emph{set} --- too few, mis-valued, or mis-located ---
so fixes target task production and valuation, not per-troll behavior.

\section*{Deployment}
The modules below live as a library so tests and a black-box equality harness can
reach them; a bundler (\texttt{tools/bundle.py}) re-inlines them into the single file
CodinGame accepts, then a minifier keeps it under the 100\,KB limit.
"""


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs/troll-farm-bot.pdf")
    os.makedirs(SCRATCH, exist_ok=True)
    ver = version()

    body = [
        r"\documentclass[9pt]{extarticle}",
        r"\usepackage[margin=1.5cm]{geometry}",
        r"\usepackage{fontspec}",
        r"\setmonofont{DejaVu Sans Mono}[Scale=0.88]",
        r"\usepackage{minted}",
        r"\usemintedstyle{friendly}",
        r"\usepackage{hyperref}",
        r"\hypersetup{colorlinks=true,linkcolor=blue!50!black,pdftitle={Troll Farm Bot Source Reference}}",
        r"\usepackage{titlesec}",
        r"\setminted{fontsize=\footnotesize,breaklines,breakanywhere,linenos,numbersep=4pt,frame=leftline,framesep=6pt}",
        r"\title{\textbf{Troll Farm Bot}\\[2pt]\large Source Reference}",
        r"\author{CodinGame Spring Challenge 2026 --- Gold league}",
        r"\date{Version \texttt{" + tex_escape(ver) + r"} --- generated \today}",
        r"\begin{document}",
        r"\maketitle",
        DESCRIPTION,
        r"\newpage",
        r"\tableofcontents",
        r"\newpage",
    ]
    for path, role in MODULES:
        abspath = os.path.join(ROOT, path)
        loc = sum(1 for _ in open(abspath))
        body.append(r"\section{\texttt{" + tex_escape(path.replace("rust/src/", "")) + r"}}")
        body.append(r"\noindent\textit{" + tex_escape(role) + r"} \\ \small(" + str(loc) + r" lines)\normalsize")
        body.append(r"\vspace{4pt}")
        body.append(r"\inputminted{rust}{" + abspath + r"}")
        body.append(r"\newpage")
    body.append(r"\end{document}")

    tex = os.path.join(SCRATCH, "botsrc.tex")
    open(tex, "w").write("\n".join(body))

    # xelatex twice for the TOC/page refs
    for i in range(2):
        r = subprocess.run(
            ["xelatex", "-shell-escape", "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory", SCRATCH, tex],
            cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            tail = "\n".join(l for l in r.stdout.splitlines() if l.startswith("!") or "Error" in l)
            print(f"xelatex pass {i+1} FAILED:\n{tail[-2000:]}")
            sys.exit(1)

    pdf = os.path.join(SCRATCH, "botsrc.pdf")
    shutil.copy(pdf, out)
    pages = "?"
    try:
        pages = subprocess.run(["pdfinfo", out], capture_output=True, text=True).stdout
        pages = re.search(r"Pages:\s+(\d+)", pages).group(1)
    except Exception:
        pass
    print(f"wrote {out}  ({os.path.getsize(out)//1024} KB, {pages} pages, version {ver})")


if __name__ == "__main__":
    main()
