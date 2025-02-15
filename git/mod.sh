#!/bin/bash

# git: add, commit, and push all
function git.all() {
  git status
  git add .
  git commit -m "$@"
  git push
}
