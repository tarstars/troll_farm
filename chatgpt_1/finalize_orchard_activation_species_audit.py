#!/usr/bin/env python3
"""Correct the paired bootstrap and publish the final orchard interpretation."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "chatgpt_1/orchard-activation-species-audit-2026-08-04.json"
MD_PATH = ROOT / "chatgpt_1/orchard-activation-species-audit-2026-08-04.md"
ANALYZER = ROOT / "chatgpt_1/orchard_activation_species_audit.py"


def mean(values):
    values = list(values)
    return sum(values) / len(values) if values else None


def exact_bootstrap(deltas: list[float]) -> dict:
    draws = sorted(mean(sample) for sample in itertools.product(deltas, repeat=len(deltas)))
    n = len(draws)
    return {
        "method": f"exhaustive ordinary paired bootstrap: {len(deltas)}^{len(deltas)} resamples",
        "pairs": len(deltas),
        "resamples": n,
        "mean": mean(deltas),
        "median": sorted(deltas)[len(deltas) // 2 - 1 : len(deltas) // 2 + 1],
        "lower_95": draws[int(0.025 * n)],
        "upper_95": draws[min(n - 1, int(0.975 * n))],
        "probability_le_zero": sum(value <= 0 for value in draws) / n,
    }


def patch_analyzer() -> None:
    source = ANALYZER.read_text(encoding="utf-8")
    start = source.index("def paired_bootstrap(")
    end = source.index("\ndef build_sources(", start)
    replacement = '''def paired_bootstrap(deltas: list[float], repetitions: int = 100_000) -> dict[str, Any] | None:
    if not deltas:
        return None
    import itertools
    n = len(deltas)
    if n <= 8:
        draws = sorted(mean(sample) for sample in itertools.product(deltas, repeat=n))
        method = f"exhaustive ordinary bootstrap: {n}^{n} resamples"
    else:
        import random
        rng = random.Random(0x6A09E667)
        draws = sorted(
            sum(deltas[rng.randrange(n)] for _ in range(n)) / n
            for _ in range(repetitions)
        )
        method = f"deterministic ordinary bootstrap: {repetitions} resamples"
    return {
        "method": method,
        "pairs": n,
        "resamples": len(draws),
        "mean": mean(deltas),
        "median": median(deltas),
        "lower_95": draws[int(0.025 * len(draws))],
        "upper_95": draws[min(len(draws) - 1, int(0.975 * len(draws)))],
        "probability_le_zero": sum(value <= 0 for value in draws) / len(draws),
    }

'''
    ANALYZER.write_text(source[:start] + replacement + source[end + 1 :], encoding="utf-8")


def render(report: dict) -> str:
    arena = report["arena_ab"]
    actual = report["actual_apple"]
    species = report["species"]
    quality = report["quality"]
    bootstrap = arena["paired_score_bootstrap"]
    return f'''# Secure orchard activation and species audit

Task: `20260804-orchard-activation-species-audit`  
Data: eight exact one-hour Arena legs, **1,280 games**  
Platform mutation: none

## Final verdict

**Keep the current APPLE secure orchard and its present activation rule.** The completed replay
audit rejects all three simple replacements considered here:

- idle-only activation is effectively orchard deletion;
- enemy-arrival-before-first-bank is the wrong safety criterion because it ignores APPLE health;
- a like-for-like BANANA mother has the same support but roughly half the fruit throughput and far
  less survival margin.

The remaining plausible activation improvement is not another distance threshold. It is a
**prospective opportunity-cost gate** comparing the orchard's guaranteed remaining fruit value to
the value of the starter task that would be displaced. That value is not available in replay
output, so it needs source instrumentation and a fresh closed-loop experiment.

## Repeated live result

| Variant | Legs | Games | Mean Arena score | Wins | Catastrophes | Mean game margin |
|---|---:|---:|---:|---:|---:|---:|
| no orchard | 4 | 640 | {arena['no-orchard']['mean_arena_score']:.3f} | {arena['no-orchard']['wins']} | {arena['no-orchard']['catastrophes']} | {arena['no-orchard']['mean_margin']:.3f} |
| current APPLE orchard | 4 | 640 | {arena['orchard']['mean_arena_score']:.3f} | {arena['orchard']['wins']} | {arena['orchard']['catastrophes']} | {arena['orchard']['mean_margin']:.3f} |

Adjacent orchard-minus-no-orchard score deltas were
`{arena['paired_score_deltas']}`: mean **{arena['paired_score_mean']:+.3f}**. The corrected
exhaustive paired bootstrap interval is **[{bootstrap['lower_95']:+.3f},
{bootstrap['upper_95']:+.3f}]**, with bootstrap probability of a nonpositive mean
**{bootstrap['probability_le_zero']:.3f}**. Four unpaired opponent queues are not enough for a
causal rating estimate.

The stable qualitative pattern is polarization: orchard produced **38 more wins** but also **22
more catastrophic losses** over 640 games. It increased wins in every adjacent pair and
catastrophes in every adjacent pair.

## What happens when the orchard activates

The current orchard activated in **{actual['activated']}/{actual['orchard_games']} games
({actual['activation_rate']:.2%})**. Of those activations:

- underlying starter command: `{actual['base_command_verbs']}`;
- mother successfully planted: **{actual['mother_planted']}**;
- games banking orchard fruit: **{actual['games_with_banked_fruit']}**;
- total APPLE banked: **{actual['total_banked_fruit']}**;
- median APPLE banked per activated game: **{actual['banked_fruit_median']:.0f}**;
- median activation-to-first-bank delay: **{actual['first_bank_delay_median']:.0f} turns**;
- mother alive at game end: **{actual['mother_survived']}**.

This is not a marginal one-seed trick. It is a rare, high-output policy that reserves one of the
two workers and then converts a protected mother into roughly a hundred fruit in a successful
game.

## Activation conditions tested

### Idle-only / work-conserving

Only **{actual['work_conserving_kept']}/{actual['activated']}** actual activations had an inner
`WAIT`; **{actual['work_conserving_blocked']}** would be blocked. On the 640 no-orchard trajectories,
the exact idle-only source activated **{species['apple_idle']['activations']} times**. Thus the
existing `work_conserving()` constructor is, in the current field, essentially another no-orchard
ablation. Since blanket orchard removal lost live rating, this is not the next candidate.

### Enemy arrival versus first bank

A travel-only rule would keep {actual['payback_safe_kept']} activations and block
{actual['payback_safe_blocked']}. The supposedly unsafe group actually had the better descriptive
outcomes: mean margin **{actual['payback_safe_blocked_outcomes']['mean_margin']:+.1f}** and win rate
**{actual['payback_safe_blocked_outcomes']['win_rate']:.1%}**, versus
**{actual['payback_safe_kept_outcomes']['mean_margin']:+.1f}** and
**{actual['payback_safe_kept_outcomes']['win_rate']:.1%}** for the kept group. This is not a causal
comparison, but it decisively shows that enemy arrival is not a sound mechanical veto.

### Time to kill the mother

The conservative continuous-attack simulation includes enemy movement speed, chop power, tree
growth during attack, action order, and the fact that HARVEST resolves before CHOP. **All
{actual['kill_safe_kept']} actual APPLE activations survived mechanically through the first
harvest; zero failed this test.** Kill safety validates the current APPLE geometry but cannot
select a better subset.

## Why APPLE, not BANANA?

The protected tree is never ordinarily chopped by our bot: the starter repeatedly
`HARVEST -> DROP -> WAIT`, and other workers are kept off the mother. Therefore “hard to chop” is
a defensive advantage.

On the mandatory water-adjacent mother cell:

| Property | APPLE | BANANA |
|---|---:|---:|
| effective growth cooldown | 2 | 4 |
| first bank after activation | travel + 11 | travel + 19 |
| mature health | 20 | 6 |
| steady bank interval | 2 turns | 4 turns |

On the 640 no-orchard trajectories, APPLE and BANANA had exactly the same 46 activation states;
both seeds were already available in all 46. So BANANA did not unlock extra support. Where both
could activate, uninterrupted projected output averaged **{species['both_species_projected']['mean_apple_banked_fruit_ceiling']:.2f}
APPLE** versus **{species['both_species_projected']['mean_banana_banked_fruit_ceiling']:.2f}
BANANA**, a difference of **{species['both_species_projected']['mean_apple_minus_banana_ceiling']:.2f}
fruit**.

With the current minimum enemy travel ETA of 9, a chop-2 opponent attacking continuously can kill
a water BANANA around 12 turns after activation, before its first harvest around turn 18. The
same attack kills APPLE only around turn 19, after APPLE's first harvest around turn 10 and several
subsequent fruit opportunities. The species choice and the safety threshold are coupled.

## What about a self-sustained BANANA wood orchard?

That is a valid **different hypothesis**. A BANANA mother could generate seeds for a separate
near-tent cut plot, where a trained chopper repeatedly plants and fells small BANANA trees for
wood. Easy chopping is useful there. It is not a like-for-like replacement for the protected
harvest mother.

The repository's earlier banana-factory work found large production potential, but also increased
opponent production; the two live banana implementations were implementation-invalid because of
unbounded geography, banking failure, and period-2 movement. A scientifically clean successor
would therefore use:

1. one protected mother, preferably diagonal to the tent;
2. at most one orthogonal cut/replant slot at first;
3. explicit seed banking and chopper ownership;
4. monotone bank commitments and zero period-2 movement;
5. exact preservation of parent commands outside activation;
6. a fresh closed-loop value panel before any Arena submission.

This BANANA printer deserves a separate experiment. The present audit rejects only replacing the
APPLE mother with BANANA while keeping the same harvest-only lifecycle.

## Next experiment

Freeze a three-arm local/common-seed panel:

- `C0`: current APPLE orchard;
- `C1`: current APPLE orchard plus a mechanics-derived opportunity-cost gate;
- `C2`: bounded BANANA mother + one cut slot, as a separate architecture.

For `C1`, expose the inner starter's selected task class, predicted cycle ETA, and expected banked
score before the orchard wrapper overrides it. Activate only when projected remaining APPLE value
minus the seed exceeds the displaced task's projected remaining value by a frozen margin. Do not
fit that margin on these 1,280 outcomes.

For `C2`, the prerequisite gates are mother survival, cut-slot completion, banked wood, no lost
seed, no opponent-favored crop leakage, and no movement oscillation. Compare it against `C0`, not
against no-orchard alone.

## Data quality and limits

- all eight LFS packages hash-verified;
- full deployed command parity: **{quality['deployed_command_parity_games']}/1280**;
- exact deployed prefix through the turn-100 activation window:
  **{quality['deployed_prefix_exact_through_turn_100_games']}/1280**;
- generated alternatives interpreted only before their first divergence;
- exact matches on initial state + opponent submission + seat: **0**, so no game-level causal pair
  estimate is claimed;
- raw replay bodies were not duplicated.

Artifacts:

- `chatgpt_1/orchard-activation-opportunities-2026-08-04.csv`;
- `chatgpt_1/orchard-activation-species-audit-2026-08-04.json`;
- `chatgpt_1/orchard_activation_species_audit.py`;
- `chatgpt_1/patch_orchard_activation_species_audit.py`.
'''


def main() -> None:
    report = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    deltas = [float(value) for value in report["arena_ab"]["paired_score_deltas"]]
    report["arena_ab"]["paired_score_bootstrap"] = exact_bootstrap(deltas)
    report["verdict"] = (
        "KEEP_CURRENT_APPLE_ORCHARD; IDLE_ONLY_REJECTED_AS_EFFECTIVE_DELETION; "
        "TRAVEL_ONLY_SAFETY_REJECTED; KILL_SAFETY_NONDISCRIMINATING; "
        "BANANA_MOTHER_SWAP_REJECTED; OPPORTUNITY_COST_GATE_AND_BOUNDED_BANANA_PRINTER_REMAIN"
    )
    report["recommendation"] = (
        "Keep the current APPLE orchard. The next activation candidate must compare projected "
        "orchard value with the displaced starter task; do not use idle-only or enemy-arrival "
        "thresholds. Treat a self-sustained BANANA wood printer as a separate bounded architecture."
    )
    report["audit_correction"] = {
        "reason": (
            "The first paired-bootstrap implementation used low LCG bits modulo four; each four-draw "
            "sample contained every pair once and produced a degenerate interval. Replaced by exact "
            "enumeration of all 4^4 ordinary bootstrap resamples."
        ),
        "activation_interpretation": (
            "Idle-only keeps 3/54 actual activations and 0/640 no-orchard opportunities; all 54 "
            "APPLE activations pass adversarial first-harvest kill safety."
        ),
    }
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render(report), encoding="utf-8")
    patch_analyzer()
    digest = hashlib.sha256(JSON_PATH.read_bytes()).hexdigest()
    print(json.dumps({"json_sha256": digest, "verdict": report["verdict"]}, indent=2))


if __name__ == "__main__":
    main()
