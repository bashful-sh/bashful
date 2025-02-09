#!/bin/bash

# Install if not exists
venv="$BASHFUL_DIR/.tmp/pyvenv"
if ! [ -d "$venv" ]; then
  sudo apt install --upgrade python3.13 python3-venv
  python3.13 -m venv "$venv"
fi
