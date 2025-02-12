#!/bin/bash
# Name: main.sh
# Desc: the main entry file (imported by bash)
# Version: 1.0.x

# bashful information
export BASHFUL_DIR="$HOME/.bashful"
export BASHFUL_GIT="$BASHFUL_DIR/.git"
channel=""
branch=""
commit=""
release=""
version="1.0.0"

if [ -d $BASHFUL_GIT ]; then
  channel="git"
  branch=$(git rev-parse --abbrev-ref HEAD)
  commit=$(git rev-parse --short HEAD)
  release="$branch-$commit@$channel"
  version="$version@$platform-$architecture"
else
  channel="bashful-sh.github.io/bashful"
  branch="lts"
  commit="2025"
  release="$branch-$commit@$channel"
  version="$version@$platform-$architecture"
fi

export BASHFUL_CHANNEL=$channel
export BASHFUL_BRANCH=$branch
export BASHFUL_COMMIT=$commit
export BASHFUL_RELEASE=$release
export BASHFUL_VERSION=$version

export BASHFUL_TMP="$BASHFUL_DIR/.tmp"
if ! [ -d "$BASHFUL_TMP" ]; then
  mkdir -p "$BASHFUL_TMP"
fi

export BASHFUL_RELEASE_TYPE=$release_type
export BASHFUL_VERSION="$version"
export BASHFUL_RELEASE="$release"
export BASHFUL_COMMIT_ID="$commit"

export COFF='\033[0m'           # Text Reset
export CRED='\033[0;31m'        # Red
export CGREEN='\033[0;32m'      # Green
export CDIM='\033[0;2m'         # White
export CBOLD='\033[1m'          # Bold White
export CBOLD_GREEN='\033[1;32m' # Bold Green

function bashful() {
  echo $BASHFUL_RELEASE
}

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

inherit_builtin profile
inherit_builtin apt
inherit_builtin python
inherit_builtin git
inherit_builtin bun
inherit_builtin redis
inherit_builtin redis-cloud
inherit_builtin ollama
