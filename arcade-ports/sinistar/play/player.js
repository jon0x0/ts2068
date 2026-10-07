const frame = document.getElementById('emulator');
const status = document.getElementById('player-status');
const url = new URL('tsrun/index.html', location.href);
url.searchParams.set('url', new URL('assets/sinistar.dck', location.href).href);
url.searchParams.set('crt', '0');
url.searchParams.set('keyboard', '0');
document.getElementById('standalone').href = url.href;
document.getElementById('standalone').target = '_blank';
document.getElementById('standalone').rel = 'noopener';
frame.src = url.href;

// Keep upstream TSRun unchanged. Keys typed beside its same-origin frame also
// reach its normal keyboard handler; no cartridge memory is changed here.
const gameKeys = new Set(['KeyQ','KeyA','KeyO','KeyP','Space','Enter','KeyB','KeyR','KeyS','KeyC','KeyF']);
const held = new Map();
const releases = new Map();
function send(type, code, key = '', repeat = false) {
  frame.contentWindow?.dispatchEvent(new KeyboardEvent(type, {code, key, repeat, bubbles: true, cancelable: true}));
}
for (const type of ['keydown', 'keyup']) {
  window.addEventListener(type, event => {
    if (event.ctrlKey || event.metaKey || event.altKey || !gameKeys.has(event.code)) return;
    if (event.target.closest?.('input,textarea,select,button,a,summary,[contenteditable="true"]')) return;
    event.preventDefault();
    if (type === 'keydown') {
      clearTimeout(releases.get(event.code));
      releases.delete(event.code);
      if (!held.has(event.code)) held.set(event.code, performance.now());
      send(type, event.code, event.key, event.repeat);
    } else {
      // Very short taps must survive until the emulated keyboard is polled.
      const remaining = Math.max(0, 80 - (performance.now() - (held.get(event.code) ?? 0)));
      releases.set(event.code, setTimeout(() => {
        send(type, event.code, event.key);
        held.delete(event.code);
        releases.delete(event.code);
      }, remaining));
    }
  });
}
function releaseKeys() {
  for (const timeout of releases.values()) clearTimeout(timeout);
  releases.clear();
  for (const code of held.keys()) send('keyup', code);
  held.clear();
}
window.addEventListener('blur', releaseKeys);
document.addEventListener('visibilitychange', () => { if (document.hidden) releaseKeys(); });
frame.addEventListener('load', () => {
  status.textContent = 'Click the screen, then press Space to begin. Attract mode is silent.';
});
