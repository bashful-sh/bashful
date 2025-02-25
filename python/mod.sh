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

# Executes a built-in Python script
function bpy-script() {
  bpy "$BASHFUL_DIR/python/scripts/$1.py"
}

# Install and Upgrade from Python requirements.txt
function bpy-update() {
  source "$BPY_VENV/bin/activate"
  pip install --upgrade -r "$BASHFUL_DIR/python/requirements.txt"
  deactivate
}

# Simple Local Only Web-Server
function bpy-serve() {
  bpy -m http.server "$@"
}

# Simple Local Only (GPU and/or CPU) LLM runner
function llm() {
  user_working_dir=$(pwd)
  script_working_dir="$BASHFUL_DIR/python/scripts"
  script_name="llm_runner.py"

  cd "$script_working_dir" || exit
  bpy "$script_working_dir/$script_name" "$1" "$2" "$3" "$4" 2>/dev/null
  cd "$user_working_dir" || exit
}

# Production Ready (GPU only) LLM runner
function vllm() {
  user_working_dir=$(pwd)
  script_working_dir="$BASHFUL_DIR/python/scripts"
  script_name="vllm_runner.py"

  cd "$script_working_dir" || exit
  bpy "$script_name" "$1" "$2" 2>/dev/null
  cd "$user_working_dir" || exit
}

# Simple Universal (CPU/GPU) based (AI/ML/LLM) Model Server
function model-server() {
  user_working_dir=$(pwd)
  working_dir="$BASHFUL_DIR/python/libs/server"
  main_file_name="server.py"
  cd "$working_dir" && bpy "$main_file_name" "$@"
}

# Simple Local Only Live Audio Transcription Client
function transcription-client() {
  user_working_dir=$(pwd)
  working_dir="$BASHFUL_DIR/python/libs/server"
  main_file_name="client.py"
  cd "$working_dir" && bpy "$main_file_name" "$@"
}

# Simple Speech to Text using a local Flask Server
function lstt() {
  user_working_dir=$(pwd)
  working_dir="$BASHFUL_DIR/python/libs/lstt"
  main_file_name="main.py"
  cd "$working_dir" && bpy "$main_file_name" "$@"
}

# API: Text to Speech using Google Cloud
function gtts() {
  user_working_dir=$(pwd)
  working_dir="$BASHFUL_DIR/python/libs/gtts"
  main_file_name="main.py"
  cd "$working_dir" && bpy "$main_file_name" "$@"
}

# API: Speech to Text using Google Cloud
function gstt() {
  user_working_dir=$(pwd)
  working_dir="$BASHFUL_DIR/python/libs/gstt"
  main_file_name="main.py"
  cd "$working_dir" && bpy "$main_file_name" "$@"
}
