---
schema_version: 2
type: handoff
task_id: 20260810-manifest-implementation
from: claude_1
to: local_claude_1
cc: ["user", "chatgpt_1", "local_codex_1"]
message_id: coordination/messages/claude_1/20260810T133000Z-20260810-m3a-oscillation-library-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: a6d5de6f750cafbd8d6d51795903d7e3192dcbc6
artifact_paths: ["claude_1/banana-restoration-r2/oscillation-library", "claude_1/banana-restoration-r2/oscillation_library.py", "claude_1/banana-restoration-r2/test_oscillation_library.py", "claude_1/banana-restoration-r2/oscillation-library-2026-08-10.md"]
created_utc: 2026-08-10T13:30:00Z
---

# M3a delivered: 33 frozen situations, 47 episodes — and one finding that decides the cure

Library hash `5858d351…`. Verified by me: **40/40 tests pass with the gated replay enabled**
(`OSC_LIB_REPLAY=1`, no skips), and `rust/**`, `cgauto/**`, `fuzz_panel.py` and
`trace_detectors.py` are byte-unchanged.

## The finding that matters most

**All 20 terminal (≥62-turn) D-1 episodes have an IDLE blocker. Not one episode with a
*working* blocker reaches 62 turns.**

That is the empirical form of what I argued from the mechanism side: the mover invariant alone
would convert oscillations into stalls, because the pathology is not the moving unit — it is a
peer that never moves. **The idle-yield rule is the load-bearing half of the cure, and the
mover invariant is the supporting half**, not the reverse. It also explains the `m040`
two-worker case lasting 6 turns rather than 194: its blocker is working.

## Contents

- **33 situations / 47 episodes** (27 D-1, 5 P4-stall, 1 partial real-corpus), deduped on
  mechanism + blocker state + resolver-relevant local geometry, multiplicity retained.
- Mechanism histogram (situations/episodes): **M1 11/11 · M2 14/20 · M3 1/1 ·
  UNCLASSIFIED 7/15**.
- Blocker split: **IDLE 17/23 · WORKING 8/8 · NONE 8/16**.
- All 32 FULL situations **replay byte-exactly** from literal data through `make_referee` with
  no generator call; `m110` is byte-identical to the published R-6a fixture.

**The coverage gap, stated plainly: 7 situations / 15 episodes are `UNCLASSIFIED`** — roughly a
third of the corpus does not fit M1/M2/M3. The merged three-mechanism model is therefore not
complete, and I would not want it treated as such when M3b adjudicates.

## Freezing is demonstrated, not asserted

Ten tests each **really mutate a scratch copy** — world state, classification, a single command
line, a self-consistent forgery, a forgery that also rewrites the index, deleted and added
files, count, library hash, dropped provenance, nulled world state — and show `IntegrityError`,
with a control proving the copy loads clean first.

## What yielded nothing, and nothing was invented

`m040` seat 0 (no violation at all under corpus `c3`); the **18 real B3.4 games — no per-episode
rows are committed anywhere**, since `data/external` is git-ignored, so the real-corpus arm is
one partial situation and no more; the Zasmu postmortem (returns are 3 states, below D-1's ≥7
threshold). Given three cited-but-uncommitted artefacts this week, I would rather the library be
smaller and true.

## M3b scope held

**No "best action" is recorded anywhere** — not in a situation file, the index, the loader or
the report. A test walks every key and string of every frozen file against forbidden-key and
phrase lists, and the index declares the M3a/M3b boundary. Recording an adjudication now,
derived from the scorer M3b must judge, is exactly the circularity that has already cost three
detectors.
