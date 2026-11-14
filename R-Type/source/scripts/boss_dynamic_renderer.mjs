// Dynamic object damage/composition prototype; host-side trial, not game Z80 code.
export const offset=y=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2);
export const palette=Array.from({length:16},(_,i)=>{const v=i&8?255:205;return[(i&2)?v:0,(i&4)?v:0,(i&1)?v:0];});
const pairs=[];for(let bright=0;bright<2;bright++)for(let p=0;p<8;p++)for(let i=p;i<8;i++)if(!bright||p!==0)pairs.push([p?bright*8+p:0,i?bright*8+i:0]);
const distance=(a,b)=>palette[a].reduce((s,v,k)=>s+(v-palette[b][k])**2,0);
const errors=palette.map((_,a)=>palette.map((_,b)=>distance(a,b)));
const cellCache=new Map();
export function legalCell(colours){
 const key=colours.join(',');if(cellCache.has(key))return cellCache.get(key);
 const unique=[...new Set(colours)];let best=Infinity,pair=[0,0],bits=0;
 for(const[p,i]of pairs){if(unique.includes(0)&&p!==0&&i!==0)continue;let cost=0,bb=0;for(let x=0;x<8;x++){const c=colours[x],pe=errors[c][p],ie=errors[c][i];cost+=Math.min(pe,ie)*(c===0?16:1);if(ie<pe)bb|=128>>x;}if(cost<best){best=cost;pair=[p,i];bits=bb;if(cost===0)break;}}
 const[p,i]=pair;const result=[bits,((p&7)<<3)|(i&7)|(((p|i)&8)?64:0),best];cellCache.set(key,result);return result;
}
export class BossScene{
 constructor(sprites){this.sprites=sprites;this.parts=[];this.pix=new Uint8Array(6144);this.attrs=new Uint8Array(6144);this.cache=new Map();this.background=false;this.composedCells=0;this.colourErrors=0;}
 // Cache sprite-local eight-pixel samples by cel, phase and orientation.
 // They contain no destination/backdrop/other-object information.
 sample(p,row,col){const src=this.sprites[p.cel],phase=((p.x%8)+8)%8,key=[p.cel,phase,p.flipX?1:0,p.flipY?1:0,row,col].join(':');if(this.cache.has(key))return this.cache.get(key);const v=new Uint8Array(8);for(let x=0;x<8;x++){let sx=col*8+x-phase,sy=row;if(sx<0||sx>=src.width||sy<0||sy>=src.height)continue;if(p.flipX)sx=src.width-1-sx;if(p.flipY)sy=src.height-1-sy;v[x]=src.colours[sy*src.width+sx];}this.cache.set(key,v);return v;}
 bounds(p){const s=this.sprites[p.cel];return[Math.floor(p.x/8),p.y,Math.ceil((p.x+s.width)/8),p.y+s.height];}
 dirtyPart(p,set){if(!p)return;const[l,t,r,b]=this.bounds(p);for(let y=Math.max(0,t);y<Math.min(192,b);y++)for(let x=Math.max(0,l);x<Math.min(32,r);x++)set.add(y*32+x);}
 composeCell(x,y,parts=this.parts){const cs=new Uint8Array(8);if(this.background&&((y*37+x*19)%97===0))cs[(x+y)%8]=7;for(const p of parts){const s=this.sprites[p.cel],r=y-p.y,c=x-Math.floor(p.x/8);if(r<0||r>=s.height||c<0||c>=Math.ceil((s.width+((p.x%8)+8)%8)/8))continue;const v=this.sample(p,r,c);for(let i=0;i<8;i++)if(v[i])cs[i]=v[i];}return legalCell(cs);}
 update(next,{background=this.background,full=false}={}){const dirty=new Set();if(full||background!==this.background)for(let i=0;i<6144;i++)dirty.add(i);else{const old=new Map(this.parts.map(p=>[p.id,p])),now=new Map(next.map(p=>[p.id,p]));const reordered=this.parts.map(p=>p.id).join(',')!==next.map(p=>p.id).join(',');for(const id of new Set([...old.keys(),...now.keys()])){const a=old.get(id),b=now.get(id);if(reordered||JSON.stringify(a)!==JSON.stringify(b)){this.dirtyPart(a,dirty);this.dirtyPart(b,dirty);}}}this.parts=next.map(p=>({...p}));this.background=background;const changes=[];let error=0;for(const cell of [...dirty].sort((a,b)=>a-b)){const y=cell>>5,x=cell&31,at=offset(y)+x,[px,attr,e]=this.composeCell(x,y);error+=e;const bx=this.pix[at]^px,ax=this.attrs[at]^attr;if(bx||ax){changes.push({x,y,bx,ax});this.pix[at]=px;this.attrs[at]=attr;}}this.composedCells=dirty.size;this.colourErrors=error;return changes;}
}
export function encodeChanges(changes){const out=[];for(let i=0;i<changes.length;){const start=changes[i],data=[];let nextX=start.x;while(i<changes.length&&changes[i].y===start.y&&changes[i].x===nextX){data.push(changes[i].bx,changes[i].ax);nextX++;i++;}out.push(start.y,start.x,data.length/2,...data);}out.push(255);return Uint8Array.from(out);}
