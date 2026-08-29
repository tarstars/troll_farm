#!/usr/bin/env python3
"""Build "orchard 4": orchard 3 with the concurrent-picking rule softened (2026-08-28 ~10:5xZ).
The smoke of orchard 3 showed a starter camping 25 turns on an immature lemon tree because the
rule LOCKED it to lemons while plums and iron went unworked. Now the assigned resource is a
preference: every missing item's sources are scored by the turns to get them, and the troll's
own resource gets a head start of ASSIGNED_BONUS turns -- it switches when another missing
resource is clearly quicker (an immature tree loses to a plum tree in fruit or to the ore).

THE EDIT: orchard 3's thirty-three replacements followed by two more (the two score lines of
`early_candidates` carry the bonus; the exclusivity is gone).

    python3 local_claude_1/third-troll/make_orchard4.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_third_troll as mk       # noqa: E402
import make_three_heroes as th      # noqa: E402
import make_orchard as mo           # noqa: E402
import make_orchard2 as mo2         # noqa: E402
import make_orchard3 as mo3         # noqa: E402

REPL_PREFER = dict(
    name="early_candidates: the assigned resource is a preference (a head start), not a lock",
    anchor=(
        "                let mine: Vec<usize> = if missing.len() > 1 && own.len() > 1 {\n"
        "                    vec![missing[rank % missing.len()]]\n"
        "                } else {\n"
        "                    missing.clone()\n"
        "                };\n"
        "                for item in [PLUM, LEMON, APPLE, IRON] {\n"
        "                    if !mine.contains(&item) {\n"
        "                        continue;\n"
        "                    }\n"
    ),
    text=(
        "                let mine: Vec<usize> = if missing.len() > 1 && own.len() > 1 {\n"
        "                    vec![missing[rank % missing.len()]]\n"
        "                } else {\n"
        "                    missing.clone()\n"
        "                };\n"
        "                // A head start for the troll's own resource, not a lock: it switches when\n"
        "                // another missing resource is clearly quicker (orchard 4, 2026-08-28).\n"
        "                const ASSIGNED_BONUS: f64 = 8.0;\n"
        "                for item in [PLUM, LEMON, APPLE, IRON] {\n"
        "                    if !missing.contains(&item) {\n"
        "                        continue;\n"
        "                    }\n"
        "                    let bonus = if mine.contains(&item) { ASSIGNED_BONUS } else { 0.0 };\n"
    ),
)

REPL_SCORES = dict(
    name="early_candidates: the bonus on the two score lines",
    anchor=(
        "                    if item == IRON {\n"
        "                        out.extend(Self::iron_candidates(view, unit, 6_100.0));\n"
    ),
    text=(
        "                    if item == IRON {\n"
        "                        out.extend(Self::iron_candidates(view, unit, 6_100.0 + bonus));\n"
    ),
)

REPL_SCORES2 = dict(
    name="early_candidates: the bonus on the fruit score line",
    anchor="                        out.extend(Self::fruit_candidates(view, unit, kind, 6_000.0));\n",
    text="                        out.extend(Self::fruit_candidates(view, unit, kind, 6_000.0 + bonus));\n",
)

ORCHARD4 = (REPL_PREFER, REPL_SCORES, REPL_SCORES2)


def main() -> int:
    mk.configure_spec("2303")
    mk.REPLACEMENTS = (tuple(mk.REPLACEMENTS) + th.EXTRA + mo.ORCHARD + mo2.ORCHARD2 + mo3.ORCHARD3
                       + ORCHARD4)
    mk.STACKED = True
    mk.ARM = HERE / "champion-orchard4-v6-instrument.rs"
    mk.READABLE_EDITED = HERE / "orchard4-readable.rs"
    mk.SUBMISSION = mk.REPO / "cgauto" / "submissions" / "candidate-orchard4-v6-instrument.rs"
    mk.REPORT = mk.REPO / "readable" / "reports" / "candidate-orchard4-v6-instrument.round-trip.json"
    mk.DIFF = mk.REPO / "readable" / "diffs" / "orchard4.diff"
    for label, name in (("the third troll (a) 2/3/0/3", "candidate-third-troll-v6-instrument.rs"),
                        ("the third troll variant (b) 2/2/0/2", "candidate-third-troll-2202-v6-instrument.rs"),
                        ("three heroes", "candidate-three-heroes-v6-instrument.rs"),
                        ("the orchard", "candidate-orchard-v6-instrument.rs"),
                        ("orchard 2", "candidate-orchard2-v6-instrument.rs"),
                        ("orchard 3", "candidate-orchard3-v6-instrument.rs")):
        mk.OTHERS_LIST.append((label, mk.REPO / "cgauto" / "submissions" / name))
    rc = mk.main()
    if rc == 0:
        report = json.loads(mk.REPORT.read_text())
        report["task"] = "orchard 4 (the third troll card: orchard 3 with the assigned resource as a preference, not a lock)"
        report["bot"] = "orchard 3; each troll prefers its resource of the bill by a head start of 8 turns and switches when another is quicker"
        report["edit"]["what"] = "thirty-six replacements: orchard 3's thirty-three + orchard 4's three"
        for path in (mk.REPORT, HERE / "results" / "build-orchard4.json"):
            path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        stray = HERE / "results" / "build-v6.json"
        if stray.exists():
            stray.unlink()
    return rc


if __name__ == "__main__":
    try:
        sys.exit(main())
    except mk.BuildError as exc:
        print(f"BUILD REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
