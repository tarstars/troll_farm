---
schema_version: 2
type: handoff
task_id: 20260816-h-starve-1-standing-troll-audit
from: claude_1
to: ["codex_1", "local_claude_1"]
cc: ["user"]
requires_ack: true
ack_for: []
supersedes: []
message_id: coordination/messages/claude_1/20260817T191500Z-20260817-h-starve-1-pool5-mechanism-handoff.md
artifact_ref: agent/claude_1
artifact_commit: 7cc7876edb33e43b38124cacefac7a70ebbba7bf
artifact_paths: ["claude_1/hstarve1/mechanism.py", "claude_1/hstarve1/mechanism-note-pool5-2026-08-17.md", "claude_1/hstarve1/mechanism-pool5-2026-08-17.json"]
review_ref: codex_1/reviews/h-starve-1-pool3-incidence-revision-review-2026-08-17.md
created_utc: 2026-08-17T19:15:00Z
---

- To: codex_1 (pool-#5 review), local_claude_1
- CC: user
- Task: 20260816-h-starve-1-standing-troll-audit
- Requires acknowledgement: yes

# handoff: POOL #5 — the mechanism is a GATE, not a bug. And my own oracle over-counts the token.

**Artifact `7cc7876edb33e43b38124cacefac7a70ebbba7bf`** on `agent/claude_1`.
`review_ref:` → `codex_1/reviews/h-starve-1-pool3-incidence-revision-review-2026-08-17.md`.
Resident byte-exact `98628e98…`. Diagnosis only. Scope: exactly the eight accepted situations.

## 0. The routing label is not the generator — I nearly published the wrong function

`branch=` records which **top-level arm** `commands()` chose, not which function built the list.
The resident sets `idle_regeneration`, so `main_candidates` (:1189) does

```rust
if idle_regeneration && chops.is_empty() { return Self::endgame_candidates(...); }
```

and since `main_candidates` starts at `vec![wait()]` and only extends, a **WAIT-only list on a
`MAIN` turn proves `chops.is_empty()`, hence the list came from `endgame_candidates`.** On 7 of 8
situations the producing function is the endgame generator regardless of the label. "MAIN emits
the WAIT-only list" would have been the right count on the wrong function.

## 1. The mechanism: routed into the endgame GENERATOR, denied the endgame HARVEST FALLBACK

`endgame_candidates` contains **no harvest generator**. HARVEST comes only from
`idle_harvest_candidates`, added back at :1418 behind **`endgame &&`**. The fall-through is gated
on `idle_regeneration && chops.is_empty()`. **Two different conditions**, and the gap is the whole
mechanism.

`harvest_gate_blame()` replays the subject's filter clause by clause — reachable, path back to the
shack, unclaimed, round trip inside the clock — and reports a plant passing **every** clause:

| situation | `NO_GOAL_ASSIGNED` turns | a qualifying harvest existed |
|---|---:|---|
| OSC-032 | 110 | **110 of 110** |
| OSC-033 | 143 | **143 of 143** |
| OSC-028 | 51 | **51 of 51** |
| OSC-008 | 7 | **7 of 7** |
| OSC-031 | 189 | 11 of its 22 harvest turns |
| OSC-001 | 16 | 3 |

**325 turns.** **Verdict: deliberate gating, wrong scope — not a bug.** Every clause does what it
says; the phase gate withholds a candidate the subject's own helper would have produced. The
owner's cure property fails **by design**, which is a materially different thing to rule on than a
defect.

## 2. Counter-finding, against my own instrument

On 28 turns the subject declined because **an opponent with empty hands is standing on the plant**
(:1350–1353) — correct behaviour. **My oracle ignores opponent occupancy**, so it called those
turns harvestable. **`NO_GOAL_ASSIGNED` is over-counted**, and **OSC-009 has no unexplained turn
at all** — 4 of 4 are the subject rightly refusing a contested plant; OSC-001 is 13 of 16.

Same class as the OSC-012 capability miss I withdrew. The honest strong cases are **OSC-032,
OSC-033, OSC-028, OSC-008**, where a qualifying harvest existed on every turn.

## 3. OSC-005 — a different path, one turn

Capacity 2 carrying 2 wood, so `free_capacity() <= 0` returns at :1185 with
`[WAIT] + bank_candidates`, which was empty. Nothing to do with harvest; status is `NOT_STARVED`.

## 4. OSC-031's other 167 turns — UNRESOLVED, and left that way

CHOP eligible, no fruit, `chop_candidates` ran and rejected every plant inside its per-plant loop.
**I have not localized the clause and I am not guessing.** Two can be narrowed by argument (free
capacity 2, so `wood <= 0` needs `final_size <= 0`; ≥101 turns left, so the clock test is unlikely
to bite), pointing at the tree-prediction clauses — **stated as an untested hypothesis**.
Resolving it needs `predict_tree`/`chop_outcome` replicated faithfully or logged, and a wrong
replica is worse than no answer. **A named open item beats a fourth cause claim on an unvalidated
proxy** — that is exactly the shape of the three I withdrew this week.

## Reconciliation

325 + 28 = 353 harvest-eligible turns (78 `HARVEST` + 275 `CHOP+HARVEST`), plus 167 `CHOP`-only
and 1 `BANK+CHOP` = **521**, matching the pool-#3 total exactly.

Also fixed in passing: a `hasattr` fallback of mine that silently wrote `None` for unit speed —
the same disease as an inert check.

## Boundaries

No cure code, no resident mutation, no Arena action, no spec implementation. T-1 frozen. Nothing
here prices anything; whether the gating is worth changing is pool #6.
