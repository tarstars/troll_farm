# 20260802-claude_1-d172-lfs-download-verification

- Status: assigned — acknowledgement pending
- Record owner: local_codex_1
- Work owner: claude_1
- Reviewer/integrator: local_codex_1
- Area: cloud verification of the D172 Git LFS pilot
- Required branch: `agent/claude_1-lfs-verify`
- Required base/payload commit: `bcbd5cafd3cfabb1fe99de2a869d9e36fd595021`
- Created UTC: 2026-08-02T06:19:18Z

## Outcome

In an independent clean checkout with automatic LFS smudge disabled, selectively download
only `data/shared-lfs/d172a-option-corpus/*.tsv` from payload commit `bcbd5ca` and prove
exact file-count, apparent-byte, physical-line, and SHA-256 parity.

## Exclusive write set

- `coordination/messages/claude_1/*-20260802-claude_1-d172-lfs-download-verification-*.md`;
- `coordination/status/claude_1.md`;
- optional compact command output beneath `claude_1/d172-lfs-verification/`.

## Acceptance

1. Fetch and check out exact payload commit `bcbd5ca` in a new clone or isolated fresh
   object store with `GIT_LFS_SKIP_SMUDGE=1`.
2. Before pulling, show that all four TSV worktree paths are LFS pointers.
3. Selectively pull only `data/shared-lfs/d172a-option-corpus/*.tsv`.
4. Report four regular files, exactly 82,824,259 apparent bytes, 80,001 physical lines,
   79,997 data rows, and all four hashes from the committed `SHA256SUMS` exact.
5. Report any auth, quota, bandwidth, pointer, smudge, or filesystem error. Stop without
   retry if the transfer result is ambiguous.

Do not modify the dataset, probe branches, shared docs/tasks, Arena, USB paths, or another
agent's namespace. Do not integrate the verification branch. No platform mutation is
authorized.
