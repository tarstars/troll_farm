# 20260803-owner-no-orchard-ablation-arena: live no-orchard ablation

- Status: 74-game health clean at score 22.49; terminal convergence pending
- Priority: direct owner assignment
- Record owner / work owner / Arena controller: local_codex_1
- Artifact author: claude_1
- Candidate:
  `claude_1/no-orchard-arena/candidate-e7a-r28-no-orchard.rs`
- Candidate bytes: 56,200
- Candidate SHA-256:
  `d1f32c358d0f7b6a49b988c1b4ad6958a2d8ed84a9e3492632087732aae7e02a`
- Created UTC: 2026-08-03T14:59:16Z
- Last updated UTC: 2026-08-03T15:21:07Z

## Objective and authority

Measure the live ladder value of the secure-orchard wrapper by submitting a deliberate ablation
of the simplified round-28 source. The owner explicitly directed this unqualified Arena experiment
in the Claude session; the pushed request is
`coordination/messages/claude_1/20260803T152000Z-20260803-owner-no-orchard-ablation-arena-submission-request.md`.
This satisfies the `docs/STATE.md` §3 requirement to surface a non-gate-qualified live experiment.
Only `local_codex_1` may mutate the Arena.

## Exact change and evidence boundary

The unique Dormant-phase orchard-activation branch is replaced by an unconditional return.
`SecureOrchardBot` therefore remains Dormant and becomes a pure `YamoBot` passthrough. This is
deliberately behavior-changing and has no development or untouched value qualification.

Independent controller verification:

- the exact builder reproduces the candidate byte-for-byte;
- optimized Rust compile and empty-input behavior pass;
- all ten frozen semantic fixtures pass;
- frozen replay packet: 24/25 games exact; game `897833045` first differs at turn 79, one turn
  after orchard activation, with clean exit and stderr;
- live source recovered before the cycle is exact E7a SHA-256 `97bfe71e...`;
- submission-history preflight confirms the candidate hash has never been deployed.

## Pre-trial baseline

At 2026-08-03T14:57:23Z, resident agent `6590141` / submission `41081503` is identity-clean with
160 finished games, 82W/3T/75L, 35 catastrophes, negative-margin mass 10,045, and no runtime
signals. Arena-room read: score 25.3, rank 12/137. The platform source is exactly 62,820 bytes at
SHA-256 `97bfe71e...`.

## Serialized execution

1. Push and remotely verify the task, acknowledgement, start announcement, baseline evidence,
   live-state update, and ledger opening before mutation.
2. Submit the exact candidate by absolute path with `cgauto/api_submit.py` exactly once.
3. Preserve the complete stdout/stderr, exit code, returned submission id, and resulting agent id.
4. Never auto-retry an ambiguous response.
5. Monitor identity, runtime health, game count, score, and rank through the platform's fast
   convergence window; compare with the frozen pre-trial resident record.
6. Append every submission and read to the live ledger when it occurs. Announce cycle termination
   to all agents and the owner, update live state and the submission registry, then push.

## Submission result 2026-08-03T15:02:24Z

Exactly one explicit submit command used the absolute candidate path. `TestSession/submit`
returned HTTP 200 with submission id `41085842`; the tool exited 0 after `SUBMIT-OK` and did not
try another endpoint. The new agent is `6592097`. The first ten observed battles were queued and
unfinished. Complete response log:
`data/analysis/live-agent-6553250/no-orchard-ablation-submit-20260803T150224Z.log`, SHA-256
`725e8a2628452c51eef47c0ee5790b7ac6da562bd0f3f4da1b0099c594b87bea`.

Monitoring is read-only until termination or an explicit restore disposition.

## First live health 2026-08-03T15:04:31Z

Agent `6592097` / submission `41085842` has 13 parsed finished games plus one pending, score 17.93,
rank 97/137, one catastrophe, negative-margin mass 302, zero runtime signals, and clean identity.
This fresh partial read is not a value verdict; monitoring continues to the terminal queue state.

## 45-game checkpoint 2026-08-03T15:14:08Z

Agent `6592097` / submission `41085842` has 45 parsed finished games plus one pending, score 19.69,
rank 66/137, two catastrophes (4.4%), negative-margin mass 883, zero runtime signals, and clean
identity. The queue remains healthy; this is a phase marker, not the terminal value verdict.

## 74-game checkpoint 2026-08-03T15:21:07Z

Agent `6592097` / submission `41085842` has 74 parsed finished games plus one pending, score 22.49,
rank 38/137, four catastrophes (5.4%), negative-margin mass 1,561, zero runtime signals, and clean
identity. It remains below the 25.3 pre-trial resident while convergence continues.

## Safety and stop rules

- No second Arena mutation while this cycle is in flight.
- Restore exact E7a only for an explicit owner/controller disposition after evidence is captured,
  or immediately on a clear runtime/identity failure. An ambiguous submit response is never
  retried automatically.
- Keep `rust/src/bin/yamo_orchard_live.rs` exact at SHA prefix `fff6669b`.
- Do not touch `data/raw/games/`, the 05:17 cron, or any sealed map range.
