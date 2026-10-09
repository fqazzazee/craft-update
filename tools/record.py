# SPDX-License-Identifier: MIT OR Apache-2.0
# Regenerate docs/watch-preview.svg: start `craft-update` in one terminal, then run
#   python3 tools/record.py rec.json && python3 tools/ansi2svg.py rec.json docs/watch-preview.svg
# Record `craft-update --watch` in a pseudo-terminal: raw output with per-chunk timestamps.
import os, pty, sys, time, struct, fcntl, termios, json
out = sys.argv[1]
pid, fd = pty.fork()
if pid == 0:
    os.environ["TERM"] = "xterm-256color"
    os.execvp("craft-update", ["craft-update", "--watch"])
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 22, 104, 0, 0))
chunks, t0 = [], time.time()
while True:
    try:
        data = os.read(fd, 65536)
    except OSError:
        break
    if not data:
        break
    chunks.append([time.time() - t0, data.decode("utf8", "replace")])
os.waitpid(pid, 0)
json.dump(chunks, open(out, "w"))
