# 20260826-candidate-3-keep-your-goal: Candidate 3 — "a troll keeps its goal"; delivered as a GitHub PR with the patch visible

- Status: **CHARTER CORRECTED 2026-08-26T08:10Z (coordinator) after G-0 r3 BLOCK-pending-correction
  (codex_1 `20260826T074444Z`).** The measurement is accepted: on the six loop games the challenger's
  advantage `rho` rises monotonically as the shared tree nears completion (0.02 → 0.27), so **no
  fixed margin `M` can prove "no second exchange"** — the fixed-margin form is falsified, not
  mis-tuned. **Corrected rule form: absolute keep.** A troll keeps its chosen goal until it is
  **done** (progress at it), **gone** (the plant/bank/cell no longer exists), or **impossible**
  (no path even with the teammate's cell free — the swap handles a standing teammate); **no
  challenger overrules a valid kept goal** — the "clearly better by a margin" clause is removed.
  The loop proof is then immediate (a valid kept goal never changes, so clause 6 fails for the
  reverse exchange). Also: a **kept plan** — a `PICK` taken to plant is kept until the `PLANT`
  happens or becomes impossible (Candidate 0's PICK↔DROP two-cycle is the same disease). **Base:
  the champion readable `readable/door1-champion.rs`** (Candidate 0 is closed). Telemetry v6 with
  mutual refusal against v4/v5 (its own decoder). Round-trip gate = canonical-compaction identity.
  G-0 r4 requested: the exact release predicates (each with its observable), the pair-selector
  interaction, the plan-keeping case, the panel expectations (MIXED windows ↓; parked-troll and
  idle share not worse — the risk of the no-margin form; score in units), determinism.
  Original status follows.
- Status at charter: **OPEN — CHARTERED 2026-08-26T06:05Z by owner ruling** (coordinator session ~06:00Z,
  the coordinator's transcription: *"the same for candidate 3 — prepare PR in which code patch is
  visible"*, after the owner's page recommended Candidate 3 = "a troll keeps its goal" as the
  remedy for the swap's loop).
- Record owner: local_claude_1 · Work owner: **claude_1** · Reviewer: **codex_1** (G-0
  definitions before any code; the diff and the panel from a fresh archive) · PR reviewer and
  merger: **the owner** · Arena: nothing authorized by this charter.
- Area: the planner's goal selection. Base: **the merged Candidate 0 readable source**
  (`readable/door1-champion.rs` after `20260826-candidate-0-regeneration-fallback`'s PR is
  merged); until then, design and G-0 proceed on the champion's readable baseline.
- Inputs: `claude_1/cure2/loop-anatomy-2026-08-25.md` (the goals stay with the cells; the
  re-pick after an exchange), `local_claude_1/dance-cure-proposal-2026-08-24.md` §2 B (target
  stickiness), the P3 jitter reading in `local_claude_1/dance-mechanism-map-2026-08-25.md`, the
  MIXED-target windows in the attribution (`claude_1/dance1/`), Candidate 2's G-1 packet
  (`claude_1/cure2/g1-packet-2026-08-25.md`) for the loop games and the C-5 rows.
- Branch: `candidate-3/keep-your-goal` (a PR branch, stacked on Candidate 0's branch until that
  merges, then rebased onto `main`); work mirrored on `agent/claude_1`.
- Progress lease: 15 minutes without concrete evidence.
- Created UTC: 2026-08-26T06:05:00Z · Last updated UTC: 2026-08-26T06:05:00Z

## THE QUESTION (owner's, plain words)

Today the bot re-picks every troll's goal from scratch every turn. That is why two trolls that
change places swap their goals too and swap back, and why a troll's stated goal flips inside a
dance. **Rule: once a troll has chosen a goal, it keeps it until the goal is done or gone, or a
clearly better one appears.** Show the change as a pull request I can read; prove on the panel
what it changes; then the swap is re-run on top of it.

## The rule — the spine; G-0 fixes the exact text

Per troll, one remembered goal (`kept_goal[id]`: the `Target` and the turn it was chosen):

1. **Keep** — at selection, if the troll's kept goal is still *valid* (the plant/bank/cell still
   exists and is still a legal candidate for that troll this turn) it is preferred over the
   freshly scored best unless the challenger beats it by a **margin `M`** (proposed 15 % of the
   kept goal's current score; fixed at G-0).
2. **Release** — the kept goal is dropped on: progress on it (the accepted `progress_event`
   predicate: chopped / picked / dropped / planted / banked at it), the goal disappearing (tree
   felled, plant gone), the troll reaching it and completing its action, or the troll dying.
3. **The pair selector** (`select`, the joint pairing that scores two trolls' candidates
   together) sees the kept goal as the troll's candidate with its *kept* preference applied —
   so after an exchange the mover still wants its own tree and the displaced worker still wants
   its own square (which the swap rule refuses to swap for, by clause 6). **No lock on the
   swap.** No change to the resolver.
4. Telemetry: the instrument arm prints, per unit, whether the goal was kept (`k=1`) or freshly
   picked, and the challenger margin when a kept goal was overruled (v5 grammar extension, fixed
   at G-0).

**Proof obligation for the loop (G-0):** on the six loop games of Candidate 2's C-5 (four panel,
two fixtures), show from the wire that with goals kept, after the first exchange the mover's goal
stays its own tree and the displaced worker's goal stays its own square, so the reverse exchange's
clause 6 (`target ≠ landing`) fails and no second exchange can fire — argued from the rule text
and the recorded goals, then **measured** at G-1 when Candidate 2 is re-run on top.

## Delivery — the readable diff file (owner amendment 06:10Z: "not exactly PRs — I want to see diffs in files"; a PR is optional)

**The deliverable of record is `readable/diffs/candidate-3-keep-your-goal.diff`** — a unified diff
of the base readable source (Candidate 0's, once merged; else `readable/door1-champion.rs`) → the
readable Candidate 3 source, beside its round-trip report and the regenerated compact arm;
integrated onto `main` by the coordinator after codex_1's review, readable on GitHub at
`https://github.com/tarstars/troll_farm/blob/main/readable/diffs/candidate-3-keep-your-goal.diff`.

### The original PR shape (kept as the description of the parts)

Commit 1 (only if Candidate 0's baseline is not yet on `main`): the readable baseline. Commit 2:
the rule on `readable/door1-champion.rs` (the diff the owner reads), the regenerated compact arm
`cgauto/submissions/candidate-3-keep-your-goal.rs` + manifest, the panel results, the report. PR
against `main` (stacked on Candidate 0's PR until it merges). **The owner reviews and merges.**

## Gates

- **G-0 (codex_1, ack-required):** the exact rule text, `M`, the validity and release
  predicates, the interaction with the pair selector, the telemetry, the loop proof, the panel
  plan and pre-committed expectations (which games may change and why).
- **G-1 panel (claude_1; codex_1 reproduces):** rule-off arm byte-identical to its base; rule-on
  vs base on 240 + 34: D-1 / D-3 / P3 / P4 / P4b not worse, every changed game named with its
  delta in own-score points; **the MIXED-target windows** of the attribution's kind counted before
  and after (the rule's own target); the score table with units; determinism.
- **G-2 — Candidate 2 re-run on top** (a separate handoff on Candidate 2's card): the swap arm
  rebuilt on Candidate 3's source, C-5 expected **0** on the six loop games, C-8's four
  silenced-without-progress cases re-read, `m061` re-read on top of Candidate 0.
- Platform measurement: **not authorized by this charter** — the owner rules after the PR.

## Deliverables

`claude_1/cure3/definitions-g0-2026-08-2x.md`; the PR; `claude_1/cure3/` (arms, probe, panel
results, report); `codex_1/reviews/candidate-3-*.md`.

## Do not touch

`rust/src/bin/yamo_orchard_live.rs`; the champion file; the resolver (`hold_pass` and its
callers) — Candidate 3 is a planner change only; `data/raw/games/`; the resident; the cron.

## Not in scope

The swap itself (Candidate 2); score smoothing of the chop score (a possible Candidate 4, not
here); any lock or timer.
