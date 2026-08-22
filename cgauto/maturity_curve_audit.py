#!/usr/bin/env python3
"""Run the N1 maturity-identifiability audit over stored D61p snapshots."""
from __future__ import annotations
import argparse, collections, csv, datetime as dt, json, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from chatgpt_1.n1_maturity_io import load_snapshots,build_panel,build_intervals,battle_summary,field_inventory
from chatgpt_1.n1_maturity_model import identify,fit,project,decide

def save_csv(path,rows):
    fields=sorted({k for r in rows for k in r});path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def markdown(result):
    i=result['identification'];p=result['resident_projection'];v=result['scientific_verdict']
    lines=['# N1 maturity-curve measurement','',f"**Verdict: {v['verdict']}**",'',f"- Support: **{i['support']}**",f"- Snapshots: {i['snapshot_count']}",
        f"- Panel rows / unique / repeated agents: {i['panel_rows']} / {i['unique_agents']} / {i['repeated_exact_agents']}",f"- Score-changing intervals: {i['score_changing_intervals']}",
        f"- With/without advancing updateTime: {i['score_changes_with_advancing_update_time']} / {i['score_changes_without_advancing_update_time']}",
        f"- Rank-only score-frozen intervals: {i['score_frozen_rank_movement_intervals']}",f"- Age-bin crossings: {i['age_bin_crossings']}",
        f"- creationTime/updateTime coverage: {i['creation_time_coverage']:.1%} / {i['update_time_coverage']:.1%}",f"- Lifetime battle-count coverage: {i['lifetime_battle_count_coverage']:.1%}",
        f"- Visible new/dropped battle IDs: {i['visible_new_battle_ids_across_intervals']} / {i['visible_dropped_battle_ids_across_intervals']}",'','## Resident projection','']
    if p.get('available'):lines += [f"- Score: {p.get('current_score')}",f"- Age/bin: {p.get('current_age_days')} / {p.get('current_age_bin')}",f"- Remaining uplift: {p.get('remaining_maturity_uplift')}",f"- Mature projection: {p.get('projected_mature_score')}",f"- Gap to 24.70 now/projected: {p.get('gap_to_interim_now')} / {p.get('gap_to_interim_projected')}",f"- Gap to 25.40 now/projected: {p.get('gap_to_target_now')} / {p.get('gap_to_target_projected')}"]
    else:lines.append(f"- unavailable: {p.get('reason')}")
    lines += ['','## Interpretation','',*['- '+x for x in i['reasons']],'- Individual fixed effects identify only within-agent age-bin transitions; snapshot fixed effects absorb pool-wide score shifts.','- Rank-only movement is pool drift, not maturity.','- Recent battle-list length is never treated as lifetime games.','- The anecdotal 3–4 point figure is not used as a prior.','','## Reproduction','','```bash','python3 cgauto/maturity_curve_audit.py --snapshot-root data/raw/snapshots --output-dir chatgpt_1/n1-maturity-result','```','']
    return '\n'.join(lines)

def run(a):
    snaps,errors=load_snapshots(a.snapshot_root);rows=build_panel(snaps);intervals=build_intervals(rows);battles=battle_summary(snaps);ident=identify(rows,intervals,snaps,battles)
    counts=collections.Counter(r['agent_id'] for r in rows);fit_rows=[r for r in rows if counts[r['agent_id']]>=2]
    model=fit(fit_rows,ident['full_model_includes_lifetime_battle_count'],a.bootstrap,a.seed) if ident['support']!='UNIDENTIFIABLE' else {'fit_status':'not_run_unidentifiable'}
    projection=project(rows,model,a.resident_agent_id,a.target_score,a.interim_score);verdict=decide(ident,projection,model)
    result={'schema':'troll-farm-n1-maturity-audit-v1','generated_at_utc':dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z'),
        'configuration':{'snapshot_root':str(a.snapshot_root),'output_dir':str(a.output_dir),'resident_agent_id':a.resident_agent_id,'target_score':a.target_score,'interim_score':a.interim_score,'bootstrap':a.bootstrap,'seed':a.seed},
        'snapshot_ids':[s['id'] for s in snaps],'load_errors':errors,'field_inventory':field_inventory(snaps),'battle_summary':battles,'identification':ident,'fit_panel_rows':len(fit_rows),'fit':model,'resident_projection':projection,'scientific_verdict':verdict}
    a.output_dir.mkdir(parents=True,exist_ok=True);(a.output_dir/'coverage-and-result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');save_csv(a.output_dir/'panel.csv',[{k:v for k,v in r.items() if k!='visible_battle_ids'} for r in rows]);save_csv(a.output_dir/'intervals.csv',intervals);(a.output_dir/'report.md').write_text(markdown(result));return result

def selftest():
    with tempfile.TemporaryDirectory() as d:
        root=Path(d)/'snapshots';base=dt.datetime(2026,7,1,tzinfo=dt.timezone.utc)
        for day in range(7):
            p=root/f's{day}';(p/'battles').mkdir(parents=True);now=base+dt.timedelta(days=day);users=[]
            for j,aid in enumerate(range(100,112)):
                created=base-dt.timedelta(days=1+j%5)+dt.timedelta(hours=j);age=(now-created).total_seconds()/86400
                users.append({'agentId':aid,'score':18+j*.1+min(max(age,0),14)*.08+(.2 if day>=4 else 0),'localRank':j+1+day%2,'creationTime':int(created.timestamp()*1000),'updateTime':int((now-dt.timedelta(hours=1)).timestamp()*1000),'codingamer':{'userId':aid+1000}})
                (p/'battles'/f'{aid}.json').write_text(json.dumps([{'gameId':day*1000+aid,'date':int(now.timestamp()*1000)}]))
            (p/'leaderboard.json').write_text(json.dumps({'users':users}));(p/'manifest.json').write_text(json.dumps({'schema':'troll-farm-d61p-snapshot-v1','snapshot_id':f's{day}','completed_at_utc':now.isoformat().replace('+00:00','Z'),'complete':True}))
        a=argparse.Namespace(snapshot_root=root,output_dir=Path(d)/'out',resident_agent_id=100,target_score=25.4,interim_score=24.7,bootstrap=30,seed=7)
        result=run(a);assert result['identification']['snapshot_count']==7 and result['identification']['support']=='PARTIAL' and (a.output_dir/'report.md').exists()

def parse_args():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--snapshot-root',type=Path,default=Path('data/raw/snapshots'));p.add_argument('--output-dir',type=Path,default=Path('chatgpt_1/n1-maturity-result'));p.add_argument('--resident-agent-id',type=int,default=6561795);p.add_argument('--target-score',type=float,default=25.4);p.add_argument('--interim-score',type=float,default=24.7);p.add_argument('--bootstrap',type=int,default=1000);p.add_argument('--seed',type=int,default=20260730);p.add_argument('--self-test',action='store_true');return p.parse_args()
def main():
    a=parse_args()
    if a.self_test:selftest();print('self-test: ok');return 0
    result=run(a);print(json.dumps({'support':result['identification']['support'],'verdict':result['scientific_verdict']['verdict'],'snapshots':result['identification']['snapshot_count'],'output_dir':str(a.output_dir)},sort_keys=True));return 0 if result['scientific_verdict']['verdict']!='UNIDENTIFIABLE' else 2
if __name__=='__main__':sys.exit(main())
