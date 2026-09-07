#!/usr/bin/env python3
"""Read-only arithmetic, documentary index and optional pinned-checkout audit.

No network, games, builds, holdout opens, or repository mutations. --out writes only
new report files. The embedded census is a documentary index, not a build count.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import difflib
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import subprocess
import sys
import unittest

MAIN_PIN = '67b2acc1e828cf25a7e6e76c2814dfcd3268a45c'
NEIGHBOUR_PIN = 'badf27efee7eca794c149f0707c087f7ed1eb0ff'
RECENT = [18.19, 17.04, 18.14, 18.72, 19.23]
# Explicit documentary tags. Unlisted identifiers stay unresolved; neither a
# numeric range nor a source filename certifies a distinct completed experiment.
GROUPS = {
 'orchard': '100-101,105,108,114,137-140,143-145,153-159,160-163,166-186,187-194,200-211,231-236,245-246,248-258,267-269,292-293,298,301,316-318,320-324,331-348,352,399-404,423,441-467,476-481,549,552-554,556-562,569-571,588-608,610-614,616-630',
 'roster': '20,164,195-199,212-221,237,241-244,247,300,302,325,349,384-388,470-475,548,551,563-568,572-586,609',
 'denial': '259-264,270-291,295-296,299,303-309,357-383,389-398,422,468-469',
 'traffic': '354-356,410-421,433-440',
 'allocation': '116,127,133,146-152,228-230,238,252,294,297,310-315,319,326-330,351,405-409',
 'legacy_reference': '1-3,54,222-227,239-240,425',
 'adaptive_economy': '529,539,541-543,545-547',
 'instrument': '550,555,587,615',
}
ALIASES = {115:54,121:54,125:100,133:127,350:311,353:314,356:355,
           370:368,381:379,392:390,414:413,417:416,421:420,424:368,
           438:437,440:439}
MEASUREMENT_ONLY = {550,551,555,556,563,587,615}
# These values are documentary readings; no dates are inferred from version IDs.
MATURE = {2:(23.03,32),100:(24.03,25),108:(22.90,32),115:(23.53,29),
121:(22.92,31),125:(23.76,26),133:(22.30,35),137:(23.35,28),140:(21.52,37),
152:(22.72,30),231:(24.01,25),236:(23.05,29),248:(22.45,32),251:(23.81,27),
256:(23.65,28),258:(24.59,21),266:(22.85,30),274:(23.32,28),311:(24.67,22),
314:(22.72,30),350:(24.79,20),353:(23.22,29),356:(22.60,30),370:(25.21,17),
381:(24.73,22),392:(21.15,38),414:(22.66,32),417:(24.95,20),421:(23.54,27),
424:(21.06,37),438:(22.07,35),440:(22.91,29),543:(13.92,155)}


def expand(text: str) -> set[int]:
    result: set[int] = set()
    for part in text.split(','):
        ends = [int(x) for x in part.split('-')]
        lo, hi = ends[0], ends[-1]
        if not 1 <= lo <= hi <= 630:
            raise ValueError(f'invalid version range {part}')
        result.update(range(lo, hi + 1))
    return result


def documentary_census() -> list[dict]:
    tags = {name: expand(text) for name, text in GROUPS.items()}
    rows = []
    for version in range(1, 631):
        parent = ALIASES.get(version)
        lookup = parent if parent is not None else version
        families = sorted(name for name, ids in tags.items() if lookup in ids)
        if version == 266:
            families = ['orchard']
        kind = ('measurement_only' if version in MEASUREMENT_ONLY else
                'publication_or_recheck_alias' if parent is not None else
                'documented_label' if families else 'unresolved')
        if version == 477:
            kind = 'built_unmeasured_reported'
        rating, rank = MATURE.get(version, (None, None))
        rows.append(dict(version=version, kind=kind, alias_of=parent,
                         families=';'.join(families) or 'UNRESOLVED',
                         mature_rating=rating, mature_rank=rank,
                         source='N:README.md; N:RESEARCH-QUEUE.md; dated results' if families else '',
                         source_inventory_checked=False,
                         note='Also used for a portfolio measurement; numeric ID is not unique' if version == 612 else ''))
    return rows


def halfwidth(sd: float, n: int) -> float:
    if not math.isfinite(sd) or sd < 0 or n < 1:
        raise ValueError('finite nonnegative SD and positive n required')
    return 1.96 * sd * math.sqrt(2 / n)


def match_points(wins: int, draws: int, losses: int) -> float:
    if any(type(x) is not int or x < 0 for x in (wins, draws, losses)):
        raise ValueError('outcome counts must be nonnegative integers')
    return wins + draws / 2


def official_points(own_rank: int, opponent_rank: int) -> float:
    if type(own_rank) is not int or type(opponent_rank) is not int:
        raise ValueError('official rank integers required')
    return 1.0 if own_rank < opponent_rank else 0.0 if own_rank > opponent_rank else 0.5


def chunks(job_count: int, maximum: int = 12) -> list[int]:
    if job_count < 0 or maximum < 1:
        raise ValueError('invalid chunk budget')
    full, remainder = divmod(job_count, maximum)
    return [maximum] * full + ([remainder] if remainder else [])


def observed_complete(row: dict) -> bool:
    """Recognize completion assertions, never reinterpret fetch success as maturity.

    This validates recorded counts, not unique raw games. Exact raw identity/archive
    validation remains a separate prerequisite. Unknown schemas are NOT_COMPLETE.
    """
    room = row.get('room')
    if not isinstance(room, dict):
        return False
    expected = row.get('expected_agent_id', row.get('agent_id'))
    agent = room.get('agentId')
    count = row.get('listed_battles', row.get('games_done_count', row.get('battle_count')))
    pending = row.get('pending_battles', row.get('pending_count'))
    return (type(expected) is int and expected == agent and
            type(count) is int and count >= 160 and pending == 0 and
            room.get('percentage') == 100 and room.get('percentageNoCache') == 100 and
            room.get('inProgress') is False and row.get('submission_id') is not None)


def git_bytes(root: Path, pin: str, path: str) -> bytes:
    return subprocess.check_output(['git', '-C', str(root), 'show', f'{pin}:{path}'],
                                   stderr=subprocess.PIPE)


def git_paths(root: Path, pin: str) -> list[str]:
    raw = subprocess.check_output(['git', '-C', str(root), 'ls-tree', '-r', '--name-only', '-z', pin],
                                  stderr=subprocess.PIPE)
    return [x.decode('utf-8') for x in raw.split(b'\0') if x]


def blob_id(content: bytes) -> str:
    return hashlib.sha1(f'blob {len(content)}\0'.encode() + content).hexdigest()


def rust_tokens(text: str) -> list[str]:
    """Conservative token stream; removes comments/space, preserves literals exactly.

    Not a Rust parser. Raw/ordinary strings, chars and nested block comments are
    preserved/handled. Token equality is only lexical, not semantic equivalence.
    """
    out = []
    i = 0
    while i < len(text):
        if text[i].isspace():
            i += 1
        elif text.startswith('//', i):
            end = text.find('\n', i)
            i = len(text) if end < 0 else end + 1
        elif text.startswith('/*', i):
            depth, j = 1, i + 2
            while j < len(text) and depth:
                if text.startswith('/*', j): depth, j = depth + 1, j + 2
                elif text.startswith('*/', j): depth, j = depth - 1, j + 2
                else: j += 1
            if depth: raise ValueError('unterminated block comment')
            i = j
        else:
            raw = re.match(r'(?:br|cr|r)(#*)"', text[i:])
            if raw:
                endmark = '"' + raw.group(1)
                end = text.find(endmark, i + raw.end())
                if end < 0: raise ValueError('unterminated raw string')
                j = end + len(endmark)
                out.append(text[i:j]); i = j
                continue
            string = re.match(r'(?:b|c)?"(?:\\.|[^"\\])*"', text[i:], re.S)
            char = re.match(r"(?:b)?'(?:\\(?:u\{[0-9a-fA-F_]+\}|x[0-9a-fA-F]{2}|.)|[^'\\])'", text[i:], re.S)
            word = re.match(r'[A-Za-z_][A-Za-z_0-9]*|[0-9][A-Za-z_0-9.]*', text[i:])
            token = string or char or word
            if token:
                out.append(token.group()); i += token.end()
            else:
                out.append(text[i]); i += 1
    return out


def checkout_audit(main_root: Path, neighbour_root: Path, out: Path) -> dict:
    """Read pinned Git objects; untracked working-tree files never become evidence."""
    mpaths, npaths = git_paths(main_root, MAIN_PIN), git_paths(neighbour_root, NEIGHBOUR_PIN)
    inventory = []
    for version in range(1, 631):
        pattern = re.compile(rf'(?i)(?:^|[/_\-])v?{version}(?!\d)(?:[_\-.]|$)')
        hits = [p for p in npaths if pattern.search(p) and p.endswith(('.rs', '.py', '.md'))]
        inventory.append(dict(version=version, source_paths=hits,
                              interpretation='Filename matches, not unique semantic builds'))
    (out / 'checkout-candidate-paths.json').write_text(json.dumps(inventory, indent=2) + '\n')
    copies = []
    for p in npaths:
        target = 'neighbour/separate_troll_farm/' + p
        if p.endswith('.md') and target in mpaths:
            a, b = git_bytes(neighbour_root, NEIGHBOUR_PIN, p), git_bytes(main_root, MAIN_PIN, target)
            copies.append(dict(path=p, neighbour_blob=blob_id(a), snapshot_blob=blob_id(b), equal=a == b))
    (out / 'checkout-snapshot-comparison.json').write_text(json.dumps(copies, indent=2) + '\n')
    dated, unclassified = [], []
    for p in mpaths:
        if 'working-storage/' not in p or not p.endswith('.jsonl') or 'readings' not in p:
            continue
        content = git_bytes(main_root, MAIN_PIN, p)
        completed = []
        for number, line in enumerate(content.decode('utf-8').splitlines(), 1):
            if not line.strip(): continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f'{p}:{number}: invalid JSON') from exc
            if observed_complete(row):
                completed.append((number, row))
        if not completed:
            unclassified.append(dict(path=p, reason='No recognized complete-count assertion; inspect schema/narrative'))
        else:
            # One documented final poll per submission, never best-score selection.
            by_sub = {}
            for number, row in completed:
                by_sub[str(row['submission_id'])] = (number, row)
            for number, row in by_sub.values():
                dated.append(dict(path=p, blob=blob_id(content), line=number,
                                  at=row.get('at', row.get('read_at')), submission_id=row['submission_id'],
                                  agent_id=row['room'].get('agentId'), rating=row['room'].get('score'),
                                  rank=row['room'].get('rank'), evidence='Recorded count/progress assertion; archive not checked'))
    (out / 'checkout-dated-readings.json').write_text(json.dumps(dated, indent=2) + '\n')
    (out / 'checkout-unclassified-ledgers.json').write_text(json.dumps(unclassified, indent=2) + '\n')
    a = git_bytes(main_root, MAIN_PIN, 'readable/denial-off-champion.rs').decode()
    b = git_bytes(neighbour_root, NEIGHBOUR_PIN, 'bot.rs').decode()
    diff = difflib.unified_diff(rust_tokens(a), rust_tokens(b), fromfile='M denial-off tokens', tofile='N V439 tokens', lineterm='')
    (out / 'checkout-lineage-tokens.diff').write_text('\n'.join(diff) + '\n')
    return dict(status='EXECUTED', main_pin=MAIN_PIN, neighbour_pin=NEIGHBOUR_PIN,
                neighbour_paths=len(npaths), snapshot_docs_compared=len(copies),
                dated_assertions=len(dated), unclassified_ledgers=len(unclassified),
                scope='Read-only tracked-object census and lexical diff; no source builds or raw-game certification')


def metrics() -> dict:
    sd = statistics.stdev(RECENT)
    rows = documentary_census()
    family_labels = Counter(f for r in rows for f in r['families'].split(';'))
    return dict(
        scope='Arithmetic and manually sourced documentary tags only',
        checkout_audit='NOT_RUN', source_pins={'main': MAIN_PIN, 'neighbour': NEIGHBOUR_PIN},
        recent_champion={'n':5, 'mean':statistics.mean(RECENT), 'sample_sd':sd,
                         'range':max(RECENT)-min(RECENT),
                         'normal_halfwidth':{str(n):halfwidth(sd,n) for n in [1,4,6,21]}},
        proposed_budgets={'development':32*2*6*2, 'aa':5*2*2, 'pilot':12*2*2,
                          'confirmation':512*2, 'unranked_total':20+48+1024,
                          'confirmation_chunks':len(chunks(1024)),
                          'stage_separate_chunks':len(chunks(20))+len(chunks(48))+len(chunks(1024)),
                          'ladder_nominal':4*2*160},
        precision={'matchpoint_halfwidth_worst_sd1_n512':1.96/math.sqrt(512),
                   'matchpoint_blocks_80pct_power_5pp_sd1':math.ceil(((1.96+0.8416212335729143)/.05)**2),
                   'local_margin_halfwidth_n512':halfwidth(40.20345625425082,512)},
        matched_records={'funding_parent_points':match_points(7,6,3),
                         'funding_candidate_points':match_points(8,5,3),
                         'homegrowth_parent_points':match_points(173,5,14),
                         'homegrowth_candidate_points':match_points(173,5,14),
                         'V543_384_parent_points':match_points(341,2,41),
                         'V543_384_candidate_points':match_points(340,4,40)},
        census={'version_labels':len(rows),'kinds':dict(Counter(r['kind'] for r in rows)),
                'family_tag_counts_nonexclusive':dict(family_labels),
                'unique_completed_build_count':None,
                'explanation':'Numeric labels, aliases and documentary tags; source inventory not executed'}
    )


class AuditTests(unittest.TestCase):
    def test_census_coverage(self):
        rows = documentary_census()
        self.assertEqual([x['version'] for x in rows], list(range(1,631)))
        self.assertEqual(rows[369]['alias_of'],368)
        self.assertEqual(rows[476]['kind'],'built_unmeasured_reported')
        self.assertEqual(rows[550]['kind'],'measurement_only')
        self.assertIn('portfolio',rows[611]['note'])
    def test_sd(self):
        sd = statistics.stdev(RECENT)
        self.assertAlmostEqual(sd, .8154937154877409)
        self.assertGreater(halfwidth(sd,4),1)
        self.assertLess(halfwidth(sd,6),1)
        with self.assertRaises(ValueError): halfwidth(sd,0)
    def test_match_points(self):
        self.assertEqual(match_points(341,2,41),match_points(340,4,40))
        self.assertEqual(match_points(8,5,3)-match_points(7,6,3),.5)
        with self.assertRaises(ValueError): match_points(-1,0,0)
    def test_official_outcomes(self):
        self.assertEqual(official_points(0,1),1)
        self.assertEqual(official_points(0,0),.5)
        self.assertEqual(official_points(1,0),0)
        with self.assertRaises(ValueError): official_points(None,1)
    def test_budget(self):
        self.assertEqual(sum(chunks(1024)),1024)
        self.assertEqual(len(chunks(1024)),86)
        self.assertEqual(chunks(1024)[-1],4)
        self.assertEqual(metrics()['proposed_budgets']['unranked_total'],1092)
    def test_not_fetch_success(self):
        self.assertFalse(observed_complete({'success':True,'age_min':65.1,'score':23.03}))
        row={'expected_agent_id':1,'submission_id':2,'listed_battles':160,'pending_battles':0,
             'room':{'agentId':1,'percentage':100,'percentageNoCache':100,'inProgress':False}}
        self.assertTrue(observed_complete(row))
        for key,value in [('listed_battles',159),('pending_battles',1),('expected_agent_id',3)]:
            bad=dict(row); bad[key]=value; self.assertFalse(observed_complete(bad))
        row['room']['percentage']=99; self.assertFalse(observed_complete(row))
    def test_tokens(self):
        a='let x = r#"/* text */"#; /* outer /* inner */ end */ // c\n let y = "//keep";'
        b='let x=r#"/* text */"#;let y="//keep";'
        self.assertEqual(rust_tokens(a),rust_tokens(b))
        self.assertNotEqual(rust_tokens('let x="a";'),rust_tokens('let x="b";'))
        self.assertEqual(rust_tokens("'a' //x\n &'life str"),["'a'",'&',"'",'life','str'])
        with self.assertRaises(ValueError): rust_tokens('/* nope')
    def test_utf16_and_blob(self):
        self.assertEqual(len('a\U0001f331'.encode('utf-16-le'))//2,3)
        self.assertEqual(blob_id(b''),'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391')


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--self-test',action='store_true')
    p.add_argument('--out',type=Path)
    p.add_argument('--main-root',type=Path)
    p.add_argument('--neighbour-root',type=Path)
    args=p.parse_args()
    if args.self_test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(AuditTests)
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    if bool(args.main_root) != bool(args.neighbour_root):
        p.error('both checkout roots are required together')
    result=metrics()
    try:
        if args.out:
            args.out.mkdir(parents=True,exist_ok=True)
            # Refuse accidental overwrites of prior audit outputs.
            targets=['extension-metrics.json','candidate-index.csv']
            if any((args.out/name).exists() for name in targets):
                raise ValueError('output already contains an audit; choose a fresh directory')
            rows=documentary_census()
            with (args.out/'candidate-index.csv').open('w',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
            if args.main_root:
                result['checkout_audit']=checkout_audit(args.main_root,args.neighbour_root,args.out)
            (args.out/'extension-metrics.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        elif args.main_root:
            p.error('--out is required for checkout auditing')
        print(json.dumps(result,indent=2,sort_keys=True))
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f'AUDIT FAILED: {exc}',file=sys.stderr);return 2
    return 0

if __name__=='__main__':
    raise SystemExit(main())
