#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
source "$ROOT/experiments/common/testbed.sh"
out="$HERE/raw/startup.csv"
echo "timestamp,total_seconds,ue_ip,status" > "$out"
started=$(date +%s.%N)
if start_testbed && wait_for_ue 120; then
  ended=$(date +%s.%N)
  elapsed=$(awk -v a="$started" -v b="$ended" 'BEGIN{printf "%.3f",b-a}')
  ue_ip=$(docker exec nr_ue sh -lc "ip -4 addr show uesimtun0 | awk '/inet /{print \$2}'" | cut -d/ -f1)
  echo "$(date --iso-8601=seconds),$elapsed,$ue_ip,success" >> "$out"
else
  ended=$(date +%s.%N)
  elapsed=$(awk -v a="$started" -v b="$ended" 'BEGIN{printf "%.3f",b-a}')
  echo "$(date --iso-8601=seconds),$elapsed,,failed" >> "$out"
  exit 1
fi
echo "Saved: $out"
