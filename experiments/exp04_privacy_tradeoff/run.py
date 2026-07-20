import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "marl"))

from marl5g.environment import FiveGSimulationEnv

CONFIG_PATH = ROOT / "marl" / "config" / "experiment.json"
CONFIG = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

levels = [
    ("minimal", 0),
    ("standard", 1),
    ("detailed", 2),
]

rows = []
for level_name, privacy_action in levels:
    rewards = []
    exposures = []
    throughputs = []
    latencies = []

    for seed in range(30):
        env = FiveGSimulationEnv(CONFIG, seed=seed)
        env.reset()
        _, reward, metrics = env.step({
            "qos": 2,
            "privacy": privacy_action,
            "coordinator": 1,
        })
        rewards.append(reward["coordinator"])
        exposures.append(metrics.privacy_exposure)
        throughputs.append(metrics.throughput_mbit)
        latencies.append(metrics.latency_ms)

    rows.append({
        "telemetry_level": level_name,
        "modeled_exposure": sum(exposures) / len(exposures),
        "mean_reward": sum(rewards) / len(rewards),
        "mean_throughput_mbit": sum(throughputs) / len(throughputs),
        "mean_latency_ms": sum(latencies) / len(latencies),
        "repetitions": len(rewards),
    })

HERE = Path(__file__).parent
OUTPUT = HERE / "results" / "privacy_tradeoff.csv"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved: {OUTPUT}")
for row in rows:
    print(row)
