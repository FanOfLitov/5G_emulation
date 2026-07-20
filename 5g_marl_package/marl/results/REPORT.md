# Experiment report

Comparison of fixed baseline and learned MARL policy.

| Policy | Throughput, Mbit/s | Latency, ms | Packet loss | Privacy exposure | Global reward | Stability |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 19.31 | 41.10 | 0.0070 | 0.400 | 0.385 | 100.0% |
| marl | 45.31 | 34.68 | 0.0110 | 0.110 | 0.611 | 99.7% |

Learned-policy global reward change: **+0.226**.

> These are surrogate-training results. Final academic conclusions must use live-testbed repetitions produced by `scripts/live_probe.sh`.
