#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT/marl"
./run_all.sh
cp results/evaluation.csv "$HERE/raw/evaluation.csv"
cp results/training.csv "$HERE/raw/training.csv"
cp results/REPORT.md "$HERE/results/REPORT.md"
echo "MARL and baseline outputs copied to $HERE"
