// Functional stock single-FIFO/TAP + 512KB SRAM model. Slot semantics are
// inferred from documented MEMDOCK and later source; not frozen-1.00 execution.
import assert from 'node:assert/strict';
const xor=bytes=>bytes.reduce((a,b)=>a^b,0);
export function tapBlocks(tap){const out=[];for(let i=0;i<tap.length;){const n=tap.readUInt16LE(i);i+=2;const b=tap.subarray(i,i+n);assert.equal(b.length,n);out.push(Buffer.from(b));i+=n;}return out;}
function codeTap(header,data){return Buffer.concat([Buffer.from([19,0,0]),header,Buffer.from([xor(header)]),Buffer.from([(data.length+2)&255,(data.length+2)>>8,255]),data,Buffer.from([255^xor(data)])]);}
export class SramPicoModel{
  constructor(m,cartridge,tap,{badBlock=-1,readOnlyPage=-1,missing=false,volumes={},modern=false,service=null,verbose=false,rejectCommand=null,missingSaveDirectory=false,getinfoText=null,missingStatus=null,stallCommand=null}={}){
    this.m=m;this.ram=new Uint8Array(524288);this.slot=4;this.bootSlot=4;
    this.queue=[];this.input=[];this.phase='header';this.blocks=tapBlocks(tap);this.block=0;
    this.modern=modern;this.status=255;this.syncs=0;this.service=service?Buffer.from(service):null;
    this.stallCommand=stallCommand;this.missingStatus=missingStatus;this.getinfoText=getinfoText;this.verbose=verbose;this.rejectCommand=rejectCommand;this.missingSaveDirectory=missingSaveDirectory;this.commandHeaders=[];
    this.cwd='/';this.append=false;this.mounted=null;
    this.badBlock=badBlock;this.readOnlyPage=readOnlyPage;this.missing=missing;this.commands=[];this.saved=new Map();this.volumes={...volumes};
    let offset=9;
    for(let page=0;page<8;page++){const type=cartridge[page+1];if(type&2){this.ram.set(cartridge.subarray(offset,offset+8192),4*32768+page*8192);offset+=8192;}}
    assert.equal(offset,cartridge.length);m.exCart.fill(null);m.exCartRam.fill(false);this.map();
  }
  map(){for(let i=0;i<8;i++){this.m.dock[i]=this.ram.subarray(this.slot*32768+i*8192,this.slot*32768+(i+1)*8192);this.m.dockRam[i]=!(this.slot!==4&&i===this.readOnlyPage);}}
  read(port){if(this.modern&&(port&255)===15)return this.status;const value=this.queue.shift()??0;if(this.modern&&this.autoIdle&&this.queue.length<=1)this.status=255;return value;}
  reply(status=1){this.queue.push(...(this.modern?[status,1]:[64,status]));this.status=255;this.phase='header';}
  message(status,text){if(!this.modern&&this.verbose){this.queue.push(64,129,status,13,...Buffer.from(text),0);this.status=255;this.phase='header';}else this.reply(status);}
  packet(data){this.queue.push(1,data.length,...data,xor(data),1);this.status=247;this.autoIdle=true;this.phase='header';}
  write(port,value){
    if(this.modern&&(port&255)===15){this.syncs++;this.queue=[1];this.input=[];this.phase='header';this.status=255;return;}
    assert.equal(port&255,14,'stock firmware must never receive modern SYNC');
    this.input.push(value);
    if(this.phase==='header'&&this.input.length===10){
      this.pre=this.input;this.input=[];assert.equal(xor(this.pre),0,'preheader checksum');
      this.length=this.pre[7]|this.pre[8]<<8;
      // Modern pre-load is one token, not a second ACK after SYNC.
      if(!this.modern)this.queue.push(1,64);else if(!this.queue.length)this.queue.push(1);
      this.status=247;this.autoIdle=false;
      if(this.pre[0]===66){this.phase='command';if(!this.modern)this.queue.push(1);}
      else this.phase=this.pre[1]===1?'readEcho':'saveHeader';
    }else if(this.phase==='command'&&this.input.length===this.length+4){
      assert.equal(xor(this.input),0);const text=Buffer.from(this.input.slice(3,-1)).toString();this.input=[];this.commands.push(text);this.commandHeaders.push(Buffer.from(this.pre));
      const name=text.toUpperCase();
      if(name===this.stallCommand){this.phase='stalled';return;}
      if(name==='TPI:DIR'){
        const prefix=(this.cwd==='/'?'':this.cwd)+'/';
        const files=Object.keys(this.volumes).filter(x=>x.startsWith(prefix)&&!x.slice(prefix.length).includes('/'));
        let listing=('Path:'+this.cwd).padEnd(32)+'File Name'.padEnd(22)+'    Size'.padStart(10)+'-'.repeat(32);
        listing+=files.length?files.map((x,i)=>(String(i).padStart(3,'0')+' '+x.slice(prefix.length).padEnd(18)+'     128 b')).join(''):'Directory is empty'.padEnd(32);
        const before=this.verbose;this.verbose=true;this.message(1,listing);this.verbose=before;return;
      }
      if(name==='TPI:GETINFO'){if(this.getinfoText){const before=this.verbose;this.verbose=true;this.message(1,this.getinfoText);this.verbose=before;}else this.reply(5);return;}
      if(this.rejectCommand===name){this.message(5,'81 - Unrecognized command: '+name);return;}
      if(!this.modern&&((name.endsWith('.TAP')&&this.pre[1]===0)||(name.startsWith('TPI:CD ')&&this.pre[1]!==0))){this.message(5,'81 - Unrecognized command: '+name);return;}
      if(name==='TPI:.CPMCAP'||name==='TPI:.CPMINFO'){
        if(this.service)this.packet(Buffer.from([67,80,77,49,1,128,0,this.service.length/32768]));else this.reply(5);
      }else if(name==='TPI:.CPMRD'){
        const lba=this.pre[3]|this.pre[4]<<8;
        if(this.service&&lba<this.service.length/128)this.packet(this.service.subarray(lba*128,lba*128+128));else this.reply(6);
      }else if(name.startsWith('TPI:.CPMW0 ')){
        this.pending=Buffer.from(text.split(' ')[1],'hex');this.reply();
      }else if(name.startsWith('TPI:.CPMW1 ')){
        const lba=this.pre[3]|this.pre[4]<<8;
        Buffer.concat([this.pending,Buffer.from(text.split(' ')[1],'hex')]).copy(this.service,lba*128);this.reply();
      }else if(name==='TPI:MEMDOCK'){
        assert.equal(this.pre[1],0);assert.equal(this.pre[3]|this.pre[4]<<8,1);
        this.slot=this.pre[5]|this.pre[6]<<8;assert(this.slot%2===0&&this.slot<=14);this.map();this.reply();
      }else if(name.endsWith('.TAP')&&name.startsWith('TPI:')){
        const filename=(this.cwd==='/'?'':this.cwd)+'/'+name.slice(4);
        const data=this.volumes[filename];this.block=0;this.append=false;
        if(data&&!this.missing){this.blocks=tapBlocks(data);this.mounted=filename;this.reply();}else this.message(this.missingStatus??(this.modern?3:0),'Error! File does not exists! '+name.slice(4));
      }else if(name.startsWith('TPI:CD ')){
        const arg=name.slice(7);if(!(this.missingSaveDirectory&&arg==='SAVE'))this.cwd=arg==='/'?'/':(this.cwd==='/'?'':this.cwd)+'/'+arg;this.reply();
      }else if(name==='TPI:CLOSE'){this.append=false;this.mounted=null;this.reply();}
      else if(name==='TPI:APPEND ON'){
        if(this.modern&&this.mounted){this.append=true;this.reply();}else this.reply(4);
      }
      else throw Error('unsupported legacy command '+text);
    }else if(this.phase==='readEcho'){
      const block=this.blocks[this.block++];assert(block,'TAP exhausted');assert.equal(value,this.pre[0]);
      assert.equal(block.length,this.length+2,'requested block length');
      const bytes=Buffer.from(block);if(this.block-1===this.badBlock)bytes[bytes.length-1]^=1;
      this.queue.push(...bytes);this.input=[];this.phase='readResult';
    }else if(this.phase==='readResult'){
      this.input=[];this.reply();
    }else if(this.phase==='saveHeader'&&this.input.length===21){
      assert.equal(xor(this.input),0);this.saveHeader=Buffer.from(this.input.slice(3,20));
      this.saveLength=this.input[14]|this.input[15]<<8;this.input=[];this.queue.push(...(this.modern?[1]:[64,1]));this.status=247;this.phase='saveData';
    }else if(this.phase==='saveData'&&this.input.length===this.saveLength+4){
      assert.equal(this.input[0],255);assert.equal(xor(this.input),0);
      const name=this.saveHeader.subarray(1,11).toString().trim()+'.TAP';
      const target=this.append?this.mounted:(this.cwd==='/'?'':this.cwd)+'/'+name;
      const block=codeTap(this.saveHeader,Buffer.from(this.input.slice(3,-1)));
      const data=this.append?Buffer.concat([this.volumes[target],block]):block;
      this.volumes[target]=data;this.saved.set(target.split('/').at(-1),data);this.input=[];this.reply();
    }
  }
  image(){return Buffer.concat(Array.from({length:40},(_,page)=>{const pairs=[0,2,6,8,10,12];return Buffer.from(this.ram.subarray(pairs[Math.floor(page/7)]*32768+(page%7)*8192,pairs[Math.floor(page/7)]*32768+(page%7+1)*8192));}));}
}
