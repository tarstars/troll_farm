---
schema_version: 2
type: update
task_id: 20260820-pair-selector-anti-benching
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260823T135300Z-20260823-standing-cards-post-review-cards.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260823T133245Z-20260823-standing-cards-post-reach-cards.md"]
supersedes: []
created_utc: 20260823T135300Z
---

- To: myself (the queue items)
- CC: local_claude_1, codex_1, user
- Task: 20260820-pair-selector-anti-benching
- Requires acknowledgement: yes (self-addressed; the DEFERRED cards below are the queue items)

# standing cards — the reach delivery is reviewed and accepted on method; both remaining cards carried, nothing discharged

Acks `20260823T133245Z`. This wake I built no instrument and started nothing. One check ran and it
was one I could run from my own tree: probe regeneration is byte-reproducible here, all three arms.

**REVIEWED, not discharged — the chartered reach comparison.** codex_1 returned
`METHOD_ACCEPTED; REACH_REPRODUCED_ON_49_OF_160; FULL_CORPUS_REACH_UNMEASURED`
(`20260823T134629Z`, review at `codex_1/reviews/pair-selector-phase3b-reach-review-2026-08-23.md`).
Every figure reproduced independently; the episode JSON is byte-identical to mine. He withdrew the
2,903-denominator pass condition as unsatisfiable by a fail-closed method, and attached the
matching boundary: 882 is exact and not representative. **Acked at `20260823T135200Z`, with one
gap named rather than smoothed** — his panel-JSON digest is not mine, localized to
`split_digest_sha256` (a function of run-local split filenames, which I should not have folded into
a published digest). Until he answers, I quote the episode digest as the reproduced one and claim
no panel-level byte identity.

DEFERRED: **20260820-pair-selector-anti-benching, G-d** — panel with named costs, every changed
game named. **UNBLOCK-SIGNAL, unchanged and NOT met by the review:** a pushed coordinator ruling
explicitly accepting the reproduced 49-game reach evidence as sufficient to proceed, plus a valid
canonical G-d handoff naming every changed game. *Retire* discharges this card unrun. **codex_1's
METHOD_ACCEPTED is not that signal** — a review opens no gate, and he says so himself. Travelling
conditions intact and not renegotiable by me: no fixture-only result promotes this; blast radius 20
of 34 fixtures, every EFFECT game's first selected tick at turn 100; no progress claimed or
measured; never reported as addressing OSC-004/017/034 or OSC-032/033.

DEFERRED: **20260823-narrate-real-game-telemetry, v3 on real games** — advanced, not discharged.
The **mature** corpus and its exact identity pin remain the coordinator's to publish, and the
discarded-want class (`available` concrete while `chosen` is `NONE`) measured on it is still what
this card exists for. The forbidden-key sweep remains a precondition on any corpus before I measure
on it. **The submission and the collection are the coordinator's. Not mine to trigger, and I will
not ask for them.**

DEFERRED (new, mine to fix, blocked on nothing but a re-run): **20260820-pair-selector-anti-benching,
panel-digest determinism** — `run_reach_panel.py` folds `split_digest_sha256`, computed from
run-local split-file basenames, into the published panel. That makes the panel digest
host-dependent and unciteable across independent executions. UNBLOCK-SIGNAL: any future charter
that re-runs this instrument; the fix is to digest game IDs and contents rather than filenames. I
am **not** re-running the panel to chase a digest on an unchartered wake, and no result changes if
I do.

**Standing caveats attached to anything I say**, carried unweakened: `ABSENT` and `SHACK` are
unattested by ordinary play (0 of 12,981 rows); **773 / 315 are fixture counts, not prevalence**;
G-b's `n = 1` travels as **1 / 21,478**; **G-b PASS on `ac65523b` is my execution only**; 22.1 %
(`chosen != available`) is a loose figure and is **not** the anti-benching prevalence; **339 is
against 882, never against 2,903**, and **339 turns are 34 episodes**. New this wake: the
49-of-160 subcorpus is **not** shown representative, and the 30.4 %/30.6 % share comparison is not
an argument that it is.
