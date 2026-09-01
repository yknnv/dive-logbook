#!/usr/bin/env python3
"""Подготовка новых иллюстраций к вёрстке.

Обрезает лишние белые поля, переводит в градации серого и раскладывает
под именами, которые ожидает вёрстка.

    python3 tools/prepare_illustrations.py входная_папка mapping.txt

mapping.txt — по строке на файл:

    S-22  s-22-shore-line
    S-23  s-23-stern-to
"""
import os
import sys

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


def main(src_dir, mapping_file, greyscale=True):
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
        im = autocrop(Image.open(path).convert("RGB"))
        if greyscale:
            im = im.convert("L")
        im.save(os.path.join(DST, name + ".png"), optimize=True)
        print("%-10s -> %-26s %dx%d" % (src, name, *im.size))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(1)
    main(sys.argv[1], sys.argv[2])
