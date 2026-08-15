#!/usr/bin/env python3
"""P-1 increment 2 — the REQUIRED-SITE INVENTORY, derived from the subject.

`codex_1`'s review of increment 1 (`155d8dd8`) named the hole precisely:

> Completeness and semantic mapping need an independently curated required-site inventory or
> conformance assertions against the contract — **not comparison with the same `SITES` list used
> to build the registry.**

That is the defect this module exists to remove. **Nothing here reads `registry.SITES` to decide
what ought to exist.** The required set is enumerated from the subject's own text, so the registry
can finally be measured against something it did not author.

## What §5.4 requires an id for, and how each is found in the source

| §5.4 class | enumerated as | why that is the right proxy |
|---|---|---|
| generator | `fn` definition | a generator is a function in this subject |
| **score term** | `Candidate{...}` construction | every emitted candidate carries one `score:` expression; the construction *is* the term |
| **filter** | `.filter(` / `.retain(` / `continue` guard | the three ways this subject discards a considered option |
| **early return** | `return` statement | §5.4 names early returns explicitly; step 2 must show which fired |
| compatibility rule / replacement / resolver branch | `.max_by` / `.sort` arbitration | where an ordering decides the outcome |

**These are proxies and they are stated as proxies.** A `continue` inside a loop that merely skips
a malformed row is not a semantic filter, and this module cannot tell the difference. It therefore
reports a *candidate* inventory for independent review — it does not certify one. Curation is a
human judgment and belongs to whoever checks it, which per my own commitment is **not me**.

## Coverage is measured, not asserted

`coverage()` reports how many enumerated sites fall inside a registered site's line span. It
answers "does the registry name this piece of code at all", NOT "does it name it correctly" —
semantic mapping stays open, exactly as the review says.

Run:
    python3 claude_1/decision_packet/inventory.py --self-test
    python3 claude_1/decision_packet/inventory.py --report
    python3 claude_1/decision_packet/inventory.py --freeze
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import registry as R  # noqa: E402  (the registry is the SUBJECT of measurement, not its source)

INVENTORY_PATH = "claude_1/decision_packet/required-site-inventory.json"
SCHEMA = "troll-farm-decision-packet-inventory/v1"

FN_RE = R.FN_RE
STRING_RE = re.compile(r'"(?:[^"\\]|\\.)*"')
LINE_COMMENT_RE = re.compile(r"//.*$")

#: Each class is (id_prefix, matcher). Matchers run on code with strings and comments stripped,
#: so a `//` mentioning `return` or a `format!("...continue...")` cannot invent a site.
CLASSES = [
    ("TERM", lambda s: s.count("Candidate{")),
    ("FILTER", lambda s: s.count(".filter(") + s.count(".retain(")
     + len(re.findall(r"\bcontinue\b", s))),
    ("EARLYRET", lambda s: len(re.findall(r"\breturn\b", s))),
    ("ARBITRATE", lambda s: len(re.findall(r"\.max_by|\.min_by|\.sort", s))),
]


def strip_noncode(line):
    """Remove string literals and line comments so text inside them cannot mint a site."""
    return LINE_COMMENT_RE.sub("", STRING_RE.sub('""', line))


def enclosing_functions(lines):
    """Map every line number to the function whose body contains it."""
    starts = [(i, m.group(2)) for i, line in enumerate(lines, 1)
              for m in [FN_RE.match(line)] if m]
    spans = []
    for idx, (ln, name) in enumerate(starts):
        end = starts[idx + 1][0] - 1 if idx + 1 < len(starts) else len(lines)
        spans.append((ln, end, name))
    at = {}
    for ln, end, name in spans:
        for i in range(ln, end + 1):
            at[i] = (name, ln, end)
    return spans, at


def enumerate_sites(lines=None):
    """Enumerate every §5.4-required site from the SOURCE. Never consults `registry.SITES`."""
    lines = R.subject_lines() if lines is None else lines
    spans, at = enclosing_functions(lines)
    out = []
    # generators: one per function definition
    for ln, end, name in spans:
        out.append({
            "derived_id": f"GEN__{name}__{ln}", "klass": "GEN", "fn": name,
            "line": ln, "fn_start": ln, "fn_end": end,
            "text": " ".join(lines[ln - 1].split())[:160],
        })
    # sub-function sites
    per_fn_counter = {}
    for i, raw in enumerate(lines, 1):
        code = strip_noncode(raw)
        if not code.strip():
            continue
        name, fn_start, fn_end = at.get(i, ("<file>", 0, 0))
        for prefix, matcher in CLASSES:
            n = matcher(code)
            for _ in range(n):
                key = (prefix, name)
                per_fn_counter[key] = per_fn_counter.get(key, 0) + 1
                out.append({
                    "derived_id": f"{prefix}__{name}__{per_fn_counter[key]}",
                    "klass": prefix, "fn": name, "line": i,
                    "fn_start": fn_start, "fn_end": fn_end,
                    "text": " ".join(raw.split())[:160],
                })
    return out


def coverage(required=None, registered=None):
    """Which enumerated sites does the registry name at all?

    Registered sites are whole functions, so a sub-function site is 'covered' when it falls
    inside a registered span. **This measures naming, not correctness** — a covered site may
    still carry the wrong stage or intent, which is the semantic gap the review left open and
    which nothing in this file closes.
    """
    required = enumerate_sites() if required is None else required
    if registered is None:
        registered = R.derive(R.subject_lines())
    spans = [(s["start_line"], s["end_line"], s["site_id"]) for s in registered]
    covered, uncovered = [], []
    for site in required:
        hit = next((sid for a, b, sid in spans if a <= site["line"] <= b), None)
        (covered if hit else uncovered).append({**site, "covered_by": hit})
    return covered, uncovered


def summarize(required, covered, uncovered):
    by_class = {}
    for s in required:
        by_class.setdefault(s["klass"], {"total": 0, "covered": 0})
        by_class[s["klass"]]["total"] += 1
    for s in covered:
        by_class[s["klass"]]["covered"] += 1
    return by_class


def build(lines=None):
    lines = R.subject_lines() if lines is None else lines
    required = enumerate_sites(lines)
    covered, uncovered = coverage(required)
    payload = {
        "schema": SCHEMA,
        "status": "PROPOSAL_FOR_INDEPENDENT_REVIEW",
        "status_note": (
            "Derived mechanically from the subject; NOT curated and NOT certified. The class "
            "matchers are stated proxies (a `continue` that skips a malformed row is not a "
            "semantic filter, and this module cannot tell the difference). Whoever curates this "
            "must not be its author."),
        "subject": {"path": R.SUBJECT_PATH, "sha256": R.SUBJECT_SHA256},
        "derivation": {
            "generator": "every `fn` definition",
            "score_term": "every `Candidate{` construction",
            "filter": "every `.filter(` / `.retain(` / `continue`",
            "early_return": "every `return`",
            "arbitration": "every `.max_by` / `.min_by` / `.sort`",
            "noncode_stripped": "string literals and // comments removed before matching",
        },
        "totals": summarize(required, covered, uncovered),
        "required_count": len(required),
        "covered_count": len(covered),
        "uncovered_count": len(uncovered),
        "uncovered": sorted(uncovered, key=lambda s: s["line"]),
        "required": sorted(required, key=lambda s: (s["line"], s["derived_id"])),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["inventory_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return payload


# --------------------------------------------------------------------------------------


def _self_test():
    """The inventory's own claims, each demonstrated failing before being trusted."""
    lines = R.subject_lines()
    cases = []

    def case(label, passed, detail=""):
        cases.append((label, passed, detail))

    required = enumerate_sites(lines)
    case("enumerates a non-trivial site set", len(required) > 100, f"{len(required)} sites")

    # INDEPENDENCE: the enumeration must not change when SITES changes. This is the property
    # the review actually asked for, so it is tested rather than asserted.
    original = R.SITES
    R.SITES = original[:3]
    try:
        shrunk = enumerate_sites(lines)
    finally:
        R.SITES = original
    case("enumeration is INDEPENDENT of registry.SITES",
         [s["derived_id"] for s in shrunk] == [s["derived_id"] for s in required],
         "identical with SITES cut to 3")

    # coverage must MOVE when the registry shrinks — otherwise it measures nothing
    cov_full, unc_full = coverage(required)
    R.SITES = original[:3]
    try:
        cov_small, unc_small = coverage(required)
    finally:
        R.SITES = original
    case("coverage falls when the registry shrinks",
         len(cov_small) < len(cov_full),
         f"{len(cov_full)} -> {len(cov_small)} covered")

    # comments and strings must not mint sites
    synth = ['fn f(){', '    // return continue Candidate{', '    let s="return continue";', '}']
    got = [s["klass"] for s in enumerate_sites(synth)]
    case("a comment/string cannot invent a site", got == ["GEN"], f"classes={got}")

    # a real construct IS found (the control proving the check above is not vacuous)
    synth2 = ['fn f(){', '    return 1;', '}']
    got2 = sorted(s["klass"] for s in enumerate_sites(synth2))
    case("a real early return IS enumerated", got2 == ["EARLYRET", "GEN"], f"classes={got2}")

    # every enumerated site sits inside the function it names
    bad = [s for s in required if s["klass"] != "GEN"
           and not (s["fn_start"] <= s["line"] <= s["fn_end"])]
    case("every site lies inside its enclosing function", not bad, f"{len(bad)} stray")

    # digests are stable across rebuilds
    case("inventory digest is deterministic",
         build(lines)["inventory_sha256"] == build(lines)["inventory_sha256"])

    allok = True
    for label, passed, detail in cases:
        print(f"  {'OK  ' if passed else 'BAD '} {label:52} {detail}")
        allok = allok and passed
    print(f"\nself-test: {len(cases)} cases —",
          "PASS" if allok else "FAIL — a claim of this module is untrue")
    return 0 if allok else 1


def _report():
    inv = build()
    print(f"subject {inv['subject']['sha256'][:16]}…  schema {inv['schema']}")
    print(f"\n§5.4 required sites enumerated FROM THE SOURCE: {inv['required_count']}")
    print(f"named by the current registry: {inv['covered_count']}  "
          f"({100*inv['covered_count']//max(1,inv['required_count'])}%)  "
          f"unnamed: {inv['uncovered_count']}\n")
    print(f"  {'class':<12}{'required':>9}{'named':>8}{'unnamed':>9}")
    for k, v in sorted(inv["totals"].items()):
        print(f"  {k:<12}{v['total']:>9}{v['covered']:>8}{v['total']-v['covered']:>9}")
    print("\nFunctions holding UNNAMED sites (the registry does not mention them at all):")
    fns = {}
    for s in inv["uncovered"]:
        fns.setdefault(s["fn"], []).append(s["klass"])
    for fn, ks in sorted(fns.items(), key=lambda kv: -len(kv[1]))[:18]:
        counts = {k: ks.count(k) for k in sorted(set(ks))}
        print(f"  {fn:<38}{len(ks):>4}  {counts}")
    print(f"\n  … {len(fns)} functions total hold unnamed sites")
    print("\nWHAT THIS DOES NOT SHOW: whether a NAMED site carries the correct stage or intent.")
    print("Coverage measures naming, not semantics. That gap is open and is not closed here.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--freeze", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if args.report:
        return _report()
    if args.freeze:
        inv = build()
        path = os.path.join(R.REPO, INVENTORY_PATH)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(inv, fh, indent=1, sort_keys=True)
            fh.write("\n")
        print(f"wrote {INVENTORY_PATH}: {inv['required_count']} required sites, "
              f"{inv['uncovered_count']} unnamed; inventory_sha256 = {inv['inventory_sha256']}")
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
