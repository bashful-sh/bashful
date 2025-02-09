#!/bin/bash

# Define Meta Data
export BUN_PATH="$HOME/.bun"
export BUN_INSTALL="$BUN_PATH"
export BUN_BIN_PATH="$BUN_PATH/bin"

# Define Path Additions
export PATH="$BUN_BIN_PATH:$PATH"

# Define Functions
function sass() {
  bunx sass "$@"
}
