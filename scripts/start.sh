#!/bin/bash

echo "[+] Starting 5G Network Emulator..."

docker compose -f docker/docker-compose.yml up -d

echo "[+] Done."