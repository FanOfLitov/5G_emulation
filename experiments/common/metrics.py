from __future__ import annotations
import csv, math, statistics
from pathlib import Path
from typing import Iterable


def summarize(values: Iterable[float]) -> dict[str, float]:
    vals = [float(v) for v in values]
    if not vals:
        return {"n": 0, "mean": math.nan, "std": math.nan, "median": math.nan, "ci95": math.nan}
    n = len(vals)
    std = statistics.stdev(vals) if n > 1 else 0.0
    return {
        "n": n,
        "mean": statistics.fmean(vals),
        "std": std,
        "median": statistics.median(vals),
        "ci95": 1.96 * std / math.sqrt(n) if n > 1 else 0.0,
    }


def write_rows(path: str | Path, rows: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
