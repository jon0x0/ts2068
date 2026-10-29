#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -z "${PASMO:-}" ]]; then
    if command -v pasmo >/dev/null 2>&1; then
        PASMO=pasmo
    else
        PASMO=../PasmoAssembler/pasmo-0.5.5/pasmo
    fi
fi
mkdir -p build
if ! "$PASMO" -I src --equ TS2068=1 --bin src/zxdesk.asm build/zxdesk2068.bin build/zxdesk2068.sym >build/assembler.log 2>&1; then
    cat build/assembler.log
    exit 1
fi
python3 scripts/package.py
if ! "$PASMO" -I src --equ TS2068=1 --equ HIRES=1 --bin src/zxdesk.asm build/zxdesk2068-512.bin build/zxdesk2068-512.sym >build/assembler-512.log 2>&1; then
    cat build/assembler-512.log
    exit 1
fi
python3 scripts/package.py zxdesk2068-512
if [[ "${1:-}" == "--check-spectrum" ]]; then
    "$PASMO" -I src --bin src/zxdesk.asm build/spectrum-port.bin >build/spectrum-port.log 2>&1
    "$PASMO" -I upstream/src --bin upstream/src/zxdesk.asm build/spectrum-upstream.bin >build/spectrum-upstream.log 2>&1
    cmp build/spectrum-port.bin build/spectrum-upstream.bin
    echo 'PASS Spectrum build remains byte-identical to pinned upstream'
fi
