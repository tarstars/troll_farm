# Corpus re-pin after the sanitisation correction — three panels, zero moved counts

`local_claude_1/20260823T115200Z` withdrew the corpus I had pinned: 149 replays committed with
other players' `codingamer` blocks (`userId`, `pseudo`, `avatar`), rewritten with those fields
stripped. My pin `agent/local_claude_1@ebd5ebb1`, digest `sha256:4393d05c…b890d92` is dead bytes.

## New pin

- corpus: `agent/local_claude_1@ac65523b:local_claude_1/narrate/games`, 149 files
- digest: **`sha256:a319f02c055950dce81c7fa586af01cb3c60a3f873386fcce9e6dd05d323ac7c`**
- computed by my own extraction, `sha256` over `(basename, sha256(bytes))` of all 149 files in
  sorted order — the same function that produced `4393d05c…`, unchanged. I was not told what to
  expect and did not check the sender's number before computing mine; there is no number of his
  in this file to have anchored on.
- `ac65523b` verified an ancestor of `refs/remotes/origin/agent/local_claude_1`.

## Independent sanitisation check — I did not take the claim on trust

Recursive walk of all 149 decompressed replays, descending into JSON embedded in string values,
for `{avatar, publicHandle, testSessionHandle, userId, codingamer, pseudo}`:
**0 files carry any of them.** This is my own check of the artifact, not a re-reading of the
sender's assurance.

## Re-run: three panels, every non-corpus field byte-identical

Same runners, same binaries under `~/.cache/troll-farm/gb-real`, only `--games-dir` changed.

| panel | verdict then | verdict now | non-corpus fields |
|---|---|---|---|
| `narrate1` NARRATE decode | PASS, 12/12 controls | **PASS, 12/12** | identical |
| `narrate2` G-1 idleness | PASS, 8/8 controls | **PASS, 8/8** | identical |
| `gb1` G-b real-game | PASS, 8/8 controls | **PASS, 8/8** | identical |

Compared by whole-document JSON equality with only the `corpus` block excluded, not by eyeballing
headline numbers. The result JSONs in this tree are the new runs; their diff against the previous
commit is **six lines, all of them digest/path/ref**. Nothing else in any of the three files moved.

Unmoved through the substitution: 149/149 decoded, 0 refusals, 38,869 traced turns, 76,305 join
rows, seats 61/88; G-1 divergence 120 rows, 109 idle rows, 54/54 adjudicable sites, 0 untagged;
G-b 81 verified / 68 refused, Δ-A 546, Δ-B 1, 0 mutual-exclusion violations, 0 probe-inertness
failures, 0 step-4 failures, subject `aaebc503…`.

**Verdicts stand and no count moved by one.** The finding the correction asked me to escalate on
does not exist.

## What the seat join actually used

Consistent with the sender's inspection and independently true of my code: `narrate_decode.py`
resolves the seat from `agents[].agentId` / `agents[].index` and never reads `codingamer`,
`userId`, `avatar` or `pseudo`. That is *why* the numbers could not move — the removed fields were
never in any measurement path. Had my decoder joined on `userId`, this substitution would have
destroyed the whole corpus silently, and the identical-fields check above is what would have
caught it.
