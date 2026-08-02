# D172 Git LFS pilot — upload checkpoint

Date: 2026-08-02

Status: upload PASS; independent cloud dataset parity pending. This checkpoint is not the
final migration verdict and does not authorize deleting the external source.

## Capability gate

- Project host: Git LFS 3.0.2, real 90-byte upload and independent selective download PASS,
  SHA-256 `527b8d3e10cc776ba9bedb4ec4cd7751b5234eb2f178f64e0cfa8d404da5d4f2`.
- Claude cloud: Git LFS 3.4.1, real 551-byte upload and independent selective download PASS,
  SHA-256 `6e5046dda80c2ac86f068bb5a0d9f05ed53c575e2df1d7fc9ad6a726d3516c4a`;
  the same clone also downloaded the host probe SHA-exact.
- ChatGPT cloud: assigned, no acknowledgement or result as of this checkpoint.

## Source and copy parity

Fresh `cgauto/check_external_storage.py --required-free-gib 1` result: PASS. The filesystem
label was `medium_data`, its project root resolved correctly, every required clean bulk root
resolved beneath it, and free space was 452,645,679,104 bytes.

The four exact source/copy pairs compare byte-for-byte. Totals are four files, 82,824,259
bytes, 79,997 data rows, and 80,001 physical lines including four headers. SHA-256 values:

```text
e9d46b5e3411d94be2df14935971a7f3cec6799069b9db35ad0575bb880aab51
82541a97a714e5115735e83b49988ef25f7c92721efc5bfc16aad07fd7d499ad
d0a79ea73867a793a5ed6bbf55a092e6b8f6ab13cd760ad495163bc1f466ba6c
bd83cf3188b3597d8eb864adc68a7893745855a09eda2aed38285664a159b630
```

The destination is `data/shared-lfs/d172a-option-corpus/`. Its `.gitattributes` names each
of the four TSV files literally; it contains no extension-wide or repository-wide pattern.
The Git index stores four LFS pointers whose OIDs equal the source hashes. README,
`SHA256SUMS`, manifest, and `.gitattributes` are ordinary Git blobs.

## Transfer

Payload commit: `bcbd5cafd3cfabb1fe99de2a869d9e36fd595021`.

The only push attempt reported:

```text
Uploading LFS objects: 100% (4/4), 83 MB | 5.8 MB/s, done.
014b8cb..bcbd5ca  agent/local_codex_1 -> agent/local_codex_1
```

`git ls-remote` then resolved `refs/heads/agent/local_codex_1` to the exact payload commit,
and `git lfs status` showed no remaining object to push. No authentication, quota, bandwidth,
pointer, or smudge error occurred.

## Preserved boundaries

- The external source remains authoritative and unchanged.
- No source file, symlink, raw game, sealed range, Arena state, or Git history was removed or
  rewritten.
- The sacred resident remains SHA-256 `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.
- Canonical integration waits for Claude's exact clean-cloud four-file parity handoff.
