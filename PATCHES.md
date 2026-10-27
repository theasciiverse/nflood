# Changes from upstream

This is the Asciiverse packaging of [nFlood](https://github.com/alexdantas/nFlood),
a Flood-It puzzle for the terminal by Alexandre Dantas (2011 to 2014),
with contributions from Yu-Jie Lin, GPL-3.0-or-later (README and the
source headers: "either version 3 of the License, or any later
version"; COPYING is the GPL 3). Upstream is the `upstream` remote; the
`asciiverse` branch starts from its `master` at `769203f` (2014-02-18),
28 commits after the only release, v0.5.0, adding the board size
options, high scores and fixes. The version stays 0.5.0. No newer fork
was found; repology lists only SlackBuilds, at 0.5.0 (its build script
not checked).

The option parser in `src/commander/` is TJ Holowaychuk's Commander
(github.com/clibs/commander, 1.3.2, slightly modified upstream), MIT.
Its source carries only a copyright line, so its licence text, from
Commander's Readme.md, is added as `src/commander/LICENSE` and shipped
as `COMMANDER-LICENSE`.

## Code

- **Builds with GCC 10 and later.** `options.h` and `engine.h` defined the
  global `options` and `engine` (and an unused variable `options_t`) in
  every file that included them, which links only with the old
  `-fcommon` default. They are declared `extern` and defined once.
- **A different first board each time.** The first board was dealt
  before the random numbers were seeded, so every start began with the
  same board. `main()` seeds once, first; `game_init()` no longer seeds
  (seeding again with the same second dealt the first board again on r).
- **High scores in the XDG data folder.** The best score was kept in
  `~/.local/share/nflood/nflood.scores` whatever `XDG_DATA_HOME` said,
  and in `/tmp` when `HOME` was not set. It is
  `$XDG_DATA_HOME/nflood/nflood.scores` (`~/.local/share/nflood` when
  that is unset, empty or relative; `%APPDATA%\nflood` on Windows), and
  not saved when there is no such folder. README and the man page follow.
- **A new best score is shown at once.** It was stored after the board
  was drawn, so a winning game showed the old best, until the next
  finished game.
- **Clicking "r: New Game" deals a new board.** The mouse's New Game only
  flooded the corner again, keeping the board and its move count.
- **Boards at least 2x2.** `-W`/`-H` of 0, or anything `atoi()` reads as
  0, made an empty board that the first flood ran past the end of (ASan).
- **Centred board follows a resize; clear message when too small.** A
  centred board stayed put when the terminal was resized; it is centred
  again. In a terminal under 44x16 the game said "ERROR: Failed to
  initialize nCurses"; it now says what size it needs.
- **Locale set before curses starts**, so wide ncurses draws the
  checkerboard cells in UTF-8 where it does not trust the VT100 line set
  (screen, tmux, the Linux console).
- **Windows.** `<curses.h>` (PDCurses) instead of `<ncurses.h>`, with
  `NCURSES_MOUSE_VERSION` for the ncurses-style `getmouse()`.

Upstream starts the board in the top left corner and centres it with
`-c` or the c key (its commit `98d2c19` made that the default); that is
kept, and the catalog starts it with `-c`.

## Packaging (new files)

- `asciiverse/build.sh`: the sources and Commander in one compiler run
  against wide ncurses (wide PDCurses on Windows), the man page filled in
  as upstream's `make install` does.
- `asciiverse/package.sh`: one archive per target with the binary, the man
  page, COPYING, COMMANDER-LICENSE, README.md and this file.
- `.github/workflows/release.yml`: static Linux in Alpine (x86_64,
  aarch64), macOS (x86_64, arm64) and Windows x86_64 (MinGW and wide
  PDCurses 3.9), plus SHA256SUMS, on a tag.
- `asciiverse/record-preview.py`: records `asciiverse/nflood.cast`; a
  driver reads the board's colours from the screen and floods with a
  two-move lookahead, a whole board and then a second.
- `src/commander/LICENSE`, `.gitignore` (the build folders).

## Tested

Linux: native (glibc, ncursesw 6.6) and static (Alpine 3.22, musl)
builds; boards flooded to Congrats! with keys and with the mouse (SGR
mouse reports), New Game by key and by click, a new best stored and
shown, the score file in `~/.local/share/nflood` and under
`XDG_DATA_HOME`; centred with `-c` at 100x30, re-centred after resizes to
70x20 and 120x40; under 44x16 the message. ASan and UBSan: three
40-second runs of random keys and clicks with random resizes, and the
odd sizes `-W 0`, `-H 0`, `-W 1 -H 1`, `-W 200 -H 200`, `-W abc`, no
reports after the size fix. Windows: cross-built with MinGW-w64 against
wide PDCurses 3.9 and run under Wine (a board flooded to Congrats!, the
score file in `%APPDATA%\nflood`, r and q); Wine's console showed the
cells as `?`, so the drawing and the mouse are unchecked on real
Windows. macOS: not built here.

## Ours

- **How to play it, at the top of README.md.** A short note on installing and
  starting it with av, or from a release archive; the original text follows
  unchanged.
