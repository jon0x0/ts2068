"""Save a reviewable playable milestone without changing earlier demos."""

from pathlib import Path

import hashlib,json,shutil,re,argparse

parser=argparse.ArgumentParser()

parser.add_argument('--name',default='playable-scrolling-world-v1')

args=parser.parse_args()

assert re.fullmatch(r'[a-z0-9-]+',args.name)

root=Path(__file__).resolve().parents[1]

cart=root/'build/sinistar-mining.dck'

digest=hashlib.sha256(cart.read_bytes()).hexdigest()

page=root/'mining-web/index.html'

s=page.read_text(encoding='utf-8')

s=re.sub(r'emulator/\?build=[a-f0-9]+','emulator/?build='+digest[:8],s)

s=s.replace('Shoot the planetoid and collect its crystals','Shoot planetoids and collect their crystals')

s=s.replace('href="../pursuit-web/"','href="/port/pursuit-web/"')

a=s.index('<p>Follow the moving planetoid') if '<p>Follow the moving planetoid' in s else s.index('<p>Explore the scrolling world');b=s.index('<p><a href=',a)

s=s[:a]+'''<p>Explore the scrolling world and mine its <strong>18 persistent planetoids</strong>. Objects move offscreen and remain in the world; shattered rocks replenish away from you. Ten stars scroll with the camera.</p>

<p><strong>Top radar:</strong> white is you, cyan is planetoids, red is the worker, and yellow is Sinistar. Blue corners show the current viewport. The player stays centered on radar.</p>

<p>This is a functional world milestone. The measured scrolling scene renders about <strong>6 fps</strong> on the emulated TS2068; it still needs substantial drawing optimization to approach arcade smoothness.</p>

<details><summary>Implementation and remaining adaptations</summary><p>World coordinates, camera, clipping, mining, assembly, homing bombs, speech, and effects run in the Z80 cartridge. The scanner covers the full 512 by 512 world, including offscreen planetoids. Drawing publishes only changed final bitmap and attribute bytes. Precomputed Sinistar movement remains available when old and new object bounds permit it.</p><p>The first-wave population follows the source count: ten type-1 planetoids and two each of types 2â€“5. These currently share one pre-shifted planetoid image and initial mass. Starting positions and replenishment are simplified. Secondary planetoids integrate in four groups, preserving average scaled velocity. One worker, one free crystal, one bullet and one Sinibomb are active at a time. Multiple workers, warriors, full arcade AI, wave progression and separate planetoid artwork remain pending. The camera uses a dead zone adapted to the smaller display. The source uses ten stars with a common camera displacement; randomized edge-star replacement is pending.</p><p>Sinistar speech always takes priority over shooting effects. Complete archived recordings are resynthesized through AY speech2ay streams. The original saved demos remain available separately. See SCROLLING.md in the saved revision for tests and limitations.</p></details>

'''+s[b:]

s=s.replace("' Â· Rock '+(s.alive?'intact':'regenerating')","' Â· Planetoids '+s.planetoids")

page.write_text(s,encoding='utf-8')

if args.name=='playable-scrolling-culling-v2':

    s=s.replace('about <strong>6 fps</strong>','about <strong>6.9 fps</strong>')

    s=s.replace('<details><summary>','<p>Visibility culling now skips hidden sprite transfers. Visible planetoids avoid a redundant clearing pass, and the radar refreshes at most once per 16 physics ticks. The same flight benchmark improves from 5.8 to 6.9 fps. The 18-object world population is preserved.</p>\n<details><summary>',1)

    page.write_text(s,encoding='utf-8')

if args.name=='playable-compose-endings-v3':

    s=s.replace('about <strong>6 fps</strong>','about <strong>7.1 fps</strong>')

    s=s.replace('<details><summary>','<p>Native YOU WIN / GAME OVER messages now appear above play. Release fire, then press Space or joystick fire to restart. R also restarts. Radar preparation runs at most once per 24 physics ticks (about 2.5 Hz), while movement and collision timing stay unchanged. Composition avoids redundant clears; movement uses direct axis indexing and precomputed planetoid drift.</p>\n<details><summary>',1)

    s=s.replace('VICTORY â€” R to play again','VICTORY â€” release fire, then fire to play again').replace('GAME OVER â€” R to retry','GAME OVER â€” release fire, then fire to retry')

    page.write_text(s,encoding='utf-8')

if args.name=='playable-compiled-rocks-v4':

    s=s.replace('about <strong>6 fps</strong>','about <strong>8.15 fps</strong>')

    s=s.replace('<details><summary>','<p>Fully visible planetoids now draw through precompiled Z80 row programs. Clipped rocks use raw graphics cached in HOME RAM. Hidden rocks skip projection and rectangle copies where possible. The controlled chase measures 11.37 fps with one visible rock and 7.70 fps with three; one rock without Sinistar reaches 19.26 fps. These tests disable combat and speech. The 20 fps chase target remains unmet.</p><p>After YOU WIN or GAME OVER, release fire and press Space or joystick fire to restart. Radar prepares at most once per 24 physics ticks. Movement, collisions and audio retain their timing.</p>\n<details><summary>',1)

    s=s.replace('VICTORY â€” R to play again','VICTORY â€” release fire, then fire to play again').replace('GAME OVER â€” R to retry','GAME OVER â€” release fire, then fire to retry')

    page.write_text(s,encoding='utf-8')

if args.name=='playable-incremental-overlap-v5':
    s=s.replace('about <strong>6 fps</strong>','about <strong>8.09 fps</strong>')
    s=s.replace('<details><summary>','<p>Incremental restoration preserves cells beneath the new Sinistar image and clears only exposed strips. A stationary, fully visible Sinistar repairs dirty overlap spans and eye-animation rows. Movement, clipping and mouth transitions retain the full-image fallback. The controlled chase measures 11.95 fps with one rock and 7.93 fps with three. This remains below the 20 fps target.</p><p>Release fire after YOU WIN or GAME OVER, then press Space or joystick fire to restart.</p>\n<details><summary>',1)
    s=s.replace('VICTORY â€” R to play again','VICTORY â€” release fire, then fire to play again').replace('GAME OVER â€” R to retry','GAME OVER â€” release fire, then fire to retry')
    page.write_text(s,encoding='utf-8')
if args.name=='playable-retained-rocks-v6':
    s=s.replace('about <strong>6 fps</strong>','about <strong>8.15 fps</strong>')
    s=s.replace('<details><summary>','<p>Unchanged planetoids now retain their background and repair only damaged rows. The controlled three-rock chase improves from 7.93 to 11.49 fps (+45%); one-rock pursuit reaches 12.43 fps. These fixtures hold rock screen positions stable and disable combat and speech. Continuous scrolling remains about 8.15 fps. The 20 fps target is still unmet.</p><p>All 18 world planetoids remain simulated. Final screen writes still update only changed bytes. After YOU WIN or GAME OVER, release fire and press Space or joystick fire to restart.</p>\n<details><summary>',1)
    s=s.replace('VICTORY — R to play again','VICTORY — release fire, then fire to play again').replace('GAME OVER — R to retry','GAME OVER — release fire, then fire to retry')
    page.write_text(s,encoding='utf-8')
if args.name=='playable-border-flashes-v7':
    s=s.replace('about <strong>6 fps</strong>','about <strong>8 fps</strong>')
    s=s.replace('<details><summary>','<p>Brief red border flashes mark Sinibomb impacts and player deaths. Destroying Sinistar triggers a short red/yellow border sequence. The border returns to black; native win/loss messages remain visible. The refresh-clock timer adds no playfield redraws and is inactive between effects. This is an inexpensive approximation of the arcade palette flashes.</p>\n<details><summary>',1)
    page.write_text(s,encoding='utf-8')
if args.name=='playable-attribute-flashes-v8':
    s=s.replace('about <strong>6 fps</strong>','about <strong>8 fps</strong>')
    s=s.replace('<details><summary>','<p>Full-screen attribute flash experiment: Sinibomb hits and player deaths briefly change the background to red; victory uses yellow. Sprite ink and bitmap pixels are preserved, and attributes restore exactly. Speech continues. Each pulse pauses animation for about 123 ms, including the two attribute passes. The earlier v7 border-only build remains available for comparison.</p>\n<details><summary>',1)
    page.write_text(s,encoding='utf-8')
if args.name=='playable-local-bright-v9':
    s=s.replace('about <strong>6 fps</strong>','about <strong>8 fps</strong>')
    s=s.replace('<details><summary>','<p>Localized impact pulse: a visible Sinistar briefly brightens within its clipped rectangle. Already-bright cells are preserved and every attribute restores exactly. The pulse lasts one displayed refresh; the complete routine takes about 25-37 ms including alignment, compared with the previous build’s 123 ms full-screen flash. Speech continues. Offscreen hits, player deaths and the final destruction retain the border feedback.</p>\n<details><summary>',1)
    page.write_text(s,encoding='utf-8')
if args.name=='playable-ring-fast-v10':
    s=s.replace('about <strong>6 fps</strong>','about <strong>8.25 fps</strong>')
    s=s.replace('<details><summary>','<p><strong>New impact ring:</strong> red, yellow, red, then off on successive refreshes. Exact screen restoration; speech continues. Setup and restoration bring the complete pause to 81–87 ms. <a href="/port/build/ring-pulse-video/WATCH.html">Watch the native ring demonstration</a>.</p><p><strong>F: fast chase mode</strong> starts off. During pursuit, visible planetoids may leave but cannot reenter; hidden rocks and replacements are suppressed. Switch off to restore retired rocks. The matched silent chase fixture improves from 6.62 to 12.67 fps (13.47 fps after the rocks leave). This changes world behavior and remains below the 20 fps goal.</p>\n<details><summary>',1)
    page.write_text(s,encoding='utf-8')
if args.name=='playable-filled-flash-v11':
    s=s.replace('about <strong>6 fps</strong>','about <strong>8 fps</strong>')
    s=s.replace('<details><summary>','<p><strong>Filled impact flash:</strong> a circular region about 1.75 times Sinistar’s diameter cycles gray, yellow, red and white over four refreshes, then restores on the fifth. Attributes only; speech continues. Including preparation, the complete effect takes about 84–110 ms. <a href="/port/build/disc-pulse-video/WATCH.html">Watch the new filled-flash demo</a>.</p><p><strong>F: fast mode</strong> starts off and briefly displays FAST MODE ON/OFF inside the game. It caps visible planetoids at two. During pursuit, rocks can leave but cannot reenter; replacements are suppressed. Switch off to restore retired rocks. This changes world behavior to favor speed.</p>\n<details><summary>',1)
    page.write_text(s,encoding='utf-8')
if args.name=='playable-halo-v12':
    s=s.replace('about <strong>6 fps</strong>','about <strong>8 fps</strong>')
    s=s.replace('<details><summary>','<p><strong>Color-cycling halo:</strong> a broad outline about 1.75 times Sinistar’s diameter leaves Sinistar fully visible and cycles gray, yellow, red and white over four refreshes, then restores on the fifth. Attributes only; speech continues. Including preparation, the complete effect takes about 98–124 ms. <a href="/port/build/halo-pulse-video/WATCH.html">Watch the new halo demo</a>.</p><p><strong>F: fast mode</strong> starts off and briefly displays FAST MODE ON/OFF inside the game. It caps visible planetoids at two. During pursuit, rocks can leave but cannot reenter; replacements are suppressed. Switch off to restore retired rocks. This changes world behavior to favor speed.</p>\n<details><summary>',1)
    page.write_text(s,encoding='utf-8')
if args.name=='playable-expanding-halo-v13':
    s=s.replace('about <strong>6 fps</strong>','about <strong>8 fps</strong>')
    s=s.replace('<details><summary>','<p><strong>Expanding color halo:</strong> an artwork-centered outline expands through diameters 86, 90, 94 and 98 pixels, leaving Sinistar visible while cycling gray, yellow, red and white over four refreshes, then restores on the fifth. Attributes only; speech continues. Including preparation, the complete effect takes about 98–176 ms (roughly 175 ms fully visible). <a href="/port/build/expanding-halo-video/WATCH.html">Watch the expanding halo demo</a>.</p><p><strong>F: fast mode</strong> starts off and briefly displays FAST MODE ON/OFF inside the game. It caps visible planetoids at two. During pursuit, rocks can leave but cannot reenter; replacements are suppressed. Switch off to restore retired rocks. This changes world behavior to favor speed.</p>\n<details><summary>',1)
    page.write_text(s,encoding='utf-8')
if args.name=='playable-cycling-halo-v14':
    s=s.replace('about <strong>6 fps</strong>','about <strong>8 fps</strong>')
    s=s.replace('<details><summary>','<p><strong>Moving color bands:</strong> an artwork-centered outline expands through diameters 86, 90, 94 and 98 pixels, leaving Sinistar visible while yellow/white/red bands move upward one scanline per refresh for four refreshes, then restores on the fifth. Attributes only; speech continues. Including preparation, the complete effect takes about 98–176 ms (roughly 175 ms fully visible). <a href="/port/build/cycling-halo-video/WATCH.html">Watch the moving-band halo demo</a>.</p><p><strong>F: fast mode</strong> starts off and briefly displays FAST MODE ON/OFF inside the game. It caps visible planetoids at two. During pursuit, rocks can leave but cannot reenter; replacements are suppressed. Switch off to restore retired rocks. This changes world behavior to favor speed.</p>\n<details><summary>',1)
    page.write_text(s,encoding='utf-8')
if args.name=='playable-fast-supply-v15':
    s=s.replace('about <strong>6 fps</strong>','about <strong>8 fps</strong>')
    s=s.replace('<details><summary>','<p><strong>Moving color bands:</strong> an artwork-centered outline expands through diameters 86, 90, 94 and 98 pixels, leaving Sinistar visible while yellow/white/red bands move upward one scanline per refresh for four refreshes, then restores on the fifth. Attributes only; speech continues. Including preparation, the complete effect takes about 98–176 ms (roughly 175 ms fully visible). <a href="/port/build/cycling-halo-video/WATCH.html">Watch the moving-band halo demo</a>.</p><p><strong>F: fast mode</strong> starts off and briefly displays FAST MODE ON/OFF inside the game. It caps visible planetoids at two. Before Sinistar awakens, planetoids replenish so mining and construction can continue. During pursuit, rocks can leave but cannot reenter; replacements are suppressed. Switch off to restore retired rocks. Fast-mode profiles measure 8.67 fps during assembly and 12.46 fps in the silent chase fixture. <a href="../FAST_MODE_PROFILE.md">Full performance analysis</a>.</p>\n<details><summary>',1)
    page.write_text(s,encoding='utf-8')
p=root/'mining-web/emulator/adapter.js';s=p.read_text(encoding='utf-8')

if 'const planetRecords=' not in s:

    s=s.replace('    const state={','    const planetRecords=[...Array.from({length:8},(_,i)=>0x79b0+i*10),...Array.from({length:8},(_,i)=>0x7db0+i*10),0x58b4];\n    const state={planetoids:Number(machine.ram[0x7810]!==0)+planetRecords.filter(a=>machine.ram[a+7]!==0).length,')

p.write_text(s,encoding='utf-8')

if args.name=='playable-empty-eye-v16':
    s=page.read_text(encoding='utf-8')
    s=s.replace('about <strong>6 fps</strong>', 'about <strong>15.4 fps in fast-mode pursuit</strong>')
    s=s.replace('<details><summary>', '<p><strong>F: fast mode.</strong> Keeps at most two visible planetoids; mining supply refills until Sinistar awakens. Empty retired populations now bypass projection, drawing and physics. Eye changes can use guarded direct updates. Ordinary fast pursuit measures 15.38 fps; continuous speech and shooting measures 15.46 fps. Stars hidden by Sinistar are skipped using position checks. The 20 fps target remains unmet.</p><p>Player visibility is unchanged. An optional fully-covered-player experiment measured 16.48 fps, but remains disabled. See <a href="../FAST_MODE_PROFILE.md">the detailed comparison and remaining bottlenecks</a>. The expanding color-band halo is retained.</p>\n<details><summary>',1)
    page.write_text(s,encoding='utf-8')

dest=root/'revisions'/args.name

if args.name=='playable-clipped-cleanup-v17':
    s=page.read_text(encoding='utf-8')
    s=s.replace('<details><summary>', '<p><strong>Clipped Sinistar cleanup fixed:</strong> old and new rectangles now compare height as well as position and width. Shrinking behind the radar correctly erases the exposed bottom strip. Direct drawing, star occlusion and fast mode remain enabled.</p>\n<details><summary>',1)
    page.write_text(s,encoding='utf-8')

if args.name=='playable-assembly-cache-v18':
    s=page.read_text(encoding='utf-8')
    s=s.replace('about <strong>6 fps</strong>', 'about <strong>19.7 fps in the stationary assembly fixture</strong>')
    s=s.replace('<details><summary>', '<p><strong>Assembly graphics cache:</strong> eight horizontal shifts are prepared in a back buffer over 26 picture updates. The completed set replaces the visible set atomically. Assembly draws over the player, stars and other objects. In the controlled one-rock/player-overlap test, a stationary shifted assembly improves from 6.01 to 19.75 fps; changing scroll phase every picture improves from 7.33 to 12.40 fps. These are specific benchmark scenes, not a general 20 fps guarantee. New pieces appear after cache preparation finishes.</p><p><strong>F: fast mode.</strong> Caps visible planetoids at two and preserves mining supply until Sinistar awakens. <a href="../ASSEMBLY_CACHE.md">Cache design, measurements and verification</a>. The clipped cleanup and expanding color-band halo remain enabled.</p>\n<details><summary>',1)
    page.write_text(s,encoding='utf-8')

if args.name=='playable-assembly-composite-v19':
    s=page.read_text(encoding='utf-8')
    s=s.replace('The measured scrolling scene renders about <strong>6 fps</strong> on the emulated TS2068; it still needs substantial drawing optimization to approach arcade smoothness.', 'The controlled stationary assembly fixture runs at about <strong>19 fps with object overlap</strong>. Continuous scrolling and busier scenes remain slower.')
    s=s.replace('<details><summary>', '<p><strong>Assembly transparency:</strong> objects remain visible through gaps and outside Sinistar’s actual shape. Rows without overlaps keep the direct cached renderer; overlapping rows use the assembly mask. Fully covered object rectangles skip graphics staging and drawing, while their game logic continues. Unchanged rows are skipped.</p><p>The matched one-rock tests measure 19.63 fps with the player apart and 19.00 fps with overlap (v18: 19.45 / 19.75). Constant phase-changing overlap costs more: 8.62 fps versus 12.40 in the opaque v18 build. Cache preparation remains atomic over 26 picture updates. <a href="../ASSEMBLY_CACHE.md">Details, timings and tests</a>.</p><p><strong>F: fast mode.</strong> At most two visible planetoids; mining supply remains available before Sinistar awakens.</p>\n<details><summary>',1)
    page.write_text(s,encoding='utf-8')

if args.name=='playable-mask-cache-v20':
    s=page.read_text(encoding='utf-8')
    s=s.replace('The measured scrolling scene renders about <strong>6 fps</strong> on the emulated TS2068; it still needs substantial drawing optimization to approach arcade smoothness.', 'Precomputed assembly masks improve the controlled scrolling-overlap fixture from <strong>8.62 to 9.81 fps</strong>. Stationary assembly remains around 19 fps; busy scrolling scenes remain slower.')
    s=s.replace('<details><summary>', '<p><strong>Precomputed masks:</strong> all eight horizontal mask phases build in the back cache. The selected lookup is reused and assembly composition touches only dirty cells. Transparent gaps and fully covered-object culling remain enabled. New pieces appear after cache preparation completes.</p><p><strong>F: fast mode.</strong> At most two visible planetoids, with mining supply retained before awakening. Natural fast assembly measures 8.48 fps and fast pursuit 15.04 fps. <a href="../ASSEMBLY_CACHE.md">Current performance and tests</a>. <a href="../README.md">Original-source gameplay audit and remaining features</a>.</p>\n<details><summary>',1)
    page.write_text(s,encoding='utf-8')

if args.name=='playable-worker-combat-v21':
    s=page.read_text(encoding='utf-8')
    s=s.replace('The measured scrolling scene renders about <strong>6 fps</strong> on the emulated TS2068; it still needs substantial drawing optimization to approach arcade smoothness.', 'Player movement now accelerates to roughly twice the earlier speed. Graphics still run below the 20 fps target in busy scenes.')
    s=s.replace('Blue corners show the current viewport.', 'A blue outline shows the current viewport.')
    s=s.replace('<details><summary>', '<p><strong>Worker combat:</strong> shoot workers to destroy them in an expanding fragment explosion. Carried crystals drop, and replacement workers keep construction viable. Worker and planetoid destruction play a speech2ay explosion effect; Sinistar speech retains priority.</p><p><strong>Movement:</strong> gradual acceleration, faster travel, coasting, and bounce off planetoids. The bounce treats rocks as heavy moving obstacles. The top scanner now draws the complete camera-relative viewport outline.</p><p><strong>F: fast mode.</strong> Limits visible planetoids to two and maintains mining supply before awakening. Precomputed assembly masks and covered-object culling remain enabled. <a href="../FAST_MODE_PROFILE.md">Performance results</a>. <a href="../README.md">Changes and remaining arcade features</a>.</p>\n<details><summary>',1)
    page.write_text(s,encoding='utf-8')

assert '<iframe' in page.read_text(encoding='utf-8') and '<!doctype html>' in page.read_text(encoding='utf-8').lower(), 'Launcher must remain HTML with an emulator frame'

assert not dest.exists(), 'Preserve an existing saved revision'

dest.mkdir(parents=True)

for directory in ['src','scripts','mining-web']:

    shutil.copytree(root/directory,dest/directory,ignore=shutil.ignore_patterns('__pycache__','debug_incremental.mjs'))

for name in ['README.md','SCROLLING.md','MINING.md','MEMORY_MAP.md','ONE_ROCK_PROFILE.md','FAST_MODE_PROFILE.md','ASSEMBLY_CACHE.md']:

    shutil.copy2(root/name,dest/name)

(dest/'build').mkdir()

for p in (root/'build').iterdir():

    if not p.is_file() or p.name=='fast-final-profile.json':continue

    # Do not package old measurements as evidence for the current cartridge.
    if p.suffix=='.json':
        data=json.loads(p.read_text(encoding='utf-8'))
        if isinstance(data,dict) and data.get('dck_sha256') and data['dck_sha256']!=digest:continue

    current_report=p.name in ['assembly-cache-verification.json','assembly-scrolling-verification.json','mining-scene-verification.json','mining-eyes-verification.json','mining-covered-verification.json','fast-stars-scrolling-verification.json','scrolling-verification.json','population-verification.json','pursuit-timing-verification.json','playable-verification.json','voices-verification.json','mining-transitions-verification.json','scrolling-profile.json','end-screen-verification.json','incremental-verification.json','border-verification.json','attribute-flash-verification.json','cycling-raster-verification.json','fast-mode-verification.json','fast-playable-verification.json','fast-scrolling-verification.json','fast-mode-profile.json','one-planetoid-profile-current.json','one-planetoid-profile-culling-v2.json']

    native=p.name.startswith(('home-render','mining-','world-','fast-','assembly-','awakening-','speech-','sfx-','sinibomb-','title-','boot-','incremental','attribute-flash','render-kernels','rock-programs','player-tables','sinistar-speeds','scrolling-screen','sinistar-mining','effects','ring-points','ring-phases','mode-notice'))

    if current_report or p.name in ['gameplay-features-verification.json','stress-fast-verification.json','stress-covered-verification.json'] or (native and p.suffix in ['.bin','.dck','.asm','.json','.txt','.png'] and 'verification' not in p.name and 'trace' not in p.name):shutil.copy2(p,dest/'build'/p.name)

(dest/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(dest).as_posix()+'\n' for p in sorted(dest.rglob('*')) if p.is_file()),encoding='utf-8')

print(json.dumps(dict(path=str(dest),dck_sha256=digest),indent=2))

