#!/bin/bash

# Add all files to the staging area
git add .

# Get the current date and time
current_datetime=$(date +"%Y-%m-%d %H:%M:%S")

# Commit with the current date and time
git commit -m "Auto commit at $current_datetime"

# Push changes to the remote repository
git push
