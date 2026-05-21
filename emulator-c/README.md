# 5G SA Network Emulator using Open5GS + UERANSIM

## Описание проекта

Данный проект представляет собой полноценный программный эмулятор сети 5G Standalone (5G SA), построенный на базе:

* Open5GS
* UERANSIM
* Docker / Docker Compose
* MongoDB
* Grafana

Система позволяет:

* эмулировать UE (User Equipment)
* запускать gNB (5G базовую станцию)
* поднимать ядро 5G Core
* устанавливать PDU Session
* создавать пользовательский туннель
* обеспечивать выход UE в интернет через UPF

---

# Архитектура системы

```text
                         +-------------------+
                         |     Internet      |
                         +---------+---------+
                                   |
                                   |
                             +-----+------+
                             |    UPF     |
                             +-----+------+
                                   |
                    +--------------+--------------+
                    |                             |
             +------+-----+               +------+------+
             |    SMF     |               |     AMF     |
             +------+-----+               +------+------+
                    |                             |
                    |                     +-------+-------+
                    |                     |               |
             +------+-----+         +-----+-----+   +-----+-----+
             |    NRF     |         |    UDM    |   |    AUSF   |
             +------------+         +-----------+   +-----------+
                                             |
                                      +------+------+
                                      |     UDR     |
                                      +-------------+

                ================= 5G CORE =================

                              |
                              |
                        NGAP / GTP-U
                              |
                       +------+------+
                       |     gNB     |
                       +------+------+
                              |
                         Radio Link
                              |
                       +------+------+
                       |      UE     |
                       +-------------+
```

---

# Используемые технологии

| Компонент        | Назначение                      |
| ---------------- | ------------------------------- |
| Open5GS          | Реализация 5G Core              |
| UERANSIM         | Эмуляция UE и gNB               |
| Docker           | Контейнеризация                 |
| MongoDB          | База данных подписчиков         |
| Grafana          | Мониторинг                      |
| Linux Networking | NAT, routing, tunnel interfaces |

---

# Компоненты 5G Core

| Компонент | Назначение                         |
| --------- | ---------------------------------- |
| AMF       | Registration и mobility management |
| SMF       | Управление PDU Session             |
| UPF       | User Plane Forwarding              |
| UDM       | Subscriber data                    |
| UDR       | Хранилище данных UE                |
| AUSF      | Authentication                     |
| NRF       | Discovery сервис                   |
| NSSF      | Network slicing                    |
| PCF       | Policy control                     |

---

# Структура проекта

```text
5g-network-emulator/
│
├── docker/
├── docs/
├── scripts/
├── emulator-c/
│
├── external/
│   └── docker_open5gs/
│       ├── amf/
│       ├── smf/
│       ├── upf/
│       ├── ueransim/
│       ├── nrf/
│       ├── webui/
│       ├── nr-gnb.yaml
│       ├── nr-ue.yaml
│       └── .env
│
└── README.md
```

---

# Параметры сети

## PLMN

```text
MCC = 001
MNC = 01
```

## TAC

```text
TAC = 1
```

## IMSI

```text
001011234567895
```

---

# Конфигурация UE

Файл:

```text
/UERANSIM/config/ueransim-ue.yaml
```

Конфигурация:

```yaml
supi: 'imsi-001011234567895'

mcc: '001'
mnc: '01'

key: '8baf473f2f8fd09487cccbd7097c6862'

op: '11111111111111111111111111111111'
opType: 'OP'

amf: '8000'

imei: '356938035643803'
imeiSv: '4370816125816151'
```

---

# Конфигурация gNB

Файл:

```text
/UERANSIM/config/ueransim-gnb.yaml
```

```yaml
mcc: '001'
mnc: '01'

tac: 1
```

---

# Настройка Subscriber в Open5GS WebUI

## Данные Subscriber

| Поле    | Значение                         |
| ------- | -------------------------------- |
| IMSI    | 001011234567895                  |
| Key     | 8baf473f2f8fd09487cccbd7097c6862 |
| OP Type | OP                               |
| OP      | 11111111111111111111111111111111 |
| AMF     | 8000                             |
| APN     | internet                         |
| SST     | 1                                |

---

# Запуск системы

## 1. Запуск Core

```bash
docker compose up -d
```

---

## 2. Запуск gNB

```bash
docker compose -f nr-gnb.yaml up -d
```

---

## 3. Запуск UE

```bash
docker compose -f nr-ue.yaml up -d
```

---

# Проверка регистрации UE

## Логи UE

```bash
docker logs -f nr_ue
```

Успешная регистрация:

```text
Initial Context Setup Request received
PDU session resource(s) setup
```

---

# Проверка туннеля

```bash
docker exec -it nr_ue ip addr
```

Ожидаемый интерфейс:

```text
uesimtun0
inet 192.168.100.2/32
```

---

# Проверка интернета

```bash
docker exec -it nr_ue ping -I uesimtun0 8.8.8.8
```

---

# Реализованный datapath

```text
UE
 ↓
uesimtun0
 ↓
gNB
 ↓
NG-U
 ↓
UPF
 ↓
NAT
 ↓
Internet
```

---

# Основные ошибки и их исправление

## 1. FIVEG_SERVICES_NOT_ALLOWED

### Причина

Несовпадение MCC/MNC.

### Решение

Убедиться, что:

```text
UE == gNB == AMF == Subscriber
```

используют одинаковые:

```text
MCC = 001
MNC = 01
```

---

## 2. Cannot find IMSI in DB

### Причина

Subscriber отсутствует в MongoDB/Open5GS.

### Решение

Добавить subscriber через WebUI.

---

## 3. SQN out of range

### Причина

Неверно настроены OP/OPC.

### Решение

Если используется:

```text
opType: OP
```

то в WebUI нужно указывать:

```text
OP
```

а не OPC.

---

# Проверка контейнеров

```bash
docker ps
```

---

# Полезные команды

## Просмотр логов AMF

```bash
docker logs amf --tail 100
```

## Просмотр логов gNB

```bash
docker logs nr_gnb --tail 100
```

## Просмотр логов UE

```bash
docker logs nr_ue --tail 100
```

---

# Проверка маршрутизации

```bash
docker exec -it nr_ue ip route
```

---

# Проверка NAT

```bash
iptables -t nat -L
```

---

# Проверка интерфейсов UPF

```bash
docker exec -it upf ip addr
```

---

# Проверка connectivity

```bash
docker exec -it nr_ue ping 192.168.100.1
docker exec -it nr_ue ping 8.8.8.8
```

---

# Итог

В результате работы был реализован полноценный программный эмулятор 5G SA сети с:

* UE registration
* Authentication
* PDU Session Establishment
* User Plane tunnel
* Internet connectivity
* Docker orchestration
* Open5GS Core
* UERANSIM RAN

Система успешно обеспечивает обмен пользовательским трафиком через UPF с выходом в интернет.

---


# Лицензия

Educational / Research Use
