# claude_1 status — wake #29, 2026-08-21

Task `20260821-swap-r1-cure`: **G-0 rev 2 ACCEPTED by codex_1, α BUILT, G-1 BLOCKED by its own
re-swap gate.** Package `claude_1/swap1/g1-package-2026-08-21.md`, handoff `20260821T103200Z`
(requires_ack). Five G-1 gates pass — probe parity, shadow inertness on 6,800 ticks, whole-game
identity on the 18 zero-fire fixtures, pre-first-fire identity everywhere, and a non-zero trigger
count. The sixth, ruling 4's re-swap detector, **fails at 111**: OSC-006 trades the pair {0,2} on
27 consecutive ticks, OSC-011 on 6. I did not invent a cooldown; three remedies are named, a
progress conjunct is recommended, and the ruling is codex_1's. **DEFERRED card in force:** G-1
rev 2 then G-2..G-4.

Secondary, and it bounds G-2: **OSC-027 never fires** (its recorded stall does not reproduce under
the base — the re-run problem measured at wake #27), and the card's "back on the tree within 2
ticks" is **untested**, because all 27 work-displacing fires sit inside OSC-006's dance.

---

# claude_1 status — wake #26, 2026-08-21

Task `20260821-osc032-033-cause-attribution`: **CLOSED — all three gates ACCEPTED.** codex_1
returned **G-3 ACCEPTED** this wake (`20260821T090757Z`), reproduced from a detached worktree at
`e8034b79`, all three generated JSON artifacts byte-identical to the pin. Their `ack_for` names my
G-3 handoff exactly, which retires my r3 card; they declared **no deferrals and no replacement
card**. Queue drained: 1 new, 0 ack-required, no card of mine outstanding.

Task `20260815-oscillation-deep-dive`: the one item I carried open from wake #25 is now
**dispositioned and published** (`20260821T091400Z`, commit `3a690980`).

## What arrived

One message, not ack-required, read in full:

- **codex_1 `20260821T090757Z` — G-3 ACCEPTED.** The amended questions are answered and the
  controls bite. They record, explicitly, that the accepted scope is **measurement only**: it does
  not decide bug versus correct caution, does not explain OSC-032's unbanked reachable plum, and
  authorizes no fix, no candidate, no class-wide claim and no Arena action. Their review is
  `codex_1/reviews/osc032-033-cause-attribution-g3-review-2026-08-21.md`. One thing to carry: they
  state the opponent-independent grace-only bound as **at most 5/110 and 0/143** real window
  turns; my note states the same bound as 105/110 and 143/143 turns *excluded*. Same measurement,
  complementary phrasing — 110 − 5 = 105. No discrepancy.

## The carried-open item, closed by DETECTION rather than a source fix

`build_oscillation_library.py:808` defaults `--out` to the **STALE** parent-lineage tree.

**I did not change the default, and that is the substantive decision.** The file's SHA-256
`4b9fce4c…` is pinned in the artifact tables of `oscillation-library-2026-08-10.md` and
`oscillation-library-subject-correction-2026-08-11.md`, and the **authoritative**
`oscillation-library-98628e98/` tree rests its provenance on that builder being *unmodified*
(`oscillation-library-98628e98/README.md:28`; `build_subject_library.py` imports it and reuses
`harvest`/`dedupe`/`write_library` verbatim). Making `--out` required would falsify an attestation
two already-accepted artifacts depend on — a worse defect than the hazard. Builder verified
byte-identical to the pin after this wake's work.

**The hazard, measured.** Both other arguments are `required=True`, so a bare invocation is
impossible; the trap needs `--games`/`--panel-config` supplied and `--out` omitted. `write_library`
unlinks `*.json` **only**, so README.md *survives* the overwrite and is left describing 33 cases
that are gone — a false document at the exact path the marker exists to protect.

**Detection was already two-thirds built.** `TestParentLineageIsLabelled` already pinned
`library_sha256` to `5858d351…` and asserted the index's `WRONG SUBJECT` note (which a rebuild
drops, since `write_library` never writes that field). Neither covers the README. I added
`test_the_stale_readme_still_describes_the_tree_it_sits_in`, which ties the README's ID-map rows to
the `OSC-*.json` files actually present.

**Three controls executed against throwaway `tempfile` copies — the real tree was never written:**

| control | expected | observed |
|---|---|---|
| untouched copy | all 4 pass | all 4 pass, hash matches pin, 33 cases |
| default-run overwrite (5 cases) | tree tests **and** README test fire | all 3 fire: `8bd2a0f4…` ≠ pin, `subject_note` KeyError, ID map 5 ≠ 33 |
| README deleted, tree intact | **only** the new test fires | exactly the new test fires |

The third is the one that earns the test: it proves the new leg is not redundant with the two that
already existed. Full suite **95 tests OK, 2 skipped** (opt-in `rustc` replay); the two
`INTEGRITY FAILURE` lines in that output are fail-closed tests passing.

**Scope, stated honestly.** This is containment, not prevention. The overwrite remains possible;
it can no longer happen quietly. The stale README now carries the trap and the reason the default
was not fixed, at its head.

## Standing limits that survive this wake

- G-3's accepted scope is **measurement only**. Bug versus correct caution is the owner's ruling,
  not mine and not codex_1's.
- The eleven unobserved plant-rejection clauses, and OSC-032's 52 turns where H-C's generator was
  never entered, remain UNOBSERVED — not refuted.
- OSC-032's unbanked reachable plum is **not measured and not claimed**.
- `items_the_shack_never_held_enough_of` and `items_no_live_source_ever_existed_for` stay strictly
  apart; collapsing them overstates H-A.

## Open

Nothing. No card outstanding, none deferred, none requested. Queue drained and pushed.
