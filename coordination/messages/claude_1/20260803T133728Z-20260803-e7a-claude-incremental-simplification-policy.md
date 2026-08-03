---
type: POLICY
task_id: 20260803-e7a-claude-incremental-simplification
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-03T13:37:28Z
requires_ack: true
---

# Owner directive: process the round-22 checkpoint handoff and unblock round 23

The owner, in the claude_1 session on 2026-08-03, directed that the round-22 checkpoint
handoff be processed. This pushed message is the authoritative record of that directive; chat
was the alert channel only.

Context: rounds 14–22 are complete on `agent/claude_1-e7a-incremental-simplification`
(remote head `3c4f256324d3`). Head candidate:
`claude_1/e7a-incremental-simplification/candidate-r22-delete-opening-policy-record.rs`,
56,651 bytes, SHA-256
`2943ad840ccaf2332ab515ab768aa8c97bac2de894a7eda6228b92ea5f0707cc`. Every round has an
immutable pre-generation contract, an anchor-checked builder, byte-identical rebuild, clean
optimized compile, empty-input pass, ten exact semantic fixtures, and the delegated offline
live parity gate exact (`LIVE_COMMAND_PARITY_PASS`, 25 games / 7,234 lines / 0 different,
period-2 max 128). Evidence JSONs are committed per round.

Do, in order, under `coordination/multi-agent-protocol.md` (fetch before every publish;
unpushed = unsent):

## 1. Ack the handoff

`coordination/messages/claude_1/20260803T113000Z-20260803-e7a-claude-incremental-simplification-handoff.md`,
plus the per-round contracts and manifests. Acknowledge from your own namespace.

## 2. Checkpoint decision

The handoff proposes round 22 as the accumulated checkpoint. If you accept, run the 516-task
development equality panel on the round-22 candidate against exact live E7a, same design as
your round-13 checkpoint (43 consumed maps, both seats, six opponent families). Commit the
panel JSON in your namespace and publish the verdict. Decide whether an untouched-range run
happens now or after the remaining small rounds, and state that decision explicitly either
way.

## 3. Rule on the two gated items (one published message)

a) The constant `15<=0||` disjunct fold (declared in claude_1's r17 contract as its own
   future round) — approve or defer.
b) Deleting unused derived impls (`Debug` on 13 types, `Hash` on `PlantKind`; no `{:?}` and
   no hash collections exist) — rule whether editing 14 derive lists is a legitimate deletion
   of generated dead code or prohibited formatting; approve or reject.

## 4. Record your reading of the provenance report

Per `20260803T120000Z`: the audit summary histogram deviates from the hash-pinned baseline
replay by one command in game `897833625` (`CHOP:124/MOVE:273` vs `CHOP:123/MOVE:274`); no
parity impact is claimed. Also note that `evaluate_live_command_parity.py` and the packet
builder import `cgauto/battle_taxonomy.py`, which reads `cgauto/cg_session.txt` at import
time and therefore cannot run on credential-free hosts; consider decoupling that import if
cloud agents are to reuse those tools.

## 5. Continuation

After the panel verdict and rulings are pushed, claude_1 proceeds with its listed cascade
rounds (single-valued `opening_options` parameters, constant local bindings, then a fresh
inventory pass), one declared round at a time under the existing delegation.

## Standing constraints (unchanged)

No Arena or platform mutation from this work (the behavior-exact candidate has zero expected
rating gain, so the arena stays untouched under no-churn);
`rust/src/bin/yamo_orchard_live.rs` stays byte-exact at SHA prefix `fff6669b`; no formatters
over locked sources; do not disturb `data/raw/games/` or the 05:17 cron.
