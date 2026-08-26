---
schema_version: 2
type: handoff
task_id: 20260825-dance-cure-candidate-1-hold
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260825T115600Z-20260825-dance-cure-candidate-1-hold-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 22d6b2bb2418eece82d67d154c33441bbd655519
artifact_paths: ["claude_1/cure1/g2-grade-2026-08-25.md", "claude_1/cure1/g2_grade.py", "claude_1/cure1/g2_controls.py", "claude_1/cure1/results/g2-grade.json", "claude_1/cure1/results/g2-controls.json", "claude_1/narrate4/narrate4_join.py", "claude_1/cure1/regressive_baseline.py"]
created_utc: 2026-08-25T11:56:00Z
---

- To: local_claude_1 (disposition), codex_1 (the assigned execution check)
- CC: user, chatgpt_1
- Task: 20260825-dance-cure-candidate-1-hold
- Requires acknowledgement: yes — this is the G-2 grade; codex_1's card unblocks on it

# G-2 GRADE — Candidate 1 **FAILS** both acceptance clauses; **no kill rule fired**; the hold fires 253 times in 102 games and in **none** of the 25 D-1 windows

`agent/claude_1@22d6b2bb`, seven paths, all present at that commit. Full report:
`claude_1/cure1/g2-grade-2026-08-25.md`.

| clause | measured | bar | result |
|---|---|---|---|
| **(a)** F7 `DANCER_PROGRESS` share | **11 of 25 = 44.00 %** | ≥ 65.00 % (the v3 instrument's 52 of 80) | **FAIL** |
| **(b)** `R_pos` per 1,000 own troll-turns | **4.3122** (357 / 82,789) | ≤ **3.8386** | **FAIL** (43.83 % reduction; 50 % required) |
| kill: idle-with-work (`H`+`W`) | 0.4360 % | > 1.5 % | PASS |
| kill: D-3 own-troll contention | 0 | > 0 | PASS |
| kill: long-stall share | **0.0000 %** vs the champion's **1.3072 %** | above the champion's | PASS |
| kill: P1/P2 row migrating to a parked/stalled shape | — | — | **NOT MEASURABLE ON A READ** |

**The arm is not dangerous. It is too small, and the read says exactly why.**

## The finding, which is worth more than the verdict

Of the **25** D-1 episodes, the dancer's own `r=` over the window is `REGRESSIVE_NO_HOLD` on
**24** and `NEITHER` on 1. **`HOLD_SEEN` is 0.** The rule fired 253 times in 230 runs across 102
of 160 games — and inside not one dance the detector recorded. That is why clause (a) fails: F7
asks how the dance ended and the rule was not in it. `TRANSIENT_ONLY` scopes the hold to
transient blocks and the real D-1 dances are not transient — the same fact G-1 found from the
other side (98 % of the as-built holds were against permanent blockers), now confirmed in the
wild on the revised arm. **The cure and the disease do not overlap.**

## The crosswalk I declared owed and refused to fake — delivered, and it clears the instrument

Over all 82,789 own troll-turns: **both 339**, `R_pos`-only **18**, `r=R`-only **0**, neither
79,430, plus 2 `r=R` rows `R_pos` cannot score. Agreement **94.96 %** on the union, and control
**K-X** shows **18 of 18** disagreeing rows sit **off the BFS map**, where the arm's own Manhattan
fallback decides — **0 unexplained**. On every row where the BFS map decides, the two labels
agree exactly. Published as a finding about the instrument; folded into no gate. Clause (b) is
still graded `R_pos` on **both** sides, with `r=R` (341 turns, 4.1189 per 1,000) beside it under
its own name.

## Scope, measured on this read

**146 of 160 games (91.25 %)** scope-active, computed from the read's own games by the arm's own
orchard-eligibility predicate. The panel's 228/240 does **not** transfer and is not quoted.
Control **K-S**: **0** `r=H` turns in the 14 scope-inactive games, where the hold is inert for the
whole game by construction.

## Controls, each with its number

K-D decode **PASS** (82,789 rows, 0 refusals, 0 opponent `NARRATE`, longest line 136/2,000) ·
K-E exhaustiveness **PASS** (42,354 + 3 + 357 = 42,714) · K-F manhattan fallback **FIRES** (320
rows; 18 of the 357 depend on it, 339 without — both published, graded figure stays the
arm-faithful 357) · K-P poison target **PASS** (×57.97) · K-S scope inertness **PASS** ·
K-B baseline byte-identity **PASS** (the v3 baseline JSON re-derived byte-identical after the
one-keyword refactor, so the *same function object* graded both sides) · K-DET determinism
**PASS** · K-IND independent census **PASS** (a regex over raw frame stdout — no adapter, no
trace, no join — reproduces H 253 · L 245 · P 42,136 · R 341 · W 108 · N 39,706 exactly) ·
K-CH champion long-stall **PASS** (the identical function on 306 champion games: 4 games,
1.3072 %) · K-V invariants: `pz` max **2**, stale protections **0**, W-collisions **0**.

## What I did not measure, stated as such

- The **fourth kill rule has no population on a read** — P1/P2 are panel gates over a
  candidate/parent pair. Recorded NOT MEASURABLE, never PASS. Read-side evidence beside it, as
  evidence and not as a substitute: longest hold `b` = **2** (the bound held in the wild), 0
  long-stall games, 0 D-3.
- **Long-stall is a proxy** for P4, built from P4's own imported arithmetic (window 60,
  live-horizon trimming) but run on replays, which do not know the final turn's outcome. Both
  corpora measured with the identical function.
- **Clause (a) is underpowered, and I am not using that to soften the FAIL.** 11/25 has a 95 %
  Clopper–Pearson interval of **[24.40 %, 65.07 %]** — which *contains* the 65.00 % bar — and
  Fisher's exact against 52/80 gives **p = 0.1003**. The bar was pre-committed and the read is
  under it, so the clause fails; what the read cannot do is *distinguish* 44 % from 65 %. Both
  facts stand, neither cancels the other.
- **D-1 off replays is an upper bound** (reconstructed plant clocks; the error direction invents
  dancing) — for the 25 here and the v3 read's 34 alike.
- The two reads are **different arms, different days, different opponent fields, no
  randomisation.** The charter fixed the v3 read as clause (b)'s comparator and I graded what the
  charter fixed; I do not claim the gap is the rule's alone.

## The two figures the charter asked for beside the clauses

**D-1 down and not by silence**: 34 in 160 v3 games (0.7852 per 1,000 game turns) → **25 in 160
G-2 games (0.5942)**, in 24 games, with 0 decode and 0 adapter refusals. **D-2 0, D-3 0.**
Classes (r3): `BLOCKED_BY_WORKING_TEAMMATE` 15, `UNCLASSIFIED` 5, `FIXED_TARGET_NO_BLOCKER` 4,
`SWAP_FLAP` 1. F7: 11 / 8 / 5 / 1.

## Disposition — not mine

G-2 fails, so by the coordinator's own policy **G-3 does not start**. Whether Candidate 1 is
revised, parked or retired, and whether the reserved second Arena action goes elsewhere, is
`local_claude_1`'s call with the owner. I make **no recommendation** and propose myself as builder
for nothing. codex_1: the assigned fresh-archive execution check and package-identity
verification are now unblocked — `python3 claude_1/cure1/g2_grade.py` then
`python3 claude_1/cure1/g2_controls.py --champion-games … --champion-manifest …`, both
deterministic and byte-reproducible from `22d6b2bb`.

Deferrals: none. Resident SHA-256 unchanged at `fff6669b…`.
