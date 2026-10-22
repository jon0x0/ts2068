// Functional JLO/WD adapter for this CP/M BIOS; not cycle-accurate FDC emulation.
const text=data=>String.fromCharCode(...data);
const word=(data,at)=>data[at]|data[at+1]<<8;
const xor=data=>data.reduce((a,b)=>a^b,0);
function tapRecords(input){
 const data=new Uint8Array(input),blocks=[];
 for(let at=0;at<data.length;){
  if(at+2>data.length)throw Error('Truncated TAP length.');
  const length=word(data,at);at+=2;
  if(length<2||at+length>data.length)throw Error('Truncated TAP block.');
  const block=data.slice(at,at+length);at+=length;
  if(xor(block))throw Error('TAP checksum mismatch.');blocks.push(block);
 }
 if(blocks.length%2)throw Error('Expected TAP CODE header/data pairs.');
 const records=[];
 for(let i=0;i<blocks.length;i+=2){
  const h=blocks[i],d=blocks[i+1];
  if(h.length!==19||h[0]!==0||h[1]!==3||d[0]!==255||word(h,12)!==d.length-2)throw Error('Invalid TAP CODE record.');
  records.push({name:text(h.subarray(2,12)).trimEnd(),data:d.subarray(1,-1)});
 }
 return records;
}
function geometry(metadata){
 if(metadata.length!==128||text(metadata.subarray(0,9))!=='CPMRAM1\0\0'||![5,10].includes(metadata[9])||metadata[10]!==metadata[9]*4||metadata[11]!==(metadata[9]===5?16:32))throw Error('Invalid CP/M TAP geometry.');
 return metadata[10];
}
function pagesToMedia(records,count){
 if(records.length!==count)throw Error('Incomplete TAP disk.');
 const raw=new Uint8Array(count*8192);
 records.forEach((record,i)=>{if(record.name!==`CPM${String(i).padStart(2,'0')}`||record.data.length!==8192)throw Error('Missing or out-of-order TAP page.');raw.set(record.data,i*8192);});
 return {raw,sides:count/20,format:'tap'};
}
export function decodeTap(input){
 const records=tapRecords(input),meta=records.shift();
 if(meta?.name!=='CPMRAM')throw Error('Expected a CP/M disk TAP, not a program/tape loader.');
 return pagesToMedia(records,geometry(meta.data));
}
export function decodeMedia(input){
 const bytes=new Uint8Array(input);
 return text(bytes.subarray(0,34))==='MV - CPCEMU Disk-File\r\nDisk-Info\r\n'?decodeDsk(bytes):decodeTap(bytes);
}
function fletcher(data){let a=0,b=0;for(const value of data){a=(a+value)%255;b=(b+a)%255;}return a|b<<8;}
export function decodeTapSet(files){
 const byName=new Map();for(const file of files){const name=file.name.toUpperCase();if(byName.has(name))throw Error('Duplicate TAP filename.');byName.set(name,tapRecords(file.data));}
 const descriptor=byName.get('CPMSTATE.TAP');
 if(descriptor){
  if(descriptor.length!==1||descriptor[0].name!=='CPMSTATE')throw Error('Invalid saved-disk descriptor.');
  const state=descriptor[0].data;
  if(state.length!==128||text(state.subarray(0,8))!=='CPMSAV1\0'||state[8]!==1||![5,10].includes(state[9])||state[10]!==state[9]*4)throw Error('Incomplete/invalid saved disk.');
  const pages=[];for(let i=0;i<state[10];i++){
   const record=byName.get(`CPM${String(i).padStart(2,'0')}.TAP`);
   if(record?.length!==1||fletcher(record[0].data)!==word(state,12+2*i))throw Error('Missing or mismatched saved page.');pages.push(record[0]);
  }
  return pagesToMedia(pages,state[10]);
 }
 if(byName.has('CPM32000.TAP')){
  const first=byName.get('CPM32000.TAP');if(first[0]?.name!=='CPMRAM')throw Error('Invalid preload metadata.');
  const count=geometry(first[0].data),volumes=count/5,pages=[],identity=first[0].data.slice(16,48);
  for(let i=0;i<volumes;i++){
   const records=byName.get(`CPM3200${i}.TAP`),meta=records?.[0];
   if(records?.length!==6||meta.name!=='CPMRAM'||geometry(meta.data)!==count||meta.data[12]!==i||meta.data[13]!==volumes||identity.some((v,n)=>meta.data[16+n]!==v))throw Error('Missing or mixed preload TAP volumes.');
   pages.push(...records.slice(1));
  }
  return pagesToMedia(pages,count);
 }
 // Old descriptor-free exports are accepted only as an exact 20/40-page set.
 if(![20,40].includes(byName.size))throw Error('Select a complete disk TAP or all saved chunks, including CPMSTATE.TAP.');
 const pages=[];for(let i=0;i<byName.size;i++){const records=byName.get(`CPM${String(i).padStart(2,'0')}.TAP`);if(records?.length!==1)throw Error('Missing saved TAP page.');pages.push(records[0]);}
 return pagesToMedia(pages,pages.length);
}
function codeTap(name,payload){
 const h=new Uint8Array(19);h[1]=3;h.fill(32,2,12);h.set([...name].map(c=>c.charCodeAt(0)),2);h[12]=payload.length&255;h[13]=payload.length>>8;h[15]=160;h[17]=128;h[18]=xor(h);
 const output=new Uint8Array(2+19+2+payload.length+2);output.set([19,0]);output.set(h,2);const at=21,n=payload.length+2;output.set([n&255,n>>8,255],at);output.set(payload,at+3);output[output.length-1]=255^xor(payload);return output;
}
function concatenate(parts){const output=new Uint8Array(parts.reduce((n,p)=>n+p.length,0));let at=0;for(const p of parts){output.set(p,at);at+=p.length;}return output;}
export function encodeTap(raw){
 if(![163840,327680].includes(raw.length))throw Error('Unsupported TAP geometry.');
 const meta=new Uint8Array(128);meta.set([67,80,77,82,65,77,49,0,0,raw.length/32768,raw.length/8192,raw.length/10240]);
 return concatenate([codeTap('CPMRAM',meta),...Array.from({length:raw.length/8192},(_,i)=>codeTap(`CPM${String(i).padStart(2,'0')}`,raw.subarray(i*8192,(i+1)*8192)))]);
}
export function encodeTapSet(raw){
 if(![163840,327680].includes(raw.length))throw Error('Unsupported TAP geometry.');
 const state=new Uint8Array(128),files=[];state.set([67,80,77,83,65,86,49,0,1,raw.length/32768,raw.length/8192]);
 for(let i=0;i<raw.length/8192;i++){const name=`CPM${String(i).padStart(2,'0')}`,page=raw.subarray(i*8192,(i+1)*8192),crc=fletcher(page);state[12+i*2]=crc&255;state[13+i*2]=crc>>8;files.push({name:name+'.TAP',data:codeTap(name,page)});}
 files.push({name:'CPMSTATE.TAP',data:codeTap('CPMSTATE',state)});return files;
}
export function storedZip(files){
 const table=Uint32Array.from({length:256},(_,n)=>{for(let i=0;i<8;i++)n=n&1?0xedb88320^(n>>>1):n>>>1;return n>>>0;});
 const crc=data=>{let c=0xffffffff;for(const value of data)c=table[(c^value)&255]^(c>>>8);return (c^0xffffffff)>>>0;};
 const local=[],central=[];let offset=0;
 for(const file of files){
  const name=Uint8Array.from(file.name,c=>c.charCodeAt(0)),sum=crc(file.data),h=new Uint8Array(30),c=new Uint8Array(46),hv=new DataView(h.buffer),cv=new DataView(c.buffer);
  hv.setUint32(0,0x04034b50,true);hv.setUint16(4,20,true);hv.setUint16(12,33,true);hv.setUint32(14,sum,true);hv.setUint32(18,file.data.length,true);hv.setUint32(22,file.data.length,true);hv.setUint16(26,name.length,true);
  cv.setUint32(0,0x02014b50,true);cv.setUint16(4,20,true);cv.setUint16(6,20,true);cv.setUint16(14,33,true);cv.setUint32(16,sum,true);cv.setUint32(20,file.data.length,true);cv.setUint32(24,file.data.length,true);cv.setUint16(28,name.length,true);cv.setUint32(42,offset,true);
  local.push(h,name,file.data);central.push(c,name);offset+=h.length+name.length+file.data.length;
 }
 const directory=concatenate(central),end=new Uint8Array(22),view=new DataView(end.buffer);view.setUint32(0,0x06054b50,true);view.setUint16(8,files.length,true);view.setUint16(10,files.length,true);view.setUint32(12,directory.length,true);view.setUint32(16,offset,true);
 return concatenate([...local,directory,end]);
}
export function encodeDsk(raw){
 const sides=raw.length/163840;if(![1,2].includes(sides))throw Error('Unsupported DSK geometry.');
 const output=new Uint8Array(256+40*sides*4352),put=(at,s)=>output.set([...s].map(c=>c.charCodeAt(0)),at);
 put(0,'MV - CPCEMU Disk-File\r\nDisk-Info\r\n');put(34,'CPM2068');output.set([40,sides,0,17],48);
 for(let t=0;t<40*sides;t++){const at=256+t*4352,c=Math.floor(t/sides),h=t%sides;put(at,'Track-Info\r\n');output.set([c,h],at+16);output.set([1,16,0x4e,0xe5],at+20);for(let s=0;s<16;s++)output.set([c,h,s+1,1,0,0,0,1],at+24+s*8);output.set(raw.subarray(t*4096,(t+1)*4096),at+256);}
 return output;
}
export function decodeDsk(input){
 const data=new Uint8Array(input),ascii=(a,n)=>String.fromCharCode(...data.subarray(a,a+n));
 if(ascii(0,34)!=='MV - CPCEMU Disk-File\r\nDisk-Info\r\n')throw Error('Use a standard Fuse Oliger DSK image.');
 const sides=data[49],size=data[50]|data[51]<<8;
 if(data[48]!==40||![1,2].includes(sides)||size!==4352||data.length!==256+40*sides*size)throw Error('Expected 160KB or 320KB Oliger geometry.');
 const raw=new Uint8Array(163840*sides);
 for(let track=0;track<40*sides;track++){
  const pos=256+track*size;
  if(ascii(pos,12)!=='Track-Info\r\n'||data[pos+21]!==16)throw Error('Invalid DSK track.');
  for(let sector=0;sector<16;sector++){
   const at=pos+24+sector*8,expected=[Math.floor(track/sides),track%sides,sector+1,1,0,0];
   if(expected.some((v,i)=>data[at+i]!==v))throw Error('Unsupported DSK sector layout.');
  }
  raw.set(data.subarray(pos+256,pos+4352),track*4096);
 }
 return {raw,sides,container:data.slice(),format:'dsk'};
}

export function attachOliger(machine,input){
 const media=input?.raw?input:decodeMedia(input),read=machine.bus.ioRead,write=machine.bus.ioWrite;
 let head=0,status=0,track=0,sector=1,index=0,offset=0,writing=false,selected=true;
 const device={...media,dirty:false,writeProtected:false,reads:0,writes:0,
  reset(){head=0;status=0;track=0;sector=1;index=0;writing=false;selected=true;},
  exportDsk(){if(!media.container)return encodeDsk(media.raw);const output=media.container.slice();for(let t=0;t<40*media.sides;t++)output.set(media.raw.subarray(t*4096,(t+1)*4096),512+t*4352);return output;},
  exportTap(){return encodeTap(media.raw);},
  detach(){machine.bus.ioRead=read;machine.bus.ioWrite=write;}
 };
 machine.bus.ioRead=p=>{
  switch(p&255){
   case 0x8f:return status;
   case 0x9f:return track;
   case 0xaf:return sector;
   case 0xbf:if(!writing&&(status&3)===3){const value=media.raw[offset+index++];if(index===256)status=0;return value;}return 255;
   default:return read(p);
  }
 };
 machine.bus.ioWrite=(p,v)=>{
  switch(p&255){
   case 0xb7:selected=(v&3)===1;head=(v>>7)&1;break;
   case 0x9f:track=v;break;
   case 0xaf:sector=v;break;
   case 0xbf:
    if(writing&&(status&3)===3){media.raw[offset+index++]=v;device.dirty=true;if(index===256){status=0;writing=false;}}
    else index=v;
    break;
   case 0x8f:
    if(v===0){track=0;status=0;writing=false;}
    else if(v===0x10){track=index;status=0;writing=false;}
    else if(v===0xd0){status=0;writing=false;}
    else if(v===0x80||v===0xa0){
     index=0;writing=v===0xa0;
     if(!selected||track>=40||head>=media.sides||sector<1||sector>16){status=16;writing=false;break;}
     offset=((track*media.sides+head)*16+sector-1)*256;
     if(writing&&device.writeProtected){status=64;writing=false;break;}
     status=3;if(writing)device.writes++;else device.reads++;
    }else{status=16;writing=false;}
    break;
   default:write(p,v);
  }
 };
 return device;
}
