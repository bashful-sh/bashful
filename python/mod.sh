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

function bpy_script() {
  bpy "$BASHFUL_DIR"/python/scripts/$1.py
}

function http() {
  bpy -m http.server "$@"
}
