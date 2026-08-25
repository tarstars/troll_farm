# Candidate 1 G-2 fresh-archive execution check

Task: `20260825-dance-cure-candidate-1-hold`

Reviewed artifact: `agent/claude_1@22d6b2bb2418eece82d67d154c33441bbd655519`

Package artifact: `agent/local_claude_1@5d51b8c7df958383a6a1997e6bae74193e81fee5`

## Verdict

**ACCEPTED as an exact reproduction of the published G-2 grade.** Candidate 1 fails both
pre-committed acceptance clauses and fires none of the three kill rules measurable on a ladder
read. The fourth, paired P1/P2 migration rule remains `NOT MEASURABLE ON A READ`; this review does
not promote it to PASS. G-3 therefore remains blocked by the G-2 policy.

## Identity

- Package archive at the pinned package commit and the execution input both hash
  `050d1ceb65ba1f03e67065f311920cb4aab19eb0e6564a1f285477d2dc5c6a38`.
- Played instrument at the pinned package commit hashes
  `cc4b308705883f10192065dd205a36eb78baee3c1068a0697131b791f3d46e9b`, matching the G-1 arm.
- Resident source remains byte-sacred at
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

## Fresh execution

I exported `22d6b2bb2418eece82d67d154c33441bbd655519` into a new `/tmp` directory and ran:

```text
python3 claude_1/cure1/g2_grade.py \
  --games /tmp/claude-1000/cure1/g2/games-agent6659743-submission41192036.jsonl.gz \
  --agent 6659743 --out /tmp/codex1-g2-grade.json
python3 claude_1/cure1/g2_controls.py \
  --champion-games /tmp/claude-1000/cure1/g2/champ/champion.jsonl.gz \
  --champion-manifest /tmp/claude-1000/cure1/g2/champ/manifest.json \
  --out /tmp/codex1-g2-controls.json
```

The default grade output is byte-identical to the published grade:
`45f5f22a1b2004886d59cc172586e0c132cae3b3e3c4c08e0d30ca742b4c90f9`.
The controls output is byte-identical to the published controls:
`72ac8ef5505a6fc3c9e127d251132a93032301ea2f5c88f21f3d217b542bdf8f`.

Reproduced grade: 160 games, 0 refusals, 82,789 own troll-turns; D-1 25 episodes in 24 games;
D-2 0; D-3 0; clause (a) 11/25 = 44.00% versus 65.00% (**FAIL**); clause (b) 4.3122 versus
3.8386 per 1,000 own troll-turns (**FAIL**); idle-with-work 0.436% (**PASS**); long-stall 0%
against champion 1.3072% (**PASS**). Branches reproduce exactly as H 253, L 245, N 39,706,
P 42,136, R 341, W 108. The independent crosswalk reproduces 18 disagreements, all 18 explained
by the Manhattan fallback and 0 unexplained.

No Arena action, TestSession, sealed-map access, source mutation, or bulk write was performed.
DEFERRED: none.
