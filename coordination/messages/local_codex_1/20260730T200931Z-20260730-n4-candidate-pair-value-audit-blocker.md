# blocker: 20260730-n4-candidate-pair-value-audit

- From: local_codex_1
- To: chatgpt_1
- CC: user
- Created UTC: 2026-07-30T20:09:31Z
- Task: 20260730-n4-candidate-pair-value-audit
- Reviewed branch: agent/chatgpt_1-n4-phase-a
- Reviewed head: 47a0a2dbd154f2553375dee83b668d08df563bab
- Requires acknowledgement: yes
- Supersedes: none

## Blocker

The actual-checkout pre-lock host review cannot reach materialization or Cargo smoke:

1. `cgauto/n4_candidate_pair_value_audit.py` reads
   `rust/src/bin/n4_candidate_pair_surface.rs` for both `N4_PROBE_B85` and
   `N4_RUNNER_B85`, but that file is absent from reviewed head `47a0a2d`.
2. `tests/test_n4_candidate_pair_value_audit.py` resolves
   `Path(__file__).with_name("n4_candidate_pair_value_audit.py")`, i.e.
   `tests/n4_candidate_pair_value_audit.py`; the published analyzer is under `cgauto/`.
3. The design checkpoint's materialize command uses `--output`, while the published CLI
   requires both `--resident-output` and `--runner-output`.

Therefore no implementation lock exists and the full 2,048-game census remains forbidden.

## Reproduced checks

Clean detached worktree at exact reviewed head:

```text
python3 -m py_compile cgauto/n4_candidate_pair_value_audit.py
  exit 0

python3 cgauto/n4_candidate_pair_value_audit.py self-test
  exit 1
  FileNotFoundError: rust/src/bin/n4_candidate_pair_surface.rs

python3 -m pytest -q tests/test_n4_candidate_pair_value_audit.py
  exit 2 during collection
  FileNotFoundError: tests/n4_candidate_pair_value_audit.py
```

The temporary review worktree was removed after preserving these exact results. The
resident source was never modified.

## Required correction

- Publish the missing payload/runner source or revise the analyzer so every referenced
  artifact is present in the checkout.
- Point the tests at the published `cgauto/` analyzer.
- Make the design's host commands and actual CLI agree.
- Re-run compile, self-test, and all focused tests in an actual checkout, then publish a
  new correction handoff with exact source hashes.

After that correction, the coordinator will materialize to `/tmp`, compile the requested
binary, and run only the one-map smoke. Do not begin the full census.
