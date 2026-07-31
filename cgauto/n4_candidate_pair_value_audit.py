#!/usr/bin/env python3
"""N4 Phase A: materialize the exact resident probe and analyze its pair surface."""
from __future__ import annotations
import argparse, base64, csv, hashlib, json, math, zlib
from pathlib import Path
from typing import Any, Iterable

REPO=Path(__file__).resolve().parents[1]
RESIDENT=REPO/"rust/src/d171a_control_resident_snapshot.rs"
RESIDENT_SHA256="fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f"
EXPECTED_GAMES=2048; ELIGIBLE_FLOOR=103; BOUNDARY_FLOOR=41
FAMILY_FLOOR=6; SEAT_SHARE_FLOOR=.30; LATENCY_P95_MS=5.0
PAYLOAD_SOURCE=REPO/"rust/src/bin/n4_candidate_pair_surface.rs"

def payload(name:str)->str:
    text=PAYLOAD_SOURCE.read_text(); begin=f"// N4_{name}_B85_BEGIN\n"; end=f"// N4_{name}_B85_END"
    body=text.split(begin,1)[1].split(end,1)[0]
    return "".join(line.removeprefix("// ").strip() for line in body.splitlines())

def unpack(value:str)->str:
    return zlib.decompress(base64.b85decode(value)).decode()

def probe_source()->str:return unpack(payload("PROBE"))
def runner_source()->str:return unpack(payload("RUNNER"))

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""): h.update(block)
    return h.hexdigest()

def replace_once(text:str,old:str,new:str,label:str)->str:
    n=text.count(old)
    if n!=1: raise ValueError(f"{label}: expected one anchor, found {n}")
    return text.replace(old,new,1)

def instrument_resident(source:str)->str:
    source=source.removeprefix("#![allow(dead_code, unused_imports)]\n")
    candidate="""        #[derive(Clone, Debug)]
        struct Candidate {
            command: String,
            score: f64,
            target: Target,
        }
"""
    source=replace_once(source,candidate,candidate+probe_source(),"probe types")
    field="            banana_factory_worker_three_bridge_post_training_commands: usize,\n"
    source=replace_once(source,field,field+"            n4_forced_pair: Option<Vec<String>>,\n","forced field")
    init="                    banana_factory_worker_three_bridge_post_training_commands: 0,\n"
    source=replace_once(source,init,init+"                    n4_forced_pair: None,\n","forced init")
    method="            pub fn fresh_harvest_regeneration_telemetry(\n"
    added="""            pub fn n4_force_pair(&mut self, commands: Vec<String>) {
                self.n4_forced_pair = Some(commands);
            }
"""
    source=replace_once(source,method,added+method,"forced method")
    select="""                let tree_targets = Self::tree_targets_by_command(&by_id);
                let mut selected = MoisanBot::select(by_id, &view.inventories[0]);
"""
    hooked="""                let n4_candidates = by_id.clone();
                let tree_targets = Self::tree_targets_by_command(&by_id);
                let mut selected = self.n4_forced_pair.take()
                    .unwrap_or_else(|| MoisanBot::select(by_id, &view.inventories[0]));
                let n4_selected_pre = selected.clone();
"""
    source=replace_once(source,select,hooked,"selection hook")
    final="""                self.remember_selected_regeneration(view, &selected);
                self.apply_opponent_crop_harvest_contact(view, &mut selected);
                self.remember_own_plant_attempts(view, &selected);
                if let Some(farmer_id) = scarce_farmer_id {
                    self.regeneration_commitments.remove(&farmer_id);
                }
                out.extend(selected);
                if out.is_empty() {
"""
    publish="""                self.remember_selected_regeneration(view, &selected);
                self.apply_opponent_crop_harvest_contact(view, &mut selected);
                self.remember_own_plant_attempts(view, &selected);
                if let Some(farmer_id) = scarce_farmer_id {
                    self.regeneration_commitments.remove(&farmer_id);
                }
                N4_LAST_PROBE.with(|slot| {
                    *slot.borrow_mut() = Some(N4Probe::capture(
                        view, &n4_candidates, &view.inventories[0],
                        &self.inner.opponent_crops, &n4_selected_pre, &selected,
                    ));
                });
                out.extend(selected);
                if out.is_empty() {
"""
    return replace_once(source,final,publish,"probe publication live path")

def materialize(args:argparse.Namespace)->int:
    actual=sha256_file(args.resident)
    if actual!=RESIDENT_SHA256: raise SystemExit(f"resident hash mismatch: {actual}")
    resident=instrument_resident(args.resident.read_text()); runner=runner_source()
    for path,text in ((args.resident_output,resident),(args.runner_output,runner)):
        path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text)
    print(json.dumps({"resident_sha256":actual,"instrumented_sha256":hashlib.sha256(resident.encode()).hexdigest(),"runner_sha256":hashlib.sha256(runner.encode()).hexdigest()},sort_keys=True))
    return 0

def decode_field(value:str)->str:
    out=bytearray(); data=value.encode("ascii"); i=0
    while i<len(data):
        if data[i]==37 and i+2<len(data): out.append(int(data[i+1:i+3],16)); i+=3
        else: out.append(data[i]); i+=1
    return out.decode()

def split_encoded(value:str)->list[str]:
    return [] if not value else [decode_field(x) for x in value.split(";")]

def load_frozen_commands(path:Path):
    commands={}; tasks=set()
    with path.open() as stream:
        for number,line in enumerate(stream,1):
            if not line.strip(): continue
            record=json.loads(line)
            if record.get("arm")!="referee": raise ValueError(f"line {number}: non-referee")
            task=(int(record["seed"]),int(record["seat"]),int(record["opp"]))
            if task in tasks: raise ValueError(f"duplicate task {task}")
            tasks.add(task); key="c0" if task[1]==0 else "c1"
            for turn,row in enumerate(record[key],1): commands[(*task,turn)]=[x.strip() for x in row if x.strip()]
    return commands,{"tasks":len(tasks),"command_turns":len(commands)}

def percentile(values:list[float],fraction:float)->float:
    if not values:return math.inf
    values=sorted(values); return values[max(0,min(len(values)-1,math.ceil(fraction*len(values))-1))]

def truth(value:str)->bool:return value in {"1","true","True"}

def analyze_rows(rows:Iterable[dict[str,str]],frozen:dict)->dict[str,Any]:
    by_task={}; observed=set(); failures=[]; states=set(); blobs=set(); boundaries=set(); latencies={}
    leaked=False; distinct=separate=0
    boundary_fields=("boundary_bank","boundary_tree","boundary_collision","boundary_disappearance","boundary_route_order")
    overlap_fields=("overlap_move_residual","overlap_threatened_crop","overlap_d163_d168","overlap_primitive_mutation","overlap_static_option")
    for raw in rows:
        task=tuple(int(raw[x]) for x in ("seed","seat","opp")); observed.add(task)
        leaked|=truth(raw.get("terminal_margin_used_for_eligibility","0"))
        if raw.get("row_type","pair")=="task":continue
        turn=int(raw["turn"]); state=(*task,turn); states.add(state)
        if raw.get("candidates_blob",""):blobs.add(state)
        exact=(frozen.get(state)==split_encoded(raw["live_full"]) and truth(raw.get("probe_present","0")) and truth(raw.get("live_pair_found","0")))
        if not exact and len(failures)<20:failures.append(list(state))
        latencies.setdefault(state,float(raw["latency_us"])/1000)
        boundary=any(truth(raw[x]) for x in boundary_fields)
        if boundary:boundaries.add(task)
        overlap=any(truth(raw[x]) for x in overlap_fields)
        potential=(int(raw["pair_count"])>=2 and not truth(raw["is_live"]) and truth(raw["semantic_distinct"]) and boundary and exact)
        if potential:distinct+=1; separate+=int(not overlap)
        by_task.setdefault(task,[]).append({"turn":turn,"eligible":potential and not overlap})
    eligible={task:min((r for r in rs if r["eligible"]),key=lambda r:r["turn"]) for task,rs in by_task.items() if any(r["eligible"] for r in rs)}
    family={}; seat={}
    for _,s,o in eligible:family[o]=family.get(o,0)+1; seat[s]=seat.get(s,0)+1
    count=len(eligible); shares={str(s):(seat.get(s,0)/count if count else 0) for s in (0,1)}
    complete=len(observed)==EXPECTED_GAMES and len({key[:3] for key in frozen})==EXPECTED_GAMES
    p95=percentile(list(latencies.values()),.95)
    closes={
      "eligible_games_below_103":count<ELIGIBLE_FLOOR,
      "boundary_games_below_41":len(boundaries)<BOUNDARY_FLOOR,
      "not_distinct_from_consumed_grammar":distinct>0 and separate==0,
      "live_reconstruction_not_exact":bool(failures),
      "latency_p95_above_5ms":p95>LATENCY_P95_MS,
      "eligible_families_below_6":len(family)<FAMILY_FLOOR,
      "seat_share_below_30pct":any(v<SEAT_SHARE_FLOOR for v in shares.values()),
      "source_or_outcome_integrity_failure":not complete or leaked or blobs!=states,
    }
    triggered=[k for k,v in closes.items() if v]
    if not triggered:verdict="SURFACE_CLEARED_FOR_PHASE_B"
    elif closes["source_or_outcome_integrity_failure"] or closes["live_reconstruction_not_exact"]:verdict="UNIDENTIFIABLE"
    elif closes["latency_p95_above_5ms"]:verdict="RUNTIME_CLOSE"
    elif closes["not_distinct_from_consumed_grammar"]:verdict="NOT_DISTINCT"
    else:verdict="SURFACE_TOO_SPARSE"
    return {"schema":"troll-farm-n4-candidate-pair-phase-a-v1","verdict":verdict,"hard_closes":closes,"triggered_closes":triggered,
      "counts":{"expected_games":EXPECTED_GAMES,"observed_games":len(observed),"natural_two_worker_states":len(states),"eligible_games":count,"boundary_games":len(boundaries),"eligible_families":len(family),"eligible_by_family":{str(k):v for k,v in sorted(family.items())},"eligible_by_seat":{str(k):v for k,v in sorted(seat.items())},"seat_shares":shares,"reconstruction_failures":len(failures),"candidate_blob_states":len(blobs),"state_rows":len(states),"distinct_boundary_pairs":distinct,"distinct_nonoverlap_pairs":separate},
      "latency":{"p95_ms":p95,"observations":len(latencies)},"reconstruction_failure_examples":failures,"outcome_influenced_eligibility":leaked,"phase_b_authorized":False}

def analyze(args:argparse.Namespace)->int:
    frozen,summary=load_frozen_commands(args.trajectories)
    with args.surface.open(newline="") as f:rows=list(csv.DictReader(f,delimiter="\t"))
    result=analyze_rows(rows,frozen)
    result["source"]={"trajectory_path":str(args.trajectories),"trajectory_sha256":sha256_file(args.trajectories),"surface_path":str(args.surface),"surface_sha256":sha256_file(args.surface),**summary}
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"verdict":result["verdict"],"eligible_games":result["counts"]["eligible_games"],"boundary_games":result["counts"]["boundary_games"],"p95_ms":result["latency"]["p95_ms"]},sort_keys=True))
    return 0 if result["verdict"]=="SURFACE_CLEARED_FOR_PHASE_B" else 2

def self_test()->None:
    fixture="""        #[derive(Clone, Debug)]
        struct Candidate {
            command: String,
            score: f64,
            target: Target,
        }
            banana_factory_worker_three_bridge_post_training_commands: usize,
                    banana_factory_worker_three_bridge_post_training_commands: 0,
            pub fn fresh_harvest_regeneration_telemetry(
                let tree_targets = Self::tree_targets_by_command(&by_id);
                let mut selected = MoisanBot::select(by_id, &view.inventories[0]);
                out.extend(selected);
                if out.is_empty() {
                    out.push("WAIT".to_string());
                }
                self.remember_selected_regeneration(view, &selected);
                self.apply_opponent_crop_harvest_contact(view, &mut selected);
                self.remember_own_plant_attempts(view, &selected);
                if let Some(farmer_id) = scarce_farmer_id {
                    self.regeneration_commitments.remove(&farmer_id);
                }
                out.extend(selected);
                if out.is_empty() {
"""
    transformed=instrument_resident(fixture)
    assert "pub struct N4Probe" in transformed and "n4_forced_pair" in transformed
    assert transformed.count("N4_LAST_PROBE.with(|slot| {") == 1
    assert transformed.count(
        "N4_LAST_PROBE.with(|slot| *slot.borrow_mut() = None);"
    ) == 1
    assert transformed.count(
        "N4_LAST_PROBE.with(|slot| slot.borrow_mut().take())"
    ) == 1
    assert transformed.count("out.extend(selected);") == 2
    assert decode_field("MOVE%201%202%203")=="MOVE 1 2 3"
    frozen={}; rows=[]
    for seed in range(1,EXPECTED_GAMES+1):
        seat=seed%2; opp=seed%8; frozen[(seed,seat,opp,1)]=["WAIT","WAIT"]
        rows.append({"row_type":"pair","seed":str(seed),"seat":str(seat),"opp":str(opp),"turn":"1","live_full":"WAIT;WAIT","latency_us":"1000","pair_count":"2","probe_present":"1","live_pair_found":"1","is_live":"0","semantic_distinct":"1","candidates_blob":"x","boundary_bank":"1","boundary_tree":"0","boundary_collision":"0","boundary_disappearance":"0","boundary_route_order":"0","overlap_move_residual":"0","overlap_threatened_crop":"0","overlap_d163_d168":"0","overlap_primitive_mutation":"0","overlap_static_option":"0"})
    assert analyze_rows(rows,frozen)["verdict"]=="SURFACE_CLEARED_FOR_PHASE_B"
    assert analyze_rows(rows[:10],{k:v for k,v in frozen.items() if k[0]<=10})["verdict"]=="UNIDENTIFIABLE"
    assert "fn main()" in runner_source()
    print("self-test: ok")

def main()->int:
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command",required=True)
    m=sub.add_parser("materialize"); m.add_argument("--resident",type=Path,default=RESIDENT); m.add_argument("--resident-output",type=Path,required=True); m.add_argument("--runner-output",type=Path,required=True); m.set_defaults(func=materialize)
    a=sub.add_parser("analyze"); a.add_argument("--trajectories",type=Path,required=True); a.add_argument("--surface",type=Path,required=True); a.add_argument("--output",type=Path,required=True); a.set_defaults(func=analyze)
    s=sub.add_parser("self-test"); s.set_defaults(func=lambda _:(self_test() or 0))
    args=p.parse_args(); return args.func(args)
if __name__=="__main__":raise SystemExit(main())
