# Adaptive 5G Stack Configuration Using Multi-Agent Reinforcement Learning

## Description

This project implements an experimental 5G Standalone (SA) network based on Open5GS and UERANSIM and extends it with a Multi-Agent Reinforcement Learning (MARL) framework for adaptive network parameter tuning.

The system combines:

- Open5GS 5G Core
- UERANSIM UE and gNB
- Docker-based deployment
- Multi-Agent Reinforcement Learning
- Automatic experiment execution
- Report generation

The project was developed as an experimental platform for studying adaptive optimization of 5G network parameters using reinforcement learning.

---

# Project Structure

```
5G_emulation/

├── emulator-c/             # Network emulator
├── external/
│   └── docker_open5gs/      # Open5GS + UERANSIM deployment
│
├── marl/                   # Multi-Agent RL framework
│   ├── marl5g/
│   │   ├── environment.py
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   ├── report.py
│   │   └── qlearning.py
│   │
│   ├── models/
│   ├── results/
│   ├── scripts/
│   ├── config/
│   └── run_all.sh
│
├── scripts/
├── docs/
└── README.md
```

---

# Architecture

```
              +----------------+
              |   MARL System  |
              +----------------+

        +----------+----------+----------+
        |                     |          |
        v                     v          v

   QoS Agent          Privacy Agent   Coordinator

        \                 |            /
         \                |           /
          +---------------+----------+
                          |
                    Global Reward
                          |
                          v

               Open5GS + UERANSIM

          AMF
          SMF
          UPF
          NRF
          gNB
          UE
```

---

# Multi-Agent Reinforcement Learning

The system contains three independent agents.

## QoS Agent

Responsible for improving network performance.

Observes:

- throughput
- latency
- packet loss
- jitter

Objective:

maximize network performance.

---

## Privacy Agent

Responsible for privacy-aware optimization.

Observes:

- privacy level
- telemetry level
- security metrics

Objective:

reduce privacy exposure while preserving performance.

---

## Coordinator Agent

Combines local rewards into a global optimization objective.

Global reward:

```
Reward =
0.5 × QoS
+
0.3 × Privacy
+
0.2 × Stability
```

---

# Reinforcement Learning

Current implementation:

- Q-Learning

Saved models:

```
models/

qos.json
privacy.json
coordinator.json
```

---

# Experimental Testbed

The experimental 5G network consists of

- Open5GS Core
- MongoDB
- WebUI
- UERANSIM gNB
- UERANSIM UE

After successful deployment:

```
UE
↓

gNB

↓

AMF

↓

SMF

↓

UPF

↓

Internet
```

---

# Installation

Clone repository

```bash
git clone <repository>
cd 5G_emulation
```

Install Python dependencies

```bash
cd marl

pip install -r requirements.txt
```

---

# Running Experiments

## Training only

```bash
cd marl

./run_all.sh
```

This command

- trains agents
- evaluates policies
- generates report
- stores trained models

---

## Training + Live Testbed

```bash
cd marl

./run_all.sh live
```

This additionally

- starts Open5GS
- starts gNB
- starts UE
- waits for successful registration
- collects live metrics

---

# Generated Results

Training:

```
results/training.csv
```

Evaluation:

```
results/evaluation.csv
```

Live measurements:

```
results/live_probe.csv
```

Automatic report:

```
results/REPORT.md
```

---

# Output Models

```
models/

qos.json

privacy.json

coordinator.json
```

---

# Example Workflow

```
Start Open5GS

↓

Train MARL agents

↓

Evaluate learned policies

↓

Deploy learned policy

↓

Collect live metrics

↓

Generate report
```

---

# Technologies

- Python
- Docker
- Open5GS
- UERANSIM
- Reinforcement Learning
- Q-Learning
- Multi-Agent Systems

---

# Future Work

Possible extensions include

- PPO

- MAPPO

- MADDPG

- Dynamic network slicing

- Online learning

- Real-time policy adaptation

---

# Author

Experimental implementation of

Adaptive 5G Stack Configuration Using Multi-Agent Reinforcement Learning.
