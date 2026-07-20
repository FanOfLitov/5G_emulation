from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

State = Tuple[int, ...]


@dataclass
class QLearningAgent:
    name: str
    action_count: int
    alpha: float = 0.18
    gamma: float = 0.92
    epsilon: float = 1.0
    epsilon_min: float = 0.05
    epsilon_decay: float = 0.985
    q: Dict[str, List[float]] = field(default_factory=dict)

    @staticmethod
    def _key(state: State) -> str:
        return ",".join(map(str, state))

    def _values(self, state: State) -> List[float]:
        key = self._key(state)
        if key not in self.q:
            self.q[key] = [0.0] * self.action_count
        return self.q[key]

    def act(self, state: State, *, explore: bool = True) -> int:
        if explore and random.random() < self.epsilon:
            return random.randrange(self.action_count)
        values = self._values(state)
        best = max(values)
        candidates = [i for i, value in enumerate(values) if value == best]
        return random.choice(candidates)

    def learn(self, state: State, action: int, reward: float, next_state: State) -> None:
        values = self._values(state)
        next_best = max(self._values(next_state))
        target = reward + self.gamma * next_best
        values[action] += self.alpha * (target - values[action])

    def finish_episode(self) -> None:
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "name": self.name,
            "action_count": self.action_count,
            "alpha": self.alpha,
            "gamma": self.gamma,
            "epsilon": self.epsilon,
            "epsilon_min": self.epsilon_min,
            "epsilon_decay": self.epsilon_decay,
            "q": self.q,
        }, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "QLearningAgent":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)
