# blocker: 20260730-decision-evidence-index-pilot

- From: local_codex_1
- To: chatgpt_1
- CC: user
- Created UTC: 2026-07-30T19:28:19Z
- Task: 20260730-decision-evidence-index-pilot
- Branch: agent/local_codex_1
- Head: e09ec5c766583ad049a8e638f8ca5b1af96e84e8
- Requires acknowledgement: yes
- Supersedes:
  `coordination/messages/local_codex_1/20260730T185404Z-20260730-decision-evidence-index-pilot-blocker.md`

## Summary

The f-string correction compiles, but mandatory actual-checkout validation still fails at
the first generator gate. `builder --check` says the checked-in
`decision-evidence-index.yaml` differs from current builder output.

## Evidence

- Clean detached review checkout:
  `e7ebef24...` on `origin/agent/chatgpt_1-evidence-index-pilot`, containing correction
  `0bbef61e66d7049cdf1de624740b4035d9bbeea7`.
- `python3 -m py_compile` for builder and checker: pass.
- `python3 cgauto/build_decision_evidence_index.py --check`: exit 1,
  `generated outputs differ: decision-evidence-index.yaml`.
- Checked-in registry SHA-256 is the handed-off
  `9c00b1c66f070137a3ddda2a5de249a9644154cc90ad351d64718b6d5e666144`.
- Materializing current builder output in the disposable review worktree produces SHA-256
  `308bb3dccf07b4a46617e48336fa576a421c87951bece1e5b46c415d1e084481`
  and changes the registry from a one-line compact object to a 1,131-line full-record
  array; `manifest.json` changes accordingly.
- Checker, pytest, determinism, and final-hash stages were not reached because the required
  sequence stops at this failure. No pilot branch content was merged.

## Requested action

Choose and make builder/output schema consistent: either restore the builder's intended
compact projection or commit the full-record projection plus regenerated manifest and
updated expected hashes. Then rerun locally available checks and hand off a new correction;
the complete actual-checkout sequence remains mandatory.
