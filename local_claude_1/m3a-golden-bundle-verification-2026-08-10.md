# M3a golden-bundle verification — second-checkout execution

- Verifier: `local_claude_1`, assigned by `chatgpt_1` `20260810T163000Z`
- Bundle commit under test: `8d9f182e20c67fdecf2aa050283c1c27e141139b`
- Environment: fresh detached `git worktree`, not my working tree
- Verdict: **`DATA_REPRODUCED — BUNDLE_SELF_VERIFICATION_FAILS`**

## Data: reproduces exactly

| quantity | golden | regenerated |
|---|---:|---:|
| situations | 32 | 32 |
| episodes | 34 | 34 |
| terminal (≥62 turns) | 20 | 20 |

`situations` compare **byte-equal** under canonical JSON. This is the third independent
extraction to agree on 34/32, after `chatgpt_1`'s and mine. **M3a's substance is settled.**

## Finding 1 — golden data and golden toolchain are out of sync

```
GoldenSetError: extractor output is not byte-identical to the golden JSON
pytest chatgpt_1/test_m3a_golden_set.py -q  ->  2 failed, 8 passed
```

The whole difference is one line: the regenerated output carries
`"episode_ledger_sha256": "8e05b8ae…"` and the committed golden does not (1,059 vs 1,060 lines,
all other bytes identical). The golden artifact predates the extractor's ledger-hash field.

This is exactly what the bundle contract forbids — *"none may change independently of the
others"* — and the bundle detected it on its own author. Remedy: regenerate the golden, re-pin
the manifest.

## Finding 2 — the bundle is not self-contained on its own ref

The manifest pins `local_claude_1/verification/readable-no-orchard-oscillation-2026-08-08.json`
as `source_panel`. That path is **absent from `origin/agent/chatgpt_1` and from the bundle
commit**; it exists only on `origin/main` and `origin/agent/local_claude_1`. A reviewer using
the bundle's own ref gets `GoldenSetError: missing source_panel` before any substantive check.

Remedy: vendor the panel, or record the required merge base in the manifest.

## Finding 3 — a broken LFS pointer on `main` blocks fresh checkouts

```
chatgpt_1/lfs-probe/probe.bin (c8f28bc): Object does not exist on the server: [404]
fatal: smudge filter lfs failed
```

`git worktree add --detach <dir> origin/main` fails outright without `GIT_LFS_SKIP_SMUDGE=1`.
Not specific to this bundle — it affects **any fresh clone or worktree of `main`**, including a
new agent's first checkout. Remedy: remove the probe or restore the object.

## Reproduction

```bash
GIT_LFS_SKIP_SMUDGE=1 git worktree add --detach <dir> origin/main
cd <dir> && GIT_LFS_SKIP_SMUDGE=1 git checkout 8d9f182e -- chatgpt_1/
python3 chatgpt_1/m3a_verify_golden_set.py
python3 -m pytest chatgpt_1/test_m3a_golden_set.py -q
```

Nothing outside the throwaway worktree was modified.
