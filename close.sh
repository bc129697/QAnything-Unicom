#!/bin/bash


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
    echo "Usage: $0 [-v, -h]"
    echo " -v: 删除容器数据卷"
    echo " -h: 显示帮助信息"
    exit 1
}

del_volume=""
while getopts "vh" opt; do
    case $opt in
        v) del_volume="-v" ;;
        *) usage ;;
    esac
done


# 检查操作系统类型，cpu类型，启动不同版本的docker compose文件
if [ -e /proc/version ]; then
  if grep -qi microsoft /proc/version || grep -qi MINGW /proc/version; then
    # 不支持Windows
    echo "当前版本不支持Windows，请在Linux环境下运行此脚本"
  else
    echo "Running under native Linux"

    # 检查CPU架构
    ARCH=$(uname -m)
    if [[ "$ARCH" == "x86_64" || "$ARCH" == "i686" || "$ARCH" == "i386" ]]; then
      echo "Detected x86_64 architecture"
      if [[ $device_id == "-1" ]]; then
        sudo $DOCKER_COMPOSE_CMD -f docker-compose-linux-cpu.yaml down $del_volume
      else
        sudo $DOCKER_COMPOSE_CMD -f docker-compose-linux-gpu.yaml down $del_volume
      fi
    elif [[ "$ARCH" == "aarch64" ]]; then
      echo "Detected aarch64 architecture"
      if [[ $device_id == "-1" ]]; then
        sudo $DOCKER_COMPOSE_CMD -f docker-compose-linux-arm.yaml down $del_volume
      else
        sudo $DOCKER_COMPOSE_CMD -f docker-compose-linux-npu.yaml down $del_volume
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
