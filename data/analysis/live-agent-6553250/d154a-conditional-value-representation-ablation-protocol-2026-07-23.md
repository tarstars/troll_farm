# D154a conditional-value representation ablation — frozen protocol

Date: 2026-07-23  
Status: frozen after D153b closed scalar confidence, before any D154 fit

## Hypothesis

The 379 action features contain 64 expert-identity indicators and 270 redundant context × semantic
products. D153's 16 hidden units may spend capacity on discovery-fold expert identities instead of
the 45 deployable action semantics. Test representation, not more capacity or new data.

Retain D153's exact 909 groups/16,228 values, grouped soft-ranking plus Smooth-L1 objective, width
16, 80 epochs, batch 64, optimizer, seeds `15301--15304`, eight outer folds, and exact slot-zero
anchoring. Compare these frozen inputs (action slices use Python half-open indexing):

| Name | Input | Width | Parameters |
|---|---|---:|---:|
| `full443` | state 64 + action `[0:379]` | 443 | 7,121 |
| `no_expert_ids379` | state 64 + action `[0:45]` + `[109:379]` | 379 | 6,097 |
| `semantic_context115` | state 64 + action `[0:45]` + direct context `[109,154,199,244,289,334]` | 115 | 1,873 |
| `semantic109` | state 64 + action `[0:45]` | 109 | 1,777 |
| `semantic_supporters173` | state 64 + action `[0:109]` | 173 | 2,801 |
| `action_semantic_context51` | action `[0:45]` + direct context indices only | 51 | 849 |

The six direct-context positions are valid because noncontrol semantic feature zero is one, so the
first product in each 45-wide context block recovers raw context; slot zero remains all zeros.

Use ten fork workers × two PyTorch threads and run the complete 192-fit selection twice. Require
each `full443` seed to reproduce D153a held counts, exact A/B held counts for every
representation/seed, and record any harmless threaded model-hash drift.

## Frozen readout

Apply all original D153 held gates to each representation/seed: +5 mean value, at least 30%
strict positive and at most 15% harmful, at least 15% oracle capture, regret at most 26, at least
20% within ten, every fold nonnegative, six positive families with floor -2, sign balanced accuracy
60%, crop safety, and workforce safety.

This is a multiple-representation discovery audit. Even an eligible cell cannot become a
checkpoint or submission; it opens a separately frozen confirmation on fresh nonreserved maps.
If no cell is eligible, close these fixed semantic slices and move to an explicitly factorized or
recurrent representation rather than widening the same MLP.

## Boundary

D154a cannot read/generate reserved maps `9,844,200--9,844,215`, collect new maps, use YT, integrate
Rust, save a deployable checkpoint, qualify or submit a candidate, change the resident, or interact
with Arena.
