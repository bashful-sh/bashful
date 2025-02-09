#!/bin/bash

# Define Environment
export BPY_INSTALL="$BASHFUL_DIR/python/install.sh"
export BPY_VENV="$BASHFUL_DIR/.tmp/pyvenv"
export BPY_BIN="$BPY_VENV/bin"
export BPY="$BPY_BIN/python3"
export BPIP="$BPY_BIN/python3 -m pip"
export BVENV="$BPY_BIN/activate"

# Define Path Additions

# Define Module
alias bpy='$BPY'
alias bpip='$BPIP'
alias bvenv='source $BVENV'
alias bpy.mods='bpip freeze'

# Define Functions
function http() {
  bpy -m http.server "$@"
}
