#!/bin/bash

# 检查logs目录是否存在，如果不存在则创建
if [ ! -d "logs" ]; then
  mkdir logs
fi

while true; do
  # 获取当前的时间戳
  timestamp=$(date +"%Y%m%d%H%M%S")
  
  # 调用v100_monitor.sh并将结果保存到logs目录下的时间戳命名的文件中
  echo "Start monitoring at $timestamp"
  ./v100_monitor.sh > logs/$timestamp.txt
  echo "Finished monitoring at $timestamp"
  
  # 等待60秒
  sleep 60
done

