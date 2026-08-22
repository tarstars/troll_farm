# Coordinator handover — `claude_1` → `local_codex_1`, 2026-07-30

Owner directive: *"notify other agents that now coordinator is local_codex_1."* Authority:
`coordination/multi-agent-protocol.md` §1 — "Roles are defaults, not capability limits… the
user may reassign at any time." Outgoing coordinator: `claude_1`. Incoming: `local_codex_1`.

**Scope note requiring your confirmation, owner:** the protocol treats the **arena
controller** as "normally the integrator", so by default it follows the coordinator role to
`local_codex_1`. That role can submit to the live ladder under the 2026-07-30 standing
authorization. **Practical exposure today is zero — no qualified candidate exists, so there is
nothing submittable** — but if you want the arena controller to stay with `claude_1` or move
somewhere else, say so and it will be recorded. Until then it moves with the coordinator.

## 1. Read this first, in order

`docs/STATE.md` → `docs/CONSTRAINTS.md` → `docs/BACKLOG.md` (live priorities) →
`docs/APPROACH-REGISTER-2026-07-30.md` (35 items, the rolling work list) →
`coordination/multi-agent-protocol.md` → `coordination/README.md`. Then sweep:
`python3 scripts/inbox_sweep.py --me local_codex_1 --fetch`.

New-agent onboarding text, if you have not joined the repo yet:
`coordination/peer-prompt.md`. You have no namespace here yet — create
`coordination/messages/local_codex_1/`, `coordination/status/local_codex_1.md`, and
`local_codex_1/` for private bookkeeping.

## 2. Where the project stands

Resident agent `6561795`, **score 21.76**, untouched since 2026-07-19. Goal was re-scoped by
the owner on 2026-07-30 to a **mature score ≥ 25.40** (interim checkpoint 24.70 = `yamo`, the
published design this bot reproduces); rank ≤3 is superseded. Corpus 9,082 games, growing
~450/night by cron.

**Nothing is running.** No experiment, no audit, no agent job.

**Live owner decisions already made:** goal re-scope; A2 rebuild authorized (Phase 0a passed);
standing arena authorization; breadth strategy at the plateau; history rewrite declined.

**Open owner decisions:** H10b (whole-policy learned network — competes with A2); arena
submission timing (waits on N1).

## 3. What is assigned and to whom

- **N1 maturity-curve measurement — assigned to `chatgpt_1`.** Identifiability preflight
  complete (verdict: CONDITIONALLY IDENTIFIABLE, raw-field audit is the prerequisite). **The
  full analysis has NOT been performed** — no analyzer file, no verdict, nothing running. This
  is the highest-value item on the board: if the fresh-vs-mature effect is the documented 3–4
  points, our true code gap is ~2.5–3.5 rather than 6.46 and the right action may be to wait.
- **Decision-evidence-index pilot — `chatgpt_1`**, accepted with four additions from my review
  (void-premise status, panel-vs-arena strength split, per-claim population, cost).
- **N4** (H6 residual) reserved to `chatgpt_1` by authorship. **A2-0b** parity harness offered,
  unclaimed.
- Everything else in the register is unclaimed and, per the rolling rule, **audits need no
  value bar**; experiments need ≥+1.0 rating from an audit first.

## 4. Invariants — violating these breaks other agents' work

- `rust/src/bin/yamo_orchard_live.rs` stays byte-exact at SHA-256 prefix **`fff6669b`**; it is
  library-visible as `troll_farm::resident_policy`, so any working-tree diff contaminates every
  concurrent experiment. Compile-then-restore for anything that must modify it.
- **Never run a formatter** over `rust/src/bin/` or `cgauto/` — experiment locks record file
  hashes. A stray `cargo fmt` already broke 11 files once.
- **Never `git add -A`** while another agent is working. I did, and swept a running audit's
  in-progress script into an unrelated commit.
- Sealed: maps 9,844,200–215; the official-map holdout; the 11 sealed D164 games;
  9,852,000–063; 9,857,000–127.
- Do not disturb `data/raw/games/` or the 05:17 cron.
- **Unpushed means unsent** (protocol head): never tell the owner or a peer that something was
  sent, published, or handed off until the remote SHA is verified.

## 5. The traps, stated as my own errors this week

These are the things that actually went wrong, and they are all coordinator-level:

1. **Concluding from a partial subagent output.** Twice in one day. I declared "no renewable
   base exists anywhere" from an incomplete `report.json`; the finished analysis said the
   opposite and had the mechanically decisive argument. Wait for the verdict, or label the
   reading as provisional in the same breath.
2. **Specifying a gate against the wrong quantity.** Three times — D176a's worst-case gate
   anchored to a corpus statistic the panel's own control missed by 12×, its displacement gate
   unable to tell the intended cure from the failure mode it inherited, and A2's K1 written
   against "renewal" when the binding variable was conversion efficiency. Calibrate on the
   population the panel measures.
3. **Trusting my own value estimates.** Wrong four times in one sweep. That is why the owner
   directed breadth over filtering, and why audits carry no value bar.
4. **Taking a task a peer had claimed.** `chatgpt_1` claimed N1 and was waiting on me to cut
   the record; I dispatched my own agent instead. Contributing cause: my sweep tool paired acks
   on filenames and kept crying wolf, so I stopped believing it. Tool now fixed; the lesson is
   that the enforcer is not exempt.
5. **Stale hardcoded values in generators.** The atlas title page claimed 2026-07-27 through
   two updates because the date was baked into the script.

## 6. Peer relationship — worth knowing

`chatgpt_1` is genuinely good and its corrections have been load-bearing: it proved H7's
mechanic does not exist in this game, rejected my H1 bundle design on attribution grounds,
caught an opponent-family/map-class confusion, re-characterised H1's bound correctly, and
fixed the transport hole in the protocol. Its first two artifacts analysed the *wrong bot*
(the retired v1.59 and pre-Gold v0.6.1) because it read stale `main` and skipped
STATE/CONSTRAINTS — corrected, and it has been reliable since. **Corrections flow both ways
and that is the point.**

## 7. Mechanical state at handover

`main` and `session-2026-07-01` identical and pushed; no unmerged peer commits; inbox clean;
working tree clean; dev copy verified. Full-history bundle and 1,629 migrated bulk artifacts on
the `medium_data` volume. Atlas current at 29 pages, snapshot 2026-07-30.

## 8. What I would do first, for whatever it is worth

Chase **N1** to a verdict — it re-baselines every build-vs-wait decision and is already
assigned. Then **X1**, the systematic mechanics re-derivation: it was promoted today because
Phase 0a found an **undocumented per-player starting bank of ~24 fruit and ~6 iron**, absent
from `docs/mechanics.md` and an input to every affordability calculation this project has ever
run. One rule was missing; others may be. Then **A2-0b**, since no A2 number can be trusted
until the measurement rig is proven.
