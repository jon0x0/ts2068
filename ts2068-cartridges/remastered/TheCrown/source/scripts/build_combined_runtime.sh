#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
python3 scripts/prepare_runtime_only.py
python3 scripts/prepare_combined_runtime.py
cd build/combined-runtime
assembler="$root/tools/sjasmplus/sjasmplus"
defs=(-DV2_MAINT_SOUND0 -DV2_MAINT_AY_BEEP -DV2_MAINT_CHIME_C -DV2_MAINT_AYB_PERIOD_HOME -DV2_MAINT_SHARED_WAIT)
"$assembler" "${defs[@]}" --sym=build/test_basic.sym rom/v2_home.asm
python3 tools/write_v2_crossbank.py build/test_basic.sym build/v2_crossbank.inc
"$assembler" "${defs[@]}" --sym=build/exrom.sym rom/v2_exrom.asm
