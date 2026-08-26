# HANDOVER 2026-08-26 — diffs in files; Candidate 0 blocked and closed; Candidate 3's rule corrected to "absolute keep"; the goal hook cleared by the owner

Read `coordination/HANDOVER-2026-08-25c-candidate-2-stop.md` (and its predecessors) for the
afternoon of 08-25. This file is the delta 2026-08-26 06:00Z → 10:35Z, written at the owner's
request ("save the current state, prepare to context flush") by `local_claude_1`. Trunk at
writing: `origin/main` == `agent/local_claude_1` == `c8872ffd` + this commit.

## Resume here

- Agent `local_claude_1`: coordinator, integrator, sole Arena controller (owner, 08-24). Worktree
  `/home/tarstars/prj/troll_farm-local_claude_1`; **every shell command `cd`s into it** (the
  harness resets the cwd to the stale main checkout). Ritual:
  `python3 scripts/inbox_sweep.py --me local_claude_1 --fetch` → read every new message whole from
  the peer's remote ref → `--mark` as its own step → commit the seen-state. The sweep now reads
  the quarantine from `origin/main` (roster v2, `former_coordinators`).
- **`coordination/GOAL.md` = the live mission text (Candidate 3 → diff on `main`; Candidate 2
  re-run on top), amended 08:10Z; the `/goal` hook is CLEARED by the owner (10:3xZ) — nothing
  runs unattended until the owner re-runs `/goal coordination/GOAL.md`.** Peers still wake on
  ack-required mail via the VM launcher.
- **Last thing I did:** published two ack-required rulings at 10:27Z
  (`20260826T102747Z-…-candidate-0-…-policy.md`: Candidate 0 CLOSED;
  `20260826T102748Z-…-candidate-3-…-policy.md`: the charter correction, G-0 r4 requested).
  claude_1 and codex_1 will answer them; the next wake reads those answers first.
- **Owner's queue:** the v3 page + its 08:10Z addendum,
  `local_claude_1/cure2/owner-question-2026-08-25.md` — the correction of the `m061` attribution
  and the Candidate 3 rule change (absolute keep, no margin) are stated there for the owner to
  veto; otherwise nothing waits on the owner. Candidate 1's verdict sheet: parked, code kept (done).

## The owner's rulings of 2026-08-26 (all transcribed in the cards)

1. ~06:00Z: Candidate 0 (fix the champion's replant fallback) and Candidate 3 ("a troll keeps its
   goal") go ahead; the owner wants to read the code; Candidate 0 gets an 8-exposure
   self-replacement platform block after the change ("AAAAAAAA"); the bot being fixed must have
   its own platform score (checked: the champion `547fa706` has ≥ 11 mature reads, mean ≈ 22.9).
2. ~06:10Z: **"it shouldn't be exactly PRs — I want to see diffs in files."** → deliverable of
   record = `readable/diffs/<candidate>.diff` on `main` (`docs/readable-format.md`, amended
   ruling). Published immediately: `readable/door1-champion.rs` (the champion, 2,210 lines),
   `candidate-1-hold.rs`, `candidate-2-swap.rs`, their round-trip reports, and three diffs
   (`candidate-1-hold.diff`, `candidate-2-swap.diff`, `candidate-2-swap-vs-candidate-1-hold.diff`
   = the swap rule alone, 327 lines) + `readable/README.md`. GitHub:
   `https://github.com/tarstars/troll_farm/tree/main/readable`.
3. 10:3xZ: `/goal clear`; "clear background commands" (none were running); then this flush.

## What happened (06:04Z charters → 07:54Z both blocked → 10:27Z rulings)

- **Candidate 0** (`20260826-candidate-0-regeneration-fallback`) — **CLOSED, BLOCKED at G-1.**
  The one-hunk fix (the `idle_regeneration && chops.is_empty()` fallback extends `out` instead of
  replacing it) was built and measured by claude_1 and independently reproduced by codex_1:
  containment perfect (97 diverging games, all with the fallback firing; 34/34 fixtures identical;
  determinism), **but unsafe** — blocking games **118/240 vs 43/240**, D-2 0 → 387, P4 16 → 85,
  P3 0 → 5, `m061` worse by 18 and 9: the surviving 7,500-point regeneration `PICK` beats every
  job for a shack-adjacent empty-handed troll, the bank clause offers `DROP` next turn, nothing
  links `PICK` to `PLANT` — a PICK↔DROP two-cycle. Panel aggregate **+530 own-score points**
  (recorded as the size of the regeneration value a plan-keeping successor could capture; it does
  not pass the hard gate). **Record correction:** the "−75 on `m061`" was the *swap's* cost
  (rule-off 75/82 → instrument 39/43); the champion scores 75/82 there. The 8-read block lapses.
  Successor = Candidate 3's plan-keeping case.
- **Candidate 3** (`20260826-candidate-3-keep-your-goal`) — **charter corrected 10:27Z; G-0 r4
  requested.** claude_1's r3 measured, on the six loop games, that the challenger's advantage
  `rho` rises monotonically as the shared tree's remaining chops `K` fall (0.0231 → 0.26984 >
  M = 0.25 at `m090:0` t=12), so **no fixed margin can prove "no second exchange"** — the form is
  falsified (codex_1 BLOCK pending correction). Corrected rule: **absolute keep** — a troll keeps
  its goal until **done** (progress at it), **gone**, **impossible** (no path with the teammate's
  cell treated as free), or **dead**; nothing overrules a valid kept goal; **a fruit picked to
  plant is kept until planted** (the same rule on a two-step goal). Base = `readable/door1-champion.rs`
  (Candidate 0 gone); telemetry v6 with mutual refusal; round-trip gate = canonical-compaction
  identity; deliverable `readable/diffs/candidate-3-keep-your-goal.diff`. Platform measurement
  of Candidate 3 **not authorized** (ask when the diff is up). Then Candidate 2 re-run on top
  (C-5 expected 0 on the six loop games).
- **`readable/door1-champion.rs` header corrected** (it claimed compaction reproduces `547fa706…`
  and carried an inherited `102caecd…` lineage line — both false). Now: source path, the
  canonical-compaction gate (`compact(readable) == compact(parent)` = `0da12c33e07a…`; the parent
  was never minified), true lineage. Readable sha now `ad1ae4ef…`, 2,210 lines (+4 from the top —
  line numbers in claude_1's Candidate 0 packet shift by +4). Round-trip re-verified identical.
  `docs/readable-format.md` notes the gate for non-minified parents and that `--title` is an
  unpinned input.

## Unowned defects surfaced today (for the owner's next sheet / future charters)

- **23 of 34 frozen fixtures are `NOT_REPRODUCIBLE_ON_BASE` on every arm** (the library drifted
  from the referee build); silently removes two thirds of the fixture corpus from every verdict.
  Needs its own charter.
- The `--p4b` gate reads one telemetry dialect (v4): NOT_EVALUABLE on v5 arms and on
  non-instrument arms (banner `MSG`). Follow-up `20260826-p4b-narrator-param` (codex_1 builds,
  claude_1 reviews) — not started.
- `20260826-deferred-card-lint` (a `-deferred` message with no `^DEFERRED:` line is a lint
  error) — not started. Standing rule meanwhile: after publishing a card, re-run the sweep and
  confirm it is live; a clean lint is not evidence.
- Shipping form: arms are shipped compacted (the champion's ladder reads were of the expanded
  file); behaviour identity by panel parity — ruled, no action.

## Operational notes (see also memory `vm-launcher-ops`)

- The VM launcher rings only on ack-required *news*; plain receipts do not wake a peer; a dead wake
  consumes its bell → re-ring with an ack-required message. A wake can die on a transient 403 at
  the proxy (`10.77.0.1:3128`) mid-session, after work and before pushing; the next wake must check
  its worktree and re-verify. Session logs flush at session end. Disk: codex_1's and claude_1's
  scratch extracts are removed by `trap` now; watch `df` anyway.
- The stamp rule (`date -u` in the writing command) held all day after the 08-25 drift.

## Arena — unchanged all day

Ladder resident: the Candidate 1 instrument (agent `6659743`, 21.8); champion of record door 1
`547fa706…`, off ladder; `NIGHT-HALT`. **No Arena action was taken today; none is authorized now**
(the Candidate 0 block lapsed with its task).

## Owed by me

Nothing to the peers beyond reading their answers to the 10:27Z rulings. To the owner: nothing —
they may veto the Candidate 3 rule change or re-run `/goal`. Peer branches carry ~200 unmerged
commits each; integration owed, non-blocking, pin-only.
