from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path

from .environment import FiveGSimulationEnv
from .qlearning import QLearningAgent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/experiment.json")
    parser.add_argument("--models", default="models")
    parser.add_argument("--results", default="results/training.csv")
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    random.seed(config["seed"])
    env = FiveGSimulationEnv(config, config["seed"])
    agents = {
        "qos": QLearningAgent("qos", len(config["qos_actions"])),
        "privacy": QLearningAgent("privacy", len(config["privacy_actions"])),
        "coordinator": QLearningAgent("coordinator", len(config["coordinator_actions"])),
    }

    result_path = Path(args.results)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    with result_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "episode", "reward_qos", "reward_privacy", "reward_coordinator",
            "throughput_mbit", "latency_ms", "packet_loss", "privacy_exposure"
        ])
        writer.writeheader()
        for episode in range(config["episodes"]):
            observations = env.reset()
            totals = {name: 0.0 for name in agents}
            last_metrics = None
            for _ in range(config["steps_per_episode"]):
                actions = {name: agent.act(observations[name]) for name, agent in agents.items()}
                next_obs, rewards, last_metrics = env.step(actions)
                for name, agent in agents.items():
                    agent.learn(observations[name], actions[name], rewards[name], next_obs[name])
                    totals[name] += rewards[name]
                observations = next_obs
            for agent in agents.values():
                agent.finish_episode()
            assert last_metrics is not None
            writer.writerow({
                "episode": episode,
                "reward_qos": totals["qos"],
                "reward_privacy": totals["privacy"],
                "reward_coordinator": totals["coordinator"],
                "throughput_mbit": last_metrics.throughput_mbit,
                "latency_ms": last_metrics.latency_ms,
                "packet_loss": last_metrics.packet_loss,
                "privacy_exposure": last_metrics.privacy_exposure,
            })
            if (episode + 1) % 20 == 0:
                print(f"episode={episode + 1} coordinator_reward={totals['coordinator']:.3f}")

    model_dir = Path(args.models)
    for name, agent in agents.items():
        agent.save(model_dir / f"{name}.json")
    print(f"Models saved to {model_dir}")


if __name__ == "__main__":
    main()
