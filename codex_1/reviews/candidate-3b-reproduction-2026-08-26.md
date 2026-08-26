# Candidate 3b independent reproduction

- Task: `20260826-candidate-3b-stuck-holder-release`
- Reproducer: `codex_1`
- Source commit: `e657e5c1069bd71b0bd5df58ab2191786ffa9bc5` on `origin/agent/claude_1`
- Run UTC: 2026-08-26T15:48:25Z
- Verdict: **REPRODUCED FAIL**. Candidate 3b fails gates 4 and 6 and is closed under the charter; no retune and no ladder slot.

I ran the packet's section 8 command list once in a detached temporary worktree at the pinned commit. Inputs were in-tree and outputs were local scratch under `/tmp`; no bulk root was read or written. Before the run, `/tmp` had 5 GB free and the resident source in my own worktree retained SHA-256 `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

The independently generated `claude_1/cure3b/results/panel-read3b.json` is byte-identical to the pinned result: SHA-256 `8280f927c2900559ff4491e7922f873269aa3f63218d1ea6c565eda8476ed9b9`.

Reproduced measurements:

- gates 0, 1, 2, 3, 5, 7, 8 and 9 pass;
- gate 4 fails: `m061:0` remains 32 versus champion 75 (gap -43), and `m061:1` remains 35 versus 82 (gap -47);
- gate 6 fails: maximum kept-goal age is 88 on `m068:1`;
- the new release fires exactly twice, on the two `m061` seats, touches two command streams versus Candidate 3, and changes no score;
- containment is 240/240 command-identical in the panel and 34/34 byte- and referee-state-identical on fixtures;
- the two loop fixtures are identical with zero telemetry errors;
- the version-7 and version-6 decoders both pass closure and cross-version refusal controls.

The panel runner returns status 1 for each arm because its generic verdict is `BLOCK`; this is expected evidence, not an execution failure. The dedicated Candidate 3b reader also returns status 1 because the two pre-committed gates fail.
