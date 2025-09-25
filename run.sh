#!/bin/bash

# 函数：更新或追加键值对到.env文件
update_or_append_to_env() {
  local key=$1
  local value=$2
  local env_file=".env"

  # 如果不存在.env文件，则创建
  if [ ! -f "$env_file" ]; then
    touch "$env_file"
  fi

  # 确保文件以换行符结束
  sed -i'' -e '$a\' "$env_file"

  # 检查键是否存在于.env文件中
  if grep -q "^${key}=" "$env_file"; then
    # 如果键存在，则更新它的值
    if [[ "$OSTYPE" == "darwin"* ]]; then
      # macOS (BSD sed)
      sed -i '' "/^${key}=/c\\
${key}=${value}" "$env_file"
    else
      # Linux (GNU sed)
      sed -i "/^${key}=/c\\${key}=${value}" "$env_file"
    fi
  else
    # 如果键不存在，则追加键值对到文件
    echo "${key}=${value}" >> "$env_file"
  fi

  # 再次确保文件以换行符结束
  sed -i'' -e '$a\' "$env_file"
}

# 定义颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color


# 检测支持的 Docker Compose 命令
if docker compose version &>/dev/null; then
  DOCKER_COMPOSE_CMD="docker compose"
elif docker-compose version &>/dev/null; then
  DOCKER_COMPOSE_CMD="docker-compose"
else
  echo "无法找到 'docker compose' 或 'docker-compose' 命令。"
  exit 1
fi


# 命令说明
usage() {
    echo "Usage: $0 [-i <device_id>]"
    echo " -i <device_id>: Specify GPU device_id"
    exit 1
}


# 默认 device_id
device_id="-1"
while getopts "i:" opt; do
    case $opt in
        i) device_id=$OPTARG ;;
        *) usage ;;
    esac
done


# 检查device_id是否是0-9或-1，如果device_id是-1，则提示在cpu上启动
if [[ ! $device_id =~ ^[0-9]|-1$ ]]; then
    echo "device_id 必须是0-9或-1"
    exit 1
fi
echo "device_id=${device_id}"
if [[ $device_id == "-1" ]]; then
    echo "将在CPU上启动服务"
else
    echo "将在GPU $device_id 上启动服务"
fi


# 读取和添加环境变量中的用户信息
update_or_append_to_env "GPUID" "$device_id"
ip="localhost"
update_or_append_to_env "USER_IP" "$ip"
GATEWAY_IP=$(hostname -I | awk '{print $1}')
update_or_append_to_env "GATEWAY_IP" "$GATEWAY_IP"
source .env

# 检查操作系统类型，cpu类型，启动不同版本的docker compose文件
if [ -e /proc/version ]; then
  if grep -qi MINGW /proc/version; then
    echo "当前版本不支持 Windows，请在 Linux 环境下运行此脚本"
    exit 1
  else
    echo "Running under native Linux"

    # 检查CPU架构
    ARCH=$(uname -m)
    if [[ "$ARCH" == "x86_64" || "$ARCH" == "i686" || "$ARCH" == "i386" ]]; then
      echo "Detected x86_64 architecture"
      if [[ $device_id == "-1" ]]; then
        sudo $DOCKER_COMPOSE_CMD -f docker-compose-linux-cpu.yaml up -d
      else
        sudo $DOCKER_COMPOSE_CMD -f docker-compose-linux-gpu.yaml up -d
      fi
    elif [[ "$ARCH" == "aarch64" ]]; then
      echo "Detected aarch64 architecture"
      if [[ $device_id == "-1" ]]; then
        sudo $DOCKER_COMPOSE_CMD -f docker-compose-linux-arm.yaml up -d
      else
        sudo $DOCKER_COMPOSE_CMD -f docker-compose-linux-npu.yaml up -d
      fi
    else
      echo "Unsupported architecture: $ARCH"
    fi
  fi
else
  echo "Running under Macos"
  sudo $DOCKER_COMPOSE_CMD -f docker-compose-mac.yaml up -d
  sudo $DOCKER_COMPOSE_CMD -f docker-compose-mac.yaml logs -f qanything_local
fi
