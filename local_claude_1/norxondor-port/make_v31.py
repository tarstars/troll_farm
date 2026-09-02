#!/usr/bin/env python3
"""v3.1 of the norxondor port = v3's readable with its three stale tests brought to the cap.

The play code is untouched: the three replacements below live entirely inside the
`#[cfg(test)] mod port_tests` block, so the `-O` binary is v3's. The one variable of the
card's refinement loop stays `PRODUCE_ROSTER_CAP = 3`.

Why: claude_1's 13:25Z blocker — `rustc --test` on v3 read 12 passed, 3 failed, and all
three failures were v2's specification ("a roster of three stays in Produce") asserted by the
test module. A build whose tests contradict its code is not a build of record, so the tests
follow the cap.

Usage:  python3 make_v31.py readable/norxondor-port-v3.rs readable/norxondor-port-v3.1.rs
Every replacement must match exactly once, or the script refuses to write.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPLACEMENTS: list[tuple[str, str, str]] = [
    (
        "test 1: the third troll ends Produce whatever train_now says",
        """            #[test]
            fn roster_three_turn_106_stays_produce() {
                let view = test_view(3, 106, true);
                let mut bot = bot();
                bot.update_mode(&view, false);
                assert_eq!(bot.mode, EconomyMode::Produce);
            }
""",
        """            #[test]
            fn roster_three_turn_106_switches_deforest() {
                // v3: PRODUCE_ROSTER_CAP is 3, so a roster of three ends Produce on
                // the next update whatever the turn or the train signal says
                // (v2 kept a roster of three in Produce here until turn 144).
                let view = test_view(3, 106, true);
                let mut bot = bot();
                bot.update_mode(&view, true);
                assert_eq!(bot.mode, EconomyMode::Deforest);
            }
""",
    ),
    (
        "test 2: the projection is exercised at roster 2, where the cap does not decide",
        """            fn missing_source_is_hopeless_but_iron_free_is_omitted() {
                let mut iron_free = test_view(3, 106, false);
""",
        """            fn missing_source_is_hopeless_but_iron_free_is_omitted() {
                // v3: at roster 3 the cap decides the mode, so the projection's two
                // rules are exercised at roster 2 (v2 used roster 3 here).
                let mut iron_free = test_view(2, 106, false);
""",
    ),
    (
        "test 3: only the roster-2 deadline is reachable under the cap",
        """                for (roster, deadline) in [(2, 129), (3, 144), (4, 154)] {
""",
        """                // v3: with PRODUCE_ROSTER_CAP at 3, switch_deadline's entries for
                // rosters 3 and 4 (turns 144 and 154) can never fire — the cap is
                // tested first in the same condition — so only the roster-2 deadline
                // remains reachable. The entries stay in the table, inert.
                for (roster, deadline) in [(2, 129)] {
""",
    ),
]


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    source = Path(sys.argv[1]).read_text(encoding="utf-8")
    result = source
    for name, old, new in REPLACEMENTS:
        count = result.count(old)
        if count != 1:
            print(f"refusing: {name}: expected exactly one match, found {count}", file=sys.stderr)
            return 1
        result = result.replace(old, new)
    Path(sys.argv[2]).write_text(result, encoding="utf-8")
    print(f"wrote {sys.argv[2]}: {len(REPLACEMENTS)} replacements, {len(source)} -> {len(result)} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
