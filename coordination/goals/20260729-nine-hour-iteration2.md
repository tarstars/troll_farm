# Goal — nine-hour autonomous window, iteration 2

Author: `claude_1` (integrator), 2026-07-29. Type: coordination goal file
(`coordination/multi-agent-protocol.md` §4). Self-contained by design: the liveness, stop,
and authority rules are restated inline so this file can be handed to any agent without
further reading.

## Activation

The owner activates this by naming the file — e.g. *"Pursue the goal in
`coordination/goals/20260729-nine-hour-iteration2.md`."* **The nine-hour window begins
when the receiving agent accepts it, not when this file was committed.** Any agent may
accept; if that agent is not `claude_1`, it works on `agent/<id>` and hands off, and
`claude_1` retains integrator and arena-controller roles.

## Mission

**Establish what our real gap actually is, and then spend the remaining time only on work
that a measured number justifies.**

Iteration 1 closed five hypotheses in a day and produced one experiment worth +0.045
margin. Its most valuable output was a suspicion, not a candidate: H13 could attribute at
most ~1 point of our 2.94-point deficit to `yamo` to code, while the documented
fresh-versus-mature score effect is 3–4 points. **If that holds, our true code gap to the
28.22 bar is roughly 2.5–3.5 rather than 6.46** — and several strategic conclusions,
including whether to build anything at all, change. That measurement is the mission.

## Primary task — N1, the maturity-curve measurement

Quantify the fresh-versus-mature score effect empirically rather than from a single
2026-07-16 anecdote.

**Acceptance criteria, numbered:**
1. Uses the six ladder snapshots (`data/raw/snapshots/`, 2026-07-21 → 07-29, daily since
   07-28) and the 8,131-game corpus; **no new platform reads of any kind.**
2. Fits score against time-since-submission across the field, controlling at minimum for
   battle count and for pool composition drift (the league grew 110 → 112 in this window).
3. Distinguishes *convergence* from *plateau*: does a fresh agent asymptote, and after how
   many battles or days?
4. Delivers three numbers with uncertainty: **(a)** the maturity effect in rating points,
   **(b)** our expected mature score, **(c)** the resulting true code gap to 28.22.
5. States plainly what it cannot determine. Our own agent contributes a single, still-fresh
   trajectory; if the field data cannot separate maturity from strength, **say so and return
   "underdetermined"** — that is a valid, useful outcome and must not be padded into a
   number.

## The fork — what the answer buys

- **Maturity is large (≥ 2 points).** Then the code gap is small, patience and submission
  *timing* dominate every code candidate we have found, and **H9 becomes the live strategic
  question** rather than a curiosity. Write that up for the owner; do **not** act on it —
  every arena action needs explicit authorization.
- **Maturity is small (< 1 point).** Then the ~6-point code gap is real, no execution-class
  candidate found this week comes close to closing it, and **N3 (renewable-base
  feasibility) becomes the priority** because H2 is the only remaining route with that much
  headroom. Run N3 next.
- **Underdetermined.** Run N2 and N3, and report the ambiguity honestly.

## Bounded fallback ladder

Work down this list; do not skip ahead, and do not invent new items.

1. **N1** (above). If blocked at criterion 1 or 2 within ~90 minutes, record why and drop to 2.
2. **N2 — B4.4 verification sweep.** Its figures have been corrected twice (H3 on four
   counts; yamo's own postmortem contradicting the 21–29 planting-tempo claim that motivated
   D175a). Verify or retire the remainder. Until this lands, B4.4 figures may not be cited
   in any new protocol.
3. **N3 — renewable-base feasibility.** Does a self-sustaining resource loop exist on these
   maps, or does the top cohort merely consume a larger windfall faster? H1 found worker 4
   affordable in 0/220 games because our credited resources are a finite windfall, yet the
   top cohort runs 3.55 workers. **This gates H2 entirely.**
4. **N5 — endgame opponent-plant contest.** A mechanic the source design specifies and our
   code lacks; quantify its cost before proposing anything.
5. **N7 — dead-accretion cleanup plan.** Confirm `ScarceIntent`, `banana_factory`,
   `task_market` and opponent-crop scoring are unreachable, then *plan* removal. Removal
   touches the byte-sacred file and needs its own protocol plus a behavioural-identity
   proof — planning only in this window.
6. **H12 filler** — weekly comparative refresh on the newest corpus; report deltas only.

**N4 (H6 residual value audit) is reserved for `chatgpt_1` by right of authorship.** Do not
take it unless they decline or the window's final hour arrives with nothing else to do.

## The bar for starting an experiment

**Do not author or run an experiment protocol unless the originating audit's own honest
value estimate is ≥ +1.0 rating.** Evidence for this rule, all from this week: D175a
measured −26.44, D174a −10.76, H1's package −2.49, and D176a — which largely *worked* —
returned +0.045 with a confidence interval straddling zero. Cycles spent on sub-1-point
candidates have a perfect record of not mattering. If an audit produces something above the
bar, author the protocol properly (frozen thresholds, calibrated gates, preregistered
floors) and dispatch it; otherwise record the finding and move down the ladder.

Two gate-design rules from D176a apply to any protocol written in this window: calibrate
mechanism gates on the **same population the panel measures**, and make each gate able to
distinguish the intervention's intended mechanism of action from the failure mode it was
inherited to catch.

## Authority — explicit

**May:** run read-only audits; dispatch subagents; read the corpus and snapshots; author
frozen protocols; run local paired panels; commit and push to `session-2026-07-01` and
fast-forward `main`; publish coordination messages; integrate peer handoffs; update STATE,
CONSTRAINTS, BACKLOG, and the ledger.

**May not:** perform **any** arena or platform mutation — no submission, no TestSession, no
game generation — *this goal file does not authorize arena writes and cannot*; start the H2
Architecture-2 programme (owner decision, gated on N1 and N3); open sealed ranges
(9,844,200–215; the official-map holdout; the 11 sealed D164 games; 9,852,000–063;
9,857,000–127 consumed by D176a); modify `rust/src/bin/yamo_orchard_live.rs` except via
compile-then-restore under a frozen protocol, ending byte-exact at SHA prefix `fff6669b`;
run any formatter over `rust/src/bin/` or `cgauto/`; use `git add -A` while another agent is
working; force-push; disturb `data/raw/games/` or the 05:17 cron.

## Startup checklist

```bash
python3 scripts/inbox_sweep.py --me <id> --fetch     # ack anything requiring it
sha256sum rust/src/bin/yamo_orchard_live.rs          # must start fff6669b
git status --short                                    # clean before starting
sed -n '1,40p' docs/STATE.md                          # what is live
```
Then read `docs/BACKLOG.md` LIVE PRIORITIES and `docs/CONSTRAINTS.md` before proposing
anything.

## Progress and synchronization (restated inline)

An active task carries a **15-minute progress lease**. Concrete progress means new
inspectable evidence — a commit, a diff, a test or experiment result, a narrowed failure, or
a previously announced long-running command with traceable output. Repeating an intention or
touching a timestamp does not renew it. **Long-running work renews the lease through phase
markers** (`.superpowers/sdd/<exp>-phase-markers.md`); a silent multi-hour run is a breach
even if work is happening. This matters concretely: subagents were killed by transient API
errors **five times this week**, and every one was recovered only because markers and
artifacts were on disk. Write markers after every stage, and stream intermediate results to
disk rather than holding them to the end.

If an agent produces no concrete progress for 15 minutes, the integrator may stop or take
over without further approval, never rewriting the stopped agent's worktree or commits.

## Handoff requirements

Every completed item produces: a scratchpad report with methodology and numbers; a ledger
entry in vol 2; a `docs/CONSTRAINTS.md` bullet for anything closed; a `docs/STATE.md` §4
update; a coordination message to peers; and a commit pushed to both branches. A statement
such as "done" without an inspectable commit and validation evidence is not a handoff.
Negative results are recorded in full — this project's ledger is built from them, and two of
this week's most valuable findings were corrections to the integrator's own claims.

## End condition

The window ends when **any** of these is true: nine hours elapse; N1 returns a verdict and
the fork's implied next item completes; the fallback ladder is exhausted; or a STOP trigger
fires (an integrity-gate failure without an authorized repair, an ambiguity requiring a
design decision, anything touching the arena or sealed data, or the H2 go/no-go).

At the end, regardless of how it ends: consolidate the ledger, refresh `docs/STATE.md`, push
both branches, publish a summary coordination message, and leave a written statement of what
the owner must decide next. If the window closes mid-audit, leave the phase markers and a
resume note rather than a partial conclusion.
