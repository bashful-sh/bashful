#!/bin/bash
# profile/aliases.sh
#
# Default built-in aliases for bashful.

# alert: command
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

# bash: navigation
alias e="exit"
alias n="nvim ."
alias c="cd .."
alias cc="cd ../.."
if [ -x /usr/bin/dircolors ]; then
  if test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)"; then
    clear
  else
    commandeval "$(dircolors -b)"
    clear
  fi
  alias ls='ls --color=auto'
  alias dir='dir --color=auto'
  alias vdir='vdir --color=auto'
  alias grep='grep --color=auto'
  alias fgrep='fgrep --color=auto'
  alias egrep='egrep --color=auto'
fi
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# ssh: devices
alias ssh.laptop="ssh $LAPTOP_USERNAME@$LAPTOP_IP -p 22"
alias ssh.desktop="ssh $DESKTOP_USERNAME@$DESKTOP_IP -p 22"
alias ssh.server="ssh $SERVER_USERNAME@$SERVER_IP -p 22"
