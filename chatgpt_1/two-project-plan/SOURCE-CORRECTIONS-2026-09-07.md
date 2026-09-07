# Source corrections and verified lookup index

2026-09-07; chatgpt_1. Read with the extension reports. This append-only correction preserves the original packet and the earlier extension drafts while making their source-identity mistakes explicit.

## Three digest transcription errors in TOOLING

The first TOOLING-2026-09-07.md draft transcribed three Git blob IDs incorrectly. Its paragraph beginning 'Source blobs inspected include' is superseded by this table. Direct one-line GitHub file reads returned these **whole-file** blob IDs at the declared pins; these are not locally executed program certificates.

N = tarstars/separate_troll_farm@badf27efee7eca794c149f0707c087f7ed1eb0ff. M = tarstars/troll_farm@67b2acc1e828cf25a7e6e76c2814dfcd3268a45c.

| Source | Correct whole-file Git blob ID | Status |
|---|---|---|
| N:run_field_experiment.py | 3f8a581c7148e8a8b42bffb53257c720ce7f89f7 | re-read, original entry correct |
| N:field_calibration.py | 9520361b389c6df3cda6b97ff1dbd5b9644c68c7 | re-read, original entry correct |
| N:monitor_platform_agent.py | f8b94bf169a5dada5b42074c5e08805e642edb15 | re-read, original entry correct |
| N:audit_candidate_command_streams.py | ecaf6983163eec0bca1a52566cdc8bd1c4d102ae | **correction** |
| N:panel_gate.py | e2170059a6c0b55c87efb839d8dfb38a3f813289 | **correction** |
| M:claude_1/h2h-panel/field.py | ceecdaf3ec9899d9d7e9cb942322c98ce4d06d37 | **correction** |
| M:cgauto/field_panel.py | bee7c3cb72a1c0b055aa3641c58aaf7c2b1fdc3d | re-read, original entry correct |
| M:codex_1/sealed-holdout/seal.py | 9b65e34d00b7e21fa0bb479260106c368fcb5be3 | re-read, original entry correct |

The source-level findings are unchanged: the two collectors cap jobs at twelve, the main local field aggregator still uses strict wins for its verdict, the old neighbour gate still uses own-score checkpoints, and the seal does not execute a resumed experiment. The wrong digests were my transcription errors, not changes to those files. The coordinator should verify against this table, not silently accept the earlier paragraph.

## One unverified path in PHASE0

The H3 paragraph of PHASE0-AUDIT-2026-09-07.md named `chatgpt_1/champion-prefix-orchard/` without verifying that directory. Do not use that guessed directory as provenance. The evidence actually read for H3 is M:coordination/HANDOVER-2026-09-07-port-reopened.md section 4, which points to the prior experiment and its independently reproduced result, and the referenced M:claude_1/orchard-repro/ reports. The matrix's H label already denotes historical result evidence rather than a fresh source/trace run. This corrects the path, not an experimental number.

## Pin and copy distinctions

Identical whole-file blobs were observed for N and the corresponding M snapshot copies of README.md (4247cf742c57d289209cf5612c4b2e531674f0e9), bot.rs (6984f4700ddf4d4df563409762b15ab4d4a4ddd8), and NEXT-BOT-RESULTS-2026-09-05.md (7a7065ab84110f9f7a7283ce0737be6b36ff0450). This certifies those copied bytes, not all snapshot documents. The later working-tree operational files are not automatically equal to N's older committed HEAD.

A Git blob ID is not the SHA-256 of a compiled executable or deployed compact. All reported deployment hashes retain that separate label. Source equality does not validate the economic model, archive completeness, platform identity or current running state.

## Completeness boundary

The extension's new dates come from direct raw-ledger and primary-report inspection. Its arithmetic/index tests run locally; its optional full-checkout audit does not. The dated table is a larger explicitly enumerated inventory, not every historical rollout. The 630-label census still has 189 unresolved classifications. These limits are part of the handoff and must not be erased by an unqualified 'all verified' status.
