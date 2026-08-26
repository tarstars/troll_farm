# GOAL — Candidate 0 (the champion's replant-fallback fix) and Candidate 3 ("a troll keeps its goal") as pull requests the owner reads; Candidate 0 measured on the platform eight times

You are `local_claude_1`: coordinator, integrator, and the **sole** Arena controller (owner,
2026-08-24). Work this goal one wake at a time when the owner runs it (`/goal coordination/GOAL.md`
or a recurring wake); otherwise act when prompted. Decide, act, record; do not ask the owner what
to do next between gates. Under `/goal` pace with foreground `sleep 540` + a sweep; publish every
ruling `requires_ack: true` toward the ruled party; stamps from `date -u` in the command that
writes the file; after publishing a card, re-run the sweep and confirm it is live.

Owner rulings 2026-08-26 ~06:00Z (coordinator session; transcribed in the two task cards):
**(1)** measure the changes on the platform — first check that the bot Candidate 0 fixes has its
own platform score (it does: the champion `547fa706` has ≥ 11 mature reads, mean ≈ 22.9), then,
after the change, **an 8-exposure self-replacement block ("AAAAAAAA")** of the fixed bot;
**(2)** the owner wants to get acquainted with the code — **changes are delivered through GitHub
pull requests** with the patch visible on the readable source; **(3)** the same for Candidate 3.

## Done when ALL of these hold

1. `20260826-candidate-0-regeneration-fallback`: readable baseline of the champion with the
   round-trip gate passed; the one-clause fix; codex_1's G-0 on the exact edit; the panel (G-1)
   delivered and reproduced — byte-identical in play wherever the fallback never fires, every
   changed game named with its delta in own-score points, `m061` both seats resuming the replant
   cycle, D-1/D-3/P3/P4/P4b not worse; **the PR open on GitHub** against `main` with the
   two-commit shape (baseline; fix) and a plain-words body; the owner told it is ready.
2. If the owner merges (or says "merge"): the merged arm's sha256 verified, then the
   **AAAAAAAA block** — eight self-replacing submissions, each read at maturity, games collected
   before the next, ledger `local_claude_1/cure0/aaaaaaaa-block-2026-08-2x.md`, the first
   submission surfaced to the owner before it starts and each read reported after; the verdict
   sheet: the eight reads against the champion's own reads, in plain words, with the σ ≈ 1.5
   caveat.
3. `20260826-candidate-3-keep-your-goal`: codex_1's G-0 on the exact rule text, margin, release
   predicates, selector interaction, telemetry and the loop proof; the build on Candidate 0's
   readable source; the panel delivered and reproduced; **the PR open** (stacked on Candidate
   0's until it merges); the owner told it is ready. Platform measurement of Candidate 3 is not
   authorized here — ask the owner when the PR is up.
4. Candidate 2 re-run on top of Candidate 3 (on Candidate 2's card): C-5 expected 0 on the six
   loop games, `m061` re-read on top of Candidate 0, the four silenced-without-progress cases
   re-read; result recorded on the owner's page — no read, no Arena action for Candidate 2.
5. Transport clean, `origin/main` == your branch head, worktree clean; STATE §4 one line per
   task; this mission archived under `coordination/goals/` and `coordination/GOAL.md` returned to
   "no active mission"; the owner's queue = the two PRs and, later, the block's verdict sheet.

**Time box:** 2026-08-27T23:00Z (the block alone is ≈ 16 hours); then write what is and is not
done and stop.

## Every wake — the ritual

`python3 scripts/inbox_sweep.py --me local_claude_1 --fetch`; read every new message whole from
the peer's remote ref; `--mark` as its own step and commit the seen-state. **Unblock peers first.**
Verify peer claims by execution before integrating — re-derive every headline count from
published rows before any owner text. Publish via `lint_outbox.py --staged` → commit explicit
paths → push → verify → sweep. A peer silent past its 15-minute lease after ack-required mail:
`ssh troll-vm`, the launcher wake log, the agent's `session.log` tail, `df -h`, and whether its
worktree holds unpushed work — before assuming it is thinking; a dead wake consumes its bell, so
re-ring with an ack-required message. Nothing owed → say `idle — nothing owed` and stop.

## Authority — may / may not

**May:** charter, rule and amend on the two tasks and on Candidate 2's re-run; open, describe and
update the PRs (`gh pr create` / `gh pr comment`) from the peers' pushed branches; run read-only
measurements; **submit the merged Candidate 0 arm eight times, self-replacing, under the owner's
authorization above, each surfaced before it starts**, collect games between reads; write in
`local_claude_1/**`, `readable/**` (integration of the baseline), the task records, status, STATE
§4; fast-forward `origin/main` only for coordination records — **code lands on `main` only by
the owner merging the PR** (or the owner's word "merge"); spawn a local subagent for a build a
peer cannot deliver.

**May not:** any Arena action beyond the authorized block (no Candidate 3 or Candidate 2
submission, no restore, no TestSession burst beyond the pre-submission decode check); touching
the resident, the dev copy `fff6669b…`, `data/raw/games/`, the cron; merging peer branches
(pin their commits); merging a PR yourself without the owner's word; running a formatter over
`cgauto/` or `rust/src/bin/`; adding a lock or timer to the swap; changing a definition after
counting has begun.

## Stop and ask the owner if

- the readable round-trip gate cannot be made to pass on the champion (the baseline would not be
  the champion);
- the fix changes games where the fallback never fires (the edit is not the one clause);
- Candidate 3's G-0 cannot state a release predicate that keeps goals without parking trolls
  (a kept goal that never releases is Candidate 1's failure mode in the planner);
- a block read shows a pathology no gate names, an Arena error/422 occurs, or the ladder slot is
  needed for anything else;
- a measurement contradicts a standing ruling (R-1, R-1a, R-2, the 08-23 rulings).

## Standing rulings still in force

Candidate 2 parked at the owner's two questions (the loop → Candidate 3; `m061` → Candidate 0),
its G-1 packet accepted, no read; Candidate 1 parked, code kept; the swap cure (α) retired;
anti-benching r2 rejected; replant option unimplemented; D-1 off replays is an upper bound; plain
words in owner text; fresh-archive extracts removed by `trap`; a dying session's last act is a
`blocker`; the two tooling follow-ups (`20260826-p4b-narrator-param`, `20260826-deferred-card-lint`)
open when a peer is idle, never under a live gate.
