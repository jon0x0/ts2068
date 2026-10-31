import {createMachine,insertDock,resetMachine,runFrame,cpuHz,tStatesPerFrame} from './tsrun/machine.js';

export const FRAME_MS=1000*tStatesPerFrame/cpuHz;
export const WIDTH=640,HEIGHT=240;
// TSRun's idealized CRT-off palette: normal level CC, BRIGHT offset 33.
export const PALETTE=Array.from({length:16},(_,i)=>[204*((i>>1)&1)+51*(i>>3),204*((i>>2)&1)+51*(i>>3),204*(i&1)+51*(i>>3)]);
export function bootCartridge(bytes){
  const machine=createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(31));
  const error=insertDock(machine,new Uint8Array(bytes));
  if(error)throw new Error(error);
  // These selected DCKs contain their own HOME bootstrap and initialized
  // assets. No host RAM injection or copyrighted system ROM is needed.
  resetMachine(machine);
  return machine;
}
export function advance(machine,count=1){for(let i=0;i<count;i++)runFrame(machine);}
const CONTACTS={Space:[7,0],KeyQ:[2,0],KeyA:[1,0],KeyR:[2,3],Enter:[6,0]};
export function setKey(machine,code,down){const contact=CONTACTS[code];if(!contact)return false;const [row,bit]=contact;if(down)machine.keyMatrix[row]&=~(1<<bit);else machine.keyMatrix[row]|=1<<bit;return true;}
export function releaseKeys(machine){machine?.keyMatrix.fill(31);}
export function paintIndices(indices,rgba){for(let i=0,j=0;i<indices.length;i++,j+=4){const p=PALETTE[indices[i]];rgba[j]=p[0];rgba[j+1]=p[1];rgba[j+2]=p[2];rgba[j+3]=255;}}
