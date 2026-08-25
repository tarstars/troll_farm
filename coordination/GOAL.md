# GOAL — measure the dance geometry on the instrumented real games, so the owner can rule on Candidate 2

You are `local_claude_1`: coordinator, integrator, and the **sole** Arena controller (owner,
2026-08-24). Work this goal one wake at a time when the owner runs it (`/goal coordination/GOAL.md`
or a recurring wake); otherwise act when prompted. Decide, act, record; do not ask the owner what
to do next between gates. Under `/goal` pace with foreground `sleep 540` + a sweep; publish every
ruling `requires_ack: true` toward the ruled party (a bare receipt wakes nobody).

Owner authorization 2026-08-25 ~13:30Z (coordinator session, after the dance discussion: *"create
goal file for measurements you just mentioned"* — the coordinator's transcription). **Measurements
only**: no cure, no candidate, no bot change, no Arena action of any kind. Goal files never
authorize Arena writes (protocol §4); nothing here needs one — every input is already in the repo.

## Why (plain words)

The instrumented real games say the dance is one mechanism: the dancing troll wants a tree or the
bank a few cells away, its path runs through the cell where **our other troll stands still and
works**, and the mover — which plans blind to units and repairs one step at a time — steps
*backwards* when every free neighbour is farther from the goal. The coordinator's re-read of the
published fact rows (`local_claude_1/dance-geometry/re-read-2026-08-25.md`, script
`reread_shapes.py`) found the teammate standing next to the dance at its start in **55 of 80**
episodes of the older read and **24 of 25** of the v4 read (the accepted class labels said 34 and
15, because their blocker test demanded one cell for the whole window), and the short "nobody
adjacent" dances at **25 of 80 → 1 of 25** on the hold arm (Fisher p ≈ 0.005, confounded by day and
opponents). Two things are still unmeasured and both decide the open Candidate 2 ruling — *swap
the standing teammate out of the way once, or route around it*:

- **M-1 — is there a road around the standing teammate, and how much longer is it?** If a road
  usually exists at small extra cost, routing around has room; if the corridor is one cell wide,
  only a swap (or the teammate moving) can end the dance.
- **M-2 — what stood on the dancer's next cell on each backward step of the older read's short
  "nobody adjacent" dances?** The older read has no resolver letters. Counting *standing teammate /
  teammate passing through / nothing of ours* turns the "transient block" hypothesis into a number
  and tests the re-read on the read that lacks the letters.

## Inputs — pinned, all in the repo

- Fact rows: `agent/claude_1@4c92432f:claude_1/dance1/results/dance-facts-instrument-2026-08-24.json`
  (80 episodes) and `agent/claude_1@22d6b2bb:claude_1/cure1/results/g2-grade.json` (25 episodes,
  `per_game[].episodes[]`, `v4_branch_sequence` = the resolver letters P/L/H/R/W/N).
- Replays (sanitised packages, our seat carries the telemetry): batch 1
  `local_claude_1/narrate/games/` (149 files, agent 6652424, v2); batch 2
  `local_claude_1/narrate/read2/games-agent6652602-submission41182352.jsonl.gz` (`84f46acb…18897`);
  batch 3 `local_claude_1/narrate/v3/games-agent6652642-submission41182608.jsonl.gz`
  (`01169944…c3ceb`, v3); v4 `local_claude_1/cure1/g2-games/games-agent6659743-submission41192036.jsonl.gz`
  (`050d1ceb…c6a38`). Manifests beside each package.
- Machinery to **import, never copy**: `claude_1/adapter1/replay_to_trace.py` (map + per-turn
  units), `claude_1/cure1/regressive_baseline.py` (`measure_game`: walkable map, `td.bfs_distances`
  seeded at the target exactly as the arm does, the stated target per turn, v3/v4 joins),
  `claude_1/narrate4/narrate4_join.py`, `claude_1/dance1/dance_facts.py` (`f3_peers`,
  `measure_blocker`). The arm's own step rule for reference: `claude_1/cure1/cure1-hold-v4.rs`
  ~826–922 (`next_cell`, `reserved`, the detour, letters).

## The charter's spine (the builder proposes the exact definitions at G-0; codex_1 accepts them before any count)

**Population:** every D-1 episode of both reads — 80 + 25 = 105 — and, inside each, every window
turn on which the dancer has a stated cell target and a successor cell (the same eligibility as
`R_pos`).

**M-1, per eligible turn:** `d0` = BFS distance from the dancer's cell to its stated target on the
bare walkable map (the arm's metric, Manhattan fallback off-map as the arm does); `d1` = the same
with the teammate's *current* cell removed from the walkable set; "teammate on every shortest road"
⇔ `d1 > d0`; road-around cost = `d1 − d0`, **∞** when unreachable; also whether a free orthogonal
neighbour no farther than the dancer's cell exists (the arm's `L` branch — if it exists the arm
would not dance). Per episode: the share of eligible turns with `d1 > d0`; the median cost over
those turns; a cost class `0 / 1–2 / 3–5 / >5 / ∞`; the dance length beside it. Headline tables:
cost class × shape (`one-cell` / `adjacent` / `nobody`, from `reread_shapes.py`), and cost class ×
dance length, both reads separately. **Controls:** (K-1, positive) on the v4 read, a turn lettered
`R` has the teammate's cell on the arm's forward step and `d1 > d0` — expected agreement ≥ 95 %,
every disagreement explained; (K-2, negative) a turn lettered `P` has a free forward cell; (K-3,
poison) walling a random walkable cell not adjacent to the dancer gives cost 0 on nearly every
turn; (K-4) determinism — a second run is byte-identical; (K-5) exhaustiveness — eligible turns
counted per episode reconcile with the window length.

**M-2, per backward step of the older read** (a dancer step with `d0` increasing toward the stated
target, on all 80 episodes, headline on the 25 `nobody`): what is on the dancer's forward cell
(the arm's `next_cell` from the pre-step cell): (a) an own unit standing there this turn *and*
last turn; (b) an own unit that arrived this turn or last turn, or is moving (transient); (c)
nothing of ours — residual (Manhattan fallback off-map, or a planner flip). Counts per episode and
per shape. **Control (K-6):** the same predicate on the v4 read must give (a) on `R` turns and (b)
on `H` turns, disagreements explained.

**Not in scope:** any bug ruling, any cure, any change to the accepted r3 classification (the
re-read is a *second* reading beside it, not a replacement), opponents' reasons, prevalence beyond
these two reads.

## Done when ALL of these hold

1. The re-read note and script are on trunk (`local_claude_1/dance-geometry/`) and named in the
   charter as input, with their caveats (straight-line test on the older read; upper bound; day and
   opponent confound).
2. Task card `coordination/tasks/20260825-dance-geometry-measurements.md` chartered: claude_1
   builds, codex_1 reviews **definitions first (G-0, ack-required)** and then reproduces the
   execution from a fresh archive (G-1); record owner local_claude_1. If the VM launcher is down or
   claude_1 does not claim within 30 minutes, a local Opus subagent builds under your supervision
   (owner directive 2026-08-21: delegate the reading and the instruments); codex_1 still reviews.
3. G-0 `DEFINITIONS_ACCEPTED` by codex_1; if codex_1 has not answered within 60 minutes of an
   ack-required request, proceed with the published definitions marked *unreviewed* and have
   codex_1 review definitions and execution together at G-1 — say so in the record.
4. G-1: the results JSON published whole (every episode, every eligible turn, every control with
   its number), determinism shown, codex_1's reproduction byte-identical or the difference
   explained and the numbers re-issued.
5. Owner brief, plain words, at `local_claude_1/dance-geometry/owner-brief-2026-08-2x.md` (one
   page + the two headline tables): for the teammate dances, how often a road around exists and
   what it costs, against how long the dances lasted; the M-2 count; what each answer means for
   *swap* versus *route around* — stated as evidence, **the ruling stays the owner's**. If M-2
   proves expensive, deliver M-1 alone and mark M-2 not done.
6. Transport clean, `origin/main` == your branch head, worktree clean; STATE §4 carries one line;
   this mission archived as `coordination/goals/20260825-dance-geometry-measurements.md` and
   `coordination/GOAL.md` returned to "no active mission"; the owner's queue = this brief beside
   the still-open Candidate 1 verdict sheet.

**Time box:** 2026-08-26T14:00Z; then write what is and is not done and stop.

## Every wake — the ritual

`python3 scripts/inbox_sweep.py --me local_claude_1 --fetch` (check filenames against `MSG_RE`
when a peer says it answered and the sweep shows nothing); read every new message whole from the
peer's remote ref; `--mark` as its own step and commit the seen-state. **Unblock peers first**
(rulings owed, questions, acks). Verify peer claims by execution before integrating. Publish via
`lint_outbox.py --staged` → commit explicit paths → push → verify → sweep. Stamps are `date -u`,
never ahead; `git rev-parse` every `artifact_commit`. Nothing owed → say `idle — nothing owed`
and stop.

## Authority — may / may not

**May:** charter and rule on this measurement task; run read-only computations on the packages
in the repo (and on `project_host` if a replay must be re-exported — sanitiser
`cgauto/export_agent_replays.py`, never raw replays into the repo); write in `local_claude_1/**`,
the task record, status, STATE §4; spawn a local Opus subagent for the build; fast-forward
`origin/main` when nothing foreign is on it.

**May not:** any Arena action (submit, TestSession, restore — none is needed and none is
authorized); touching the resident, the dev copy `fff6669b…`, `data/raw/games/`, the cron;
merging peer branches (quarantine hazard — pin their commits, read their refs); chartering
Candidate 2 or 3, the structural step, or the P4 gate repair; changing a definition after counting
has begun (a change = a new revision, re-accepted, re-counted); ruling swap-versus-route-around
yourself — the owner rules on the brief.

## Stop and ask the owner if

- the adapter refuses replays of a whole batch (the map or positions cannot be recovered) — the
  population would change;
- control K-1 fails (the letters and the geometry disagree beyond 5 % and the disagreement is not
  a fallback artefact) — the measurement would not be the arm's geometry;
- a measurement contradicts a standing ruling (R-1, R-2, the 08-23 rulings);
- anyone proposes to build a cure "while we are here" — that is Candidate 2/3;
- an Arena error, a ladder change, or anything that needs the ladder slot appears.

## Standing rulings still in force

Candidate 1 PARKED pending the owner's word on the verdict sheet (`local_claude_1/cure1/owner-verdict-sheet-2026-08-25.md`);
Candidate 2 ruling OPEN; the ladder holds the Candidate 1 instrument (agent `6659743`, no restore
obligation); archive-wide defect counting closed; publication gateway closed; swap cure retired;
anti-benching r2 rejected; replant option unimplemented; D-1 off replays is an upper bound on
every count; plain words in owner text, every code explained at first use.
