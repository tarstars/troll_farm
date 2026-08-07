# Coordinator handover — `local_codex_1` → `local_claude_1`, 2026-08-06

Owner directive: *“write down all important things from this conversation in context-flush safe
way and give coordinator role to local_claude_1.”* The user is the authority for role changes
under `coordination/multi-agent-protocol.md` §9.

This is the context-flush recovery document. It is a timestamped operational snapshot, not a
replacement for experiment records. When facts conflict, use this order:

1. the newest pushed correction or exact-task message;
2. `docs/STATE.md` for live identity and authority;
3. the governing task/frozen protocol and its immutable result;
4. `docs/CONSTRAINTS.md` for closed scientific branches;
5. the live ledger volume named in STATE §5;
6. this handover for conversation decisions and navigation.

## 0. Role transfer and first recovery sequence

Effective with the pushed roster commit, **`local_claude_1` is coordinator/integrator and the
single Arena controller**. Arena control follows the coordinator by protocol default; the owner
did not separate it. `local_codex_1` relinquishes both roles and must not mutate the Arena after
publication. The standing Arena authorization remains unchanged; role transfer does not relax its
qualification gates.

`local_claude_1` is a new protocol identity. At handover time it has no canonical branch, worktree,
status, message namespace, or seen-state. Do not reuse another Claude identity or worktree.

First actions, in order:

```bash
cd /home/tarstars/prj/troll_farm
git fetch origin
git worktree add /home/tarstars/prj/troll_farm-local_claude_1 \
  -b agent/local_claude_1 origin/agent/local_codex_1
cd /home/tarstars/prj/troll_farm-local_claude_1
mkdir -p coordination/messages/local_claude_1 local_claude_1
cp coordination/templates/status.md coordination/status/local_claude_1.md
python3 scripts/inbox_sweep.py --me local_claude_1 --fetch \
  --task 20260806-coordinator-transfer-local-claude
sha256sum rust/src/bin/yamo_orchard_live.rs
```

Fill and publish the status snapshot, then acknowledge the exact transfer-handoff message from
`local_claude_1`'s own message directory. Push and verify the remote SHA before claiming receipt.
After acceptance, integrate through the protocol's session branch deliberately; do not force or
reset refs.

Important inbox bootstrap trap: because this identity is new and has no seen-state, an unfiltered
sweep currently reports 89 legacy/new paths and 44 apparent unacknowledged messages. They are not
44 new assignments. Start with the exact transfer-task filter. Then audit the historical backlog,
acknowledge only genuinely actionable v2 paths by exact `ack_for`, publish a legacy-backlog audit
for the rest, and only afterward run `--mark`. Never blanket-ack by timestamp. In particular, the
2026-08-04 orchard-code-cost assignment to `local_claude_1` was explicitly canceled by
`coordination/messages/local_codex_1/20260804T064002Z-20260804-orchard-code-cost-ablation-stop.md`;
the new coordinator role does not revive that task.

## 1. Repository and protocol state

- Latest outgoing coordinator ref at preparation start:
  `origin/agent/local_codex_1` = `240c27f25d89f4efd6f7d658c934fee04bf7a6d5`; the later typed
  handoff message names the exact artifact commit containing this document.
- `origin/main` and `origin/session-2026-07-01` were both at
  `b6f9a7825a17afbbd91949d31d5957b330f6adf0`, well behind the outgoing agent ref. The protocol
  says the integrator updates the session branch and that there is no automatic main workflow.
  Do not infer that `main` is canonical merely because old chat requested merges.
- The outgoing worktree contains unrelated user/collector work: before handover edits it had 16
  modified tracked paths and 206 untracked paths, mostly live data/manual refreshes and a large
  simplification scratch set. Do not stage, clean, delete, reset, or “tidy” them. The separate
  incoming worktree avoids this ownership hazard.
- The user explicitly warned that `~/prj/{arcadia,arc00,arc01}` are huge mounted repositories.
  Never use broad `find`, `rg`, `du`, or recursive Git operations from `~/prj` or `$HOME`. Search
  only exact Troll Farm subpaths; use `rg`/`rg --files` with narrow roots.
- Git transport is authoritative. “Unpushed means unsent.” New messages use schema v2,
  remote-only refs, exact-path `ack_for`, immutable corrections with `supersedes`, and canonical
  handoff artifact validation. Fetch failure/schema failure is exit 2, not an empty inbox.
- One worktree/branch per writing agent; never share an index. Stage exact paths only; `git add -A`
  and `git add -u` are forbidden while other work exists.

Roster after transfer:

- `local_claude_1`: coordinator/integrator and sole Arena controller;
- `local_codex_1`: contributor/outgoing handoff author, no Arena authority;
- `claude_1`: active contributor, currently revising Banana R2 design; no platform credentials or
  `medium_data` mount, but Git LFS works;
- `chatgpt_1`: contributor/reviewer; its checked-in status is stale, so trust task/message history,
  not the 2026-07-29 status snapshot.

## 2. Non-negotiable safety boundaries

- `rust/src/bin/yamo_orchard_live.rs` is library-visible and byte-sacred at full SHA-256
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.
- Never run a formatter across `rust/src/bin/` or `cgauto/`; experiment locks record hashes.
- Never open sealed map `9,844,200–9,844,215`, the official holdout, the 11 sealed D164 games, or
  reserved/confirmation ranges unless their frozen protocol explicitly authorizes it.
- Do not write, move, symlink, lock, or broadly scan `data/raw/games/`; the 05:17 collector owns it.
- External play bursts are at most 12 games; stop on HTTP 422 or degenerate results.
- The authoritative bulk filesystem is the volume labeled `medium_data`, historically mounted at
  `/media/tarstars/medium_data`, project root
  `/media/tarstars/medium_data/database/troll_farm`. Before every bulk write run
  `python3 cgauto/check_external_storage.py --required-free-gib <GiB>` and verify the label and
  symlink targets. Never create fallback real directories for missing bulk symlinks.
- Canonical YT root is `//home/delivery_ml/research/tarstars/troll_farm`; assess YT before a batch
  expected to exceed about one hour.
- No secrets, browser profiles, personal handles, tokens, or session state enter Git/LFS. Shared
  replay exports replace names with positional placeholders while preserving game/submission IDs.

## 3. Goal, current live bot, and Arena authority

Goal: mature score **≥25.40**, with **24.70** as the interim checkpoint. The old rank≤3 goal is
superseded. Passive maturity is not a plan: N1 estimates remaining uplift −0.1612 with 95% CI
[-0.7525,+0.4567]. Improvement must come from policy/architecture.

Current live source:

- round-36 behavior-exact simplified E7a;
- agent/submission `6594200` / `41090606`;
- source `cgauto/submissions/candidate-agent6553250-e7a-r36-simplified.min.rs`;
- 55,799 bytes, SHA-256
  `2caac7c6e71e8dcc613a2275fe8129cdf9aec2c1230e50f7dfdec79908528381`;
- settled 160/160, score 22.81, rank 32/137, 93W/2T/65L, identity/runtime clean;
- exact equality to E7a on ten fixtures, 7,234 public command lines, and the frozen 516-task
  development panel. It is smaller, not behaviorally stronger.

The strongest repeated algorithmic evidence remains exact E7a: historical complete rows 25.26
and 23.56, median 24.41. Use the submission registry rather than a single maximum:

```bash
python3 cgauto/submission_history.py validate
python3 cgauto/submission_history.py query
python3 cgauto/submission_history.py preflight <candidate-source>
```

The registry categories strategy/architecture, deployment purpose, evidence maturity,
disposition, comparison type, and authority. Never select “best” from one recent maximum.

Standing Arena authorization permits the controller to submit only a candidate that has a
`QUALIFIED` frozen-protocol verdict, expected gain above the ±0.5–1 noise band, and a full
promotion-runbook cycle. Notify the owner before and after. A non-qualified live experiment,
abandoning a mature score without a replacement, or multiple cycles in flight must be surfaced
before acting. Never automatically retry an ambiguous submission. There is currently **no Arena
mutation cycle running and no qualified new candidate**.

## 4. Orchard/no-orchard evidence and readable bot artifacts

The owner resolved a seeming contradiction explicitly: early planting can establish a
self-reproducing orchard; late in the game, fruit/trees should be converted into wood. Do not turn
this into “always farm” or “always chop.”

The eight-leg owner-directed live A/B completed (the old task header incorrectly said running and
is corrected in this handover commit). Four no-orchard and four orchard submissions each settled
at 160 games. Orchard-minus-no-orchard paired score deltas were +1.60, +2.03, −0.36, −0.93; mean
+0.585, median +0.620. Opponent queues were not game-paired, so this is noisy repeated-live
evidence, not a clean causal estimate. Exact table and eight LFS replay packages:
`data/analysis/live-agent-6553250/orchard-ab-night-20260803/result.md`. The controller service is
inactive and absent; do not restart it.

A separate global no-orchard ablation scored 23.27/rank 34 versus an exact E7a pre-trial row at
25.3/rank 12, so global orchard deletion is closed. The orchard implementation's readable code
cost is nevertheless measured: 1,850 physical/1,845 code lines with orchard versus 1,475
physical/1,470 code lines physically stripped — 375 physical lines removed, 369 implementation
lines beyond the six-line activation edit. Task:
`coordination/tasks/20260804-readable-orchard-loc-cost.md`.

The 1,470-code-line readable no-orchard source is:
`local_codex_1/readable-orchard-code-cost/e7a-without-orchard-readable.rs`, exact source SHA
`98628e98...`. Beginner manual:
`docs/manuals/readable-no-orchard-rust-manual-2026-08-04.{md,pdf}` (43 pages). These paths have
uncommitted user refreshes in the outgoing worktree; use the committed branch version or inspect
the diff before accepting later bytes.

## 5. Banana restoration R2 — highest-priority active design thread

Canonical task: `coordination/tasks/20260802-banana-restoration-r2.md`. Stable parent is
`cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`, 62,725 bytes,
SHA `a8eb3b2b...`. This is a design/implementation-validity programme; no banana candidate has
earned value or Arena testing.

Owner intent:

- early planted bananas form a bounded self-reproducing orchard;
- late fruit/tree value is converted to wood;
- harvest/bank fruit when the resident controls it;
- do not create fruit an opponent can harvest first;
- preserve second-worker funding before banana/denial work;
- a wood carrier committed to the tent continues until DROP/cargo loss;
- units do not chase one another's occupied tree/cell;
- commitments need hysteresis and no A→B→A loops.

Lineage and disposition:

- `f29efd0e`, `280ed777`, `2f58edef`, `9f5ef833`: implementation-invalid for distinct
  lifecycle/oracle/reachability/liveness defects;
- round 4 `9f5ef833` produced a 225-turn full-wood carrier oscillation on map 9,854,000;
- round 5 `47c98f53` was withdrawn by Claude before host work after 141/240 fuzz blocks across
  seven families, including 37 recurrences through a second stationary-resident/articulation
  mechanism;
- round 6 `eac2eb36` reduces blocking games to 47/240 but is explicitly **not a handoff**.

Claude proposed an 11-state/six-channel FSM. Independent review is
`data/analysis/live-agent-6553250/banana-restoration-r2-fsm-design-review-2026-08-06.md`:
`REVISION_REQUIRED`. Required corrections:

1. atomic turn timing and deterministic priority for simultaneous events;
2. one exact growth-aware harvester+chopper asset-survival oracle for founding and response;
3. parent-difference attribution only on the aligned prefix, channel telemetry afterward;
4. an enforced carrier-yield/progress rule instead of unconditional resident priority plus an
   assertion;
5. bounded post-release vetoes, explicit exits for impossible commitments, and a frozen exact
   enumeration manifest proving event/edge/compound coverage.

Claude acknowledged all five at
`coordination/messages/claude_1/20260806T090000Z-20260802-banana-restoration-r2-ack.md` and is
revising the design before any implementation. The next valid inbound artifact is a design-only
review request. Do not run host, 516, replay, value, or Arena gates before design acceptance and a
later fuzz-clear implementation handoff.

Deferred non-blocking request: regenerate the 32,885-byte raw map-9,854,000 diagnostic trace
(old SHA prefix `c7d6e033`) from the documented round-4 host command before optional shared-LFS
publication; the scratch original is gone. It does not unblock design.

## 6. Durable owner observations about tactics

Treat these as hypotheses/requirements with exact task records, not permission for another broad
graft:

- **Dridriun (`896352129`)**: the opponent repeatedly farmed its door apple; our ripe own apples
  were converted without harvest despite local control. Corrected verdict is
  `NARROWED_TO_DISTINCT_FRUIT_CONTROL_PRECHECK`, not a bot change. Task:
  `20260731-dridriun-fruit-control-postmortem`.
- **zasmu (`896352750`)**: lemon denial was not sustained oscillation, but seven mature lemons
  held 84 health; we spent 28 chop commands removing five while zasmu harvested 25, replanted,
  and paid later TRAIN bills. Verdict `NARROWED_TO_FEASIBILITY_PRECHECK`: price liquid stock,
  regeneration, clear time, wood value, and bills before denying.
- Initial resource denial owner rule: if the route from a denial chop to our tent exceeds three
  map cells, the denial troll should not carry that wood home. This was an owner-directed
  historical branch; verify the current source before assuming it remains active.
- **DoubtinGiyov** owner rule: count enemy-tent neighboring trees; coordination starts with one,
  more than two activates full denial, and diagonal neighbors were later explicitly included.
  One worker preserves ordinary harvest/wood return; another denies planted trees without return.
  Second-worker funding/resource collection must outrank denial. The broad coordination layer was
  mechanically coherent but disastrously weak live; do not resubmit it.
- **Adler3D**: once a full wood carrier chooses banking, it must persist to DROP/cargo loss.
- **Elost**: a capable worker already standing on a tree owns that tree for the current decision;
  do not send a second worker to the occupied cell.

The key lesson is coordination and opportunity cost, not another unconditional denial overlay.
Relevant task records are the exact `20260731-*` postmortem/policy files under
`coordination/tasks/`.

## 7. Strategic work and what is actually open

- Most two-worker resident micro-optimizations, broad overlays, fixed grammars, replay cloning,
  value learners, late search, denial scalar changes, and Architecture-2 Phase 1 are closed in
  `docs/CONSTRAINTS.md`. Do not reopen by renaming a threshold.
- The all-agent top-player analysis ranked H3a pressure conditioning as the only surviving route,
  but it is not runnable end to end. Reconciled report:
  `docs/reports/2026-08-02-top-player-all-agent-analysis.pdf`.
- H3a task `20260802-h3a-conditioned-value-unblock` is recorded active but has no current visible
  lease. The 17-game/5,100-decision public trajectory package is accepted only for retrospective
  Phase A2. Literal gate-4 analyzer/tests remain pending. Phase B/C is blocked by 213 numeric fruit
  alias crashes, continued-RNG divergence, and empty `MSG ;` incompatibility. Contact `claude_1`
  and serialize this against Banana R2 before resuming; do not assume both are active.
- Initial-state sector work is measurement-only. The exploratory E7a rule was exactly materialized
  but selected from consumed labels and not prospectively value-qualified. The owner once
  published it to escape a broken banana bot; that is history, not validation. Canonical task:
  `20260802-initial-state-sector-policy-audit`.
- `20260802-top15-public-battle-audit` still says `in_progress` but has no current lease or
  published terminal handoff. Reconcile/reassign explicitly before continuing.
- Dridriun, zasmu, and corrected N5 have narrow peer reviews pending; they are review debt, not
  implementation authority.
- There is **no neural-network agent ready for Arena deployment**.
- AlphaZero/AlphaGo-style search-teacher distillation is preserved as H10b-r1, an owner-requested
  programme concept only. Training-time search would label states visited by a compact student;
  deployment would be a search-free int8 network. Planning prior: 50–70% chance of local teacher
  improvement, 25–35% chance a compact student clears closed-loop local gates, 10–20% chance the
  first programme is Arena-worthy. No charter, exporter, map range, fit, model, compute job,
  candidate, or Arena action is authorized. Freeze the feasibility charter first. Task:
  `coordination/tasks/20260801-h10b-search-teacher-distillation-record.md`.

Suggested priority after onboarding: finish the Banana FSM design review loop; then choose one of
H3a Phase-A closure or H10b feasibility charter based on owner priority. Do not spend Arena cycles
on behavior-exact simplification: it reduces source size but cannot improve score.

## 8. Data, replay access, Git LFS, and environment matrix

- Corpus checkpoint in STATE: 10,470 games / 513 agents / zero parse failures. The 05:17 cron
  continues independently.
- All 160 full replays of current round-36 agent/submission `6594200`/`41090606` are sanitized and
  published under `data/shared-lfs/r36-agent-6594200/`: 86,940 frames, 5,774,722 compressed bytes,
  SHA prefix `59f6283b`. Task `20260804-collect-r36-games` contains the selective-pull command.
- Exact E7a restore's 162 games are under `data/shared-lfs/e7a-restore-agent-6592131/`.
- The D172 Git LFS pilot passed: project host Git LFS 3.0.2 and Claude cloud 3.4.1 can upload and
  clean-clone selective-pull; ChatGPT's current shell cannot. Four D172 shards, 82,824,259 bytes,
  79,997 rows, were published without deleting the authoritative USB source. Migration plan:
  `docs/git-lfs-shared-artifact-migration-plan-2026-08-02.md`; capability matrix:
  `coordination/ENVIRONMENTS.md`. Never run `git lfs migrate`, force-push, or broad extension
  tracking.
- Local host historically has Arena credentials and `medium_data`; cloud agents do not. Do not
  place credentials in the handoff. `local_claude_1` must verify actual local access rather than
  infer it from the name.
- Open-game trajectory exports exist specifically so cloud agents can analyze without the host
  replay cache. They are causal/public reconstruction packages, not valid counterfactual Phase-C
  referee streams.

Useful explanatory artifacts:

- sector candidate algorithm: `docs/reports/2026-08-02-e7a-sector-agent-description.pdf`;
- all-agent/top-player synthesis: `docs/reports/2026-08-02-top-player-all-agent-analysis.pdf`;
- simplification work summary:
  `data/analysis/live-agent-6553250/e7a-half-size-last-eight-hours-report-2026-08-03.pdf`;
- beginner Rust/bot manual: `docs/manuals/readable-no-orchard-rust-manual-2026-08-04.pdf`;
- long experiment atlas: `docs/D-series-atlas.pdf`.

## 9. Communication failure that was permanently fixed

The earlier coordination failure was systemic, not merely a missed chat notification: old inbox
logic could count local/unpushed artifacts, rely on timestamp-like matching, hide fetch failures,
and accept incomplete handoffs. Phase 3 now requires:

- only `refs/remotes/origin/**` are authoritative;
- exact immutable repository paths in `ack_for`/`supersedes`;
- handoff artifact commit reachability and path validation on the sender's canonical branch;
- exact-path JSON seen state, separate from acknowledgement;
- loud exit 2 on fetch/schema/collision/delivery error;
- artifact commit first, handoff-message commit second;
- sender verifies remote SHA before saying “sent.”

Use `python3 scripts/inbox_sweep.py --me <id> --fetch`; exit 0 means healthy/clear, 1 means healthy
with unacknowledged messages, 2 means transport invalid. Chat/clipboard screenshots are alerts,
not the bus.

## 10. Immediate coordinator checklist

1. Create and push the new worktree/branch, status, message namespace, filtered ACK, and audited
   seen-state.
2. Verify `fff6669b...`, external volume by label, no running Arena controller/service, and exact
   live source identity before any platform action.
3. Notify/collect ACKs from `claude_1` and `chatgpt_1`; ask Claude for the revised design-only
   Banana FSM artifact, not code.
4. Reconcile the stale active records (`top15` and H3a lease) and serialize actual work. Do not
   infer ownership from old status snapshots.
5. Keep Arena unchanged. There is no qualified candidate and the current round-36 source is clean.
6. When proposing experiments, read STATE, CONSTRAINTS, then only the tail of the live ledger;
   use `docs/archive/INDEX.md` for archaeology.

## 11. Transfer completion condition

The role decision is effective in the pushed roster. Operational handover completes when
`local_claude_1` publishes and remotely verifies:

- its branch/worktree and status;
- a schema-v2 ACK for the exact transfer handoff;
- an inbox backlog audit/seen-state migration;
- confirmation that it is the only Arena controller and that no mutation is in flight.

Until that ACK is visible, the project has an assigned incoming controller but no acknowledged
operator. `local_codex_1` remains non-controller during that gap; safety is achieved by leaving the
Arena unchanged, not by dual control.
