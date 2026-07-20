import csv
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "marl"))

from marl5g.environment import FiveGSimulationEnv

CONFIG_PATH = ROOT / "marl" / "config" / "experiment.json"
CONFIG = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

configurations = {
    "full_marl": (2, 1, 1),
    "qos_only": (2, 0, 0),
    "privacy_only": (0, 1, 0),
    "no_coordinator": (2, 1, 0),
    "random": None,
}

rows = []
for name, fixed_actions in configurations.items():
    rewards = []
    throughputs = []
    latencies = []
    exposures = []

    for seed in range(30):
        env = FiveGSimulationEnv(CONFIG, seed=seed)
        env.reset()

        if fixed_actions is None:
            rng = random.Random(seed)
            actions = (
                rng.randrange(len(CONFIG["qos_actions"])),
                rng.randrange(len(CONFIG["privacy_actions"])),
                rng.randrange(len(CONFIG["coordinator_actions"])),
            )
        else:
            actions = fixed_actions

        _, reward, metrics = env.step({
            "qos": actions[0],
            "privacy": actions[1],
            "coordinator": actions[2],
        })
        rewards.append(reward["coordinator"])
        throughputs.append(metrics.throughput_mbit)
        latencies.append(metrics.latency_ms)
        exposures.append(metrics.privacy_exposure)

    rows.append({
        "configuration": name,
        "mean_coordinator_reward": sum(rewards) / len(rewards),
        "mean_throughput_mbit": sum(throughputs) / len(throughputs),
        "mean_latency_ms": sum(latencies) / len(latencies),
        "mean_privacy_exposure": sum(exposures) / len(exposures),
        "repetitions": len(rewards),
    })

HERE = Path(__file__).parent
OUTPUT = HERE / "results" / "ablation.csv"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved: {OUTPUT}")
for row in rows:
    print(row)
