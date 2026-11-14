from pathlib import Path
p=Path('scripts/convert_l2_rpc_settings.mjs');s=p.read_text(encoding='utf-8-sig');s=s.replace("fs.writeFileSync(path.join(out,p.id+'.rgb'),rgb);", """// Canonical native packing: black is paper, transparent bitmap bits are zero.
 for(let k=0;k<attrs.length;k++){const a=attrs[k];if(!(a&64)&&(a&7)===0){const paper=(a>>3)&7;attrs[k]=paper;bits[k]=paper?(bits[k]^255):0;}}
 const preserve=new Uint8Array(n/8);for(let k=0;k<n;k++)if(!mask[k])preserve[k>>3]|=128>>(k&7);
 fs.writeFileSync(path.join(out,p.id+'.preserve'),preserve);
 fs.writeFileSync(path.join(out,p.id+'.rgb'),rgb);""")
s=s.replace("bright_black_disabled:true,serpentine", "bright_black_disabled:true,black_is_paper:true,transparent_bitmap_zero:true,serpentine");p.write_text(s,encoding='utf-8')
