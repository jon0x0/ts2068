// Functional modern TPI wire model; no claims about physical FIFO timing.
export class PicoModel {
  constructor(image,{mode='service',files={}}={}) {
    this.image=Buffer.from(image);this.mode=mode;this.files={'/CPM/DRIVEA.IMG':this.image,...files};
    this.status=255;this.tx=[];this.rx=[];this.phase='header';this.streams=new Map();
    this.commands=[];this.writes=[];this.syncs=0;this.pending=null;
  }
  read(p){
    if(this.mode==='legacy')return 64;
    if(this.mode==='busy')return 0;
    if(this.mode==='absent')return 255;
    if(this.mode==='stale')return (p&255)===14?1:255;
    return (p&255)===15?this.status:(this.tx.shift()??0);
  }
  write(p,v){
    this.writes.push([p&255,v]);
    if(['absent','legacy','busy','stale'].includes(this.mode))return;
    if((p&255)===15){this.syncs++;this.rx=[];this.tx=[1];this.phase='header';this.status=255;return;}
    this.rx.push(v);
    if(this.phase==='header'&&this.rx.length===10){
      const h=this.rx;this.rx=[];
      if(h.reduce((a,b)=>a^b,0)!==0){this.tx=[2];this.status=247;return;}
      this.par1=h[3]|h[4]<<8;this.par2=h[5]|h[6]<<8;this.length=h[7]|h[8]<<8;
      this.phase='body';this.tx=[1];this.status=247;
    }else if(this.phase==='body'&&this.rx.length===this.length+4){
      const body=this.rx;this.rx=[];this.phase='header';
      if(body.reduce((a,b)=>a^b,0)!==0){this.reply([2]);return;}
      const command=Buffer.from(body.slice(3,-1)).toString('ascii');this.commands.push(command);
      this.dispatch(command);
    }
  }
  reply(bytes){this.tx=[...bytes,1];this.status=255;}
  packet(data){let crc=0;for(const b of data)crc^=b;this.reply([1,data.length,...data,crc^(this.mode==='badcrc'?1:0)]);}
  dispatch(command){
    const [cmd,...args]=command.split(' ');const name=cmd.toLowerCase();
    if(name.startsWith('tpi:.cpm')&&this.rpc){this.reply(this.rpc(command,this.par1,this.par2));return;}
    if(name.startsWith('tpi:.cpm')&&this.mode==='stock'){this.reply([5]);return;}
    if(name==='tpi:.cpmcap'||name==='tpi:.cpminfo'){this.pending=null;this.packet(Buffer.from([67,80,77,49,1,128,(this.image.length/128)&255,this.image.length/32768]));return;}
    if(name==='tpi:.cpmrd'){this.pending=null;if(this.par1>=this.image.length/128){this.reply([6]);return;}this.packet(this.image.subarray(this.par1*128,this.par1*128+128));return;}
    if(name==='tpi:.cpmw0'){this.pending={lba:this.par1,data:Buffer.from(args.join(''),'hex')};this.reply([1]);return;}
    if(name==='tpi:.cpmw1'){
      if(!this.pending||this.pending.lba!==this.par1||this.par1>=this.image.length/128){this.reply([5]);return;}
      Buffer.concat([this.pending.data,Buffer.from(args.join(''),'hex')]).copy(this.image,this.par1*128);
      this.pending=null;this.reply([1]);return;
    }
    if(name==='tpi:chopen'){
      const [mode,...path]=args;const file=this.files[path.join(' ')];
      if(!file||mode!=='rb'){this.reply([3]);return;}
      this.streams.set(this.par1,{file,pos:0});this.reply([1]);return;
    }
    if(name==='tpi:chclose'){this.streams.delete(this.par1);this.reply([1]);return;}
    const stream=this.streams.get(this.par1);
    if(name==='tpi:chwr'&&stream){const b=Buffer.from(args.join(''),'hex');if(b.length===3&&b[0]===23){stream.pos=(b[1]|b[2]<<8)-1;this.reply([1]);return;}}
    if(name==='tpi:chrd'&&stream){const bytes=stream.file.subarray(stream.pos,stream.pos+(this.par2||255));stream.pos+=bytes.length;if(bytes.length)this.packet(bytes);else this.reply([7]);return;}
    this.reply([5]);
  }
}
