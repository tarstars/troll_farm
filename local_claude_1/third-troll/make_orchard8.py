#!/usr/bin/env python3
"""Build "orchard 8": orchard 6 plus ONE of orchard 7's three fixes -- the deadline never abandons
the opening (owner 2026-09-02 18:0xZ: "extend" on the stalled orchard rows; the coordinator's
recommendation of 08-29: orchard 6, which read 18.8 above the champion's 18.2, with the never-abandon
rule that cured orchard 6's lone-troll games (10 of 160 -> 1 of 160 in orchard 7), and WITHOUT
orchard 7's other two changes -- the 2 + 2 fruit reserve before planting and the orchard cells
within reach of the tent -- one of which cost more than the fix gained (orchard 7 read 16.7 / 16.6).

THE EDIT: orchard 6's forty-four replacements followed by one more (orchard 7's REPL_NO_ABANDON,
imported verbatim so the rule is byte for byte orchard 7's).

    python3 local_claude_1/third-troll/make_orchard8.py
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
import make_orchard4 as mo4         # noqa: E402
import make_orchard5 as mo5         # noqa: E402
import make_orchard6 as mo6         # noqa: E402
import make_orchard7 as mo7         # noqa: E402

ORCHARD8 = (mo7.REPL_NO_ABANDON,)


def main() -> int:
    mk.configure_spec("2303")
    mk.REPLACEMENTS = (tuple(mk.REPLACEMENTS) + th.EXTRA + mo.ORCHARD + mo2.ORCHARD2 + mo3.ORCHARD3
                       + mo4.ORCHARD4 + mo5.ORCHARD5 + mo6.ORCHARD6 + ORCHARD8)
    mk.STACKED = True
    mk.ARM = HERE / "champion-orchard8-v6-instrument.rs"
    mk.READABLE_EDITED = HERE / "orchard8-readable.rs"
    mk.SUBMISSION = mk.REPO / "cgauto" / "submissions" / "candidate-orchard8-v6-instrument.rs"
    mk.REPORT = mk.REPO / "readable" / "reports" / "candidate-orchard8-v6-instrument.round-trip.json"
    mk.DIFF = mk.REPO / "readable" / "diffs" / "orchard8.diff"
    for n in ("third-troll", "third-troll-2202", "three-heroes", "orchard", "orchard2", "orchard3",
              "orchard4", "orchard5", "orchard6", "orchard7"):
        mk.OTHERS_LIST.append((n, mk.REPO / "cgauto" / "submissions" / f"candidate-{n}-v6-instrument.rs"))
    rc = mk.main()
    if rc == 0:
        report = json.loads(mk.REPORT.read_text())
        report["task"] = "orchard 8 (the third troll card, extended 2026-09-02: orchard 6 + never abandon the opening, nothing else)"
        report["bot"] = "orchard 6; the deadline keeps waiting for the fallback troll instead of abandoning the opening (orchard 7's first fix alone)"
        report["edit"]["what"] = "forty-five replacements: orchard 6's forty-four + orchard 7's never-abandon rule"
        for path in (mk.REPORT, HERE / "results" / "build-orchard8.json"):
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
