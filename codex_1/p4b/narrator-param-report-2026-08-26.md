# P4b narrator parameter — v4 and v5 reproduced; narrator-less arms are explicit

- Task: `20260826-p4b-narrator-param`
- Charter: `local_claude_1@d6bbe3de16b4c05cb3e8353ad34144350e7f91eb`
- Builder: `codex_1`
- Scope: `codex_1/p4b/**` only; no arm, champion, resident, resolver, raw game data, or Arena state changed

## Result

`p4b_gate.py` now requires an explicit dialect per arm: `v4`, `v5`, `v6`, or `none`. The
applicable dialect imports its own fail-closed decoder; giving a v5 archive to v4 (or conversely)
is therefore a counted hard error. `none` is not a decoder alias: it scans the complete archive,
rejects any NARRATE payload, and otherwise returns `NOT_APPLICABLE` with the reason that the arm
was explicitly declared narrator-less. Comparisons involving such an arm remain
`NOT_APPLICABLE`, never `PASS`.

## Reproduction

Candidate 2's v5 rule-off and instrument panels were regenerated from the hash-pinned configs and
sources in the clean `agent/claude_1` worktree, in isolated scratch
`/tmp/codex1-p4b-v5-repro`. The evaluator used `--dialect ...=v5`; the count verifier compared
the regenerated packet with the accepted Candidate 2 artifact
`claude_1/cure2/results/c12-idle-with-work.json`.

| count | v5 instrument | v5 rule-off |
| --- | ---: | ---: |
| games / maps / unit lives | 240 / 120 / 384 | 240 / 120 / 384 |
| observable transitions | 76,364 | 76,364 |
| complete 60-turn windows | 53,708 | 53,708 |
| all-available windows | 7,137 | 8,839 |
| P4b episodes / failed units | 16 / 16 | 27 / 27 |
| blind unit lives (`NONE` in every window) | 277 | 268 |
| longest-run distribution (min/q1/median/q3/max) | 0/8/14/22/199 | 0/8/14/22/199 |

Every compared count field matches the accepted row exactly; `verify_v5_counts.py` returns zero
with `instrument: true` and `ruleoff: true`. The differential is `PASS`, with no added unit key.
Fresh gzip digests are `0f067555e52f3219c1e28ea1c3ffeed94fd7538028f47956df641fecc4b164a8`
(instrument) and `e4e7345371025791d214658be535b5c47df5e4c90c3433497f90ce7b44632aa7`
(rule-off); the complete regenerated result packet hashes
`a9303bc0eb62e911b9e1e45bae890d1026cf102af12438669f1f45376f0b0ace`.

The unchanged v4 path was also rerun on the existing Candidate 1 archives: both arms `READY`,
25 candidate versus 27 champion failed units, differential `PASS`.

Two narrator-less 240-game archives were then checked twice. Declared `none`, both return
`NOT_APPLICABLE` with zero errors and the explicit reason. Deliberately declared `v5`, both return
`GATE_UNREADY` with exactly 172,364 decoder errors, first error `no NARRATE token`; the wrong
dialect cannot become a silent zero.

## Commands

```text
python3 -m unittest codex_1/p4b/test_p4b_gate.py
python3 codex_1/p4b/reproduce_v5.py \
  --claude-root /home/tarstars/prj/troll_farm-claude_1 \
  --scratch /tmp/codex1-p4b-v5-repro
python3 codex_1/p4b/p4b_gate.py \
  --module-root /home/tarstars/prj/troll_farm-claude_1/claude_1 \
  --arm champion=/tmp/codex1-p4b-v5-repro/cure2-ruleoff-config/games/games.jsonl.gz \
  --dialect champion=v5 \
  --arm candidate=/tmp/codex1-p4b-v5-repro/cure2-instrument-config/games/games.jsonl.gz \
  --dialect candidate=v5 --base champion \
  --json /tmp/codex1-p4b-v5-repro/p4b-v5.json
python3 codex_1/p4b/verify_v5_counts.py \
  --accepted-c12 /home/tarstars/prj/troll_farm-claude_1/claude_1/cure2/results/c12-idle-with-work.json \
  --reproduced /tmp/codex1-p4b-v5-repro/p4b-v5.json
```

Ten unit tests pass. The added v6 contract fixture carries r5's required three-valued `/k=2`
unit field and proves that P4b reads the unchanged `available` and `branch` tuple positions without
depending on v6's expanded census. `git diff --check` is clean.

## v6 boundary

The `v6` import path is implemented and fail-closed. P4b deliberately delegates the complete wire
grammar and mutual version refusal to the arm's `narrate6` decoder, just as it delegates v4 and v5
to their accepted decoders. Its own dialect-neutral boundary validates that each decoded unit tuple
still contains `chosen`, `available`, `branch`, and `blocked`; the r5 fixture adds `k` as a fifth
field and decodes cleanly. A real v4 archive passed under `--dialect ...=v6` will therefore be a
counted hard error as soon as the Candidate 3 build supplies its mutually-refusing `narrate6`
module; P4b contains no fallback parser that could accept it.
