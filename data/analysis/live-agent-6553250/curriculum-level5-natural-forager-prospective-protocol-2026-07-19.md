# Curriculum Level 5 natural-forager prospective protocol — frozen 2026-07-19

## Purpose and exact bank

Test whether the already accepted Level-4 actor robustly transfers to isolated active movement and
initial-natural-fruit competition without any new learning.  D1 development seeds 500--999 pass;
individual failures were not inspected.  The exact prospective interval is
2,019,000--2,020,999, all 2,000 seeds in order.

Before learned replay, generate and hash deterministic teacher and random-legal controls over the
complete interval.  The actor is fixed to Level-4 confirmation checkpoint SHA-256
`b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`.  No clone, PPO, model
seed, checkpoint selection, or training stream enters this protocol.

## Environment invariants

- deterministic no-growth natural-forager cascade from the frozen D1 protocol;
- opponent may only MOVE, HARVEST reset-time plants, and DROP;
- opponent never CHOPs, PLANTs, PICKs, MINEs, or TRAINs;
- unchanged eight recipes, automatic requested player-0 TRAIN, two controlled roles, reward,
  objective, 240 turns, observation/action ABI, and deterministic actor; and
- 100 vector environments and 14 unbound Torch threads on AC power.

## Control validity

Teacher control must satisfy all of:

- at least 99% overall and 98% nontrivial success;
- at least 95% in every recipe and every height;
- at least 99% crop creation and 99% renewable harvest;
- zero illegal selected teacher actions;
- exactly one opponent worker in every episode; and
- positive opponent score in at least 95% of episodes.

Random legal must remain at or below 5% overall success.  Failure of either control stops before
actor replay.

## Prospective zero-shot gate

The fixed actor must satisfy:

- at least 95% overall and 93% nontrivial success;
- at least 90% success in every recipe and 93% in every height;
- at least 97% crop creation and 97% renewable harvest;
- paired-teacher median completion delay at most 10 turns;
- exactly one opponent worker in every episode; and
- material opponent activation in at least 95% of episodes.

Passing accepts the **natural-forager interaction abstraction**, not a new checkpoint or live
candidate.  It authorizes design of the next single opponent mechanism from the accepted Level-4
base.  Failure rejects zero-shot transfer on this abstraction; no threshold, policy constant, or
checkpoint may be tuned from the prospective bank.

## Exclusions

No opponent planting/training, created-crop interaction, autonomous recipe selection, third own
worker, self-play, opponent mixture, deployment work, field promotion, or Arena write is allowed.
