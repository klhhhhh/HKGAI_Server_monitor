import os
import re
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np



def parse_txt_to_json(path):
    # Sample log data (replace with your actual log data)
    with open(path, "r") as ff:
        log_data = ff.readlines()
        log_data = "".join(log_data)

    # Regular expressions to extract necessary information
    server_pattern = re.compile(r"Checking GPU memory usage and utilization on (\d+\.\d+\.\d+\.\d+)")
    gpu_pattern = re.compile(r"(\d+ MiB), (\d+ MiB), (\d+ %)")
    cpu_pattern = re.compile(r"(\d+:\d+:\d+) up (\d+ days?,\s+\d+:\d+),\s+\d+ users,\s+load average: (\d+\.\d+), (\d+\.\d+), (\d+\.\d+)")

    # Parsing the log data
    parsed_data = {}
    servers = server_pattern.findall(log_data)
    gpu_infos = gpu_pattern.findall(log_data)
    cpu_infos = cpu_pattern.findall(log_data)

    # Split the GPU info into chunks of 8 for each server
    gpu_chunks = [gpu_infos[i:i+8] for i in range(0, len(gpu_infos), 8)]

    # Construct the parsed data structure
    for server, gpu_chunk in zip(servers, gpu_chunks):
        parsed_data[server] = {
            "gpu": [
                {
                    "memory_used": gpu_info[0],
                    "memory_total": gpu_info[1],
                    "utilization_gpu": gpu_info[2]
                } 
                for gpu_info in gpu_chunk
            ],
            # "cpu": {
            #     "uptime": f"{cpu_info[1]}, {cpu_info[0]}",
            #     "load_average": [cpu_info[2], cpu_info[3], cpu_info[4]]
            # }
        }

    # Convert the parsed data to a JSON string
    json_data = json.dumps(parsed_data)
    return json_data


def filter_recent_logs(logs_list, duration=360):
    # 获取当前时间
    now = datetime.now()
    # 计算1小时之前的时间
    one_hour_ago = now - timedelta(seconds=duration)
    
    recent_logs = []
    for log in logs_list:
        # 提取日志文件中的日期和时间
        log_time = datetime.strptime(log[:-4], "%Y%m%d%H%M%S")
        
        # 判断日志文件的时间是否在最近1小时内
        if log_time > one_hour_ago:
            recent_logs.append(log)
            
    return recent_logs

########### plot #############
# 提取每个服务器的GPU使用率
def get_usuage(input_jsonl, name_mapper):

    server_gpu_usage = {}

    with open(input_jsonl, 'r') as file:
        for line in file:
            # 解析每一行JSON数据
            log_entry = json.loads(line)

            # 遍历日志条目中的每个服务器
            for server_ip, server_info in log_entry.items():
                gpu_usages = [
                    int(gpu_info['utilization_gpu'].rstrip(' %'))  # 移除百分比符号并转换为整数
                    for gpu_info in server_info['gpu']
                ]
                avg_gpu_usages = sum(gpu_usages) / len(gpu_usages)
                server_name = name_mapper[server_ip]
                if server_name in server_gpu_usage:
                    server_gpu_usage[server_name].append(avg_gpu_usages)
                else:
                    server_gpu_usage[server_name] = [avg_gpu_usages]
    return server_gpu_usage


# 绘制数据

def save_plot(server_gpu_usage, duration):
    # 计算每个服务器的总平均使用率
    overall_average_usage = {server_name: np.mean(usages) for server_name, usages in server_gpu_usage.items()}

    # 使用一个更为鲜艳的颜色映射
    colors = plt.cm.tab20(np.linspace(0, 1, len(server_gpu_usage)))

    # 绘制数据
    plt.figure(figsize=(15, 7))
    for (server_name, usages), color in zip(server_gpu_usage.items(), colors):
        plt.plot(usages, label=f"{server_name} (Avg: {overall_average_usage[server_name]:.2f}%)", color=color)


    # 设置图表属性
    plt.title(f"GPU Usage of previous {duration}s per Server")
    plt.xlabel("Time Points")
    plt.ylabel("GPU Usage (%)")
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    plt.tight_layout()
    plt.savefig("./server_usuage.png")



################## main ###############
DURATION = 3600
MAPPER = {
    # "36.133.54.208": "v100s001",
    # "36.133.54.135": "v100s002",
    # "36.133.54.47": "v100s003",
    # "36.133.54.229": "v100s004",
    # "36.134.24.117": "v100s005",
    # "36.134.25.168": "v100s006",
    # "36.138.58.42": "v100s007",
    # "36.138.58.66": "v100s008",
    "10.96.164.50": "USTDGXH800127-001",
    "10.96.164.51": "USTDGXH800127-002",
    "10.96.164.52": "USTDGXH800127-003",
    "10.96.164.53": "USTDGXH800127-004",
    "10.96.164.54": "USTDGXH800127-005",
    "10.96.164.55": "USTDGXH800127-006",
    "10.96.164.56": "USTDGXH800127-007",
    "10.96.164.57": "USTDGXH800127-008",
    "10.96.164.58": "USTDGXH800127-009",
    "10.96.164.59": "USTDGXH800127-010",
}

logs = os.listdir("./logs")
logs.sort()

logs = filter_recent_logs(logs, duration=DURATION)
logs = [parse_txt_to_json(os.path.join("logs", log)) for log in logs]

with open("log.jsonl", "w") as ff:
    for line in logs:
        ff.write(line + "\n")

server_gpu_usage = get_usuage('log.jsonl', MAPPER)
save_plot(server_gpu_usage, DURATION)
