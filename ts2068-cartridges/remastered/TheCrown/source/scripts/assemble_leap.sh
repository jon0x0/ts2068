#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
assembler="$root/tools/sjasmplus/sjasmplus"
defs=(-DV2_MAINT_SOUND0 -DV2_MAINT_AY_BEEP -DV2_MAINT_CHIME_C -DV2_MAINT_AYB_PERIOD_HOME -DV2_MAINT_SHARED_WAIT)
for variant in host cartridge wide-host wide-cartridge; do
    cd "$root/build/$variant"
    "$assembler" "${defs[@]}" --sym=build/test_basic.sym --lst=build/test_basic.lst rom/v2_home.asm
    python3 tools/write_v2_crossbank.py build/test_basic.sym build/v2_crossbank.inc
    "$assembler" "${defs[@]}" --sym=build/exrom.sym --lst=build/exrom.lst rom/v2_exrom.asm
done
