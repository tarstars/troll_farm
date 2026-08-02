#!/usr/bin/env python3
from __future__ import annotations
import argparse
import csv
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
from typing import Iterable
RESIDENT = 'resident'
B100 = 'opponent_crop_b100_e6'
FACTORY = 'banana_seed_factory'
CANDIDATE = 'banana_factory_opponent_crop_b100_e6'
PROFILES = (RESIDENT, B100, FACTORY, CANDIDATE)
FRUITS = ('plum', 'lemon', 'apple', 'banana')
OPPONENTS = ('compact_gold', 'gold_adaptive', 'gold_elite', 'mybot', 'printer_bot', 'sched_bot', 'script_boss', 'silver_boss')

class AnalysisError(RuntimeError):
    pass

def read_tsv(path: Path) -> list[dict]:
    with path.open(newline='') as handle:
        rows = list(csv.DictReader(handle, delimiter='\t'))
    for row in rows:
        for key, value in list(row.items()):
            if key in {'opponent', 'profile'}:
                continue
            if value is None or value == '':
                raise AnalysisError(f'empty numeric field {key!r} in {path}')
            row[key] = int(value)
    return rows

def margin(row: dict) -> int:
    return row['own_score'] - row['opponent_score']

def own_crop_harvest(row: dict) -> int:
    return sum((row[f'own_fruit_from_ours_{kind}'] for kind in FRUITS))

def opponent_created_fruit(row: dict) -> int:
    return sum((row[f'opponent_fruit_from_opponent_{kind}'] for kind in FRUITS))

def opponent_created_wood(row: dict) -> int:
    return row['opponent_from_opponent']

def lower_quantile(values: Iterable[float], probability: float) -> float:
    selected = sorted(values)
    if not selected:
        raise AnalysisError('quantile of empty collection')
    return selected[math.floor(probability * (len(selected) - 1))]

def mean(values: Iterable[float]) -> float:
    selected = list(values)
    if not selected:
        raise AnalysisError('mean of empty collection')
    return statistics.mean(selected)

def cluster_bootstrap_ci(values_by_seed: dict[int, list[float]], *, samples: int=20000, rng_seed: int=20260802) -> list[float]:
    seeds = sorted(values_by_seed)
    if not seeds:
        raise AnalysisError('bootstrap has no clusters')
    cluster_means = [statistics.mean(values_by_seed[seed]) for seed in seeds]
    rng = random.Random(rng_seed)
    draws = []
    for _ in range(samples):
        draws.append(statistics.mean((rng.choice(cluster_means) for _ in seeds)))
    draws.sort()
    return [draws[int(0.025 * (samples - 1))], draws[int(0.975 * (samples - 1))]]

def index_cells(rows: list[dict]) -> tuple[dict[tuple, dict[str, dict]], list[dict]]:
    grouped: dict[tuple, dict[str, dict]] = defaultdict(dict)
    failures: list[dict] = []
    for row in rows:
        key = (row['seed'], row['seat'], row['opponent'])
        profile = row['profile']
        if profile in grouped[key]:
            failures.append({'kind': 'duplicate', 'key': key, 'profile': profile})
        grouped[key][profile] = row
    for key, profiles in sorted(grouped.items()):
        if set(profiles) != set(PROFILES):
            failures.append({'kind': 'incomplete', 'key': key, 'profiles': sorted(profiles)})
    return (grouped, failures)

def paired_values(cells: dict[tuple, dict[str, dict]], left: str, right: str, field, *, keys: set[tuple] | None=None) -> list[float]:
    selected = []
    for key, profiles in cells.items():
        if keys is not None and key not in keys:
            continue
        if set(profiles) != set(PROFILES):
            continue
        selected.append(field(profiles[left]) - field(profiles[right]))
    return selected

def contrast_summary(cells: dict[tuple, dict[str, dict]], left: str, right: str, *, keys: set[tuple] | None=None) -> dict:
    valid_keys = [key for key, profiles in cells.items() if set(profiles) == set(PROFILES) and (keys is None or key in keys)]
    margin_delta = [margin(cells[key][left]) - margin(cells[key][right]) for key in valid_keys]
    own_delta = [cells[key][left]['own_score'] - cells[key][right]['own_score'] for key in valid_keys]
    opponent_delta = [cells[key][left]['opponent_score'] - cells[key][right]['opponent_score'] for key in valid_keys]
    wood_delta = [cells[key][left]['own_inventory_wood'] - cells[key][right]['own_inventory_wood'] for key in valid_keys]
    crop_harvest_delta = [own_crop_harvest(cells[key][left]) - own_crop_harvest(cells[key][right]) for key in valid_keys]
    opponent_created_fruit_delta = [opponent_created_fruit(cells[key][left]) - opponent_created_fruit(cells[key][right]) for key in valid_keys]
    opponent_created_wood_delta = [opponent_created_wood(cells[key][left]) - opponent_created_wood(cells[key][right]) for key in valid_keys]
    by_seed_margin: dict[int, list[float]] = defaultdict(list)
    by_seed_opp_fruit: dict[int, list[float]] = defaultdict(list)
    by_seed_opp_wood: dict[int, list[float]] = defaultdict(list)
    for key, value, fruit_value, wood_value in zip(valid_keys, margin_delta, opponent_created_fruit_delta, opponent_created_wood_delta):
        by_seed_margin[key[0]].append(value)
        by_seed_opp_fruit[key[0]].append(fruit_value)
        by_seed_opp_wood[key[0]].append(wood_value)
    return {'left': left, 'right': right, 'n': len(valid_keys), 'mean_margin_delta': mean(margin_delta), 'mean_own_score_delta': mean(own_delta), 'mean_opponent_score_delta': mean(opponent_delta), 'mean_wood_delta': mean(wood_delta), 'mean_own_crop_harvest_delta': mean(crop_harvest_delta), 'mean_opponent_created_fruit_delta': mean(opponent_created_fruit_delta), 'mean_opponent_created_wood_delta': mean(opponent_created_wood_delta), 'improved': sum((value > 0 for value in margin_delta)), 'tied': sum((value == 0 for value in margin_delta)), 'regressed': sum((value < 0 for value in margin_delta)), 'p10_margin_delta': lower_quantile(margin_delta, 0.1), 'minimum_margin_delta': min(margin_delta), 'maximum_margin_delta': max(margin_delta), 'map_cluster_bootstrap_margin_ci95': cluster_bootstrap_ci(by_seed_margin), 'map_cluster_bootstrap_opponent_created_fruit_ci95': cluster_bootstrap_ci(by_seed_opp_fruit), 'map_cluster_bootstrap_opponent_created_wood_ci95': cluster_bootstrap_ci(by_seed_opp_wood), '_margin_delta': margin_delta, '_keys': valid_keys}

def negative_margin_mass(cells: dict[tuple, dict[str, dict]], profile: str, keys: set[tuple]) -> int:
    return sum((-margin(cells[key][profile]) for key in keys if margin(cells[key][profile]) < 0))

def analyze(input_a: Path, input_b: Path, *, expected_maps: int, phase: str) -> dict:
    content_a = input_a.read_bytes()
    content_b = input_b.read_bytes()
    rows = read_tsv(input_a)
    cells, pairing_failures = index_cells(rows)
    expected_cells = expected_maps * 2 * len(OPPONENTS)
    expected_rows = expected_cells * len(PROFILES)
    complete_keys = {key for key, profiles in cells.items() if set(profiles) == set(PROFILES)}
    candidate_rows = [row for row in rows if row['profile'] == CANDIDATE]
    factory_rows = [row for row in rows if row['profile'] == FACTORY]
    total_wood = sum((row['total_chop_wood'] for row in rows))
    assigned_wood = sum((row['assigned_chop_wood'] for row in rows))
    total_fruit = sum((row['total_harvested_fruit'] for row in rows))
    assigned_fruit = sum((row['assigned_harvested_fruit'] for row in rows))
    wood_rate = assigned_wood / total_wood if total_wood else 1.0
    fruit_rate = assigned_fruit / total_fruit if total_fruit else 1.0
    active_keys = {key for key in complete_keys if cells[key][CANDIDATE]['banana_factory_active'] == 1}
    bootstrap_keys = {key for key in active_keys if cells[key][CANDIDATE]['banana_factory_bootstrap_successes'] >= 3}
    sustained_keys = {key for key in active_keys if cells[key][CANDIDATE]['banana_factory_harvest_successes'] > 0 and cells[key][CANDIDATE]['banana_factory_renewable_plant_successes'] > 0}
    opponent_seen_keys = {key for key in complete_keys if cells[key][CANDIDATE]['banana_factory_opponent_crop_policy_selections'] > 0 or cells[key][CANDIDATE]['banana_factory_trained_opponent_crop_selections'] > 0 or cells[key][CANDIDATE]['opponent_crops_seen'] > 0}
    opponent_selected_keys = {key for key in complete_keys if cells[key][CANDIDATE]['banana_factory_opponent_crop_policy_selections'] + cells[key][CANDIDATE]['banana_factory_trained_opponent_crop_selections'] > 0}
    inactive_exact = True
    for key in complete_keys - active_keys:
        left = cells[key][CANDIDATE]
        right = cells[key][B100]
        for field in ('own_score', 'opponent_score', 'workers', 'terminal_turn', 'action_hash', 'terminal_state_hash'):
            if left[field] != right[field]:
                inactive_exact = False
    integrity_gates = {'repeat_byte_identical': content_a == content_b, 'row_count_exact': len(rows) == expected_rows, 'cell_count_exact': len(complete_keys) == expected_cells and (not pairing_failures), 'profile_set_exact': set((row['profile'] for row in rows)) == set(PROFILES), 'opponent_set_exact': set((row['opponent'] for row in rows)) == set(OPPONENTS), 'games_complete_or_stalled': all((row['terminal_turn'] > 1 for row in rows)), 'assigned_wood_at_least_0_95': wood_rate >= 0.95, 'assigned_fruit_at_least_0_95': fruit_rate >= 0.95, 'factory_prefix_exact_to_resident': all((row['banana_factory_preactivation_mismatches'] == 0 for row in factory_rows)), 'candidate_prefix_exact_to_b100': all((row['banana_factory_preactivation_mismatches'] == 0 for row in candidate_rows)), 'inactive_candidate_exact_to_b100': inactive_exact, 'worker_count_exact_candidate_vs_b100': all((cells[key][CANDIDATE]['workers'] == cells[key][B100]['workers'] for key in complete_keys)), 'bootstrap_counters_bounded': all((row['banana_factory_bootstrap_successes'] <= row['banana_factory_bootstrap_attempts'] and row['banana_factory_bootstrap_successes'] <= row['banana_factory_initial_budget'] for row in candidate_rows)), 'harvest_counters_bounded': all((row['banana_factory_harvest_successes'] <= row['banana_factory_harvest_selections'] for row in candidate_rows)), 'renewable_counters_bounded': all((row['banana_factory_renewable_plant_successes'] <= row['banana_factory_renewable_plant_attempts'] for row in candidate_rows)), 'zero_trained_forbidden_commands': all((row['banana_factory_trained_forbidden_commands'] == 0 for row in candidate_rows)), 'zero_worker_three_bridge_activity': all((row['banana_factory_worker_three_bridge_funding_turns'] == 0 and row['banana_factory_worker_three_bridge_train_attempts'] == 0 and (row['banana_factory_worker_three_bridge_train_successes'] == 0) for row in candidate_rows)), 'zero_unclassified_divergence': all((row.get('banana_factory_unclassified_divergences', 0) == 0 for row in candidate_rows))}
    mechanism_gates = {'active_tasks_at_least_62_5_percent': len(active_keys) >= math.ceil(0.625 * expected_cells), 'both_seats_active': {key[1] for key in active_keys} == {0, 1}, 'all_eight_opponents_active': {key[2] for key in active_keys} == set(OPPONENTS), 'bootstrap_3plus_rate_at_least_0_75': bool(active_keys) and len(bootstrap_keys) / len(active_keys) >= 0.75, 'sustained_tasks_at_least_25_percent': len(sustained_keys) >= math.ceil(0.25 * expected_cells), 'opponent_crop_seen_support': len(opponent_seen_keys) >= math.ceil(0.0625 * expected_cells), 'opponent_crop_selected_support': len(opponent_selected_keys) >= math.ceil(0.03125 * expected_cells)}
    result = {'schema': 'troll-farm-banana-factory-b100-restoration-analysis-v1', 'phase': phase, 'inputs': {'a': str(input_a), 'a_sha256': hashlib.sha256(content_a).hexdigest(), 'b': str(input_b), 'b_sha256': hashlib.sha256(content_b).hexdigest()}, 'expected': {'maps': expected_maps, 'cells': expected_cells, 'rows': expected_rows}, 'observed': {'rows': len(rows), 'complete_cells': len(complete_keys), 'active_cells': len(active_keys), 'bootstrap_3plus_cells': len(bootstrap_keys), 'sustained_cells': len(sustained_keys), 'opponent_crop_seen_cells': len(opponent_seen_keys), 'opponent_crop_selected_cells': len(opponent_selected_keys), 'assigned_wood_rate': wood_rate, 'assigned_fruit_rate': fruit_rate}, 'pairing_failures': pairing_failures, 'integrity_gates': integrity_gates, 'mechanism_gates': mechanism_gates}
    if not all(integrity_gates.values()):
        result['decision'] = 'QUARANTINE_INTEGRITY'
        return result
    if not all(mechanism_gates.values()):
        result['decision'] = 'CLOSED_AT_MECHANISM'
        return result
    primary = contrast_summary(cells, CANDIDATE, B100)
    active_primary = contrast_summary(cells, CANDIDATE, B100, keys=active_keys)
    suppressive = contrast_summary(cells, CANDIDATE, FACTORY)
    factory_main = contrast_summary(cells, FACTORY, RESIDENT)
    b100_main = contrast_summary(cells, B100, RESIDENT)
    interaction_margin = primary['mean_margin_delta'] - factory_main['mean_margin_delta']
    family_means = {}
    for opponent in OPPONENTS:
        family_keys = {key for key in active_keys if key[2] == opponent}
        family_means[opponent] = contrast_summary(cells, CANDIDATE, B100, keys=family_keys)['mean_margin_delta']
    candidate_catastrophes = sum((margin(cells[key][CANDIDATE]) <= -100 for key in complete_keys))
    control_catastrophes = sum((margin(cells[key][B100]) <= -100 for key in complete_keys))
    candidate_negative_mass = negative_margin_mass(cells, CANDIDATE, complete_keys)
    control_negative_mass = negative_margin_mass(cells, B100, complete_keys)
    negative_mass_ratio = candidate_negative_mass / control_negative_mass if control_negative_mass else 0.0 if candidate_negative_mass == 0 else None
    own_delta = primary['mean_own_score_delta']
    opponent_delta = primary['mean_opponent_score_delta']
    safety_ratio_ok = own_delta > 0 and opponent_delta <= 0.4 * own_delta
    value_gates = {'overall_mean_margin_at_least_1': primary['mean_margin_delta'] >= 1.0, 'map_cluster_ci_lower_nonnegative': primary['map_cluster_bootstrap_margin_ci95'][0] >= 0.0, 'active_mean_margin_at_least_4': active_primary['mean_margin_delta'] >= 4.0, 'active_mean_own_score_at_least_2': active_primary['mean_own_score_delta'] >= 2.0, 'active_more_improve_than_regress': active_primary['improved'] > active_primary['regressed'], 'active_regression_rate_at_most_0_40': active_primary['regressed'] / active_primary['n'] <= 0.4, 'at_least_six_nonnegative_families': sum((value >= 0 for value in family_means.values())) >= 6, 'worst_family_at_least_minus_5': min(family_means.values()) >= -5.0, 'active_p10_at_least_minus_20': active_primary['p10_margin_delta'] >= -20.0, 'active_worst_at_least_minus_60': active_primary['minimum_margin_delta'] >= -60.0, 'catastrophes_do_not_increase': candidate_catastrophes <= control_catastrophes, 'negative_margin_mass_at_most_control': negative_mass_ratio is not None and negative_mass_ratio <= 1.0, 'active_wood_delta_positive': active_primary['mean_wood_delta'] > 0, 'active_own_crop_harvest_delta_positive': active_primary['mean_own_crop_harvest_delta'] > 0}
    safety_gates = {'mean_opponent_score_delta_at_most_1': opponent_delta <= 1.0, 'opponent_score_delta_at_most_0_40_of_own_delta': safety_ratio_ok, 'mean_opponent_created_fruit_delta_at_most_2': primary['mean_opponent_created_fruit_delta'] <= 2.0, 'opponent_created_fruit_ci_upper_at_most_5': primary['map_cluster_bootstrap_opponent_created_fruit_ci95'][1] <= 5.0, 'mean_opponent_created_wood_delta_at_most_2': primary['mean_opponent_created_wood_delta'] <= 2.0, 'opponent_created_wood_ci_upper_at_most_5': primary['map_cluster_bootstrap_opponent_created_wood_ci95'][1] <= 5.0, 'b100_inside_factory_reduces_opponent_score_by_5': suppressive['mean_opponent_score_delta'] <= -5.0, 'b100_inside_factory_own_score_cost_at_most_5': suppressive['mean_own_score_delta'] >= -5.0, 'direct_theft_does_not_increase': paired_values(cells, CANDIDATE, FACTORY, lambda row: sum((row[f'opponent_fruit_from_ours_{kind}'] for kind in FRUITS)) + row['opponent_from_ours']) and mean(paired_values(cells, CANDIDATE, FACTORY, lambda row: sum((row[f'opponent_fruit_from_ours_{kind}'] for kind in FRUITS)) + row['opponent_from_ours'])) <= 0.0}
    for summary in (primary, active_primary, suppressive, factory_main, b100_main):
        summary.pop('_margin_delta', None)
        summary.pop('_keys', None)
    result.update({'contrasts': {'candidate_minus_current_b100': primary, 'active_candidate_minus_current_b100': active_primary, 'candidate_minus_factory': suppressive, 'factory_minus_resident': factory_main, 'b100_minus_resident': b100_main, 'factorial_interaction_mean_margin': interaction_margin}, 'family_mean_margin_delta': family_means, 'tails': {'control_catastrophes': control_catastrophes, 'candidate_catastrophes': candidate_catastrophes, 'control_negative_margin_mass': control_negative_mass, 'candidate_negative_margin_mass': candidate_negative_mass, 'negative_margin_mass_ratio': negative_mass_ratio}, 'value_gates': value_gates, 'safety_gates': safety_gates})
    if not all(safety_gates.values()):
        result['decision'] = 'CLOSED_AT_SAFETY'
    elif not all(value_gates.values()):
        result['decision'] = 'CLOSED_AT_VALUE'
    elif phase == 'discovery':
        result['decision'] = 'PASS_OPEN_CONFIRMATION'
    else:
        result['decision'] = 'QUALIFIED_LOCAL'
    return result

def write_atomic(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(payload, indent=2) + '\n')
    temporary.replace(path)

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-a', type=Path, required=True)
    parser.add_argument('--input-b', type=Path, required=True)
    parser.add_argument('--phase', choices=('discovery', 'confirmation'), required=True)
    parser.add_argument('--expected-maps', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.input_a, args.input_b, expected_maps=args.expected_maps, phase=args.phase)
    write_atomic(args.output, result)
    print(json.dumps({'decision': result['decision'], 'observed': result['observed'], 'integrity_gates': result['integrity_gates'], 'mechanism_gates': result['mechanism_gates'], 'value_gates': result.get('value_gates'), 'safety_gates': result.get('safety_gates')}, indent=2))
if __name__ == '__main__':
    main()
