// BEGIN_D29B_OPTION_CRITIC_KERNEL
const H:usize=11;
const W:usize=22;
const AREA:usize=H*W;
const PLANES:usize=36;
const GRID:usize=PLANES*AREA;
const SCALARS:usize=426;
const THRESHOLD:f32=4.0;
const PAYLOAD_LEN:usize=10864;
const PAYLOAD_SHA256:&str="acf192cf6b2225de01b12e0507120866f20c7b2e8296a026aa85dfae288be87f";
const PAYLOAD_B64:&str="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";
const META:[(usize,usize,usize,usize,usize,usize);5]=[(8,36,3,0,2592,2624),(8,8,3,2656,3232,3264),(8,426,0,3296,6704,6736),(16,24,0,6768,7152,7216),(1,16,0,7280,7296,7300)];
const SCALAR_MEAN_OFFSET:usize=7304;
const SCALAR_STD_OFFSET:usize=9008;
const PLANE_SCALE_OFFSET:usize=10712;
const TARGET_OFFSET:usize=10856;

struct Layer{o:usize,i:usize,k:usize,w:Vec<f32>,b:Vec<f32>}
struct Critic{
    layers:Vec<Layer>,scalar_mean:Vec<f32>,scalar_std:Vec<f32>,plane_scale:Vec<f32>,
    target_mean:f32,target_std:f32,input:Vec<f32>,conv1:Vec<f32>,conv2:Vec<f32>,
    scalar_input:Vec<f32>,combined:Vec<f32>,hidden:Vec<f32>,
}

fn b64_value(byte:u8)->Option<u8>{match byte{
    b'A'..=b'Z'=>Some(byte-b'A'),b'a'..=b'z'=>Some(byte-b'a'+26),
    b'0'..=b'9'=>Some(byte-b'0'+52),b'+'=>Some(62),b'/'=>Some(63),b'='=>None,_=>None,
}}
fn decode_payload()->Vec<u8>{
    let source=PAYLOAD_B64.as_bytes();let mut out=Vec::with_capacity(PAYLOAD_LEN);let mut n=0;
    while n<source.len(){
        let a=b64_value(source[n]).unwrap() as u32;let b=b64_value(source[n+1]).unwrap() as u32;
        let c=b64_value(source[n+2]);let d=b64_value(source[n+3]);out.push(((a<<2)|(b>>4)) as u8);
        if let Some(c)=c{let c=c as u32;out.push(((b<<4)|(c>>2)) as u8);if let Some(d)=d{out.push(((c<<6)|d as u32) as u8);}}
        n+=4;
    }
    assert_eq!(out.len(),PAYLOAD_LEN);out
}
fn read_f32(data:&[u8],offset:usize)->f32{f32::from_le_bytes(data[offset..offset+4].try_into().unwrap())}
fn read_f32s(data:&[u8],offset:usize,count:usize)->Vec<f32>{(0..count).map(|n|read_f32(data,offset+4*n)).collect()}

impl Critic{
    fn new()->Self{
        let payload=decode_payload();let mut layers=Vec::with_capacity(5);
        for &(o,i,k,wo,so,bo) in &META{
            let count=i*if k==0{1}else{k*k};let mut w=Vec::with_capacity(o*count);
            for output in 0..o{let scale=read_f32(&payload,so+4*output);let start=wo+output*count;
                for n in 0..count{w.push((payload[start+n] as i8) as f32*scale);}
            }
            layers.push(Layer{o,i,k,w,b:read_f32s(&payload,bo,o)});
        }
        let target=read_f32s(&payload,TARGET_OFFSET,2);
        Self{layers,scalar_mean:read_f32s(&payload,SCALAR_MEAN_OFFSET,SCALARS),
            scalar_std:read_f32s(&payload,SCALAR_STD_OFFSET,SCALARS),
            plane_scale:read_f32s(&payload,PLANE_SCALE_OFFSET,PLANES),
            target_mean:target[0],target_std:target[1],input:vec![0.0;GRID],
            conv1:vec![0.0;8*AREA],conv2:vec![0.0;8*AREA],scalar_input:vec![0.0;SCALARS],
            combined:vec![0.0;24],hidden:vec![0.0;16]}
    }
    fn convolution(layer:&Layer,input:&[f32],output:&mut[f32]){
        let pad=layer.k/2;
        for oc in 0..layer.o{for y in 0..H{
            let ky0=pad.saturating_sub(y);let ky1=(H+pad-y).min(layer.k);
            for x in 0..W{let kx0=pad.saturating_sub(x);let kx1=(W+pad-x).min(layer.k);
                let mut sum=layer.b[oc];
                for ic in 0..layer.i{for ky in ky0..ky1{let ir=ic*AREA+(y+ky-pad)*W;
                    let wr=((oc*layer.i+ic)*layer.k+ky)*layer.k;
                    for kx in kx0..kx1{sum+=input[ir+x+kx-pad]*layer.w[wr+kx];}
                }}
                output[oc*AREA+y*W+x]=sum.max(0.0);
            }
        }}
    }
    fn forward(&mut self,row:&[u8])->(f32,f32){
        for n in 0..GRID{let at=2*n;let value=i16::from_le_bytes([row[at],row[at+1]]);
            self.input[n]=value as f32/self.plane_scale[n/AREA];}
        let scalar_offset=2*GRID;
        for n in 0..SCALARS{let value=read_f32(row,scalar_offset+4*n);
            self.scalar_input[n]=(value-self.scalar_mean[n])/self.scalar_std[n];}
        Self::convolution(&self.layers[0],&self.input,&mut self.conv1);
        Self::convolution(&self.layers[1],&self.conv1,&mut self.conv2);
        let count=self.input[..AREA].iter().filter(|&&value|value!=0.0).count() as f32;
        for channel in 0..8{let mut total=0.0f32;let mut maximum=-1.0e9f32;
            for cell in 0..AREA{if self.input[cell]!=0.0{let value=self.conv2[channel*AREA+cell];
                total+=value;if value>maximum{maximum=value;}}}
            self.combined[channel]=total/count;self.combined[8+channel]=maximum;
        }
        let scalar=&self.layers[2];
        for output in 0..8{let mut sum=scalar.b[output];for input in 0..SCALARS{
            sum+=self.scalar_input[input]*scalar.w[output*SCALARS+input];}
            self.combined[16+output]=sum.max(0.0);
        }
        let hidden=&self.layers[3];
        for output in 0..16{let mut sum=hidden.b[output];for input in 0..24{
            sum+=self.combined[input]*hidden.w[output*24+input];}
            self.hidden[output]=sum.max(0.0);
        }
        let output=&self.layers[4];let mut normalized=output.b[0];
        for input in 0..16{normalized+=self.hidden[input]*output.w[input];}
        (normalized,normalized*self.target_std+self.target_mean)
    }
}
// END_D29B_OPTION_CRITIC_KERNEL
