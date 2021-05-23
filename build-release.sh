#!/bin/bash
#
# Builds a src-dist folder with .mpy files, and can upload it.
#
# Building requires mpy-cross in the path: https://github.com/micropython/micropython/blob/master/mpy-cross/README.md
# mctl: https://github.com/metachris/micropython-ctl/tree/master/cli (npm install -g micropython-ctl@beta)
#
set -eEu -o pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # reference all relative things with dir first: "$DIR/relativestuff.sh"
cd "$DIR"

echo "copying ./src/ -> ./src-dist/"
rm -rf src-dist
cp -r src src-dist
cd src-dist

echo "Cross-compiling Python files from .py -> .mpy"
find ./ -name "*.py" ! -name "main.py" -exec mpy-cross {} \;
find ./ -name "*.py" ! -name "main.py" | xargs rm

read -p "Press enter to upload with 'mctl sync'... " y
mctl sync
