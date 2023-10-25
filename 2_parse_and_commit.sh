#!/bin/bash

while true; do
  python parse_logs.py
  git pull
  git add .
  git commit -m"update server_usuage.png"
  git push
  sleep 600
done

