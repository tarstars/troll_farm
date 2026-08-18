# OSC-031 owner-pinned 167-manifest independent reproduction — 2026-08-18

Verdict: **REPRODUCED**.

At implementer artifact `20e713aa5e9d9e1eb00a2a5180f1dc0a88de535c`, I ran
`claude_1/chop4c/derive_167_manifest.py` in a detached worktree. All five pinned input
hashes verified before execution. The accepted diagnostic path independently produced:

```text
window [11,200] · pool-3 NO_GOAL turns for unit 0: 189
excluded by token: 1 · by eligibility != {CHOP}: 22
|manifest| = 167  (pre-registered 167)
```

The regenerated manifest is byte-identical to the committed artifact and has SHA-256
`b9eed4c2d66401761845bcb223893cc91a82171806cc43fd1ce4175bae1f21e5`.

This reproduces only the task-owner-pinned G-4c.3 population derivation. It does not
accept a clause distribution, cure the outstanding instrument reconciliation defect,
or authorize a finding, judgment, resident mutation, or Arena action.
