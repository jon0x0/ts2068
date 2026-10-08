# Maintaining the TS2068 hub

## Existing projects and URLs

Keep Berzerk, TSWriter, the AI skill, the existing demos, speech2ay and
TSVideoCodec in their current repositories. The root README links to them.
Do not rename those repositories or move their Pages entry points merely to
add them to this directory. Berzerk's root URL and
`personalizations/berzerk/` path remain owned by `jon0x0/berzerk_ts2068`.

Add new public projects to the relevant table. Unpublished local work should
be identified as such instead of receiving a speculative URL.

## Sinistar source import

The initial import is Sinistar commit `d957358`, under
`arcade-ports/sinistar/`. The commit is an ancestor of the hub's initial
commit, preserving the complete prior history. The original development
checkout has not moved and remains the development source for now.

Last synchronized source commit: `815e5f5`. This includes both static browser
players, full keyboard instructions and the isolated Berzerk virtual D-pad
runtime. Fullscreen hides the D-pad player's guide and restores it on exit.
Upper-right controls include Fast mode, Bounce and emulator Pause/Resume.
The source cartridge is unchanged.

For subsequent imports, commit and verify changes in that development checkout
first. Apply the committed diff since the last imported revision with the
`arcade-ports/sinistar/` prefix in this repository, review it, and record
the new source commit here. Treat changes to the source `.gitmodules` separately:
the hub owns submodule registration at its root. Do not develop independently
in both copies without merging those changes back.

The imported files retain their original relative layout. The browser player
at `arcade-ports/sinistar/play/` bundles unmodified TSRun commit `41dbe3e` and
requires only a static web server; it can be hosted beneath a project URL.
Existing public players and emulator checkouts remain independent.

For the older development viewer and the default native test setup, a
compatible TSRun checkout at the hub root supplies the local emulator
dependency. The development server maps `/tsrun/` to that checkout. Use the
new `play/` package for static hosting instead.

## Preparation checks

The source checkpoint passed a cartridge rebuild, frontend, playable lifecycle,
render stress, gameplay features, voices, AY editor and assembly/clipping tests.
The clipping harness was updated to prevent its frozen victory fixtures from
timing out into score entry. It completed 1,772 cases. The rendering stress
test completed 18,000 refreshes with no late raster writes or ROM writes.

Cartridge SHA-256:
`e16a68ead32e6aeed388f1ceb33f62061c45cff4680a89437df12c38e2500617`.

The public repository is `jon0x0/ts2068`. GitHub Pages serves the main branch
root at https://jon0x0.github.io/ts2068/. Run `python scripts/build_site.py`
after updating the hub or cartridge catalog, then commit and push to publish.
The D-pad and newer TSRun demos keep separate emulator snapshots.
