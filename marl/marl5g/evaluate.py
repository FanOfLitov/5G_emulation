from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path

from .environment import FiveGSimulationEnv
from .qlearning import QLearningAgent


def run_policy(env, config, agents, episodes, learned):
    rows = []
    for episode in range(episodes):
        obs = env.reset()
        for step in range(config["steps_per_episode"]):
            if learned:
                actions = {name: agent.act(obs[name], explore=False) for name, agent in agents.items()}
            else:
                actions = {"qos": 1, "privacy": 1, "coordinator": 1}
            obs, rewards, metrics = env.step(actions)
            rows.append({
                "policy": "marl" if learned else "baseline",
                "episode": episode,
                "step": step,
                "throughput_mbit": metrics.throughput_mbit,
                "latency_ms": metrics.latency_ms,
                "packet_loss": metrics.packet_loss,
                "privacy_exposure": metrics.privacy_exposure,
                "stable": int(metrics.stable),
                "global_reward": rewards["coordinator"],
            })
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/experiment.json")
    parser.add_argument("--models", default="models")
    parser.add_argument("--output", default="results/evaluation.csv")
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    model_dir = Path(args.models)
    agents = {name: QLearningAgent.load(model_dir / f"{name}.json")
              for name in ("qos", "privacy", "coordinator")}
    rows = []
    rows += run_policy(FiveGSimulationEnv(config, config["seed"] + 100), config, agents,
                       config["evaluation_episodes"], False)
    rows += run_policy(FiveGSimulationEnv(config, config["seed"] + 100), config, agents,
                       config["evaluation_episodes"], True)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)
    for policy in ("baseline", "marl"):
        sample = [r for r in rows if r["policy"] == policy]
        print(policy, {
            "throughput": round(statistics.mean(r["throughput_mbit"] for r in sample), 3),
            "latency": round(statistics.mean(r["latency_ms"] for r in sample), 3),
            "loss": round(statistics.mean(r["packet_loss"] for r in sample), 5),
            "privacy": round(statistics.mean(r["privacy_exposure"] for r in sample), 3),
            "reward": round(statistics.mean(r["global_reward"] for r in sample), 3),
        })

if __name__ == "__main__":
    main()
