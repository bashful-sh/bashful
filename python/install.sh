#!/bin/bash
venv="$BASHFUL_DIR/.tmp/pyvenv"
if ! [ -d "$venv" ]; then
  sudo apt install --upgrade python3.13 python3-venv
  python3.13 -m venv "$venv"
  export BPY_VENV="$BASHFUL_DIR/.tmp/pyvenv"
  export BPY_BIN="$BPY_VENV/bin"
  export BPY="$BPY_BIN/python3"
  source "$BPY_VENV/bin/activate"
  pip install pip-tools
  pip install -r "$BASHFUL_DIR/python/requirements.txt"
  deactivate
fi
