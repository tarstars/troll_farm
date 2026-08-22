# Context-flush handover — `local_claude_1`, 2026-08-12

Owner-directed: *"write down everything important in a context-flush safe way."* This is an
operational snapshot, not a replacement for the records. When facts conflict, use this order:

1. the newest pushed correction or exact-task message;
2. `docs/STATE.md` for live identity and authority;
3. the governing task record or frozen protocol and its immutable result;
4. `docs/CONSTRAINTS.md` for closed branches;
5. this handover for conversation decisions and navigation.

Every figure below was re-verified against the repository while writing.

---

## 0. Who I am and how to start

**I am `local_claude_1` — coordinator/integrator and sole Arena controller.** Worktree
`/home/tarstars/prj/troll_farm-local_claude_1`, branch `agent/local_claude_1`.

```bash
cd /home/tarstars/prj/troll_farm-local_claude_1
python3 scripts/inbox_sweep.py --me local_claude_1 --fetch     # exit 2 today; see §3
sha256sum rust/src/bin/yamo_orchard_live.rs                    # MUST start fff6669b
```

**`main`, `session-2026-07-01` and `agent/local_claude_1` were all identical at `ac141f6003fe`.**
The owner pushes CI-runner commits to `main` frequently — expect to `git fetch` and `git merge`
rather than force, several times a session.

**Read next:** `docs/STATE.md` → `docs/CONSTRAINTS.md` → `docs/BACKLOG.md` →
`docs/reports/2026-08-10-status-and-next-moves.pdf` (plain-language current state).

---

## 1. The single most important thing

**The competition bot has not changed in over a week and the score has not moved: 22.81, rank
32/137.** Everything since 2026-08-05 has gone into repairing the equipment used to judge
changes, because that equipment was giving meaningless answers.

**And the best bot we have ever measured is not the one running.**

| | source | SHA-256 | score |
|---|---|---|---|
| **live** | `cgauto/submissions/candidate-agent6553250-e7a-r36-simplified.min.rs` | `2caac7c6…` | **22.81**, rank 32 |
| **best measured** | `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs` | `98628e98…` | **24.76**, rank 21 |

The second is `readable__no_orchard` (owner-assigned name; record
`docs/reference/readable__no_orchard.md`). It is simultaneously the **only human-readable
submitted source** (1,475 lines; every other is one line of 55,000+ chars), the **smallest by
real code** (46,859 chars vs 54,720 live), and the **highest mature score measured**. It is
`displaced_superseded`.

**Caveat that governs any decision: one mature run.** The registry warns unprompted, and a
near-identical no-orchard source scored 23.27 on its own run — a 1.5-point spread, wider than the
±0.5–1 noise band. **Re-running it for a second observation is the only open move that could
improve standing, needs no working gate, and awaits owner authorisation.**

---

## 2. The gate: FIXED as of 2026-08-12, not yet integrated

**TRAIN r4 was ACCEPTED** by `chatgpt_1` on a clean exact-commit Actions run: 163 panel tests,
24 pre-review tests, **all 16 declared mutations caught**, and

```text
floor      118/240 BLOCK, 0 gate-unready
candidate  121/240 BLOCK, 0 gate-unready
referee    d8900abf31dd030d07096e9a063365aa0e1f58b85a1613d02b07d3935c523a6a
```

**First run in this programme with zero `GATE_UNREADY` rows.** Four rounds, three rejections.

**✅ INTEGRATED 2026-08-12** (this section originally read "⚠ NOT INTEGRATED"; retained and
corrected rather than rewritten). `main` = `session-2026-07-01` = `agent/local_claude_1`, and
`main:claude_1/pipeline/fuzz_panel.py` is now `d8900abf31dd030d…` with **33** TRAIN references.
Nine branches merged, `abgate-selfplay-gate` deliberately unmerged per invariant 4; all four
hash-locked sources verified intact; zero changes under `rust/`, `sim/`, `cgauto/`; one
agent-authored CI file stripped. Anyone working from `main` now has the repaired referee.

**Two corrections to what this section originally claimed:**

1. **The size figure was wrong.** I wrote that `claude_1`'s branch diverged by "2,104 files,
   +193,920 / −729,616 lines". Measured: **251 files, +231,176 / −127**, touching only
   `claude_1/` and `coordination/`. Same error shape as the rest of §10 — a number adjacent to
   the right one, quoted rather than measured.
2. **The conflict risk did not materialise.** The only conflict in the whole integration was
   `scripts/lint_outbox.py`, and both sides were byte-identical to the pinned `f3c47b70…` — an
   add/add bookkeeping artifact, not a disagreement.

**B1 (independent execution review) is CLOSED** — see
`local_claude_1/verification/train-r4-independent-execution-review-2026-08-12.md`. Floor and
candidate both reproduced exactly, deterministic, and **row-identical** to the committed
`evidence-r4` packets. `118/240` is citable **with r4 §9's restriction**: 10 of 17 repaired
rules have no corpus witness and the floor is not evidence for them.

### How the gate was broken (both defects, for anyone re-deriving)

- **D-9 measured the wrong thing.** Its `banana_before_train` clause fired 196 times across 74
  games in a parent-vs-parent run where displacement is mathematically impossible. It was
  measuring ordinary designed behaviour (the shack-ring orchard: 98 PICK / 98 PLANT).
- **The referee silently discarded TRAIN.** The token appeared **zero** times in `fuzz_panel.py`.
  The bot re-issued TRAIN every turn for 166 and 182 turns on map `m040` — and those two games
  scored as the panel's **cleanest**, `block=False` with all nine detectors and P4 silent.
  A candidate could have been *rewarded* for provoking it.

---

## 3. Transport: working, with four known delivery errors

```
delivery errors 4   quarantined 6   quarantine errors 0
```

- **Two are `claude_1`'s from 2026-08-07** (`review_request` kind; `correction` with empty
  `supersedes`). Content validly re-published at `20260807T170100Z`; ready to quarantine.
- **Two are `claude_1`'s r4 handoff** (`20260811T163000Z`) pinning artifact paths absent from its
  commit. It self-corrected at `20260811T173000Z` — but **a correction does NOT clear a delivery
  error** (verified by execution). Quarantine is the only repair.

**I have not quarantined them** because doing so uses my own repair, which both peers reviewed
but whose *fixes* have not been re-reviewed. That judgement is reversible; the entries are
well-founded.

### Tooling state, verified 2026-08-12 by digest, not by inference

| agent | `scripts/inbox_sweep.py` on its canonical branch |
|---|---|
| `local_claude_1` | `0f78bf38…` ✓ current |
| `chatgpt_1` | `0f78bf38…` ✓ current (finally) |
| `chatgpt_2` | `0f78bf38…` ✓ onboarded correctly |
| **`claude_1`** | `12b27e9c…` — **older**; parses front matter and sees messages, but does **not** enforce roster/quarantine/baseline |
| `local_codex_1` | `12b27e9c…` — unresponsive since 2026-08-06 |

**Standing rule (protocol §1, §10.0):** an agent is not reachable until it publishes the *content*
SHA-256 of the tools it runs. **A reply is evidence of nothing.** I got that inference wrong twice.
Current values on `main`: `inbox_sweep.py` `0f78bf38f32cdd805e29ebfa5591f4f4a55e5a288cd85541df022a452e235515`,
`lint_outbox.py` `f3c47b70d4f99647eed917876a675a1c28fe5e7236e609455d367a34f6af045d`.

**Dual-format addressing is mandatory** (§10.0): every message carries v2 front matter **and** a
legacy `- To:` block, because `chatgpt_1` was blind to every v2 message for ten days.

**Always** `python3 scripts/lint_outbox.py --me local_claude_1 --fetch --staged` before
publishing — and **never pipe it**, which discards its exit code (I did that once and published
past a real error).

---

## 4. Roster

| agent | state |
|---|---|
| `local_claude_1` | me — coordinator, integrator, sole Arena controller |
| `claude_1` | most productive; owns detectors, pipeline, D1-A root cause. Stale tool |
| `chatgpt_1` | adversarial reviewer; cannot execute (no repo clone) — committed-blob analysis is its strength, and it found the worst security hole that way |
| `chatgpt_2` | newly self-onboarded 2026-08-09; delivered a sync-architecture review; **owes its tool digest** |
| `local_codex_1` | unresponsive since 2026-08-06; its work was reassigned |

**Owner ran CI runners on `main`** to unblock reviews — `permissions: contents: read`, which
satisfies the standing rule that evidence must come from a party that cannot publish the verdict.

---

## 5. The oscillation programme

Owner objective, **not score**: *"Oscillations are our lack of control over the program. I want to
remove them not to improve score, but to reduce technical debt, improve our test coverage and
understanding."* Success = the bot **cannot** enter a 194-turn no-op, a test proves it, and we can
explain why the design allowed it.

**`CONSTRAINTS.md` closes oscillation on VALUE and that stands** — D176a fixed it below yamo's own
reference and was worth **+0.045 margin, CI [−0.024,+0.114]**. Nobody may argue this raises score.

### What three independent answers established

- **The obvious fix does not work.** Every D-1 step is advance-or-retreat, zero lateral, so a
  monotone-or-hold mover removes 34/35 episodes — but **20 of 20 terminal blockers never move**.
  A mover-only fix converts 20 oscillations into 20 stalls and restores progress in none.
- **`Target::None` bypass** (`claude_1`): `compatible()` returns `true` unconditionally when
  either target is `None` (candidate line 643, sacred source 1329). Same-target contention *does*
  survive the pairwise check.
- **D1-B localised for the first time** at `endgame_candidates:1290-1302` — a door-pricing
  asymmetry. Matters because raw zero is conjunctive.
- **The defect is an interface** (`chatgpt_1`): the resolver's override is never fed back into
  target validity or scoring, so two correct stateless functions compose into a terminal
  involution.
- **The Gold-era watchdog cannot be ported** — it counts a *same-position* streak and an
  oscillating unit moves every turn. Found independently by two agents; it was my own suggestion.

**Merged plan:** `local_claude_1/oscillation-merged-plan-2026-08-09.md`. Its principle was
**corrected** — the terminal blocker is **IDLE, not working**, so the load-bearing fix is an
**idle-yield rule**, not re-targeting. ⚠ **That finding is still unreplicated**: it came from a
library built on a *different* bot (`a8eb3b2b`), and `chatgpt_1` reports
`BLOCKER_ACTIVITY_UNRESOLVED` — it could not confirm it from committed data.

**Acceptance:** all 20 terminal episodes gone **and progress restored** — "D-1 = 0" alone is
insufficient because a stall satisfies it.

---

## 6. The manifest programme (score transparency)

Owner: the bot's logic is weights on actions; that hides what trolls are doing; build a bridge,
build tooling, build an oscillation situation library, audit the score hierarchy.

**Both reviewers corrected the premise:** the bot is a **pipeline** and weights are ~**a third**
of the decision. **The static bridge is demoted.** Deliverable one is `chatgpt_1`'s
**Decision Packet** — spec frozen, includes the attainable-range requirement I added.

- **M2 hierarchy audit** (`claude_1`, done): **10 boundary crossings, 8 measured end-to-end**,
  3 hierarchy inversions, 3 pieces of dead scoring code. Two-tier: banded and sound above
  `6_000`, **entirely unbanded below**. Largest crossing is **temporal** — conversion priced
  `≤187.5` on turn 250 and `7_000` on turn 251, a ×37–×961 jump at a magic number.
- **M3a situation library**: **34 episodes / 32 situations / 20 terminal**, agreed by **three
  independent extractions**. `claude_1`'s first library counted 47 because it used a **different
  bot** plus 10 P4-only windows and 1 partial — reconciled exactly, not an over-count.
- **`chatgpt_1`'s golden bundle fails its own verification** (my second-checkout run): the
  committed golden JSON predates the extractor's `episode_ledger_sha256` field, so regeneration
  is not byte-identical; 2 of 10 bundle tests fail. Data is fine. Also not self-contained on its
  own ref.
- **M3b adjudication** — the manifest's most valuable item, never attempted: judge each situation
  *independently* and compare with what the score chose. Asks whether a decision was **correct**;
  everything we own asks only whether it *oscillated*.

---

## 7. Bananas: both routes closed

- **D89a `NOT_REPAIRABLE`** (`claude_1`, restored after it withdrew and then re-did the assigned
  adversarial work). Perfect-hindsight selection still fails the gate **eight-fold** — oracle
  upper bound `+8.002` against a `≤+1` bar. Its cited pre-treatment snapshot **does not exist**;
  zero d89a data rows across all refs.
- **R2 wrapper line**: a week, zero valid candidates.
- **CBF conditional banana farm** — the owner-specified design — is the **only route standing**.
  Spec `docs/superpowers/specs/2026-08-07-conditional-banana-farm-design.md`. Latched
  `DENY → FARM → WOOD`; byte-identical to the resident when the opponent never fields a third
  troll. **Parked, not started.**
- **The `+12.453` theft / `+76.508` opponent-production split is UNRESOLVED** — prose only, no
  committed data. I propagated it as fact; corrected.

---

## 8. Owner decisions outstanding

1. **Re-run `readable__no_orchard`** for a second mature observation. Only move that could improve
   standing; needs no working gate. **Arena action — needs your word.**
2. **Check GitHub branch-protection on `agent/*`.** Last unresolved *critical* finding from
   `claude_1`'s security review: one push could nullify the entire quarantine irreparably. It
   declined to test it because *the proof of that attack is the damage*. **Only you can answer.**
3. **Scope for `chatgpt_2`** — it has onboarded but holds no authority.
4. **Which banana route**, if any, after the gate is integrated.

---

## 9. Hazards (violating these breaks other agents)

- `rust/src/bin/yamo_orchard_live.rs` byte-exact at `fff6669b…`; candidate `98628e98…`; live
  `2caac7c6…`.
- Never run a formatter over `rust/src/bin/` or `cgauto/`.
- Never `git add -A` or `git add -u` with concurrent agents — stage exact paths.
- Sealed: maps 9,844,200–215, the official holdout, 11 D164 games, 9,852,000–063, 9,857,000–127.
- Do not disturb `data/raw/games/` or the 05:17 cron.
- Arena: standing authorization since 2026-07-30 (per-candidate gate lifted) but requires a
  QUALIFIED frozen-protocol verdict and gain above the ±0.5–1 noise band. **No mutation in
  flight; no qualified candidate.**
- `git reset --hard` destroyed an hour of my uncommitted work once. **Commit before any history
  operation.**

---

## 10. Calibration — my own error record

Read this before trusting anything I wrote. **Nine claims of mine were later found unsupported**:
four caught by another agent, three by me before publishing, two by a tool before publishing.

The recurring shape: **I quote a number adjacent to the right one, or repeat a summary instead of
reading the data.** Worked examples — I read `compatible()` and saw only its `a != b` branch,
missing the `Target::None` escape in code I had pasted; I claimed a chop maximum of 3900 when
`turns ≥ 2` always makes it 2400; I said the band was caller-set when both functions have one
call site with a literal; I cited a theft/production split that was never measured; I twice
invented the tail of a commit hash.

**The countermeasures that work:** tools check what tools can check (the lint has caught two of
my errors pre-publication, including the exact defect that is one of claude_1's permanent
delivery errors); and **no conclusion is adopted until two agents have independently attacked
it** — which has overturned a recommendation or a premise *every single time it has been
applied*.

**The trend is the useful part:** early in the week errors were caught by people after
publication; by the end, by tools and authors before it.

---

## 11. Immediate next actions, ordered

1. ~~Integrate TRAIN r4 to `main`~~ **DONE 2026-08-12** — `main` at the integrated head; see §2.
2. ~~Independently re-verify the 118/240 floor~~ **DONE 2026-08-12** — reproduced exactly and
   row-identically; B1 closed.
3. ~~Read the six unread `chatgpt_1` reviews from the 2026-08-11 burst~~ **DONE.** Dispositions:
   M3a correct-subject `REVISION_REQUIRED` (replay not portable); M3a golden bundle v2 renewed
   **green** and requesting adoption review — *claimed, not yet verified by me, and my last
   second-checkout run of the v1 bundle failed 2 of 10 tests, so this needs execution before it
   is believed*; fast-verification-executor requirements handoff (review requested);
   M2 revision 2 `ADVERSARIAL_ACCEPTED`; I-30 revision 3 core accepted, `REVISION_REQUIRED` at
   the trust root; bite-test audit r2 historical accepted, current revision required.
4. ~~Quarantine `claude_1`'s four delivery errors~~ **DONE 2026-08-12.** Both peers had by then
   attacked the mechanism, releasing the hold. Sweep is now **0 delivery errors, 0 quarantine
   errors, 9 quarantined, 0 collisions** — the first clean sweep. TQ-2 rejected my own
   unauthorized adjudication on the way, and failed closed rather than partially applying.

**Now the top of the list:**

5. **Rebuild M3a on the correct subject; replicate the idle-blocker finding; then M3b.** M3b —
   judging each situation independently and comparing with what the score chose — is still the
   most valuable unattempted item, and the only one that asks whether a decision was *correct*
   rather than whether it *oscillated*.
6. Verify `chatgpt_1`'s golden-bundle-v2 "green" claim by execution before adopting it.
7. Answer owed by peers: `chatgpt_1` re-publishes reconcilable tool digests (the two SHA-256s in
   its `20260811T232000Z` blocker match no blob in either file's entire history, including the
   blob cited beside them); `claude_1` restores `scripts/lint_outbox.py`, which is **absent**
   from its branch and explains its recurring delivery errors; `chatgpt_2` still owes its digest.
