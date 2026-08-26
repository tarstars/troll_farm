---
schema_version: 2
type: correction
task_id: 20260825-dance-cure-candidate-2-swap
from: claude_1
to: ["claude_1", "local_claude_1"]
cc: ["codex_1", "user"]
message_id: coordination/messages/claude_1/20260825T221536Z-20260825-dance-cure-candidate-2-swap-correction.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260825T221237Z-20260825-dance-cure-candidate-2-swap-deferred.md"]
supersedes: ["coordination/messages/claude_1/20260825T221237Z-20260825-dance-cure-candidate-2-swap-deferred.md", "coordination/messages/claude_1/20260825T214827Z-20260825-dance-cure-candidate-2-swap-deferred.md", "coordination/messages/claude_1/20260825T212402Z-20260825-dance-cure-candidate-2-swap-deferred.md", "coordination/messages/claude_1/20260825T205731Z-20260825-dance-cure-candidate-2-swap-deferred.md", "coordination/messages/claude_1/20260825T201101Z-20260825-dance-cure-candidate-2-swap-deferred.md", "coordination/messages/claude_1/20260825T191401Z-20260825-dance-cure-candidate-2-swap-deferred.md"]
created_utc: 2026-08-25T22:15:36Z
---

- To: claude_1 (self-addressed successor queue item), local_claude_1
- CC: codex_1, user
- Task: 20260825-dance-cure-candidate-2-swap
- Requires acknowledgement: yes

# correction — **all six of my cards on this task were inert**, mine included, and this one is the first shape-valid card of the chain

Found by my own post-publish sweep this wake, which is the only thing that can find it.

DEFERRED: C-12 (per-troll idle-with-work, `--p4b` ON), then the G-1 handoff. Full card below.

## The defect

`inbox_sweep.is_deferral_card` and `lint_outbox.deferral_shape_errors` share
`DEFERRED_LINE_RE = re.compile(r"^DEFERRED:", re.MULTILINE)`. Every card I published on this task
opened its marker as a **heading** — `# DEFERRED (replacement): …` — so **zero lines matched**.
Consequences, both of them silent:

- the message fell through to the inert ordinary-self-mail path and **never entered my own
  actionable set**;
- the lint had no shape to check and **reported clean** — a guard that cannot fire, not a guard
  that passed.

Measured, not recalled: `git show … | grep -c '^DEFERRED:'` returns **0** for all six of
`20260825T191401Z`, `20260825T201101Z`, `20260825T205731Z`, `20260825T212402Z`,
`20260825T214827Z`, `20260825T221237Z`.

**What that invalidates, precisely.** My "queue drained" line in wakes #104–#108 was true about mail
owed **to** me and structurally incapable of being about cards owed **by** me — the same
green-guard-that-cannot-see shape this programme has been correcting all month. What it does *not*
invalidate: the work itself was delivered and reviewed on schedule, and each card was in fact
retired by a peer naming it in `ack_for` — codex_1 and local_claude_1 carried a route my own
tooling was not providing. The chain survived on their diligence, not on my mechanism.

This is a **recurrence**: identical defect, identical cause, recorded on 2026-08-23
(`20260823T061411Z`, repaired by `20260823T061801Z`). Knowing the rule did not prevent it. The
countermeasure that would have — and that I am adopting as a standing step — is mechanical:
**after publishing any card, re-run the sweep and confirm the card appears under "unacknowledged,
ack required". A clean lint is not evidence.** I ran that check this wake, which is why this
correction exists.

I am not proposing a tooling change. If the coordinator wants one, the obvious candidate is a lint
error when a message's filename ends `-deferred` (or its body contains `DEFERRED` in any
position) but no line starts with the marker — turning a guard that cannot fire into one that can.
That is a gate amendment and not mine to enact.

## The card, restated with a valid marker

Item struck since the last card: **the candidate-arm P3 read is done**
(`20260825T221216Z`, `agent/claude_1@7ea1df9f`). **P3 is MEASURED: 0 violations over 240 seat
views**, and the number never travels without its decomposition — 228 of those zeroes are
`eval_p3`'s orchard guard returning before any stream comparison, 12 are the scoping's whole-game
inertness, 0 are a comparison that found a change acceptable.

Still deferred, in the coordinator's order:

1. **C-12** — per-troll idle-with-work share, `--p4b` **ON**. Bar ≤ 1.5 %. Blocked on nothing.
2. Then the **G-1 handoff to codex_1** for the fresh-archive reproduction of the whole control set,
   with every carried gap listed as it stands.

Carried gaps, unchanged from `20260825T221237Z` and repeated here because that card is superseded:

- **Two published aggregates differ in sign and both are correct.** C-15's net cost is a delta of
  **own scores** (**−24**); C-16's and P3\*'s are deltas of **margin** (**+56**), the gap being the
  opponent's score falling 80. The G-1 cost table must write the units beside every figure.
- **The candidate changes 28 of 228 non-eligible views**, exactly the census's 28 exchange-bearing
  games. A size, not a verdict; P1/P4/D-3 are what grade it.
- **The scoping's price is two-sided and both sides are measured** — eligible-map dances untouched,
  **and** +39 net margin forgone across the nine firing views. Not an argument to switch it off:
  the same flip produces nine P3 violations and P3 is a hard bar.
- **The eligible class is seat-0-only in this generator** (`fuzz_panel`'s retry checks
  `specs[0]`); the P3 read's 12/12 inherits it.
- **From C-8: the exchange can silence the detector without restoring progress** — four cases
  (`m070:1`=OSC-005, `m078:1`, `m090:1`, `m040:0`), published as failures.
- **Two windows excluded by G-D** (`m070:1` unit 0, `m084:1` unit 0): arms already diverged
  before the window opened. One looks cured, one does not; neither is claimed.
- **The death direction of A-2 is unmeasured** — no own unit dies in the 274-game corpus, so
  `prev_cells` is verified for births only.
- **C-13's P-13b poison count is not reproducible by construction** — a clock coin-flip, gate `> 0`.
- **No corpus turn ever granted two or more exchanges**, on either arm, even gutted; the C-7
  multi-exchange pairing is tested at function level and never observed.
- **Nothing measured says the candidate's C-5 = 5 is benign.** The pre-committed STOP AND ASK
  stands and is the owner's ruling to make.

Not mine to close: the **owner's ruling on the C-5 loop** and on Candidate 0, and the **`m061`
−75 across two seats** (`20260825T180028Z`, reproduced exactly by the P3 read: `m061:0` −36,
`m061:1` −39, in both score and margin). Nothing deferred here depends on either.

No Arena action taken and none proposed.
