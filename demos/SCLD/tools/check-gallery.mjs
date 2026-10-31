import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {bootCartridge,advance,setKey} from '../player/emulator.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const catalog=JSON.parse(fs.readFileSync(path.join(root,'catalog.json')));
const hash=x=>createHash('sha256').update(x).digest('hex');
const provenance=JSON.parse(fs.readFileSync(path.join(root,'player/tsrun-version.json')));
for(const [name,expected]of Object.entries(provenance.files)){if(hash(fs.readFileSync(path.join(root,'player/tsrun',name)))!==expected)throw Error('Emulator changed: '+name);}
const report={families:catalog.families.length,cartridges:0,unmodifiedTsrunCore:true,crt:false,systemRomRequired:false,results:[]};
const seen=new Set(),ids=new Set();fs.mkdirSync(path.join(root,'validation/captures'),{recursive:true});
for(const d of catalog.families){
 if(ids.has(d.id))throw Error('Duplicate family');ids.add(d.id);
 for(const f of ['what','how','look','controls','technical','source'])if(!d[f])throw Error('Missing explanation '+d.id+' '+f);
 for(const f of ['technical','source'])if(!fs.existsSync(path.join(root,d[f])))throw Error('Missing link '+d[f]);
 for(const [index,v]of d.variants.entries()){
  const data=fs.readFileSync(path.join(root,v.cartridge));if(hash(data)!==v.sha256)throw Error('Cartridge hash '+v.id);
  if(seen.has(v.sha256))throw Error('Duplicate cartridge bytes '+v.cartridge);seen.add(v.sha256);
  const m=bootCartridge(data);advance(m,120);
  const colors=new Set(m.pixels);if(colors.size<3)throw Error('Cartridge did not boot '+v.cartridge);
  const before=m.pixels.slice();let compareChanged=null;
  if(d.space==='Compare ECM'){
   setKey(m,'Space',true);advance(m,10);setKey(m,'Space',false);advance(m,20);
   compareChanged=m.pixels.some((v,i)=>v!==before[i]);if(!compareChanged)throw Error('Space comparison failed '+v.cartridge);
   setKey(m,'Space',true);advance(m,10);setKey(m,'Space',false);advance(m,20);
   if(!m.pixels.every((v,i)=>v===before[i]))throw Error('Space did not restore dynamic view '+v.cartridge);
  }
  for(const tap of v.taps)if(!fs.existsSync(path.join(root,tap.url)))throw Error('Missing tape '+tap.url);
  if(index===0){if(d.id==='evolution')advance(m,230);if(d.id==='reveal')advance(m,440);fs.writeFileSync(path.join(root,'validation/captures',d.id+'.bin'),m.pixels);}
  report.results.push({family:d.id,variant:v.id,sha256:v.sha256,bootFrames:120,colors:colors.size,compareChanged});report.cartridges++;
 }
}
if(report.families!==12||report.cartridges!==18)throw Error('Curated count changed');
fs.writeFileSync(path.join(root,'validation/gallery-native.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
