#!/usr/bin/env bash
set -euo pipefail
UE_CONTAINER=${UE_CONTAINER:-nr_ue}
TUN=${TUN:-uesimtun0}
TARGET=${TARGET:-8.8.8.8}
OUT=${1:-results/live_probe.csv}
mkdir -p "$(dirname "$OUT")"
if ! docker exec "$UE_CONTAINER" ip link show "$TUN" >/dev/null 2>&1; then
  echo "TUN interface $TUN is not available in $UE_CONTAINER" >&2
  exit 1
fi
PING=$(docker exec "$UE_CONTAINER" ping -q -c 5 -I "$TUN" "$TARGET" || true)
LOSS=$(printf '%s\n' "$PING" | sed -n 's/.* \([0-9.]*\)% packet loss.*/\1/p')
RTT=$(printf '%s\n' "$PING" | sed -n 's#.*= [^/]*/\([^/]\+\)/.*#\1#p')
RX=$(docker exec "$UE_CONTAINER" cat "/sys/class/net/$TUN/statistics/rx_bytes")
TX=$(docker exec "$UE_CONTAINER" cat "/sys/class/net/$TUN/statistics/tx_bytes")
CPU=$(docker stats --no-stream --format '{{.CPUPerc}}' "$UE_CONTAINER" | tr -d '%')
if [[ ! -f "$OUT" ]]; then echo 'timestamp,latency_ms,packet_loss_percent,rx_bytes,tx_bytes,cpu_percent' > "$OUT"; fi
printf '%(%FT%T%z)T,%s,%s,%s,%s,%s\n' -1 "${RTT:-nan}" "${LOSS:-100}" "$RX" "$TX" "$CPU" >> "$OUT"
echo "Live metrics appended to $OUT"
