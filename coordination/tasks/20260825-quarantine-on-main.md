# 20260825-quarantine-on-main: the message-quarantine list moves to `origin/main`, like the roster

- Status: **CLOSED — DONE 2026-08-25T19:02Z.** Peers confirmed the refresh (claude_1 `20260825T185200Z`,
  codex_1 `20260825T184917Z`: drift line gone, authority `refs/remotes/origin/main:coordination/quarantine.json`,
  134/134 each); **roster v2 published** (`main` = `82f7908e`: `schema_version` 2,
  `former_coordinators: []`, note rewritten for the succession rule); all five roster ids sweep at
  12 quarantined / 0 delivery / 0 quarantine / 0 collisions on the v2 roster; launcher clone at
  `82f7908e`. The quarantine now survives a role transfer by one roster edit (set `coordinator`,
  append the outgoing id). Earlier status follows.
- Status (18:42Z): **INTEGRATED 2026-08-25T18:42Z (`main` = `6a8d4db0`); closing on the peers' refresh
  confirmations and the roster v2 commit.** G-1 delivered by codex_1 (`agent/codex_1@dfaf94a2`,
  134/134, five roster ids 12/0/0/0); reproduced by me from a detached worktree at the pin and by
  claude_1 independently (same numbers; both authority readings are the same blob `0921f135c3dd`
  today). Integrated by taking the pin's bytes for the six files (diff vs `main` identical to the
  reviewed diff). Refresh order executed: `main` → launcher clone on the VM (was 197 commits
  behind; now `6a8d4db0`, digest `5734a753…`) → peers on their next wake → roster v2
  (`former_coordinators: []`) only after both confirm, because the old sweep rejects any roster
  version but 1. Improvement noted, not blocking: the "ignored agent-branch entry" test asserts
  counts and exit code, not the reason string. Earlier status follows.
- Status (18:2xZ): **G-0 ACCEPTED 17:57Z; blocker ruled 18:10Z (B′) + follow-up 18:2xZ (option 3);
  implementation in progress (codex_1).** Role-transfer invariant: an entry's `adjudicated_by` is
  valid iff it names the current coordinator or a member of the roster's new `former_coordinators`
  list (roster schema v2; a v1 roster reads as an empty list), fail-closed; the list is appended by
  the new coordinator in the same §9 roster edit as the transfer; rename tests split (with the
  append → 12 in force; without → 12 fail loudly). Named limitation (option 3): the sweep does not
  stop a former coordinator signing a *new* entry — the integrator refuses it at review before
  `main`; §10.2 says so, and the report line names an honoured former-coordinator signature.
  The roster edit is the integrator's at integration. Original status follows.
- Status at charter: **OPEN — CHARTERED 2026-08-25T16:05Z by owner ruling** ("change the rule so the list
  lives on main", coordinator session ~15:55Z — the coordinator's transcription). Blocks nothing;
  sequenced **after** codex_1's `P4b` build.
- Record owner: local_claude_1 · Work owner: **codex_1** · Reviewer: **local_claude_1** (the
  sweep and lint are the integrator's tooling) with **claude_1** as second reader (its sweep is
  affected) · Integrator: local_claude_1.
- Area: transport tooling — `scripts/inbox_sweep.py`, `tests/test_inbox_sweep.py`,
  `coordination/multi-agent-protocol.md` §10.2, `scripts/lint_outbox.py` if it reads the file.
- Why: today `coordination/quarantine.json` is validated from the **coordinator's canonical
  branch** (`load_quarantine(coordinator_ref)`, `inbox_sweep.py:847`), the coordinator being named
  by the roster on `origin/main`. Every role transfer and every careless merge therefore breaks
  the quarantine silently (recorded 2026-08-24: repaired by hand twice). The roster already lives
  only on `origin/main` as the shared root of trust (`ROSTER_REF`, `:108-110`); the list should
  live beside it.
- Branch: agent/codex_1 (work), agent/local_claude_1 (review + integration).
- Progress lease: 15 minutes without concrete evidence.
- Created UTC: 2026-08-25T16:05:00Z · Last updated UTC: 2026-08-25T16:05:00Z

## The change (plain words, then exact)

The list of permanently-invalid messages that every sweep suppresses is read from `main` — the
branch everyone integrates into — instead of from whichever branch the current coordinator owns.
Who may **edit** the list does not change: only the coordinator named in the roster, with every
entry pointing at an adjudication message, exactly as §10.2 says.

Exactly: `load_quarantine`, `load_legacy_baseline` and `verify_legacy_baseline`
(`scripts/inbox_sweep.py:847-940`) read their files from `ROSTER_REF` (`origin/main`) rather than
from `coordinator_ref`; the coordinator identity from the roster is kept for the
"adjudicated_by must be the coordinator" and "self-adjudication fails" checks; the report line
`quarantine authority: …` names `origin/main`. The integrated branch is fast-forwarded by the
coordinator, so a quarantine entry becomes effective when it reaches `main` — state that in
§10.2. `lint_outbox.py`: same source if it reads the file.

## Tests (`tests/test_inbox_sweep.py`) — rewrite the affected ones, add the new property

Affected by name: `test_roster_naming_a_different_coordinator_moves_the_authority` (the authority
no longer moves with the coordinator's branch — it stays on `main`; the coordinator identity
still gates who may adjudicate), `test_quarantine_on_a_non_coordinator_ref_is_ignored` (becomes:
a quarantine on any agent branch, coordinator's included, is ignored unless it is on `main`),
`test_worktree_quarantine_alone_suppresses_nothing`, `test_local_quarantine_drift_from_authority_is_loud`,
`test_authority_comes_from_the_roster_not_the_environment`, `test_missing_roster_disables_quarantine_loudly`
(unchanged in spirit: no roster → quarantine disabled loudly), plus every other quarantine test
must stay green. **New:** a role transfer (roster coordinator changes on `main`) leaves the
quarantine in force with zero edits; a merge of an agent branch into `main` that carries a stale
`quarantine.json` is caught loudly by the existing entry validation (the target blobs must still
match).

## Gates

- **G-0 (local_claude_1, ack-required):** the exact change list and the test plan — one message.
- **G-1 (codex_1 builds; local_claude_1 reproduces the test run; claude_1 second reader):**
  `python3 -m pytest tests/test_inbox_sweep.py tests/test_lint_outbox.py -q` green; a dry run of
  the sweep for each agent id from the patched script against the live remote refs reports the
  same 12 quarantined paths and 0 errors as today; the protocol §10.2 text updated in the same
  change. Integrated by the coordinator with the digest gate (`tool_drift`) in mind: every agent's
  copy of the sweep must be updated from `main` after integration (the launcher's clone included).

## Deliverables

A patch series on `agent/codex_1` touching only the four files above; `codex_1/quarantine-main/
report-2026-08-2x.md` with the test output and the dry-run counts.

## Do not touch

Any message under `coordination/messages/**`; `coordination/quarantine.json`'s entries; the roster;
any bot source. No Arena action.
