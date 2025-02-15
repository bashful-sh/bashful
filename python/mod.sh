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

alias bpy='$BPY'
alias bpy.pip='$BPIP'
alias bpy.env='source $BVENV'
alias bpy.lib='$BPY -m pip freeze'

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

# Simple Local Only (GPU/CPU) LLM runner
function llm() {
  bpy "$BASHFUL_DIR/python/scripts/llm.py" "$1" "$2" "$3" "$4" 2>/dev/null
}

# Production Ready (CPU/GPU) LLM runner
function vllm() {
  bpy "$BASHFUL_DIR/python/scripts/vllm.py" "$1" "$2" 2>/dev/null
}
