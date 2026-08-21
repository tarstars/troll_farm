---
schema_version: 2
type: handoff
task_id: 20260820-pair-selector-anti-benching
from: claude_1
to: ["codex_1"]
cc: ["local_claude_1", "user"]
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260820T194842Z-20260820-pair-selector-phase-two-build-card.md"]
supersedes: []
message_id: coordination/messages/claude_1/20260820T201729Z-20260820-pair-selector-phase2-dual-base-handoff.md
created_utc: 2026-08-20T20:17:29Z
artifact_ref: agent/claude_1
artifact_commit: 5409ba13c04d87f81dbad4b13138986da2942898
artifact_paths: ["claude_1/picker2/phase2-package-2026-08-20.md", "claude_1/picker2/candidate-cureC-p1p2.rs", "claude_1/picker2/candidate-door1-p1p2.rs", "claude_1/picker2/make_pair_selector_candidate.py", "claude_1/picker2/run_gates.py", "claude_1/picker2/gate1-bench-2026-08-20.json", "claude_1/picker2/decomposition-cureC-2026-08-20.json", "claude_1/picker2/decomposition-door1-2026-08-20.json", "claude_1/picker2/named-changes-2026-08-20.json"]
---

- To: codex_1 (UNIFIED review of both packages as ONE unit, per the card)
- CC: local_claude_1, user
- Task: 20260820-pair-selector-anti-benching, Phase 2
- Requires acknowledgement: yes
- Acknowledges: the phase-two build card (delivery, not deferral)

# handoff: P1+P2 built on BOTH bases, full battery run — and the bench is gone while the situations mostly are not cured

Report: `claude_1/picker2/phase2-package-2026-08-20.md`. Whole battery replays with one
command: `python3 claude_1/picker2/run_gates.py` (add `--skip-panels` to reuse the committed
panels). Every step's exit status is recorded in `gate-battery-run-2026-08-20.json`: **19 of 19
OK**, the four `exit=1`s being fuzz_panel's BLOCK verdicts, which are results and are named as
such rather than swallowed.

## Read this before the numbers

**The bench is gone; the situations are mostly not cured.** Every ruled fixture that is red on
its base goes from benched to **0 benched turns** and the D-1 detector falls silent — but on the
standing grader (*silent AND progress restored*) three of four cure-C fixtures land in
**detector-quiet-but-still-stalled**, which is precisely what that rule exists to refuse. I am
not presenting that as a cure and I would rather you reject it than have it read as one.

## What you are reviewing

One generator, two subjects. Diff body byte-identical across bases (`af8f710ce50336e3…`), and
the **patched selection regions** byte-identical too — step 0 measured them identical before the
patch; they are identical after. Builder refuses an un-allowlisted digest, a non-unique anchor,
or any edit reaching outside the selection regions. `select()` gains one input (`unit_cells`);
the >2-unit greedy fallback is deliberately untouched and named as such.

| gate | cure-C base | door-1 base |
|---|---|---|
| benched on ruled fixtures | 12/187/194/94 → **0/0/0/0** | 0*/187/194/0* → 0/**0**/**0**/0 |
| all-34 FIXED | 3 → **4** (+OSC-034) | 8 → 8 |
| panel blocking (240, matched floor) | 53 → **33** | 43 → **35** |
| de-novo / healed, keyed (map_id, seat) | **0** / 20 | **0** / 8 |
| latency p95 delta | +0.0020 ms | +0.0616 ms (budget 50 ms) |
| process-count parity | 8160 field comparisons IDENTICAL | — |

\* OSC-004 and OSC-034 are **not benched at all** on the door-1 base — the forecast hunk already
employs the unit there. Redness is measured per base and never inherited; inheriting cure-C's
would have manufactured two failures against a fixture with nothing to repair.

## The three places I most want you to attack

1. **The 0 de-novo.** It carries a liveness control — swap the arms and the bucket refills with
   exactly the healed keys, 20 of 20 and 8 of 8 — but a control I wrote for a result I wanted is
   exactly the thing that should be checked by someone else.
2. **P1 liveness.** `p1drop=true` is observed on every candidate arm (3/5/3/1 on cure-C,
   3/9/3/2 on door-1), tapped from the selector's own `self_blocked` call hoisted into a
   `let` that the original `if` reads. If you think the probe's pair rows are not the
   selector's own verdicts, that is the claim to break.
3. **P3 on `m004` seat 0, door-1 base only.** P3 asserts the candidate's command stream is
   byte-equal to the parent's on orchard-eligible seat views; P1+P2 is by design a command
   change, so **any** real selector edit can reach it, and cure-C passing 12 of 12 is luck.
   Whether P3 is applicable to an intentional selector change is a **ruling**, and it is not
   mine. Also named: `m021` seat 1 gains property P4 and an `r5-horizon` flag on **both**
   bases, inside a game that already blocks under the floor.

## Not claimed

Neither candidate cures the benching situations (1 of 4 on cure-C, 0 added on door-1). The 235
non-deadlock benched turns from Phase 1 remain out of scope and are named, not hoped away.
Neither base is ranked here — the title is the night tree's verdict and the queue slot is the
owner's D3 ruling. **No Arena action was taken.**

## For the owner, in plain words

Both repairs are built and tested to the full standard, on both possible champions, and the
package is on the shelf as you asked. The honest headline is half a success: the trolls stop
standing in each other's way — the picker no longer orders one to walk onto a square while
telling the occupant to stay put — and across 240 games each version blocks meaningfully less
often with **nothing new broken**. But on the strict per-situation bar, only one of the four
frozen cases actually starts making progress again; the rest just stop tripping the alarm. That
is a smaller win than the fixture list suggests, and you should see it as one before deciding
which candidate, if either, gets the queue slot.
