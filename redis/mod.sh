#!/bin/bash

function br-get() {
  redis-cli get "$1"
}

function br-set() {
  redis-cli set "$1" "$2"
}

function br-status() {
  sudo systemctl status redis-server
}

function br-stop() {
  sudo systemctl stop redis-server
}

function br-start() {
  sudo systemctl start redis-server
}
