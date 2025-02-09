#!/bin/bash
if ! [ -d "$HOME/.bun" ]; then
  curl -fsSL https://bun.sh/install | bash
fi
