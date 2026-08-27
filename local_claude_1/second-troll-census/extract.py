import gzip, json, collections, sys, time
path='/home/tarstars/prj/troll_farm/data/processed/turns.jsonl.gz'
first = {}                      # (gameId, seat) -> (turn, args, agentId, name)
trains_per_seat = collections.Counter()
games_by_agent = collections.Counter()
n=0; t0=time.time()
with gzip.open(path,'rt') as fh:
    for line in fh:
        n+=1
        is_t1 = '"turn":1,' in line
        has_tr = '"TRAIN"' in line
        if not (is_t1 or has_tr): continue
        r=json.loads(line)
        if is_t1: games_by_agent[(r['agentId'], r['name'])]+=1
        if not has_tr: continue
        for c in r['cmds']:
            if c['verb']=='TRAIN':
                key=(r['gameId'], r['seat']); trains_per_seat[key]+=1
                if key not in first: first[key]=(r['turn'], tuple(c['args']), r['agentId'], r['name'])
agg=collections.defaultdict(lambda: {'games':0,'trained':0,'turns':[], 'args':collections.Counter(), 'hp_pos':0, 'third':0})
for k,g in games_by_agent.items(): agg[k]['games']=g
for key,(turn,args,aid,name) in first.items():
    a=agg[(aid,name)]; a['trained']+=1; a['turns'].append(turn); a['args'][' '.join(args)]+=1
    if len(args)>=3 and args[2].lstrip('-').isdigit() and int(args[2])>0: a['hp_pos']+=1
    if trains_per_seat[key]>=2: a['third']+=1
out={}
for (aid,name),a in agg.items():
    t=sorted(a['turns']); med=t[len(t)//2] if t else None
    out[f"{aid}|{name}"]={'games':a['games'],'trained':a['trained'],'median_first_train_turn':med,'mean_first_train_turn': (sum(t)/len(t) if t else None),'hp_positive':a['hp_pos'],'seats_with_2plus_trains':a['third'],'top_args':a['args'].most_common(8)}
json.dump(out, open('train-census.json','w'), indent=1)
print('rows',n,'game-seats',sum(games_by_agent.values()),'seats that trained',len(first),'secs',round(time.time()-t0))
