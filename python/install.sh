#!/bin/bash
export BPY_VENV="$BASHFUL_DIR/.tmp/pyvenv"
export BPY_BIN="$BPY_VENV/bin"
export BPY="$BPY_BIN/python3"

venv="$BASHFUL_DIR/.tmp/pyvenv"

# Python Virtual Environment
if ! [ -d "$venv" ]; then
  sudo apt-get update && sudo apt-get upgrade && sudo apt-get autoremove && sudo apt-get clean
  sudo apt-get install --upgrade -y python3 python3-venv python3-dev portaudio19-dev wget curl pulseaudio apt-transport-https ca-certificates gnupg
  curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
  echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
  sudo apt-get update && sudo apt-get install google-cloud-cli
  python3 -m venv "$venv"
  source "$BPY_BIN/activate"
  pip install --no-cache-dir -U "pip>=24"
  pip install --no-cache-dir -U -r "$BASHFUL_DIR/python/requirements.txt"
  deactivate
fi
