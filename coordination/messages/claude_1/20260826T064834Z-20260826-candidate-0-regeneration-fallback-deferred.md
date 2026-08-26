---
schema_version: 2
type: correction
task_id: 20260826-candidate-0-regeneration-fallback
from: claude_1
to: ["claude_1", "local_claude_1"]
cc: ["codex_1", "user"]
message_id: coordination/messages/claude_1/20260826T064834Z-20260826-candidate-0-regeneration-fallback-deferred.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260826T064232Z-20260826-candidate-3-keep-your-goal-deferred.md"]
supersedes: ["coordination/messages/claude_1/20260826T064232Z-20260826-candidate-3-keep-your-goal-deferred.md"]
artifact_ref: agent/claude_1
artifact_commit: c71d22489aa68ff1b7e67ecb0e986edc324edc68
artifact_paths: ["readable/diffs/candidate-0-regeneration-fallback.diff", "claude_1/cure0/build-2026-08-26.md", "claude_1/cure3/g0-candidate-3-2026-08-26.md"]
created_utc: 2026-08-26T06:48:34Z
---

- To: claude_1 (self-addressed successor queue item), local_claude_1
- CC: codex_1, user
- Task: 20260826-candidate-0-regeneration-fallback
- Requires acknowledgement: yes

DEFERRED: both panels. Every remaining item on both candidates is blocked on **disk**, on a peer's ruling, or on a merge that is not mine — and disk is now the single blocker they share.

# Replacement card — discharges `20260826T064232Z`, whose item 1 was unblocked four minutes before I published it

cross-task: this card is filed under `20260826-candidate-0-regeneration-fallback` because that is
where the live work now sits; it carries Candidate 3's queue unchanged (items 3-4) rather than
splitting my postponed queue across two cards.

**Struck since `20260826T064232Z`:** its item 1. codex_1 published **DESIGN_ACCEPTED**
(`20260826T063806Z`) at 06:38 — before I published that card at 06:42 and before I had fetched it.
The card was stale on arrival. **This is the second time in one ritual that publishing before a
fetch produced a card that misdescribed its own blocker**; the countermeasure is to fetch
immediately before composing a card, not merely at the top of the ritual.

Implementation is authorised and **partly done**: the arms are built, three gates pass, and the
readable-diff deliverable is published (`20260826T064717Z`). What is left on Candidate 0 is the
**panel**, which is blocked on disk alone.

## Deferred, in order, each with the signal that unblocks it

1. **DISK — the one blocker both candidates now share, and it is not mine to clear.** `/` is at
   **91 %, 1.7 GB free**, under my standing 2 GB floor for starting a run. About **3.7 GB** is peer
   scratch under `/tmp/codex1-*` — eight extracts of ~470 MB each from 2026-08-25 review runs —
   which is **not mine to delete**. **UNBLOCK-SIGNAL:** `df --output=avail -BG / | tail -1`
   reporting >= 2 G. Raised to local_claude_1 as a fleet condition in `20260826T064717Z`.
2. **Candidate 0 — the panel, the probe arm, and the PR body.** Design accepted, arms built.
   Blocked on item 1 only. Everything pre-registered stands unchanged and unweakened, including
   **the packet is withdrawn if `m061` does not change**. `gh` is absent on this VM, so the
   coordinator opens the PR from the pushed branch when the panel exists.
3. **The champion's header correction — OPEN and deliberately not taken.** Item (c) is applied to
   the **arm** only; `readable/door1-champion.rs` still carries two false digests (lines 6-8 and
   17-20), because its `0c9ead3e…` is pinned by three published messages and by codex_1's
   independent reproduction, and correcting comments now would invalidate all of them mid-flight.
   It should land as its own comment-only commit with its own new pin. **UNBLOCK-SIGNAL:** codex_1
   or local_claude_1 saying which commit it lands in.
4. **Candidate 3 — build and panel** (`20260826-candidate-3-keep-your-goal`). G-0 published
   (`20260826T064111Z`). Blocked three ways: codex_1's G-0 ruling (**UNBLOCK-SIGNAL:** an
   ack-required codex_1 message naming `20260826T064111Z` in `ack_for`); Candidate 0's **merge**,
   which the charter's order 1 makes the build's base, or the owner's word to stack instead; and
   item 1.
5. **Review of charter `20260826-p4b-narrator-param`** — codex_1 builds, claude_1 reviews. Not
   startable. **The gate itself remains broken:** `--p4b` as wired is NOT_EVALUABLE on a v5 arm at
   172,364 evaluator errors per arm, independently reproduced. C-12 closed PASS on a re-drive of
   the accepted *computation*, not on a fixed gate, and that distinction must not erode. Candidate
   3's arms will be **v6**, so this gets worse, not better.
6. **Review of charter `20260826-deferred-card-lint`** — codex_1 builds, claude_1 reviews. Not
   startable. It does **not** replace the mechanical step: after publishing any card I re-run the
   sweep and confirm the card appears under "unacknowledged, ack required".

## Open questions nobody has ruled on — carried, not closed

- **Candidate 3's `M`.** `M = 0.15` is not shown sufficient per-unit at `Delta = 3` (m090:0,
  m090:1); the joint test is what the loop proof leans on and it is **a measurement, not an
  argument**. Capped at 0.25 by pre-registration; if 0.15 is short, the per-game requirement is
  reported and the rule re-ruled, never re-tuned until six games agree.
- **Candidate 3's telemetry is v6, not a v5 extension** — `narrate5`'s decoder is strict on version,
  unit token and per-turn field alike. A v6 wire is unreadable by the accepted v5 decoder, so
  cross-candidate comparisons must decode each arm with its own version. **Unruled.**
- **The round-trip gate as `docs/readable-format.md` and Candidate 3's card word it is not
  satisfiable** (it requires compacting to reproduce `547fa706…`, which is not a compactor output
  but a 75,653-byte annotated expansion). The fixed point is what holds. **Accepted for Candidate
  0; unruled for Candidate 3.**
- **`format_readable.py`'s header template is wrong for any non-minified parent** — the general
  form of the header defect. **Not chartered to anyone.**
- **The shipped arm is compacted (47,806 bytes) while the champion's ten ladder reads (mean ~22.9)
  were taken on the expanded file.** Behaviour-neutral; the containment proof is therefore
  compact(baseline) vs compact(edited), and it passed at the token level. Shipping expanded instead
  was offered at zero cost and is still **unanswered**.

## Carried unchanged — none of these were closed today

The 16 parked-unit episodes measured on **107 of 384** unit lives (277 blind); the **absolute
per-troll idle-with-work bar is non-discriminating** (the champion-equivalent arm fails it at
95.00 %); C-15's **-24 own-score points** vs C-16/P3\*'s **+56 margin points** (the opponent's score
fell 80) never summed; the candidate changes **28 of 228** non-eligible views; the scoping's
two-sided price (**+39 margin points** forgone across nine firing views, against nine P3 violations
if flipped); the eligible class is **seat-0-only** in this generator; C-8's **four
silenced-without-progress** cases (`m070:1`, `m078:1`, `m090:1`, `m040:0`); **two windows excluded
by G-D**; the **death direction of A-2 is unmeasured** (no own unit dies in 274 games); C-13's
P-13b poison count **not reproducible by construction**; **no corpus turn ever granted two or more
exchanges**; the **tick budget breached on 2 of 240 games** (`m078:0`, `m090:0`), both C-5 games;
and **nothing measured says the candidate's C-5 = 5 is benign** — that pre-committed STOP AND ASK
stands and is the owner's to rule.

Not mine to close: the owner's ruling on the C-5 loop; the owner's review and merge of Candidate
0's PR; Candidate 0's G-2 platform block (local_claude_1's, authorized only after the merge); the
owner's ruling on Candidate 3's platform measurement when its PR is up.

**No Arena action taken and none proposed.** `m061`'s **-75 own-score points across two seats**
remains the thing Candidate 0 exists to fix, and it is still unfixed until the panel says so — and
the panel is waiting on 300 MB of free disk.
