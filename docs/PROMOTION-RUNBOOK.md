# B4.1 Promotion Runbook — arena candidate transfer

Operational, copy-paste command sequence for the standing promotion protocol B4.1
(`docs/BACKLOG.md` Tier 4). Written 2026-07-28 while candidate D171a was still running, to
have the machinery ready the moment it qualifies. Reusable mechanics; the *authorization* below
is scoped to one candidate only — see next section.

## Authorization gate — read this first

**This runbook executes ONLY under the recorded owner authorization in `docs/STATE.md` §3**,
quoted verbatim:

> Arena writes require explicit user authorization. No exceptions. **STANDING
> AUTHORIZATION 2026-07-28: if D171a returns QUALIFIED (all frozen local gates pass),
> execute promotion protocol B4.1 without further ask** — capacity A/A → candidate
> submission → +20/+35/+50-min reads → frozen bands (≥+0.5 keep / ≤−0.5 or inconclusive
> → revert) → exact-resident restore on any failure. Scope: this one candidate only.

Current binding scope: **candidate D171a**
(`data/analysis/live-agent-6553250/d171a-oscillation-breaker-protocol-2026-07-28.md`) only.
Trigger condition: D171a's result doc records verdict **QUALIFIED**. If D171a is **CLOSED**,
nothing in this document runs. Do not reuse this runbook for a different candidate without a
fresh STANDING AUTHORIZATION entry recorded in STATE §3 — re-verify the section below before
relying on an old copy.

If in doubt about whether the authorization still applies (revoked, superseded, scope
mismatch), STOP after the read-only preflight (§4/Step 0) and ask.

## 1. Fixed identities (verified 2026-07-28, read-only)

| Field | Value |
|---|---|
| Puzzle id | `spring-challenge-2026-troll-farm` |
| User id / pseudo | `1302251` / `tass` |
| Test session handle (TSH) | `77167730956ef53402472b3c52474908f5b73026` |
| Resident agent | `6561795` |
| Resident submission id | `41015603` |
| Resident source | `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` (62,725 bytes) |
| Resident SHA-256 | `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55` |

Verified 2026-07-28: `sha256sum` of the resident file above, its `.sha256` sidecar, and the SHA
recorded in `docs/STATE.md` §1 are all byte-identical to each other. Byte size (62,725) also
matches. `cgauto/api_submit.py`'s hardcoded default source path is exactly the path above (read
from source, not executed).

## 2. The one placeholder

`$CANDIDATE` cannot be filled in ahead of time. Per D171a's frozen protocol, if QUALIFIED the
pair is expected at:

```
cgauto/submissions/candidate-agent6561795-oscillation-breaker.rs        # formatted, informational
cgauto/submissions/candidate-agent6561795-oscillation-breaker.min.rs    # slim — this is $CANDIDATE
cgauto/submissions/candidate-agent6561795-oscillation-breaker.min.rs.sha256
```

Confirm the real filename and SHA-256 in D171a's actual result doc
(`data/analysis/live-agent-6553250/d171a-oscillation-breaker-result-*.{md,json}`) before
substituting — if it differs from the expected name above, use the real one everywhere `$CANDIDATE`
appears below.

## 3. Tooling verified read-only, 2026-07-28 (no submission made by this verification)

- **`cgauto/api_submit.py [path-to-.rs]`** — path arg optional, defaults to the resident path in
  §1 (verified). Language gate: extension must resolve via `{".go": "Go", ".rs": "Rust"}`;
  anything else prints `LANGUAGE GATE: unsupported extension ... — abort`, exit 2. Separate size
  gate: source over 100,000 chars prints `SIZE GATE: ... — abort`, exit 2. On success it tries 4
  request shapes against `TestSession/submit`/`Solution/submit` in order; the first that returns
  HTTP 200 prints `<service>/<method>: 200 <first 220 chars of body>` then `SUBMIT-OK via
  <service> <method>`, exit 0. **No explicitly labeled "submission id" field is printed** — the
  numeric id is embedded in that response body text. Always pipe through `tee` to a log file (see
  §6) so it isn't lost to the 220-char terminal truncation; §6 Step 1/3 also gives a more robust
  way to recover it (read `submissionId` directly off a landed battle's player record).
- **`cgauto/cg_rank.py [--top N]`** — read-only. Prints the authoritative `ARENA-ROOM` line
  (rank/total/league/score/`agentId`/`promotable`), the puzzle-leaderboard row, and with `--top N`
  the top N ladder rows. Confirmed working live 2026-07-28 (§7 baseline below).
- **`cgauto/battles.py [max_games]`** — read-only. Prints `battles listed: N` (the figure
  `docs/STATE.md` calls "listed battles") plus a small W/L/margin sample joined against
  opponents' Gold rank. Confirmed working live 2026-07-28 (§7 baseline below).
- **`cgauto/arena_transfer_checkpoint.py --agent-id ID --submission-id ID --role ROLE
  [--output PATH]`** — read-only. Submission-scoped: rejects battles that don't match the given
  agent+submission id instead of silently mixing data (`identity_clean` flag) — this is what
  guards against the exact kind of cross-agent contamination that confused a read during the
  2026-07-08 `v1.38.0-deny1` verdict. Documented in live use for the 2026-07-18 Phase-21
  controlled-transfer execution
  (`data/analysis/live-agent-6553250/opponent-crop-controlled-transfer-execution-2026-07-18.md`);
  tested in `tests/test_arena_transfer_checkpoint.py`. Prints one summary line
  (games/score/rank/catastrophic-rate/negative-mass/`identity_clean`), exit 0 if clean else 2, and
  optionally archives the full JSON. **This is the primary read tool for every mandatory
  checkpoint below.**
- **`cgauto/recover_live_source.py <output> [--expected-sha256 SHA]`** — read-only (hits
  `TestSession/startTestSession`, an info fetch, not a submit endpoint per its own docstring).
  Recovers the actual IDE-saved source and aborts on a hash mismatch. Used as the first step in
  the most rigorous historical write protocol on record (2026-07-18 Phase-21 draft); reused here
  as Step 0.

### Read-tooling: what "the 07-17/18 fine-grained tool" actually is (gap note)

No standalone poll-loop script survives specifically from the 07-17/18 sessions as a named,
reusable artifact — those reads were ad hoc interactive calls, not committed under a durable
name at the time. This is a naming/provenance gap, not a functional one: `cg_rank.py` and
`battles.py` both predate 07-17/18 (committed 2026-07-06) and remain the lightest, fastest reads;
`arena_transfer_checkpoint.py` (present in git since the 2026-07-23 checkpoint commit, but
already described in the 2026-07-18 Phase-21 execution doc — that commit squashed several days
of session history) is a strictly safer successor built for exactly this job. Together they fully
cover rank/score/battle-count/top-N reads with timestamps; no substitute is needed. If, only if,
all three become unavailable: `data/scripts/collect_wide.py` calls the same
`Leaderboards/getFilteredPuzzleLeaderboard` endpoint and writes a `leaderboard.json` inside its
snapshot directory as a side effect (also runs once daily at 05:17 via cron) — usable as a coarse
rank/score fallback, but with no per-checkpoint timing precision and much heavier per-run cost
(it also pulls full battle histories). Prefer the three tools above.

## 4. Preconditions checklist (verify all before Step 1)

```bash
REPO=/home/tarstars/prj/troll_farm
cd "$REPO"
PY=.venv/bin/python
CANDIDATE=cgauto/submissions/<CANDIDATE_FILENAME>.min.rs   # <-- fill in from D171a's result doc

# 1. D171a verdict is QUALIFIED
grep -m1 -i "verdict" data/analysis/live-agent-6553250/d171a-oscillation-breaker-result-*.md

# 2. Candidate artifact + sidecar exist
ls -la "$CANDIDATE" "$CANDIDATE.sha256"

# 3. Candidate SHA-256 matches its sidecar AND the SHA recorded in D171a's result doc
sha256sum "$CANDIDATE"
cat "$CANDIDATE.sha256"
grep -i "sha-256\|sha256" data/analysis/live-agent-6553250/d171a-oscillation-breaker-result-*.md

# 4. Candidate is within api_submit.py's own size gate (<100,000 bytes)
wc -c "$CANDIDATE"

# 5. Working tree is clean for the paths this protocol touches — ignore the unrelated,
#    legitimate D171 in-flight diff on rust/src/bin/yamo_orchard_live.rs; do not touch that file
git status --short -- cgauto/submissions/ cgauto/api_submit.py docs/PROMOTION-RUNBOOK.md \
  docs/STATE.md docs/CONSTRAINTS.md docs/BACKLOG.md

# 6. Baseline read taken and logged (see §7). If more than ~24h old by execution time, or
#    anything about the resident's own standing looks off, re-run §7's two commands and log a
#    fresh baseline before Step 1.
```

All six must be clean/confirmed before Step 1.

## 5. Timing schedule

- **Capacity A/A (Step 1-2):** submit the resident as its own fresh control; read repeatedly
  (every 15-20 min is reasonable) until it reconverges within noise of the §7 baseline bracket
  (rank 43/112 @ 22.0). "Within noise" is operationalized here as **≈±1** — the project's own
  documented single-convergence sampling noise floor
  (`docs/archive/bronze-to-gold/arena-queue.md`, measurement policy v2); B4.1's own text does not
  give capacity-reconvergence a separate numeric band, so use judgment on top of this — a control
  that reads clearly flat/degraded (cf. the 2026-07-16 rollback precedent, `arena-verdict-2026-07-16.md`)
  fails capacity regardless of the exact threshold. If it fails to reconverge, STOP — go to §8 and
  do not submit the candidate.
- **Candidate (Step 3-4):** submit candidate at time `T0`. Mandatory reads at `T0+20m`,
  `T0+35m`, `T0+50m`. At each of the three times, read **both** the candidate and the control
  (same-window — re-read the control's *current* number at that instant, not just its Step-2
  bracket, so mid-window drift is caught). Decide at `T0+50m` using §7's bands. No extension
  logic is authorized under B4.1 (some one-off past protocols used one; B4.1's own text does not)
  — decide at +50 as read.

## 6. Step-by-step command sequence

```bash
REPO=/home/tarstars/prj/troll_farm
cd "$REPO"
PY=.venv/bin/python
RESIDENT=cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs
CANDIDATE=cgauto/submissions/<CANDIDATE_FILENAME>.min.rs   # <-- fill in
LOGDIR=data/analysis/live-agent-6553250
STAMP() { date -u +%Y%m%dT%H%M%SZ; }
```

### Step 0 — preflight (read-only)

```bash
$PY cgauto/recover_live_source.py /tmp/d171a-platform-source-preflight.rs \
  --expected-sha256 a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55
```

If this aborts (hash mismatch), STOP — something else changed the live submission out of band;
investigate before touching anything else.

### Step 1 — capacity A/A: submit resident as fresh control

```bash
$PY cgauto/api_submit.py "$RESIDENT" 2>&1 | \
  tee "$LOGDIR/d171a-promotion-b41-control-submit-$(STAMP).log"
```

Confirm `SUBMIT-OK` and exit 0 in the log. Note the wall-clock submit time.

```bash
# Discover the new control agent id (cg_rank.py's ARENA-ROOM line updates immediately)
$PY cgauto/cg_rank.py --top 3
```

Record `agentId=...` from the `ARENA-ROOM:` line as `$CONTROL_AGENT_ID`.

```bash
# Once >=1 battle has landed for the new agent, read its submissionId directly off the
# battle/player record — authoritative, avoids parsing the truncated submit response:
$PY - <<'PYEOF'
import sys; sys.path.insert(0, "cgauto")
import battle_taxonomy as arena
battles = arena.call("gamesPlayersRanking/findLastBattlesByTestSessionHandle", [arena.TSH, None])
for b in battles[:10]:
    for p in b.get("players", []):
        if p.get("userId") == 1302251:
            print(p.get("playerAgentId"), p.get("submissionId"), b.get("gameId"), b.get("done"))
PYEOF
```

Record the row matching `$CONTROL_AGENT_ID`'s `submissionId` as `$CONTROL_SUBMISSION_ID`.

### Step 2 — capacity read loop (repeat until reconverged, or declare capacity failure)

```bash
$PY cgauto/arena_transfer_checkpoint.py --agent-id "$CONTROL_AGENT_ID" \
  --submission-id "$CONTROL_SUBMISSION_ID" --role capacity-control \
  --output "$LOGDIR/d171a-promotion-b41-control-$(STAMP).json"
$PY cgauto/cg_rank.py --top 3
```

Repeat every 15-20 min until score is within ≈±1 of 22.0 on two consecutive reads (§5). Append
each read to §9. On success, proceed to Step 3. On capacity failure, go to §8.

### Step 3 — submit candidate (only after Step 2 passes)

```bash
$PY cgauto/api_submit.py "$CANDIDATE" 2>&1 | \
  tee "$LOGDIR/d171a-promotion-b41-candidate-submit-$(STAMP).log"
date -u +%Y-%m-%dT%H:%M:%SZ   # <- this timestamp is T0; compute T0+20/35/50m from it
```

Repeat the Step-1 agent/submission-id discovery (`cg_rank.py --top 3`, then the
`battle_taxonomy` one-liner) to get `$CANDIDATE_AGENT_ID` / `$CANDIDATE_SUBMISSION_ID`.

### Step 4 — mandatory reads at T0+20m, T0+35m, T0+50m

At each of the three times, read candidate **and** control:

```bash
$PY cgauto/arena_transfer_checkpoint.py --agent-id "$CANDIDATE_AGENT_ID" \
  --submission-id "$CANDIDATE_SUBMISSION_ID" --role candidate \
  --output "$LOGDIR/d171a-promotion-b41-candidate-$(STAMP).json"
$PY cgauto/arena_transfer_checkpoint.py --agent-id "$CONTROL_AGENT_ID" \
  --submission-id "$CONTROL_SUBMISSION_ID" --role same-window-control \
  --output "$LOGDIR/d171a-promotion-b41-control-$(STAMP).json"
$PY cgauto/cg_rank.py --top 3
```

**Additional safety trigger (on top of the score bands):** if either checkpoint JSON shows
`identity_clean: false`, or the candidate's `summary.validity_runtime_signals` is non-empty, treat
it as a failure regardless of score — go to §8. (This is a safety addition drawn from documented
historical practice, e.g. the b100_e6 protocol's "reject early only for a validity/runtime
signal" step; it is not itself a B4.1 score-band rule.)

Append every read's timestamp + score/rank/games to §9 — hard rule, not optional (§9).

## 7. Decision (bands verbatim from `docs/STATE.md` §3)

> frozen bands (≥+0.5 keep / ≤−0.5 or inconclusive → revert)

Delta = candidate score − same-window control score, evaluated at `T0+50m`:

- **delta ≥ +0.5 → KEEP.** Candidate stays live in the arena slot. Update
  `cgauto/api_submit.py`'s hardcoded `SOURCE` default to `$CANDIDATE`'s path. Commit that change
  plus a `docs/STATE.md` §1 update (resident identity: new agent/submission id, new source path
  and SHA), a `docs/BACKLOG.md` B4.2 bar-tracking update, a `docs/CONSTRAINTS.md` bullet if a
  class fact changed, and a ledger entry in the live volume (STATE §5 names it) — see
  `docs/RUNBOOK.md` "Per-experiment obligations" for the same house pattern.
- **delta ≤ −0.5, OR |delta| < 0.5 (inconclusive) → REVERT.** Go to §8 immediately. (This
  inconclusive-means-revert rule is B4.1/STATE §3's own text for this one-shot candidate trial —
  stricter than the continuous-queue policy-v2 default of "inconclusive = log and hold," which
  assumes a next-candidate chain that doesn't apply here.)

## 8. Abort / restore (run any time something goes wrong, or on REVERT)

The restore command is byte-identical to Step 1 — resubmit the exact resident explicitly (do not
rely on the default, even though it should still point here):

```bash
$PY cgauto/api_submit.py cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs \
  2>&1 | tee "$LOGDIR/d171a-promotion-b41-restore-$(STAMP).log"
```

Then verify identity and reconvergence:

```bash
$PY cgauto/cg_rank.py --top 3          # confirm new agentId, sane rank
# discover $RESTORE_AGENT_ID / $RESTORE_SUBMISSION_ID the same way as Step 1, then:
$PY cgauto/arena_transfer_checkpoint.py --agent-id "$RESTORE_AGENT_ID" \
  --submission-id "$RESTORE_SUBMISSION_ID" --role resident-restore \
  --output "$LOGDIR/d171a-promotion-b41-restore-$(STAMP).json"
```

Confirm `cgauto/api_submit.py`'s default was never edited before a KEEP decision:
`git diff -- cgauto/api_submit.py` should be empty. Record the restore in §9 and close the ledger
entry as REJECT/REVERTED, matching the 2026-07-17/18 precedents
(`docs/archive/legend/session-handoff-2026-07-16.md` "2026-07-18 controlled rollout arena:
rejected and resident restored").

**Failure triggers that route here (any one):** capacity A/A does not reconverge (§5); candidate
submit itself fails (non-zero exit, no `SUBMIT-OK`); the additional safety trigger in §6 Step 4;
or the score bands in §7.

## 9. Hard rule — execution log

**Every submission and every read gets a row here, appended at the time it happens, during
execution — not reconstructed afterward.** Do not batch this; append immediately after each
command.

| Timestamp (UTC) | Action | Command | Result |
|---|---|---|---|
| 2026-07-28T13:59:25Z | Pre-trial passive baseline read (rank/score/top-3) — this runbook's authoring pass, resident agent 6561795 | `.venv/bin/python cgauto/cg_rank.py --top 3` | `ARENA-ROOM: tass rank 43/112 Legend score 22.0 \| promotable=False \| agentId=6561795`; puzzle-board row: `tass: rank 43 score 22.0 Legend`; leagues `Wood2:121 Wood1:255 Bronze:405 Silver:686 Gold:526 Legend:112` (1000 ranked, global page); boss bar `score>~23.3 (top Gold @rank 113)`; top-3: `#1 31.00 delineate`, `#2 29.52 norxondor_gorgonax`, `#3 28.22 MSz` — matches `docs/STATE.md` §1's 2026-07-27 figures exactly (score frozen, confirms the D159/no-recompute finding) |
| 2026-07-28T13:59:35Z | Pre-trial passive baseline read (listed battle count) | `.venv/bin/python cgauto/battles.py 5` | `battles listed: 203` (matches STATE.md's "203 listed battles"); 5-game sample: 1/5 wins vs `FreZzz` (oppRank 39 @22.4), avg score 167 vs 187 |

(Append new rows below this line during actual B4.1 execution — capacity control submit/reads,
candidate submit/reads, decision, restore if any.)
