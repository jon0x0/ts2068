// Gameplay regressions start via the real keyboard port, after the title.
export function acceptTitle(m, symbols) {
 const read=m.bus.ioRead;
 let accepted=false;
 m.bus.ioRead=port => {
  const waiting=symbols.front_fire!==undefined ? m.cpu.pc>=symbols.front_fire && m.cpu.pc<symbols.front_table : symbols.title_wait!==undefined && m.cpu.pc>=symbols.title_wait && m.cpu.pc<symbols.title_data;
  if(!accepted && waiting && port===0x7ffe){accepted=true;return 30;}
  return read(port);
 };
}
