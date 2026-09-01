#!/usr/bin/env python3
"""Проверка: не вылезает ли что-нибудь за границы набора."""
import sys
import itertools

import pdfplumber

MM = 72 / 25.4
TRIM_W, TRIM_H = 148 * MM, 210 * MM
MT = MB = 10 * MM
M_BIND, M_OUT = 23 * MM, 10 * MM
HOLE_INSET = 11 * MM

TOL = 0.15            # мм допуска
TOLP = TOL * MM


def box(page_no):
    """Границы набора в координатах pdfplumber (top-down)."""
    ml, mr = (M_BIND, M_OUT) if page_no % 2 else (M_OUT, M_BIND)
    return ml, TRIM_W - mr, MT, TRIM_H - MB     # x0, x1, top, bottom


def is_punch(page_no, x0, x1, top, bottom):
    """Метки перфорации живут в поле переплёта — это норма."""
    cx = HOLE_INSET if page_no % 2 else TRIM_W - HOLE_INSET
    return (abs((x0 + x1) / 2 - cx) < 5 * MM and (x1 - x0) < 8 * MM
            and (bottom - top) < 8 * MM)


def check(path, skip_pages=()):
    bad = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            if i in skip_pages:
                continue
            lx, rx, ty, by = box(i)
            items = []
            for ch in page.chars:
                items.append(("текст «%s»" % ch["text"], ch["x0"], ch["x1"],
                              ch["top"], ch["bottom"]))
            for o in page.lines + page.rects + page.curves:
                items.append(("линия/фигура", o["x0"], o["x1"], o["top"], o["bottom"]))

            for kind, x0, x1, top, bottom in items:
                if is_punch(i, x0, x1, top, bottom):
                    continue
                # фолио печатается ниже поля намеренно
                if top > by:
                    if kind.startswith("текст") and top - by < 6 * MM:
                        continue
                over = []
                if x0 < lx - TOLP:
                    over.append("слева на %.1f мм" % ((lx - x0) / MM))
                if x1 > rx + TOLP:
                    over.append("справа на %.1f мм" % ((x1 - rx) / MM))
                if top < ty - TOLP:
                    over.append("сверху на %.1f мм" % ((ty - top) / MM))
                if bottom > by + TOLP:
                    over.append("снизу на %.1f мм" % ((bottom - by) / MM))
                if over:
                    bad.append((i, kind, ", ".join(over)))
    return bad




def check_vertical(path, skip_pages=()):
    """Слова не должны налезать друг на друга.

    Сравниваем именно слова, а не строки целиком: русская подпись и английский
    дубль стоят на одной базовой линии разным кеглем, и при построчном
    сравнении это давало ложные срабатывания.
    """
    bad = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            if i in skip_pages:
                continue
            words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
            words = [(w["x0"], w["x1"], w["top"], w["bottom"], w["text"]) for w in words]
            words.sort(key=lambda t: t[2])
            for a, b in itertools.combinations(words, 2):
                if b[2] >= a[3] - 0.3:
                    continue
                ovx = min(a[1], b[1]) - max(a[0], b[0])
                ovy = min(a[3], b[3]) - max(a[2], b[2])
                if ovx > 0.4 and ovy > 0.6:
                    bad.append((i, round(ovy / MM, 2), a[4], b[4]))
    return bad


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "dive-logbook-A5.pdf"
    skip = {1}                      # обложка: рамка намеренно шире набора
    res = check(path, skip)
    seen = {}
    for pno, kind, msg in res:
        seen.setdefault((pno, msg.split(" на ")[0], kind[:6]), []).append(kind)
    if not res:
        print("нарушений нет")
    for (pno, msg, k), lst in sorted(seen.items()):
        sample = lst[0][:60]
        print("стр. %-3d %-28s x%-4d %s" % (pno, msg, len(lst), sample))

    vert = check_vertical(path, skip)
    if vert:
        agg = {}
        for pno, ov, w1, w2 in vert:
            if ov > agg.get(pno, (0, "", ""))[0]:
                agg[pno] = (ov, w1, w2)
        for pno in sorted(agg):
            ov, w1, w2 = agg[pno]
            print("стр. %-3d наложение %.2f мм: «%s» и «%s»" % (pno, ov, w1[:24], w2[:24]))
    else:
        print("вертикальных наложений нет")
