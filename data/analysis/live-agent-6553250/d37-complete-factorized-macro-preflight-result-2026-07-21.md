# D37 complete factorized macro PPO preflight — result (2026-07-21)

## Verdict

**Reject the behavior initializer before cloning or PPO.** The complete macro environment is
deterministic, active, and mechanically clean, but the frozen highest-rate/provenance heuristic
does not fund workforce growth. It beats random legal control by only **+18.313 margin**, below the
+50 preflight floor; trains worker two in **31.25%** of episodes, below 80%; and trains worker three
in **0%**, below 15%.

The failure closes D37's behavior dataset, behavior-cloning run, 600k PPO pilot, development seeds,
and confirmation seeds. No neural model or candidate was produced, and no TestSession, submission,
resident, or Arena state changed.

## What was implemented

D37 is the first project environment in which a factorized scheduler owns the complete exact
official-map trajectory rather than overriding another policy:

- explicit global `NO_TRAIN` / producer / chopper decisions;
- asynchronous persistent `BANK`, `FELL_BANK`, `HARVEST_BANK`, `RENEW`, `MINE_BANK`, and one-turn
  idle jobs for every free worker;
- deterministic acquisition, planting, banking, collision reservations, and completion boundaries;
- exact plant-creator provenance and eight warmed mechanism opponents;
- no resident, farm, D11, or other command on our side; and
- separate telescoping own-score, opponent-score, and margin rewards.

Four focused Rust tests pass. The initial implementation exposed one rich-trajectory performance
straggler because target catalogs were recomputed three times per decision. Caching the exact mask
once per boundary and sharing home-distance maps reduced the full 256-cell run to 33--34 seconds.
This was an implementation-only optimization before the final rows; action semantics and outcomes
are deterministic.

## Integrity

- Heuristic and random controls each contain the complete 16-map x two-seat x eight-opponent grid:
  256 episodes.
- Independent heuristic runs are byte-identical at
  `d44d4096c753ea91c578fd9a33110eb6fba0635a1641280f415d0a49737abef2`.
- There are zero missing/duplicate cells, wrong policy labels, empty-decision episodes, action-count
  mismatches, invalid direct commands, provenance failures, branches above three workers, margin
  identity errors, or own/opponent/margin return identity errors.
- Every action mask contains a legal one-turn idle action; state and action hashes repeat exactly.
- Four independent analyzer tests pass, including weak-workforce, provenance-corruption, and repeat
  mismatch rejection.

The remaining protocol parity/replay work was not opened because the frozen value/mechanism
preflight already failed. The failure is supported by clean execution rows rather than attributed
to an unverified learned model.

## Preflight outcome

| Measure | Heuristic | Random legal | Frozen requirement |
|---|---:|---:|---:|
| Mean own score | 70.254 | 57.707 | descriptive |
| Mean opponent score | 182.313 | 188.078 | descriptive |
| Mean margin | **-112.059** | -130.371 | heuristic advantage >=+50 |
| Paired margin advantage | **+18.313** | reference | **fail** |
| Worker two | **31.25%** | 41.41% | >=80% — **fail** |
| Worker three | **0.00%** | 0.00% | >=15% — **fail** |
| Own renewable crop | **100.00%** | 95.31% | >=60% — pass |
| Median non-idle jobs | **37** | 16 | >=4 — pass |
| Invalid commands / provenance failures | 0 / 0 | 0 / 0 | zero — pass |

The heuristic improves 143 paired cells, ties four, and loses 109. Its family margin advantage over
random is positive against Compact Gold (+43.813), adaptive Gold (+32.844), Legend Balanced
(+11.813), ScriptBoss (+54.750), and SilverBoss (+22.031), but negative against MyBot (-1.094),
native Norxondor (-6.250), and resident (-11.406). This is not a uniformly superior mechanics
teacher.

Tail behavior remains far from usable: 110/256 heuristic episodes have margin at most -100 and
negative-margin mass is 29,585. Random has 123 catastrophes and mass 33,635. The heuristic's real
but modest improvement is insufficient for behavior initialization.

## Mechanism diagnosis

### Exact resource flow

The heuristic selects 7,368 `RENEW` jobs but only 462 `HARVEST_BANK` and 40 `MINE_BANK` jobs. With
the one-capacity, one-harvest starter, `RENEW` harvests one seed and consumes that same seed when it
plants. It creates supply but deposits no training currency. The policy repeatedly requests the
producer (4,812 global decisions) and later chopper (4,586), yet does not capitalize the orchard
into the exact PLUM/LEMON/APPLE/IRON deficits.

Random control accidentally allocates much more funding work—1,381 harvest-bank and 1,282 mine-bank
jobs—and therefore trains worker two more often than the supposedly informed heuristic (41.41%
versus 31.25%). This localizes the failure to **initialization policy accounting**, not absence of
funding actions in the environment.

### Abstraction level

Persistent macro actions remove primitive waypoint noise: the heuristic executes a median 37
non-idle jobs and creates crops in every episode with no illegal command. D37 therefore does not
refute factorized macro control. It refutes a scalar rate/provenance teacher that values renewable
asset creation without conditioning job value on the current TRAIN bill.

### Learning boundary

Cloning this teacher would teach the network to spend scarce seed instead of banking it. PPO would
then start from a policy that fails the very workforce mechanism it was meant to preserve, repeating
D21's production-erosion risk. The frozen preflight correctly prevents that expensive run.

### Compute

The heuristic executes 21,861 macro decisions in 33.37 seconds and random executes 13,082 in 20.46
seconds: roughly 640--655 exact macro decisions/s including opponent computation on 24 workers.
Environment throughput is adequate for a local pilot; compute is not the rejection reason.

## Next experiment

D38 may retain the clean complete environment and action vocabulary, but it must use a fresh,
coefficient-free **TRAIN-deficit teacher** on disjoint official seeds:

1. represent the exact outstanding cost vector for the persistent TRAIN goal;
2. while unaffordable, choose `BANK` or acquisition jobs lexicographically by deposited reduction
   of that vector, then shorter completion time and stable key;
3. distinguish `HARVEST_BANK` from `RENEW`: a seed spent on planting does not count as funding, and
   RENEW becomes eligible for capitalization only after the current bill is covered or when it
   leaves a bankable surplus;
4. use `MINE_BANK` whenever IRON is the unresolved bill component;
5. after worker three or cancellation, return to the unchanged rate/provenance objective; and
6. rerun the same preregistered mechanism floors on fresh seeds before any behavior data or PPO.

This is a new initialization experiment derived from exact game accounting, not a bonus/threshold
tune on D37 outcomes. If a deficit teacher still cannot build workforce on fresh maps, the macro
action interface lacks a required funding state/action and must change before learning.

## Evidence and SHA-256

- protocol: `0844625a432dc5c6ad116f08f976d6ffb6d197ef06cde33e640698b51a211410`;
- macro environment: `003dd32092e42f6b9325601b9ec53b388438f03628b4f8f966bdfdaae40c1ffa`;
- preflight runner: `8778fc1650d12dc6b396f809dbdf798ed2186d3c48ada8597275d2f3e2ca95e2`;
- analyzer: `5f8059f4686768ae29b4dd9d2daad2cbf12547cf260d452ca54ec7631bee9500`;
- heuristic rows: `d44d4096c753ea91c578fd9a33110eb6fba0635a1641280f415d0a49737abef2`;
- random rows: `bd6889a9bf0630fa0fb96d36350a7f177c16f83d64696e0bd4ca21cf26986716`;
- result JSON: `e53fa230d7fe08dfe9dfe07212e2f2bc1767c8110d08a47093339e116b3f2fc7`.
