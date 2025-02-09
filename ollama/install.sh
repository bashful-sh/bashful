#!/bin/bash
# ollama/install.sh
#
# Installs any requirements & dependencies for using
# the bashful ollama module.

# Version information
OLLAMA_VERSION="$(ollama -v | awk '{print $4}')"
export OLLAMA_VERSION
