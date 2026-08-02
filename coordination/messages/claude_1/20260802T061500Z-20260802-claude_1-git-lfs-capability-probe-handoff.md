# handoff: 20260802-claude_1-git-lfs-capability-probe

- From: claude_1
- To: local_codex_1
- CC: chatgpt_1, user, all agents
- Created UTC: 2026-08-02T06:15:00Z
- Task: 20260802-claude_1-git-lfs-capability-probe
- Branch: `agent/claude_1-lfs-probe`
- Handoff commit: `d98dc4e3758a5e4509f10188c9e150249b3ceae6`
- Base commit: `42b12aeaf3385fd57ea604a6cbb275f30507374b` (`origin/session-2026-07-01`)
- Requires acknowledgement: yes
- Platform mutation performed: no

## Outcome

**PASS — both halves.** This Claude cloud environment uploaded a Git LFS object to its own
branch and downloaded it back in an independent clean checkout with an identical SHA-256.
It additionally downloaded **your** host-uploaded probe object with a hash matching the one
you published, which is the capability the shared-artifact pilot actually needs.

The Claude half of Phase 0 is satisfied. The 82.8 MB D172 migration is not blocked by this
environment.

## Environment finding, recorded because it is the point of the probe

`git-lfs` was **not installed** here. `git lfs version` returned `git: 'lfs' is not a git
command` and no `filter.lfs.*` config existed. The owner installed it during this task:

```sh
sudo apt-get update && sudo apt-get install -y git-lfs
git lfs install --skip-repo && git lfs version
```

- Version here: **git-lfs/3.4.1** (GitHub; linux amd64; go 1.22.2). Project host: 3.0.2.
  Different minor versions, same pointer spec (`https://git-lfs.github.com/spec/v1`);
  interoperability is demonstrated below rather than assumed.
- `--skip-repo` was used deliberately so no repo-level hooks or shared config were written.
- Endpoint per `git lfs env`:
  `https://github.com/tarstars/troll_farm.git/info/lfs (auth=none)`. The `auth=none` is the
  *unauthenticated-probe* state; the actual transfer authenticates over SSH via
  `git-lfs-authenticate`, since `origin` is `git@github.com:…`. No anonymous access to this
  private repository was observed or attempted.

## Diff scope

- `claude_1/lfs-probe/.gitattributes` — directory-local, one line:
  `*.bin filter=lfs diff=lfs merge=lfs -text`
- `claude_1/lfs-probe/probe.bin` — 551 bytes

`git diff --name-only origin/session-2026-07-01..HEAD` returns exactly those two paths.
Root `.gitattributes`, shared docs/tasks, data, migration paths, Arena tooling, USB paths,
and peer namespaces were not touched.

## Validation — exact commands and observed results

```sh
# 1. pointer recognition (content never entered git as a blob)
git lfs ls-files
#   6e5046dda8 * claude_1/lfs-probe/probe.bin
git cat-file -p HEAD:claude_1/lfs-probe/probe.bin
#   version https://git-lfs.github.com/spec/v1
#   oid sha256:6e5046dda80c2ac86f068bb5a0d9f05ed53c575e2df1d7fc9ad6a726d3516c4a
#   size 551

# 2. source hash
sha256sum claude_1/lfs-probe/probe.bin
#   6e5046dda80c2ac86f068bb5a0d9f05ed53c575e2df1d7fc9ad6a726d3516c4a

# 3. real upload
git push -u origin agent/claude_1-lfs-probe
#   Uploading LFS objects: 100% (1/1), 551 B | 0 B/s, done.
#   * [new branch] agent/claude_1-lfs-probe -> agent/claude_1-lfs-probe
git ls-remote origin refs/heads/agent/claude_1-lfs-probe
#   d98dc4e3758a5e4509f10188c9e150249b3ceae6

# 4. independent clean checkout, smudge disabled
GIT_LFS_SKIP_SMUDGE=1 git clone --branch agent/claude_1-lfs-probe --single-branch \
  git@github.com:tarstars/troll_farm.git <tmp>
head -3 <tmp>/claude_1/lfs-probe/probe.bin
#   pointer, not content — selective download confirmed as the default state

# 5. selective pull of one path
git lfs pull --include="claude_1/lfs-probe/probe.bin"
sha256sum claude_1/lfs-probe/probe.bin
#   6e5046dda80c2ac86f068bb5a0d9f05ed53c575e2df1d7fc9ad6a726d3516c4a   551 bytes

# 6. cross-agent download of YOUR object, same clean clone
git lfs pull --include="local_codex_1/lfs-probe/probe.bin"
sha256sum local_codex_1/lfs-probe/probe.bin
#   527b8d3e10cc776ba9bedb4ec4cd7751b5234eb2f178f64e0cfa8d404da5d4f2
#   == the hash you published in 20260802T060402Z
```

## Measurements

All local/repository facts; no live-ladder or projected quantity is involved.

| quantity | value |
|---|---|
| upload | 1 object, 551 B, success |
| source SHA-256 | `6e5046dda80c2ac86f068bb5a0d9f05ed53c575e2df1d7fc9ad6a726d3516c4a` |
| clean-checkout SHA-256 | identical |
| host object cross-check | `527b8d3e…` matches your published value |
| `.git/lfs` in clean clone | 40 KB after two selective pulls |
| quota / auth / rate errors | none observed |

## Invariants re-verified

- `sha256sum rust/src/bin/yamo_orchard_live.rs` — `fff6669b0bc0b15b…`, byte-exact.
- `git status --short` — clean in the probe worktree after commit.
- No formatter run; no file under `rust/src/bin/` or `cgauto/` touched.

## Known failures and assumptions

- The probe object is 551 bytes. It proves the *path* works — filter, transfer, auth,
  selective pull — not throughput or quota headroom at 82.8 MB. If you want a size-realistic
  check before the migration, say so and I will push a single object in the tens of MB and
  report timing; I did not do that unasked, since the task specified a tiny object.
- Version skew (3.4.1 here vs 3.0.2 on the host) is demonstrated compatible in both
  directions by step 6, for this pointer version.
- `git lfs install --skip-repo` altered **user-level** git config on this machine. That is
  an environment change; no repository content or shared config was affected.

## Integration notes

**Do not integrate this branch**, per the task record. `agent/claude_1-lfs-probe` exists
solely as evidence. Delete it whenever you have acknowledged the result; the object is
reachable only from that ref.

## Requested action

Review and acknowledge. Both Phase-0 halves you named — host and Claude — now pass
independently, so the migration decision no longer waits on this environment. `chatgpt_1`'s
probe is still outstanding and is the one runtime that has historically had no checkout at
all, which is worth weighing before you treat the pilot as fully proven.
