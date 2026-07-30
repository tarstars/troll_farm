"""Snapshot parsing and exact-agent panel construction for N1."""
from __future__ import annotations
import collections, datetime as dt, json, math, statistics
from pathlib import Path
from typing import Any

BINS=(('lt_1d',0,1),('d1_3',1,3),('d3_7',3,7),('d7_14',7,14),('ge_14d',14,math.inf))
COUNT_KEYS=('totalBattleCount','totalBattles','battlesCount','battleCount','totalGames','gamesCount','gameCount','matchesCount','matches')
BATTLE_IDS=('gameId','battleId','id','matchId')
TIME_KEYS=('creationTime','creation_time','createdAt','created_at','updateTime','update_time','updatedAt','updated_at','date','timestamp','endTime','startTime')

def ts(v:Any):
    if v is None or isinstance(v,bool): return None
    if isinstance(v,(int,float)):
        x=float(v); x=x/1000 if x>1e10 else x
        try:return dt.datetime.fromtimestamp(x,dt.timezone.utc)
        except (ValueError,OSError,OverflowError):return None
    if isinstance(v,str):
        t=v.strip()
        if not t:return None
        if t.isdigit():return ts(int(t))
        try:return dt.datetime.fromisoformat(t.replace('Z','+00:00')).astimezone(dt.timezone.utc)
        except ValueError:return None
    return None

def num(v):
    try:
        x=float(v); return x if math.isfinite(x) else None
    except (TypeError,ValueError):return None

def first(d,keys):return next((d[k] for k in keys if k in d and d[k] is not None),None)
def agebin(x):return next((n for n,a,b in BINS if x is not None and x>=0 and a<=x<b),None)
def agent_id(r):
    try:return int(first(r,('agentId','agent_id')))
    except (TypeError,ValueError):return None
def user_id(r):
    v=(r.get('codingamer') or {}).get('userId',first(r,('userId','user_id')))
    try:return int(v)
    except (TypeError,ValueError):return None

def users(p):
    if isinstance(p,dict) and isinstance(p.get('users'),list):return [x for x in p['users'] if isinstance(x,dict)]
    if isinstance(p,list):return [x for x in p if isinstance(x,dict)]
    raise ValueError('leaderboard has no users list')

def battle_id(r):
    for k in BATTLE_IDS:
        if r.get(k) is not None:return f'{k}:{r[k]}'
    return None

def lifetime_count(r):
    for k in COUNT_KEYS:
        x=num(r.get(k))
        if x is not None and x>=0:return x,k
    return None,None

def load_snapshots(root:Path):
    out=[]; errors=[]
    for mpath in sorted(root.glob('*/manifest.json')) if root.exists() else []:
        p=mpath.parent
        try:
            m=json.loads(mpath.read_text())
            if m.get('schema')!='troll-farm-d61p-snapshot-v1' or not m.get('complete'):continue
            when=ts(m.get('completed_at_utc'))
            if not when:raise ValueError('bad completed_at_utc')
            leaderboard=json.loads((p/'leaderboard.json').read_text());battles={}
            for f in sorted((p/'battles').glob('*.json')):
                try:
                    q=json.loads(f.read_text());battles[int(f.stem)]=[x for x in q if isinstance(x,dict)] if isinstance(q,list) else []
                except (ValueError,json.JSONDecodeError):pass
            out.append({'id':str(m.get('snapshot_id') or p.name),'time':when,'manifest':m,'leaderboard':leaderboard,'battles':battles,'path':str(p)})
        except Exception as e:errors.append({'path':str(p),'error':str(e)})
    return sorted(out,key=lambda s:s['time']),errors

def build_panel(snaps):
    out=[]
    for s in snaps:
        for r in users(s['leaderboard']):
            aid=agent_id(r);score=num(r.get('score'))
            if aid is None or score is None:continue
            created=ts(first(r,('creationTime','creation_time','createdAt','created_at')));updated=ts(first(r,('updateTime','update_time','updatedAt','updated_at')))
            total,field=lifetime_count(r);br=s['battles'].get(aid,[]);age=(s['time']-created).total_seconds()/86400 if created else None
            out.append({'snapshot_id':s['id'],'snapshot_epoch':s['time'].timestamp(),'snapshot_time':s['time'].isoformat().replace('+00:00','Z'),
                'agent_id':aid,'user_id':user_id(r),'pseudo':r.get('pseudo') or (r.get('codingamer') or {}).get('pseudo') or f'agent-{aid}',
                'score':score,'rank':num(first(r,('localRank','rank','globalRank','source_rank'))),
                'creation_epoch':created.timestamp() if created else None,'creation_time':created.isoformat().replace('+00:00','Z') if created else None,
                'update_epoch':updated.timestamp() if updated else None,'update_time':updated.isoformat().replace('+00:00','Z') if updated else None,
                'age_days':age,'age_bin':agebin(age),'lifetime_battle_count':total,'lifetime_battle_count_field':field,
                'visible_battle_count':len(br),'visible_battle_ids':sorted({x for z in br if (x:=battle_id(z))})})
    return sorted(out,key=lambda r:(r['snapshot_epoch'],r['agent_id']))

def build_intervals(rows):
    by=collections.defaultdict(list)
    for r in rows:by[r['agent_id']].append(r)
    out=[]
    for aid,rs in by.items():
        rs.sort(key=lambda r:r['snapshot_epoch'])
        for x,y in zip(rs,rs[1:]):
            ds=y['score']-x['score'];dr=None if x['rank'] is None or y['rank'] is None else y['rank']-x['rank']
            advanced=x['update_epoch'] is not None and y['update_epoch'] is not None and y['update_epoch']>x['update_epoch'];regressed=x['update_epoch'] is not None and y['update_epoch'] is not None and y['update_epoch']<x['update_epoch']
            xb,yb=set(x['visible_battle_ids']),set(y['visible_battle_ids']);delta=None if x['lifetime_battle_count'] is None or y['lifetime_battle_count'] is None else y['lifetime_battle_count']-x['lifetime_battle_count'];changed=abs(ds)>1e-12
            out.append({'agent_id':aid,'user_id':y['user_id'],'pseudo':y['pseudo'],'from_snapshot':x['snapshot_id'],'to_snapshot':y['snapshot_id'],
                'elapsed_days':(y['snapshot_epoch']-x['snapshot_epoch'])/86400,'age_before_days':x['age_days'],'age_after_days':y['age_days'],'age_bin_before':x['age_bin'],'age_bin_after':y['age_bin'],
                'score_before':x['score'],'score_after':y['score'],'score_delta':ds,'rank_before':x['rank'],'rank_after':y['rank'],'rank_delta':dr,
                'score_changed':changed,'update_advanced':advanced,'update_regressed':regressed,'score_changed_without_update_advance':changed and not advanced,
                'update_advanced_without_score_change':advanced and not changed,'rank_only_movement':not changed and dr not in (None,0),
                'crossed_age_bin':x['age_bin']!=y['age_bin'] and None not in (x['age_bin'],y['age_bin']),'lifetime_battle_count_delta':delta,
                'visible_new_battle_ids':len(yb-xb),'visible_dropped_battle_ids':len(xb-yb)})
    return out

def battle_summary(snaps):
    lengths=[];fields=collections.Counter();time_rows=0
    for s in snaps:
        for rs in s['battles'].values():
            lengths.append(len(rs))
            for r in rs:
                fields.update(r.keys());time_rows+=any(ts(r.get(k)) for k in TIME_KEYS)
    return {'battle_lists':len(lengths),'visible_rows':sum(lengths),'list_length_min':min(lengths) if lengths else None,
        'list_length_median':statistics.median(lengths) if lengths else None,'list_length_max':max(lengths) if lengths else None,
        'raw_top_level_field_counts':dict(sorted(fields.items())),'rows_with_any_timestamp':time_rows,
        'lifetime_count_status':'right_censored recent list unless a separate invariant leaderboard count is present'}

def field_inventory(snaps):
    out={}
    for s in snaps:
        rs=users(s['leaderboard']);out[s['id']]={'leaderboard_top_level_fields':sorted({k for r in rs for k in r}),'rows':len(rs),
            'creationTime_rows':sum(ts(first(r,('creationTime','creation_time','createdAt','created_at'))) is not None for r in rs),
            'updateTime_rows':sum(ts(first(r,('updateTime','update_time','updatedAt','updated_at'))) is not None for r in rs),
            'lifetime_count_fields':dict(collections.Counter(k for r in rs for k in COUNT_KEYS if num(r.get(k)) is not None))}
    return out
