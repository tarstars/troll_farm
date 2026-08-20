# claude_1 Status

- Updated UTC: 2026-08-20T12:53:28Z (REAL clock, `date -u`)

## READ THIS FIRST — what is WITHDRAWN (2026-08-17)

**Everything I published about the parked troll's CAUSE is withdrawn. Standing causal state: ZERO
established causes.** If you are resuming, do not act on any of it:

- **`GENERATOR_GAP` on OSC-001 / OSC-012 / OSC-031 — WITHDRAWN.** Three separate defects, each
  found after I published: (a) my audit runner omitted `referee.grow()`, so every measurement came
  from a world where **no plant ever ripened**; (b) my work-oracle counted *geometric reachability*
  as work, ignoring capability — **OSC-012's parked unit has `harvest=0, chop=0`**, so the planner
  offering it nothing was **correct**; (c) my runner replaced the shared runner's fail-closed error
  on early stdout closure with a fail-open `break`.
- **The "3 of 3" and "2 of 2" counts — WITHDRAWN** with the labels they carried.
- **`local_claude_1`'s dance-is-innocent result — WITHDRAWN to hypothesis** by its author (pool #4
  v2), and **my approving repetition of it is withdrawn with it**. It is *consistent with* T-1's
  1-of-25 and the ≈ +0.045 pre-registration; it is **demonstrated by nothing yet**.
- **`1.41` corpus points never travels without both its IFs** (audit shows the freezes fixable AND
  the owner judges those games winnable).

**What stands:** T-1's measured results (separate instrument, world-evolution verified `c673dd37`)
— stage 2 and 3 both **0 FIXED / 34**, stage 4 swap **2 FIXED / 34**, graded by the integrator as
**1 of the 25 predicted**. Panel: **0 de-novo oscillation**, D-1 **12.50%** vs a **matched floor
14.58%** I measured rather than inherited. Gates: 2, 3 (warm p95 **0.04 ms**), 4 (parity identical)
**MET**; gate 1 **partially met** — `half_swap` guard unvalidated because whole-game perturbation
cannot hold the trajectory fixed.

## Current position (2026-08-20, later) — proxy FIXED, launcher starves one layer up

**Inbox drained to 0/0 and pushed.** Head `agent/claude_1` carries: tooling sync (suite **119/119**,
was 105 — `agent_launcher.py` and the cc-ack narrowing were both missing here again), the `--mark`
stranded by a starved launched session, two evidence artifacts, two blockers, two acks, and the
quarantine registry resynced from the coordinator (I was one entry behind — my own 055011Z handoff).

### What actually happened today, in the right order

1. **The 403 was the PROXY, not auth** — the owner's memory, not any record. `/home/tarstars/bin/claude-proxy`
   (egress `10.77.0.1:3128`) is the sanctioned wrapper; `docs/vm-proxy.md` now exists so it can never
   be lost again. My credential-expiry diagnosis was **wrong**, and I cited `daemon-auth-status.json`
   = `auth_required` as support. **That file still reads `auth_required` with a live authenticated
   session running.** It was never evidence of what I used it for.
2. **Wakes #1 (12:38:16Z) and #2 (12:47:15Z) both authenticated and both starved.** `claude -p` is
   non-interactive: `git status/log/show/diff` allowed; `python3 …`, `git fetch`, `git commit`,
   `git push` and **`Write`** denied. A woken session can read the queue and cannot sweep, `--mark`,
   ack, publish, **or leave a DEFERRED card** — carding requires writing a file. Worse than the 403,
   which at least died visibly in 3 s; this logs an ordinary `wake` and changes nothing.
3. **The fix is tested, not proposed.** Per-lane `--allowedTools` on the launcher argv: Arm A ran
   (`42`), Arm B with the flag removed was denied — same wrapper, same command, one minute apart.
   Scoped to launcher sessions, not host-wide; push scoped to `agent/claude_1`, never
   `--dangerously-skip-permissions`. **NOT APPLIED — owner's posture call**, on the machine holding
   the Arena cookie. This is the one action that ends the starvation.
4. **I corrected the round summary's attribution.** It credited wake #1 with "read, marked, synced
   tooling". It read; it could not mark or sync. Those were mine, `mtime 12:29:33Z` vs the wake at
   `12:38:16Z` — **nine minutes earlier**. Wake #1's own log made the same misread of my uncommitted
   seen-state, and the summary compounded it. It matters because the repair aimed at it — sharpening
   the ritual prompt to "end pushed" — **was tested by wake #2 and refused**: a prompt cannot lift a
   permission denial. The ritual line is still right and still worth keeping; it is not what broke.

### Standing

- **The launcher card's bar — "a launched session DRAINS a real queue" — remains UNMET. I am not
  claiming it.** The next launched session that completes sweep → mark → commit → push unattended
  is the delivery, and it cannot happen before the allowlist lands.
- Card 2 sentinel build: still blocked on the integrator's `actionable_set()` extraction ruling.
  Note a precedent nobody has ruled on: `agent_launcher.py:58` gets the actionable set by running
  `inbox_sweep.py` **as a subprocess and parsing its stdout section headers**. That route needs no
  extraction ruling — and it is fragile in this project's signature way: reword a section header and
  `SECTION_RE` matches nothing, `paths` comes back empty, and the launcher reports "no work" instead
  of failing.
- Card 3 pair-selector Phase 1: still deferred behind the OSC-031 KEEP/REVERT.
- `night-runner` HEALTHY. **VM disk 98%, 541M free** — down from ~1.2G this morning; this has already
  blocked one deploy with ENOSPC.
- Trap re-hit and worth writing down again: `publish_outbox.sh` lints `--staged`, so running it with
  nothing staged lints **0 files and passes**. A gate with an empty subject is not a gate.

## Current position (2026-08-20) — two services deployed on the VM; one blocked on auth

**SESSION FLUSHED HERE. Read this block, then `troll-farm-vm-services`, `troll-farm-transport-rules`
and `troll-farm-osc031-state` in memory.**

### Services I deployed on the VM (check both first: `systemctl is-active night-runner agent-launcher`)

- **`night-runner.service` — HEALTHY, accepted.** Runs the M-1 decider night with no LLM from
  `/home/tarstars/prj/troll_farm-claude_1-lfs` on branch `agent/local_claude_1` (the branch NAME
  must match; the runner pushes that ref). Cookie `cgauto/cg_session.txt`, chmod 600, gitignored,
  never committed. Handshake `local_claude_1/door1-night-owner.txt` = `vm-runner` ⇒ laptop cron
  stood down. `Restart=on-abnormal`, deliberately NOT the card's `restart-always`, because
  `always` would retry the submission a HALT exists to prevent. 3 of 10 marks taken unattended.
- **`agent-launcher.service` — LIVE but REVIEW-REJECTED, and the reason is not code.** The
  mechanism is proven end to end: 11:34:08Z it detected a real peer message, debounced, wrote the
  pidfile, launched, logged `wake claude_1 n=1 pid=3107274`. **The session died in 3 s:
  `403 Request not allowed`.** `~/.claude/daemon-auth-status.json` = `auth_required`; `claude -p`
  reproduces the 403 by hand from an interactive shell; `codex exec` 403s too.
  **OWNER ACTION: re-authenticate the VM.** Re-test = one `claude -p` echo returning text.
  Service left active (cap 4/hour, sub-second failures); `LAUNCHER-PAUSED` silences it.

### Things that will bite the next session if forgotten

- **The launcher needs a FULL clone with ALL agent refs.** The card's "shallow ok" is wrong:
  shallow gave **518 phantom would-wakes** (seen-state materialization silently no-ops without
  `refs/remotes/origin/agent/*`) and made the quarantine registry reject as a set
  (`delivery errors 98 · quarantine errors 1 · quarantined 0` vs the true `0 · 0 · 12`).
- **VM disk is 19G and hit 100%**, blocking a deploy with ENOSPC. ~1.2G free now. Eight checkouts
  live here; this recurs.
- **A self-authored message never enters your own actionable set** — so the launcher card's
  self-probe cannot trigger a wake, by construction.
- **Only `ack_for` discharges; `supersedes` is inert.** A `CARD:` is discharged by the delivery
  handoff or a `DEFERRED:` replacement naming it in `ack_for` — never a bare receipt-ack.
- **Never `git commit` without a pathspec while a lint-rejected message is staged.** That is how
  an invalid handoff of mine reached origin and had to be quarantined, which made all 12
  quarantine entries reject for a sweep.
- Sync `scripts/` **and** `tests/` each session; my suite read 105 when it should read **117**.

### The OSC-031 lane

Phase 2 REJECTED (9 de-novo). I proved **pre-build** that Door-1b could not pass and that
two-truths was worse (5–14 vs a gate of 0) — no 240-game panel was spent on either. Owner then
ruled **named-costs**; my package (9 costs named, 15 healed, 53→47, latency, parity) was ACCEPTED
and reproduced byte-identically. **Decider night running**, pre-registered σ_pair 1.5 / bar 1.315
at n=5. KEEP/REVERT is the owner's.

### My open cards

- **Card 2 sentinel build** — blocked on ONE ruling: may `actionable_set()` be extracted into the
  coordinator's `inbox_sweep.py` so `main()` and the sentinel share one path? Not gated by the
  launcher.
- **Card 3 pair-selector Phase 1** — deferred; it is third and its subject rebases if tonight is
  a KEEP.

## Current position (2026-08-19) — gate 1 r4 delivered, sits with codex_1

- **Task `20260818-osc031-forecast-defect-fix`, gate 1 r4 DELIVERED** (`20260819T134755Z`,
  artifact `52bde865`, message `32cfdc9a`). codex_1's r3 verdict was REVISION_REQUIRED on one
  check-that-cannot-fail: `seq2_rows` was **assigned** `PREDICT_TREE_NONE + SEQ2_PASS` and then
  compared against that same expression, and its control called a local `check()` helper the
  production run never invoked. The finding was right and I accepted it without argument.
- **Repair**: the probe now emits a distinct `USEQ2` **entry** row immediately before
  `predict_tree`, under the same `(call, plant)` identity, so the left side of the identity comes
  off the wire. `tally()` is the single counting path, `chain_check()` the single chain checker —
  per-fixture, aggregate, counter controls and observed controls all call it. Three controls
  delete or duplicate **actual emitted rows** and re-derive through `parse_join` + `tally`; each
  runs on the first fixture that can host it and the runner **raises if any never ran**.
- **Every count is byte-identical to r3** — the only diff in `gate1-unified-2026-08-19.json` is
  `probe_sha256` on both subjects. The assigned numbers were not wrong, they were **unmeasured**.
  Resident 120 EVIDENCE_BASED / 530 UNEXPLAINED; candidate 103 / 0; seq2 entry observed
  9,900 = 650 + 9,250 and 7,368 = 103 + 7,265; `later = 0` on both.
- **Declined one thing codex_1 offered and said so**: no observed control deleting a downstream
  terminal, because all four downstream clauses have **zero rows on either subject**, so the case
  could never execute — the same inert-check defect in a new place. Counter control covers that arm.
- **Tooling**: `scripts/lint_outbox.py` was stale on this branch — `origin/main` and
  `agent/claude_1` both lacked the cross-task-reference and deferral-shape gates that
  `local_claude_1` has carried since 2026-08-18. Synced from `origin/agent/local_claude_1`
  (`3448833b`); transport suite 105 pass. **`origin/main` is no longer the freshest `scripts/`** —
  check the coordinator's branch too.
- Inbox: **0 unseen, 0 ack-required** at 13:50Z, cross-checked against peer branch logs.

## Current position (2026-08-17)

- **POOL #3 DELIVERED** (`20260817T171000Z`, artifact `4514db90`, `review_ref:` →
  `codex_1/reviews/h-starve-1-pool1-logging-repair-review-2026-08-17.md`). Pools #1 and #2 are
  CLOSED (GATE_ACCEPTED). Table: **`GOAL_SPLIT_WRONG` 21 · `NO_GOAL_ASSIGNED` 6 · `NOT_STARVED` 4
  · `CANNOT_USE_WORK` 2 · `WORLD_INTERACTION` 0**, plus OSC-026 `NO_ANCHOR_SINGLE_UNIT` (coverage
  state, not a cause). WAIT turns: 2,240 / 521 / — / 349 / 0.
- **The dominant cause is not the generator.** In 21 of 34 the generator DID offer the parked
  troll a real candidate and `select()` discarded it. **That is not a defect claim** — `select()`
  maximises a joint score and the trade may be right; the token records *where* the WAIT came
  from. Whether it is worth changing is pool #6.
- `WORLD_INTERACTION` = 0 is a **measurement**: the 97 manufactured `MOVE→WAIT` land on the
  DANCER (94 in OSC-034 unit 2; anchor is unit 0), one outside its window. `--control` observes
  the arm firing on 94 turns, so the zero is not a dead branch.
- **Two defects of my own in the sweep, both found by reading per-turn records, not totals:** the
  kinds regex read the adjacent `ncand` group (so `NO_GOAL_ASSIGNED` was **unreachable** and 21
  rows were `GOAL_SPLIT_WRONG` by construction — a complete, plausible, wrong table); and
  `NOT_STARVED` cleared any unit that acted once (OSC-023: 73 WAITs of 74). Both now guarded.
- **Token SEMANTICS were never published** — the registry bound spelling only. Mine are in
  `cause_table.py`'s docstring; per-turn attribution ships in the artifact so a different ruling
  needs no re-run.
- **I retracted a false claim of my own about `codex_1`** (`20260817T163500Z`). My status query
  asserted their published work since 12:00Z was spec reviews; it was not — their pool-#2 verdict
  was published 11:23Z, addressed to me, `requires_ack: false`. **My sweep gates on the
  ack-required count, so it CANNOT surface a verdict.** Zero unacknowledged is not zero unread.
  Standing correction: before calling a sweep clean, check whether anything addressed to me is
  newer than my last read, whatever its kind.
- **LOGGING-POINT REPAIR DELIVERED** (`20260817T160500Z`, artifact `8cd55c14`, instrument
  `1384df74`) — `codex_1`'s pool-#2 verdict was REVISION_REQUIRED on one blocker: `HS2` logged
  before `force_unique_door_clear` and `HS2CHOSEN` before `resolve_move_conflicts`, so both could
  record what the selector never received and the engine never got. Taps are now **duplicated**
  (`HS2PRE`/`HS2`, `HS2CHOSENPRE`/`HS2CHOSEN`) so the mutation paths are **observable**, and the
  final-stage names are the ones every consumer already parses.
- **The blocker was material, not cosmetic:** on all 34 situations, door clearing rewrote a
  candidate list **21** unit-turns, conflict resolution rewrote a command **3,517** turns, of which
  **97 are MOVE → WAIT**. A table built from the old tap would have credited those **97
  manufactured WAITs to the generator, which never emitted them**. The other 3,420 are target-only
  (order-vs-landing) and change no attribution.
- **Row totals were UNCHANGED by the repair** (12,981 / 6,800). Coverage counts could never have
  caught this — only reading the emit point could. Everything `codex_1` accepted (anchors, count
  reconciliation, oracle repairs, fail-closure, 34/34 parity) stands.
- Instrument is now **regenerated from the byte-exact resident** by `make_instrumented2.py`, which
  refuses on a non-unique anchor and asserts tap ORDER **positionally**; the previous one was
  hand-edited. `coverage.py --selftest` drives three rejection arms of `check_final_stage` plus a
  positive twin; the tap comparator runs PRE-against-PRE and must find zero differences.
- **Both specs are OWNER-APPROVED and the specs task is CLOSED.** I am the named implementer and
  am **NOT authorized to build**: implementation needs pool #6 **and** an explicit owner go.
- (superseded 16:07Z) **Pool #1 REVISION IS HANDED OFF** and sits with `codex_1` for pool-#2 review: handoff
  `20260817T111300Z` at `37c5b9b3`, instrument pinned `0a95de5b`. Artifact and all four declared
  paths verified reachable on `origin/agent/claude_1`. Parity + coverage since closed at **34/34**
  (`34857fa1`) — the limit I had handed over at 3/34.
- **Since the anchor revision I self-audited and found FOUR more defects of my own**, all fixed and
  each observed firing: `PLANT` eligibility was **always true** for any carrying unit
  (`any(c in reach for c in walkable)` — `reach` is a BFS *over* walkable from the unit's own cell);
  `BANK` rested on `td.orth_neighbors` behind a `hasattr` guard and **that helper does not exist**,
  so the predicate silently weakened; `check_parity()` had **never rejected anything** (now observed
  rejecting a deliberately different bot); and `UNRULED_SHAPE` had **never executed** (now observed
  on an unknown kind and on a blocker cell matching no own unit).
- **The deadlock that cost two hours was mine.** I reported "awaiting acceptance" for two hours
  while never sending the pinned handoff `codex_1` was waiting for; each side believed it was
  waiting on the other. **Self-audit is not a substitute for the review gate — ship, then audit.**
- (superseded 12:30Z) **Pool #1 (instrument repairs) is REOPENED**, not complete. I declared it complete while two
  rulings addressed to me sat unread — the transport did not fail, I did not sweep before claiming
  done. **Rule I now hold: sweep immediately before any handoff that claims completion.**
- Anchor rule **revised to the ruled per-kind mapping** (`5802e357`): D1-with-blocker → blocker
  unit; D1 blocker-less pair → unique non-dancer; D1 single-unit → honest no-anchor (OSC-026);
  **`P4_STALL` → `window.unit` ITSELF** (my uniform "not the dancer" rule excluded the subject in
  all four stalls); anything else → `UNRULED_SHAPE`, fail-closed. 0 fall-throughs.
- Count reconciled: **3 single-unit situations** (OSC-026/032/033) but **1 no-anchor state**
  (OSC-026) — the other two are stalls that now anchor on the dancer.
- Other four repairs delivered but **not silently accepted**: eligible-action oracle with both
  charter arms observed firing each beside a positive twin (`f9748283`); candidate-kind and
  chosen-action logging; exact one-row-per-turn coverage with duplicate rejection; **runner parity
  PROVEN** byte-identical to `regression_tests.run_binary_custom` (`97714f13`).
- **Pool #3 not started** and must not start before `codex_1`'s pool-#2 acceptance. It serializes
  exactly `NO_GOAL_ASSIGNED` / `GOAL_SPLIT_WRONG` / `WORLD_INTERACTION` / `CANNOT_USE_WORK` /
  `NOT_STARVED` and carries `review_ref:`. **I will not map old labels onto these by inference.**
- **T-1 is FROZEN** for me; half-swap fixture is recorded debt.
- Transport: WIP limit (one in-flight ack-requiring handoff per task) and the evidence gate
  (`review_ref:` on any cause label) are machine-enforced. `scripts/` drifts on this branch —
  sync from `origin/main` every session; `pool_status.py` was missing this morning.

## The error pattern this week, stated so it is not repeated

Three published causal claims, each resting on a proxy I had not validated: all-WAIT for "no work
offered", geometric reachability for "work available", a frozen world for a live one. **Each time
the direction felt obvious and each time the proxy was the whole argument.** Plus three inert
checks shipped (viewer inference-marking, harness detector clause, stage-2 reachability model),
each caught only by a negative control, never by reading the code.

- (superseded) Updated UTC: 2026-08-15T19:39:00Z (REAL clock, `date -u`)
- **VIEWER REV 2 — all four `codex_1` blockers fixed** (`e29cf6bd`, ack `86e2f6e4`). **Blocker 1 was a real data-labelling bug I shipped:** inventory columns as `PLUM, APPLE, LEMON, BANANA, ORANGE, WOOD` where the subject's own `pub const` declarations (`:11-16`) say `PLUM, LEMON, APPLE, BANANA, IRON, WOOD` — two fruits transposed and `ORANGE` invented where the authority has `IRON`. Every inventory and carry column on all 34 pages was wrong. **I asserted a label instead of deriving one** — everything else on the page was derived and machine-checked; this one list I typed from memory. `check_slot_order()` now parses the constants from the subject and fails the build on disagreement, with a control reproducing my exact wrong order. Also fixed: frozen evidence rendered (mechanism, blocker state/cell, unresolved, provenance) with the blocker cell marked; **frame 0 is now the ENTRY state** — entry is the only exact board state and my first build applied turn one's command before rendering, so the one ground-truth frame was never shown; and the ordered cell now has its own mark, separate from the assumed arrival. Self-test 11 → **23 cases**. Visual layer still unverified by execution and rev 2 adds three new mark types, so a human look is **more** necessary than before.
- **P-1 INCREMENT 2a DELIVERED** (`e43d000b`, handoff `20260815T193500Z`): the required-site inventory **derived from the subject, never from `SITES`** — the circularity `codex_1` named. **249 §5.4-required sites; the registry names 132 (53%), 117 unnamed.** GEN 22/79, TERM 12/20, FILTER 52/76, EARLYRET 34/58, ARBITRATE 12/16. Independence is *tested*: enumeration is byte-identical with `SITES` cut to 3, and coverage falls 132 → 13. **`endgame_candidates` (`:1233`) is absent from the registry entirely** — the generator the D3 appendix places C2/C3 inside, holding 3 unnamed score-term sites; `idle_harvest_candidates` (`:1340`) absent, a plausible home for `IDLE_HARVEST`, one of the five intents increment 1 flagged as unbound. Offered as **candidate** mappings: status `PROPOSAL_FOR_INDEPENDENT_REVIEW`, and **I will not curate what I derived.** Limits: class matchers are proxies, so 249 is an upper bound; coverage measures NAMING, not semantics.
- **Transport note against myself:** mangled a commit message with an unescaped backtick, then amended an already-pushed commit. Push rejected; **reset to the remote rather than force-pushing** — published history stays immutable.
- (superseded) Updated UTC: 2026-08-15T15:32:00Z (REAL clock, `date -u` — see the stamp-drift correction below)
- **D2 PHASE 1 VIEWER DELIVERED 2026-08-15**, artifact `423b87a1`, handoff `20260815T152700Z`. 34 self-contained pages + index, generated through `load_library(verify=True)` (fails closed), no server, no external asset, keyboard step-through, display-only. Acceptance verified against generated output, not intent: 34 pages, 13 with `+`/`~`, OSC-032/033 as stalls, 32 2-cell cycles, frame indices consistent. **11 guard cases, each observed rejecting — and two caught real defects in my own code.** (1) The inference-marking check was **inert**: it matched the required class against the whole tag, and `data-role="derived-position"` itself contains the substring `derived`, so an unmarked element passed. Only the negative control exposed it. (2) The opponent was drawn **hollow**, the same treatment as inference, while the legend claimed "solid red circle" — ground truth and assumption looked alike. **No referee re-implementation:** no predicted landing is computed, because a BFS/speed mirror that disagrees with `engine.rs` is worse than no mirror. **Known limit, stated not papered over: no browser on this host, so the visual layer is unverified by execution and needs one human look before the first live session.**
- **P-1 INCREMENT 1 RELABELLED `PARTIAL_FOUNDATION`; acceptance item 1 REOPENED** (`codex_1` review `155d8dd8`, relabel `6701aa16`, ack `453361d3`). **I reproduced both of their claims by execution before accepting**: relabelling `GEN_FRUIT_CANDIDATES`'s intent `HARVEST_FRUIT` → `MINE_IRON` gives **0 failures**, and deleting three sites outright gives **0 failures**. Withdrawn: "this is rollout step 1", "this closes item 1", and "`validate_registry()` closes the wrong-at-freeze hole" — it closes only the *syntactic* subset. The registry is a **versioned partial**: no `FILTER_*`/`TERM_*` ids, so adding required sites will change `source_registry_sha256`. `STATUS`/`SEMANTIC_GAPS` now ride **inside the frozen JSON** so the label survives reading the artifact without its source. Guard suite untouched and green (26 cases, 21/21 types firing). **The recurring lesson, twice in one day: an accurate caveat lower down does not repair an overclaim in the summary — the summary is what gets quoted. Naming a gap is not pricing it.**
- **Before step 1 can genuinely freeze:** a required-site inventory derived *mechanically from the subject*, not from `SITES` (deriving expected coverage from the thing being checked is the same circularity `codex_1` killed in the viewer's acceptance check 4), published as a proposal and checked by someone who did not write it. **I will not author and then review it.** Sequencing is `local_claude_1`'s.
- Inbox clean, sweep exit 0, 0 unacknowledged (2026-08-15T15:32Z). Acked this cycle: owner rulings 3–5 (`f408b5c0`, with the materiality-floor false-stop risk quantified — **14.6% chance of stopping as "immaterial" at a true Δ of 2.0, n=5/arm**), D2 scope agreed (`9c207db8`), the two `codex_1` reviews (`453361d3`). Claim `c5f1add3`.
- **P-1 INCREMENT 1 DELIVERED 2026-08-15, artifact `ef76ab54`, handoff `20260815T054700Z` at `96f50105`.** Rollout step 1 / acceptance item 1 of the frozen Decision Packet contract: §4 envelope as code (`check_envelope`), §5.1–5.4 registries code-owned with prose as a generated projection, 22 source sites pinned by `start_line`, drift guard. **26 self-test cases, 21/21 declared failure types observed firing**, coverage computed from what the checkers actually emitted; the coverage assertion itself verified failing on an unreachable declared type. Subject byte-exact `98628e98…` before and after. **Two guards existed only on paper until this pass:** `SITE_MISSING` had no control at all, and `SPAN_CHANGED` was masked by `SITE_MOVED` in a shared any-of case — both now have their own controls. **The design point worth re-reading: drift checking cannot catch a registry that was wrong at freeze time**, because the frozen and live copies are built by the same code, so `validate_registry()` checks the registry against the *subject* instead. NOT complete and does not claim to be: 22 sites of 79 fn definitions, no `FILTER_*`/`TERM_*` ids, all 13 intents carry null predicates with `predicate_status: UNSPECIFIED`, 16 of 17 acceptance items open.
- **V1 CONCURRED AND MY P-2 SENTENCE WITHDRAWN (2026-08-15, ack `c4cf77dd`).** `codex_1`'s D2/D3 review is `REVISION_REQUIRED` and its blocking V1 lands on my own P-2 wording: I wrote *"own-side reconstruction is sound … replaying command lines will not hit a hole"* on the strength of command **contiguity**. Contiguity is a fact about the command record; positions are a different quantity. Verified in the authority, not taken on trust — `engine.rs` (`7c240abf…`) `next_cell` returns the target only `if d <= speed`, so a distant `MOVE` lands intermediate, and simultaneous resolution against an unrecorded opponent can move it again. **My own counter-proposal item 4 stated the correct rule and my summary line four paragraphs earlier contradicted it: a caveat further down the page does not repair an overclaim at the top.** Phase 1, if built, renders verbatim command / command target / *predicted* position as three distinct classes, every side panel stamped `at entry`.
- Inbox clean, sweep exit 0, 0 unacknowledged (2026-08-15T05:55Z). Acked this cycle: two `codex_1` claims (`30dfdad9`), two `codex_1` review handoffs (`c4cf77dd`). Working checkout is `/home/tarstars/prj/troll_farm-plan-agent`; `scripts/` verified in sync with `origin/main` this session.
- State: **inbox clean, sweep exit 0, 0 unacknowledged, 0 delivery errors.** Three `policy` messages processed this cycle: the two quarantine adjudications (`20260812T193500Z` superseded by `20260812T193800Z`) and the **bounded arena lease `20260812T201400Z`, ACCEPTED and not yet started**. Acks at `5c753f9f`, `26afe667`, `85045fed`.
- **ARENA LEASE COMPLETE 2026-08-13T06:43Z — all five steps delivered, authority reverted to `local_claude_1`.** Final handoff `20260813T064318Z`, artifact `a890dfa9`, published `cdbc5800`. **Pooled within-source SD = 1.501** score points, 95% CI [1.049, 2.634], 4 families / 14 mature observations / 10 d.o.f. — up 37% from 1.098, and the CI's lower bound now sits *above* the old point estimate. Campaign family n=6: [19.77, 22.46, 23.39, 23.73, 24.76, 24.90], range 5.13 (2–3× every other family). **`docs/STATE.md` §3's ±0.5–1.0 band does not survive**; a ≥+1.0 gate needs 5 runs per arm, not 3. Run 4 = `41129543` / agent `6614096`, owner-authorized in session. **Re-deployment noise and ladder drift are confounded and no analysis of these six observations separates them** — the runs are sequential, never contemporaneous, spanning 08-04→08-13 while the field grew 139→147.
- **The stale arena-room row is the story of this campaign.** `6604529 / field 140 / 22.46` appeared **six times** across two days, including on three consecutive *complete* 160/160 reads of run 4. **A gate on `matching_finished == 160` alone would have recorded 22.46 — another deployment's score — as run 4's terminal observation, with 0 pending, 0 unexpected rows and 0 fetch failures.** Gate on `identity_clean` AND the process exit status; `field total 140` is the reliable tell. Related repair `a9abae5f`: `submission_history.py` validated `filtered_ladder.agent_id` but never `arena.agent_id`, then read score/rank/field from that unchecked block — silent corruption with `identity_faults: 0` and maturity `terminal`. Two tests, both verified to fail first. `codex_1` reviews; I authored it.
- **Read the label, then read the content — the content wins.** I escalated a semantics question about run 2 that did not need to exist: `run2-checkpoint-initial.json` was a complete 160/160 clean terminal observation (23.73) sitting in the same directory the whole time. I had filtered on the `*-terminal` filename role and never opened it. Maturity is keyed on `matching_finished`/`matching_pending`/`identity_clean`, never on a role string.
- **`publish_outbox.sh` fetched only `origin/$BRANCH` until 2026-08-13** — so publishing could never surface inbound mail, and a policy addressed to me sat unread for 8h28m while I executed the task it governed. Fixed on trunk (`git fetch origin`, all refs), synced here at `5596941d`. **Binding: any Arena mutation requires a full `--fetch` sweep with its exit examined within ~10 minutes of the call.** Publishing is not freshness.
- (Superseded) **ARENA LEASE HELD (bounded, reverts on final handoff)**: σ campaign steps 1–5, serialized. Preconditions verified independently — cookie sha `09164093…` mode 600, gitignored + untracked; submission blob = `98628e98…` in three-way agreement with the `--expected-sha256` and the committed sidecar; run-3 interim is the 118-game read (arena 23.61, filtered 23.73, rank 31/147). **Step 2 (run-4 submit, the fourth and LAST budgeted mutation) is held for an explicit owner go** — irreversible, single call, ambiguity → STOP with no retry. Execution-environment gap named to the coordinator: the cookie is in the ~1300-commit-stale `/home/tarstars/prj/troll_farm`, the tooling is at `f7069d16`, and `troll_farm-plan` is detached at `21bd338d`.
- **`scripts/publish_outbox.sh` — the wrapper the coordinator calls binding — was ABSENT from `agent/claude_1`.** `scripts/` was stale against `main` by nine files; synced at `7ec39b4c`, and every message this cycle published through the wrapper with the lint armed. Second silent drift of this directory while the publish gate was defined as one of its scripts. **Verify the gate exists before trusting it; nothing on screen announces its absence.**
- **`requires_ack: false` does not exempt a `policy` message.** `policy` is in `ACK_REQUIRED_KINDS` (`scripts/inbox_sweep.py:78`) and the set is applied after the field (`:289`), so both adjudications declared `requires_ack: false` and both were correctly reported ack-required. Raised with the coordinator; needs a ruling.
- **250 messages remain `new (unseen)` and the watermark was deliberately NOT advanced** — protocol forbids blanket timestamp-marking a backlog before a pushed legacy-backlog audit. That audit remains the outstanding transport work.
- **Filename stamps ≠ real time.** Messages named `20260813T*` have real commit dates of 08-09; the M3a repair, the transport review and bite-test r2 are all ancestors of the current tip despite later-looking names. Trust `git log`, never the filename.
- (Prior cycle) **G2 delivered and accepted** (substance ACCEPTED by `codex_1`; the `task_id` provenance revision is published at `6fbacca4` and awaits the coordinator's integration, at which point G2 closes). **G6 started: all four D-7 branches pinned, 4 of 19.** Collector-v2 tasks both in `review`, all findings ACCEPTED.
- **G6 COMPLETE 2026-08-13 — 19 of 19 actionable branches resolved** (artifact `bb845da5`, handoff `20260813T200014Z` at `dac57f73`). Whole-manifest mutation: **51 caught / 25→13 survived of 64**, `caught_by_expected` **51/51**, control green. Ledger `impl_validity` **33 PINNED, 3 PARTIAL, 6 UNPINNED, 5 NO_FIXTURE** — from **12 PINNED / 22 NO_FIXTURE** when G6 opened; mutation from **21/64** at the audit's first publication. Groups: D-7 (4) → 29, D-8 (3+1) → 33, D-5 (3+2) → 39, D-6 (3+1) → 46, D-1/D-3/D-4 (4+1) → **51**. Detector suite 67 tests OK; audit self-tests 13 passed. **D-9 (b)/(c)/(d) still parked on the c5 instrument ruling, which is assigned to me after G6 and is now the natural next item.**
  - **TWO BRANCHES ARE UNPINNABLE — EQUIVALENT MUTANTS, PROVEN NOT ASSERTED.** **D-8 (b)** `plant kind == BANANA`: reached only inside `c in alive_per_turn[t]`, and `own_banana_history` builds that set from the *same* `state(t)` with the same kind filter. **D-4 (e)** DROP-at-door commitment start: `DROP` is not in `D4_BANNED_VERBS` so no episode can be raised on that turn, `executed_drop` clears `committed` on the same turn, and the only residue `nd_run = 0` is set by every commitment start anyway. Each proved by construction **and** by differential (**0/416 probe-corpus traces differ**). **Both left COUNTED and their rows at `NO_FIXTURE` on purpose** — excluding them moves the headline 51/64 → 51/62, i.e. in my own favour, so the disposition is referred to the coordinator. Each carries a test pinning the *reasoning*, so if the surrounding code changes the branch fails loudly.
  - **D-6 clause (a1) is close to inert and is reported, not repaired**: `min_own` is always 0 at a PLANT event because the planter stands on the cell it plants, so `opp_h <= min_own` can only fire when an opponent harvester shares that exact square. Pinnable that way, but not what the spec text suggests. Detector-semantics question; G6 changes no predicate.
  - **Nine of the newly caught mutants were incidental** — killed by fixtures aimed elsewhere. Each was traced, its `owner_test_classes` extended, and reported; `caught_by_expected` was short at every group until they were named. Two recurring levers: **asserting an exact boundary value constrains every term in the formula that produces it** (the D-5 deadline pair also pinned the cutoff arithmetic), and **asserting a value sits just OUTSIDE a bound constrains how far that bound can move** (the D-6 speed pair also pinned the `<= 2` clause).
  - **A test asserting SILENCE needs a companion proving the noise was available.** The D-1 progress clauses suppress episodes rather than raise them, so their fixtures assert absence; `TestD1Uncovered` therefore opens by showing the same pacing with no progress event *does* fire.
  - Boundaries verified not asserted at every group: no predicate touched, nothing under `rust/`, `yamo_orchard_live.rs` byte-exact sha256 `fff6669b0bc0b15b…`. Pinned-source drift re-pinned every time, never `--allow-drift`.
- **Owner plain-language policy in force (`20260813T191500Z`, acked `4b011941`)**: anything the owner reads opens with a sentence a non-specialist can follow, spells out what a thing IS before its code name, and gives numbers meaning. Technical artifacts keep full precision; the plain summary goes in the message that carries them.
- **THREE OF MY OWN GUARDS FAILED TODAY — read before publishing anything.** (1) **Message stamps ran up to +42 min ahead** of the clock because I incremented them by narrative instead of reading `date -u`; my drift put a coordinator reply *before* the message it answered. (2) **I published an invalid `correction` with an empty `supersedes`** — the identical defect that quarantined `20260807T113000Z`. (3) **I broke the publish gate**: `lint …; echo "LINT=$?"; git add … && commit && push` chains off `echo`, which always succeeds, so the gate ran and gated nothing. Worse, once pushed the message becomes *published* and default lint **skips it** — exit 0, defect invisible. Use `lint … || exit 1`, and `--all` after publishing. Retiring a message also **retires every ack it discharged**: carry `ack_for` forward when superseding.
- **`project_host`'s cron fires 02:17 UTC, not 05:17** (crontab `17 5` on Europe/Moscow) and skipped Aug 11-12. My unit comment and reports are corrected: 05:47 is right, but by luck not by the stated reasoning.
- **First unattended collector run** (2026-08-12 05:47): 6,295 candidates, 6,295 held, **0 fetched, 0 dropped**, exit 0 — verified as coverage not blindness (max held id `898583715` > max live-window id `898550181`). **Cut-over caution: with the platform quiet AND the reference cron intermittent, the seven-day criterion measures neither collector.**
- **Three measured facts to carry:** replay availability tracks participant battle windows, not age; the bucket grant blocks deletion but NOT overwriting (append-only is enforced by `If-None-Match: *` in our code); *missing from a day's manifests* (352) is a different question from *absent from S3* (**0**).
- Role: contributor + **execution reviewer** on every artifact. Coordinator/integrator/arena controller AND detector-semantics owner = `local_claude_1`. **`chatgpt_1` and `chatgpt_2` are unreachable** (owner ruling 2026-08-12). `codex_1` is a NEW agent (canonical `agent/codex_1`, onboarded 2026-08-09) and is **not** `local_codex_1`, which is dormant since 2026-08-06.
- Branch: agent/claude_1-banana-restoration-r2; canonical agent/claude_1 at `7366e1cf`. Tooling `inbox_sweep.py` `be8251c4…`, `lint_outbox.py` `f3c47b70…` (synced from `main` twice this cycle — `main` moved under me).
- **Read `claude_1/SESSION-FINDINGS-2026-08-07-to-11.md` before acting.** It carries the programme state, the measured findings, and the error patterns. It predates the 08-12 unblock below.

## Blocking state

- **The TRAIN/referee blocker is CLEARED.** r4 accepted by `chatgpt_1` for the c5 execution layer; B1 closed by `local_claude_1` through independent execution in a second checkout (7/7 artifact digests, `engine.rs` `7c240abf` untouched, panel 163 OK, pre-review 24 OK, mutation 16/16 caught, and floor packets **row-level `IDENTICAL`** to committed `evidence-r4/` — agreement on *which* games block, not just the total). The r4 panel is merged to `main`: `main:claude_1/pipeline/fuzz_panel.py` = `d8900abf31dd030d…`, 33 TRAIN references. `main` was pre-r4 until 08-12, so anything measured from `main` before then used the broken referee.
- **This does NOT authorize verdicts.** `chatgpt_1` holds I-30 at `GATE_UNREADY / MEASURED_UNTHRESHOLDED` and states plainly: **no detector branch is authorized for candidate acceptance, and no I-30 PASS, FAIL, threshold or candidate verdict is accepted.** Do not read the r4 acceptance as a gate opening.
- Instrument `fuzz-panel/5` · corpus `c5-two-player-phase-merged-2026-08-11`. **Floor (parent vs itself) = 118/240. Candidate run (banana `eac2eb36` vs parent) = 121/240.** Different quantities; `run_identity` is machine-checked. `118/240` is quotable **only** with r4's binding restriction attached: TRAIN is witnessed in 2 games (1 spawn each), and 10 of 17 repaired rules have no corpus witness — those are pinned by unit tests, the two-oracle differential and the mutation drive, never by the floor.

## Reviewers — resolved, and degraded on purpose

`chatgpt_1` held every review slot below and is unreachable. `codex_1` claimed
`20260807-gate-architecture-review` and the M3a idle-blocker replication, and declined the rest.
`local_claude_1` ruled (`20260812T211000Z`, superseding `20260812T204000Z`): **three of the four
reviews had already been delivered before `chatgpt_1` went dark**, so the vacancy is the *re-review
of my repairs*, not of my current work — I am not blocked.

Standing terms of that ruling, all still in force:

- **I do not review my own repairs.** Not negotiable, and it is why I am not the check on anything
  below that I author.
- Anything `local_claude_1` reviews alone is labelled **`SINGLE_REVIEWER_DEGRADED`**; it is the
  coordinator, so it adds a second look, not a second opinion.
- **Nothing closes as fully `ACCEPTED` under a single reviewer without the owner's sign-off.**
- Every `chatgpt_1` disposition is **`RECORDED / UNREPLICATED`** until reproduced by execution here
  — they rest on self-run Actions jobs by the reviewing agent, the same evidence class as the
  quarantined 2026-08-06 fabrication.
- `local_claude_1` **cannot** review `20260807-transport-quarantine-and-outbox-lint` (it authored
  it), so that task still needs a second reviewer; I am one of the two required and the other slot
  is unfilled.

Worth remembering: I once treated a reassignment table as a settled allocation. It was an *offer* —
a reassignment is not complete until the receiving agent claims it, and the decline was already
published when I wrote. **Re-sweep between reading an allocation and acting on it.**

## Open dispositions requiring my revision work

- **M3a correct-subject** — **REPAIRED AND DELIVERED** 2026-08-13, handoff `20260813T003000Z`, artifact `ae701fc4`. Each panel config now carries `source_git = {commit, path}` on an immutable 40-hex commit; the replay materialises the blob and re-checks it against the config's own `sha256` before compiling; corpus skips are evaluated before compilation; no absolute host path remains in either config's data fields. `fuzz_panel.py` untouched (`d8900abf…` is the accepted referee digest). Verified against a control that failed first: with the scratch directory masked, pre-repair reproduces `chatgpt_1`'s `PanelError` verbatim and repaired gives 94 tests OK / **34 of 34 byte-for-byte**. New `TestSourcesArePortable` (6 tests, default suite, no `rustc`) makes a recurrence a failure now. **Still open and not mine:** the M3b substrate selection — the c5 46-episode diagnostic library and the golden v2 record (34 exact D-1 episodes / 32 source games) are different populations and neither may silently replace the other.
- **Bite-test audit r2** — **blockers 1, 2, 4, 5 CLOSED; blocker 3 open.** Handoffs `20260813T030000Z`, `20260813T054000Z`, `20260813T081000Z`; latest artifact `3e5ade1b`.
  - **4** `run_mutations.py` exit status describes the experiment: `1` control not green, `2` incomplete, `0` only when whole; `--only` needs `--partial`. Accepted.
  - **5** 47-branch tallies derived from `branch_ledger.json`; `render_branch_ledger.py --check` compares audit prose to data both ways. Accepted. **The contract-authority tally was never derivable from the table** — now an explicit field.
  - **1** `LIVE` → **`PROBE_SENSITIVE`** with the limit inline everywhere: *changes probe output on generated traces; does NOT establish legal-game reachability.* Results schema bumped to `detector-mutation-results/3`; derived artifacts regenerated, not edited. Measurement unchanged and verified: 64 counted, 21 caught, 43 survived, 30 probe-sensitive survivors.
  - **2** No contention label. `max(speed, 1)` replaced by the engine's own `d <= speed` — **`engine.rs::next_cell` has no floor**, so at speed 0 the authority returns `current`. Three D-3 rows carry `NO_WITNESSED_POPULATION (720 referee games, 3 corpora)`. **Binding wording: zero observed episodes is a statement about this corpus, NOT "the predicate cannot fire."** No D-3 branch is probe-covered.
  - **3** — **substantially unblocked 2026-08-10, not closed.** The owner's strict rule (*no banana manipulation before training the second troll*, threshold 0) **dissolves** D-9 (a)'s affordability question rather than answering it: there is no affordable delay to price when the permitted count is zero. Row (a) is the operative rule, no longer a retired proxy. **I pinned it** (handoff `20260810T111000Z`, artifact `80c3dd63`): it was `UNPINNED` with D9-M1/M2/M3 surviving — a strict rule policed by a detector nobody had shown could tell right from wrong — and three negative tests, each verified to kill its own mutant before being written, take D-9 to **4/4 CAUGHT, 0 survivors**. Overall 21→24 caught; tally 11→12 `PINNED`. **Paired branches (b) `train_late`, (c) `train_missing`, (d) `train_stats_differ` still carry the stale pre-c5 `INSTRUMENT_UNSUPPORTED` label and are NOT addressed** — the rule says nothing about non-banana TRAIN displacement.
- **I-30 rev 3** — **blocker 2 REPAIRED**, handoff `20260813T050000Z`, artifact `7e5c9874`. Owner-freeze chronology is decided by Git ancestry between the decision's commit and an immutable `observation_anchor`; an anchored authority refuses to fall back to timestamps, so an unanchored production run cannot reach `verified`. Demonstrated: the pre-repair analyzer verifies a bound frozen AFTER the observation with **zero reasons**. 105 existing tests still pass + 8 new (all 8 fail pre-repair). **Blocker 1 still open** — `ExecutionValidity` still validates a self-declaration: `referee_sha256` checked for presence only, `verb_manifest_sha256` self-consistent by construction, command counts caller-supplied. Design proposed; awaiting a ruling on whether the verb manifest is *derived from the dispatcher* or *bound to a committed registry of reviewed referee digests*.
- **M2 rev 2** — accepted, nothing owed. **Fast-verification-executor requirements** — **PARKED** by the coordinator: its author is unreachable and nobody inherits an unowned spec. `coordination/tasks/20260811-fast-verification-executor-design.md` is `PROPOSED / BLOCKED ON REQUIREMENTS REVIEW`, owner unassigned.
- **`20260807-transport-quarantine-and-outbox-lint`** — my execution review delivered 2026-08-13, handoff `20260813T012000Z`, artifact `afb6903a`: **`REVISION_REQUIRED`**. Accepted: the 41-message delta is exact, all 41 carry an explicit `ack_for` (verified from raw blobs, not via the tool under review), 92 tests pass, zero regressions. Blocking: `parse_json_list` is unguarded in `collect_my_acks`, so a malformed `ack_for` in the sweeping agent's **own** namespace crashes the sweep with an uncaught `JSONDecodeError` — exiting `1`, which collides with the documented "healthy but unacknowledged" status — and published messages are immutable, so it cannot be repaired without quarantine. No test reaches the changed branch.

## Owed, now unparked by r4

M1 Decision Packet implementation (spec frozen against `98628e98`) · M3b adjudication (needs M1 + valid M3a) · P4 re-do on c5 evidence · D-4 repair · gate revision 3 execution review. **With the owner:** the D89a label; whether to fund a fresh 512-row corpus for U4.

## Do not cite

**My idle-blocker claims are `UNREPLICATED / UNRESOLVED`** (`codex_1`, `20260809T190604Z`, accepted
by me in full). The terminal population of **20 episodes** on subject `98628e98` IS independently
reproduced and may be cited. **Claims 1 (all 20 have an `IDLE` blocker) and 2 (no working-blocker
episode reaches 62 turns) are not** — the base panel carries no per-turn states, so they are
unresolvable from any evidence outside my own library. **The merged repair plan's mover-only
rationale rests on claim 2 and must carry that label wherever cited.** Repair proposed and awaiting
the coordinator's sequencing: commit raw `98628e98` transcripts as a non-library artifact. The
lesson is mine — committing my extraction is not committing the evidence it came from.

The `+12.453/+76.508` D89a split (`UNRESOLVED`, TSVs never committed) · `oscillation-library/` as M3a (it is parent lineage `a8eb3b2b`) · D-9 as `INAPPLICABLE` or "196 false positives" (now `INSTRUMENT_UNSUPPORTED / GATE_UNREADY`) · D-6 as falsified (it is a `CONTRACT AUTHORITY: CONFLICT`) · any floor figure for the ~10 of 17 rules lacking a corpus witness.

## Transport

**Dual-format MANDATORY** (v2 front matter + legacy `- To:` bullets) — a peer was blind to v2 for ten days. **Gate publishes on `lint_outbox.py` EXIT STATUS**, not on grepping its output. Push before citing: *unpushed is unsent*, and a stale remote-tracking ref makes `git merge` a silent no-op. Never `git add -A` — agents share this tree.

**`ack_for` is no longer inert on non-`ack` kinds** (changed 2026-08-12, `f9fc1810`). It used to count only on `type: ack` — I broke that 4x — and now any kind may discharge by naming exact paths. `ack` must still carry a non-empty `ack_for`. **Prefer a separate `ack` anyway:** a busy handoff acking four questions in its front matter is easy for a reader to miss.

**`pytest` is absent from the host but the transport suite requires it** — `tests/test_inbox_sweep.py` does `import pytest`, so `python3 -m unittest` cannot run it. Use `uvx pytest tests/…` (92 pass). The old "use `python3 -m unittest`" guidance holds only for suites that do not import pytest.

**Tooling: `inbox_sweep.py` `be8251c4…`, `lint_outbox.py` `f3c47b70…`, both matching `main`.** `lint_outbox.py` had been **absent from this branch entirely** — the publish gate did not exist where I was publishing from, which is the mechanical cause of all three of my quarantined messages.

**Verify your tool digest against `origin/main` before trusting any sweep — every time, not once.** I went stale twice in one cycle: first at `12b27e9c…`, which reported **56** unacknowledged against the true **16** and printed no quarantine section at all; then again the same day when `main` moved to `be8251c4…` under me, so a handoff I had genuinely acknowledged still showed as outstanding. Nothing on screen announces a stale tool. Re-check after every `main` movement.

**Three of my messages are quarantined** (`20260807T090000Z` non-canonical type, `20260807T113000Z` correction with empty `supersedes`, `20260811T163000Z` handoff pinning a commit lacking two of its own paths). All rejected on transport, not substance; all have verified replacements; no content lost.

**Roster blocker (`20260812T193500Z`) — RAISED AND CLOSED.** The roster naming `codex_1` sat only on
`origin/session-2026-07-01` while both `roster.json`'s own note and `inbox_sweep.py`
(`ROSTER_REF = refs/remotes/origin/main`) treat `main` as the sole authoritative location. Upheld in
full by `local_claude_1`, which reproduced it and fast-forwarded `cff2398c..db0574cf`. Verified:
`origin/main:coordination/roster.json` now carries `unreachable: [chatgpt_1, chatgpt_2]` and
`dormant: [local_codex_1]`. Coordination commits now go to both refs in one action.

**Live pattern to watch — state reaching a ref ahead of the process governing it.** Four instances
this cycle: task records committed but unpushed; the roster on an unread ref; a withdrawal stated in
an `ack`, which carries no `supersedes` and so retires nothing; and `f9fc1810`, whose own commit
subject says *PENDING REVIEW*, already an ancestor of `origin/main`. *Integrated* and *accepted*
are not the same event.

**Watermark deliberately NOT advanced.** 141 messages remain `new (unseen)`. Protocol forbids blanket-marking a backlog by timestamp: actionable messages are acknowledged by exact path (done — 16 of 16, sweep exit 0), and the rest need a pushed legacy-backlog audit before `--mark`. That audit is outstanding.

## Standing constraints

Arena controller: **NO**. `rust/src/bin/yamo_orchard_live.rs` (`fff6669b`) byte-untouchable; `engine.rs` (`7c240abf`) is the authority, not any bot's self-restraint. `trace_detectors.py` is `local_claude_1`'s. No CI anywhere.
