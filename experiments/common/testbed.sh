#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OPEN5GS_DIR="$ROOT_DIR/external/docker_open5gs"

check_port_9090() {
  local owner
  owner="$(docker ps --format '{{.Names}} {{.Ports}}' | grep -E '(^|,)0\.0\.0\.0:9090->|\[::\]:9090->' || true)"
  if [[ -n "$owner" ]]; then
    echo "Port 9090 is still occupied: $owner" >&2
    echo "Stop that container or change the metrics port before continuing." >&2
    return 1
  fi

  if command -v ss >/dev/null 2>&1 && ss -ltn | awk '{print $4}' | grep -Eq '(^|:)9090$'; then
    echo "Host port 9090 is occupied by a non-Docker process." >&2
    echo "Inspect it with: sudo ss -ltnp | grep ':9090'" >&2
    return 1
  fi
}

start_testbed() {
  cd "$OPEN5GS_DIR"

  # Remove stale radio and metrics containers from previous Compose runs.
  docker rm -f nr_ue nr_gnb >/dev/null 2>&1 || true
  docker rm -f metrics >/dev/null 2>&1 || true
  check_port_9090 || return 1

  docker compose -f sa-deploy.yaml up -d || return 1
  docker compose -f nr-gnb.yaml up -d --force-recreate || return 1
  sleep 5
  docker compose -f nr-ue.yaml up -d --force-recreate || return 1
}

wait_for_ue() {
  local timeout="${1:-90}"
  local start now
  start=$(date +%s)
  while true; do
    if docker exec nr_ue ip addr show uesimtun0 >/dev/null 2>&1; then
      return 0
    fi
    now=$(date +%s)
    if (( now - start > timeout )); then
      echo "UE did not become ready within ${timeout}s" >&2
      docker logs nr_ue --tail 100 >&2 || true
      return 1
    fi
    sleep 2
  done
}

stop_radio() {
  docker rm -f nr_ue nr_gnb >/dev/null 2>&1 || true
}
