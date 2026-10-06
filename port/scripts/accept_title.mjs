// Gameplay regressions start via the real keyboard port, after the title.
export function acceptTitle(m, symbols) {
 const read=m.bus.ioRead;
 m.bus.ioRead=port => symbols.title_wait!==undefined && m.cpu.pc>=symbols.title_wait && m.cpu.pc<symbols.title_data && port===0x7ffe ? 30 : read(port);
}
