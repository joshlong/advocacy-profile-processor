#!/bin/bash

#git config --global user.email "josh@joshlong.com"
#git config --global user.name "Advocacy Profile Processor"

OUTPUT_DIR=$HOME/Desktop/out
CLONE_DIR=$OUTPUT_DIR/clone
export PROFILE_PAGE=$CLONE_DIR/content/advocate/joshlong.md

ts=$(date +%s)
message="update joshlong.md @ ${ts}"

rm -rf $OUTPUT_DIR && mkdir -p $OUTPUT_DIR
git clone https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/joshlong/tanzu-tuesdays.git "$CLONE_DIR"

hub pull-request -b vmware-tanzu/tanzu-tuesdays:master -m $message || echo "there's already a PR, so just updating it"

pipenv install
pipenv run python main.py

cd "$CLONE_DIR"
git add "$PROFILE_PAGE"
git commit -a -m "${message}"
git push
