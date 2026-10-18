#!/bin/sh
# Builds nflood into out/: the sources and the bundled Commander in one
# compiler run (one process, so no parallel jobs to limit), with the man
# page filled in as upstream's install does. The compiler, flags and
# curses library come from the environment, so one script serves every
# target (see .github/workflows/release.yml):
#
#   asciiverse/build.sh                                        # Linux
#   LDFLAGS="-static -s" asciiverse/build.sh                   # Alpine, static
#   LIBS=-lncurses CFLAGS="-O2 -arch arm64" \
#     LDFLAGS="-arch arm64" asciiverse/build.sh                # macOS
#   CC=x86_64-w64-mingw32-gcc CFLAGS="-O2 -I$PDC -DPDC_WIDE -DPDC_FORCE_UTF8" \
#     LIBS="$PDC/wincon/pdcurses.a" LDFLAGS="-static -s" EXE=.exe \
#     asciiverse/build.sh                                      # Windows (wide PDCurses)
set -eu
cd "$(dirname "$0")/.."
CC="${CC:-cc}"
CFLAGS="${CFLAGS:--O2}"
LDFLAGS="${LDFLAGS:-}"
LIBS="${LIBS:--lncursesw}"
EXE="${EXE:-}"
VERSION=$(sed -n 's/^VERSION *= *//p' Makefile)
DATE="Feb2014"   # the date of the last upstream commit, not the build's
mkdir -p out
rm -f "out/nflood$EXE"
# shellcheck disable=SC2086
nice -n 10 $CC -std=gnu99 $CFLAGS -DVERSION="\"$VERSION\"" -DPACKAGE='"nflood"' -DDATE="\"$DATE\"" \
  -o "out/nflood$EXE" src/*.c src/commander/commander.c $LDFLAGS $LIBS
sed -e "s|DATE|$DATE|g" -e "s|VERSION|$VERSION|g" man/nflood.6 > out/nflood.6
echo "built nflood$EXE $VERSION"
