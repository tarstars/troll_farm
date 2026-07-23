# D88b yaichi task-state archaeology — frozen repair (2026-07-21)

D88b inherits the evidence boundary, 16-game held-out validation set, exact lineage accounting,
integrity thresholds, mechanism-transfer gates, and decision rule from the D88a protocol. It is
frozen after D88a discovery and before any validation message stream is parsed.

The only changes are those uniquely identified by the D88a discovery audit:

1. normalize prefix `GET_SEED_TREE` as `GET_SEED_TREE` and prefix `ATTACK` as `ATTACK`;
2. allow `MOVE` or `WAIT` for each of those persistent travel intents (discovery observed only
   `MOVE`; `WAIT` is retained consistently with every other travel state);
3. treat normalized `PLANT` as the persistent farm task and allow issued `PICK`, `HARVEST`, or
   `PLANT`; and
4. retain the original `PICK_SHACK` and `HARVEST` states as their narrower standalone tasks.

No other state alias or command is allowed. `GET_SEED_TREE` and `ATTACK` target coordinates are
reported descriptively and cannot become a post-validation threshold. The same coverage gates now
apply to this corrected 13-state vocabulary.

Before validation, rerun all 19 discovery games once with one process and once with 20 processes.
Require byte-identical canonical rows, all D88a integrity gates, and no state/command mismatch.
Only then open the fixed validation IDs. Run validation once with one process and once with 20;
require byte-identical canonical rows before behavioral interpretation.

The unchanged held-out mechanism gates are:

- bank bootstrap before own-crop maintenance in at least 10/12 renewable games;
- at least 80% of starter plants sourced from bank or own-crop tokens;
- at least 80% of own-crop harvested tokens replanted by the same worker;
- at least 95% of trained-worker productive actions CHOP or DROP, with trained HARVEST/PLANT in at
  most one renewable game;
- the complete ordered four-phase lifecycle in at least 10/12 renewable games; and
- the same qualitative directions in consumed current renewable games.

All passing gates authorize only a written controller blueprint and a separately frozen D89 local
research implementation. They do not authorize platform writes or a submission.
