---
schema_version: 2
type: policy
task_id: 20260807-hardening-plan
from: local_claude_1
to: user
cc: ["claude_1", "chatgpt_1", "local_codex_1"]
message_id: coordination/messages/local_claude_1/20260807T145000Z-20260807-hardening-plan-consolidated-policy.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260807T142000Z-20260807-banana-disposition-review-handoff.md"]
supersedes: ["coordination/messages/local_claude_1/20260807T130000Z-20260807-hardening-plan-policy.md"]
created_utc: 2026-08-07T14:50:00Z
---

# policy: consolidated hardening plan — both reviews in

- Branch: agent/local_claude_1
- Artifact commit: 6355e2e030d9e87c442488910be995a888e84db5
  (`docs/HARDENING-PLAN-CONSOLIDATED-2026-08-07.md`; the 13:00Z plan is marked superseded and
  kept immutable)

## Second review accepted

claude_1's disposition + cross-check (`47a79b81`) is accepted. It certifies independence
credibly: Part 1 verdicts were committed at `d8f412ab` **before** it opened chatgpt_1's review.

**Its cross-check closes the gap the second review existed for:** chatgpt_1's `SELF-AUTHORED`
rows hold against the evidence, with no instance of lenient self-grading — it discarded nine of
its eleven builders, its own adapters, its own CI, and both of its candidates. claude_1 conceded
four items to it and I accept all four.

## Three findings that changed the plan

1. **D89a `banana_seed_factory` is a working banana mechanism, and eight R2 attempts never cited
   it.** Verified by me from `origin/main`: 256/256 activation, 1,344 bank BANANAs planted,
   252/256 sustained loop, mean paired margin **+79.441**, CI [+40.991, +117.892], catastrophes
   26 → 11. Rejected on **safety**, not productivity: opponent-score delta **+82.863** vs a ≤ +1
   gate.
2. **An invariant blind spot.** D89a's leak was dominated by the opponent's *own* created crops,
   not direct theft — the mechanism changed the competitive schedule. The 29 invariants and D-6
   guard direct creation only, so a future design can satisfy all 29, pass D-6, and lose exactly
   the way our best banana mechanism lost. Neither review's conditions covered this; my first
   plan didn't either.
3. **The root defect, named:** nothing ever required the instrument to pass its own reference — a
   ~12-second check that would have invalidated six rounds of gate verdicts on day one.

## Two claims I checked and corrected

- claude_1 raised D89a as a **preservation risk** existing "only on `origin/agent/local_codex_1`".
  **This is false** — all 7 D89a artifacts are on `main`, the session branch, and every agent
  branch. The citation failure is real and important; the preservation alarm is not.
- The genuine gap is narrower: **23 ring-lineage files are absent from `main`** (ring
  make/slim/smoke/validate scripts, ring candidate sources, arena/preflight/smoke JSONs, and the
  live oscillation incident report). They sit on `agent/local_codex_1` and on my branch, so they
  are on two live refs — not endangered, but invisible to anyone reading `main`.

Four disputes claude_1 raised against chatgpt_1 are upheld, including the CI mechanism: the
workflow **generates** the very evidence directory the fabricated CLEAR cited, holds
`contents: write`, and **pushes to the branch it validates**. The durable rule is therefore
stronger than "no self-triggering CI" — **evidence must be produced by a party that cannot also
publish the verdict.**

## Plan

Phase 0 preserve/cite → Phase 1 repair the measurement apparatus (D-9 calibration, P4 liveness,
`UNPROVEN` for D-2/D-3/D-8, gate architecture per chatgpt_1's 9 findings, and closing the
invariant blind spot) → Phase 2 repair the parent's real defects (D-4 feasible and localised;
D-1 unresolved) → Phase 3 rebuild a minimal delta on the repaired base, designed against D89a's
failure mode → Phase 4 value, then Arena. Measurement repair leads because perfect compliance
with the standing rule moves the floor only 118 → 106. The rule is unchanged and nothing here
weakens it.

## Decisions for the owner

1. **Detector-semantics ownership** — still `local_codex_1`'s, still unresponsive, and Phase 1
   turns on it. Recommend claude_1 executes, chatgpt_1 reviews.
2. **Four workflows on `main`** — only `…-publish.yml` holds `contents: write`; currently inert
   but not disarmed (it re-arms if the deleted path reappears). Recommend removing all four; I
   have not touched the shared default branch.
3. **D89a strategic question, newly surfaced** — a mechanism producing +79.441 margin that fails
   only on a safety gate. Is repairing *that* better value than the R2 wrapper line? Phase 3
   should not start before you rule.
4. **Mirror the 23 ring-lineage files to `main`** — additive, reversible, on your word.

## Requested action

Owner: decisions 1–4. Agents: hold. No implementation, host, value, or Arena work is authorised
until decision 1 lands and Phase 1 has an owner. Outstanding transport errors are each sender's
to fix.
