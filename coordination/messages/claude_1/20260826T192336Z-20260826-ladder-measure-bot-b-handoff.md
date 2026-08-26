---
schema_version: 2
type: handoff
task_id: 20260826-ladder-measure-cured-dancing-troll
from: claude_1
to: ["codex_1", "local_claude_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260826T192336Z-20260826-ladder-measure-bot-b-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: db89554afb757608826f6a8fede3d3e5e94f8c6e
artifact_paths: ["cgauto/submissions/candidate-3-keep-v6-instrument.rs", "cgauto/submissions/candidate-3-keep-v6-instrument.rs.sha256", "readable/reports/candidate-3-keep-v6-instrument.round-trip.json", "claude_1/ladder-measure-b/make_candidate3_v6.py", "claude_1/ladder-measure-b/candidate-3-keep-v6-instrument.rs", "claude_1/ladder-measure-b/bot-b-build-2026-08-26.md", "claude_1/ladder-measure-b/results/build.json"]
created_utc: 2026-08-26T19:23:36Z
---

- To: codex_1, local_claude_1
- CC: user, chatgpt_1
- Task: 20260826-ladder-measure-cured-dancing-troll
- Requires acknowledgement: yes — codex_1: the one check of step 2; local_claude_1: the file to submit as B

# handoff: L-1 step 1 — bot B built (Candidate 3 keep-rule ON, v6 diagnostics ON), compacted the 0-3a way, round trip EXACT, and provably not the same program as bot A

**The file to submit as B:** `cgauto/submissions/candidate-3-keep-v6-instrument.rs`,
sha256 `04e3db43865121e82a8c6fab65e9fa09f6be487406af3a1fdd8e2a7807a0d879`, 63,961 bytes
(bot A is 63,962; the un-instrumented champion is 75,653 — B is smaller than a file the
platform has already accepted). Sidecar `.sha256` is beside it.

**In plain words.** Bot B is the champion with one rule switched on — a troll keeps its goal —
plus the same per-turn diagnostic line bot A carries. A and B differ by **exactly one line** of
readable source, line 602:

    A:  const KEEP_RULE_ENABLED: bool = false; const NARRATE_V6_ENABLED: bool = true;
    B:  const KEEP_RULE_ENABLED: bool = true;  const NARRATE_V6_ENABLED: bool = true;

Nothing else differs. That single line is the whole experiment.

**How it was built.** `claude_1/ladder-measure-b/make_candidate3_v6.py` regenerates the arm from
the one source and the one flag line and then refuses unless the bytes it produced are the bytes
that were already gated — a generator that agrees with the record, not a copy. Fatal checks:
readable base `ad1ae4ef…`; compacted champion `547fa706…` with the same canonical token stream
as that base; source `01b61444…`; the flag line occurs exactly once and B differs from the source
in **zero** lines (B *is* the source arm — A's rule-off arm is the one that differs in one);
byte-identity with the gated `claude_1/cure3/arm-instrument.rs`; `rustc --edition=2021 -O` on
the arm; write, re-read, token-stream compare, compile the written file; and finally the written
file's token stream is **not** bot A's — a run that compared A with A would otherwise pass in
silence. Report: `readable/reports/candidate-3-keep-v6-instrument.round-trip.json`, verdict
`CANDIDATE_3_KEEP_V6_INSTRUMENT_ROUND_TRIP_EXACT`.

**codex_1, step 2 (one line back).** Confirm the submission inherits the recorded parity: with
the diagnostic line stripped, B's command streams on the 240 local games are identical to the
parity-gated arm's. I did not re-run that panel; the claim I rest on is the recorded one in
`claude_1/cure3/g1-packet-2026-08-26.md` (instrument arm with `MSG` stripped byte-identical in
play to the candidate arm on all 240 games). Confirming it for the *compacted* file is your check,
not mine — that is the card's "dead means" clause and I have not pre-empted it.

**What I do not claim.** Nothing about score: B cost 65 fruit over 240 local games and whether
that shows on the ladder is what the measurement is for. No KEEP/REVERT comes out of this task and
the champion of record is unchanged. I also do not claim the diagnostic line survives the
platform's `MSG` truncation on a *collected* game — the v6 wire budget is 328 characters and the
longest `MSG` the platform has ever returned to us is 127; that is still open and the card covers
it.

Standing order followed: the branch was rebased onto `origin/main` first, this handoff pinned
after, and `db89554a…` is reachable from `agent/claude_1`.
