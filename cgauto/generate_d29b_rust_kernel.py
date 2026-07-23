#!/usr/bin/env python3
"""Generate the frozen standalone Rust D29b int8 critic and parity harness."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
from typing import Any


EXPECTED_FORMAT = "troll-farm-d29-option-critic-int8-per-output-v1"
EXPECTED_LAYERS = {
    "conv1": [8, 36, 3, 3],
    "conv2": [8, 8, 3, 3],
    "scalar": [8, 426],
    "hidden": [16, 24],
    "output": [1, 16],
}
KERNEL_BEGIN = "// BEGIN_D29B_OPTION_CRITIC_KERNEL\n"
KERNEL_END = "// END_D29B_OPTION_CRITIC_KERNEL\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def validated_metadata(
    manifest: dict[str, Any], payload: bytes
) -> tuple[str, dict[str, int]]:
    if manifest.get("format") != EXPECTED_FORMAT:
        raise ValueError(f"unexpected D29a format: {manifest.get('format')!r}")
    if manifest.get("payload_bytes") != len(payload):
        raise ValueError("D29b payload length differs")
    if manifest.get("payload_sha256") != sha256_bytes(payload):
        raise ValueError("D29b payload hash differs")
    layers = manifest.get("layers")
    if [layer.get("name") for layer in layers] != list(EXPECTED_LAYERS):
        raise ValueError("D29b layer order differs")
    metadata = []
    for index, layer in enumerate(layers):
        name = layer["name"]
        shape = layer["weight_shape"]
        if layer["index"] != index or shape != EXPECTED_LAYERS[name]:
            raise ValueError(f"D29b layer metadata differs for {name}")
        output, inputs = map(int, shape[:2])
        kernel = int(shape[2]) if len(shape) == 4 else 0
        count = output * inputs * (kernel * kernel if kernel else 1)
        if int(layer["weight_bytes"]) != count:
            raise ValueError(f"D29b weight extent differs for {name}")
        if int(layer["scale_bytes"]) != 4 * output:
            raise ValueError(f"D29b scale extent differs for {name}")
        if int(layer["bias_bytes"]) != 4 * output:
            raise ValueError(f"D29b bias extent differs for {name}")
        metadata.append(
            "(" + ",".join(
                str(int(value))
                for value in (
                    output,
                    inputs,
                    kernel,
                    layer["weight_offset"],
                    layer["scale_offset"],
                    layer["bias_offset"],
                )
            ) + ")"
        )
    runtime = {entry["name"]: entry for entry in manifest["runtime_arrays"]}
    expected_runtime = {
        "scalar_mean": [426],
        "scalar_std": [426],
        "plane_scales": [36],
        "target_mean_std": [2],
    }
    if set(runtime) != set(expected_runtime):
        raise ValueError("D29b runtime arrays differ")
    offsets = {}
    for name, shape in expected_runtime.items():
        entry = runtime[name]
        if entry["shape"] != shape or entry["bytes"] != 4 * shape[0]:
            raise ValueError(f"D29b runtime array differs for {name}")
        offsets[name] = int(entry["offset"])
    return ",".join(metadata), offsets


def generate_source(
    manifest: dict[str, Any], payload: bytes
) -> tuple[str, dict[str, int | str]]:
    metadata, offsets = validated_metadata(manifest, payload)
    encoded = base64.b64encode(payload).decode("ascii")
    payload_sha = sha256_bytes(payload)
    kernel = f"""{KERNEL_BEGIN}const H:usize=11;
const W:usize=22;
const AREA:usize=H*W;
const PLANES:usize=36;
const GRID:usize=PLANES*AREA;
const SCALARS:usize=426;
const THRESHOLD:f32=4.0;
const PAYLOAD_LEN:usize={len(payload)};
const PAYLOAD_SHA256:&str=\"{payload_sha}\";
const PAYLOAD_B64:&str=\"{encoded}\";
const META:[(usize,usize,usize,usize,usize,usize);5]=[{metadata}];
const SCALAR_MEAN_OFFSET:usize={offsets['scalar_mean']};
const SCALAR_STD_OFFSET:usize={offsets['scalar_std']};
const PLANE_SCALE_OFFSET:usize={offsets['plane_scales']};
const TARGET_OFFSET:usize={offsets['target_mean_std']};

struct Layer{{o:usize,i:usize,k:usize,w:Vec<f32>,b:Vec<f32>}}
struct Critic{{
    layers:Vec<Layer>,scalar_mean:Vec<f32>,scalar_std:Vec<f32>,plane_scale:Vec<f32>,
    target_mean:f32,target_std:f32,input:Vec<f32>,conv1:Vec<f32>,conv2:Vec<f32>,
    scalar_input:Vec<f32>,combined:Vec<f32>,hidden:Vec<f32>,
}}

fn b64_value(byte:u8)->Option<u8>{{match byte{{
    b'A'..=b'Z'=>Some(byte-b'A'),b'a'..=b'z'=>Some(byte-b'a'+26),
    b'0'..=b'9'=>Some(byte-b'0'+52),b'+'=>Some(62),b'/'=>Some(63),b'='=>None,_=>None,
}}}}
fn decode_payload()->Vec<u8>{{
    let source=PAYLOAD_B64.as_bytes();let mut out=Vec::with_capacity(PAYLOAD_LEN);let mut n=0;
    while n<source.len(){{
        let a=b64_value(source[n]).unwrap() as u32;let b=b64_value(source[n+1]).unwrap() as u32;
        let c=b64_value(source[n+2]);let d=b64_value(source[n+3]);out.push(((a<<2)|(b>>4)) as u8);
        if let Some(c)=c{{let c=c as u32;out.push(((b<<4)|(c>>2)) as u8);if let Some(d)=d{{out.push(((c<<6)|d as u32) as u8);}}}}
        n+=4;
    }}
    assert_eq!(out.len(),PAYLOAD_LEN);out
}}
fn read_f32(data:&[u8],offset:usize)->f32{{f32::from_le_bytes(data[offset..offset+4].try_into().unwrap())}}
fn read_f32s(data:&[u8],offset:usize,count:usize)->Vec<f32>{{(0..count).map(|n|read_f32(data,offset+4*n)).collect()}}

impl Critic{{
    fn new()->Self{{
        let payload=decode_payload();let mut layers=Vec::with_capacity(5);
        for &(o,i,k,wo,so,bo) in &META{{
            let count=i*if k==0{{1}}else{{k*k}};let mut w=Vec::with_capacity(o*count);
            for output in 0..o{{let scale=read_f32(&payload,so+4*output);let start=wo+output*count;
                for n in 0..count{{w.push((payload[start+n] as i8) as f32*scale);}}
            }}
            layers.push(Layer{{o,i,k,w,b:read_f32s(&payload,bo,o)}});
        }}
        let target=read_f32s(&payload,TARGET_OFFSET,2);
        Self{{layers,scalar_mean:read_f32s(&payload,SCALAR_MEAN_OFFSET,SCALARS),
            scalar_std:read_f32s(&payload,SCALAR_STD_OFFSET,SCALARS),
            plane_scale:read_f32s(&payload,PLANE_SCALE_OFFSET,PLANES),
            target_mean:target[0],target_std:target[1],input:vec![0.0;GRID],
            conv1:vec![0.0;8*AREA],conv2:vec![0.0;8*AREA],scalar_input:vec![0.0;SCALARS],
            combined:vec![0.0;24],hidden:vec![0.0;16]}}
    }}
    fn convolution(layer:&Layer,input:&[f32],output:&mut[f32]){{
        let pad=layer.k/2;
        for oc in 0..layer.o{{for y in 0..H{{
            let ky0=pad.saturating_sub(y);let ky1=(H+pad-y).min(layer.k);
            for x in 0..W{{let kx0=pad.saturating_sub(x);let kx1=(W+pad-x).min(layer.k);
                let mut sum=layer.b[oc];
                for ic in 0..layer.i{{for ky in ky0..ky1{{let ir=ic*AREA+(y+ky-pad)*W;
                    let wr=((oc*layer.i+ic)*layer.k+ky)*layer.k;
                    for kx in kx0..kx1{{sum+=input[ir+x+kx-pad]*layer.w[wr+kx];}}
                }}}}
                output[oc*AREA+y*W+x]=sum.max(0.0);
            }}
        }}}}
    }}
    fn forward(&mut self,row:&[u8])->(f32,f32){{
        for n in 0..GRID{{let at=2*n;let value=i16::from_le_bytes([row[at],row[at+1]]);
            self.input[n]=value as f32/self.plane_scale[n/AREA];}}
        let scalar_offset=2*GRID;
        for n in 0..SCALARS{{let value=read_f32(row,scalar_offset+4*n);
            self.scalar_input[n]=(value-self.scalar_mean[n])/self.scalar_std[n];}}
        Self::convolution(&self.layers[0],&self.input,&mut self.conv1);
        Self::convolution(&self.layers[1],&self.conv1,&mut self.conv2);
        let count=self.input[..AREA].iter().filter(|&&value|value!=0.0).count() as f32;
        for channel in 0..8{{let mut total=0.0f32;let mut maximum=-1.0e9f32;
            for cell in 0..AREA{{if self.input[cell]!=0.0{{let value=self.conv2[channel*AREA+cell];
                total+=value;if value>maximum{{maximum=value;}}}}}}
            self.combined[channel]=total/count;self.combined[8+channel]=maximum;
        }}
        let scalar=&self.layers[2];
        for output in 0..8{{let mut sum=scalar.b[output];for input in 0..SCALARS{{
            sum+=self.scalar_input[input]*scalar.w[output*SCALARS+input];}}
            self.combined[16+output]=sum.max(0.0);
        }}
        let hidden=&self.layers[3];
        for output in 0..16{{let mut sum=hidden.b[output];for input in 0..24{{
            sum+=self.combined[input]*hidden.w[output*24+input];}}
            self.hidden[output]=sum.max(0.0);
        }}
        let output=&self.layers[4];let mut normalized=output.b[0];
        for input in 0..16{{normalized+=self.hidden[input]*output.w[input];}}
        (normalized,normalized*self.target_std+self.target_mean)
    }}
}}
{KERNEL_END}"""
    harness = r'''const MAGIC:&[u8;8]=b"D29BPRT1";
const HEADER:usize=24;
const ROW_BYTES:usize=2*GRID+4*SCALARS+5;
fn load(path:&str)->std::io::Result<(Vec<u8>,usize)>{
    let data=std::fs::read(path)?;
    if data.len()<HEADER||&data[..8]!=MAGIC{return Err(std::io::Error::new(std::io::ErrorKind::InvalidData,"header"));}
    let rows=u32::from_le_bytes(data[8..12].try_into().unwrap()) as usize;
    let grid=u32::from_le_bytes(data[12..16].try_into().unwrap()) as usize;
    let scalars=u32::from_le_bytes(data[16..20].try_into().unwrap()) as usize;
    let threshold=f32::from_le_bytes(data[20..24].try_into().unwrap());
    if grid!=GRID||scalars!=SCALARS||threshold.to_bits()!=THRESHOLD.to_bits()||data.len()!=HEADER+rows*ROW_BYTES{
        return Err(std::io::Error::new(std::io::ErrorKind::InvalidData,"shape"));
    }
    Ok((data,rows))
}
fn parity(path:&str)->std::io::Result<()>{
    let (data,rows)=load(path)?;let mut critic=Critic::new();let mut max_raw=0.0f32;
    let mut max_normalized=0.0f32;let mut disagreements=0usize;let mut finite=true;let mut checksum=0u64;
    for sample in 0..rows{
        let start=HEADER+sample*ROW_BYTES;let row=&data[start..start+ROW_BYTES];let (_,raw)=critic.forward(row);
        let expected_offset=2*GRID+4*SCALARS;let expected=read_f32(row,expected_offset);
        let expected_decision=row[expected_offset+4]!=0;let decision=raw>THRESHOLD;
        let error=(raw-expected).abs();max_raw=max_raw.max(error);max_normalized=max_normalized.max(error/critic.target_std);
        finite&=raw.is_finite();disagreements+=usize::from(decision!=expected_decision);
        checksum=checksum.rotate_left(7)^u64::from(raw.to_bits());
    }
    println!("{{\"rows\":{},\"finite\":{},\"maximum_raw_absolute_error\":{:.9},\"maximum_normalized_absolute_error\":{:.9},\"decision_disagreements\":{},\"decision_agreement\":{:.12},\"checksum\":{},\"payload_sha256\":\"{}\"}}",
        rows,finite,max_raw,max_normalized,disagreements,1.0-disagreements as f64/rows as f64,checksum,PAYLOAD_SHA256);
    Ok(())
}
fn benchmark(path:&str,iterations:usize)->std::io::Result<()>{
    let (data,rows)=load(path)?;if rows==0||iterations==0{return Err(std::io::Error::new(std::io::ErrorKind::InvalidInput,"empty"));}
    let initialization=std::time::Instant::now();let mut critic=Critic::new();
    let first=&data[HEADER..HEADER+ROW_BYTES];let (_,raw)=critic.forward(first);
    let initialization_first_ns=initialization.elapsed().as_nanos() as u64;let mut checksum=u64::from(raw.to_bits());
    for n in 0..16{let sample=n%rows;let start=HEADER+sample*ROW_BYTES;let (_,raw)=critic.forward(&data[start..start+ROW_BYTES]);checksum^=u64::from(raw.to_bits());}
    let mut durations=Vec::with_capacity(iterations);
    for n in 0..iterations{let sample=n%rows;let start=HEADER+sample*ROW_BYTES;let began=std::time::Instant::now();
        let (_,raw)=critic.forward(&data[start..start+ROW_BYTES]);durations.push(began.elapsed().as_nanos() as u64);checksum=checksum.wrapping_add(u64::from(raw.to_bits()));}
    durations.sort_unstable();let median=durations[durations.len()/2];let p95=durations[((durations.len()*95+99)/100).saturating_sub(1)];let maximum=*durations.last().unwrap();
    println!("{{\"iterations\":{},\"warmup\":16,\"initialization_first_ns\":{},\"median_ns\":{},\"p95_ns\":{},\"maximum_ns\":{},\"checksum\":{},\"payload_sha256\":\"{}\"}}",
        iterations,initialization_first_ns,median,p95,maximum,checksum,PAYLOAD_SHA256);Ok(())
}
fn main()->std::io::Result<()>{let args:Vec<_>=std::env::args().collect();if args.len()<2{return Err(std::io::Error::new(std::io::ErrorKind::InvalidInput,"corpus path"));}
    if args.get(2).map(String::as_str)==Some("--bench"){let iterations=args.get(3).and_then(|v|v.parse().ok()).unwrap_or(1000);benchmark(&args[1],iterations)}else{parity(&args[1])}}
'''
    prefix = "// Generated by cgauto/generate_d29b_rust_kernel.py; do not edit.\n#![allow(clippy::needless_range_loop)]\n"
    source = prefix + kernel + harness
    source_bytes = source.encode()
    accounting: dict[str, int | str] = {
        "payload_bytes": len(payload),
        "payload_base64_bytes": len(encoded),
        "kernel_bytes_including_payload": len(kernel.encode()),
        "parity_benchmark_harness_bytes": len(harness.encode()),
        "generated_source_bytes": len(source_bytes),
        "generated_source_sha256": sha256_bytes(source_bytes),
        "payload_sha256": payload_sha,
    }
    return source, accounting


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("payload", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--kernel-output", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    payload = args.payload.read_bytes()
    source, result = generate_source(manifest, payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(source)
    if args.kernel_output:
        start = source.index(KERNEL_BEGIN)
        stop = source.index(KERNEL_END, start) + len(KERNEL_END)
        args.kernel_output.parent.mkdir(parents=True, exist_ok=True)
        args.kernel_output.write_text(source[start:stop])
    result.update(
        {
            "manifest": str(args.manifest),
            "manifest_sha256": sha256_bytes(args.manifest.read_bytes()),
            "payload": str(args.payload),
            "output": str(args.output),
            "kernel_output": (
                str(args.kernel_output) if args.kernel_output else None
            ),
            "under_100000_bytes": len(source.encode()) < 100_000,
        }
    )
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
