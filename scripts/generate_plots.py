#!/usr/bin/env python3
"""Generate reproducible PNG figures from available project CSV files."""
from __future__ import annotations

import csv
import math
from pathlib import Path
from statistics import mean

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "figures"
OUT.mkdir(parents=True, exist_ok=True)


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        print(f"skip: {path.relative_to(ROOT)}")
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def number(row: dict[str, str], key: str) -> float | None:
    try:
        value = float(row[key])
        return value if math.isfinite(value) else None
    except (KeyError, TypeError, ValueError):
        return None


def save(name: str) -> None:
    plt.tight_layout()
    path = OUT / name
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()
    print(f"saved: {path.relative_to(ROOT)}")


def plot_training() -> None:
    rows = read_rows(ROOT / "marl/results/training.csv")
    if not rows:
        return
    x = [number(r, "episode") for r in rows]
    reward = [number(r, "reward_coordinator") for r in rows]
    points = [(a, b) for a, b in zip(x, reward) if a is not None and b is not None]
    if not points:
        return
    plt.figure(figsize=(9, 5))
    plt.plot([p[0] for p in points], [p[1] for p in points], label="Coordinator reward", alpha=0.5)
    window = 10
    if len(points) >= window:
        rolling = [mean([points[j][1] for j in range(i - window + 1, i + 1)]) for i in range(window - 1, len(points))]
        plt.plot([points[i][0] for i in range(window - 1, len(points))], rolling, label=f"Moving average ({window})")
    plt.xlabel("Episode")
    plt.ylabel("Reward")
    plt.title("MARL training reward")
    plt.grid(True, alpha=0.3)
    plt.legend()
    save("training_reward.png")


def evaluation_groups() -> dict[str, list[dict[str, str]]]:
    rows = read_rows(ROOT / "marl/results/evaluation.csv")
    groups: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        groups.setdefault(row.get("policy", "unknown"), []).append(row)
    return groups


def plot_policy_metric(metric: str, title: str, ylabel: str, filename: str) -> None:
    groups = evaluation_groups()
    if not groups:
        return
    labels, values = [], []
    for policy, rows in sorted(groups.items()):
        data = [v for r in rows if (v := number(r, metric)) is not None]
        if data:
            labels.append(policy)
            values.append(mean(data))
    if not labels:
        return
    plt.figure(figsize=(7, 5))
    plt.bar(labels, values)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, axis="y", alpha=0.3)
    save(filename)


def plot_baseline() -> None:
    rows = read_rows(ROOT / "experiments/exp01_baseline/results/summary.csv")
    if not rows:
        return
    labels, values = [], []
    for row in rows:
        value = number(row, "mean")
        if value is not None:
            labels.append(row.get("metric", "metric"))
            values.append(value)
    if not labels:
        return
    plt.figure(figsize=(9, 5))
    plt.bar(labels, values)
    plt.ylabel("Mean value")
    plt.title("Live baseline metrics")
    plt.xticks(rotation=20, ha="right")
    plt.grid(True, axis="y", alpha=0.3)
    save("baseline_metrics.png")


def plot_simple_category(path: Path, category_candidates: list[str], value_candidates: list[str], title: str, ylabel: str, filename: str) -> None:
    rows = read_rows(path)
    if not rows:
        return
    category = next((c for c in category_candidates if c in rows[0]), None)
    value = next((c for c in value_candidates if c in rows[0]), None)
    if category is None or value is None:
        print(f"skip schema: {path.relative_to(ROOT)}")
        return
    labels, values = [], []
    for row in rows:
        v = number(row, value)
        if v is not None:
            labels.append(row.get(category, "unknown"))
            values.append(v)
    plt.figure(figsize=(9, 5))
    plt.bar(labels, values)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=20, ha="right")
    plt.grid(True, axis="y", alpha=0.3)
    save(filename)


def plot_dynamic() -> None:
    rows = read_rows(ROOT / "experiments/exp03_dynamic_load/raw/timeline.csv")
    if not rows:
        return
    x_key = next((k for k in ("elapsed_seconds", "time_seconds", "step", "timestamp") if k in rows[0]), None)
    y_key = next((k for k in ("rtt_ms", "latency_ms", "packet_loss_percent") if k in rows[0]), None)
    if not x_key or not y_key:
        print("skip schema: dynamic load")
        return
    xs, ys = [], []
    for i, row in enumerate(rows):
        x = number(row, x_key)
        y = number(row, y_key)
        if y is not None:
            xs.append(i if x is None else x)
            ys.append(y)
    plt.figure(figsize=(10, 5))
    plt.plot(xs, ys, marker="o")
    plt.xlabel(x_key)
    plt.ylabel(y_key)
    plt.title("Dynamic network conditions")
    plt.grid(True, alpha=0.3)
    save("dynamic_load.png")


def plot_zero_touch() -> None:
    series_dir = ROOT / "experiments/exp06_zero_touch_startup/raw/series"
    paths = sorted(series_dir.glob("run_*.csv")) if series_dir.exists() else []
    if not paths:
        one = ROOT / "experiments/exp06_zero_touch_startup/raw/startup.csv"
        paths = [one] if one.exists() else []
    values = []
    for path in paths:
        rows = read_rows(path)
        for row in rows:
            v = number(row, "total_seconds")
            if v is not None:
                values.append(v)
    if not values:
        return
    plt.figure(figsize=(9, 5))
    plt.plot(range(1, len(values) + 1), values, marker="o")
    plt.xlabel("Run")
    plt.ylabel("Startup time, s")
    plt.title("Zero-touch 5G startup time")
    plt.grid(True, alpha=0.3)
    save("zero_touch_startup.png")


def main() -> None:
    plot_training()
    plot_policy_metric("global_reward", "Mean global reward by policy", "Global reward", "policy_reward.png")
    plot_policy_metric("throughput_mbit", "Mean throughput by policy", "Throughput, Mbps", "policy_throughput.png")
    plot_policy_metric("latency_ms", "Mean latency by policy", "Latency, ms", "policy_latency.png")
    plot_policy_metric("privacy_exposure", "Mean privacy exposure by policy", "Privacy exposure", "policy_privacy.png")
    plot_baseline()
    plot_simple_category(
        ROOT / "experiments/exp04_privacy_tradeoff/results/privacy_tradeoff.csv",
        ["telemetry_level", "profile", "privacy_level"],
        ["mean_reward", "global_reward", "reward"],
        "QoS/privacy trade-off",
        "Mean reward",
        "privacy_tradeoff.png",
    )
    plot_simple_category(
        ROOT / "experiments/exp05_agent_ablation/results/ablation.csv",
        ["configuration", "variant", "policy"],
        ["mean_reward", "global_reward", "reward"],
        "Agent ablation study",
        "Mean reward",
        "agent_ablation.png",
    )
    plot_dynamic()
    plot_zero_touch()


if __name__ == "__main__":
    main()
