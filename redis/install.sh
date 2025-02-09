#!/bin/bash

# Define Redis Version
export REDIS_CLI=0
export REDIS_SERVER=0

# Health check for redis-server
function health_check_verify_redis_server() {
  cmd=$(redis-server -v)
  if [[ $cmd == Redis* ]] || [[ $cmd == redis* ]]; then
    export REDIS_SERVER=1
  fi
}

function health_check_fix_redis_server() {
  cmd=$(redis-server -v)
  if [[ $cmd == "Redis server v=*" ]]; then
    export REDIS_SERVER=1
  else
    echo ""
    echo "Warning: redis-server is not installed!"
    echo "         attempting to fix..."
    echo ""
    sudo apt remove redis-server
    sudo apt autoremove
    sudo apt update
    sudo apt upgrade
    sudo apt install --upgrade redis-server
  fi
}

function health_check_redis_server() {
  cmd=$(redis-server -v)
  if [[ $cmd == Redis* ]] || [[ $cmd == redis* ]]; then
    health_check_verify_redis_server
  else
    health_check_fix_redis_server
    health_check_verify_redis_server
  fi
}

health_check_redis_server
