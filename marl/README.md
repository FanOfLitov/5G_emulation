# Adaptive 5G Stack Tuning with Multi-Agent Reinforcement Learning

Учебно-исследовательский MVP многоагентной RL-системы для адаптивной настройки экспериментального стенда **Open5GS + UERANSIM**.

## Архитектура

Три табличных Q-learning агента обучаются совместно:

- **QoS agent** выбирает профиль ограничения скорости и задержки;
- **Privacy agent** выбирает уровень детализации телеметрии;
- **Coordinator agent** выбирает веса многокритериальной награды.

Локальные награды объединяются с глобальной наградой, учитывающей throughput, latency, packet loss, privacy exposure и стабильность.

## Быстрый запуск

Из корня репозитория:

```bash
chmod +x marl/run_all.sh
./marl/run_all.sh
```

Команда обучит агентов, проведёт сравнение с фиксированной baseline-конфигурацией и создаст:

- `marl/models/*.json` — Q-таблицы агентов;
- `marl/results/training.csv` — ход обучения;
- `marl/results/evaluation.csv` — результаты эксперимента;
- `marl/results/REPORT.md` — итоговая таблица.

Для запуска вместе с уже настроенным стендом:

```bash
./marl/run_all.sh live
```

Скрипт поднимет `sa-deploy.yaml`, gNB и UE, дождётся `uesimtun0`, затем добавит реальные измерения в `results/live_probe.csv`.

> Subscriber с IMSI и ключами должен один раз существовать в MongoDB/Open5GS WebUI. Docker volume сохраняет его между запусками. Скрипт намеренно не генерирует секретные ключи и не перезаписывает существующую подписку.

## Требования

- Python 3.9+;
- Docker и Docker Compose;
- рабочая директория `external/docker_open5gs`;
- для live-режима: зарегистрированный subscriber и доступный `uesimtun0`.

Внешние Python-библиотеки для MVP не нужны.

## Воспроизводимый эксперимент

Параметры находятся в `config/experiment.json`: seed, число эпизодов, действия агентов и веса награды. Baseline и MARL запускаются на одинаковой последовательности состояний благодаря одинаковому seed.

```bash
python3 -m marl5g.train
python3 -m marl5g.evaluate
python3 -m marl5g.report
```

## Ограничения MVP

Обучение выполняется на быстрой surrogate-модели сети, чтобы не разрушать регистрацию UE тысячами действий. На стенде выполняется проверка обученной системы и сбор реальных метрик. Следующий этап — live environment с `tc/netem`, `iperf3`, безопасным rollback и MAPPO.

## Git

```bash
git add marl
git commit -m "feat: add multi-agent RL tuning experiments for 5G testbed"
git push
```
