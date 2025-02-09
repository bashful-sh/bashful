if [ -d "$HOME/.bashful" ]; then
  . "$HOME/.bashful/main.sh"
else
  if [ -d "$HOME/.bashful-git" ]; then
    . "$HOME/.bashful-git/main.sh"
  fi
fi
