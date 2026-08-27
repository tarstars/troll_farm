# Review — `cut_fixtures.py` and the first bot-hash-tagged libraries (task `20260826-fresh-fixture-dataset`, board row 0-3)

Reviewer: `claude_1` (the one reviewer the charter names). Reviewed handoff:
`coordination/messages/codex_1/20260827T033133Z-20260826-fresh-fixture-dataset-handoff.md`,
artifact commit `c0a4074dec04090c943738e2fc60c37c31abed9c`.

## Verdict: **ACCEPT-WITH-EDIT**

The generator is sound, deterministic and honest about what it does not know. I reproduced
both libraries **byte-identically** from the pinned manifest and the slice, and I verified
the one thing the code cannot check for itself — the replay-derived seat. The edits are all
**labelling and counting**: no number codex_1 published is wrong, but three of them read as
something stronger than they are, and one of the two libraries is a four-game sample.

## What I ran (independent, on the host)

```text
python3 scripts/cut_fixtures.py --manifest <slice manifest> \
    --games-dir /home/tarstars/prj/troll_farm-codex_1/data/raw/slice/games \
    --bot-hash 72673124 --output /tmp/rev/champ.json      -> errors [], counts as published
    --bot-hash 04e3db43 --output /tmp/rev/keep.json       -> errors [], counts as published

sha256 champion library  58e9a99b030df4954d4529aa1149310f12c84894a293afc2bc6893d23bdd6e61  (mine == codex_1's)
sha256 keep-rule library 3fea48c8efbf09940395f96d919f0075fab5bd088621460f5234c93b63832358  (mine == codex_1's)
```

- The manifest I used hashes `dacd2e6e…`, which is exactly the `source_manifest_sha256`
  recorded inside both libraries. Same input, same output, byte for byte.
- All 212 manifest entries: file present, `file_sha256` matches. 0 missing, 0 mismatched.
- Telemetry decoded: champion arm **56,288 v6 rows over 208 games**, turn counts 102–300 and
  contiguous from 1 in every game; keep arm **1,200 rows over 4 games**, 300 turns each.

## The seat, checked independently (the charter asked for this one)

For every one of the 212 games I counted v6 fragments per `agentId` and compared with the
manifest's `our_seat`: **v6 rows appear at the manifest seat in 212 of 212 games, and at no
other seat in any game; 0 games have zero rows at the manifest seat.** Seat handling is
correct on this slice.

This matters more than it looks, because of a latent hole (F5 below): a wrong seat would
produce *no error and no fixture*, so a silent seat bug would have looked exactly like a
quiet library. It did not happen here; I checked rather than assumed.

## Findings

**F1 — two classes cannot fire on the champion arm at all, and the library says only that
they were "not observed".** `ka` and `xc` are counters of the *keep* machinery. On the
champion arm `k=` is `0` on **all 110,784 unit-rows**, and `max ka = 0`, `max xc = 0` across
all 56,288 rows: no goal is ever kept, so `long_kept_goal` (`ka>30`) and the `xc` half of
`dance` are **structurally inert** on that arm, not merely unobserved. The library's absence
reason — "not observed in the selected hash-pinned replay slice" — invites the reader to
think a bigger slice would find some. It would not. This is the same category as the
turn-100 shack-engine class, which codex_1 labelled correctly as *unavailable*, and it is
the failure mode already on our record: a guard pointed at a verb the arm never utters never
fires at all.

**F2 — `wc` is zero everywhere, so the `dance` detector has never been shown to fire on real
data.** Across both arms, 57,488 rows, `max wc = 0`. `dance` fires only in the unit test, on
a synthetic row. "dance: 0" is therefore not yet evidence about dancing; it is a detector
with no positive control on real input.

**F3 — `blocked_troll` counts turns, not events, while `parked_troll` counts runs.** The 139
champion blocked windows are **45 maximal per-unit runs over 29 games** (run lengths: 18×1,
6×2, 3×3, 2×4, 4×5, 12×6); the keep arm's 8 are **4 runs over 2 games**. With `radius=3`,
two adjacent turn-windows share 6 of their 7 rows, so the library also stores the same
telemetry many times over. The report's caveat ("event-window count, not independent-game
prevalence") is true but does not say this; it says the *parked* detector coalesces runs,
which invites the reader to assume blocked does too. Either coalesce blocked runs the way
parked and stall are coalesced, or publish both numbers (45 runs / 139 turn-windows).

**F4 — the keep-rule library is a four-game sample.** The id-ascending slice contains 208
champion games and **4** keep-rule games. Its `parked_troll: 0` and `long_kept_goal: 0` carry
almost no information (its observed `max ka` is 20 against a `>30` threshold). The
coordinator explicitly offered a second, disjoint slice by the same rule; the keep-rule side
of this library should not be read as evidence until that lands.

**F5 — a game with no telemetry is silently a pass.** `replay_rows` enforces "turns
contiguous from 1", but an empty row list satisfies that vacuously, so a game decoded at the
wrong seat, or one whose bot never printed, yields no error and no fixture. `errors: []` then
means "nothing broke", not "everything was read". Add a census to the library — games
matched, games decoded, games with zero telemetry rows, rows total — so the denominator is
visible next to the counts. (0 such games in this slice; I checked.)

**F6 — `stall` is a strict superset of `parked_troll`.** Any run ≥ 60 emits both, so the
class counts are not a partition and cannot be summed. Moot at 0 here; say it in the report
before it is not moot.

**F7 (minor) — `grade` cannot detect an edited library.** It recomputes counts from the
fixtures it is handed, so a hand-edited library grades PASS. It does not re-check
`source_manifest_sha256`, nor that a fixture's rows actually span its `event_window`. Cheap
to add; worth it for an artifact whose whole claim is reproducibility.

## The charter's questions, answered

- **Deterministic manifest/hash checks** — correct and effective. Every replay is hashed
  against the manifest before decoding; a mismatch becomes a recorded error, not a silent
  skip. Reproduced byte-identically off the same manifest hash.
- **Replay-derived seat handling** — correct on this slice, verified independently
  (212/212), with the latent hole F5 named.
- **Detector definitions** — `parked_troll`/`stall` are well posed and coalesced;
  `blocked_troll` is per-turn (F3); `dance` and `long_kept_goal` are inert on the arm that
  supplies 98% of the data (F1, F2).
- **Regeneration rule** — good, and the right principle: libraries are records, never gates.
  The regenerate line in the JSON names the exact command.
- **Zero-class reporting** — present for every class, which is the part I most wanted to see;
  the wording needs F1's distinction between *unobserved* and *inapplicable*.
- **Is the grading mode sufficient for a harness to consume the library?** For integrity,
  yes. For consumption, one gap: fixtures carry raw v6 strings, so any consumer must
  re-implement the decoder or import `cut_fixtures.decode`. Say which, in the report or the
  JSON's `regenerate` note, so the second consumer does not write a third decoder.

## Requested edits (none change a published number)

1. Re-label `long_kept_goal` (and the `xc` half of `dance`) on the champion arm as
   *inapplicable to this arm*, alongside the existing *unavailable* and *unobserved* reasons.
2. Publish blocked as **45 runs / 139 turn-windows**, or coalesce it like parked.
3. State the `stall` ⊃ `parked_troll` overlap.
4. Mark the keep-rule library as a 4-game sample and hold it until the second slice.
5. Add the decode census (matched / decoded / zero-telemetry / rows).
6. Optional: have `grade` re-verify `source_manifest_sha256` and window coverage.

Edits 1–5 are report-and-JSON text plus one counter; edit 2 is the only one that touches the
generator, and it is a call codex_1 may reasonably decline by publishing both numbers instead.
