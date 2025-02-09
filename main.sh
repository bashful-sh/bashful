#!/bin/bash
# Name: Bashful
# Desc: Debian/Ubuntu shell script package manager
# Git ssh: github:oceaster/bashful.git
# Version: 1.0.0

# System information
platform=$(uname)
architecture=$(uname -p)

export PLATFORM="$platform"
export ARCHITECTURE="$architecture"

# Root directory
if [ -d "$HOME/.bashful" ]; then
  export BASHFUL_DIR="$HOME/.bashful"
  export BASHFUL="$BASHFUL_DIR"

else
  if [ -d "$HOME/.bashful-git" ]; then
    export BASHFUL_DIR="$HOME/.bashful-git"
  fi
fi

# Temporary directory
export BASHFUL_TMP="$BASHFUL_DIR/.tmp"
if ! [ -d "$BASHFUL_TMP" ]; then
  mkdir -p "$BASHFUL_TMP"
fi

# Version information
channel=""
branch=""
commit=""
release=""
version="0.0.0"

if [ -d "$BASHFUL_DIR/.git" ]; then
  channel="git"
  branch=$(git rev-parse --abbrev-ref HEAD)
  commit=$(git rev-parse --short HEAD)
  release="$branch-$commit@$channel"
  version="$version@$platform-$architecture"
else
  channel="oceaster.github.io"
  branch="lts"
  commit="2025"
  release="$branch-$commit@$channel"
  version="$version@$platform-$architecture"
fi

# Commit information
export BASHFUL_RELEASE_TYPE=$release_type
export BASHFUL_VERSION="$version"
export BASHFUL_RELEASE="$release"
export BASHFUL_COMMIT_ID="$commit"

# Reset
export COFF='\033[0m' # Text Reset

# Regular Colors
export CRED='\033[0;31m'   # Red
export CGREEN='\033[0;32m' # Green
export CDIM='\033[0;2m'    # White

# Bold
export CBOLD='\033[1m'          # Bold White
export CBOLD_GREEN='\033[1;32m' # Bold Green

function inherit_absolute_module() {
  if [ -d "$1" ]; then
    if [ -f "$1/install.sh" ]; then
      . "$1/install.sh"
    fi
    if [ -f "$1/private.sh" ]; then
      . "$1/private.sh"
    fi
    if [ -f "$1/mod.sh" ]; then
      . "$1/mod.sh"
    fi
    if [ -f "$1/aliases.sh" ]; then
      . "$1/aliases.sh"
    fi
  fi
}

function inherit_builtin() {
  inherit_absolute_module "$BASHFUL_DIR/$1"
}

function init_tmp_directory() {
  if ! [ -d "$BASHFUL_TMP" ]; then
    mkdir "$BASHFUL_TMP"
  fi
}

function dump_tmp_directory() {
  rm -rf "$BASHFUL_TMP"
  mkdir "$BASHFUL_TMP"
}

function mktmp() {
  if ! [ -d "$BASHFUL_TMP/$1" ]; then
    mkdir "$BASHFUL_TMP/$1"
  fi
}

function rmtmp() {
  rm -rf "$BASHFUL_TMP/${1:?}"
  mkdir "$BASHFUL_TMP/$1"
}

# Built-in Applications Library
inherit_builtin profile
inherit_builtin apt
inherit_builtin python
inherit_builtin git
inherit_builtin bun
inherit_builtin redis
inherit_builtin redis-cloud
inherit_builtin ollama

# Define main entry point function
function bashful() {
  echo $BASHFUL_RELEASE
}
