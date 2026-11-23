"""Crops every page and widget the App map draws out of a shots run.

Usage: python3 crop_shots.py <shots run dir> <out dir>
Reads the `SHOT RECT <shot> <Type> <l> <t> <w> <h> <hits>` lines a screenshot adapter logs to
drive.log, picks the best view of each type (fully on screen first, then the largest) and
saves it as <out dir>/<Type>.jpg at 2x. Rects are in the screen's logical units (points, dp):
`SHOT SCREEN <w> <h>` in the log gives the screen's size in them (default 375×812, the Flutter
adapter's iPhone).
"""
import math
import os
import re
import sys

from PIL import Image

SCREEN_W, SCREEN_H = 375.0, 812.0
PAD = 6.0
OUT_SCALE = 2.0
MIN_SIDE = 12.0

run_dir, out_dir = sys.argv[1], sys.argv[2]
line = re.compile(r'SHOT RECT (\S+) (\S+) (-?[\d.]+) (-?[\d.]+) ([\d.]+) ([\d.]+)(?: (\d))?')
best = {}
with open(os.path.join(run_dir, 'drive.log'), errors='replace') as log:
    text = log.read()
screen = re.search(r'SHOT SCREEN ([\d.]+) ([\d.]+)', text)
if screen:
    SCREEN_W, SCREEN_H = float(screen.group(1)), float(screen.group(2))
for match in line.finditer(text):
    shot, name = match.group(1), match.group(2)
    left, top, width, height = (float(value) for value in match.groups()[2:6])
    # Points of 5 that hit the widget: fewer means something covers part of it.
    hits = int(match.group(7) or 0)
    if match.group(7) is not None and hits == 0:
        continue
    if not os.path.exists(os.path.join(run_dir, shot + '.png')):
        continue
    right, bottom = min(left + width, SCREEN_W), min(top + height, SCREEN_H)
    left, top = max(left, 0.0), max(top, 0.0)
    if right - left < MIN_SIDE or bottom - top < MIN_SIDE:
        continue
    visible = (right - left) * (bottom - top) / (width * height)
    # Bigger wins only when it's clearly bigger (1.5×); among copies of about the same size, the
    # one nearest the middle of the screen, away from the bars at its edges.
    size = int(math.log((right - left) * (bottom - top), 1.5))
    middle = -abs((top + bottom) / 2 - SCREEN_H / 2)
    score = (hits, visible >= 0.95, size, middle)
    if name not in best or score > best[name][0]:
        best[name] = (score, shot, (left, top, right, bottom))

os.makedirs(out_dir, exist_ok=True)
for name, (_, shot, (left, top, right, bottom)) in sorted(best.items()):
    image = Image.open(os.path.join(run_dir, shot + '.png'))
    scale = image.width / SCREEN_W
    box = (
        int(max(left - PAD, 0) * scale), int(max(top - PAD, 0) * scale),
        int(min(right + PAD, SCREEN_W) * scale), int(min(bottom + PAD, SCREEN_H) * scale),
    )
    crop = image.crop(box).convert('RGB')
    size = (round(crop.width * OUT_SCALE / scale), round(crop.height * OUT_SCALE / scale))
    crop.resize(size, Image.LANCZOS).save(os.path.join(out_dir, name + '.jpg'), quality=72, optimize=True)
    print(f'{name}: {shot} {int(right - left)}x{int(bottom - top)}pt')
print(f'{len(best)} crops in {out_dir}')
