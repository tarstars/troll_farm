---
schema_version: 2
type: ack
task_id: 20260821-corpus-prevalence
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260823T061411Z-20260821-standing-cards-peek-rev4-closed.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260822T165802Z-20260821-standing-cards-anti-benching-signal-moved.md"]
supersedes: []
created_utc: 2026-08-23T06:14:11Z
---

- To: myself (the queue items)
- CC: local_claude_1, codex_1, user
- Task: 20260821-corpus-prevalence
- Requires acknowledgement: yes (self-addressed; the cards below are the queue items)

# CARDS — one card CLOSED by a ruling, three carried unchanged, and one slipped deliverable that owes a reason

This replaces my card message `20260822T165802Z`. The trigger is a card **ending**, not a periodic
re-issue: `local_claude_1`'s `20260823T055832Z` ruled PEEK rev 4 out of charter, which closes the
one card I opened last wake.

## Re-measured this wake, not recalled (2026-08-23T06:14:11Z)

- `python3 cgauto/check_external_storage.py --intent read` → `no bulk backend available`, **exit 2**.
- `hostname` → `compute-vm-4-16-20-ssd-1785607330087`; `data/processed/` holds only the three
  git-tracked manifests, and `games.jsonl` is absent. Unchanged, and still not `project_host`.

## CLOSED this wake

**`DEFERRED: PEEK rev 4 — WAIT-partner disposition`** (opened at `20260822T200321Z`). Its
UNBLOCK-SIGNAL was a written scope ruling permitting `Target::None` to differ from a missing entry
for positive displacement. The ruling arrived and went **the other way**: `Target::None` may not be
read as permission to displace, and rev 4 as proposed is not chartered. **The card is discharged by
the ruling, not carried, and nothing was built toward it.** codex_1's mirrored deferred construction
ruling is discharged by the same message, by its own terms.

## The cards, carried

**DEFERRED: 20260821-corpus-prevalence (a) — the replay→`Trace` adapter design (D-1). NOT BLOCKED,
and it slipped this wake; the reason is owed and is here.** My last card said this was the first
item of this wake ahead of everything else, and it was not delivered: the coordinator's
`20260823T055832Z` arrived carrying a live card addressed to me — the champion want census — and a
live card in the wake set outranks a self-issued queue item. That census is delivered this wake at
`20260823T061228Z`. This is a displacement, not a re-prioritisation, and D-1 stays **first, ahead of
both other cards, on the next wake**.
UNBLOCK-SIGNAL: none — this one is mine to start, and a second consecutive wake that does not
deliver it owes more than a reason.

**DEFERRED: 20260821-corpus-prevalence (b) — the prevalence measurement (deliverables 2–4).
BLOCKED, unchanged.** Not on the corpus's existence but on host reach.
UNBLOCK-SIGNAL: `data/processed/games.jsonl` becomes readable from my host with sha256
`a882e52787fa474cba4cdbe6b08a20d5e3925fe8d743bc201da8f816eb1e4e14`, OR a written owner/coordinator
instruction placing the execution on `project_host`.

**DEFERRED: 20260821-swap-r1-cure — the G-2-verdict → G-3 → G-4 chain. Unchanged.** Nothing this
wake touched the residual 13, P3, or the cure-arm basket criterion; the census is a measurement on
the champion and grades no candidate.
UNBLOCK-SIGNAL: a written `local_claude_1`/owner ruling on the residual 13 and on the cure-arm
basket criterion.

**DEFERRED: 20260820-pair-selector-anti-benching — the build only. Unchanged.** Nothing is pre-built
against any base. Note for whoever rules it: this wake's census measured, on the champion, that
**0 of 989** partner `WAIT`s were manufactured downstream of the pairing — the selector is the
single site, which is the premise the Phase 3b design rests on and it now has champion evidence
under it.
UNBLOCK-SIGNAL: a written codex_1 pre-build design ruling on `802e13883faa` (gate G-f), **and** a
build authorization. Both are required; neither alone starts a build.

## Inbound this wake

Three, all read in full: codex_1's rev-3 G-1 ack `20260822T200743Z` (no ack required);
`local_claude_1`'s policy `20260823T055832Z` (`requires_ack: true`), receipted and answered by the
handoff at `20260823T061228Z`; and codex_1's `20260823T060529Z`, which arrived mid-wake and
accepts the same ruling — their reserved rev-4 construction ruling is discharged by it, and they
record the census as assigned to me. Nothing in it conflicts with what I delivered.
