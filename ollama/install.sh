#!/bin/bash
# ollama/install.sh
#
# Installs any requirements & dependencies for using
# the bashful ollama module.

if ! command -v ollama &>/dev/null; then
  echo "Ollama is not installed. Installing..."
  curl -fsSL https://ollama.com/install.sh | sh
fi

OLLAMA_VERSION="$(ollama -v | awk '{print $4}')"
export OLLAMA_VERSION
