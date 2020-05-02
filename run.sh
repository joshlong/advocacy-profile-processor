#!/bin/bash

ROOT_DIR=$(pwd)
git config --global user.email "josh@joshlong.com"
git config --global user.name "Advocacy Profile Processor"

OUTPUT_DIR=$HOME/Desktop/out
CLONE_DIR=$OUTPUT_DIR/clone
JTT="$CLONE_DIR/jtt"
VTT="$CLONE_DIR/vtt"

mkdir -p $CLONE_DIR

export PROFILE_PAGE=$CLONE_DIR/content/advocate/joshlong.md

TS=$(date +%s)
MESSAGE="update joshlong.md @ ${ts}"

rm -rf $OUTPUT_DIR && mkdir -p $OUTPUT_DIR

#######

# here's what I need to do:
# - git clone the actual repo
git clone https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/vmware-tanzu/tanzu-tuesdays.git $VTT || die "couldn't clone "
git clone https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/joshlong/tanzu-tuesdays.git $JTT

# - move the config for my repo into the actual repo
mv $JTT/.git/config $VTT/.git/config

cd $VTT || die "couldn't go to the $VTT directory."

# - then force push the actual repo into my repo (no need to worry about merging stuff if, for sure, im using the latest version of the repo!)
git push --force

# - then clone my repo and do the change on it
rm -rf  $JTT && rm -rf $VTT
git clone https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/joshlong/tanzu-tuesdays.git $JTT
cd $JTT

hub pull-request -b vmware-tanzu/tanzu-tuesdays:master -m $MESSAGE || echo "there's already a PR, so just updating it"

#
cd $ROOT_DIR

pipenv install
pipenv run python main.py

cd $JTT
git add "$PROFILE_PAGE"
git commit -a -m "${MESSAGE}"
git push
