# handoff: 20260802-claude_1-d172-lfs-download-verification

- From: claude_1
- To: local_codex_1
- CC: chatgpt_1, user, all agents
- Created UTC: 2026-08-02T06:28:00Z
- Task: 20260802-claude_1-d172-lfs-download-verification
- Branch: `agent/claude_1-lfs-verify`
- Base commit: `42b12aeaf3385fd57ea604a6cbb275f30507374b` (`origin/session-2026-07-01`)
- Verified payload commit: `bcbd5cafd3cfabb1fe99de2a869d9e36fd595021`
- Requires acknowledgement: yes
- Platform mutation performed: no

## Outcome

**PASS — exact parity on every acceptance criterion.** An independent clean clone in this
Claude cloud environment, with automatic smudge disabled, selectively downloaded only the
four D172 shards from payload commit `bcbd5ca` and reproduced the frozen manifest exactly.

| criterion | expected | observed | verdict |
|---|---|---|---|
| regular files | 4 | 4 | exact |
| apparent bytes | 82,824,259 | 82,824,259 | exact |
| physical lines | 80,001 | 80,001 | exact |
| data rows | 79,997 | 79,997 | exact |
| SHA-256, all four | committed `SHA256SUMS` | 4/4 `OK` | exact |

`sha256sum -c SHA256SUMS` returned `OK` for all four shards. No auth, quota, bandwidth,
pointer, smudge, or filesystem error occurred, so the no-retry-on-ambiguity rule was never
engaged.

## Validation — exact commands and observed results

```sh
GIT_LFS_SKIP_SMUDGE=1 git clone --no-checkout git@github.com:tarstars/troll_farm.git <tmp>
GIT_LFS_SKIP_SMUDGE=1 git checkout --detach bcbd5cafd3cfabb1fe99de2a869d9e36fd595021
git rev-parse HEAD          # bcbd5cafd3cfabb1fe99de2a869d9e36fd595021

# step 2 — pre-pull state: every TSV is a 133-byte pointer
head -2 data/shared-lfs/d172a-option-corpus/*.tsv
#   version https://git-lfs.github.com/spec/v1
#   oid sha256:e9d46b5e…  82541a97…  d0a79ea7…  bd83cf31…

# step 3 — selective pull, 8.173 s wall for ~83 MB
git lfs pull --include="data/shared-lfs/d172a-option-corpus/*.tsv"

# step 4 — parity
ls -1 *.tsv | wc -l                    # 4
stat -c%s *.tsv | paste -sd+ | bc      # 82824259
cat *.tsv | wc -l                      # 80001   → 79997 data rows (4 headers)
sha256sum -c SHA256SUMS                # 4× OK
```

Per shard: 20,862,015 / 20,608,837 / 20,642,952 / 20,710,455 bytes and 20,150 / 19,907 /
19,940 / 20,004 lines. Each file ends with a trailing newline and carries exactly one
header row beginning `map_seed<TAB>seat<TAB>opponent_index<TAB>opponent<TAB>tu…`.

## Selectivity — the property the migration actually depends on

`git lfs ls-files` in the verified checkout marks the four D172 shards `*` (downloaded) and
`local_codex_1/lfs-probe/probe.bin` `-` (pointer only); that probe file remains 127 bytes
on disk. The local `.git/lfs` store is 80 MB — the requested objects and nothing else. A
consumer can therefore materialise one shard family without paying for unrelated LFS
content, which is the behaviour the shared-artifact plan assumes.

## Measurements

Local repository facts only; no live-ladder or projected quantity involved. Transfer took
8.173 s wall (1.051 s user, 0.888 s sys) for ~83 MB, roughly 10 MB/s on this host — a
capacity observation, not a guarantee.

## Invariants re-verified

- Verification ran in a throwaway clone outside the project worktrees; the dataset, the USB
  source, the probe branches, shared docs/tasks, Arena tooling, and peer namespaces were
  not modified.
- Diff scope of this branch: `claude_1/d172-lfs-verification/verification-2026-08-02.txt`
  and this message.
- `sha256sum rust/src/bin/yamo_orchard_live.rs` in my working tree — `fff6669b…`, byte-exact.

## Known failures and assumptions

- One download, one environment, one payload commit. It proves this consumer can retrieve
  the published objects exactly; it does not test concurrent consumers, GitHub LFS bandwidth
  quota across a month, or restoration from a deleted branch.
- The 10 MB/s figure is a single sample on a cloud VM and should not be planned against.

## Integration notes

**Do not integrate this branch**, per the task record. It exists as evidence. The raw
command log is committed at `claude_1/d172-lfs-verification/verification-2026-08-02.txt`.

## Requested action

Review and acknowledge. From my side the Phase-1 payload is independently verified as
downloadable and byte-exact from a second environment, so the migration's read path is
proven end to end: host upload → GitHub → clean-room selective download at exact hashes.
