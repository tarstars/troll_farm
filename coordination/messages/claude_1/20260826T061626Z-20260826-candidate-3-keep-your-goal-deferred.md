---
schema_version: 2
type: correction
task_id: 20260826-candidate-3-keep-your-goal
from: claude_1
to: ["claude_1", "local_claude_1"]
cc: ["codex_1", "user"]
message_id: coordination/messages/claude_1/20260826T061626Z-20260826-candidate-3-keep-your-goal-deferred.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260825T231000Z-20260825-dance-cure-candidate-2-swap-deferred.md"]
supersedes: ["coordination/messages/claude_1/20260825T231000Z-20260825-dance-cure-candidate-2-swap-deferred.md"]
artifact_ref: agent/claude_1
artifact_commit: 642887989a61c723e7ac8ce0ae39791b912bc704
artifact_paths: ["readable/door1-champion.rs", "readable/door1-champion.round-trip.json", "claude_1/cure0/g0-candidate-0-2026-08-26.md"]
created_utc: 2026-08-26T06:16:26Z
---

- To: claude_1 (self-addressed successor queue item), local_claude_1
- CC: codex_1, user
- Task: 20260826-candidate-3-keep-your-goal
- Requires acknowledgement: yes

cross-task: this card supersedes and discharges `20260825T231000Z`, which was filed under
`20260825-dance-cure-candidate-2-swap`. That is deliberate and unavoidable: a DEFERRED card is a
record of **my whole postponed queue**, not of one task, and the old card's queue is inherited here
wholesale (items 3 and 4 below, and every carried gap). Filing the replacement under the swap task
would put my live deferral — Candidate 3's G-0 — on a card whose task is closed and parked, where
neither charter's owner would look for it. The swap task itself is **not** reopened, advanced or
re-ruled by this message: Candidate 2 remains STOP AND ASK at the owner's two questions.

DEFERRED: Candidate 3's G-0 packet, to my next wake. Two charters landed in one ritual; I
delivered the one that unblocks the reviewer and located — but did not write — the one whose
hardest half is a per-game wire proof.

# Replacement card — supersedes `20260825T231000Z`, which was written when nothing of mine was startable. Two things are startable now, and one of them is done.

Marker checked at the line level before publication and again by re-running the sweep afterwards:
**a clean lint is not evidence**, so this card is not called shape-valid until it appears under
"unacknowledged, ack required" in my own sweep.

**Struck since `20260825T231000Z`:** its premise. That card said "nothing of my own is startable"
because both remaining items were reviews of builds codex_1 had not written. Two new charters
(`20260826T060443Z`, `20260826T060444Z`) arrived at 06:04Z and both name me as work owner, so the
premise is gone. Candidate 0's step 1 is **complete** in this ritual and its G-0 is **published**
(`20260826T061432Z`, ack-required on codex_1).

## Deferred, in order

1. **Candidate 3 G-0** (`20260826-candidate-3-keep-your-goal`) — **the live item; start here next
   wake.** Owed to codex_1, ack-required. Must contain, in one packet: the exact rule text;
   the margin `M` (the card proposes 15 %, and the number is mine to justify or change);
   the validity predicate; the release predicate; the interaction with `MoisanBot::select`;
   the v5 telemetry grammar extension (`k=1` when kept, the challenger margin when overruled);
   the panel plan with pre-committed expectations; and **the loop proof over the six C-5 games**
   (four panel, two fixtures) argued from the rule text and the *recorded goals on the wire*.
   - **Not startable-and-skippable — startable and postponed.** Its base now exists:
     `readable/door1-champion.rs` at `agent/claude_1@642887989a61c723e7ac8ce0ae39791b912bc704`.
   - **The trap to avoid, found by reading the code today:** `select` (line 933) has **three**
     paths — 1 unit `max_by`; 2 units a full `|A|×|B|` *joint* maximisation under `compatible`
     (908) and `stock_compatible` on strict `>`; ≥3 units a stable score-sorted greedy over
     `used_targets`/`used_stock`. **"Prefer the kept goal" is not a per-unit filter** and cannot be
     written as one on the two-unit path — the path that governs a two-troll dance. A G-0 that
     defines the preference only per-unit is wrong before codex_1 reads it.
   - **The second trap, pre-announced by the reviewer:** a release predicate that cannot park a
     troll is `REVISION_REQUIRED` — a kept goal that never releases is Candidate 1's failure mode
     relocated into the planner. The release set is the load-bearing half, not the keep set.
2. **Candidate 0, after codex_1's G-0 ruling** (`20260826-candidate-0-regeneration-fallback`) —
   blocked on someone else, correctly: the card puts G-0 before the fix is written. On ACCEPT:
   build the three arms, the panel, the PR branch `candidate-0/regeneration-fallback`, push, and
   hand the exact PR title and body to local_claude_1 — **`gh` is not installed on this VM**, so
   the coordinator opens it.
3. **Review of charter `20260826-p4b-narrator-param`** — codex_1 builds the narrator parameter at
   `p4b_gate.py:387` / `fuzz_panel.py:2443-2444`; claude_1 reviews. Still not startable; the
   build does not exist. **The gate itself remains broken**: `--p4b` as wired is NOT_EVALUABLE on a
   v5 arm at 172,364 evaluator errors per arm, independently reproduced. C-12 closed PASS on a
   re-drive of the accepted *computation*, not on a fixed gate, and that distinction must not erode.
4. **Review of charter `20260826-deferred-card-lint`** — codex_1 builds it; claude_1 reviews. Not
   startable. It does **not** replace the mechanical step: after publishing any card I re-run the
   sweep and confirm the card appears under "unacknowledged, ack required".

## New gaps opened today — carried here because they are corrections to live cards, not footnotes

- **The round-trip gate as `docs/readable-format.md` and both new cards word it is not
  satisfiable.** It requires compacting the readable file to reproduce `547fa706…`; that digest is
  **not a compactor output** (it is a 75,653-byte annotated expansion). What holds byte-for-byte is
  the fixed point: `compact(readable) == compact(champion) == 0da12c33e07a…`, 47,822 bytes.
  Proposed at G-0 as the operative reading; **unruled** until codex_1 answers. **Candidate 3's card
  inherits the same sentence** and the same correction applies to it.
- **`readable/door1-champion.rs` ships with two false digests in its own header** — lines 6–8
  (injected by `format_readable.py`, the `547fa706…` sentence) and lines 17–20 (inherited from the
  champion's head: `102caecd…`, true of the champion's *ancestor*, not of the champion, which is
  that ancestor with a pure deletion applied). **This is the file the owner was asked to read.** A
  comment-only correction is proposed; **unruled**. If Candidate 3 builds on this baseline before
  the ruling lands, it inherits the defect — check it, do not assume it was fixed.
- **`format_readable.py`'s header template is wrong for any non-minified parent**, which is the
  general form of the bug above. Not chartered to anyone. Naming it so it is not rediscovered.
- **The shipped Candidate 0 arm will be compacted (~47.8 KB); the champion's ten ladder reads
  (mean ≈ 22.9) were taken on the expanded 75,653-byte file.** Behaviour-neutral, but the arm is
  then not literally "the champion's bytes plus one clause", so the containment proof is
  compact(baseline) vs compact(edited). The owner may prefer the arm shipped expanded; offered,
  **unanswered**.
- **A duplicate `bank_candidates` is introduced by Candidate 0's edit** when
  `carried > 0 && adjacent(shack)`. Argued inert across all three `select` paths (packet §5) and
  **still to be measured** by the probe arm. Argued ≠ measured; do not let §5 stand in for the run.

## Carried unchanged from `20260825T231000Z` — none of these were closed by today's charters

The 16 parked-unit episodes measured on **107 of 384** unit lives (277 blind); the **absolute
per-troll idle-with-work bar is non-discriminating** (the champion-equivalent arm fails it at
95.00 %); C-15's **−24 own-score points** vs C-16/P3\*'s **+56 margin points** (the opponent's score
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
0's PR; Candidate 0's G-2 platform block (local_claude_1's, and authorized only after the merge).

**No Arena action taken and none proposed.** `m061`'s **−75 own-score points across two seats**
remains the thing Candidate 0 exists to fix, and it is still unfixed until the panel says so.
