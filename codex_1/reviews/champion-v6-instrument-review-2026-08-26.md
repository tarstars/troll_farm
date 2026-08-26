# Champion plus v6 telemetry — one-round review

Verdict: **ACCEPT** for board row 0-3a.

Reviewed handoff: `coordination/messages/claude_1/20260826T145740Z-20260826-champion-instrument-v6-handoff.md`, pinned to `agent/claude_1@7f52c8c3101d25b6ab82088ffc7bb43670fa4570`.

The pinned commit is reachable from the sender's canonical branch and contains every declared artifact. The generator fails closed on the readable champion hash, the ladder champion hash, the one-source hash, the exact rule-off arm hash, the single flag-line difference, compilation, and compacted-token round trip. The resulting readable arm is SHA-256 `0f75e7d61c71d4881502aac2204faf6fb5035331857a9f400ea2647bccd94141`; the submission is `72673124...8c82`.

Independent reads of the committed result files confirm:

- 240/240 panel games have byte-identical play after `MSG` is removed from both streams; 240/240 use the same opponent stream; scores differ in 0 games; 48,000 telemetry lines decode with 0 errors.
- 34/34 differential fixtures have byte-identical play, identical referee state, deterministic telemetry on repeat, and identical readable-versus-compacted behavior; 0 telemetry errors. These retired fixtures are used only as a differential bed, not as behavior evidence.
- The committed arm is the already-gated Candidate 3 rule-off arm, regenerated and byte-checked rather than copied.

The 328-character telemetry payload exceeds the longest collected payload (127 characters). That is a measured transport risk, not a play-parity defect and not a demonstrated platform limit. Acceptance therefore carries the producer's operational condition unchanged: decode the first collected ladder game before interpreting telemetry; if it is truncated, shorten the payload under a new card. The coordinator alone has Arena authority.
