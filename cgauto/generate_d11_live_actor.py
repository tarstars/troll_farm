#!/usr/bin/env python3
"""Generate the frozen referee-facing D11 K2 actor integration source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from cgauto.generate_d11_actor_rust import KERNEL_END
from cgauto.generate_d11_actor_rust_k2 import generate_optimized_source


PROTOCOL_SHA256 = "f7d05facb1f5fffd08f484a72ce58b6604d91e165451c2b5e67f0da0fe703fb7"


TYPES_NAV_PARSER = r'''
// BEGIN_LIVE_TYPES_NAV_PARSER
use std::collections::VecDeque;

const RECIPES:[[i8;4];8]=[[1,1,1,1],[1,2,1,1],[2,2,1,1],[2,2,2,1],[1,3,0,1],[1,2,0,2],[2,2,0,2],[2,3,1,2]];

#[derive(Clone)]
struct Plant{k:usize,x:usize,y:usize,size:i32,health:i32,fruits:i32,cd:i32}
#[derive(Clone)]
struct Unit{id:i32,p:usize,x:usize,y:usize,ms:i32,cc:i32,hp:i32,chop:i32,carry:[i32;6]}
impl Unit{fn free(&self)->i32{self.cc-self.carry.iter().sum::<i32>()}}
struct State{inv:[[i32;6];2],plants:Vec<Plant>,units:Vec<Unit>,turn:usize}
impl State{
    fn plant_at(&self,x:usize,y:usize)->Option<&Plant>{self.plants.iter().find(|p|p.x==x&&p.y==y)}
    fn unit(&self,id:i32)->Option<&Unit>{self.units.iter().find(|u|u.id==id)}
    fn own(&self)->Vec<usize>{
        let mut out:Vec<usize>=(0..self.units.len()).filter(|&i|self.units[i].p==0).collect();
        out.sort_by_key(|&i|self.units[i].id);out
    }
    fn score(&self,p:usize)->i32{self.inv[p][0]+self.inv[p][1]+self.inv[p][2]+self.inv[p][3]+4*self.inv[p][5]}
}

struct Map{
    w:usize,h:usize,walk:[bool;AREA],iron:[bool;AREA],iron_adj:[bool;AREA],water_adj:[bool;AREA],
    shack:[(usize,usize);2],dist:Vec<u8>,park:[usize;AREA]
}
impl Map{
    fn local(&self,x:usize,y:usize)->usize{y*self.w+x}
    fn pos(&self,c:usize)->(usize,usize){(c%self.w,c/self.w)}
    fn d(&self,from:(usize,usize),to:(usize,usize))->u8{
        self.dist[self.local(from.0,from.1)*AREA+self.local(to.0,to.1)]
    }
    fn home_distance(&self,from:(usize,usize))->u8{
        let (hx,hy)=self.shack[0];let mut best=240u8;
        for (dx,dy) in [(0i32,1i32),(1,0),(0,-1),(-1,0)]{
            let x=hx as i32+dx;let y=hy as i32+dy;
            if x>=0&&y>=0&&(x as usize)<self.w&&(y as usize)<self.h&&self.walk[self.local(x as usize,y as usize)]{
                best=best.min(self.d(from,(x as usize,y as usize)));
            }
        }best
    }
    fn build(w:usize,h:usize,rows:&[String])->Self{
        let mut walk=[false;AREA];let mut iron=[false;AREA];let mut water=[false;AREA];let mut shack=[(0,0);2];
        for (y,row) in rows.iter().enumerate(){for (x,ch) in row.chars().enumerate(){let c=y*w+x;match ch{
            '.'=>walk[c]=true,'+'=>iron[c]=true,'~'=>water[c]=true,'0'=>shack[0]=(x,y),'1'=>shack[1]=(x,y),_=>{}
        }}}
        let mut iron_adj=[false;AREA];let mut water_adj=[false;AREA];
        for y in 0..h{for x in 0..w{let c=y*w+x;if !iron[c]&&!water[c]{continue;}for (dx,dy) in [(0i32,1i32),(1,0),(0,-1),(-1,0)]{
            let nx=x as i32+dx;let ny=y as i32+dy;if nx>=0&&ny>=0&&(nx as usize)<w&&(ny as usize)<h{
                let n=ny as usize*w+nx as usize;if iron[c]{iron_adj[n]=true;}if water[c]{water_adj[n]=true;}
            }
        }}}
        let mut dist=vec![255u8;AREA*AREA];let mut sources:Vec<usize>=(0..w*h).filter(|&c|walk[c]).collect();
        sources.push(shack[0].1*w+shack[0].0);sources.push(shack[1].1*w+shack[1].0);
        let mut queue=VecDeque::new();
        for src in sources{let base=src*AREA;dist[base+src]=0;queue.clear();queue.push_back(src);
            while let Some(c)=queue.pop_front(){let d=dist[base+c];let (x,y)=(c%w,c/w);
                for (dx,dy) in [(0i32,1i32),(1,0),(0,-1),(-1,0)]{let nx=x as i32+dx;let ny=y as i32+dy;
                    if nx<0||ny<0||(nx as usize)>=w||(ny as usize)>=h{continue;}let n=ny as usize*w+nx as usize;
                    if !walk[n]||dist[base+n]!=255{continue;}dist[base+n]=d+1;queue.push_back(n);
                }
            }
        }
        let mut park=[0usize;AREA];for t in 0..w*h{if walk[t]{park[t]=t;continue;}let (tx,ty)=(t%w,t/w);let mut bd=usize::MAX;
            for c in 0..w*h{if !walk[c]{continue;}let (x,y)=(c%w,c/w);let d=x.abs_diff(tx)+y.abs_diff(ty);if d<bd{bd=d;park[t]=c;}}
        }
        Self{w,h,walk,iron,iron_adj,water_adj,shack,dist,park}
    }
}

fn line(reader:&mut impl BufRead)->Option<String>{let mut s=String::new();if reader.read_line(&mut s).ok()?==0{return None;}Some(s.trim_end_matches(['\n','\r']).to_string())}
fn numbers(s:&str)->Option<Vec<i32>>{s.split_whitespace().map(|v|v.parse().ok()).collect()}
fn read_map(reader:&mut impl BufRead)->Option<Map>{let h=numbers(&line(reader)?)?;if h.len()!=2{return None;}let mut rows=Vec::new();for _ in 0..h[1]{rows.push(line(reader)?);}Some(Map::build(h[0] as usize,h[1] as usize,&rows))}
fn kind(s:&str)->usize{match s{"PLUM"=>0,"LEMON"=>1,"APPLE"=>2,_=>3}}
fn read_state(reader:&mut impl BufRead,turn:usize)->Option<State>{
    let mut inv=[[0i32;6];2];for p in 0..2{let v=numbers(&line(reader)?)?;if v.len()!=6{return None;}inv[p].copy_from_slice(&v);}
    let np:usize=line(reader)?.parse().ok()?;let mut plants=Vec::with_capacity(np);for _ in 0..np{let s=line(reader)?;let f:Vec<&str>=s.split_whitespace().collect();if f.len()!=7{return None;}
        plants.push(Plant{k:kind(f[0]),x:f[1].parse().ok()?,y:f[2].parse().ok()?,size:f[3].parse().ok()?,health:f[4].parse().ok()?,fruits:f[5].parse().ok()?,cd:f[6].parse().ok()?});
    }
    let nu:usize=line(reader)?.parse().ok()?;let mut units=Vec::with_capacity(nu);for _ in 0..nu{let v=numbers(&line(reader)?)?;if v.len()!=14{return None;}let mut carry=[0;6];carry.copy_from_slice(&v[8..14]);
        units.push(Unit{id:v[0],p:v[1] as usize,x:v[2] as usize,y:v[3] as usize,ms:v[4],cc:v[5],hp:v[6],chop:v[7],carry});
    }Some(State{inv,plants,units,turn})
}
// END_LIVE_TYPES_NAV_PARSER
'''


OBSERVER_TRACKER = r'''
// BEGIN_LIVE_OBSERVER_TRACKER
fn spatial(x:usize,y:usize)->usize{y*W+x}
fn ai(plane:usize,x:usize,y:usize)->usize{plane*AREA+spatial(x,y)}
fn quant(value:f32,scale:f32)->u8{if scale<=0.0{0}else{(255.0*value/scale).round().clamp(0.0,255.0)as u8}}
fn fnv(data:&[u8])->u64{let mut h=0xcbf29ce484222325u64;for &b in data{h^=b as u64;h=h.wrapping_mul(0x100000001b3);}h}

struct Audit{oh:u64,mh:u64,action:usize,id:i32,command:String}
struct Controller{
    map:Map,target:[i8;4],actor:Actor,previous:u8,planned:(usize,usize),created:Option<(usize,usize)>,
    renewable:u8,score_at_training:Option<i32>,pending_plants:Vec<(usize,usize)>,pending_harvests:Vec<(i32,i32)>
}
impl Controller{
    fn choose_crop(map:&Map,state:&State)->Option<(usize,usize)>{let (hx,hy)=map.shack[0];let mut best=None;
        for y in 0..map.h{for x in 0..map.w{let c=map.local(x,y);let r=x.abs_diff(hx)+y.abs_diff(hy);
            if r==0||r>3||!map.walk[c]||state.plant_at(x,y).is_some(){continue;}let key=(!map.water_adj[c],r,y,x);
            if best.is_none()||key<best.unwrap(){best=Some(key);}
        }}best.map(|v:(bool,usize,usize,usize)|(v.3,v.2))
    }
    fn new(map:Map,target:[i8;4],state:&State)->Self{let planned=Self::choose_crop(&map,state).unwrap();Self{
        map,target,actor:Actor::new(),previous:0,planned,created:None,renewable:0,score_at_training:None,
        pending_plants:Vec::new(),pending_harvests:Vec::new()
    }}
    fn target_cost(&self)->[i32;6]{[1+(self.target[0]as i32).pow(2),1+(self.target[1]as i32).pow(2),1+(self.target[2]as i32).pow(2),0,1+(self.target[3]as i32).pow(2),0]}
    fn target_built(&self,state:&State)->bool{let own=state.own();if own.is_empty(){return false;}let starter=own[0];own.into_iter().any(|i|i!=starter&&{
        let u=&state.units[i];[u.ms as i8,u.cc as i8,u.hp as i8,u.chop as i8]==self.target
    })}
    fn affordable(&self,state:&State)->bool{let c=self.target_cost();(0..6).all(|i|state.inv[0][i]>=c[i])}
    fn crop_exists(&self,state:&State)->bool{self.created.is_some_and(|(x,y)|state.plant_at(x,y).is_some_and(|p|p.k==3))}
    fn resolve(&mut self,state:&State){
        if self.created.is_some()&&!self.crop_exists(state){self.created=None;}
        for (x,y) in self.pending_plants.drain(..){if state.plant_at(x,y).is_some_and(|p|p.k==3){self.created=Some((x,y));}}
        for (id,before) in self.pending_harvests.drain(..){if state.unit(id).is_some_and(|u|u.carry[3]>before){self.renewable=self.renewable.saturating_add(1);}}
        if self.created.is_none()&&state.plant_at(self.planned.0,self.planned.1).is_some(){if let Some(next)=Self::choose_crop(&self.map,state){self.planned=next;}}
        if self.score_at_training.is_none()&&self.target_built(state){self.score_at_training=Some(state.score(0));}
    }
    fn fill(&self,obs:&mut[u8],channel:usize,value:u8){for y in 0..self.map.h{for x in 0..self.map.w{obs[channel*AREA+spatial(x,y)]=value;}}}
    fn observe(&self,state:&State,ui:usize,phase:u8,obs:&mut[u8],mask:&mut[u8]){
        obs.fill(0);mask.fill(0);let unit=&state.units[ui];let(sx,sy)=(unit.x,unit.y);let selected=(sx,sy);
        for y in 0..self.map.h{for x in 0..self.map.w{let sc=spatial(x,y);let lc=self.map.local(x,y);let target=if self.map.walk[lc]{lc}else{self.map.park[lc]};let tp=self.map.pos(target);
            obs[sc]=255;obs[AREA+sc]=if self.map.walk[lc]{255}else{0};
            obs[2*AREA+sc]=255u8.saturating_sub(quant(self.map.d(selected,tp)as f32,40.0));
            obs[3*AREA+sc]=if self.map.iron_adj[lc]{255}else{0};obs[4*AREA+sc]=if self.map.water_adj[lc]{255}else{0};
            obs[103*AREA+sc]=255u8.saturating_sub(quant(self.map.home_distance(tp)as f32,40.0));
        }}
        for p in 0..2{let(x,y)=self.map.shack[p];obs[(5+p)*AREA+spatial(x,y)]=255;}obs[7*AREA+spatial(sx,sy)]=255;
        for u in &state.units{let sc=spatial(u.x,u.y);let own=u.p==0;obs[(if own{8}else{9})*AREA+sc]=255;let base=if own{10}else{15};
            obs[base*AREA+sc]=quant(u.ms as f32,3.0);obs[(base+1)*AREA+sc]=quant(u.cc as f32,4.0);obs[(base+2)*AREA+sc]=quant(u.hp as f32,3.0);
            obs[(base+3)*AREA+sc]=quant(u.chop as f32,4.0);obs[(base+4)*AREA+sc]=quant(u.free()as f32,4.0);let cb=if own{20}else{26};
            for item in 0..6{obs[(cb+item)*AREA+sc]=quant(u.carry[item]as f32,4.0);}
        }
        for p in &state.plants{let sc=spatial(p.x,p.y);let base=32+p.k*6;obs[base*AREA+sc]=255;obs[(base+1)*AREA+sc]=quant(p.size as f32,4.0);
            obs[(base+2)*AREA+sc]=quant(p.health as f32,20.0);obs[(base+3)*AREA+sc]=quant(p.fruits as f32,3.0);obs[(base+4)*AREA+sc]=quant(p.cd as f32,9.0);
            obs[(base+5)*AREA+sc]=if self.map.water_adj[self.map.local(p.x,p.y)]{255}else{0};
        }
        for item in 0..6{self.fill(obs,56+item,quant(state.inv[0][item]as f32,30.0));self.fill(obs,62+item,quant(state.inv[1][item]as f32,30.0));
            self.fill(obs,68+item,quant(unit.carry[item]as f32,4.0));}
        self.fill(obs,74,quant(unit.ms as f32,3.0));self.fill(obs,75,quant(unit.cc as f32,4.0));self.fill(obs,76,quant(unit.hp as f32,3.0));
        self.fill(obs,77,quant(unit.chop as f32,4.0));self.fill(obs,78,quant(unit.free()as f32,4.0));self.fill(obs,79,quant(self.map.home_distance(selected)as f32,40.0));
        let steps=(state.turn-1).min(240);self.fill(obs,80,quant(steps as f32,240.0));self.fill(obs,81,quant((240-steps)as f32,240.0));
        self.fill(obs,82,quant(state.score(0)as f32,400.0));self.fill(obs,83,quant(state.score(1)as f32,400.0));self.fill(obs,84,quant(state.own().len()as f32,6.0));
        self.fill(obs,85,quant(state.units.iter().filter(|u|u.p==1).count()as f32,6.0));for j in 0..4{self.fill(obs,86+j,quant(self.target[j]as f32,4.0));}
        if !self.target_built(state){let cost=self.target_cost();for (j,item) in [0usize,1,2,4].into_iter().enumerate(){self.fill(obs,90+j,quant(cost[item]as f32,20.0));
            self.fill(obs,94+j,quant((cost[item]-state.inv[0][item]).max(0)as f32,20.0));}
        }else{let gain=self.score_at_training.map(|s|state.score(0)-s).unwrap_or(0);self.fill(obs,90,quant(gain.max(0)as f32,40.0));
            self.fill(obs,91,quant((12-gain).max(0)as f32,12.0));self.fill(obs,92,if self.crop_exists(state){255}else{0});self.fill(obs,93,quant(self.renewable as f32,4.0));
            self.fill(obs,94,255);let starter=state.own()[0];self.fill(obs,95,if ui==starter{255}else{0});self.fill(obs,96,if ui!=starter{255}else{0});self.fill(obs,97,if phase==1{255}else{0});
        }
        self.fill(obs,98,if self.affordable(state){255}else{0});let home=self.map.shack[0];self.fill(obs,99,if state.units.iter().any(|u|(u.x,u.y)==home){255}else{0});
        self.fill(obs,100,if (0..4).any(|i|unit.carry[i]>0)||unit.carry[5]>0{255}else{0});let objective=self.created.unwrap_or(self.planned);
        self.fill(obs,101,quant(self.map.d(selected,objective)as f32,40.0));self.fill(obs,102,quant(self.previous as f32,12.0));
        mask[ai(0,sx,sy)]=1;for p in &state.plants{mask[ai(0,p.x,p.y)]=1;}mask[ai(0,home.0,home.1)]=1;mask[ai(0,self.planned.0,self.planned.1)]=1;
        for y in 0..self.map.h{for x in 0..self.map.w{let lc=self.map.local(x,y);if self.map.iron[lc]||(self.map.walk[lc]&&self.map.iron_adj[lc]){mask[ai(0,x,y)]=1;}}}
        let current=spatial(sx,sy);if let Some(p)=state.plant_at(sx,sy){if unit.hp>0&&unit.free()>0&&p.fruits>0{mask[AREA+current]=1;}if unit.chop>0{mask[2*AREA+current]=1;}}
        let near=sx.abs_diff(home.0)+sy.abs_diff(home.1)<=1;if near&&unit.carry.iter().sum::<i32>()>0{mask[3*AREA+current]=1;}
        if unit.chop>0&&unit.free()>0&&self.map.iron_adj[self.map.local(sx,sy)]{mask[4*AREA+current]=1;}
        if self.map.walk[self.map.local(sx,sy)]&&state.plant_at(sx,sy).is_none(){for item in 0..4{if unit.carry[item]>0{mask[(5+item)*AREA+current]=1;}}}
        if near&&unit.free()>0{for item in 0..4{if state.inv[0][item]>0{mask[(9+item)*AREA+current]=1;}}}
    }
// END_LIVE_OBSERVER_TRACKER
'''


COMMAND_MAIN = r'''
// BEGIN_LIVE_COMMAND_MAIN
    fn command(action:usize,u:&Unit)->String{let plane=action/AREA;let cell=action%AREA;let x=cell%W;let y=cell/W;match plane{
        0=>format!("MOVE {} {} {}",u.id,x,y),1=>format!("HARVEST {}",u.id),2=>format!("CHOP {}",u.id),3=>format!("DROP {}",u.id),4=>format!("MINE {}",u.id),
        5..=8=>format!("PLANT {} {}",u.id,["PLUM","LEMON","APPLE","BANANA"][plane-5]),9..=12=>format!("PICK {} {}",u.id,["PLUM","LEMON","APPLE","BANANA"][plane-9]),_=>"WAIT".to_string()
    }}
    fn phase(&mut self,state:&State,ui:usize,phase:u8)->Audit{let mut obs=vec![0u8;OBS_C*AREA];let mut mask=vec![0u8;ACTIONS];self.observe(state,ui,phase,&mut obs,&mut mask);
        let mut logits=vec![0.0f32;ACTIONS];self.actor.forward(&obs,&mut logits);let action=masked_argmax(&logits,&mask);let u=&state.units[ui];let command=Self::command(action,u);
        self.previous=(action/AREA)as u8;Audit{oh:fnv(&obs),mh:fnv(&mask),action,id:u.id,command}
    }
    fn decide(&mut self,state:&State)->(Vec<Audit>,Vec<String>){self.resolve(state);let built=self.target_built(state);let own=state.own();let mut records=Vec::new();
        if !own.is_empty(){records.push(self.phase(state,own[0],0));if built&&own.len()>1{records.push(self.phase(state,own[1],1));}}
        let mut commands=Vec::new();if !built{commands.push(format!("TRAIN {} {} {} {}",self.target[0],self.target[1],self.target[2],self.target[3]));}
        for &ui in &own{if let Some(record)=records.iter().find(|r|r.id==state.units[ui].id){commands.push(record.command.clone());}else{commands.push("WAIT".to_string());}}
        for record in &records{let plane=record.action/AREA;let u=state.unit(record.id).unwrap();if plane==8{self.pending_plants.push((u.x,u.y));}
            if plane==1&&self.created==Some((u.x,u.y)){self.pending_harvests.push((u.id,u.carry[3]));}}
        (records,commands)
    }
}

fn main()->io::Result<()>{let args:Vec<String>=std::env::args().collect();let audit=args.get(1).is_some_and(|s|s=="--audit");let recipe=args.get(2).and_then(|s|s.parse::<usize>().ok()).unwrap_or(6).min(7);
    let stdin=io::stdin();let mut reader=io::BufReader::new(stdin.lock());let map=match read_map(&mut reader){Some(v)=>v,None=>return Ok(())};let stdout=io::stdout();let mut out=io::BufWriter::new(stdout.lock());
    let mut turn=1usize;let first=match read_state(&mut reader,turn){Some(v)=>v,None=>return Ok(())};let mut controller=Controller::new(map,RECIPES[recipe],&first);let mut state=Some(first);
    while let Some(current)=state{let(records,commands)=controller.decide(&current);if audit{write!(out,"AUDIT {}",records.len())?;for r in records{write!(out," {} {} {}",r.oh,r.mh,r.action)?;}writeln!(out," |{}",commands.join(";"))?;
        }else{writeln!(out,"{}",commands.join(";"))?;}out.flush()?;turn+=1;state=read_state(&mut reader,turn);}Ok(())}
// END_LIVE_COMMAND_MAIN
'''


def generate_live_source(manifest: dict[str, Any], payload: bytes) -> tuple[str, dict[str, Any]]:
    k2_source, k2_accounting = generate_optimized_source(manifest, payload)
    kernel_stop = k2_source.index(KERNEL_END) + len(KERNEL_END)
    kernel = k2_source[:kernel_stop]
    kernel = kernel.replace(
        "#![allow(clippy::needless_range_loop)]\nuse std::io::{self, Read, Write};\nuse std::time::Instant;",
        "#![allow(dead_code,unused_imports,clippy::needless_range_loop)]\nuse std::io::{self,BufRead,Write};",
        1,
    )
    source = kernel + TYPES_NAV_PARSER + OBSERVER_TRACKER + COMMAND_MAIN
    encoded = source.encode("utf-8")
    result: dict[str, Any] = dict(k2_accounting)
    result.update(
        {
            "generator_variant": "referee-facing-fixed-recipe6-live-v1",
            "protocol_sha256": PROTOCOL_SHA256,
            "k2_kernel_including_payload_bytes": len(kernel.encode("utf-8")),
            "parser_state_navigation_bytes": len(TYPES_NAV_PARSER.encode("utf-8")),
            "observer_mask_tracker_bytes": len(OBSERVER_TRACKER.encode("utf-8")),
            "command_train_main_audit_bytes": len(COMMAND_MAIN.encode("utf-8")),
            "generated_source_bytes": len(encoded),
            "generated_source_sha256": hashlib.sha256(encoded).hexdigest(),
            "under_100000_bytes": len(encoded) < 100_000,
        }
    )
    return source, result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("payload", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    payload = args.payload.read_bytes()
    source, result = generate_live_source(manifest, payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(source, encoding="utf-8")
    result.update(
        {
            "manifest_path": str(args.manifest.resolve()),
            "manifest_sha256": hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
            "payload_path": str(args.payload.resolve()),
            "output_path": str(args.output.resolve()),
        }
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
