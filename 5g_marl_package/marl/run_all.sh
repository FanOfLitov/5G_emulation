#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$ROOT"
MODE=${1:-simulation}
python3 -m marl5g.train
python3 -m marl5g.evaluate
python3 -m marl5g.report
if [[ "$MODE" == "live" ]]; then
  "$ROOT/scripts/start_testbed.sh"
  "$ROOT/scripts/live_probe.sh"
fi
echo "Done. See results/REPORT.md and models/."
