#!/usr/bin/env python3
"""Records asciiverse/nflood.cast, the catalog preview, at 100x30
(hub/RECORDING.md): games played by a driver that reads the board's
colours from the screen and picks each move by looking two moves ahead
for the colour that floods the most cells. It floods one board to the
end ("Congrats!"), starts another with r, and quits with q after about
45 seconds.

nflood runs from out/ (asciiverse/build.sh) by name with -c, as av starts
it, so the cast's header holds no local path, and with a throwaway HOME,
so nothing touches your own best score.

Needs asciinema 3.x and pyte. Usage, from the repo root:
  uv run --with pyte python3 asciiverse/record-preview.py
Any extra argument is used as the cast's path instead (for test runs);
with --dry-run it plays without recording."""
import fcntl, os, pty, select, shutil, struct, sys, tempfile, termios, time
import pyte

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [a for a in sys.argv[1:] if a != "--dry-run"]
dry = "--dry-run" in sys.argv
cast = args[0] if args else f"{root}/asciiverse/nflood.cast"
COLS, ROWS, PLAY = 100, 30, 45.0
SIZE = 14
# the keys 1 to 6 and their colours, as engine_init() sets them (pyte calls
# yellow "brown")
KEYS = {"blue": b"1", "magenta": b"2", "red": b"3", "brown": b"4", "green": b"5", "white": b"6"}

work = tempfile.mkdtemp(prefix="nflood-preview-")
env = dict(os.environ, TERM="xterm-256color", COLORTERM="truecolor", LANG="C.UTF-8",
           HOME=work, PATH=f"{root}/out:{os.environ['PATH']}")
for v in ("VTE_VERSION", "TERM_PROGRAM", "TERM_PROGRAM_VERSION", "TMUX", "XDG_DATA_HOME"):
    env.pop(v, None)

pid, fd = pty.fork()
if pid == 0:
    os.chdir(work)
    if dry:
        os.execvpe("nflood", ["nflood", "-c"], env)
    os.execvpe("asciinema", ["asciinema", "rec", "--overwrite", "-q", "--idle-time-limit", "2",
        "--window-size", f"{COLS}x{ROWS}", "--capture-env", "TERM,COLORTERM,LANG",
        "--title", "nflood", "--command", "nflood -c", cast], env)
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))
screen = pyte.Screen(COLS, ROWS)
stream = pyte.ByteStream(screen)
start = time.time()


def pump(seconds):
    end = time.time() + seconds
    while True:
        left = end - time.time()
        r, _, _ = select.select([fd], [], [], max(0.0, min(0.02, left)))
        if r:
            try:
                stream.feed(os.read(fd, 65536))
            except OSError:
                return False
        if left <= 0:
            return True


def key(k, wait=0.6):
    os.write(fd, k)
    pump(wait)


def text():
    return "\n".join(screen.display)


def read_board():
    """{(x, y): colour} for the 14x14 board: the "Moves:" line is 11 rows
    below the board's top and one column right of its left edge, and the
    cells start 16 columns in, two characters each."""
    for y, line in enumerate(screen.display):
        x = line.find("Moves:")
        if x >= 0:
            top, left = y - 11, x - 1 + 16
            return {(i, j): screen.buffer[top + j][left + 2 * i].fg
                    for i in range(SIZE) for j in range(SIZE)}
    return None


def region(board):
    """The cells joined to the top left corner by its colour."""
    colour = board[(0, 0)]
    seen, todo = {(0, 0)}, [(0, 0)]
    while todo:
        x, y = todo.pop()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n in board and n not in seen and board[n] == colour:
                seen.add(n)
                todo.append(n)
    return seen


def flood(board, colour):
    b = dict(board)
    for c in region(board):
        b[c] = colour
    return b


def best(board):
    here = board[(0, 0)]
    choice, value = None, -1
    for c in KEYS:
        if c == here:
            continue
        b = flood(board, c)
        v = len(region(b)) * 10 + max(len(region(flood(b, d))) for d in KEYS if d != c)
        if v > value:
            choice, value = c, v
    return choice


def play(limit):
    """Floods until Congrats! or the time limit; the number of moves."""
    moves = 0
    while time.time() - start < limit and "Congrats" not in text():
        board = read_board()
        if not board or set(board.values()) - set(KEYS):
            pump(0.2)
            continue
        key(KEYS[best(board)])
        moves += 1
    return moves


pump(2.0)
first = play(PLAY)
finished = "Congrats" in text()
pump(2.5)
if finished:
    key(b"r", 1.5)         # one more game
    second = play(PLAY)
pump(2.0)
key(b"q", 0.5)             # quits (after Congrats! any key but r does)
end = time.time() + 5
while time.time() < end:
    if not pump(0.1):
        break
    done, _ = os.waitpid(pid, os.WNOHANG)
    if done:
        break
else:
    os.kill(pid, 9)
try:
    os.waitpid(pid, 0)
except ChildProcessError:
    pass
shutil.rmtree(work, ignore_errors=True)
print(f"{cast}: {time.time() - start:.0f} s, first board {first} moves (finished: {finished}), "
      f"second {second if finished else 0} ({'Congrats' in text()})",
      file=sys.stderr)
