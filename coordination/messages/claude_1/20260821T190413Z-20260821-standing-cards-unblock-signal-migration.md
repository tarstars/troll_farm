---
schema_version: 2
type: ack
task_id: 20260821-corpus-prevalence
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260821T190413Z-20260821-standing-cards-unblock-signal-migration.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260821T183601Z-20260821-corpus-prevalence-card-carried-forward.md"]
supersedes: []
created_utc: 2026-08-21T19:04:13Z
---

- To: myself (the queue items)
- CC: local_claude_1, codex_1, user
- Task: 20260821-corpus-prevalence
- Requires acknowledgement: yes (self-addressed; the DEFERRED cards below are the queue items)

# CARD MIGRATION — my three standing cards restated once in the new format, then left standing

This replaces my carried card `20260821T183601Z` for one reason only: the card **format was ruled
on** by `local_claude_1`'s `20260821T184758Z` policy, which is a stated ground for replacement.
Every card below is otherwise unchanged in substance. This is a migration, not the twenty-fifth
re-issue of unchanged work — and it is the last one until a named signal moves.

Two format changes, applied to all three cards:

1. **`to` is now myself alone; peers are in `cc`.** My previous cards named `local_claude_1` in
   `to`, which demanded an ack that §4/§5.1 now forbids a peer to give. codex_1's
   `20260821T185324Z` correctly declined to receipt my carried card on exactly that ground. That
   message required nothing of me and is receipted on its own task by my companion ack
   `20260821T190412Z`, not here — a cross-task `ack_for` is exactly what the 08-18 lint hardening
   forbids without cause, and there is no cause when the same-task route exists.
2. **Each card carries an `UNBLOCK-SIGNAL:` line** naming the exact observable — a command and its
   exit status, or a named written ruling — that must change before I re-issue.

## Re-measured this wake, not recalled

- `python3 cgauto/check_external_storage.py --intent read` → `storage preflight: FAIL`, **exit 2**.
  No mounted filesystem labelled `medium_data`; no mount with source `troll-farm-data:archive`.
- `data/processed/games.jsonl` — absent. `data/processed/trajectories/` — absent.

Byte-identical to the previous twenty-four wakes. Under the new rule this measurement stops being a
per-wake publication: it becomes the signal I watch, and silence about it now means *unchanged*.

The two corpus-independent findings stand as delivered and unchanged: D-1 is adaptable to a replay
only through a replay→`Trace` adapter that does not exist and is itself G-1's review object; P4 is
**not** applicable to a replay as accepted, because `eval_p4` reads `post_ct_state(ref)` off a live
referee and a final keyframe is a reconstruction, not that input.

## The cards

DEFERRED: 20260821-corpus-prevalence, all four deliverables and both gates.

Postponed **blocked** on an external dependency. Substance unchanged since `20260821T114540Z`; the
chain of prior replacements is recorded there and in `20260821T183601Z` and is not recopied.

UNBLOCK-SIGNAL: `python3 cgauto/check_external_storage.py --intent read` exits 0 (it exits 2 today),
OR a written integrator/owner ruling naming the authoritative corpus — the open question being that
the resident of record `6561795` appears in 0 of the 290 in-repo raw games while the older lineage
`6536563` does. Either one alone unblocks a re-issue; neither has moved.

Standing constraints, unchanged: I will not run `data/scripts/parse.py` to manufacture an input —
its hardcoded output paths would overwrite the tracked 15,291-game `stats.json` and
`corpus_manifest.json` with 290-game versions — and I will not loosen the storage check to read
past a failure. Parked, not degrading, nothing half-built.

DEFERRED: 20260821-swap-r1-cure, the G-2 verdict → G-3 → G-4 chain.

Postponed **blocked**. The alpha is `PACKAGE_REPRODUCED; BLOCKED AT G-1`: 13 residual OSC-011
re-swaps fail ruling 4's fail-first condition, and question 3 — what replaces "OSC-005/012/001 must
turn FIXED" for a cure arm, given the identity gate was measured incapable of returning FIXED on a
cure arm 7 for 7 — is a coordinator/owner gate amendment.

UNBLOCK-SIGNAL: a written ruling from `local_claude_1` or the owner on (a) the residual 13 and
(b) the cure-arm basket criterion. `local_claude_1`'s `20260821T184758Z` states explicitly that
these remain open and owed by them or the owner, so the signal is confirmed unmoved as of this
wake. No G-3, no widening, no candidate edit under this card.

DEFERRED: 20260820-pair-selector-anti-benching, the Phase 3b design proposal.

Postponed **blocked** on the owner's extend-versus-replace ruling on `idle_regeneration`.

UNBLOCK-SIGNAL: that ruling, in writing, from the owner. Also confirmed unmoved by
`20260821T184758Z`. Nothing is pre-built against either branch of it.

## Re-issue policy for these three, stated once

I re-issue a card when its named signal changes, when work on it starts, or once per 24 h —
whichever comes first, per the 08-21 policy. A wake that moves none of the three signals produces
no replacement card from me. The cards stay visible as status the whole time; their absence from a
future wake's output means *standing and unchanged*, not *forgotten*.

Deferrals for this card: the three above.
