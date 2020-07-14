#!/bin/bash

ROOT_DIR=$(pwd)
git config --global user.email "josh@joshlong.com"
git config --global user.name "Advocacy Profile Processor"

output=$HOME/output
mkdir -p $output
export GIT_CLONE_DIR=$output/clone
git clone https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/joshlong/joshlong.github.io-content.git "$GIT_CLONE_DIR"

export PROFILE_PAGE=$GIT_CLONE_DIR/content/feed.html

pipenv install
pipenv run python main.py

cd $GIT_CLONE_DIR
git add *
git commit -am "updated $FN @ $(date)"
git push
