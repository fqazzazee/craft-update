# SPDX-License-Identifier: MIT OR Apache-2.0
# Turn a recorded `craft-update --watch` session (record.py JSON) into an animated SVG.
# Usage: ansi2svg.py rec.json out.svg [frames]
import json, re, sys
from html import escape

rec, out = sys.argv[1], sys.argv[2]
want = int(sys.argv[3]) if len(sys.argv) > 3 else 10
COLS, ROWS = 104, 22

FG, BG = "#d8dee9", "#1d2128"
COLORS = {31: "#ef6b73", 32: "#8fd18b", 33: "#f0c674", 36: "#6fc3d6"}
DIM = "#7b8494"

def blank():
    return [[(" ", None) for _ in range(COLS)] for _ in range(ROWS)]

screen, row, col = blank(), 0, 0
style = {"b": False, "d": False, "c": None}
snapshots = []  # (time, screen copy)
tok = re.compile(r"\x1b\[([0-9;?]*)([A-Za-z])|\r|\n|[^\x1b\r\n]")

def snap(t):
    snapshots.append((t, [r[:] for r in screen]))

for t, data in json.load(open(rec)):
    for m in tok.finditer(data):
        s = m.group(0)
        if m.group(2):
            args, cmd = m.group(1), m.group(2)
            if cmd == "H":
                if any(ch != " " for r in screen for ch, _ in r):
                    snap(t)
                row = col = 0
            elif cmd == "J":
                if args == "2":
                    screen = blank()
                else:
                    screen[row][col:] = [(" ", None)] * (COLS - col)
                    for r in range(row + 1, ROWS):
                        screen[r] = [(" ", None)] * COLS
            elif cmd == "K":
                screen[row][col:] = [(" ", None)] * (COLS - col)
            elif cmd == "m":
                for a in (args or "0").split(";"):
                    a = int(a or 0)
                    if a == 0: style = {"b": False, "d": False, "c": None}
                    elif a == 1: style["b"] = True
                    elif a == 2: style["d"] = True
                    elif a in COLORS: style["c"] = a
        elif s == "\r":
            col = 0
        elif s == "\n":
            row, col = min(row + 1, ROWS - 1), 0
        else:
            if col < COLS:
                screen[row][col] = (s, (style["b"], style["d"], style["c"]))
            col += 1
snap(t)

# Live frames evenly spread over the run, then the final summary held a little longer.
live = [s for s in snapshots[:-1] if any("Update running" in "".join(c for c, _ in r) for r in s[1])]
step = max(1, len(live) // (want - 1))
frames = live[::step][: want - 1] + [snapshots[-1]] * 3

CW, LH, PAD, TOP = 8.4, 19, 18, 40
used = max(max((i for i, r in enumerate(f[1]) if any(c != " " for c, _ in r)), default=0) for f in frames) + 1
W, H = COLS * CW + 2 * PAD, TOP + used * LH + PAD
SLOT = 1.6
T = SLOT * len(frames)

def runs(r):
    i = 0
    while i < len(r):
        j = i
        while j < len(r) and r[j][1] == r[i][1]:
            j += 1
        yield i, "".join(c for c, _ in r[i:j]), r[i][1]
        i = j

o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}" '
     'role="img" aria-label="craft-update --watch: live dashboard while an update runs">',
     "<style>",
     "text{font-family:'JetBrains Mono','DejaVu Sans Mono',Menlo,Consolas,monospace;font-size:14px;white-space:pre}",
     f".f{{opacity:0;animation:show {T:.1f}s infinite step-end}}",
     f"@keyframes show{{0%{{opacity:1}}{100 / len(frames):.3f}%{{opacity:0}}100%{{opacity:0}}}}",
     "</style>",
     f'<rect width="{W:.0f}" height="{H:.0f}" rx="10" fill="{BG}"/>',
     '<circle cx="20" cy="18" r="6" fill="#ff5f57"/><circle cx="40" cy="18" r="6" fill="#febc2e"/>'
     '<circle cx="60" cy="18" r="6" fill="#28c840"/>',
     f'<text x="{W / 2:.0f}" y="23" fill="{DIM}" text-anchor="middle">craft-update --watch</text>']
def draw(scr):
    for y, r in enumerate(scr[:used]):
        parts = []
        for x, txt, st in runs(r):
            b, d, c = st or (False, False, None)
            fill = COLORS.get(c, DIM if d else FG)
            weight = ' font-weight="bold"' if b else ""
            # One tspan per word at its exact column: SVG renderers collapse runs of spaces.
            for w in re.finditer(r"\S+", txt):
                parts.append(f'<tspan x="{PAD + (x + w.start()) * CW:.1f}" fill="{fill}"{weight}>{escape(w.group())}</tspan>')
        if parts:
            o.append(f'<text y="{TOP + y * LH + 14}">{"".join(parts)}</text>')

# The final frame underneath, for viewers that don't play SVG animation.
draw(frames[-1][1])
for k, (_, scr) in enumerate(frames):
    o.append(f'<g class="f" style="animation-delay:{k * SLOT:.1f}s">')
    o.append(f'<rect y="{TOP - 6}" width="{W:.0f}" height="{H - TOP:.0f}" fill="{BG}"/>')
    draw(scr)
    o.append("</g>")
o.append("</svg>")
open(out, "w").write("\n".join(o))
print(f"{len(snapshots)} snapshots, {len(live)} live, {len(frames)} frames, {W:.0f}x{H:.0f}")
