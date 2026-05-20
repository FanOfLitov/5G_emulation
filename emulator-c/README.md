# 5G Network Emulator

Виртуальная среда для эмуляции 5G SA сети под Linux/WSL с использованием Docker, Open5GS, UERANSIM и собственного C-модуля.

## Цель

Разработать среду для исследования работы 5G сети в виртуальной инфраструктуре.

## Стек

- Windows + WSL Ubuntu
- VS Code
- Docker / Docker Compose
- Open5GS
- UERANSIM
- C

## Структура

- `docker/` — контейнеры 5G Core и UE/RAN
- `emulator-c/` — собственный C-модуль
- `docs/` — документация и схемы
- `scripts/` — скрипты запуска