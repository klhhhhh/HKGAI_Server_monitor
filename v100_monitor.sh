#!/bin/bash
# Copyright (C) 2023.06.21 jiahaopan

# 定义服务器列表
# user=root
user=hkustadmin
servers=("10.96.164.50" "10.96.164.51" "10.96.164.52" "10.96.164.53" "10.96.164.54" "10.96.164.55" "10.96.164.56" "10.96.164.57" "10.96.164.58" "10.96.164.59")

counter=1
for server in "${servers[@]}"
do
  echo "Checking GPU memory usage and utilization on $server ($counter)"
  server_name=$user@$server
  # ssh -o ConnectTimeout=10 -p 65022 $server_name nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv
  sshpass -p 'hkust@dmin' ssh -o ConnectTimeout=10 $server_name nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv
  # ssh -o ConnectTimeout=10 -p 65022 $server_name uptime
  ((counter++))
done
