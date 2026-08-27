#!/usr/bin/env python3
"""Read the banana farm's v8 telemetry tokens (fs fp fh fl fd fe fw) out of a collected ladder package
and summarise the 160 games -- written 2026-08-27 for the farm's one-hour viewing (submission 41201668).

The package is what `local_claude_1/narrate/collect_submission_games.py` writes: one replay per line,
`agents[i].agentId` gives our seat, `frames[k].stdout` (for frames with `agentId == seat`) carries our
output including the `MSG NARRATE v8 ...` line. The same pattern reads any collected package; only the
regex is farm-specific. Run from the repo root: python3 local_claude_1/farm-watch/farm_decode.py
"""
import gzip, json, re, collections, statistics
p='local_claude_1/farm-watch/games-41201668/games-agent6667061-submission41201668.jsonl.gz'
ME=6667061
pat=re.compile(r"NARRATE v8 t=(\d+) fs=(\d) fp=(\d+) fh=(\d+) fl=(\d+) fd=(\S) fe=(\d+) fw=(\d+)")
rows=[]
with gzip.open(p,'rt') as f:
    for line in f:
        g=json.loads(line)
        seat=[a['index'] for a in g['agents'] if a['agentId']==ME][0]
        opp=1-seat
        margin=g['scores'][seat]-g['scores'][opp]
        first_deny=None; first_farm=None; last=None; turns=0
        for fr in g['frames']:
            if fr.get('agentId')!=seat: continue
            m=pat.search(fr.get('stdout') or '')
            if not m: continue
            t,fs,fp,fh,fl,fd,fe,fw=m.groups()
            t=int(t); fs=int(fs)
            if fs>=1 and first_deny is None: first_deny=t
            if fs>=2 and first_farm is None: first_farm=t
            last=(t,fs,int(fp),int(fh),int(fl),fd,int(fe),int(fw)); turns+=1
        rows.append((g['gameId'],seat,margin,g['scores'][seat],g['scores'][opp],first_deny,first_farm,last,turns))
n=len(rows); wins=sum(1 for r in rows if r[2]>0)
print(f"games {n}  wins {wins}  losses {n-wins}  mean margin {statistics.mean(r[2] for r in rows):.1f}  mean own {statistics.mean(r[3] for r in rows):.1f}  mean opp {statistics.mean(r[4] for r in rows):.1f}")
decoded=[r for r in rows if r[7]]
print(f"games with a decoded v8 line: {len(decoded)}")
fd=collections.Counter(r[7][5] for r in decoded); print("denial end reason:", dict(fd))
fs=collections.Counter(r[7][1] for r in decoded); print("final state:", dict(fs))
dl=[r[6]-r[5] for r in decoded if r[5] is not None and r[6] is not None]
print(f"denial length (turns): n={len(dl)} mean {statistics.mean(dl):.1f} median {statistics.median(dl)} max {max(dl) if dl else '-'}; zero-length {sum(1 for d in dl if d==0)}")
fdn=[r[5] for r in decoded if r[5] is not None]; print(f"deny entered at turn: mean {statistics.mean(fdn):.1f} median {statistics.median(fdn)}")
fp=[r[7][2] for r in decoded]; fh=[r[7][3] for r in decoded]
print(f"farm plants/game: mean {statistics.mean(fp):.1f} median {statistics.median(fp)} max {max(fp)}  games with 0 plants: {sum(1 for x in fp if x==0)}")
print(f"mother harvests/game: mean {statistics.mean(fh):.1f} median {statistics.median(fh)} max {max(fh)}  games with 0: {sum(1 for x in fh if x==0)}")
print("latch fired:", sum(1 for r in decoded if r[7][4]>0), "games")
fe=[r[7][6] for r in decoded]; fw=[r[7][7] for r in decoded]
print(f"enemy chop hits on ring (fe): mean {statistics.mean(fe):.1f}; own ring work (fw): mean {statistics.mean(fw):.1f}")
# margin by plants
hi=[r[2] for r in decoded if r[7][2]>=8]; lo=[r[2] for r in decoded if r[7][2]<8]
print(f"margin when plants>=8: n={len(hi)} mean {statistics.mean(hi) if hi else 0:.1f}; plants<8: n={len(lo)} mean {statistics.mean(lo) if lo else 0:.1f}")
big=[r for r in decoded if r[2]<=-150]; print(f"losses by >=150: {len(big)}; their plants mean {statistics.mean(r[7][2] for r in big) if big else 0:.1f}, harvests mean {statistics.mean(r[7][3] for r in big) if big else 0:.1f}, opp score mean {statistics.mean(r[4] for r in big) if big else 0:.0f}")
