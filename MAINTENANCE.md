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

For subsequent imports, commit and verify changes in that development checkout
first. Apply the committed diff since the last imported revision with the
`arcade-ports/sinistar/` prefix in this repository, review it, and record
the new source commit here. Treat changes to the source `.gitmodules` separately:
the hub owns submodule registration at its root. Do not develop independently
in both copies without merging those changes back.

The imported files retain their original relative layout. A compatible TSRun
checkout at the hub root supplies the local emulator dependency; it is not
published as part of this source import. The Sinistar server maps `/tsrun/`
to that dependency. GitHub Pages does not provide that server route, so a
hosted Sinistar player requires a separate publishing package.

## Preparation checks

The source checkpoint passed a cartridge rebuild, frontend, playable lifecycle,
render stress, gameplay features, voices, AY editor and assembly/clipping tests.
The clipping harness was updated to prevent its frozen victory fixtures from
timing out into score entry. It completed 1,772 cases. The rendering stress
test completed 18,000 refreshes with no late raster writes or ROM writes.

Cartridge SHA-256:
`e16a68ead32e6aeed388f1ceb33f62061c45cff4680a89437df12c38e2500617`.

The hub is prepared locally for `jon0x0/ts2068`; creating the remote repository,
pushing it and enabling any Pages site are separate publication steps.
