#!/bin/bash

# Set the desired date (yesterday in this case)
yesterday=$(date -d "yesterday" --rfc-3339=seconds)

# Stage your changes
git add .

# Create the commit with the specified author and committer dates
GIT_AUTHOR_DATE="$yesterday" GIT_COMMITTER_DATE="$yesterday" git commit -m "refactor: code clean up"

# Optionally, verify the commit date
git show --pretty=fuller HEAD
