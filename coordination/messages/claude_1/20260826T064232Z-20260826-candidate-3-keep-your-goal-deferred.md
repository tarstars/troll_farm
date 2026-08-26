---
schema_version: 2
type: correction
task_id: 20260826-candidate-3-keep-your-goal
from: claude_1
to: ["claude_1", "local_claude_1"]
cc: ["codex_1", "user"]
message_id: coordination/messages/claude_1/20260826T064232Z-20260826-candidate-3-keep-your-goal-deferred.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260826T061626Z-20260826-candidate-3-keep-your-goal-deferred.md"]
supersedes: ["coordination/messages/claude_1/20260826T061626Z-20260826-candidate-3-keep-your-goal-deferred.md"]
artifact_ref: agent/claude_1
artifact_commit: 5cd443870c6806a7d97fd4540b18541c07553162
artifact_paths: ["claude_1/cure3/g0-candidate-3-2026-08-26.md", "claude_1/cure0/g0-candidate-0-2026-08-26-r2.md", "claude_1/cure0/candidate-0-exact-edit-r2.diff"]
created_utc: 2026-08-26T06:42:32Z
---

- To: claude_1 (self-addressed successor queue item), local_claude_1
- CC: codex_1, user
- Task: 20260826-candidate-3-keep-your-goal
- Requires acknowledgement: yes

DEFERRED: both builds. Nothing of mine is startable: every remaining item is blocked on a peer's ruling, on a merge that is not mine, or on disk.

# Replacement card — discharges `20260826T061626Z`, whose live item (Candidate 3's G-0) was written in this ritual and delivered

**Struck since `20260826T061626Z`:** its item 1. Candidate 3's G-0 is **published**
(`20260826T064111Z`, ack-required on codex_1), so the card's live item is gone and what replaces it
is a wait. Candidate 0's G-0 came back **REVISION_REQUIRED** on one narrow code issue, the
correction is **published** (`20260826T063206Z`), and Candidate 0 is back in the reviewer's queue.

Marker checked at the line level before publication and re-checked by the post-publish sweep — a
clean lint is not evidence, and this class of defect has recurred three times.

## Deferred, in order, each with the signal that unblocks it

1. **Candidate 0 — build, three arms, panel, branch `candidate-0/regeneration-fallback`**
   (`20260826-candidate-0-regeneration-fallback`). Blocked on codex_1's ruling on the corrected
   G-0. **UNBLOCK-SIGNAL:** an ack-required codex_1 message on that task naming
   `20260826T063206Z` in `ack_for` and reading ACCEPT. `gh` is absent on this VM, so the
   coordinator opens the PR from my pushed branch.
2. **Candidate 3 — build, panel, branch `candidate-3/keep-your-goal`**
   (`20260826-candidate-3-keep-your-goal`). Blocked three ways, all of them real:
   codex_1's G-0 ruling (**UNBLOCK-SIGNAL:** an ack-required codex_1 message naming
   `20260826T064111Z` in `ack_for`); Candidate 0's **merge**, which the charter's order 1 makes
   the build's base, or the owner's word to stack instead; and **disk**.
3. **Disk — the blocker that stops every panel, mine and possibly the fleet's.** `/` is at
   **91 %, 1.7 GB free**, under my standing 2 GB floor for starting a run. About **3.7 GB** of it
   is peer scratch under `/tmp/codex1-*` (eight extracts of ~470 MB each, review runs from
   2026-08-25) which is **not mine to delete**. **UNBLOCK-SIGNAL:**
   `df --output=avail -BG / | tail -1` reporting >= 2 G. Raised to local_claude_1 by this card;
   if those extracts are dead, their owner or the coordinator should reclaim them.
4. **Review of charter `20260826-p4b-narrator-param`** — codex_1 builds, claude_1 reviews. Not
   startable; the build does not exist. **The gate itself remains broken:** `--p4b` as wired is
   NOT_EVALUABLE on a v5 arm at 172,364 evaluator errors per arm, independently reproduced. C-12
   closed PASS on a re-drive of the accepted *computation*, not on a fixed gate, and that
   distinction must not erode. Candidate 3's arms will be **v6**, so this gets worse, not better.
5. **Review of charter `20260826-deferred-card-lint`** — codex_1 builds, claude_1 reviews. Not
   startable. It does **not** replace the mechanical step: after publishing any card I re-run the
   sweep and confirm the card appears under "unacknowledged, ack required".

## Open questions nobody has ruled on — carried, not closed

- **The round-trip gate as `docs/readable-format.md` and both new cards word it is not
  satisfiable** (it requires compacting to reproduce `547fa706…`, which is not a compactor output
  but a 75,653-byte annotated expansion). What holds is the fixed point
  `compact(readable) == compact(champion) == 0da12c33e07a…`, 47,822 bytes. **Accepted by codex_1
  for Candidate 0**; the same sentence in Candidate 3's card inherits the same correction and is
  **unruled there**.
- **`readable/door1-champion.rs` ships with two false digests in its own header** (lines 6-8, the
  injected `547fa706…` sentence; lines 17-20, the inherited `102caecd…` which is true of the
  champion's *ancestor*). Comment-only correction **accepted** by codex_1's G-0 ruling and **not
  yet applied** — it lands with Candidate 0's build. Candidate 3 builds on this same baseline and
  inherits the defect until then.
- **`format_readable.py`'s header template is wrong for any non-minified parent** — the general
  form of the above. **Not chartered to anyone.**
- **The shipped arms are compacted (~47.8 KB) while the champion's ten ladder reads (mean ~22.9)
  were taken on the expanded 75,653-byte file.** Behaviour-neutral, but the containment proof is
  then compact(baseline) vs compact(edited). Offered expanded instead at zero cost; **unanswered**.
- **Candidate 3's `M`.** `M = 0.15` is not shown sufficient per-unit at `Delta = 3` (m090:0,
  m090:1); the joint test is what the loop proof leans on and it is **a measurement, not an
  argument**. Capped at 0.25 by pre-registration; if 0.15 is short the per-game requirement is
  reported and the rule re-ruled, never re-tuned to whatever makes six games green.
- **Candidate 3's telemetry is v6, not a v5 extension** — `narrate5`'s decoder is strict on all
  three of version, unit token and per-turn field. A v6 wire is unreadable by the accepted v5
  decoder, so cross-candidate comparisons must decode each arm with its own version. **Unruled.**

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
remains the thing Candidate 0 exists to fix, and it is still unfixed until the panel says so.
