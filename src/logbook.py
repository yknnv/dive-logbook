#!/usr/bin/env python3
"""Журнал погружений — A5, перфорация под кольцевой переплёт.
Подписи полей дублируются на русском и английском."""

import os

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
from reportlab.lib.colors import CMYKColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont as RLTTFont

from reference import build_reference

# ------------------------------------------------------------------ шрифты
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_D = os.path.join(_ROOT, "assets", "fonts") + os.sep
if not os.path.exists(_D + "Carlito-Regular.ttf"):
    _D = "/usr/share/fonts/truetype/crosextra/"     # запасной вариант: системный шрифт
pdfmetrics.registerFont(RLTTFont("Body", _D + "Carlito-Regular.ttf"))
pdfmetrics.registerFont(RLTTFont("BodyB", _D + "Carlito-Bold.ttf"))
pdfmetrics.registerFont(RLTTFont("Lbl", _D + "Carlito-Regular.ttf"))
pdfmetrics.registerFont(RLTTFont("LblB", _D + "Carlito-Bold.ttf"))
BODY, BOLD = "Body", "BodyB"        # проза
LBL, LBLB = "Lbl", "LblB"           # подписи полей и заголовки

# Carlito мельче DejaVu при том же кегле — компенсируем единым множителем.
# Он применяется и при отрисовке, и при замерах ширины, иначе подгонка
# подписей под колонку начнёт врать.
FONT_SCALE = 1.13


def scale_canvas(c):
    raw = c.stringWidth
    c.stringWidth = lambda s, f, sz, *a, **k: raw(s, f, sz * FONT_SCALE, *a, **k)
    return c

# ------------------------------------------------------------------ палитра
INK    = CMYKColor(0, 0, 0, 1)          # чистый K — чёткий текст на печати
ACCENT = CMYKColor(0, 0, 0, 1)
LABEL  = CMYKColor(0, 0, 0, 0.62)       # русская подпись
LABEL2 = CMYKColor(0, 0, 0, 0.40)       # английский дубль
RULE   = CMYKColor(0, 0, 0, 0.32)
GRID   = CMYKColor(0, 0, 0, 0.14)
FAINT  = CMYKColor(0, 0, 0, 0.08)
PUNCH  = CMYKColor(0, 0, 0, 0.22)



# ------------------------------------------------------------------ картинки
IMG_DIR = os.path.join(_ROOT, "assets", "images")


def img(c, name, x, y, w, h, align="c"):
    """Иллюстрация в бокс (x, y — левый верх, w×h). Пропорции сохраняются,
    картинка вписывается и центрируется. Возвращает израсходованную высоту."""
    path = os.path.join(IMG_DIR, name if name.endswith(".png") else name + ".png")
    if not os.path.exists(path):
        return 0.0
    ir = ImageReader(path)
    iw, ih = ir.getSize()
    k = min(w / iw, h / ih)
    dw, dh = iw * k, ih * k
    dx = x + (w - dw) / 2 if align == "c" else x
    c.drawImage(ir, dx, y - dh, dw, dh, mask="auto")
    return dh

# ------------------------------------------------------------------ геометрия
TRIM_W, TRIM_H = 148 * mm, 210 * mm

MT, MB = 10 * mm, 10 * mm
M_BIND = 23 * mm          # поле со стороны колец
M_OUT  = 10 * mm

# перфорация: 4 отверстия, центры по высоте листа, диаметр 6 мм
HOLE_D = 6 * mm
HOLE_INSET = 11 * mm      # от края листа до центра отверстия
HOLE_SPACING = 47 * mm    # между центрами соседних отверстий
HOLE_MARKS = True         # печатать метки под пробойник

N_DIVES = 42
N_NOTES = 10

VERSION = "1.0"        # ставится в имя файла и в свойства PDF
KEEP_CREATED_WITH_AI = True   # строка на титуле; выключается без правки композиции


def hole_centers():
    n = 4
    span = HOLE_SPACING * (n - 1)
    top = TRIM_H / 2 + span / 2
    return [top - i * HOLE_SPACING for i in range(n)]


# ------------------------------------------------------------------ примитивы
def margins(page_no):
    """Нечётные — лицевая сторона, кольца слева. Чётные — оборот, кольца справа."""
    if page_no % 2 == 1:
        return M_BIND, M_OUT
    return M_OUT, M_BIND


def txt(c, x, y, s, font, size, color, space=0.0, align="l"):
    w = c.stringWidth(s, font, size) + space * len(s)
    if align == "c":
        x -= w / 2
    elif align == "r":
        x -= w
    t = c.beginText(x, y)
    t.setFont(font, size * FONT_SCALE)
    t.setCharSpace(space)
    t.setFillColor(color)
    t.textOut(s)
    c.drawText(t)
    return w


def caps(c, x, y, text, size=5.6, color=LABEL, space=0.7, font=LBLB):
    return txt(c, x, y, text.upper(), font, size, color, space)


def bilabel(c, x, y, ru, en, size=5.4, maxw=None):
    """Русская подпись жирным, английская — светлее.
    Если пара не влезает даже в минимальном кегле, английский дубль опускается."""
    ru, en = ru.upper(), en.upper()
    en_s = "/ " + en

    def pair_w(s):
        return (c.stringWidth(ru, LBLB, s) + 0.4 * len(ru) + 1.3 * mm
                + c.stringWidth(en_s, LBL, s * 0.83) + 0.3 * len(en_s))

    while size > 3.9 and maxw is not None and pair_w(size) > maxw:
        size -= 0.1

    if maxw is not None and pair_w(size) > maxw:
        s = size
        while s > 3.6 and c.stringWidth(ru, LBLB, s) + 0.4 * len(ru) > maxw:
            s -= 0.1
        txt(c, x, y, ru, LBLB, s, LABEL, 0.4)
        return

    w1 = txt(c, x, y, ru, LBLB, size, LABEL, 0.4)
    txt(c, x + w1 + 1.3 * mm, y, en_s, LBL, size * 0.83, LABEL2, 0.3)


def field(c, x, y, w, ru, en, h=9 * mm, size=5.4):
    bilabel(c, x, y + h - 3.7 * mm, ru, en, size, maxw=w)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.4)
    c.line(x, y, x + w, y)


def cols(x, w, n, gap=4 * mm):
    cw = (w - gap * (n - 1)) / n
    return [(x + i * (cw + gap), cw) for i in range(n)]


def checkrow(c, x, y, w, items, ncols=4, size=5.2):
    """Чекбоксы по фиксированной сетке колонок — строки выравниваются между собой."""
    box = 2.6 * mm
    cw = w / ncols
    for i, (ru, en) in enumerate(items):
        cx = x + i * cw
        ru_u, en_u = ru.upper(), " / " + en.upper()
        s = size
        while s > 4.2:
            need = (box + 1.2 * mm
                    + c.stringWidth(ru_u, LBLB, s) + 0.2 * len(ru_u)
                    + c.stringWidth(en_u, LBL, s * 0.85) + 0.2 * len(en_u))
            if need <= cw - 2 * mm:
                break
            s -= 0.1
        c.setStrokeColor(RULE)
        c.setLineWidth(0.4)
        c.rect(cx, y, box, box, stroke=1, fill=0)
        tw = txt(c, cx + box + 1.2 * mm, y + 0.6 * mm, ru_u, LBLB, s, LABEL, 0.2)
        txt(c, cx + box + 1.2 * mm + tw, y + 0.6 * mm, en_u, LBL, s * 0.85, LABEL2, 0.2)


def rating(c, x, y, w, ru, en, n=5, size=5.2):
    """Шкала самооценки: подпись и n пронумерованных квадратов."""
    bilabel(c, x, y + 0.7 * mm, ru, en, size, maxw=w)
    box = 3.2 * mm
    step = 7.0 * mm
    bx = x + w - n * step + (step - box)
    for i in range(n):
        cx = bx + i * step
        c.setStrokeColor(RULE)
        c.setLineWidth(0.4)
        c.rect(cx, y, box, box, stroke=1, fill=0)
        txt(c, cx + box / 2, y + 0.9 * mm, str(i + 1), LBL, 4.6, LABEL2, 0, "c")


def block_head(c, x, y, w, ru, en):
    """Заголовок группы полей внутри карточки."""
    caps(c, x, y, ru, 5.8, ACCENT, 0.9)
    txt(c, x + w, y, en, LBL, 5.0, LABEL2, 0.6, "r")
    return 5.6 * mm


def punch(c, page_no):
    if not HOLE_MARKS:
        return
    left = page_no % 2 == 1
    cx = HOLE_INSET if left else TRIM_W - HOLE_INSET
    c.setStrokeColor(PUNCH)
    c.setLineWidth(0.3)
    for cy in hole_centers():
        c.setDash(0.8, 1.2)
        c.circle(cx, cy, HOLE_D / 2, stroke=1, fill=0)
        c.setDash()
        c.line(cx - 1.4 * mm, cy, cx + 1.4 * mm, cy)
        c.line(cx, cy - 1.4 * mm, cx, cy + 1.4 * mm)


def folio(c, page_no):
    """Номера страниц не печатаются: листы съёмные."""
    return


# ------------------------------------------------------------------ страницы
def cover(c):
    cx = TRIM_W / 2 + (M_BIND - M_OUT) / 2
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.8)
    c.rect(M_BIND - 5 * mm, 12 * mm,
           TRIM_W - M_BIND - M_OUT + 10 * mm, TRIM_H - 24 * mm, stroke=1, fill=0)

    img(c, "d-01-frontispiece", cx - 40 * mm, 118 * mm, 80 * mm, 52 * mm)

    ty = TRIM_H - 66 * mm
    w1 = c.stringWidth("DIVE", LBLB, 30) + 3.0 * 4
    w2 = c.stringWidth("logbook", LBL, 30) + 1.2 * 7
    tx = cx - (w1 + 3.5 * mm + w2) / 2
    txt(c, tx, ty, "DIVE", LBLB, 30, ACCENT, 3.0)
    txt(c, tx + w1 + 3.5 * mm, ty, "logbook", LBL, 30, LABEL, 1.2)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.2)
    c.line(cx - 16 * mm, ty - 10 * mm, cx + 16 * mm, ty - 10 * mm)
    txt(c, cx, ty - 18 * mm, "ЛИЧНЫЙ ЖУРНАЛ ДАЙВЕРА · PERSONAL DIVING RECORD",
        LBL, 6.4, LABEL2, 1.4, "c")

    txt(c, cx, 24 * mm, "Author: Yury Kononov", LBL, 7.2, LABEL, 0.8, "c")
    txt(c, cx, 19.5 * mm, "ykononov.com", LBL, 6.6, LABEL2, 0.8, "c")
    if KEEP_CREATED_WITH_AI:
        txt(c, cx, 15 * mm, "Created with AI", LBL, 6.2, LABEL2, 0.8, "c")

    x = M_BIND
    w = TRIM_W - M_BIND - M_OUT
    field(c, x, 46 * mm, w, "владелец", "name")
    a, b = cols(x, w, 2)
    field(c, a[0], 32 * mm, a[1], "квалификация", "level")
    field(c, b[0], 32 * mm, b[1], "том №", "book no.")
    punch(c, 1)


def personal(c):
    ml, mr = margins(2)
    x, w = ml, TRIM_W - ml - mr
    y = TRIM_H - MT

    caps(c, x, y - 5 * mm, "данные дайвера", 8.4, ACCENT, 1.8)
    txt(c, x + w, y - 5 * mm, "DIVER DETAILS", LBL, 6.4, LABEL2, 1.2, "r")
    y -= 9 * mm
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.8)
    c.line(x, y, x + w, y)
    y -= 11 * mm

    rows = [
        [("фамилия, имя", "full name", 1.0)],
        [("дата рождения", "date of birth", 0.5), ("группа крови", "blood type", 0.5)],
        [("адрес", "address", 1.0)],
        [("город, страна", "city, country", 0.62), ("индекс", "postcode", 0.38)],
        [("телефон", "phone", 0.5), ("e-mail", "e-mail", 0.5)],
        [("паспорт", "passport / id", 1.0)],
    ]
    for row in rows:
        cx, gap = x, 4 * mm
        avail = w - gap * (len(row) - 1)
        for ru, en, frac in row:
            cw = avail * frac
            field(c, cx, y, cw, ru, en, h=11 * mm)
            cx += cw + gap
        y -= 11 * mm

    def block(y, title, en, pairs):
        caps(c, x, y, title, 6.6, ACCENT, 1.3)
        txt(c, x + w, y, en, LBL, 5.8, LABEL2, 1.0, "r")
        y -= 14 * mm
        for l, r in pairs:
            a, b = cols(x, w, 2)
            field(c, a[0], y, a[1], l[0], l[1], h=11 * mm)
            field(c, b[0], y, b[1], r[0], r[1], h=11 * mm)
            y -= 11 * mm
        return y

    y -= 3 * mm
    y = block(y, "экстренный контакт", "EMERGENCY CONTACT",
              [(("кто", "name"), ("кем приходится", "relationship")),
               (("телефон", "phone"), ("e-mail", "e-mail"))])
    y -= 1 * mm
    y = block(y, "страховка", "INSURANCE",
              [(("компания", "provider"), ("номер полиса", "policy no.")),
               (("действует до", "valid until"), ("линия 24 ч", "24 h line"))])
    y -= 1 * mm
    caps(c, x, y, "медицина", 6.6, ACCENT, 1.3)
    txt(c, x + w, y, "MEDICAL", LBL, 5.8, LABEL2, 1.0, "r")
    y -= 14 * mm
    field(c, x, y, w, "последний медосмотр, ограничения", "last check", h=11 * mm)
    y -= 11 * mm
    field(c, x, y, w, "аллергии, препараты", "allergies, medication", h=11 * mm)

    assert y >= MB, "стр. 2 переполнена: %.1f мм" % (y / mm)
    punch(c, 2)
    folio(c, 2)


def table_page(c, page_no, title, title_en, headers, widths, n_rows, row_h=9 * mm):
    ml, mr = margins(page_no)
    x, w = ml, TRIM_W - ml - mr
    y = TRIM_H - MT

    caps(c, x, y - 5 * mm, title, 8.4, ACCENT, 1.8)
    txt(c, x + w, y - 5 * mm, title_en, LBL, 6.4, LABEL2, 1.2, "r")
    y -= 9 * mm
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.8)
    c.line(x, y, x + w, y)
    y -= 6 * mm

    total = sum(widths)
    abs_w = [w * v / total for v in widths]

    cx = x
    for (ru, en), cw in zip(headers, abs_w):
        bilabel(c, cx + 1.5 * mm, y - 3.2 * mm, ru, en, 5.0, maxw=cw - 3 * mm)
        cx += cw
    y -= 5 * mm

    top = y
    for r in range(n_rows + 1):
        yy = top - r * row_h
        c.setStrokeColor(ACCENT if r == 0 else RULE)
        c.setLineWidth(0.6 if r == 0 else 0.4)
        c.line(x, yy, x + w, yy)
    bottom = top - n_rows * row_h

    cx = x
    c.setStrokeColor(GRID)
    c.setLineWidth(0.35)
    for cw in abs_w[:-1]:
        cx += cw
        c.line(cx, top, cx, bottom)

    punch(c, page_no)
    folio(c, page_no)


def dive_page_a(c, page_no):
    """Левая страница разворота: идентификация, время, профиль, газ."""
    ml, mr = margins(page_no)
    x, w = ml, TRIM_W - ml - mr
    y = TRIM_H - MT
    cs = cols(x, w, 3, 4 * mm)
    c2 = cols(x, w, 2, 4 * mm)

    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.0)
    c.line(x, y, x + w, y)
    y -= 9.5 * mm
    hw = 34 * mm
    bilabel(c, x, y + 5.9 * mm, "погружение №", "dive no.", 5.6, maxw=hw)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.7)
    c.line(x, y, x + hw, y)
    field(c, x + hw + 4 * mm, y, w - hw - 4 * mm, "дата", "date", h=9.5 * mm)

    aw = w * 0.56
    bx, bw = x + aw + 4 * mm, w - aw - 4 * mm
    for a_ru, a_en, b_ru, b_en in [
            ("место погружения", "dive site", "страна, регион", "country"),
            ("дайв-центр, судно", "dive centre / boat", "координаты", "coordinates"),
            ("бадди", "buddy", "инструктор, гид", "instructor / guide")]:
        y -= 10 * mm
        field(c, x, y, aw, a_ru, a_en, h=10 * mm)
        field(c, bx, y, bw, b_ru, b_en, h=10 * mm)

    y -= 8 * mm
    y -= block_head(c, x, y, w, "время", "TIME")
    for row in [[("вход в воду", "time in"), ("выход", "time out"), ("под водой, мин", "total time")],
                [("интервал", "surface interval"), ("№ за день", "dive of day"), ("", "")]]:
        y -= 9.5 * mm
        for (cx, cw), (ru, en) in zip(cs, row):
            if ru:
                field(c, cx, y, cw, ru, en, h=9.5 * mm, size=5.2)

    y -= 7 * mm
    y -= block_head(c, x, y, w, "профиль", "PROFILE")
    for row in [[("макс. глубина, м", "max depth"), ("сред. глубина, м", "avg depth"),
                 ("остановка, мин", "safety stop")],
                [("ndl на выходе, мин", "ndl remaining"), ("", ""), ("", "")]]:
        y -= 9.5 * mm
        for (cx, cw), (ru, en) in zip(cs, row):
            if ru:
                field(c, cx, y, cw, ru, en, h=9.5 * mm, size=5.2)
    y -= 6.2 * mm
    caps(c, x, y + 0.4 * mm, "декомпрессионное обязательство", 5.0, LABEL, 0.5)
    checkrow(c, x + w * 0.62, y, w * 0.38, [("нет", "no"), ("да", "yes")], ncols=2)

    y -= 7 * mm
    y -= block_head(c, x, y, w, "газ", "GAS")
    for row in [[("смесь", "gas"), ("замер O\u2082, %", "analysed"), ("объём баллона, л", "cylinder")],
                [("вход, бар", "start"), ("выход, бар", "end"), ("расход, бар", "used")]]:
        y -= 9.5 * mm
        for (cx, cw), (ru, en) in zip(cs, row):
            field(c, cx, y, cw, ru, en, h=9.5 * mm, size=5.2)
    y -= 6.2 * mm
    caps(c, x, y + 0.4 * mm, "материал баллона", 5.0, LABEL, 0.5)
    checkrow(c, x + w * 0.40, y, w * 0.34, [("алюминий", "al"), ("сталь", "steel")], ncols=2)
    field(c, x + w * 0.78, y - 3.5 * mm, w * 0.22, "rmv, л/мин", "rmv", h=9.5 * mm, size=5.2)
    y -= 3.5 * mm

    y -= 7 * mm
    y -= block_head(c, x, y, w, "профиль погружения", "DIVE PROFILE")
    txt(c, x + w, y + 5.6 * mm, "ВРЕМЯ (МИН) → ГЛУБИНА (М) ↓", LBL, 4.6, LABEL2, 0.3, "r")
    ph = min(y - MB - 2 * mm, 34 * mm)
    py = y - ph
    c.setStrokeColor(GRID)
    c.setLineWidth(0.3)
    for k in range(1, 12):
        gx = x + w * k / 12
        c.line(gx, py, gx, py + ph)
    for k in range(1, 8):
        gy = py + ph * k / 8
        c.line(x, gy, x + w, gy)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    c.rect(x, py, w, ph, stroke=1, fill=0)
    for k, dep in enumerate((10, 20, 30)):
        gy = py + ph * (8 - (k + 1) * 2) / 8
        txt(c, x + 1.2 * mm, gy + 0.8 * mm, str(dep), LBL, 4.6, LABEL2)
    y = py

    assert y >= MB, "карточка A переполнена: %.1f мм" % (y / mm)
    punch(c, page_no)


def dive_page_b(c, page_no):
    """Правая страница разворота: среда, снаряжение, оценка, подписи."""
    ml, mr = margins(page_no)
    x, w = ml, TRIM_W - ml - mr
    y = TRIM_H - MT
    cs = cols(x, w, 3, 4 * mm)

    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.0)
    c.line(x, y, x + w, y)
    y -= 5.5 * mm

    y -= block_head(c, x, y, w, "среда", "ENVIRONMENT")
    for row in [[("темп. воды, °C", "water"), ("темп. воздуха, °C", "air"), ("видимость, м", "visibility")],
                [("вход", "entry"), ("выход", "exit"), ("море, погода", "sea state")]]:
        y -= 9.0 * mm
        for (cx, cw), (ru, en) in zip(cs, row):
            field(c, cx, y, cw, ru, en, h=9.0 * mm, size=5.2)
    y -= 5.6 * mm
    caps(c, x, y + 0.4 * mm, "течение", 5.0, LABEL, 0.5)
    checkrow(c, x + w * 0.20, y, w * 0.80,
             [("нет", "none"), ("слабое", "light"), ("умеренное", "moderate"),
              ("сильное", "strong")], ncols=4)

    y -= 6 * mm
    y -= block_head(c, x, y, w, "снаряжение", "EQUIPMENT")
    for row in [[("костюм и толщина", "suit"), ("компенсатор", "bcd"), ("груз, кг", "weight")],
                [("регулятор", "regulator"), ("компьютер", "computer"), ("№ погружения", "computer no.")]]:
        y -= 9.0 * mm
        for (cx, cw), (ru, en) in zip(cs, row):
            field(c, cx, y, cw, ru, en, h=9.0 * mm, size=5.2)
    for group in [[("шлем", "hood"), ("перчатки", "gloves"), ("боты", "boots"), ("фонарь", "torch")],
                  [("буй", "dsmb"), ("катушка", "spool"), ("камера", "camera"), ("нож", "knife")]]:
        y -= 5.6 * mm
        checkrow(c, x, y, w, group)

    y -= 6 * mm
    y -= block_head(c, x, y, w, "тип погружения", "DIVE TYPE")
    for group in [[("лодка", "boat"), ("берег", "shore"), ("ночь", "night"), ("дрейф", "drift")],
                  [("рэк", "wreck"), ("глубина", "deep"), ("обучение", "training"), ("сухарь", "dry suit")],
                  [("пресная", "fresh"), ("солёная", "salt"), ("", ""), ("", "")]]:
        y -= 5.6 * mm
        checkrow(c, x, y, w, [g for g in group if g[0]])

    y -= 6 * mm
    y -= block_head(c, x, y, w, "самооценка", "SELF-ASSESSMENT")
    for ru, en in [("комфорт", "comfort"), ("плавучесть", "buoyancy"), ("контроль газа", "gas")]:
        y -= 6.8 * mm
        rating(c, x, y, w, ru, en)

    y -= 5 * mm
    y -= block_head(c, x, y, w, "заметки, подводный мир", "NOTES")
    c.setStrokeColor(RULE)
    c.setLineWidth(0.4)
    for _ in range(3):
        y -= 6.4 * mm
        c.line(x, y, x + w, y)

    y -= 4 * mm
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.7)
    c.line(x, y, x + w, y)
    stamp_w = 33 * mm
    left_w = w - stamp_w - 5 * mm
    a, b = cols(x, left_w, 2, 4 * mm)
    top = y
    y -= 9.4 * mm
    field(c, a[0], y, a[1], "бадди, инструктор", "verified by", h=9.4 * mm, size=5.2)
    field(c, b[0], y, b[1], "№ сертификата", "cert. no.", h=9.4 * mm, size=5.2)
    y -= 9.4 * mm
    field(c, a[0], y, a[1], "подпись", "signature", h=9.4 * mm, size=5.2)
    field(c, b[0], y, b[1], "всего погружений", "total dives", h=9.4 * mm, size=5.2)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    c.setDash(1.6, 1.6)
    c.rect(x + w - stamp_w, y, stamp_w, top - y - 2 * mm, stroke=1, fill=0)
    c.setDash()
    scy = y + (top - y - 2 * mm) / 2
    txt(c, x + w - stamp_w / 2, scy + 1.2 * mm, "ПЕЧАТЬ", LBL, 5.1, LABEL, 0.5, "c")
    txt(c, x + w - stamp_w / 2, scy - 3 * mm, "ДАЙВ-ЦЕНТРА", LBL, 5.1, LABEL, 0.5, "c")

    assert y >= MB, "карточка B переполнена: %.1f мм" % (y / mm)
    punch(c, page_no)


def summary_page(c, page_no):
    ml, mr = margins(page_no)
    x, w = ml, TRIM_W - ml - mr
    y = TRIM_H - MT

    caps(c, x, y - 5 * mm, "итоги", 8.4, ACCENT, 1.8)
    txt(c, x + w, y - 5 * mm, "LOGBOOK SUMMARY", LBL, 6.4, LABEL2, 1.2, "r")
    y -= 9 * mm
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.8)
    c.line(x, y, x + w, y)
    y -= 14 * mm

    pairs = [
        (("всего погружений", "total dives"), ("общее время, ч : мин", "total time")),
        (("максимальная глубина, м", "deepest"), ("самое долгое, мин", "longest")),
        (("самая холодная вода, °C", "coldest"), ("стран посещено", "countries")),
        (("ночных", "night dives"), ("на рэках", "wreck dives")),
        (("на нитроксе", "nitrox dives"), ("учебных", "training dives")),
    ]
    for l, r in pairs:
        a, b = cols(x, w, 2)
        field(c, a[0], y, a[1], l[0], l[1], h=14 * mm)
        field(c, b[0], y, b[1], r[0], r[1], h=14 * mm)
        y -= 14 * mm

    y -= 4 * mm
    caps(c, x, y, "заметки", 6.6, ACCENT, 1.3)
    txt(c, x + w, y, "NOTES", LBL, 5.8, LABEL2, 1.0, "r")
    y -= 8 * mm
    c.setStrokeColor(RULE)
    c.setLineWidth(0.4)
    while y > MB + 4 * mm:
        c.line(x, y, x + w, y)
        y -= 8 * mm

    punch(c, page_no)
    folio(c, page_no)



def summary_page2(c, page_no):
    """Вторая страница итогов: разбивка по типам и сводка по годам."""
    ml, mr = margins(page_no)
    x, w = ml, TRIM_W - ml - mr
    y = TRIM_H - MT
    caps(c, x, y - 5 * mm, "итоги по типам", 8.4, ACCENT, 1.8)
    txt(c, x + w, y - 5 * mm, "BY TYPE", LBL, 6.4, LABEL2, 1.2, "r")
    y -= 9 * mm
    c.setStrokeColor(ACCENT); c.setLineWidth(0.8)
    c.line(x, y, x + w, y)
    y -= 12 * mm
    pairs = [(("ночных", "night"), ("на нитроксе", "nitrox")),
             (("на рэках", "wreck"), ("дрейфовых", "drift")),
             (("глубоких", "deep"), ("в сухаре", "dry suit")),
             (("в пресной воде", "fresh water"), ("в солёной воде", "salt water")),
             (("с лодки", "boat"), ("с берега", "shore")),
             (("учебных", "training"), ("стран", "countries"))]
    for l, r in pairs:
        a, b = cols(x, w, 2)
        field(c, a[0], y, a[1], l[0], l[1], h=12 * mm)
        field(c, b[0], y, b[1], r[0], r[1], h=12 * mm)
        y -= 12 * mm

    y -= 6 * mm
    caps(c, x, y, "по годам", 6.6, ACCENT, 1.3)
    txt(c, x + w, y, "BY YEAR", LBL, 5.8, LABEL2, 1.0, "r")
    y -= 8 * mm
    heads = [("год", "year"), ("погружений", "dives"), ("часов", "hours"),
             ("макс. глубина", "deepest"), ("ночных", "night")]
    widths = [0.7, 0.9, 0.8, 1.0, 0.8]
    total = sum(widths)
    cw = [w * v / total for v in widths]
    cx = x
    for (ru, en), ww in zip(heads, cw):
        bilabel(c, cx + 1.5 * mm, y - 3.2 * mm, ru, en, 5.0, maxw=ww - 3 * mm)
        cx += ww
    top = y - 5 * mm
    c.setStrokeColor(ACCENT); c.setLineWidth(0.6)
    c.line(x, top, x + w, top)
    rows = int((top - MB - 2 * mm) / (9 * mm))
    for r in range(rows):
        c.setStrokeColor(RULE); c.setLineWidth(0.35)
        c.line(x, top - (r + 1) * 9 * mm, x + w, top - (r + 1) * 9 * mm)
    cx = x
    c.setStrokeColor(GRID); c.setLineWidth(0.3)
    for ww in cw[:-1]:
        cx += ww
        c.line(cx, top, cx, top - rows * 9 * mm)
    punch(c, page_no)


def notes_page(c, page_no):
    ml, mr = margins(page_no)
    x, w = ml, TRIM_W - ml - mr
    caps(c, x, TRIM_H - MT - 5 * mm, "заметки", 8.4, ACCENT, 1.8)
    txt(c, x + w, TRIM_H - MT - 5 * mm, "NOTES", LBL, 6.4, LABEL2, 1.2, "r")
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.8)
    c.line(x, TRIM_H - MT - 9 * mm, x + w, TRIM_H - MT - 9 * mm)
    y = TRIM_H - MT - 21 * mm
    c.setStrokeColor(RULE)
    c.setLineWidth(0.4)
    while y > MB + 4 * mm:
        c.line(x, y, x + w, y)
        y -= 8 * mm
    punch(c, page_no)
    folio(c, page_no)


def crop_marks(c, bleed):
    L, off = 4 * mm, 1.5 * mm
    c.setStrokeColor(INK)
    c.setLineWidth(0.25)
    for cx, cy, sx, sy in [(bleed, bleed, -1, -1),
                           (bleed + TRIM_W, bleed, 1, -1),
                           (bleed, bleed + TRIM_H, -1, 1),
                           (bleed + TRIM_W, bleed + TRIM_H, 1, 1)]:
        c.line(cx + sx * off, cy, cx + sx * (off + L), cy)
        c.line(cx, cy + sy * off, cx, cy + sy * (off + L))


# ------------------------------------------------------------------ сборка
def build(path, bleed=0.0, marks=False):
    pw, ph = TRIM_W + 2 * bleed, TRIM_H + 2 * bleed
    c = scale_canvas(canvas.Canvas(path, pagesize=(pw, ph)))
    c.setTitle("DIVE logbook")
    c.setSubject("A5, перфорация под кольца · версия %s" % VERSION)
    c.setKeywords("version %s" % VERSION)

    def start():
        c.saveState()
        c.translate(bleed, bleed)

    def end():
        c.restoreState()
        if marks:
            crop_marks(c, bleed)
        c.showPage()

    ctx = dict(c=c, TRIM_W=TRIM_W, TRIM_H=TRIM_H, MT=MT, MB=MB,
               INK=INK, ACCENT=ACCENT, LABEL=LABEL, LABEL2=LABEL2,
               RULE=RULE, GRID=GRID, FAINT=FAINT,
               BODY=BODY, BOLD=BOLD, LBL=LBL, LBLB=LBLB,
               margins=margins, caps=caps, txt=txt, field=field, img=img,
               bilabel=bilabel, cols=cols, folio=folio, punch=punch)
    ref_pages = build_reference(ctx)

    start(); cover(c);    end()
    start(); personal(c); end()

    for i, draw in enumerate(ref_pages):
        start(); draw(3 + i); end()

    p = 3 + len(ref_pages)
    start()
    table_page(c, p, "сертификаты", "CERTIFICATIONS",
               [("агентство", "agency"), ("уровень", "level"), ("№", "cert. no."),
                ("дата", "date"), ("инструктор", "instructor")],
               [1.15, 1.25, 1.15, 0.8, 1.25], 18)
    end()

    p += 1
    start()
    table_page(c, p, "снаряжение", "EQUIPMENT RECORD",
               [("предмет", "item"), ("марка, модель", "brand"),
                ("серийный №", "serial no."), ("обслуживание", "service")],
               [1.0, 1.55, 1.1, 1.0], 18)
    end()

    if (p + 1) % 2:                 # карточка начинается с чётной страницы разворота
        p += 1
        start(); notes_page(c, p); end()
    for i in range(N_DIVES):
        start(); dive_page_a(c, p + 1 + 2 * i); end()
        start(); dive_page_b(c, p + 2 + 2 * i); end()

    p = p + 2 * N_DIVES + 1
    start(); summary_page(c, p); end()
    p += 1
    start(); summary_page2(c, p); end()
    for _ in range(N_NOTES):
        p += 1
        start(); notes_page(c, p); end()
    if p % 2:                      # добор до чётного: печать двусторонняя
        p += 1
        start(); notes_page(c, p); end()

    c.save()
    return p


def punch_template(path):
    """Лист 1:1 для проверки перфорации перед печатью тиража."""
    c = canvas.Canvas(path, pagesize=(TRIM_W, TRIM_H))
    c.setTitle("Шаблон перфорации A5")
    x, w = M_BIND, TRIM_W - M_BIND - M_OUT

    caps(c, x, TRIM_H - MT - 5 * mm, "шаблон перфорации", 8.4, ACCENT, 1.8)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.8)
    c.line(x, TRIM_H - MT - 9 * mm, x + w, TRIM_H - MT - 9 * mm)

    lines = [
        "Распечатайте этот лист в масштабе 100 % (без «вписать",
        "в страницу») и приложите к обложке. Центры отверстий",
        "должны совпасть с кольцами.",
        "",
        "Числа у отверстий — расстояние от нижнего края листа",
        "до центра отверстия.",
        "",
        "Текущие параметры:",
        "     лист  148 × 210 мм (A5)",
        "     отверстий  4,  диаметр %.0f мм" % (HOLE_D / mm),
        "     шаг между центрами  %.0f мм" % (HOLE_SPACING / mm),
        "     от края до центра  %.0f мм" % (HOLE_INSET / mm),
        "     поле под кольца  %.0f мм" % (M_BIND / mm),
        "",
        "Не совпало — измерьте обложку и поправьте HOLE_SPACING,",
        "HOLE_INSET и M_BIND в начале divelog.py, затем",
        "пересоберите файл.",
    ]
    y = TRIM_H - MT - 22 * mm
    for ln in lines:
        txt(c, x, y, ln, BODY, 8, INK)
        y -= 4.7 * mm

    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.6)
    for cy in hole_centers():
        c.circle(HOLE_INSET, cy, HOLE_D / 2, stroke=1, fill=0)
        c.line(HOLE_INSET - 4 * mm, cy, HOLE_INSET + 4 * mm, cy)
        c.line(HOLE_INSET, cy - 4 * mm, HOLE_INSET, cy + 4 * mm)
        txt(c, HOLE_INSET, cy - HOLE_D / 2 - 3.4 * mm,
            "%.0f мм" % (cy / mm), LBL, 5.8, LABEL2, 0, "c")

    c.setStrokeColor(RULE)
    c.setLineWidth(0.4)
    c.setDash(2, 2)
    c.line(M_BIND, MB, M_BIND, TRIM_H - MT)
    c.setDash()
    txt(c, M_BIND + 1.5 * mm, MB + 2 * mm, "граница набора", LBL, 5.8, LABEL2)
    c.save()


if __name__ == "__main__":
    n = build(os.path.join(_ROOT, "dist", "dive-logbook-A5-final.pdf"))
    build(os.path.join(_ROOT, "dist", "dive-logbook-A5-final-bleed3mm-cropmarks.pdf"), bleed=3 * mm, marks=True)
    punch_template(os.path.join(_ROOT, "dist", "punch-template-A5.pdf"))
    print("страниц:", n, "| погружений:", N_DIVES)
