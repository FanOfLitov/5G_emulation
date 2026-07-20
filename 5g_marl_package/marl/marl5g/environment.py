from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass
class Metrics:
    throughput_mbit: float
    latency_ms: float
    packet_loss: float
    jitter_ms: float
    cpu_percent: float
    privacy_exposure: float
    stable: bool


class FiveGSimulationEnv:
    """Fast, reproducible surrogate used to train policies before live evaluation."""

    def __init__(self, config: Dict[str, Any], seed: int = 42):
        self.config = config
        self.rng = random.Random(seed)
        self.load = 0.5
        self.channel = 0.8
        self.previous_actions = (1, 1, 1)
        self.steps = 0

    @staticmethod
    def _bin(value: float, edges: List[float]) -> int:
        return sum(value >= edge for edge in edges)

    def reset(self) -> Dict[str, Tuple[int, ...]]:
        self.load = self.rng.uniform(0.2, 0.9)
        self.channel = self.rng.uniform(0.45, 1.0)
        self.previous_actions = (1, 1, 1)
        self.steps = 0
        metrics = self._measure(*self.previous_actions)
        return self._observations(metrics)

    def _measure(self, qos_idx: int, privacy_idx: int, coordinator_idx: int) -> Metrics:
        qos = self.config["qos_actions"][qos_idx]
        privacy = self.config["privacy_actions"][privacy_idx]
        rate = float(qos["rate_mbit"])
        configured_delay = float(qos["delay_ms"])
        capacity = 115.0 * self.channel * (1.0 - 0.48 * self.load)
        throughput = min(rate, capacity) * self.rng.uniform(0.90, 1.03)
        congestion = max(0.0, rate - capacity) / max(capacity, 1.0)
        latency = configured_delay + 7.0 + 70.0 * congestion + 18.0 * self.load
        latency += self.rng.uniform(-2.0, 2.0)
        packet_loss = min(0.25, 0.004 + 0.10 * congestion + self.rng.uniform(0.0, 0.006))
        jitter = max(0.2, 0.12 * latency + self.rng.uniform(-0.8, 1.0))
        cpu = min(100.0, 18.0 + throughput * 0.38 + privacy["observability"] * 13.0)
        stable = packet_loss < 0.12 and latency < 180.0
        return Metrics(throughput, latency, packet_loss, jitter, cpu,
                       float(privacy["telemetry_exposure"]), stable)

    def _observations(self, m: Metrics) -> Dict[str, Tuple[int, ...]]:
        common = (
            self._bin(m.latency_ms, [20, 50, 100]),
            self._bin(m.packet_loss, [0.01, 0.04, 0.10]),
            self._bin(m.throughput_mbit, [15, 35, 70]),
        )
        return {
            "qos": common + (self._bin(m.cpu_percent, [35, 60, 85]),),
            "privacy": (self._bin(m.privacy_exposure, [0.2, 0.6]),) + common[:2],
            "coordinator": common + (int(m.stable), self._bin(m.privacy_exposure, [0.2, 0.6])),
        }

    def step(self, actions: Dict[str, int]):
        qos_idx = actions["qos"]
        privacy_idx = actions["privacy"]
        coordinator_idx = actions["coordinator"]
        metrics = self._measure(qos_idx, privacy_idx, coordinator_idx)

        qos_reward = (
            0.52 * min(metrics.throughput_mbit / 100.0, 1.0)
            - 0.28 * min(metrics.latency_ms / 150.0, 1.5)
            - 0.20 * min(metrics.packet_loss / 0.10, 2.0)
        )
        privacy_reward = 1.0 - metrics.privacy_exposure
        change_penalty = 0.03 * sum(a != b for a, b in zip(
            (qos_idx, privacy_idx, coordinator_idx), self.previous_actions))
        stability_reward = (1.0 if metrics.stable else -1.0) - change_penalty
        weights = self.config["coordinator_actions"][coordinator_idx]
        global_reward = (
            weights["qos_weight"] * qos_reward
            + weights["privacy_weight"] * privacy_reward
            + weights["stability_weight"] * stability_reward
        )
        rewards = {
            "qos": qos_reward + 0.25 * global_reward,
            "privacy": privacy_reward + 0.25 * global_reward,
            "coordinator": global_reward,
        }

        self.load = min(1.0, max(0.05, self.load + self.rng.uniform(-0.12, 0.12)))
        self.channel = min(1.0, max(0.30, self.channel + self.rng.uniform(-0.08, 0.08)))
        self.previous_actions = (qos_idx, privacy_idx, coordinator_idx)
        self.steps += 1
        return self._observations(metrics), rewards, metrics
