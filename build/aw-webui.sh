#!/usr/bin/env sh

if [ ! -d "./.build/static" ]; then
  mkdir -p .build
  cd .build || exit 1
  git clone https://github.com/ActivityWatch/aw-webui --recurse-submodules
  cd aw-webui/ || exit 1
  make install
  npm run build
  mkdir ../static
  cp -R dist/* ../static/
fi
