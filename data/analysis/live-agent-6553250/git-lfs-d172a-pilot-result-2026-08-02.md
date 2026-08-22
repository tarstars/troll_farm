# D172 Git LFS pilot — final result

Date: 2026-08-02

Verdict: **PASS — end-to-end selective distribution is proven.**

The project host uploaded exactly four immutable D172 corpus shards at payload commit
`bcbd5cafd3cfabb1fe99de2a869d9e36fd595021`. The single push reported 4/4 LFS objects and
83 MB at 100% completion with no authentication or quota error.

An independent Claude-cloud clone checked out that exact commit with automatic LFS smudge
disabled. All four TSV paths were pointers before download. A path-selective pull then
materialized only the D172 dataset and reproduced:

- four regular shard files;
- 82,824,259 apparent bytes;
- 80,001 physical lines and 79,997 data rows;
- four out of four SHA-256 values from the committed `SHA256SUMS` exactly.

The unrelated project-host LFS probe remained a pointer, so selective-download behaviour is
demonstrated rather than assumed. No auth, quota, bandwidth, pointer, smudge, or filesystem
error occurred. The external `medium_data` source remains authoritative and unchanged; no
source, symlink, history, raw game, sealed range, or Arena state was modified by migration.

Detailed host evidence:
`git-lfs-d172a-pilot-upload-checkpoint-2026-08-02.md`. Independent handoff:
`coordination/messages/claude_1/20260802T062800Z-20260802-claude_1-d172-lfs-download-verification-handoff.md`.
ChatGPT's distinct environment capability probe remains assigned and unresolved; it is not a
failure of the accepted host-to-Claude distribution path.
