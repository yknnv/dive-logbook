#!/usr/bin/env python3
"""Подготовка новых иллюстраций к вёрстке.

Обрезает лишние белые поля, переводит в градации серого и раскладывает
под именами, которые ожидает вёрстка.

    python3 tools/prepare_illustrations.py входная_папка mapping.txt
    python3 tools/prepare_illustrations.py --elements входная_папка mapping.txt

mapping.txt — по строке на файл:

    S-22  s-22-shore-line
    S-23  s-23-stern-to

Режим --elements для элементов схем (лодки, суда, фигуры), которые
ставятся поверх векторного слоя. Он делает фон прозрачным, чтобы
элемент не пробивал белую дыру в серой заливке сектора или в линии
круга под ним.

Прозрачность заливается от края кадра и внутрь не заходит: белое внутри
корпуса остаётся белым, иначе сквозь палубу просвечивала бы разметка.
"""
import os
import sys
from collections import deque

import numpy as np
from PIL import Image

DST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "assets", "images")


def autocrop(im, pad=8):
    g = np.asarray(im.convert("L"))
    ink = g < 245
    if not ink.any():
        return im
    ys, xs = np.where(ink)
    t, b = max(ys.min() - pad, 0), min(ys.max() + pad, g.shape[0] - 1)
    l, r = max(xs.min() - pad, 0), min(xs.max() + pad, g.shape[1] - 1)
    return im.crop((l, t, r + 1, b + 1))


def keyout_background(im, thr=244):
    """Белый фон в прозрачность заливкой от края. Возвращает RGBA."""
    g = np.asarray(im.convert("L"))
    h, w = g.shape
    light = g >= thr
    seen = np.zeros((h, w), dtype=bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if light[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if light[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and light[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                q.append((ny, nx))
    out = im.convert("L").convert("RGBA")
    a = np.asarray(out)[:, :, 3].copy()
    a[seen] = 0
    arr = np.asarray(out).copy()
    arr[:, :, 3] = a
    return Image.fromarray(arr, "RGBA")


def main(src_dir, mapping_file, greyscale=True, elements=False):
    pairs = []
    for line in open(mapping_file, encoding="utf-8"):
        line = line.split("#")[0].strip()
        if line:
            a, b = line.split()
            pairs.append((a, b))
    os.makedirs(DST, exist_ok=True)
    for src, name in pairs:
        path = os.path.join(src_dir, src + ".png")
        if not os.path.exists(path):
            print("нет файла:", path)
            continue
        im = autocrop(Image.open(path).convert("RGB"), pad=2 if elements else 8)
        if elements:
            im = keyout_background(im)
        elif greyscale:
            im = im.convert("L")
        im.save(os.path.join(DST, name + ".png"), optimize=True)
        print("%-10s -> %-26s %dx%d %s"
              % (src, name, *im.size, "RGBA" if elements else im.mode))


if __name__ == "__main__":
    args = sys.argv[1:]
    elements = "--elements" in args
    args = [a for a in args if a != "--elements"]
    if len(args) < 2:
        print(__doc__)
        raise SystemExit(1)
    main(args[0], args[1], elements=elements)
