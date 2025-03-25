#!/bin/bash

# apt update
alias update="sudo apt update"
alias upd="update"

# apt upgrade
alias upgrade="sudo apt upgrade"
alias upg="upgrade"

# apt autoremove
alias autoremove="sudo apt autoremove"
alias arm="autoremove"

# apt aur (auto update/upgrade and remove packages)
alias aur="upgrade && autoremove && update && upgrade && autoremove"
