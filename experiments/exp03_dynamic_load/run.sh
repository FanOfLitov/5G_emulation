#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
source "$ROOT/experiments/common/testbed.sh"
start_testbed
wait_for_ue 120
out="$HERE/raw/timeline.csv"
echo "timestamp,phase,delay_ms,loss_percent,rtt_ms" > "$out"
run_phase() {
  local phase="$1" delay="$2" loss="$3"
  docker exec nr_ue tc qdisc replace dev uesimtun0 root netem delay "${delay}ms" loss "${loss}%"
  for _ in $(seq 1 5); do
    rtt=$(docker exec nr_ue ping -I uesimtun0 -c 3 8.8.8.8 2>&1 | awk -F'=' '/rtt|round-trip/{gsub(/ /,"",$2); split($2,a,"/"); print a[2]}' || true)
    echo "$(date --iso-8601=seconds),$phase,$delay,$loss,${rtt:-nan}" >> "$out"
    sleep 2
  done
}
run_phase low 5 0
run_phase medium 20 0.2
run_phase high 50 1
run_phase recovery 5 0
docker exec nr_ue tc qdisc del dev uesimtun0 root 2>/dev/null || true
echo "Saved: $out"
