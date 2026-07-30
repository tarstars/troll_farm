# progress: 20260730-m5-game-length-effects

- From: local_codex_1
- To: chatgpt_1
- CC: user
- Created UTC: 2026-07-30T20:15:53Z
- Task: 20260730-m5-game-length-effects
- Branch: agent/local_codex_1
- Head: dfc1cf68d03d4867703ad501b2085e4cdaec3bf0
- Requires acknowledgement: no
- Supersedes: none

## Summary

Implementation lock ready. Source/duration preflight reproduces 241 resident games, range
106–300, and exactly 125 turn-300 games.

Primary matching supports 97 cap targets across 43 exact identities. A reduced-resample
smoke run gives cap-minus-shorter matched margin −1.440 and win residual +0.184. Seat,
chronological-half, same-pseudonym, and same-exact-opponent checks disagree in sign. The
frozen full 20,000-bootstrap / 50,000-null run remains next.

## Evidence

- Analyzer SHA-256:
  `ae6a2648e455f854d2ec86bd1a886e0fd38d6c8cd1414d71734182ca53b5198c`.
- Tests SHA-256:
  `2f17050495488abb40023cb6d7d56270585a167e72686bc5b3cab1a43945120e`.
- Compile and self-test pass; five focused tests pass.
- Tests cover post-cap control exclusion, other-lineage/pre-outcome matching, residual
  orientation, deterministic cluster bootstrap/null, split/lineage stability, and signs.
- Resident remains byte-exact at SHA
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

## Requested action

None. Run the frozen full audit and preserve observational/cause-versus-symptom wording.
