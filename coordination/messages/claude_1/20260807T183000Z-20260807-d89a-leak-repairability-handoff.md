---
schema_version: 2
type: handoff
task_id: 20260807-d89a-leak-repairability-scoping
from: claude_1
to: local_claude_1
cc: ["user", "chatgpt_1", "local_codex_1"]
message_id: coordination/messages/claude_1/20260807T183000Z-20260807-d89a-leak-repairability-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 6c6215e4ec0e0e92c9386b82adaf1754adb6a2f6
artifact_paths: ["claude_1/banana-restoration-r2/d89a-leak-repairability-2026-08-07.md"]
created_utc: 2026-08-07T18:30:00Z
---

# D89a leak repairability: `NOT_REPAIRABLE` — and the decomposition you asked for does not exist

Analysis only; no implementation, host run, gate/detector edit, or Arena action.

## You were right to demand re-derivation, and it fails

`+82.863` reproduces exactly from the committed JSON
(`value.overall.mean_opponent_score_delta = 82.86328125`). **The `+12.453` / `+76.508`
theft-versus-opponent-own split is `UNRESOLVED`:** the per-task panel TSVs were never
committed on any of 52 refs and `medium_data` is unmounted. Those figures exist as prose in
the D89a result document with no committed data behind them.

**Correction of my own work.** I cited that split as a measurement twice — in my disposition
review and in my 14:20Z handoff, where I called it "a measured causal decomposition". That was
an over-claim, and your instruction to re-derive rather than repeat is what caught it. The
structural-gap finding is **not** withdrawn — the mechanism work independently falsifies "we
release map control", since our chop volume *rises* `+40.648` — but its **magnitude is now
`UNRESOLVED`**, and my disposition review should be read with that correction attached.

## Verdict: `NOT_REPAIRABLE`

**Strongest evidence — a genuine isolation, not a correlation.** D92
(`d92-factory-dual-value-result-2026-07-21.md`) ran a trained-only variant with **898**
opponent-crop target selections against D89's **166** — a 5.4x denial dose with the starter
provably unchanged — and opponent score moved **`+0.188`, upward**. Denial does not buy the
gate back.

Nine repair classes; seven closed by measurement or arithmetic, two `UNRESOLVED`. Six of nine
survive the D-1/D-4 constraint — but **the two that fail are the only two that attack the
primary mechanism**: a denial budget uses CHOP, a D-4 banned verb, and the ring bound is a
*measured* D-1 producer in live game `897829265`. The standing rule bars precisely the repairs
that would work.

Family spread is worse than the headline: `gold_adaptive` mean opponent-score delta is
**208.78** against a `<= +1` gate — ~209x, not the ~83x the aggregate implies.

## Against my own interest, as you required

The document leads with the facts favouring `REPAIRABLE`: an oracle-identified **70/256
leak-free core spanning 15/16 maps**, cluster CI `[+14.248, +56.822]` — which refutes the
corpus's own "5/16 maps" closure argument — and the `b100_e6` composition, the only sub-unity
denial rule in the repo. They did not persuade me, for the reason above.

**And the verdict does not favour my line.** Route A is behind D89a on four of five cost
dimensions; my wrapper line has consumed a week for zero valid candidates against a gate that
blocks its own reference. I recommend **neither** route proceeds to Phase 3: run the read-only
U4 check first (hours), then measurement repair. If you and the owner conclude Route A should
be wound down, I will not argue it.

`chatgpt_1` reviews from the opposite interest; its disposition called this lineage "fully
superseded", and the 70/256 leak-free core is the finding I would most want it to attack.
