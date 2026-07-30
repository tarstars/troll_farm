"""Identification gates, fixed-effects model, and N1 verdict."""
from __future__ import annotations
import collections, math, random
from .n1_maturity_io import BINS
try:
    import numpy as np
except ImportError:
    np=None

def identify(rows,ints,snaps,bsummary):
    by=collections.Counter(r['agent_id'] for r in rows);repeated=sum(v>=2 for v in by.values());n=len(rows)
    cc=sum(r['creation_epoch'] is not None for r in rows)/n if n else 0;uc=sum(r['update_epoch'] is not None for r in rows)/n if n else 0;bc=sum(r['lifetime_battle_count'] is not None for r in rows)/n if n else 0
    changes=sum(i['score_changed'] for i in ints);crossings=sum(i['crossed_age_bin'] for i in ints);cvals=collections.defaultdict(set);uvals=collections.defaultdict(set);future=0
    for r in rows:
        if r['creation_epoch'] is not None:cvals[r['agent_id']].add(round(r['creation_epoch'],3));future+=r['creation_epoch']>r['snapshot_epoch']+300
        if r['user_id'] is not None:uvals[r['agent_id']].add(r['user_id'])
    badc=sum(len(v)>1 for v in cvals.values());badu=sum(len(v)>1 for v in uvals.values());no_update=sum(i['score_changed_without_update_advance'] for i in ints);updchg=sum(i['score_changed'] and i['update_advanced'] for i in ints);poscount=sum((i['lifetime_battle_count_delta'] or 0)>0 for i in ints);full=bc>=.8 and poscount>=5
    fail=[]
    if len(snaps)<2:fail.append('fewer than two complete snapshots')
    if repeated<10:fail.append(f'only {repeated} exact agents repeat')
    if changes<5:fail.append(f'only {changes} score-changing exact-agent intervals')
    if cc<.8:fail.append(f'creationTime coverage is {cc:.1%}')
    if crossings<5:fail.append(f'only {crossings} within-agent age-bin crossings')
    if badc:fail.append(f'creationTime changes for {badc} agents')
    if future:fail.append(f'{future} rows have future creationTime')
    if badu:fail.append(f'{badu} agentIds map to multiple userIds')
    if uc>=.8 and changes and no_update/changes>.25:fail.append(f'{no_update}/{changes} score changes lack advancing updateTime')
    support='UNIDENTIFIABLE' if fail else ('FULL' if full else 'PARTIAL');reasons=fail or (['creationTime and varying uncensored lifetime battle count are available'] if full else ['creationTime is usable; battle accumulation remains censored'])
    return {'support':support,'reasons':reasons,'snapshot_count':len(snaps),'panel_rows':n,'unique_agents':len(by),'repeated_exact_agents':repeated,'intervals':len(ints),
        'score_changing_intervals':changes,'score_changes_with_advancing_update_time':updchg,'score_changes_without_advancing_update_time':no_update,
        'update_advanced_without_score_change':sum(i['update_advanced_without_score_change'] for i in ints),'update_time_regressions':sum(i['update_regressed'] for i in ints),
        'score_frozen_rank_movement_intervals':sum(i['rank_only_movement'] for i in ints),'age_bin_crossings':crossings,'creation_time_coverage':cc,'update_time_coverage':uc,
        'lifetime_battle_count_coverage':bc,'positive_lifetime_battle_count_deltas':poscount,'creation_time_inconsistent_agents':badc,'agent_to_user_inconsistent_agents':badu,
        'future_creation_rows':future,'visible_new_battle_ids_across_intervals':sum(i['visible_new_battle_ids'] for i in ints),'visible_dropped_battle_ids_across_intervals':sum(i['visible_dropped_battle_ids'] for i in ints),
        'battle_count_status':bsummary['lifetime_count_status'],'full_model_includes_lifetime_battle_count':full}

def matrix(rows,include_count=False):
    snaps=sorted({r['snapshot_id'] for r in rows});bins=[x[0] for x in BINS];cols=[f's:{x}' for x in snaps[1:]]+[f'age:{x}' for x in bins[:-1]]+(['battles100'] if include_count else [])
    raw=[]
    for r in rows:
        if r['age_bin'] is None:continue
        v=[float(r['snapshot_id']==x) for x in snaps[1:]]+[float(r['age_bin']==x) for x in bins[:-1]]
        if include_count:
            if r['lifetime_battle_count'] is None:continue
            v.append(r['lifetime_battle_count']/100)
        raw.append((r['agent_id'],v,r['score']))
    by=collections.defaultdict(list)
    for aid,v,y in raw:by[aid].append((v,y))
    X=[];Y=[]
    for group in by.values():
        if len(group)<2:continue
        means=[sum(v[j] for v,_ in group)/len(group) for j in range(len(cols))];my=sum(y for _,y in group)/len(group)
        for v,y in group:X.append([v[j]-means[j] for j in range(len(cols))]);Y.append(y-my)
    return np.asarray(X,float),np.asarray(Y,float),cols

def fit(rows,include_count=False,bootstrap=1000,seed=20260730):
    if np is None:return {'fit_status':'numpy_unavailable'}
    X,y,cols=matrix(rows,include_count)
    if not len(y) or X.shape[0]<=X.shape[1]:return {'fit_status':'too_few_rows','rows':len(y),'columns':X.shape[1]}
    beta,_,rank,sing=np.linalg.lstsq(X,y,rcond=None)
    if rank<X.shape[1]:return {'fit_status':'rank_deficient','rank':int(rank),'columns':X.shape[1]}
    effects={x[0]:0. for x in BINS}
    for x in effects:
        if x!='ge_14d':effects[x]=float(beta[cols.index('age:'+x)])
    by=collections.defaultdict(list)
    for r in rows:by[r['agent_id']].append(r)
    ids=sorted(by);rng=random.Random(seed);boots=collections.defaultdict(list)
    for _ in range(max(0,bootstrap)):
        sample=[]
        for j,aid in enumerate(rng.choices(ids,k=len(ids))):
            for r in by[aid]:q=dict(r);q['agent_id']=10_000_000_000+j;sample.append(q)
        try:
            bX,byy,bc=matrix(sample,include_count)
            if bX.shape[0]<=bX.shape[1]:continue
            bb,_,br,_=np.linalg.lstsq(bX,byy,rcond=None)
            if br<bX.shape[1]:continue
            for x in effects:boots[x].append(0. if x=='ge_14d' else float(bb[bc.index('age:'+x)]))
        except Exception:pass
    ci={}
    for x in effects:
        z=sorted(boots[x]);ci[x]=None if len(z)<20 else [z[int(.025*(len(z)-1))],z[int(.975*(len(z)-1))]]
    return {'fit_status':'ok','rows':len(y),'columns':X.shape[1],'rank':int(rank),'age_effect_vs_ge_14d':effects,'age_effect_ci95':ci,'bootstrap_requested':bootstrap,
        'bootstrap_usable':min((len(v) for v in boots.values()),default=0),'condition_number':float(sing[0]/sing[-1]) if sing[-1]>0 else math.inf,
        'included_lifetime_battle_count':include_count,'lifetime_battle_score_per_100':float(beta[cols.index('battles100')]) if include_count else None}

def project(rows,model,resident,target,interim):
    rr=[r for r in rows if r['agent_id']==resident]
    if not rr:return {'available':False,'reason':'resident absent from panel'}
    r=max(rr,key=lambda z:z['snapshot_epoch']);out={'available':True,'latest_snapshot':r['snapshot_id'],'current_score':r['score'],'current_age_days':r['age_days'],'current_age_bin':r['age_bin'],'gap_to_interim_now':interim-r['score'],'gap_to_target_now':target-r['score']}
    if model.get('fit_status')!='ok' or r['age_bin'] is None:return out|{'remaining_maturity_uplift':None,'projected_mature_score':None}
    uplift=-model['age_effect_vs_ge_14d'][r['age_bin']];m=r['score']+uplift
    return out|{'remaining_maturity_uplift':uplift,'projected_mature_score':m,'gap_to_interim_projected':interim-m,'gap_to_target_projected':target-m}

def decide(ident,projection,model):
    if ident['support']=='UNIDENTIFIABLE' or model.get('fit_status')!='ok':return {'verdict':'UNIDENTIFIABLE','basis':ident['reasons']+[f"fit={model.get('fit_status')}"]}
    if projection.get('remaining_maturity_uplift') is None:return {'verdict':'UNIDENTIFIABLE','basis':['resident projection unavailable']}
    ci=model['age_effect_ci95'].get(projection['current_age_bin']);uci=None if ci is None else [-ci[1],-ci[0]]
    if uci is None:return {'verdict':'UNIDENTIFIABLE','basis':['cluster-bootstrap interval unavailable']}
    verdict='IMMATERIAL' if uci[1]<.5 else ('MATERIAL' if uci[0]>=1 else 'MODEST')
    return {'verdict':verdict,'remaining_uplift':projection['remaining_maturity_uplift'],'remaining_uplift_ci95':uci,
        'thresholds':{'immaterial_ci_upper_below':.5,'material_ci_lower_at_least':1.0},'basis':['current-resident remaining uplift; 0.5 lower noise edge and 1.0 experiment value bar']}
