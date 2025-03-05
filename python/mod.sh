#!/bin/bash
# python/mod.sh
#
# Default built-in python wrapper for bashful,
# adds multiple system shortcut functions with
# the support of a local virtual environment.

export BPY_INSTALL="$BASHFUL_DIR/python/install.sh"
export BPY_VENV="$BASHFUL_DIR/.tmp/pyvenv"
export BPY_BIN="$BPY_VENV/bin"
export BPY="$BPY_BIN/python3"
export BPIP="$BPY_BIN/python3 -m pip"
export BVENV="$BPY_BIN/activate"

LD_LIBRARY_PATH=$("$BPY" -c 'import os; import nvidia.cublas.lib; import nvidia.cudnn.lib; print(os.path.dirname(nvidia.cublas.lib.__file__) + ":" + os.path.dirname(nvidia.cudnn.lib.__file__))')
export LD_LIBRARY_PATH

# Bashful Python
function bpy() {
  "$BPY" "$@"
}

# Install and Upgrade from Python requirements.txt
function bpy.update() {
  source "$BPY_VENV/bin/activate"
  pip install --upgrade -r "$BASHFUL_DIR/python/requirements.txt"
  deactivate
}

# Simple HTTP Local Development Server
function bpy.http() {
  bpy -m http.server -b 127.0.0.1
}

# Simple HTTPS Local Development Server
function bpy.https() {
  lib_dir="$BASHFUL_DIR/python/libs/https"
  lib_main="main.py"
  bpy "$lib_dir/$lib_main" "$@"
}

# Simple Local Only (GPU and/or CPU) LLM runner
function bpy.llm_runner() {
  user_working_dir=$(pwd)
  script_working_dir="$BASHFUL_DIR/python/scripts"
  script_name="llm_runner.py"

  cd "$script_working_dir" || exit
  bpy "$script_working_dir/$script_name" "$1" "$2" "$3" "$4" 2>/dev/null
  cd "$user_working_dir" || exit
}

# Production Ready (GPU only) LLM runner
function bpy.vllm_runner() {
  user_working_dir=$(pwd)
  script_working_dir="$BASHFUL_DIR/python/scripts"
  script_name="vllm_runner.py"

  cd "$script_working_dir" || exit
  bpy "$script_name" "$1" "$2" 2>/dev/null
  cd "$user_working_dir" || exit
}

# Simple Universal (CPU/GPU) based (AI/ML/LLM) Model Server
function bpy.ts() {
  user_working_dir=$(pwd)
  working_dir="$BASHFUL_DIR/python/libs/server"
  main_file_name="server.py"
  cd "$working_dir" && bpy "$main_file_name" "$@"
}

# Simple Local Only Live Audio Transcription Client
function bpy.tc() {
  user_working_dir=$(pwd)
  working_dir="$BASHFUL_DIR/python/libs/server"
  main_file_name="client.py"
  cd "$working_dir" && bpy "$main_file_name" "$@"
}

# Simple Speech to Text using a local Flask Server
function bpy.stt() {
  user_working_dir=$(pwd)
  working_dir="$BASHFUL_DIR/python/libs/stt"
  main_file_name="main.py"
  cd "$working_dir" && bpy "$main_file_name" --debug true --use_redis true
}

# Simple Text to Speech using a local Flask Server
function bpy.tts() {
  user_working_dir=$(pwd)
  working_dir="$BASHFUL_DIR/python/libs/tts"
  main_file_name="main.py"
  cd "$working_dir" && bpy "$main_file_name" --debug true
}

# LOCAL LLM: Dexter Command Line Interface
function bpy.llm() {
  user_working_dir=$(pwd)
  working_dir="$BASHFUL_DIR/python/libs/llm"
  main_file_name="main.py"
  cd "$working_dir" && bpy "$main_file_name" --debug true
}

# LLM SERVER: Runs a Dexter Server
function bpy.dexter() {
  user_working_dir=$(pwd)
  working_dir="$BASHFUL_DIR/python/libs/llm"
  main_file_name="main.py"
  cd "$working_dir" && bpy "$main_file_name" -t "$*"
}

alias dex="bpy.dexter"

function bpy.dexnet-worker() {
  user_working_dir=$(pwd)
  working_dir="$BASHFUL_DIR/python/libs/dexnet"
  main_file_name="worker.py"
  cd "$working_dir" && bpy "$main_file_name" --wss_uri wss://api.easter.company/dexnet
}
