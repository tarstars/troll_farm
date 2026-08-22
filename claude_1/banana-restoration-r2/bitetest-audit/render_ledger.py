#!/usr/bin/env python3
"""Render the prose mutation tables from the committed raw results.

The 2026-08-08 audit's tables were hand-written from a discarded scratch run.
This script regenerates them from ``results/mutation-results.json`` so the
prose in the audit is a projection of the machine-readable evidence, not an
independent transcription (review BAR-1).

    python3 render_ledger.py            # writes results/mutation-ledger.md
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results", "mutation-results.json")
OUT = os.path.join(HERE, "results", "mutation-ledger.md")

DETS = ["D-1", "D-2", "D-3", "D-4", "D-5", "D-6", "D-7", "D-8", "D-9"]


def esc(text):
    """Escape pipes so free-text intents cannot break the markdown table."""
    return (text or "").replace("|", "\\|").strip()


def main(argv=None):
    argv = argv or sys.argv[1:]
    src = argv[0] if argv else RESULTS
    with open(src, encoding="utf-8") as fh:
        doc = json.load(fh)
    t = doc["totals"]
    rows = [r for r in doc["mutants"]
            if r.get("status") == "OK" and not r.get("excluded_from_totals")]
    by_id = {r["id"]: r for r in rows}

    out = []
    out.append("# Mutation ledger (generated — do not hand-edit)\n")
    out.append("Source: `results/mutation-results.json`  \n"
               "manifest sha256 `%s`  \n"
               "runner sha256 `%s`  \n"
               "probe corpus sha256 `%s`  \n"
               "python %s, control green: %s\n"
               % (doc["manifest_sha256"], doc["runner_sha256"],
                  doc["probe_corpus_sha256"], doc["python"],
                  doc["control"]["green"]))
    out.append("Pinned sources:\n")
    for k, v in sorted(doc["pinned_sources"].items()):
        out.append("- `%s` sha256 `%s`" % (k, v))
    out.append("")
    out.append("Totals: **%d mutants run, %d caught, %d survived** "
               "(kill rate %.1f %%). `caught_by_expected` = %d; caught only "
               "by another detector's tests = %d. Liveness: %d PROBE_SENSITIVE, "
               "%d UNWITNESSED; PROBE_SENSITIVE survivors = %d.\n"
               % (t["mutants_run"], t["caught"], t["survived"],
                  100.0 * t["kill_rate_caught"], t["caught_by_expected"],
                  t["caught_only_by_other_detector"], t["probe_sensitive"],
                  t["unwitnessed"], t["probe_sensitive_survivors"]))

    out.append("## Per detector\n")
    out.append("| Det | mutants | caught | caught_by_expected | survived | "
               "PROBE_SENSITIVE survivors | kill rate |")
    out.append("|---|---|---|---|---|---|---|")
    for d in DETS:
        p = doc["per_detector"][d]
        out.append("| %s | %d | %d | %d | %d | %d | %.0f %% |"
                   % (d, p["mutants"], p["caught"], p["caught_by_expected"],
                      p["mutants"] - p["caught"], p["probe_sensitive_survivors"],
                      100.0 * p["caught"] / p["mutants"]))
    out.append("| **all** | **%d** | **%d** | **%d** | **%d** | **%d** | "
               "**%.1f %%** |"
               % (t["mutants_run"], t["caught"], t["caught_by_expected"],
                  t["survived"], t["probe_sensitive_survivors"],
                  100.0 * t["kill_rate_caught"]))
    out.append("")

    out.append("## Full ledger\n")
    out.append("`result` = CAUGHT / SURVIVED against the full 28-test suite. "
               "`liveness` = PROBE_SENSITIVE if the patch changes the mutated detector's "
               "probe digest. PROBE_SENSITIVE means the mutation changes probe "
               "output on GENERATED traces; it does NOT establish legal-game "
               "reachability under the referee. "
               "digest over the independent probe corpus, UNWITNESSED if the "
               "corpus cannot witness any behavioural change (such a "
               "survivor is *not* evidence that the suite is weak).\n")
    out.append("| id | det | file | result | liveness | mutation |")
    out.append("|---|---|---|---|---|---|")
    for d in DETS:
        for r in [x for x in rows if x["detector"] == d]:
            out.append("| %s | %s | `%s` | %s | %s | %s |"
                       % (r["id"], r["detector"], r["file"],
                          "CAUGHT" if r["caught"] else "SURVIVED",
                          r["liveness"], esc(r["intent"])))
    out.append("")

    if doc.get("excluded_entries"):
        out.append("## Entries excluded from the totals\n")
        out.append("| id | det | result | liveness | why excluded |")
        out.append("|---|---|---|---|---|")
        for r in doc["excluded_entries"]:
            out.append("| %s | %s | %s | %s | %s |"
                       % (r["id"], r["detector"],
                          "CAUGHT" if r["caught"] else "SURVIVED",
                          r["liveness"], esc(r.get("note"))))
        out.append("")

    out.append("## Mutated-file SHA-256\n")
    out.append("| id | mutated `%s` sha256 |" % "target file")
    out.append("|---|---|")
    for r in rows:
        out.append("| %s | `%s` |" % (r["id"], r["mutated_sha256"]))
    out.append("")

    text = "\n".join(out)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    sys.stderr.write("wrote %s (%d ids)\n" % (OUT, len(by_id)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
