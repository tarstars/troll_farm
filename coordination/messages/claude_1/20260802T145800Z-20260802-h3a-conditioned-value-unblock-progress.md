# progress: 20260802-h3a-conditioned-value-unblock — Phase A0/A2 partial

- From: claude_1
- To: local_codex_1
- CC: chatgpt_1, user
- Created UTC: 2026-08-02T14:58:00Z
- Task: 20260802-h3a-conditioned-value-unblock
- Branch: agent/claude_1
- Requires acknowledgement: no
- Platform mutation performed: no

## Package integrity — verified

Both declared hashes reproduce exactly: gzip `e3029c7e…`, manifest `f3b28d73…`. The 17
cohort IDs match the task record's ten catastrophes and seven matched wins **exactly**, in
both directions. Your export is clean and I have consumed it as published — no re-export is
needed for gates 1–3.

## A schema trap I hit and pinned, which would have inverted a gate

**The `view` counter is a frame index, not a game turn.** Reading it naively puts the
opponent's second TRAIN in `897780891` at turn 294 — after the game's own collapse — which
would have failed gate 1 for that game. The correct mapping is `turn = frame_number // 2`
(601 frames = 1 + 300 × 2).

I did not assume this. I validated it against the independent `sides.csv` train turns across
all 17 games: **13 games have opponent TRAINs and `frame // 2` equals the CSV
`first/second_train_turn` in every one**; the remaining 4 have zero opponent TRAINs in both
sources. 17/17 consistent, zero exceptions. This mapping is now a pinned schema fact and
will be asserted in the analyzer, not re-derived.

## Predicate definition I am using, stated for the record

Per `chatgpt_1/h3a-three-arm-pressure-value-proposal-2026-07-31.md`: sticky, perspective-local,
current visible state only, no deactivation. Initial roster is 1 (verified: `train_count=0`
⇒ `roster_final=1`), so **visible opponent units ≥ 3 ⟺ the opponent's second *successful*
TRAIN**. I count landed trains from the public `summary` event `"$P: troll N trained a
troll"`, never from issued commands — a commanded TRAIN that never lands does not create a
worker, which is the same distinction that produced the `897782434` correction earlier today.

## Gates 1–3 computed

**Gate 1 — predicate true by turn 150 in ≥8/10 catastrophes: PASS, 9/10.**

Activation turns: 147, 138, 122, 119, 91, 137, 59, **168**, 95, 113. Only `897782213` (t168)
misses the 150 boundary.

**Gate 2 — first true turn precedes the observed collapse interval in ≥8/10: PASS, 10/10.**

I define the collapse interval outcome-blindly as the checkpoint pair where the margin first
crosses from positive to non-positive. Activation precedes it in every one of the ten:

| game | activation | margin t50→t300 | collapse interval |
|---|---:|---|---|
| 897780891 | 147 | +20 +46 +121 +52 −73 −166 | (200,250) |
| 897781216 | 138 | +2 +13 +59 −3 −38 −126 | (150,200) |
| 897781413 | 122 | +19 +13 +47 +29 −119 −219 | (200,250) |
| 897781719 | 119 | +11 +19 +59 −12 −188 −416 | (150,200) |
| 897781840 | 91 | +34 +99 +163 +49 −50 −141 | (200,250) |
| 897781987 | 137 | +6 +28 +63 +77 +50 −100 | (250,300) |
| 897782076 | 59 | −2 +48 −2 −28 −72 −115 | (100,150) |
| 897782213 | 168 | +11 +39 +67 +61 −15 −113 | (200,250) |
| 897782302 | 95 | +18 +57 +9 −35 −95 −169 | (150,200) |
| 897782366 | 113 | +24 +47 +69 +54 −65 −109 | (200,250) |

**Gate 3 — false-positive activation by turn 150 in ≤20% of the seven matched wins: PASS,
0/7.** Four matched wins have no opponent TRAIN at all; `897782068` trains once (t3);
`897782379` trains once (t280); `897781674` reaches three units only at t168. **Zero** cross
the boundary by t150.

The predicate separates the two cohorts cleanly on this package — 9/10 versus 0/7. That is a
stronger separation than I expected, and I want it reviewed rather than trusted.

## Gate 4 is the open one, and it is the one I flagged in my acknowledgement

Gate 4 needs "at least one exact ETA-6-eligible treatment-scoring decision after activation".
From the reconstruction result, eligibility is an existing **tracked** `Target::Tree` at
**ETA ≤ 6**, where ETA is BFS distance with ceil-div — a **travel** estimate, not ripeness.

What the package gives me: the full map grid in frame 0, per-troll positions from
`"moved to (x, y)"`, landed plant events with player attribution, and each side's issued
commands. What it does not give me directly is the resident's internal candidate set, and the
entity stream is a delta-encoded viewer format I have not yet decoded.

I will therefore determine, and report before claiming gate 4 either way, whether tree
identity and provenance are recoverable exactly from the public stream. If they are, gate 4
is computable as an *opportunity* test — an opponent-created existing tree within BFS ceil-div
6 of one of our trolls at a post-activation decision — and I will state that interpretation
explicitly as mine. If they are not recoverable exactly, I publish a **schema blocker** naming
the missing field rather than approximating eligibility and calling the gate passed.

## Next

Gate 4 feasibility determination, then the published decision schema, analyzer and semantic
tests under `claude_1/h3a-conditioned-value-unblock-*`. `rust/src/bin/yamo_orchard_live.rs`
re-verified byte-exact at `fff6669b`. No source arm has been edited or built.
