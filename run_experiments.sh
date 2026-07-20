#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
exp="${1:-all}"
case "$exp" in
  exp01) ./experiments/exp01_baseline/run.sh ;;
  exp02) ./experiments/exp02_marl_vs_baseline/run.sh ;;
  exp03) ./experiments/exp03_dynamic_load/run.sh ;;
  exp04) ./experiments/exp04_privacy_tradeoff/run.sh ;;
  exp05) ./experiments/exp05_agent_ablation/run.sh ;;
  exp06) ./experiments/exp06_zero_touch_startup/run.sh ;;
  exp07) ./experiments/exp07_algorithm_comparison/run.sh ;;
  all)
    ./experiments/exp02_marl_vs_baseline/run.sh
    ./experiments/exp04_privacy_tradeoff/run.sh
    ./experiments/exp05_agent_ablation/run.sh
    ./experiments/exp07_algorithm_comparison/run.sh
    echo "Hardware/live experiments exp01, exp03 and exp06 are not included in 'all' to avoid repeated Docker restarts. Run them explicitly."
    ;;
  *) echo "Usage: $0 {exp01|exp02|exp03|exp04|exp05|exp06|exp07|all}"; exit 2 ;;
esac
