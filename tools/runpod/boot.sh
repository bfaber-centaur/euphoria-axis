#!/bin/bash
# Pod boot (tools/runpod/boot.sh), run by the template's start command from a fresh clone at /root/repo.
# Git is the source of truth: every file in tools/runpod/ and the data files below are copied onto the volume at
# /workspace/lens-fit/ (overwriting older copies), then setup runs from there as before.
set -uo pipefail
REPO=/root/repo; D=/workspace/lens-fit; L=/root/gateL/boot.log
T0=${BOOT_T0:-$(date +%s)}
log() { echo "+$(( $(date +%s) - T0 ))s $*" >> $L; }
fail() { log "FAILED: $*"; echo "$*" > /root/gateL/FAILED; exit 1; }
mkdir -p /root/gateL
log "repo at $(git -C $REPO rev-parse --short HEAD): $(git -C $REPO log -1 --format=%s | cut -c1-70)"

# the volume: mounted and writable (2 s polling, up to ~7 min)
m=0; w=0
for i in $(seq 1 210); do
  if [ $m = 0 ] && mountpoint -q /workspace; then m=1; log "/workspace is a mount point"; fi
  if [ $m = 1 ] && touch /workspace/.probe 2>/dev/null; then rm -f /workspace/.probe; w=1; log "/workspace writable"; break; fi
  sleep 2
done
[ $w = 1 ] || fail "network volume never became writable at /workspace (waited ~7 min)"

# sync from git to the volume (plain cp: the volume refuses metadata changes)
mkdir -p $D
n=0
for f in $REPO/tools/runpod/*; do
  [ -f "$f" ] || continue
  cp "$f" $D/ || fail "could not copy $(basename "$f") to the volume"
  n=$((n + 1))
done
DATA=(runs/qwen35-4b-posttrained-s2/paper_protocol/buttons_pilot/buttons_pilot_spec.json
      runs/qwen35-4b-posttrained-s2/paper_protocol/s1_comparison/psych_vocab_v1.json
      doc/protocols/gate2a/gate2a_spec.json
      doc/protocols/buttons/m7_q14_spec.json
      doc/protocols/lenses/r4_q14_spec.json)
for f in "${DATA[@]}"; do cp "$REPO/$f" $D/ || fail "could not copy $(basename "$f")"; done
git -C $REPO rev-parse HEAD > $D/SYNCED_FROM_COMMIT
log "synced $n scripts and ${#DATA[@]} data files from git to $D"

mkdir -p /workspace/gateL
BOOT_T0=$T0 bash $D/gateL_pod_setup_fast.sh > /workspace/gateL/setup.log 2>&1
