# handoff: 20260730-n2-b4-4-verification-sweep

- From: local_codex_1
- To: chatgpt_1
- CC: user
- Created UTC: 2026-07-30T19:32:59Z
- Task: 20260730-n2-b4-4-verification-sweep
- Branch: agent/local_codex_1
- Head: 7c0602481391a5d35bb49791583b2fc3922e09fd
- Requires acknowledgement: yes
- Supersedes: none

## Summary

N2 is ready for review with verdict **B4_4_CORRECTED** and C1–C7 all `CORRECTED`.
Canonical live docs now prohibit the stale all/every-peer, no-loop, wood-purity,
causal-survival, and one-purpose readings while preserving the reproducible pooled
descriptives.

## Evidence

- Canonical result:
  `data/analysis/live-agent-6553250/n2-b4-4-verification-result-2026-07-30.md`,
  SHA-256
  `427e4b4df5aa3849f824ff39e2718b6e63b82d2737eee0722d18c6b5b9e1d057`.
- Machine result SHA-256:
  `ba7ae0eb9985efafddda0d0a52bb1bf02ab701b4137eca893ca02fee77c0359d`.
- Manifest SHA-256:
  `690934b7ce3cf12a12d4c4cfb716d298d562dfc4a51fbce40d5d31a1adee6a79`;
  5,614 hashed files, zero missing.
- Per-agent table SHA-256:
  `c974630dcb95808f928d025bbfd00021e80f2061e391ce084d8cd853eb755873`.
- Analyzer/test SHA-256:
  `4147bf09b29a08126676f0846c9aa4ee61935be3f2ded5490257927204c87cc9` /
  `d502b84248c731989fea4936c8ba4c30d4e24ac12e5e6ab2d5db08ec9f17e3b5`.
- Compile, self-test, and four focused tests pass. Full command exits 0:
  2,963/2,963 union occurrences, 2,787/2,787 anchor integrity parity.
- Resident remains byte-exact at SHA
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

## Requested action

Review the provenance classification, conditional/per-agent denominator distinction,
generation-outcome attribution, early-orchard versus late-conversion wording, C1–C7
verdicts, and canonical replacement text. Publish accept or a concrete blocker. No
independent Arena or mutation action is requested.
