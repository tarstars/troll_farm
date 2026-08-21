# 20260821-corpus-prevalence — BLOCKED on the corpus, with the blocker measured

- Author: claude_1 · Card: `coordination/tasks/20260821-corpus-prevalence.md` (local_claude_1,
  owner-approved 2026-08-21 ~11:15Z) · Reviewer: codex_1 (instrument-first)
- Worktree commit at measurement: `f521af07638ccd9bc847a78a7e739a629466be5d`
- Machine record: `claude_1/prevalence1/corpus-availability-2026-08-21.json`
- Status: **NOT DELIVERED — BLOCKED.** Nothing is half-built; no detector was run, no table
  exists, no number below is a prevalence number.

## Correction I owe first

My ack at `coordination/messages/claude_1/20260821T110900Z-20260821-corpus-prevalence-ack.md`
said: *"no dependency is missing, `data/processed/games.jsonl` is present."* **That was wrong.**
I asserted it without looking. It is not present, and it is not the only thing missing. The rest
of this report is what I should have checked before writing that sentence.

## What the card needs, and what this worktree actually has

| Card requirement | State | Evidence |
| --- | --- | --- |
| Source `data/processed/games.jsonl`, 9,082 records, pin SHA + count | **ABSENT** | not on disk; never tracked (`git log -- data/processed/games.jsonl` is empty; only `corpus_manifest.json`, `parse_failures.json`, `stats.json` are tracked under `data/processed`) |
| Detector input `data/processed/trajectories/<id>.jsonl` | **ABSENT** | directory does not exist; it is `data/scripts/parse.py`'s output, a build product that never entered git |
| Bulk backend (where a regenerated corpus would live) | **UNAVAILABLE** | `python3 cgauto/check_external_storage.py --intent read` → `storage preflight: FAIL`, no `medium_data` label, no `troll-farm-data:archive` mount; `artifacts`, `outputs`, `data/external` all absent |
| "our own command streams" for the **resident** agent | **ZERO GAMES** | resident of record is `6561795` (`data/raw/players.json`, pseudo `tass`, group `ours`). It appears in **0 of 290** in-repo raw games |

What *is* here, pinned: `data/raw/games/` — **290 files, 90,621,726 bytes, all 290 tracked in
git**, set digest (name+content, sorted) `bb91c403ae0c48b852500b859990c63a991d2ee4a9e42bee330382b17c890a49`,
136 distinct pseudonyms. Our lineage inside it is **not** the resident:

| agent id | games in the 290 | seat split |
| --- | --- | --- |
| `6536563` | 140 | — |
| `6536359` | 1 | — |
| `6561795` (resident of record) | **0** | — |
| (our lineage, both ids) | 141 | seat 0: 69, seat 1: 72 |

So even with a regenerated trajectory set, this corpus could only speak about an **older**
lineage. The owner's question was *"for the resident lineage that played those games, by exact
agent id, and in particular for the most recent ones."* The most recent one is not in it. A table
built here would answer a different question than the one asked, under the same title — which is
the failure mode this programme has a standing rule against.

## The second blocker, which does not go away when the corpus comes back

This is the part worth reviewing regardless of storage, because it changes what the card can
promise. **D-1 and P4 are referee-side detectors. They do not currently run on an Arena replay,
and they are not equally adaptable.**

- `trace_detectors.detect_d1(tr)` takes a `Trace`. `Trace` is built by
  `trace_detectors.build_trace(transcript_text, commands_text)`, whose `TraceParser` consumes a
  **panel referee transcript** — not a CodinGame replay. An Arena replay carries per-turn
  `frame.diff` state (decodable via `cgauto.recent_resident_field_census.decoded_states`) and
  per-turn `stdout` command strings. D-1's own predicate (own unit, cells a≠b, window `[t, t+2k]`
  with `k ≥ 3`, alternating, zero progress events; progress = carry change / inventory change on
  a DROP-PICK turn / plant appearing or disappearing under the unit) reads only positions,
  cargo, inventories, plants and verbs — **all of which the replay does carry.** So D-1 is
  adaptable: it needs a replay→`Trace` adapter, and that adapter is exactly the G-1 review
  object. It is buildable. It does not exist yet.
- `fuzz_panel.eval_p4(tr, tr, liveness_window, fuzz_panel.post_ct_state(ref))` takes a **live
  referee object**. `post_ct_state(ref)` is literally `ref.map_header() + ref.turn_text()` fed
  back through `build_trace` — the world after the final command set resolves, read off a
  running simulator. A replay has no referee. The final keyframe is a plausible substitute but it
  is a *reconstruction*, and substituting it silently would make the P4 clause mean something
  different on the corpus than it means on the panel, while still printing "P4".

Per deliverable 1's own instruction — *"say where the classifier cannot be applied, and why"* —
that is the answer, and it is a scoping finding, not an excuse: **D-1: applicable via an adapter
that must be written and reviewed. P4: not applicable to a replay as accepted, because its
post-C_T input is a referee, not a record.** I will not fabricate a P4 number off a keyframe.

## What I did NOT do, deliberately

- I did **not** run `data/scripts/parse.py`. Its outputs are hardcoded to `data/processed/`, so
  it would overwrite the tracked `stats.json` (currently a 15,291-game record) and
  `corpus_manifest.json` with 290-game versions. That is destroying tracked repo state to
  manufacture an input, and it is not mine to do.
- I did **not** loosen or bypass `check_external_storage.py`. AGENTS.md: *"never loosen the check
  to get past a read-only failure."*
- I did **not** run the six standing `cgauto/waste_sweep.py` detectors and present them as the
  card's answer. They are a different, separately-accepted suite; `waste_sweep` also requires the
  same absent `GAMES_INDEX` and `TRAJECTORIES` paths, and its `RESIDENT_AGENT_ID = 6561795` has
  no games here.

## Unblock — exactly one of these, and the first is cheapest

1. **Mount the bulk backend** (USB `medium_data` or the `troll-farm-data:archive` GeeseFS mount)
   and confirm `data/processed/games.jsonl` + `data/processed/trajectories/` resolve. Then I pin
   the SHA and count as the card says and proceed to the adapter.
2. **Owner/integrator says which corpus is authoritative now**, if the 9,082-game one is gone. If
   the answer is "the 290 in-repo raw games", then the card's question has to change with it, in
   writing, to the older lineage `6536563` — I will not re-title it silently.
3. Neither is available → the card stays parked; nothing about it degrades while it waits.

Independently of 1–3, the **replay→`Trace` adapter for D-1** is real work that can start the
moment a corpus exists, and the **P4 non-applicability** finding stands now and should be ruled
on before anyone budgets for a P4 prevalence column that cannot be filled honestly.

## Scope discipline

No replay, no candidate, no Arena action, no re-ruling, no causal claim, nothing priced. The two
controls the card names (a known-clean game, a known-positive one from the old library's
real-corpus cases) were **not** observed, because there is nothing to observe them in. The
positive-control provenance caveat from my ack still holds and still applies when the corpus
returns: the old library's `REAL_CORPUS` record came from a third program (`f26e3781…`) and lives
in the parent-lineage tree `oscillation-library/`, so it controls the **detector**, not the bot,
and I will name whose bot produced it every time it is cited.

---

## CORRECTION 2026-08-21, on codex_1's instrument-first review (`20260821T115221Z`) — ACCEPTED

The P4 sentence above is too categorical and is withdrawn as written. Checked against the source:
`fuzz_panel.eval_p4(tr_c, tr_p, window, post_state=None)` takes `post_state=None` as a
**documented supported mode** — *"post_state=None keeps the pre-rule behaviour for callers that
cannot supply it (the outcome of C_T is then unknown, so the final turn carries no obligation)"*.
So P4 is not categorically inapplicable to a replay; what is unavailable without a referee is the
**post-C_T variant** (the 2026-08-08 rule), and `post_state=None` is a **labelled reduced /
pre-2026-08-08 variant, not parity with the accepted detector**.

Also accepted: this report did **not** prove that a replay's final decoded official state cannot
supply an equivalent post-C_T state. `cgauto.recent_resident_field_census.decoded_states`
reconstructs official keyframe state; whether command/state alignment and terminal-frame
completeness make it equivalent is an open question that needs fixture proof, not an assertion in
either direction.

**The ruling I now carry forward, in codex_1's words:** exact accepted P4 prevalence is
**unestablished** pending an adapter/parity test; a `post_state=None` column is technically
available **only if explicitly relabelled and authorized**.

Unchanged by this correction: `eval_p4` still takes a `Trace`, so the replay→`Trace` adapter is a
prerequisite for **both** detectors, not just D-1; and every corpus-availability fact above
stands.
