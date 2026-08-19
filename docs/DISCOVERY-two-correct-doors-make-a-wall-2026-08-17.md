# DISCOVERY: "Two correct doors happen to make a wall" — composition failure

- Recorded: 2026-08-17, by owner directive ("I think it's crucial discovery")
- Status: CAPTURED for a future owner-led brainstorm. NO tool is chartered yet.
- Owner's stated intent: *"Later I want brainstorm this case. I want to have a tool
  which can discover and analyze these 'happen to make' cases."*

## The concept, in the owner's framing

Two rules, **each locally correct and each doing exactly what it says**, combine to
produce a systemic pathology that nobody designed and no single-rule review can see.
The wall is not in either door; it exists only in their COMPOSITION. Standard
debugging (inspect each rule, test each rule) passes both doors and never finds the
wall — because there is nothing wrong with either of them.

## The measured instance (H-starve-1, pool #5, codex-review pending)

- **Door A** (`readable resident :1189`): a troll whose chop list is empty is routed
  into the endgame candidate generator — reasonable fallback.
- **Door B** (`:1418`): harvesting is offered only OUTSIDE that generator, re-added
  behind a true-endgame check — reasonable phase scoping.
- **The wall**: a mid-game troll with nothing to chop lands in a generator that is
  incapable of offering harvest — and stands still while ripe fruit passes every
  clause of the bot's own eligibility filter. **325 turns proven across 4
  bulletproof situations** (OSC-032: 110/110, OSC-033: 143/143, OSC-028: 51/51,
  OSC-008: 7/7). Verdict phrasing per the reviewed pool-#5 semantics: **deliberate
  phase-gate composition gap — not a bug**; whether the scope is wrong or worth
  widening is the OWNER's call (pool #6).

## Why this is a CLASS, not an instance — four more from this same iteration

1. **The pairing bench** (pool #3, 24 situations): per-troll candidate generation
   correct + joint pair-selection correct ⇒ one troll idled, sometimes 194 straight
   turns. Composition of two correct optimizers.
2. **The manufactured WAITs** (logging repair, 97 cases): planner emits MOVE
   (correct) + conflict resolver rewrites to WAIT (correct) ⇒ a troll that "chose"
   to do nothing, invisible to any single-stage log.
3. **T-1's corridor deadlocks**: each troll's pathing individually correct ⇒ mutual
   standstill (the original oscillation subject).
4. **Process-level, same shape**: my publish chain (correct) + `--mark` seen-state
   (correct) ⇒ delivered verdicts nobody read. The pattern is not specific to game
   code.

5. **Process-level, the reader's half** (claude_1, 2026-08-17, appended per this note's
   standing invitation): `codex_1` published the pool-#2 verdict as `type: ack` with
   `requires_ack: false` — **correct**, a verdict on someone else's handoff needs no ack
   back. My standing sweep gates on the **ack-required count** — **correct**, that count is
   what needs my action. Composition: `ack` is not in `ACK_REQUIRED_KINDS`, so a verdict
   **addressed to me** could never reach the unacknowledged list. I ran sweeps for five
   hours, reported every one "exit 0 — clean", and then published a status query blaming
   the silence on the agent who had answered within four minutes.
   **Evidence**: verdict `coordination/messages/codex_1/20260817T112344Z-...-pool1-revision-handoff-ack.md`,
   committed in `ab5aea56` at 11:16:37Z; my false-premise query `20260817T134600Z`; my
   retraction `20260817T163500Z`.
   **Why it is a distinct door-pair from #4**: that one is the *sender/integrator* half
   (publish chain + blind `--mark`). This is the *reader* half, and neither fix repairs the
   other — the coordinator's `--mark` change would not have made my sweep show me anything.
   Two independent walls, same shape, in the same transport.

Common signature: **local correctness + unexamined composition + scope mismatch
between "the condition that routes you in" and "the capabilities that live there".**

A sharpened form from instance 5, offered for the brainstorm: the wall appears where **one
rule decides who arrives and a different rule decides what is available there** — and nobody
owns the join. In the game code the conditions are `idle_regeneration && chops.is_empty()`
versus `endgame`; in the transport they are "addressed to me" versus "requires my ack". The
join is exactly where no single-rule review ever looks, because each side is somebody else's
correct rule.

## Seeds for the brainstorm (questions, not designs — nothing chartered)

- **Detection side**: the generic symptom is an entity persistently in a degenerate
  state (WAIT / no progress / oscillation) while a counterfactual oracle says a
  useful action exists. We already own the parts: eligible-action oracles
  (capability × state × reachability), per-stage logging taps (generator → door-clear
  → select → conflict-resolve), clause-by-clause blame (`harvest_gate_blame`
  pattern), P4/D-1 detectors, observed-firing controls discipline.
- **Analysis side**: given the symptom, walk the decision path and ask at each gate
  "would the action have survived if this gate's scope matched the router's
  condition?" — i.e., compute a **compatibility matrix of (routing arms ×
  destination capabilities)** and flag arms whose entry condition does not imply the
  destination offers ≥ 1 real candidate. The measured instance is exactly one red
  cell of that matrix.
- **Relation to the parked bridge-as-code plan (B0/B1)**: the composition auditor is
  a B1-style property — "every routing arm's destination offers a real candidate
  under that arm's entry condition" — and the B0 term census is its substrate. The
  brainstorm should decide whether the tool is static (enumerate arms and scopes
  from code), dynamic (mine the per-stage logs for wall signatures), or both.
- **Scope question for the owner**: game-code walls only, or also process walls
  (items 4–5 above)? The signature is the same; the instrumentation differs.

## Links

- Mechanism note: `claude_1/hstarve1/mechanism-note-pool5-2026-08-17.md`
- Cause table (accepted): `claude_1/hstarve1/` pool-#3 artifacts
- Manufactured WAITs: T-1 logging-repair handoff `20260817T160500Z`
- Iteration record: `coordination/ITERATION.md`
