# Last Mile + Basin Jump Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reach verified arena-room rank ≤99 by running single-knob arena cycles (Track A) while building the hoard-then-factory phase mode (Track B) into the champion bot, all through a 4-stage subagent pipeline.

**Architecture:** One bot, two metas: `Meta::Tempo` (today's champion, byte-identical — equality-enforced) and `Meta::Scale` (`Phase::Hoard` → `Phase::Factory`), expressed as phase-parameterized value bands in the planner layer. Candidates flow builder → gatekeeper → arena-runner → analyst; the arena is one serialized slot.

**Tech Stack:** Rust (edition 2021, stdlib-only bot), Python tooling under `uv run --no-sync python`, CodinGame REST API.

## Global Constraints

- Bot crate: `/home/tarstars/prj/troll_farm/rust` (bin `bot`, lib module `troll_farm::botmain`). All cargo commands run there; all `cgauto/*.py` run from `/home/tarstars/prj/troll_farm`.
- Champion (do not regress): `cgauto/submissions/v1.28.2-steady2.{rs,min.rs}` — live band 19.0-19.2, rank 111-115. `api_submit.py` default must always point at the reigning champion.
- Every candidate passes, in order: `cargo test --release` (20+ suites), self-determinism equality, bundle → `rustc --edition 2021` compile (copy to a dot-free filename first), minify < 100 000 B, and (Tempo-selected builds) flag-off stream-equality vs the champion binary.
- Equality harness: `rust/target/release/equality <botA> <botB> <seeds> [max_turns] [opp]`; opponent must be a bot binary or `WAIT`, never a lib strategy.
- Arena discipline: same-hour bracket read before submit; verdict = two ARENA-ROOM reads ≥15 min apart moving <0.1; keep if ≥ bracket−0.2, revert to champion otherwise; record every verdict in `docs/silver-experiment-log.md`.
- Play-API budget ≈150 games/day; gatekeeper batches ≤14 games per candidate; on HTTP 422 wait ≥15 min.
- Version naming: `1.31.0-liq44`, `1.32.0-phases`, `1.33.0-hoard`, `1.34.0-factory`, `1.35.0-scale`; bump `const VERSION` in `src/botmain.rs`, freeze artifacts to `cgauto/submissions/<name>.{rs,min.rs}`.
- Commits after every green step; trailer: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

---

### Task 0: Pipeline conventions + stage briefs

**Files:**
- Create: `docs/superpowers/plans/pipeline-briefs.md`
- Create: `data/candidates/.gitkeep`

**Interfaces:**
- Produces: the four agent-brief templates (builder/gatekeeper/arena-runner/analyst) that Tasks 1-6 dispatch with; the candidate directory contract `data/candidates/<version>/{<version>.rs,<version>.min.rs,report.md}`.

- [ ] **Step 1: Write the briefs file** with this exact content (it is the pipeline's infrastructure — agents start cold and receive one of these briefs plus a task-specific delta):

````markdown
# Pipeline stage briefs (copy into Agent prompts; fill {PLACEHOLDERS})

## Common context (prepend to every brief)
Repo: /home/tarstars/prj/troll_farm (bot crate in rust/, tools in cgauto/, run python via
`uv run --no-sync python`). The bot: rust/src/botmain.rs + rust/src/botmain/{state,motion,
tactics,planner}.rs; submission = tools/bundle.py (module inliner) → tools/minify.py.
Champion: cgauto/submissions/v1.28.2-steady2.min.rs (arena 19.0-19.2). Read
docs/ROADMAP.md §2 (iron rules) before acting. NEVER submit to the arena unless you are the
arena-runner. Record everything you conclude in your final report.

## builder brief
You implement ONE candidate: {CHANGE DESCRIPTION + exact code/diff}. Work in the current
tree (worktree if instructed). Steps: (1) apply the change; (2) `cd rust && cargo build
--release && cargo test --release` — all suites green; (3) self-determinism:
`./target/release/equality target/release/bot target/release/bot 8 300 target/release/bot`
must print EQUAL; (4) bundle+gates: `uv run --no-sync python tools/bundle.py`, copy
target/refactor/bundled.rs to a dot-free name, `rustc --edition 2021 -O` it (must compile),
`uv run --no-sync python tools/minify.py target/refactor/bundled.rs <out>` (<100000 bytes),
compile the minified copy too; (5) {EXTRA GATE, e.g. flag-off equality vs champion};
(6) freeze: cp bundled.rs and the minified file to cgauto/submissions/{VERSION}.rs/.min.rs
and to data/candidates/{VERSION}/; (7) write data/candidates/{VERSION}/report.md: what
changed, every gate command + its output line, size, anomalies. Commit with the trailer.

## gatekeeper brief
You gate candidate {VERSION} (files in data/candidates/{VERSION}/). Build the DEBUG probe:
sed 's/const DEBUG: bool = false;/const DEBUG: bool = true;/' on the candidate .rs →
minify → rustc-compile-check → keep the DEBUG .min.rs path. Play: `uv run --no-sync python
cgauto/collect_debug_games.py <dbg.min.rs> boss 8` then vs field agentIds {FIELD_IDS}
(2 games each; get IDs via `cgauto/field_targets.py 95 130`; include ≥1 denial-style
opponent: mikdiet 6480914 or plcc 6480966, and ≥1 ≥19.6 player). Read: `cgauto/ramp.py
--last 8` (wood ≥45, t300 delta vs −15.3 baseline), telemetry from the newest .raw files
(grep @TFFARM / @TFPHASE): {PHASE_INVARIANTS}. Append a verdict section (PASS/FAIL + all
numbers) to data/candidates/{VERSION}/report.md. FAIL on: wood <40, crater signature
(delta worse than −15), invariant violation, or any game crash.

## arena-runner brief
You own the ONE arena slot for candidate {VERSION} (already gated PASS). Procedure:
(1) bracket read: `uv run --no-sync python cgauto/cg_rank.py` — record the ARENA-ROOM line;
(2) submit: `uv run --no-sync python cgauto/api_submit.py cgauto/submissions/{VERSION}.min.rs`
(expect SUBMIT-OK); (3) wait ~20 min, read; wait ~15 min, read; wait ~15 min, read — converged
when two reads ≥15 min apart move <0.1; (4) verdict: keep if converged score ≥ bracket−0.2,
else `api_submit.py cgauto/submissions/v1.28.2-steady2.min.rs` (revert) and verify the
champion reconverges (~40 min, one read ≥18.7); (5) if KEPT and it beats the champion's band,
update the default path inside cgauto/api_submit.py to {VERSION}.min.rs; (6) append the
verdict (all reads with timestamps) to docs/silver-experiment-log.md and to
data/candidates/{VERSION}/report.md. Never leave the arena on a regressed bot.

## analyst brief
The arena verdict for {VERSION} is {VERDICT}. Run `uv run --no-sync python cgauto/battles.py
40`, summarize: win rate + margins by opponent band, new blowout patterns (fetch 1-2 loss
replays via gameResult/findByGameId — see cgauto/battles.py source for the call — and count
both players' command mixes per 75-turn phase). Compare against the 2026-07-07 00:55 census
(17/35, +4 avg, 100-150 band). Deliver: (a) 5-line summary, (b) a re-ranked hypothesis
queue (append to docs/silver-experiment-log.md), (c) whether the NEXT queued candidate is
still the best bet.
````

- [ ] **Step 2: Create the candidates dir and commit**

```bash
mkdir -p /home/tarstars/prj/troll_farm/data/candidates && touch /home/tarstars/prj/troll_farm/data/candidates/.gitkeep
cd /home/tarstars/prj/troll_farm && git add docs/superpowers/plans/pipeline-briefs.md data/candidates/.gitkeep
git commit -m "pipeline: stage briefs + candidate dir contract

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 1 (A1): GE_LIQ_T 34→44 — earlier endgame banking

**Files:**
- Modify: `rust/src/botmain.rs` (const GE_LIQ_T, const VERSION)
- Create: `cgauto/submissions/v1.31.0-liq44.{rs,min.rs}`, `data/candidates/v1.31.0-liq44/`

**Interfaces:**
- Consumes: pipeline briefs (Task 0). Produces: an arena verdict; no code consumed by later tasks (pure knob).

- [ ] **Step 1 (builder): apply the knob**

```bash
cd /home/tarstars/prj/troll_farm/rust
sed -i 's/const GE_LIQ_T: i32 = 34;.*/const GE_LIQ_T: i32 = 44; \/\/ A1: bank standing value earlier (census: +4-margin coin-flips vs peers)/' src/botmain.rs
sed -i 's/const VERSION: &str = "1.28.3-sticky6".*/const VERSION: \&str = "1.31.0-liq44"; \/\/ A1 liquidation-timing knob/' src/botmain.rs
```

- [ ] **Step 2 (builder): local gates** — run the builder brief's steps 2-4 verbatim; all must pass (20 suites, EQUAL, compile, <100 KB).
- [ ] **Step 3 (builder): freeze + report + commit** per brief steps 6-7.
- [ ] **Step 4 (gatekeeper): dispatch with** `{VERSION}=v1.31.0-liq44`, `{FIELD_IDS}=6480914,6480966`, `{PHASE_INVARIANTS}=none (Tempo knob; check @TFFARM flaps stay ≤15)`.
- [ ] **Step 5 (arena-runner): dispatch on PASS.** Keep/revert per brief.
- [ ] **Step 6 (analyst): dispatch with the verdict.** Queue update.

---

### Task 2 (B1): phase skeleton — Meta/Phase enums, zero behavior change

**Files:**
- Modify: `rust/src/botmain/tactics.rs` (Meta/Phase types, Plan.phase field)
- Modify: `rust/src/botmain.rs` (GE_META const, VERSION, @TFPHASE telemetry)
- Test: `rust/tests/phase_skeleton.rs`

**Interfaces:**
- Produces: `pub enum Meta { Tempo, Scale }`, `pub enum Phase { Tempo, Hoard, Factory }`, `pub const T_SWITCH: i32 = 140;` (in tactics.rs), `Plan.phase: Phase`; consumed by Tasks 3-4 (planner band gating).

- [ ] **Step 1: Write the failing test** at `rust/tests/phase_skeleton.rs`:

```rust
//! B1: phase skeleton — Tempo meta must be phase-inert; Scale schedules Hoard→Factory.
use troll_farm::botmain::tactics::{phase_for, Meta, Phase, T_SWITCH};

#[test]
fn tempo_is_always_tempo() {
    for t in [1, 50, T_SWITCH, 299] {
        assert_eq!(phase_for(Meta::Tempo, t), Phase::Tempo);
    }
}

#[test]
fn scale_switches_at_t_switch() {
    assert_eq!(phase_for(Meta::Scale, 1), Phase::Hoard);
    assert_eq!(phase_for(Meta::Scale, T_SWITCH - 1), Phase::Hoard);
    assert_eq!(phase_for(Meta::Scale, T_SWITCH), Phase::Factory);
    assert_eq!(phase_for(Meta::Scale, 299), Phase::Factory);
}
```

- [ ] **Step 2: Run it — must fail** (`cargo test --release --test phase_skeleton` → compile error: no `Meta`).
- [ ] **Step 3: Implement** in `rust/src/botmain/tactics.rs` (top, after the imports):

```rust
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Meta { Tempo, Scale }

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Phase { Tempo, Hoard, Factory }

/// Scale meta: hoard (no felling, bank the wallet) until T_SWITCH, then the factory.
pub const T_SWITCH: i32 = 140;

pub fn phase_for(meta: Meta, turn: i32) -> Phase {
    match meta {
        Meta::Tempo => Phase::Tempo,
        Meta::Scale => {
            if turn < T_SWITCH { Phase::Hoard } else { Phase::Factory }
        }
    }
}
```

Add to `Plan`: field `pub phase: Phase,`; in `plan()`: `let phase = phase_for(super::GE_META, state.turn);` and `phase` in the struct literal. In `rust/src/botmain.rs` next to the GE_ consts: `const GE_META: tactics::Meta = tactics::Meta::Tempo;` and bump VERSION to `"1.32.0-phases"`. Add telemetry inside the existing `if DEBUG && state.turn % 5 == 0` block in `decide_elite`: extend the eprintln with ` phase={:?}` and `plan.phase`.

- [ ] **Step 4: Tests pass** (`cargo test --release` — all suites incl. the new one; fix planner_tasks.rs `Plan{}` literals by adding `phase: Phase::Tempo` — import `troll_farm::botmain::tactics::Phase`).
- [ ] **Step 5: THE gate — flag-off equality vs the champion.** Build, then:

```bash
cd /home/tarstars/prj/troll_farm/rust
cp ../cgauto/submissions/v1.28.2-steady2.min.rs /tmp/champ.rs
rustc --edition 2021 -O /tmp/champ.rs -o /tmp/champ_bin
sed 's/1.32.0-phases/1.28.2-steady2/' target/refactor/bundled.rs > /tmp/lm.rs  # label-match
# (run tools/bundle.py first if target/refactor/bundled.rs is stale)
rustc --edition 2021 -O /tmp/lm.rs -o /tmp/lm_bin
./target/release/equality /tmp/champ_bin /tmp/lm_bin 25 300 /tmp/champ_bin
```

Expected: `EQUAL: 50 games ... identical`. The skeleton ships ZERO behavior change.
- [ ] **Step 6: builder finish** (freeze v1.32.0-phases artifacts + report) **and commit.** No gatekeeper/arena needed (equality-proven ≡ champion); arena-runner submits it only bundled WITH the next kept knob, or standalone during an idle slot.

---

### Task 3 (B2): hoard bands + wallet ladder

**Files:**
- Modify: `rust/src/botmain/planner.rs` (phase gating in `candidates()`)
- Modify: `rust/src/botmain.rs` (Scale training ladder consts; VERSION `1.33.0-hoard`)
- Modify: `rust/src/botmain/tactics.rs` (want_hand ladder under Meta::Scale)
- Test: `rust/tests/phase_hoard.rs`

**Interfaces:**
- Consumes: `Plan.phase` (Task 2). Produces: hoard behavior gated by `plan.phase == Phase::Hoard`; the ladder `SCALE_LADDER: [(i32,i32,i32,i32); 3] = [(1,1,1,0), (1,1,1,0), (2,2,0,2)]` with train turns ≥10/≥40/≥110 (tactics decides `want_hand`, `train_spec`, `cost` exactly as the existing want_feeder path does — reuse it, keyed on phase).

- [ ] **Step 1: Failing test** at `rust/tests/phase_hoard.rs` — construct the 8×5 State/Plan from `tests/planner_tasks.rs` (copy the helpers verbatim), set `phase: Phase::Hoard`, put one fellable banana at (3,2) with NO enemy nearby, one enemy troll at (6,2); assert `assign()` gives the chopper **no CHOP/no MOVE toward (3,2)** (hoard suppresses fells) — and with the enemy troll moved to (4,2) (map-distance 1 from the tree) assert the chopper DOES target (3,2) (denial-emergency band).

```rust
//! B2: Hoard suppresses felling except the denial emergency (enemy within map-dist 2).
use std::collections::HashSet;
use troll_farm::botmain::planner::assign;
use troll_farm::botmain::tactics::{Phase, Plan};
use troll_farm::botmain::{State, Tree, Troll};
// [copy base_state()/base_plan()/starter()/chopper()/banana() from tests/planner_tasks.rs,
//  with base_plan() setting phase: Phase::Hoard]

#[test]
fn hoard_suppresses_fells_without_threat() {
    let mut st = base_state();
    st.trees = vec![banana(3, 2, 2)];
    st.opp_trolls = vec![chopper(9, 6, 2)];
    let cmds = assign(&st, &base_plan(), &[starter(0, 1, 2), chopper(2, 4, 2)]);
    assert!(!cmds[&2].starts_with("CHOP") && !cmds[&2].contains("3 2"),
        "hoard must not fell an unthreatened tree: {}", &cmds[&2]);
}

#[test]
fn hoard_denial_emergency_fells_threatened_tree() {
    let mut st = base_state();
    st.trees = vec![banana(3, 2, 2)];
    st.opp_trolls = vec![chopper(9, 4, 2)]; // enemy 1 step from the tree
    let cmds = assign(&st, &base_plan(), &[starter(0, 1, 2), chopper(2, 4, 2)]);
    assert!(cmds[&2] == "CHOP 2" || cmds[&2].contains("3 2"),
        "threatened tree must be denial-felled: {}", &cmds[&2]);
}
```

- [ ] **Step 2: Run — fails** (no phase gating yet; first test asserts wrongly-allowed fell).
- [ ] **Step 3: Implement in `planner.rs`** — inside `candidates()`, chopper section: wrap the band-70/72 fell loop and the band-30/31 anti-starvation loop with:

```rust
        let hoard = plan.phase == super::tactics::Phase::Hoard;
        let threatened = |pc: Cell| -> bool {
            state.opp_trolls.iter().any(|e| {
                let ed = bfs_distances(&state.walkable, &[e.pos()]);
                ed.get(&pc).map_or(false, |&dd| dd <= 2)
            })
        };
```

and gate each fell candidate push with `if !hoard || threatened(pc) { ... }` (same for the starter chop-help section). During Hoard add one new starter band — harvest ANY ripe fruit (wallet building), value `62 * BAND - eta(...)` per tree with `p.fruits > 0` (dedup vs existing bands is fine — the matcher takes the max). In `tactics.rs`, under `Meta::Scale` extend the existing want_feeder machinery: `want_hand = n < 4 && ladder_slot_affordable` with `SCALE_LADDER` turn gates 10/40/110 (reuse `training_cost`/`mb_afford`/`train_spec` exactly as want_feeder does today; Tempo path untouched).
- [ ] **Step 4: All tests pass** (new + 20 suites). **Step 5: flag-off equality vs champion** (GE_META is still Tempo — must be EQUAL; same commands as Task 2 Step 5 with the new label). **Step 6: freeze v1.33.0-hoard + report + commit.**
- [ ] **Step 7 (gatekeeper, Scale build):** builder makes a SCALE probe: change `GE_META` to `Meta::Scale`, DEBUG=true, minify → gatekeeper runs boss 8 + field 4 with `{PHASE_INVARIANTS}=@TFPHASE shows Hoard→Factory at t140; hands ≥2 trained by t140 in ≥6/8; zero CHOP commands before t140 except denial (spot-check 2 raws); lemon banked ≥ ladder cost by t100`. This gate can FAIL without blocking Task 4 (bands iterate).

---

### Task 4 (B3): factory bands

**Files:**
- Modify: `rust/src/botmain/planner.rs`, `rust/src/botmain.rs` (VERSION `1.34.0-factory`)
- Test: `rust/tests/phase_factory.rs`

**Interfaces:**
- Consumes: Phase (Task 2), hoard gating (Task 3). Produces: Factory = Tempo bands PLUS `farm_cap` 12→20 and plant band active for ALL hands.

- [ ] **Step 1: Failing test** — Factory phase on a farm-with-room state: a banana-carrying starter must PLANT (not bank) and a chopper must fell farm bananas at size 2 (Tempo semantics resumed):

```rust
#[test]
fn factory_plants_and_fells() {
    let mut st = base_state(); // phase: Factory in base_plan(); farm_cap 20
    st.trees = vec![banana(1, 1, 2)];
    let mut s = starter(0, 1, 2); s.carry = [0, 0, 0, 1, 0, 0];
    let cmds = assign(&st, &base_plan(), &[s, chopper(2, 1, 1)]);
    assert!(cmds[&0].starts_with("PLANT") || cmds[&0].starts_with("MOVE"));
    assert_eq!(cmds[&2], "CHOP 2");
}
```

- [ ] **Step 2: fails → Step 3: implement** — in `tactics.rs` `plan()`: `let farm_cap = if phase == Phase::Factory { 20 } else if econ_b { 20 } else { GE_FARM_MAX };` (Hoard keeps 12; Tempo untouched). Factory needs NO band suppression (hoard's `!hoard ||` gates already reopen everything at t≥T_SWITCH). **Step 4: tests green. Step 5: flag-off equality (Tempo) EQUAL. Step 6: freeze v1.34.0-factory + commit.**
- [ ] **Step 7 (gatekeeper, Scale build):** invariants: `PLANT count t150+ ≥25 per game (count in raws); wood ≥60 in ≥4/8 boss games; t300 delta ≥ −8`.

---

### Task 5 (B4): Scale-meta arena trial

**Files:**
- Modify: `rust/src/botmain.rs` (`GE_META = Meta::Scale`, VERSION `1.35.0-scale`)
- Create: `cgauto/submissions/v1.35.0-scale.{rs,min.rs}`

- [ ] **Step 1 (builder):** flip `GE_META` to `Meta::Scale`, VERSION `1.35.0-scale`, local gates (equality gate here = self-determinism only — Scale ≠ champion by design), freeze, report.
- [ ] **Step 2 (gatekeeper):** full batch — boss 8, field 6 incl. mikdiet+plcc+one ≥19.6. PASS bar: wood ≥55 avg, no <25-wood collapse game, invariants from Tasks 3-4 hold.
- [ ] **Step 3 (arena-runner):** bracket → submit → verdict. KEEP only if ≥ champion band (≥18.9); on keep, champion + default switch to v1.35.0-scale. On revert: analyst decodes the losses (which phase leaked?) and the queue gets `T_SWITCH sweep {120, 100}` before any new ideas.

---

### Task 6 (A2, arena filler while B iterates): denial-weight probe

**Files:**
- Modify: `rust/src/botmain/planner.rs` (chopper fell-band value), `rust/src/botmain.rs` (VERSION `1.36.0-deny1`)

- [ ] **Step 1 (builder):** in the chopper band-70 travel-fell push, change the value to:

```rust
                let deny = (manhattan(pc, plan.opp) as i64) / 2; // prefer contested trees
                out.push(Cand { kind: Kind::MoveTo, target: Some(pc), value: 70 * BAND - (steps + chop_t) - DENY_W * deny });
```

with `const DENY_W: i64 = 1;` next to `STICKY`. (`DENY_W = 0` reproduces the old value exactly — keep the const so the knob is sweepable.) VERSION `1.36.0-deny1`; local gates; freeze; report.
- [ ] **Step 2-4:** gatekeeper (standard Tempo thresholds) → arena-runner → analyst; this task runs whenever the arena slot is idle between B iterations.

---

## Orchestration loop (main session)

- [ ] Dispatch Task 0 inline (it's two file writes). Then per task: builder agent (worktree for Tasks 2-5, plain for knobs) → review report → gatekeeper agent → review → arena-runner agent (serialize! never two in flight) → analyst agent → update the queue.
- [ ] Standing rules: Track A retires after two consecutive neutral/negative verdicts; every verdict lands in `docs/silver-experiment-log.md`; roadmap §0 and memory updated at champion changes; the feature exits when rank ≤99 is read twice, ≥15 min apart.
