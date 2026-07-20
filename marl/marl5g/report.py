from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from pathlib import Path


def main():
    path = Path("results/evaluation.csv")
    groups = defaultdict(list)
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            groups[row["policy"]].append(row)
    lines = ["# Experiment report", "", "Comparison of fixed baseline and learned MARL policy.", "",
             "| Policy | Throughput, Mbit/s | Latency, ms | Packet loss | Privacy exposure | Global reward | Stability |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    summary = {}
    for name in ("baseline", "marl"):
        rows = groups[name]
        values = {
            "throughput": statistics.mean(float(r["throughput_mbit"]) for r in rows),
            "latency": statistics.mean(float(r["latency_ms"]) for r in rows),
            "loss": statistics.mean(float(r["packet_loss"]) for r in rows),
            "privacy": statistics.mean(float(r["privacy_exposure"]) for r in rows),
            "reward": statistics.mean(float(r["global_reward"]) for r in rows),
            "stability": statistics.mean(int(r["stable"]) for r in rows),
        }
        summary[name] = values
        lines.append(f"| {name} | {values['throughput']:.2f} | {values['latency']:.2f} | {values['loss']:.4f} | {values['privacy']:.3f} | {values['reward']:.3f} | {values['stability']:.1%} |")
    improvement = summary["marl"]["reward"] - summary["baseline"]["reward"]
    lines += ["", f"Learned-policy global reward change: **{improvement:+.3f}**.", "",
              "> These are surrogate-training results. Final academic conclusions must use live-testbed repetitions produced by `scripts/live_probe.sh`."]
    Path("results/REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("results/REPORT.md generated")

if __name__ == "__main__":
    main()
