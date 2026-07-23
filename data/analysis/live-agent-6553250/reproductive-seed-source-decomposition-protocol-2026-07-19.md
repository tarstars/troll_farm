# Reproductive seed-source decomposition — protocol, 2026-07-19

## Question

Why does adaptive Gold plant 29.45 more trees per game against the productive farm than against
the resident? In particular, does resident denial suppress the rival **upstream**, by removing
natural fruit before it can seed the first crop generation, or only downstream by contesting
already planted crops?

## Fixed diagnostic

Reuse the consumed seeds 0--29, both seats, and the exact resident/farm versus adaptive-Gold
profiles from the supply-ownership study. This opens no fresh outcome data and cannot qualify a
candidate.

Extend the existing provenance ledger without changing either command stream. For every
successful harvest, record collector, tree origin (`natural`, ours, opponent, unknown), fruit
kind, amount, and whether the action occurs through turn 100. Also record successful plants
through turn 100. Preserve the existing wood/provenance and complete-game fields.

Require the common 120-row grid, all games complete, at least 99% assigned harvested fruit, at
least 95% assigned wood, and exact reproduction of the preceding score/margin/wood aggregates.

## Frozen classification

An upstream natural-seed mechanism is material if farm versus resident gives adaptive Gold at
least 60 additional natural fruits through turn 100 (one per game) and at least 60 additional
successful plants through turn 100. Report kind composition without selecting a kind threshold.

Separately report crop-origin fruit after the launch window. If opponent-self-crop fruit is the
dominant added source, interpret natural fruit as bootstrap and self-crop fruit as the
compounding cascade. If early natural-fruit uplift is below the floor, close pre-fruit natural
denial and move directly to a new whole-policy scheduler.

## Decision boundary

A material upstream result authorizes only a fresh, coefficient-free causal experiment that
interrupts a seed source before the rival's first harvest while preserving private production.
It does not authorize the previously rejected unconditional crop bonus, selected-verb transplant,
confirmation data, platform games, or submission.
