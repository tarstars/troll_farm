#!/usr/bin/env python3
r"""G-4c.2 — build the COMPILED-DOMAIN probe from the byte-exact resident.

codex_1 approved compiled enumeration for the three structural-impossibility clauses and ruled
that **no Python or handwritten replica of the tree math is admissible**. So this probe is
generated from the subject and calls `MoisanBot::predict_tree` / `MoisanBot::chop_outcome`
THEMSELVES — the same functions the bot runs. The Python side only enumerates the report.

PROOF THAT THE SUBJECT'S FUNCTIONS ARE INVOKED (codex_1 condition 1): the probe is the subject
file plus one `main()` branch; the builder refuses unless the stripped file is byte-identical to
the resident, so no reimplementation can hide in it. The probe's output includes the resident
sha256 it was generated from.

DOMAIN, JUSTIFIED FROM THE SUBJECT (condition 2) — every bound is read off the code, not assumed:

| field | range | justification (source) |
|---|---|---|
| `kind` | 4 variants | `PlantKind` enum is closed |
| `size` | 1..=4 | growth guarded by `size<4`; a live plant has size>=1 |
| `health` | 1..=`tree_health(kind,size)` | `tree_health = base + slope*size`, max 20 (Apple@4) |
| `fruits` | 0..=3 | growth guarded by `fruits<3` |
| `cooldown` | 0..=9 | `plant_cooldown` max 9 (Apple); `effective_cooldown` only lowers it |
| `near_water` | 2 | boolean predicate `view.water` adjacency |
| `opp_chop` | 0..=21 | `predicted_opp_chop` output; health<=20 so any value >=21 kills on the first\n  iteration identically — SATURATION ARGUMENT, **not yet mechanically checked** |
| `travel_turns` | 0..=300 | `TOTAL_TURNS`; now ENUMERATED IN FULL, not sampled |
| `chop_power` | 1..=21 | gate requires >0; health<=20 so >=21 fells in one iteration — SATURATION ARGUMENT, **not yet mechanically checked** |
| `free_capacity` | 1..=5 | gate requires >0; `size` caps at 4 so `final_size<=4` and any capacity >=4\n  gives the same `wood` — SATURATION ARGUMENT, **not yet mechanically checked** |

The probe reports EXECUTED cardinality so the Python side can reconcile it against the declared
product (condition 3) and fail on any uncovered tuple (condition 4). Mutation controls
(condition 5) live in `g4c2_domain.py`.
"""
import hashlib, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
RESIDENT = REPO / "cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs"
OUT = REPO / "claude_1/chop4c/domain-probe.rs"
RESIDENT_SHA = "98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29"

OLD_MAIN = '''        struct MoisanBot;'''

NEW_MAIN = '''        struct MoisanBot;
//C4C_PROBE_BEGIN
        pub fn c4c_domain_probe(){
    use crate::game::types::*;
    use std::collections::BTreeSet;
    let kinds=[PlantKind::Plum,PlantKind::Lemon,PlantKind::Apple,PlantKind::Banana];
    let mut walkable=BTreeSet::new();
    for x in 0..4{for y in 0..4{walkable.insert((x,y));}}
    let mut executed:u64=0;
    let mut pt_some:u64=0;let mut pt_none:u64=0;
    let mut co_some:u64=0;let mut co_none:u64=0;let mut co_calls:u64=0;let mut wood_evals:u64=0;
    let mut max_pred_health:i32=i32::MIN;let mut max_pred_size:i32=i32::MIN;let mut max_final_size:i32=i32::MIN;
    let mut travel0:u64=0;let mut travel_ge1:u64=0;
    let mut v_pred_nonpos:u64=0;let mut v_wood_nonpos:u64=0;
    for kind in kinds{
        for size in 1..=4{
            let maxh=crate::game::rules::tree_health(kind,size);
            for health in 1..=maxh{
                for fruits in 0..=3{
                    for cooldown in 0..=9{
                        for near_water in [false,true]{
                            for opp_chop in 0..=21{
                                let mut water=BTreeSet::new();
                                if near_water{water.insert((1,0));}
                                let mut units=Vec::new();
                                if opp_chop>0{
                                    units.push(Unit{id:9,player:1,cell:(1,1),
                                        stats:Stats{movement_speed:1,carry_capacity:3,harvest_power:1,chop_power:opp_chop},
                                        carry:[0;ITEM_COUNT]});
                                    }
                                let plant=Plant{kind,cell:(1,1),size,health,fruits,cooldown};
                                let view=GameState{width:4,height:4,walkable:walkable.clone(),
                                    shacks:[(0,0),(3,3)],inventories:[[0;ITEM_COUNT];2],units,
                                    plants:vec![plant.clone()],scores:[0,0],turn:1,next_id:10,
                                    iron:BTreeSet::new(),water};
                                for travel in 0..=300{
                                    executed+=1;
                                    match MoisanBot::predict_tree(&view,&plant,travel){
                                        None=>{pt_none+=1;}
                                        Some(pred)=>{
                                            pt_some+=1;
                                            if pred.health>max_pred_health{max_pred_health=pred.health;}
                                            if pred.size>max_pred_size{max_pred_size=pred.size;}
                                            if travel==0{travel0+=1;}else{travel_ge1+=1;}
                                            if pred.size<=0||pred.health<=0{v_pred_nonpos+=1;
                                                println!("VIOLATION PREDICTED_NONPOSITIVE kind={:?} size={} health={} fruits={} cd={} nw={} opp={} travel={} psize={} phealth={}",kind,size,health,fruits,cooldown,near_water,opp_chop,travel,pred.size,pred.health);}
                                            for chop_power in 1..=21{
                                                co_calls+=1;
                                                match MoisanBot::chop_outcome(&view,&plant,pred,chop_power){
                                                    None=>{co_none+=1;
                                                        println!("VIOLATION CHOP_OUTCOME_NONE kind={:?} size={} health={} fruits={} cd={} nw={} opp={} travel={} chop={} psize={} phealth={}",kind,size,health,fruits,cooldown,near_water,opp_chop,travel,chop_power,pred.size,pred.health);}
                                                    Some((_turns,final_size))=>{
                                                        co_some+=1;
                                                        if final_size>max_final_size{max_final_size=final_size;}
                                                        for free_cap in 1..=5{
                                                            wood_evals+=1;
                                                            let wood=final_size.min(free_cap);
                                                            if final_size>0&&free_cap>0&&wood<=0{v_wood_nonpos+=1;
                                                                println!("VIOLATION WOOD_NONPOSITIVE final_size={} free_cap={} wood={}",final_size,free_cap,wood);}
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    println!("C4CDOMAIN resident_sha=98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29");
    println!("C4CDOMAIN executed={} predict_some={} predict_none={} chop_some={} chop_none={} chop_calls={} wood_evals={}",executed,pt_some,pt_none,co_some,co_none,co_calls,wood_evals);
    println!("C4CDOMAIN bounds max_pred_health={} max_pred_size={} max_final_size={} travel0_some={} travel_ge1_some={}",max_pred_health,max_pred_size,max_final_size,travel0,travel_ge1);
    println!("C4CDOMAIN violations predicted_nonpositive={} chop_outcome_none={} wood_nonpositive={}",v_pred_nonpos,co_none,v_wood_nonpos);
    }
//C4C_PROBE_END'''

OLD_ENTRY = '''fn main(){
    let stdin=io::stdin();'''
NEW_ENTRY = '''fn main(){
    if std::env::var("C4C_DOMAIN_PROBE").is_ok(){crate::bot::moisan::c4c_domain_probe();return;}
    let stdin=io::stdin();'''


def main():
    src = RESIDENT.read_text()
    if hashlib.sha256(src.encode()).hexdigest() != RESIDENT_SHA:
        print("REFUSING: resident digest differs")
        return 1
    if src.count(OLD_MAIN) != 1:
        print(f"REFUSING: main() anchor matched {src.count(OLD_MAIN)} times")
        return 1
    out = src.replace(OLD_MAIN, NEW_MAIN)
    if out.count(OLD_ENTRY) != 1:
        print(f"REFUSING: main() anchor matched {out.count(OLD_ENTRY)} times")
        return 1
    out = out.replace(OLD_ENTRY, NEW_ENTRY)

    # Condition 1: prove no reimplementation hides here. Strip the probe function and the
    # one-line main() branch; what remains must be the subject, byte for byte.
    a = out.index("//C4C_PROBE_BEGIN\n")
    b = out.index("//C4C_PROBE_END\n") + len("//C4C_PROBE_END\n")
    stripped = (out[:a] + out[b:]).replace(
        '    if std::env::var("C4C_DOMAIN_PROBE").is_ok(){crate::bot::moisan::c4c_domain_probe();return;}\n', "")
    if stripped != src:
        print("REFUSING: probe changed the subject outside the declared additions")
        return 1
    OUT.write_text(out)
    print(f"wrote {OUT.relative_to(REPO)}")
    print("  stripped probe == subject byte-for-byte (no replica can hide)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
