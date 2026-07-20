#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
source "$HERE/config.env"
source "$ROOT/experiments/common/testbed.sh"
out="$HERE/raw/runs.csv"
echo "run,startup_seconds,rtt_ms,packet_loss_percent,ue_ip" > "$out"
for run in $(seq 1 "$REPEATS"); do
  stop_radio >/dev/null 2>&1 || true
  started=$(date +%s.%N)
  start_testbed
  wait_for_ue 120
  ready=$(date +%s.%N)
  startup=$(awk -v a="$started" -v b="$ready" 'BEGIN{printf "%.3f",b-a}')
  ue_ip=$(docker exec nr_ue sh -lc "ip -4 addr show uesimtun0 | awk '/inet /{print \$2}'" | cut -d/ -f1)
  ping_out=$(docker exec nr_ue ping -I uesimtun0 -c "$PING_COUNT" "$PING_TARGET" 2>&1 || true)
  loss=$(printf '%s\n' "$ping_out" | sed -n 's/.* \([0-9.]*\)% packet loss.*/\1/p' | tail -1)
  rtt=$(printf '%s\n' "$ping_out" | awk -F'=' '/rtt|round-trip/{gsub(/ /,"",$2); split($2,a,"/"); print a[2]}' | tail -1)
  echo "$run,$startup,${rtt:-nan},${loss:-100},$ue_ip" >> "$out"
done
python3 "$HERE/analyze.py"
echo "Saved: $out"
