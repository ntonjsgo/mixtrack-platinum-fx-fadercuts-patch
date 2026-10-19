#!/usr/bin/env bash
# Decompiles the whole firmware with Ghidra headless (Cortex-M, base 0x08000000).
# Usage: GHIDRA_INSTALL_DIR=/path/to/ghidra ./analyze_firmware.sh fw.bin out_dir
# Output: out_dir/functions.txt, out_dir/strings.txt, out_dir/decomp.c
set -euo pipefail
FW=$(realpath "$1"); OUT=$(realpath -m "$2")
HERE=$(cd "$(dirname "$0")" && pwd)
PROJ=$(mktemp -d)
trap 'rm -rf "$PROJ"' EXIT
mkdir -p "$OUT"
"$GHIDRA_INSTALL_DIR/support/analyzeHeadless" "$PROJ" fw -import "$FW" \
  -loader BinaryLoader -loader-baseAddr 0x08000000 -processor ARM:LE:32:Cortex -noanalysis \
  -scriptPath "$HERE" -postScript DumpFw.java "$OUT" -deleteProject
