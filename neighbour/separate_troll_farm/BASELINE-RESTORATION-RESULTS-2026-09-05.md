# V439 directly beats the deployed V543 in the prospective restoration screen

Decision: publish one exact V439 ladder evaluation under
`BASELINE-RESTORATION-PROTOCOL-2026-09-05.md`. This restores a supported stronger baseline;
it does not establish seventh-place strength. The experimental scarce-denial controller and
the separate TRAIN timing correction are **not** in this submission.

## Development triage

Seven requests: exact V439 control repeat followed by V543 on six reused confirmation blocks.
The repeat matches the archived V439 run, including both command streams and scores. Across
the six paired blocks V439 is 1 W / 0 D / 5 L, V543 0 / 0 / 6. Mean own/opponent scores are
199.17/223.83 versus 106.67/267.50; mean margins -24.67 versus -160.83. V439 loses no match
point, improves margin on five blocks and gains one point, satisfying the advance condition.
The reused maps are development evidence, not independent confirmation.

## Prospective confirmation

The twelve requests, six new seeds and exact opponent identities were frozen before playing
in `stage-b-plan.json`. Identities/ranks came from an authenticated board read. Each pair uses
the same normalized initial input and physical seat; candidate scores below are listed first.

| Opponent (frozen rank) | Seed / seat | V439 score | V543 score |
|---|---|---|---|
| putibuzu (7) | 2609055701 / 0 | 159–98 W | 214–208 W |
| tonigineer (8) | 2609055801 / 1 | 224–280 L | 218–304 L |
| a76a44 (20) | 2609055201 / 0 | 220–278 L | 402–504 L |
| GoodDevel (40) | 2609055401 / 1 | 164–144 W | 192–256 L |
| PonyPonyCodeCode (60) | 2609055601 / 0 | 184–116 W | 39–331 L |
| putibuzu (7) | 2609055702 / 1 | 252–223 W | 315–289 W |

V439 finishes **4 W / 0 D / 2 L (4 points)** versus V543 **2 / 0 / 4 (2 points)**.
It adds two wins without losing either V543 target-rank win, and has no point regression.
Both seats are 2/3 for V439 and 1/3 for V543. Mean scores are 200.50/189.83 versus
230.00/315.33; mean margins +10.67 versus -85.33. V543 scores more and collects more wood
(48.50 versus 44.67), illustrating why own score alone selected the wrong live baseline.
Paired mean margin gain is +96, median +49.5; every observed margin improves.

The empirical six-block bootstrap (46,656 resamples) gives mean margin gain [27.50, 205.67]
and mean point gain [0, 0.667] at the 2.5/97.5 percentiles. Six fixed-opponent blocks cannot
establish coverage over unseen strategies, a calibrated ladder rating, or top-seven strength.
The test has only three target-rank games per policy. Do not reinterpret a small passing
restoration screen as evidence that the overall goal is finished.

All nineteen requests completed; no retry or deployment failure. There are 2,096 exact audited
new turns in Stage A and 3,449 in Stage B, with 70/120 startup-repeat executions. The additional
V439 packaging check compares freshly compiled readable and compact executables with the six
official streams (1,649 turns each, 120 combined startups), with zero mismatches. Maximum local
startup/first-turn/exit time was 23.3 ms; that is not a simulation of platform startup.

## Exact publication and preservation

The single publication was accepted at 2026-09-05 08:01:23 UTC:

- Submission **41245746**, agent **6704418**, verified together in platform game records.
- Exact compact V439 SHA-256 `7f61a6cd510a70e9389e794571512e2c5d0afb33bab957c70791c2c16fbff0bc`,
  96,985 bytes / UTF-16 units; `submission.rs` now matches it exactly.
- Readable `bot.rs` SHA-256 `44e3dacaee3a57cb5b861fd594664ff087c418c8b1a541698aba53ae70c39740`.
- Replaced V543 submission 41242929 / agent 6701731, last mature rank 155 at rating 13.92.
  Original readable/compact files are preserved under `packaging/previous-v543-*`.

`publish_baseline_restoration.py` checks the completed prospective decision, exact artifact and
packaging evidence, and the old exact agent's maturity. It journals before submission and refuses
a second attempt; eleven tests cover its evidence gate. The terminal response records exactly
one submission call. `monitor_platform_agent.py` tracks the new exact identities through maturity
and five-minute confirmation; early readings are provisional, even if `inProgress` is false.
After installing the exact artifacts, the final project suite passes **467 tests in 155.57 seconds**.

Evidence root: `/data/separate_troll_farm-working/baseline-restoration/2026-09-05/`.
It contains frozen plans, raw replies/replays, source snapshots, both analyses, independently
compiled packaging artifacts, deployment journal/result, and monitor readings. No neighbor
files were changed. The mature outcome is now recorded in
`V439-RESTORATION-MATURE-2026-09-05.md`: confirmed rank 28, rating 23.43, 95/0/65 over all 160
games with no deployment failures. This improves the deployed baseline but misses seventh place.
