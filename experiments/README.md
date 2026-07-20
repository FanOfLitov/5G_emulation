# Experimental evaluation

This directory contains reproducible experiments for the Open5GS + UERANSIM + MARL project.

## Experiments

| ID | Experiment | Environment |
|---|---|---|
| exp01 | Baseline startup, RTT and loss | Live testbed |
| exp02 | MARL versus fixed baseline | Surrogate MARL environment |
| exp03 | Response to changing network conditions | Live testbed + `tc netem` |
| exp04 | Privacy/QoS trade-off | Surrogate MARL environment |
| exp05 | Agent ablation study | Surrogate MARL environment |
| exp06 | Zero-touch startup time | Live testbed |
| exp07 | Q-learning/EXP3/DQN comparison scaffold | Mixed; only Q-learning currently implemented |

## Quick start

From the repository root:

```bash
chmod +x run_experiments.sh experiments/*/run.sh experiments/common/testbed.sh
./run_experiments.sh exp02
```

Surrogate experiments that do not restart Docker:

```bash
./run_experiments.sh all
```

Live experiments:

```bash
./run_experiments.sh exp01
./run_experiments.sh exp03
./run_experiments.sh exp06
```

The Open5GS subscriber must already exist in MongoDB, as in the working testbed setup.

## Repetitions

For debugging use 3–5 repetitions. For final results use at least 20 repetitions and report mean, standard deviation, median and a 95% confidence interval.

## Result policy

- `raw/` contains original measurements.
- `results/` contains summaries and reports.
- Surrogate measurements must not be described as physical testbed measurements.
- Secret subscriber fields such as `K`, `OP/OPc` and authentication material must never be written to results.
