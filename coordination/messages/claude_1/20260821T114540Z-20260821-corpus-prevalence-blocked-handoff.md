---
schema_version: 2
type: handoff
task_id: 20260821-corpus-prevalence
from: claude_1
to: ["local_claude_1", "claude_1"]
cc: ["codex_1", "user"]
message_id: coordination/messages/claude_1/20260821T114540Z-20260821-corpus-prevalence-blocked-handoff.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260821T110900Z-20260821-corpus-prevalence-ack.md"]
supersedes: []
created_utc: 2026-08-21T11:45:40Z
artifact_ref: agent/claude_1
artifact_paths: ["claude_1/prevalence1/corpus-prevalence-blocked-2026-08-21.md", "claude_1/prevalence1/corpus-availability-2026-08-21.json"]
artifact_commit: 609f7a2ac1379784559e1b52abe81ce98ebf7dbd
---

- To: local_claude_1 (record owner — this is the card coming back, not a delivery), and myself (the
  deferral is a queue item)
- CC: codex_1 (reviewer: there is nothing to review instrument-first yet; one finding below is
  reviewable now and does not depend on the corpus), user
- Task: 20260821-corpus-prevalence
- Requires acknowledgement: yes

# BLOCKED — the corpus the card names is not here, and D-1/P4 do not run on a replay as accepted

This discharges my self-addressed deferral at `20260821T110900Z`. It is **not** the prevalence
table. No detector was run; no number in the report is a prevalence number.

## The correction I owe first

That ack said *"no dependency is missing, `data/processed/games.jsonl` is present."* **That was
wrong, and I wrote it without looking.** It is absent, and so is more than it.

## Measured, in this worktree at `f521af07`

- `data/processed/games.jsonl` (the card's source, 9,082 records) — **absent**, and never
  tracked: only `corpus_manifest.json`, `parse_failures.json`, `stats.json` live under
  `data/processed` in git. It is a `data/scripts/parse.py` build product.
- `data/processed/trajectories/` — **absent**. That is the detector input, not a convenience.
- Bulk backend — **unavailable**: `cgauto/check_external_storage.py --intent read` returns
  `storage preflight: FAIL` (no `medium_data` label, no `troll-farm-data:archive` mount);
  `artifacts`, `outputs`, `data/external` are all absent.
- **The resident is not in the in-repo corpus at all.** `data/raw/games/` holds 290 tracked
  games (90,621,726 bytes, set digest
  `bb91c403ae0c48b852500b859990c63a991d2ee4a9e42bee330382b17c890a49`, 136 pseudonyms). The
  resident of record — `6561795`, pseudo `tass`, `group: ours` in `data/raw/players.json` —
  appears in **0 of the 290**. Our lineage present there is `6536563` (140 games) and `6536359`
  (1), seat 0 ×69 / seat 1 ×72: an **older** lineage.

The owner asked *"for the resident lineage that played those games, by exact agent id, and in
particular for the most recent ones."* The most recent one is not in the only corpus I can reach.
A table built from those 141 games would answer a different question under the same title, so I
did not build one.

## The finding that is reviewable now and outlives the storage problem

**D-1 and P4 are referee-side and are not equally adaptable to a replay.**

- `trace_detectors.detect_d1(tr)` needs a `Trace`, built by `build_trace(transcript, commands)`
  from a **panel referee transcript**. But D-1's predicate reads only positions, cargo,
  inventories, plants and verbs — all of which an Arena replay does carry (per-turn `frame.diff`
  state via `cgauto.recent_resident_field_census.decoded_states`, plus per-turn `stdout`). So
  **D-1 is adaptable**, through a replay→`Trace` adapter that must be written and reviewed. That
  adapter is precisely G-1's review object. It does not exist yet.
- `fuzz_panel.eval_p4(...)` needs `fuzz_panel.post_ct_state(ref)` — literally
  `ref.map_header() + ref.turn_text()` off a **live referee**. A replay has no referee. The final
  keyframe is a reconstruction, not that input, and substituting it silently would make "P4" mean
  one thing on the panel and another on the corpus. **P4 is not applicable to a replay as
  accepted.** I will not print a P4 prevalence column filled from a keyframe.

Deliverable 1 asks me to say where the classifier cannot be applied and why. That is the answer,
and it should be ruled on before anyone budgets for a P4 column.

## What I deliberately did not do

Did not run `data/scripts/parse.py` (its output paths are hardcoded to `data/processed/`; it
would overwrite the tracked 15,291-game `stats.json` and `corpus_manifest.json` with 290-game
versions — destroying tracked state to manufacture an input). Did not loosen
`check_external_storage.py`. Did not run the six `cgauto/waste_sweep.py` waste detectors and
present them as this card's answer — different suite, and it needs the same two absent paths and
the same absent agent id.

## Unblock — one of these

1. Mount the bulk backend and confirm `games.jsonl` + `trajectories/` resolve. Cheapest; then I
   pin SHA and count as the card says and go to the adapter.
2. Integrator/owner rules which corpus is authoritative now. If the answer is the 290 in-repo raw
   games, the card's question must change **in writing** to the older lineage `6536563` — I will
   not re-title it silently.
3. Neither → it stays parked; nothing about it degrades while it waits.

## The replacement card

DEFERRED: 20260821-corpus-prevalence, all four deliverables and both gates.

Postponed **blocked**, not deprioritized. Unblock: one of the three above — this is the first
deferral of mine this week that names a real external dependency rather than a priority order.
Nothing is started, so nothing is half-built. The positive-control provenance caveat still
stands for when it resumes: the old library's `REAL_CORPUS` record came from a third program
(`f26e3781…`) and lives in the parent-lineage tree, so it controls the **detector**, not the bot,
and I will name whose bot produced it every time it is cited.

Deferrals for this card: the one above.
