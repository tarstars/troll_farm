#!/usr/bin/env python3
"""Generate the std-only full-game neural bot from the signed Rust plane builder."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from cgauto.compact_rust_source import Token, _needs_space, _tokens, compact


ROOT = Path(__file__).resolve().parents[2]
RL_FULL = ROOT / "rust" / "src" / "rl_full.rs"
STATE = ROOT / "rust" / "src" / "game" / "state.rs"
ENGINE = ROOT / "rust" / "src" / "game" / "engine.rs"
EXPECTED_FORMAT = "troll-farm-full-actor-int8-refined-v1"
EXPECTED_PLAN_VERSION = "v400-2026-08-29"
EXPECTED_LAYERS = [
    "stem.0",
    "tower.0.conv1",
    "tower.0.conv2",
    "tower.1.conv1",
    "tower.1.conv2",
    "tower.2.conv1",
    "tower.2.conv2",
    "tower.3.conv1",
    "tower.3.conv2",
    "actor",
    "plan.mlp.0",
    "plan.mlp.2",
]
SHORTEN = """TF_FULL_CELLS TF_FULL_WIDTH TF_FULL_HEIGHT TF_FULL_OBS_SIZE
TF_FULL_ACTION_SIZE TF_FULL_PLAN_SIZE TF_FULL_ACTION_PLANES TF_FULL_OBS_CHANNELS
TF_FULL_MAX_TROLLS_PER_PLAYER TF_FULL_PLAN_VERSION TF_FULL_MAX_RECORDED_TRAINS
GameState StagedAction MoveRouting StaticMap Workspace Actor Layer Cell Unit Plant output
observation broadcast action_index set_cell current_reserved inventories walkable plan_index
absolute_cell view_cell from_ascii_with_talents bfs_distances decode_plan own_units
legal_plan_mask legal_action_mask fill_observation decode_action_text train_succeeds_local
read_static_map read_turn parse_stock decode_payload read_f32 b92_value payload source target
routing staged player current distance distances talents features hidden residual scratch action
plane index width height reader commands refinement packed scale coarse offset input value game
unit cell plants units shacks carry plant_type cooldown health fruits scores next_id iron water
training_cost apply_train apply_pick item_index next_cell manhattan spatial quant kind sources
command shown bank cost deficit affordable valid total start stop first second null linear conv
work turn relative refs own other tree_count unit_count seat current_view absolute plant
active_troll_id door_distance_plane distance_plane FRUIT_NAMES convolution destination kernel
plane_mean PAYLOAD_LEN plan_logits prior_target_trained staged_game masked_argmax staged_action
logits reservations candidate in_range reserved_cells rows scales sum_scales total_distance best
only_nonfruit aggregate phase plan_mask shack speed active_troll current_best fields mask
mine_sources validate_masked_action action_mask routes picks pooled queue rest tdist theirs
banks chunk doors gate goals item left load size right block before trolls header values layer
has_target has_iron movement option field base ours reachable to_target from_source
own_max own_sum opp_max opp_sum is_free is_near type_name best_dist""".split()
SHORT_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def short_name(index: int) -> str:
    digits = ""
    while True:
        digits = SHORT_ALPHABET[index % len(SHORT_ALPHABET)] + digits
        index //= len(SHORT_ALPHABET)
        if index == 0:
            return "z" + digits


SHORT_NAMES = {name: short_name(index) for index, name in enumerate(SHORTEN)}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unicode20(data: bytes) -> str:
    """Encode five payload bytes as two supplementary Unicode scalar values."""

    output: list[str] = []
    for start in range(0, len(data), 5):
        value = int.from_bytes(data[start : start + 5].ljust(5, b"\0"), "big")
        output.append(chr(0x10000 + (value >> 20)))
        output.append(chr(0x10000 + (value & 0xFFFFF)))
    return "".join(output)


def compact_submission(source: str) -> str:
    """Use the repository compactor's lexer, with deterministic generated-symbol shortening."""

    pieces: list[str] = []
    previous: Token | None = None
    for separated, token in _tokens(source):
        if token.kind == "word" and token.text in SHORT_NAMES:
            token = Token(SHORT_NAMES[token.text], token.kind)
        if separated and previous is not None and _needs_space(previous, token):
            pieces.append(" ")
        pieces.append(token.text)
        previous = token
    return compact("".join(pieces))


def _item(source: str, anchor: str) -> str:
    """Extract one Rust function or impl item, including its balanced body."""

    start = source.index(anchor)
    brace = source.index("{", start)
    depth = 0
    quote: str | None = None
    escaped = False
    index = brace
    while index < len(source):
        char = source[index]
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in {'"', "'"}:
            # Lifetimes do not occur in the extracted functions; apostrophes here are chars.
            quote = char
        elif source.startswith("//", index):
            newline = source.find("\n", index)
            index = len(source) if newline < 0 else newline
        elif source.startswith("/*", index):
            close = source.find("*/", index + 2)
            if close < 0:
                raise ValueError(f"unterminated comment after {anchor}")
            index = close + 1
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]
        index += 1
    raise ValueError(f"unterminated Rust item {anchor}")


def _between(source: str, start: str, stop: str) -> str:
    return source[source.index(start) : source.index(stop, source.index(start))]


def _lifted_runtime() -> tuple[str, dict[str, str]]:
    """Lift the state, movement, mask, codec and 104-plane code from the signed sources."""

    state = STATE.read_text()
    engine = ENGINE.read_text()
    rl = RL_FULL.read_text()
    state = state.replace("use std::collections::HashSet;\n", "", 1)
    state = state.replace(_item(state, "pub fn from_ascii"), "", 1)
    engine_parts = [
        _item(engine, "pub fn item_index"),
        _item(engine, "pub fn bfs_distances"),
        _item(engine, "pub fn next_cell"),
        _item(engine, "fn near_shack"),
        _item(engine, "pub fn apply_pick"),
        _item(engine, "pub fn training_cost"),
        _item(engine, "pub fn apply_train"),
    ]
    constants = """const PLUM:usize=0;const LEMON:usize=1;const APPLE:usize=2;
const BANANA:usize=3;const IRON:usize=4;const WOOD:usize=5;
const NEIGHBORS:[(i32,i32);4]=[(0,1),(1,0),(0,-1),(-1,0)];
"""
    signed_constants = "pub const PLUM: usize = 0;\npub const LEMON: usize = 1;"
    if signed_constants not in engine:
        raise ValueError("engine item constants drifted")

    head = _between(rl, "pub const TF_FULL_OBS_CHANNELS", "#[derive(Clone, Debug, Deserialize, Serialize)]")
    head = head.replace("pub const TF_FULL_OBS_CHANNELS: usize = 104;\n", "")
    head = head.replace(
        "pub const TF_FULL_OBS_SIZE: usize = TF_FULL_OBS_CHANNELS * TF_FULL_CELLS;\n",
        "pub const TF_FULL_OBS_SIZE: usize = 104 * TF_FULL_CELLS;\n",
    )
    head = head.replace("pub const TF_FULL_ACTION_PLANES: usize = 13;\n", "")
    head = head.replace(
        "pub const TF_FULL_ACTION_SIZE: usize = TF_FULL_ACTION_PLANES * TF_FULL_CELLS;\n",
        "pub const TF_FULL_ACTION_SIZE: usize = 13 * TF_FULL_CELLS;\n",
    )
    head = head.replace('pub const TF_FULL_PLAN_VERSION: &[u8] = b"v400-2026-08-29\\0";\n', "")
    head = head.replace("pub const TF_FULL_MAX_RECORDED_TRAINS: usize = 4;\n", "")
    routing = (
        "#[derive(Clone,Copy,Debug)]\n"
        + _item(rl, "struct StagedAction")
        + "\n#[derive(Clone,Debug)]\n"
        + _item(rl, "struct MoveRouting")
        + "\n"
        + _item(rl, "impl MoveRouting")
    )
    masks = _between(rl, "fn decode_plan", "fn set_cell")
    masks = masks.replace(_item(rl, "fn validate_masked_action"), "", 1)
    observations = _between(rl, "fn set_cell", "fn encode_command_text")
    combined = "\n".join([state, constants, *engine_parts, head, routing, masks, observations])
    source_hashes = {
        "state_sha256": sha256_bytes(STATE.read_bytes()),
        "engine_sha256": sha256_bytes(ENGINE.read_bytes()),
        "rl_full_sha256": sha256_bytes(RL_FULL.read_bytes()),
    }
    return combined, source_hashes


def _validated_metadata(manifest: dict[str, Any], payload: bytes) -> tuple[str, str, int]:
    if manifest.get("format") != EXPECTED_FORMAT:
        raise ValueError(f"unexpected export format {manifest.get('format')!r}")
    if manifest.get("observation_shape") != [104, 11, 22]:
        raise ValueError("unexpected observation shape")
    if manifest.get("action_shape") != [13, 11, 22]:
        raise ValueError("unexpected action shape")
    if manifest.get("plan_action_size") != 400:
        raise ValueError("unexpected plan action size")
    if manifest.get("plan_vocab_version") != EXPECTED_PLAN_VERSION:
        raise ValueError("unexpected plan vocabulary")
    if manifest.get("plan_sanitizer") != {
        "phase": "plan",
        "zero_planes": list(range(59, 72)) + [98],
    }:
        raise ValueError("unexpected plan sanitizer")
    if manifest.get("decoding") != {"plan": "masked_argmax", "command": "masked_argmax", "beam": False}:
        raise ValueError("unexpected decoding contract")
    if manifest.get("payload_bytes") != len(payload) or manifest.get("payload_sha256") != sha256_bytes(payload):
        raise ValueError("payload bytes or hash differ from manifest")
    layers = manifest.get("layers")
    if not isinstance(layers, list) or [layer.get("name") for layer in layers] != EXPECTED_LAYERS:
        raise ValueError("unexpected layer order")
    conv_meta: list[str] = []
    linear_meta: list[str] = []
    for index, layer in enumerate(layers):
        if layer.get("index") != index:
            raise ValueError(f"layer index drift at {index}")
        shape = [int(value) for value in layer["weight_shape"]]
        o = shape[0]
        i = int(np_product(shape[1:]))
        if int(layer["weight_bytes"]) != o * i:
            raise ValueError(f"weight extent drift at {index}")
        expected_bits = (
            16
            if layer["name"] in {"actor", "plan.mlp.0", "plan.mlp.2"}
            else 16
        )
        group_size = 64
        if (
            layer.get("effective_bits") != expected_bits
            or int(layer["refinement_bytes"]) != (o * i * (expected_bits - 8) + 7) // 8
            or layer.get("quantization_group_size") != group_size
            or layer.get("groups_per_output") != (i + group_size - 1) // group_size
            or int(layer["scale_bytes"]) != 4 * o * ((i + group_size - 1) // group_size)
            or int(layer["bias_bytes"]) != 4 * o
        ):
            raise ValueError(f"scale/bias extent drift at {index}")
        values = (
            o,
            i,
            int(layer["weight_offset"]),
            int(layer["refinement_offset"]),
            int(layer["scale_offset"]),
            int(layer["bias_offset"]),
            int(layer["effective_bits"]),
            group_size,
        )
        target = conv_meta if index < 10 else linear_meta
        target.append("(" + ",".join(map(str, values)) + ")")
    null = manifest.get("null_bias")
    if not isinstance(null, dict) or null.get("name") != "plan.null_bias" or null.get("bytes") != 4:
        raise ValueError("null-bias metadata drift")
    return ",".join(conv_meta), ",".join(linear_meta), int(null["offset"])


def np_product(values: list[int]) -> int:
    product = 1
    for value in values:
        product *= value
    return product


RUNTIME = r'''
struct StaticMap{rows:Vec<String>}
fn read_line(reader:&mut impl BufRead)->Option<String>{let mut line=String::new();match reader.read_line(&mut line){Ok(0)=>None,Ok(_)=>Some(line.trim_end_matches('\n').trim_end_matches('\r').to_string()),Err(_)=>None}}
fn read_static_map(reader:&mut impl BufRead)->Option<StaticMap>{let header=read_line(reader)?;let mut fields=header.split_whitespace();fields.next()?.parse::<i32>().ok()?;let height=fields.next()?.parse().ok()?;let mut rows=Vec::new();for _ in 0..height{rows.push(read_line(reader)?);}Some(StaticMap{rows})}
fn parse_stock(line:&str)->Option<[i32;6]>{let values:Vec<i32>=line.split_whitespace().map(|v|v.parse().ok()).collect::<Option<Vec<_>>>()?;values.try_into().ok()}
fn read_turn(reader:&mut impl BufRead,map:&StaticMap,turn:i32)->Option<(GameState,usize)>{
 let own=parse_stock(&read_line(reader)?)?;let other=parse_stock(&read_line(reader)?)?;
 let tree_count:usize=read_line(reader)?.parse().ok()?;let mut plants=Vec::with_capacity(tree_count);
 for _ in 0..tree_count{let line=read_line(reader)?;let f:Vec<&str>=line.split_whitespace().collect();if f.len()!=7{return None;}plants.push(Plant{plant_type:f[0].to_string(),x:f[1].parse().ok()?,y:f[2].parse().ok()?,size:f[3].parse().ok()?,health:f[4].parse().ok()?,fruits:f[5].parse().ok()?,cooldown:f[6].parse().ok()?});}
 let unit_count:usize=read_line(reader)?.parse().ok()?;let mut relative=Vec::with_capacity(unit_count);
 for _ in 0..unit_count{let line=read_line(reader)?;let v:Vec<i32>=line.split_whitespace().map(|x|x.parse().ok()).collect::<Option<Vec<_>>>()?;if v.len()!=14{return None;}relative.push(Unit{id:v[0],player:v[1],x:v[2],y:v[3],ms:v[4],cc:v[5],hp:v[6],chop:v[7],carry:[v[8],v[9],v[10],v[11],v[12],v[13]]});}
 let seat=relative.iter().filter(|u|u.player==0).map(|u|u.id).min()? as usize;if seat>1{return None;}
 let refs:Vec<&str>=map.rows.iter().map(String::as_str).collect();let mut game=from_ascii_with_talents(&refs,(1,1,1,1));
 if seat==1{game.shacks.swap(0,1);}game.inventories=if seat==0{[own,other]}else{[other,own]};
 for unit in &mut relative{if seat==1{unit.player=1-unit.player;}}game.units=relative;game.plants=plants;game.turn=turn;game.next_id=game.units.iter().map(|u|u.id).max().unwrap_or(-1)+1;
 for player in 0..2{let inv=&game.inventories[player];game.scores[player]=inv[0]+inv[1]+inv[2]+inv[3]+4*inv[WOOD];}
 Some((game,seat))}

fn decode_payload()->Vec<u8>{let mut chars=PAYLOAD_U20.chars();let mut output=Vec::with_capacity(PAYLOAD_LEN);while let Some(a)=chars.next(){let b=chars.next().unwrap();let value=(((a as u64-65536)<<20)|(b as u64-65536)).to_be_bytes();output.extend_from_slice(&value[3..]);}output.truncate(PAYLOAD_LEN);output}
fn read_f32(payload:&[u8],offset:usize)->f32{f32::from_le_bytes(payload[offset..offset+4].try_into().unwrap())}
struct Layer{o:usize,i:usize,w:Vec<f32>,b:Vec<f32>}
struct Workspace{input:Vec<f32>,hidden:Vec<f32>,scratch:Vec<f32>,residual:Vec<f32>,action:Vec<f32>}
struct Actor{conv:Vec<Layer>,linear:Vec<Layer>,null:f32,work:Workspace}
impl Actor{
 fn load(payload:&[u8],meta:&[(usize,usize,usize,usize,usize,usize,usize,usize)])->Vec<Layer>{meta.iter().map(|&(o,i,wo,ro,so,bo,bits,group)|{let mut w=Vec::with_capacity(o*i);let rb=bits-8;let groups=(i+group-1)/group;for output in 0..o{for offset in 0..i{let scale=read_f32(payload,so+4*(output*groups+offset/group));let index=output*i+offset;let bit=index*rb;let shift=bit%8;let mut residual=(payload[ro+bit/8]as usize)>>shift;if shift+rb>8{residual|=(payload[ro+bit/8+1]as usize)<<(8-shift);}residual&=(1<<rb)-1;let coarse=payload[wo+index]as i8 as i32;w.push((coarse*(1<<rb)+residual as i32)as f32*scale);}}let b=(0..o).map(|output|read_f32(payload,bo+4*output)).collect();Layer{o,i,w,b}}).collect()}
 fn new()->Self{let payload=decode_payload();let conv=Self::load(&payload,&CONV_META);let linear=Self::load(&payload,&LINEAR_META);let null=read_f32(&payload,NULL_OFFSET);Self{conv,linear,null,work:Workspace{input:vec![0.;TF_FULL_OBS_SIZE],hidden:vec![0.;16*TF_FULL_CELLS],scratch:vec![0.;16*TF_FULL_CELLS],residual:vec![0.;16*TF_FULL_CELLS],action:vec![0.;TF_FULL_ACTION_SIZE]}}}
 #[target_feature(enable="avx2")]unsafe fn convolution_range(layer:&Layer,input:&[f32],output:&mut[f32],kernel:usize,relu:bool,first:usize){let pad=kernel/2;let channels=layer.i/(kernel*kernel);for local in 0..output.len()/TF_FULL_CELLS{let oc=first+local;output[local*TF_FULL_CELLS..(local+1)*TF_FULL_CELLS].fill(layer.b[oc]);for ic in 0..channels{for ky in 0..kernel{let y0=pad.saturating_sub(ky);let y1=(TF_FULL_HEIGHT+pad-ky).min(TF_FULL_HEIGHT);for kx in 0..kernel{let x0=pad.saturating_sub(kx);let x1=(TF_FULL_WIDTH+pad-kx).min(TF_FULL_WIDTH);let weight=layer.w[((oc*channels+ic)*kernel+ky)*kernel+kx];let packed=_mm256_set1_ps(weight);let packed4=_mm_set1_ps(weight);for y in y0..y1{let ir=ic*TF_FULL_CELLS+(y+ky-pad)*TF_FULL_WIDTH;let or=local*TF_FULL_CELLS+y*TF_FULL_WIDTH;let mut x=x0;while x+8<=x1{let out=output.as_mut_ptr().add(or+x);let value=_mm256_loadu_ps(input.as_ptr().add(ir+x+kx-pad));_mm256_storeu_ps(out,_mm256_add_ps(_mm256_loadu_ps(out),_mm256_mul_ps(value,packed)));x+=8;}while x+4<=x1{let out=output.as_mut_ptr().add(or+x);let value=_mm_loadu_ps(input.as_ptr().add(ir+x+kx-pad));_mm_storeu_ps(out,_mm_add_ps(_mm_loadu_ps(out),_mm_mul_ps(value,packed4)));x+=4;}while x<x1{*output.get_unchecked_mut(or+x)+=*input.get_unchecked(ir+x+kx-pad)*weight;x+=1;}}}}}if relu{for value in &mut output[local*TF_FULL_CELLS..(local+1)*TF_FULL_CELLS]{*value=(*value).max(0.);}}}}
 fn forward(&mut self,observation:&[u8],mode:usize){for index in 0..self.work.input.len(){self.work.input[index]=observation[index]as f32*(1./255.);}unsafe{Self::convolution_range(&self.conv[0],&self.work.input,&mut self.work.hidden,3,true,0);for block in 0..4{Self::convolution_range(&self.conv[1+2*block],&self.work.hidden,&mut self.work.scratch,3,true,0);Self::convolution_range(&self.conv[2+2*block],&self.work.scratch,&mut self.work.residual,3,false,0);for index in 0..self.work.hidden.len(){self.work.hidden[index]=(self.work.hidden[index]+self.work.residual[index]).max(0.);}}if mode!=0{Self::convolution_range(&self.conv[9],&self.work.hidden,&mut self.work.action,1,false,0);}}}
 fn plane_mean(observation:&[u8],plane:usize,valid:f32)->f32{let start=plane*TF_FULL_CELLS;observation[start..start+TF_FULL_CELLS].iter().map(|value|*value as f32*(1./255.)).sum::<f32>()/valid.max(1.)}
 fn plan_logits(&self,observation:&[u8])->[f32;400]{let valid=observation[..TF_FULL_CELLS].iter().filter(|value|**value!=0).count()as f32;let mut pooled=[0f32;16];for channel in 0..16{let start=channel*TF_FULL_CELLS;let mut total=0.;for cell in 0..TF_FULL_CELLS{total+=self.work.hidden[start+cell]*(observation[cell]as f32*(1./255.));}pooled[channel]=total/valid.max(1.);}
  let banks=[43,44,45,47].map(|plane|Self::plane_mean(observation,plane,valid)*64.);let trolls=Self::plane_mean(observation,57,valid)*12.;let target=[60,61,62,63].map(|plane|Self::plane_mean(observation,plane,valid));let has_target=Self::plane_mean(observation,59,valid)>0.5;let has_iron=observation[4*TF_FULL_CELLS..5*TF_FULL_CELLS].iter().any(|value|*value!=0);let scales=[4.,5.,3.,4.];let mut logits=[0f32;400];logits[0]=self.null;
  for index in 1..400{let talents=decode_plan(index).unwrap();let raw=[talents.0 as f32,talents.1 as f32,talents.2 as f32,talents.3 as f32];let mut features=[0f32;30];features[..16].copy_from_slice(&pooled);let mut affordable=1.;let mut matches=has_target;for kind in 0..4{features[16+kind]=raw[kind]/scales[kind];let gate=if kind==3&&!has_iron{0.}else{1.};let cost=(trolls+raw[kind]*raw[kind])*gate;let deficit=(cost-banks[kind]).max(0.)*gate;features[20+kind]=cost/48.;features[24+kind]=deficit/48.;if deficit>0.{affordable=0.;}if (target[kind]*scales[kind]-raw[kind]).abs()>=0.5{matches=false;}}features[28]=affordable;features[29]=if matches{1.}else{0.};let first=&self.linear[0];let mut hidden=[0f32;32];for output in 0..32{let mut value=first.b[output];for input in 0..30{value+=features[input]*first.w[output*30+input];}hidden[output]=value.max(0.);}let second=&self.linear[1];let mut value=second.b[0];for input in 0..32{value+=hidden[input]*second.w[input];}logits[index]=value;}logits}
}
fn masked_argmax(logits:&[f32],mask:&[u8])->usize{let mut best=usize::MAX;let mut value=f32::NEG_INFINITY;for index in 0..logits.len(){if mask[index]!=0&&(best==usize::MAX||logits[index]>value){best=index;value=logits[index];}}assert_ne!(best,usize::MAX);best}
fn train_succeeds_local(game:&GameState,seat:usize,plan:usize,staged:&[StagedAction],routing:Option<&MoveRouting>)->bool{if plan==0{return false;}let mut shown=staged_game(game,seat,staged,routing);let mut picks=Vec::new();for action in staged{let index=action.action_index as usize;let plane=index/TF_FULL_CELLS;if(9..=12).contains(&plane){picks.push((action.troll_id,FRUIT_NAMES[plane-9].to_string()));}}apply_pick(&mut shown,&picks);let before=own_units(&shown,seat).len();apply_train(&mut shown,seat as i32,decode_plan(plan).unwrap());own_units(&shown,seat).len()>before}
fn main(){let stdin=io::stdin();let stdout=io::stdout();let mut reader=io::BufReader::new(stdin.lock());let mut output=io::BufWriter::new(stdout.lock());let Some(map)=read_static_map(&mut reader)else{return;};let mut actor=Actor::new();let mut routing=None;let mut turn=1;while let Some((game,seat))=read_turn(&mut reader,&map,turn){if routing.is_none(){routing=Some(MoveRouting::new(&game));}let routes=routing.as_ref();let mut observation=vec![0u8;TF_FULL_OBS_SIZE];let mut action_mask=vec![0u8;TF_FULL_ACTION_SIZE];let mut plan_mask=[0u8;TF_FULL_PLAN_SIZE];let staged:Vec<StagedAction>=Vec::new();fill_observation(&game,seat,-1,0,0,false,&staged,routes,&mut observation).unwrap();for plane in 59..72{observation[plane*TF_FULL_CELLS..(plane+1)*TF_FULL_CELLS].fill(0);}observation[98*TF_FULL_CELLS..99*TF_FULL_CELLS].fill(0);legal_plan_mask(&game,seat,&mut plan_mask);actor.forward(&observation,0);let plan=masked_argmax(&actor.plan_logits(&observation),&plan_mask);let mut staged=Vec::new();let mut first=true;for unit in own_units(&game,seat){fill_observation(&game,seat,unit.id,1,plan,false,&staged,routes,&mut observation).unwrap();legal_action_mask(&game,seat,unit.id,&staged,routes,&mut action_mask).unwrap();actor.forward(&observation,if first{1}else{2});first=false;let action=masked_argmax(&actor.work.action,&action_mask);staged.push(StagedAction{troll_id:unit.id,action_index:action as i32});}let mut commands:Vec<String>=staged.iter().map(|action|decode_action_text(action.action_index as usize,action.troll_id,seat,game.width,game.height).unwrap()).collect();if train_succeeds_local(&game,seat,plan,&staged,routes){let spec=decode_plan(plan).unwrap();commands.insert(0,format!("TRAIN {} {} {} {}",spec.0,spec.1,spec.2,spec.3));}writeln!(output,"{}",commands.join(";")).unwrap();output.flush().unwrap();turn+=1;}}
'''


def generate_full_source(manifest: dict[str, Any], payload: bytes) -> tuple[str, dict[str, Any]]:
    conv_meta, linear_meta, null_offset = _validated_metadata(manifest, payload)
    lifted, source_hashes = _lifted_runtime()
    encoded = unicode20(payload)
    prefix = f"""// Generated by local_claude_1/nn-bot/generate_full_bot.py; do not edit.
use std::collections::{{HashMap,HashSet,VecDeque}};
use std::arch::x86_64::*;
use std::io::{{self,BufRead,Write}};
const PAYLOAD_LEN:usize={len(payload)};
const PAYLOAD_U20:&str=\"{encoded}\";
const CONV_META:[(usize,usize,usize,usize,usize,usize,usize,usize);10]=[{conv_meta}];
const LINEAR_META:[(usize,usize,usize,usize,usize,usize,usize,usize);2]=[{linear_meta}];
const NULL_OFFSET:usize={null_offset};
"""
    source = prefix + lifted + RUNTIME
    compacted = compact_submission(source)
    accounting: dict[str, Any] = {
        "generator_variant": "full-game-v400-int8-refined-u20-k1",
        "compaction": "compact_rust_source lexer plus deterministic generated-symbol shortening",
        "payload_bytes": len(payload),
        "payload_unicode20_characters": len(encoded),
        "lifted_runtime_bytes": len(lifted.encode()),
        "readable_source_bytes": len(source.encode()),
        "readable_source_sha256": sha256_bytes(source.encode()),
        "compacted_source_bytes": len(compacted.encode()),
        "compacted_source_characters": len(compacted),
        "compacted_source_sha256": sha256_bytes(compacted.encode()),
        "under_100000_characters": len(compacted) < 100_000,
        **source_hashes,
    }
    return source, accounting


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("payload", type=Path)
    parser.add_argument("--readable-output", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    payload = args.payload.read_bytes()
    readable, result = generate_full_source(manifest, payload)
    compacted = compact_submission(readable)
    args.readable_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.readable_output.write_text(readable)
    args.output.write_text(compacted)
    result.update(
        {
            "manifest_path": str(args.manifest),
            "manifest_sha256": sha256_bytes(args.manifest.read_bytes()),
            "payload_path": str(args.payload),
            "readable_output": str(args.readable_output),
            "output": str(args.output),
        }
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
