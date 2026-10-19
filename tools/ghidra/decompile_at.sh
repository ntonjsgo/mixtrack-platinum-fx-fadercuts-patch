#!/usr/bin/env bash
# Disassembles and decompiles specific functions (Thumb), e.g. to check a patched image.
# Usage: GHIDRA_INSTALL_DIR=/path/to/ghidra ./decompile_at.sh fw.bin out.txt 0x08018ad2 0x08018df2
set -euo pipefail
FW=$(realpath "$1"); OUT=$(realpath -m "$2"); shift 2
HERE=$(cd "$(dirname "$0")" && pwd)
PROJ=$(mktemp -d)
trap 'rm -rf "$PROJ"' EXIT
"$GHIDRA_INSTALL_DIR/support/analyzeHeadless" "$PROJ" fw -import "$FW" \
  -loader BinaryLoader -loader-baseAddr 0x08000000 -processor ARM:LE:32:Cortex -noanalysis \
  -scriptPath "$HERE" -postScript DisAt.java "$OUT" "$@" -deleteProject
