#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
STACK_DIR=${STACK_DIR:-$ROOT/external/docker_open5gs}
cd "$STACK_DIR"
[[ -f .env ]] || { echo "Missing $STACK_DIR/.env" >&2; exit 1; }
docker compose -f sa-deploy.yaml up -d
for name in amf smf upf mongo webui; do
  for _ in $(seq 1 60); do docker inspect -f '{{.State.Running}}' "$name" 2>/dev/null | grep -q true && break; sleep 2; done
done
docker compose -f nr-gnb.yaml up -d --force-recreate
for _ in $(seq 1 30); do docker logs nr_gnb 2>&1 | grep -q 'NG Setup procedure is successful' && break; sleep 2; done
docker compose -f nr-ue.yaml up -d --force-recreate
for _ in $(seq 1 45); do docker exec nr_ue ip link show uesimtun0 >/dev/null 2>&1 && { echo '5G testbed is ready'; exit 0; }; sleep 2; done
echo 'UE did not create uesimtun0. Check subscriber and docker logs nr_ue.' >&2
exit 1
