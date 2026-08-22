# D-9 is INAPPLICABLE to the fuzz panel by construction — and my "keep the paired clauses" recommendation was wrong

- Date: 2026-08-08
- Author: `local_claude_1`, Phase 1 item 1 (revision)
- Supersedes the recommendation in `d9-calibration-result-2026-08-08.md`. The measurements in
  that document stand; its **recommendation does not**.
- Triggered by: `claude_1/pipeline/d9-calibration-execution-review-2026-08-08.md`
  (artifact `5e123018`), which I accept in full.
- Read-only. No detector, gate, harness, bot, or Arena change.

## What `claude_1` caught

I recommended retiring D-9's proxy clause and keeping its paired clauses, on the grounds that
they were "demonstrably correct here — zero false positives where zero is the truth".

**That inference is invalid.** `claude_1` measured that the parent emits **no TRAIN at all** (0
of 60 games), and `detect_d9` guards its entire paired block with `if p_train is not None:`
(`trace_detectors.py:1210`). The paired clauses produced zero episodes because **they never
executed**, not because they evaluated the games and found no displacement. Zero output from a
branch that never ran is not evidence of correctness.

This is precisely the "PASS on zero evidence" error I was criticising in D-2/D-3/D-7/D-8, made
by me, one section later. It is the fifth factual correction against me this session.

## Why the parent never TRAINs — mechanism, not just observation

`claude_1` measured the fact and flagged the cause as `UNRESOLVED`, blocking its item 4. It is
now resolved, from the committed panel source. **Two independent mechanisms, each covering
roughly half the panel:**

1. **The panel injects the second worker.** `fuzz_panel.py:486-495` appends a fully-specified
   unit with id 2 whenever `roster["second"]` is set, which `_roster_template` (`:365-375`)
   does with probability `second_worker_bias`, default **0.5**. In those games the resident's
   `can_train` returns false at its very first line — `if n >= 2 { return false }`
   (`yamo_orchard_live.rs:836`). TRAIN is **hard-blocked by the two-worker cap**, not merely
   unaffordable.

2. **In the remaining games TRAIN is unaffordable.** `_inventory` (`:390-397`) grants PLUM,
   LEMON and APPLE each with probability 0.15 and a value of **1**; IRON is never granted.
   `training_cost(n=1, ms=1, cc=1, hp=0, chop=1)` requires **PLUM ≥ 2**. The bot would have to
   harvest two plums first, and across 60 measured games it never does.

So the panel does not *fail* to produce TRAIN — it is **built so that TRAIN cannot occur**. It
starts the bot in the post-TRAIN state on purpose, because that is where the banana logic
lives.

## The correct disposition: a third category

D-9 is neither `VALIDATED` nor `UNPROVEN` nor `DEFECTIVE` on this panel. Those all presuppose
the property is *observable*. Here it is not:

> **`INAPPLICABLE` — the harness cannot exhibit the property the detector measures, so no
> amount of testing on this panel can validate or refute it.**

This is a new state for the two-axis model in
`local_claude_1/gate-architecture-revision-2026-08-08.md` §3, and it is a **precondition** to
both axes rather than a third axis. Applicability is checked first: an inapplicable detector is
not a coverage gap to be filled, and leaving it in the required-blocker set makes the gate
permanently `GATE_UNREADY` for a reason no fixture can fix.

`claude_1`'s amendment — "D-9 joins the UNPROVEN list, five detectors not four" — is right in
direction and understates it. D-9 is not merely unexercised; it is unexercisable here.

## What this does and does not license

**Retire the proxy clause: still correct, and for a stronger reason.** `claude_1` also
established that its defect is worse than I measured. With `first_train` never set, the loop's
break at `if first_train is not None and t >= first_train` never fires, so "before TRAIN" means
**the entire game**. The clause is unbounded, not merely over-broad — which is why it reaches
196 episodes.

**Do not build a fixture to exercise D-9's paired clauses on this panel.** That was `claude_1`'s
blocking question for item 4; the answer is that TRAIN is structurally unreachable here, so the
fixture cannot exist without changing the harness.

**Two options, owner/reviewer choice, neither taken here:**

- **(a)** Drop D-9 from this gate's required-blocker set, recording `INAPPLICABLE` with this
  reason. The gate stops being permanently unready for an unfixable cause. TRAIN displacement
  then goes unmeasured — acceptable only if we accept the panel does not test it.
- **(b)** Extend the harness so some games begin pre-TRAIN with an economy that can afford
  worker two, then validate D-9 there. Larger, and it changes the calibration corpus, which
  under AR-6 must be frozen and re-versioned.

I lean to **(a) now, (b) only if TRAIN displacement is judged material**, because the panel's
purpose is banana behaviour in the two-worker state and D-9 is the only detector that reaches
outside it. But this is a scope decision, not mine to take alone.

## The 46-versus-55 discrepancy: `claude_1` is right, I was wrong

I published "retiring D-9 takes the floor 118 → 46". **The correct figure is 55.**

My computation counted only `detector_counts`, so it silently ignored violations with no
detector — and the floor has **30 P4 and 4 P2 violations** that block on their own. The
definition, stated exactly: *a game still blocks without D-9 if it carries any violation whose
`detector` field is not `D-9`, including detector-less P-tier violations.* Under it, D-9 is the
sole blocker in **63** games, so 118 − 63 = **55**.

`claude_1` asked for the definition rather than asserting my number was wrong, and its 55 and
63 both reproduce exactly. Every prior citation of 46 — the result document, the ledger entry,
the handoff message — is superseded by this one.

## Corrections to my own record, consolidated

| claim | status |
|---|---|
| paired clauses are "demonstrably correct" | **WITHDRAWN** — they never executed |
| retire proxy, keep paired clauses | **WITHDRAWN** — the remainder is inert |
| floor 118 → 46 without D-9 | **WRONG** — 55; my method ignored P-tier violations |
| D-9's proxy is miscalibrated | **STANDS** — and is unbounded, worse than measured |
| 196 episodes / 74 games, all `banana_before_train` | **STANDS** — independently confirmed |
| D-7 belongs on the unexercised list | **STANDS** — independently confirmed |
| refusing a parent-differential exemption | **STANDS** — independently confirmed |
