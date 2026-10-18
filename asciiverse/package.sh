#!/bin/sh
# Packs the build into dist/nflood-<target>.tar.gz (.zip for Windows) for
# av: the binary at the top, with the man page, COPYING (GPL 3),
# COMMANDER-LICENSE (MIT, for the bundled option parser), README.md and
# PATCHES.md.
#
#   asciiverse/package.sh x86_64-unknown-linux-musl
set -eu
cd "$(dirname "$0")/.."
target="$1"
case "$target" in *windows*) exe=.exe ;; *) exe= ;; esac
stage=stage/nflood
rm -rf "$stage" && mkdir -p "$stage" dist
cp "out/nflood$exe" out/nflood.6 COPYING README.md PATCHES.md "$stage/"
cp src/commander/LICENSE "$stage/COMMANDER-LICENSE"
if [ -n "$exe" ]; then
  (cd "$stage" && zip -qr "../../dist/nflood-$target.zip" .)
else
  tar -czf "dist/nflood-$target.tar.gz" -C "$stage" .
fi
ls dist
