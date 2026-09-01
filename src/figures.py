"""Векторные схемы для справочных разделов.

Каждая функция fig_* рисует иллюстрацию в прямоугольнике (x, y — левый верхний
угол, w — ширина) и возвращает израсходованную высоту.
"""

import math
from reportlab.lib.units import mm


def palette(ctx):
    return dict(c=ctx["c"], INK=ctx["INK"], ACCENT=ctx["ACCENT"],
                LABEL=ctx["LABEL"], LABEL2=ctx["LABEL2"], RULE=ctx["RULE"],
                GRID=ctx["GRID"], FAINT=ctx["FAINT"],
                BODY=ctx["BODY"], BOLD=ctx["BOLD"],
                LBL=ctx["LBL"], LBLB=ctx["LBLB"], txt=ctx["txt"])


# ---------------------------------------------------------------- примитивы
def _t(P, c, x, y, s, size=5.6, color=None, font=None, align="l", space=0.2):
    return P["txt"](c, x, y, s, font or P["LBL"], size,
                    color or P["LABEL"], space, align)


def arrow(c, P, x0, y0, x1, y1, color=None, lw=0.7, head=1.9 * mm, dash=None):
    c.setStrokeColor(color or P["ACCENT"])
    c.setFillColor(color or P["ACCENT"])
    c.setLineWidth(lw)
    if dash:
        c.setDash(*dash)
    ang = math.atan2(y1 - y0, x1 - x0)
    bx, by = x1 - head * 0.85 * math.cos(ang), y1 - head * 0.85 * math.sin(ang)
    c.line(x0, y0, bx, by)
    c.setDash()
    p = c.beginPath()
    p.moveTo(x1, y1)
    p.lineTo(x1 - head * math.cos(ang - 0.38), y1 - head * math.sin(ang - 0.38))
    p.lineTo(x1 - head * math.cos(ang + 0.38), y1 - head * math.sin(ang + 0.38))
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def boat(c, P, cx, cy, ang, L, color=None, sail=None, fill=False):
    """Корпус сверху, нос по умолчанию вверх. ang в градусах, по часовой.
    sail: None — без паруса, +1 — гик на правый борт, -1 — на левый."""
    col = color or P["INK"]
    c.saveState()
    c.translate(cx, cy)
    c.rotate(-ang)
    p = c.beginPath()
    p.moveTo(0, L * 0.52)
    p.curveTo(L * 0.20, L * 0.22, L * 0.23, -L * 0.12, L * 0.19, -L * 0.44)
    p.lineTo(-L * 0.19, -L * 0.44)
    p.curveTo(-L * 0.23, -L * 0.12, -L * 0.20, L * 0.22, 0, L * 0.52)
    p.close()
    c.setStrokeColor(col)
    c.setFillColor(P["FAINT"] if not fill else col)
    c.setLineWidth(0.6)
    c.drawPath(p, stroke=1, fill=1)
    if sail:
        s = c.beginPath()
        s.moveTo(0, L * 0.34)
        s.lineTo(sail * L * 0.30, -L * 0.30)
        s.lineTo(0, -L * 0.34)
        s.close()
        c.setFillColor(P["GRID"])
        c.setStrokeColor(col)
        c.setLineWidth(0.5)
        c.drawPath(s, stroke=1, fill=1)
    c.restoreState()


def wind_band(c, P, x, y, w, label="ВЕТЕР", n=3, gap=3.4 * mm):
    """Полоса стрелок ветра, направленных вниз."""
    for i in range(n):
        ax = x + w * (i + 0.5) / n
        arrow(c, P, ax, y, ax, y - 7 * mm, P["LABEL2"], 0.6, 1.6 * mm)
    if label:
        _t(P, c, x + w / 2, y + 1.5 * mm, label, 5.2, P["LABEL2"], P["LBLB"], "c", 0.8)
    return 11 * mm


def axes(c, P, x, y, w, h, xmax, ymax, xstep, ystep, xlab="", ylab="",
         invert_y=False, xfmt="%g", yfmt="%g"):
    """Сетка с подписями. Возвращает функцию преобразования (vx, vy) -> (px, py)."""
    c.setStrokeColor(P["GRID"])
    c.setLineWidth(0.3)
    nx = int(round(xmax / xstep))
    ny = int(round(ymax / ystep))
    for i in range(nx + 1):
        gx = x + w * i / nx
        c.line(gx, y - h, gx, y)
    for j in range(ny + 1):
        gy = y - h * j / ny
        c.line(x, gy, x + w, gy)
    c.setStrokeColor(P["RULE"])
    c.setLineWidth(0.5)
    c.rect(x, y - h, w, h, stroke=1, fill=0)
    for i in range(nx + 1):
        _t(P, c, x + w * i / nx, y - h - 3.4 * mm, xfmt % (i * xstep),
           4.6, P["LABEL2"], P["LBL"], "c")
    for j in range(ny + 1):
        v = j * ystep
        gy = (y - h * j / ny) if invert_y else (y - h + h * j / ny)
        _t(P, c, x - 1.4 * mm, gy - 1.2 * mm, yfmt % v, 4.6, P["LABEL2"],
           P["LBL"], "r")
    if xlab:
        _t(P, c, x + w, y - h - 7.2 * mm, xlab, 5.0, P["LABEL2"], P["LBL"], "r", 0.6)
    if ylab:
        _t(P, c, x, y + 2.2 * mm, ylab, 5.0, P["LABEL2"], P["LBL"], "l", 0.6)

    def to_px(vx, vy):
        px = x + w * vx / xmax
        py = (y - h * vy / ymax) if invert_y else (y - h + h * vy / ymax)
        return px, py
    return to_px


def polyline(c, P, pts, color=None, lw=1.2, dash=None):
    c.setStrokeColor(color or P["ACCENT"])
    c.setLineWidth(lw)
    if dash:
        c.setDash(*dash)
    p = c.beginPath()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    c.drawPath(p, stroke=1, fill=0)
    c.setDash()


def callout(c, P, x, y, text, size=5.0, color=None):
    return _t(P, c, x, y, text, size, color or P["LABEL"], P["LBLB"], "l", 0.3)


def caption(c, P, x, y, w, text, size=6.4, lead=9.0):
    """Подпись под схемой, с переносом."""
    words, line, yy = text.split(), "", y
    for word in words:
        test = (line + " " + word).strip()
        if c.stringWidth(test, P["BODY"], size) > w and line:
            P["txt"](c, x, yy, line, P["BODY"], size, P["LABEL"])
            yy -= lead
            line = word
        else:
            line = test
    if line:
        P["txt"](c, x, yy, line, P["BODY"], size, P["LABEL"])
        yy -= lead
    return y - yy


# ============================================================ ДАЙВИНГ
def fig_profile(c, P, x, y, w):
    h = 44 * mm
    to = axes(c, P, x + 7 * mm, y, w - 9 * mm, h, 40, 40, 10, 10,
              "ВРЕМЯ, МИН", "ГЛУБИНА, М", invert_y=True)
    pts = [(0, 0), (2, 30), (18, 30), (24, 20), (26, 5), (29, 5), (30, 0)]
    polyline(c, P, [to(a, b) for a, b in pts], P["ACCENT"], 1.4)
    px, py = to(29, 5)
    c.setFillColor(P["ACCENT"])
    c.circle(*to(27.5, 5), 0.9 * mm, stroke=0, fill=1)
    callout(c, P, *[v + z for v, z in zip(to(2.5, 26), (1.5 * mm, 0))],
            text="спуск")
    callout(c, P, *[v + z for v, z in zip(to(6, 30), (0, 1.8 * mm))],
            text="рабочая глубина 30 м")
    callout(c, P, *[v + z for v, z in zip(to(15, 14), (0, 0))],
            text="всплытие не быстрее 9 м/мин")
    callout(c, P, *[v + z for v, z in zip(to(26.5, 5), (1.5 * mm, 2.6 * mm))],
            text="остановка 3 мин на 5 м")
    return h + 9 * mm


def fig_pressure(c, P, x, y, w):
    h = 40 * mm
    n = 5
    cw = w / n
    top = y - 4 * mm
    c.setStrokeColor(P["RULE"])
    c.setLineWidth(0.6)
    c.line(x, y, x + w, y)
    _t(P, c, x, y + 1.6 * mm, "ПОВЕРХНОСТЬ", 4.8, P["LABEL2"], P["LBLB"])
    for i in range(n):
        depth = i * 10
        bar = i + 1
        cx = x + cw * (i + 0.5)
        cy = top - 14 * mm
        r = 6.2 * mm / math.sqrt(bar)
        c.setStrokeColor(P["ACCENT"])
        c.setFillColor(P["FAINT"])
        c.setLineWidth(0.7)
        c.circle(cx, cy, r, stroke=1, fill=1)
        _t(P, c, cx, top - 26 * mm, "%d м" % depth, 6.0, P["INK"], P["LBLB"], "c", 0.4)
        _t(P, c, cx, top - 30 * mm, "%d бар" % bar, 5.2, P["LABEL2"], P["LBL"], "c")
        _t(P, c, cx, top - 34 * mm, "объём 1/%d" % bar, 5.2, P["LABEL2"], P["LBL"], "c")
        c.setStrokeColor(P["GRID"])
        c.setLineWidth(0.3)
        if i:
            c.line(x + cw * i, top - 2 * mm, x + cw * i, top - 36 * mm)
    return h + 4 * mm


def fig_ascent(c, P, x, y, w, img=None):
    """Слева разрез толщи воды со шкалой глубин, справа сам дайвер с выносками.
    Иллюстрация узкая и высокая, поэтому ей отдана отдельная колонка."""
    h = 64 * mm
    gw = w * 0.60                      # ширина диаграммы
    gx = x
    surf = y - 7 * mm
    scale = (h - 16 * mm) / 20.0       # мм на метр глубины, шкала до 20 м

    def dy(m):
        return surf - scale * m

    c.setStrokeColor(P["RULE"])
    c.setLineWidth(0.8)
    c.line(gx, surf, gx + gw, surf)
    c.setStrokeColor(P["GRID"])
    c.setLineWidth(0.3)
    for k in range(1, 4):
        yy = surf - 2.0 * mm * k
        c.line(gx + 3 * mm * (k % 2), yy, gx + gw - 3 * mm * (k % 2), yy)
    # судно
    bx = gx + gw * 0.30
    c.setFillColor(P["GRID"])
    c.setStrokeColor(P["INK"])
    c.setLineWidth(0.7)
    p = c.beginPath()
    p.moveTo(bx - 12 * mm, surf)
    p.lineTo(bx + 12 * mm, surf)
    p.lineTo(bx + 7 * mm, surf + 4.2 * mm)
    p.lineTo(bx - 8 * mm, surf + 4.2 * mm)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    _t(P, c, bx, surf + 6.4 * mm, "СУДНО", 5.0, P["LABEL"], P["LBLB"], "c", 0.6)

    # шкала глубин
    for m in (5, 10, 15, 20):
        yy = dy(m)
        c.setStrokeColor(P["GRID"])
        c.setLineWidth(0.3)
        c.line(gx + 9 * mm, yy, gx + gw, yy)
        _t(P, c, gx + 7.5 * mm, yy - 1.3 * mm, "%d М" % m, 4.8, P["LABEL2"],
           P["LBLB"], "r", 0.4)

    # остановка безопасности
    sy = dy(5)
    c.setStrokeColor(P["INK"])
    c.setLineWidth(0.8)
    c.setDash(2.4, 1.8)
    c.line(gx + 9 * mm, sy, gx + gw, sy)
    c.setDash()
    _t(P, c, gx + 10 * mm, sy + 2.2 * mm, "ОСТАНОВКА 3 МИН", 5.2, P["INK"],
       P["LBLB"], "l", 0.5)

    # скорость подъёма
    ax = gx + gw * 0.72
    arrow(c, P, ax, dy(18), ax, dy(6.5), P["INK"], 0.9, 2.2 * mm)
    _t(P, c, ax - 2.4 * mm, (dy(18) + dy(6.5)) / 2, "9 М/МИН", 5.4, P["INK"],
       P["LBLB"], "r", 0.5)
    _t(P, c, gx + gw * 0.72, dy(19.4), "ПОДЪЁМ", 4.8, P["LABEL2"],
       P["LBLB"], "c", 0.5)

    # ---- правая колонка: дайвер
    cw = w - gw
    cx = x + gw + cw / 2
    dh = 0
    if img:
        dh = img(c, "d-03-ascent", x + gw, y - 2 * mm, cw, h - 10 * mm)
    top = y - 2 * mm
    c.setStrokeColor(P["LABEL2"])
    c.setLineWidth(0.5)
    arrow(c, P, cx - cw * 0.30, top - 6 * mm, cx - cw * 0.06, top - 3.5 * mm,
          P["LABEL2"], 0.5, 1.4 * mm)
    _t(P, c, cx - cw * 0.32, top - 7.6 * mm, "РУКА НАД ГОЛОВОЙ", 5.0, P["INK"],
       P["LBLB"], "r", 0.4)
    arrow(c, P, cx - cw * 0.30, top - dh * 0.55, cx - cw * 0.08, top - dh * 0.5,
          P["LABEL2"], 0.5, 1.4 * mm)
    _t(P, c, cx - cw * 0.32, top - dh * 0.55 - 1.2 * mm, "ВЗГЛЯД ВВЕРХ,",
       5.0, P["INK"], P["LBLB"], "r", 0.4)
    _t(P, c, cx - cw * 0.32, top - dh * 0.55 - 5 * mm, "ОБОРОТ 360°",
       5.0, P["INK"], P["LBLB"], "r", 0.4)
    return h


def fig_lost_buddy(c, P, x, y, w):
    h = 46 * mm
    step = w / 3
    titles = ["1 · ОСМОТР 360°", "2 · ВСПЛЫТИЕ ДО МИНУТЫ", "3 · БУЙ И ОЖИДАНИЕ"]
    for i, t in enumerate(titles):
        cx = x + step * (i + 0.5)
        _t(P, c, cx, y - 2 * mm, t, 5.0, P["ACCENT"], P["LBLB"], "c", 0.5)
        by = y - 24 * mm
        if i == 0:
            c.setStrokeColor(P["LABEL2"])
            c.setLineWidth(0.5)
            c.setDash(1.4, 1.4)
            c.circle(cx, by, 9 * mm, stroke=1, fill=0)
            c.setDash()
            for a in range(0, 360, 45):
                arrow(c, P, cx + 9 * mm * math.cos(math.radians(a)),
                      by + 9 * mm * math.sin(math.radians(a)),
                      cx + 11 * mm * math.cos(math.radians(a)),
                      by + 11 * mm * math.sin(math.radians(a)),
                      P["LABEL2"], 0.4, 1.2 * mm)
            c.setFillColor(P["ACCENT"])
            c.circle(cx, by, 1.6 * mm, stroke=0, fill=1)
        elif i == 1:
            c.setStrokeColor(P["RULE"])
            c.setLineWidth(0.6)
            c.line(cx - 12 * mm, by + 12 * mm, cx + 12 * mm, by + 12 * mm)
            arrow(c, P, cx, by - 8 * mm, cx, by + 10 * mm, P["ACCENT"], 1.0)
            _t(P, c, cx, by + 13.6 * mm, "ПОВЕРХНОСТЬ", 4.6, P["LABEL2"],
               P["LBLB"], "c", 0.5)
        else:
            c.setStrokeColor(P["RULE"])
            c.setLineWidth(0.6)
            c.line(cx - 12 * mm, by + 6 * mm, cx + 12 * mm, by + 6 * mm)
            c.setStrokeColor(P["ACCENT"])
            c.setFillColor(P["FAINT"])
            c.setLineWidth(0.8)
            c.rect(cx - 1.6 * mm, by + 6 * mm, 3.2 * mm, 13 * mm, stroke=1, fill=1)
            _t(P, c, cx, by + 1 * mm, "БУЙ", 4.8, P["LABEL2"], P["LBLB"], "c", 0.6)
    return h


def fig_ppo2(c, P, x, y, w):
    h = 44 * mm
    to = axes(c, P, x + 8 * mm, y, w - 10 * mm, h, 60, 2.0, 10, 0.5,
              "ГЛУБИНА, М", "ppO2, БАР", yfmt="%.1f")
    mixes = [("Воздух 21%", 0.21), ("EAN 32", 0.32), ("EAN 36", 0.36), ("EAN 40", 0.40)]
    for name, fo2 in mixes:
        pts = []
        for d in range(0, 61, 5):
            v = fo2 * (d / 10 + 1)
            if v <= 2.0:
                pts.append(to(d, v))
        polyline(c, P, pts, P["ACCENT"] if fo2 == 0.32 else P["LABEL2"],
                 1.3 if fo2 == 0.32 else 0.7)
        lx, ly = pts[-1]
        _t(P, c, lx - 1.2 * mm, ly + 1.6 * mm, name, 4.8,
           P["ACCENT"] if fo2 == 0.32 else P["LABEL2"], P["LBLB"], "r", 0.3)
    for lim, lab in [(1.4, "1,4 — ТИПОВОЙ РАБОЧИЙ ПРЕДЕЛ"), (1.6, "1,6 — ВЕРХНИЙ ПРЕДЕЛ*")]:
        px0, py0 = to(0, lim)
        px1, _ = to(60, lim)
        c.setStrokeColor(P["INK"])
        c.setLineWidth(0.5)
        c.setDash(2, 2)
        c.line(px0, py0, px1, py0)
        c.setDash()
        _t(P, c, px0 + 1.6 * mm, py0 + 1.4 * mm, lab, 4.6, P["INK"], P["LBLB"], "l", 0.4)
    return h + 9 * mm


def fig_sac(c, P, x, y, w):
    h = 33 * mm
    to = axes(c, P, x + 7 * mm, y, w - 9 * mm, h, 30, 30, 10, 10,
              "ВРЕМЯ, МИН", "ГЛУБИНА, М", invert_y=True)
    pts = [(0, 0), (2, 20), (22, 20), (26, 5), (29, 5), (30, 0)]
    polyline(c, P, [to(a, b) for a, b in pts], P["LABEL2"], 0.9)
    a0, a1 = to(2, 20), to(22, 20)
    c.setStrokeColor(P["ACCENT"])
    c.setLineWidth(1.8)
    c.line(a0[0], a0[1], a1[0], a1[1])
    callout(c, P, a0[0] + 1 * mm, a0[1] - 4 * mm,
            "ровный участок: 20 мин на 20 м, израсходовано 50 бар")
    return h + 9 * mm


# ============================================================ ЯХТИНГ
def fig_points_of_sail(c, P, x, y, w):
    h = 86 * mm
    cx, cy = x + w / 2, y - h / 2 - 1 * mm
    R = 29 * mm
    # мёртвый угол
    c.setFillColor(P["FAINT"])
    c.setStrokeColor(P["GRID"])
    c.setLineWidth(0.4)
    p = c.beginPath()
    p.moveTo(cx, cy)
    for a in range(45, 136, 5):
        p.lineTo(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a)))
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.setStrokeColor(P["GRID"])
    c.setLineWidth(0.4)
    c.circle(cx, cy, R, stroke=1, fill=0)

    arrow(c, P, cx, cy + R + 11 * mm, cx, cy + R + 2 * mm, P["INK"], 0.9, 2.2 * mm)
    _t(P, c, cx, cy + R + 12.6 * mm, "ВЕТЕР", 5.6, P["INK"], P["LBLB"], "c", 0.8)
    _t(P, c, cx, cy + R * 0.20, "МЁРТВЫЙ УГОЛ", 5.0, P["LABEL2"], P["LBLB"], "c", 0.5)
    _t(P, c, cx, cy + R * 0.20 - 4 * mm, "ИДТИ НЕЛЬЗЯ", 4.6, P["LABEL2"],
       P["LBL"], "c", 0.4)

    items = [(45, "БЕЙДЕВИНД", "close hauled", 1),
             (90, "ГАЛФВИНД", "beam reach", 1),
             (135, "БАКШТАГ", "broad reach", 1),
             (180, "ФОРДЕВИНД", "running", 1),
             (-45, "БЕЙДЕВИНД", "close hauled", -1),
             (-90, "ГАЛФВИНД", "beam reach", -1),
             (-135, "БАКШТАГ", "broad reach", -1)]
    for ang, ru, en, side in items:
        bxp = cx + (R * 0.62) * math.sin(math.radians(ang))
        byp = cy + (R * 0.62) * math.cos(math.radians(ang))
        boat(c, P, bxp, byp, ang, 11 * mm, sail=side)
        lx = cx + (R + 4 * mm) * math.sin(math.radians(ang))
        ly = cy + (R + 4 * mm) * math.cos(math.radians(ang))
        al = "l" if ang > 0 else ("r" if ang < 0 else "c")
        if ang == 180:
            ly -= 4 * mm
        _t(P, c, lx, ly, ru, 5.2, P["INK"], P["LBLB"], al, 0.5)
        _t(P, c, lx, ly - 3.6 * mm, en.upper(), 4.4, P["LABEL2"], P["LBL"], al, 0.4)
    return h


def _panel(c, P, x, y, w, h, title, sub=None):
    c.setStrokeColor(P["GRID"])
    c.setLineWidth(0.4)
    c.rect(x, y - h, w, h, stroke=1, fill=0)
    _t(P, c, x + w / 2, y - 4.4 * mm, title, 5.2, P["INK"], P["LBLB"], "c", 0.5)
    if sub:
        _t(P, c, x + w / 2, y - h + 2.2 * mm, sub, 4.6, P["LABEL2"], P["LBL"], "c", 0.3)


def fig_colregs_sail(c, P, x, y, w):
    h = 50 * mm
    pw = (w - 5 * mm) / 2
    # разные галсы
    _panel(c, P, x, y, pw, h, "РАЗНЫЕ ГАЛСЫ", "уступает тот, кто на левом галсе")
    cx = x + pw / 2
    cy = y - h / 2 - 1 * mm
    wind_band(c, P, x + 2 * mm, y - 8 * mm, pw - 4 * mm, "", 2)
    boat(c, P, cx - 9 * mm, cy - 5 * mm, 40, 13 * mm, sail=1)
    boat(c, P, cx + 9 * mm, cy - 5 * mm, -40, 13 * mm, sail=-1, fill=False)
    _t(P, c, cx - 9 * mm, cy - 15 * mm, "ЛЕВЫЙ ГАЛС", 4.4, P["ACCENT"], P["LBLB"], "c", 0.3)
    _t(P, c, cx - 9 * mm, cy - 18.4 * mm, "УСТУПАЕТ", 4.4, P["ACCENT"], P["LBLB"], "c", 0.3)
    _t(P, c, cx + 9 * mm, cy - 15 * mm, "ПРАВЫЙ ГАЛС", 4.4, P["LABEL2"],
       P["LBLB"], "c", 0.3)

    # один галс
    x2 = x + pw + 5 * mm
    _panel(c, P, x2, y, pw, h, "ОДИН ГАЛС", "уступает наветренное судно")
    cx2 = x2 + pw / 2
    wind_band(c, P, x2 + 2 * mm, y - 8 * mm, pw - 4 * mm, "", 2)
    boat(c, P, cx2 - 8 * mm, cy + 1 * mm, 35, 13 * mm, sail=1)
    boat(c, P, cx2 + 8 * mm, cy - 9 * mm, 35, 13 * mm, sail=1)
    _t(P, c, cx2 - 8 * mm, cy - 8 * mm, "НАВЕТРЕННОЕ", 4.4, P["ACCENT"], P["LBLB"], "c", 0.3)
    _t(P, c, cx2 - 8 * mm, cy - 11.4 * mm, "УСТУПАЕТ", 4.4, P["ACCENT"], P["LBLB"], "c", 0.3)
    _t(P, c, cx2 + 8 * mm, cy - 17 * mm, "ПОДВЕТРЕННОЕ", 4.4, P["LABEL2"],
       P["LBLB"], "c", 0.3)
    return h + 3 * mm


def fig_colregs_power(c, P, x, y, w):
    h = 46 * mm
    pw = (w - 6 * mm) / 3
    cy = y - h / 2 - 2 * mm

    _panel(c, P, x, y, pw, h, "КУРС НА КУРС", "оба вправо")
    cx = x + pw / 2
    boat(c, P, cx - 5 * mm, cy - 7 * mm, 0, 12 * mm)
    boat(c, P, cx + 5 * mm, cy + 7 * mm, 180, 12 * mm)
    arrow(c, P, cx - 5 * mm, cy + 1 * mm, cx - 1 * mm, cy + 7 * mm, P["ACCENT"], 0.7, 1.6 * mm)
    arrow(c, P, cx + 5 * mm, cy - 1 * mm, cx + 1 * mm, cy - 7 * mm, P["ACCENT"], 0.7, 1.6 * mm)

    x2 = x + pw + 3 * mm
    _panel(c, P, x2, y, pw, h, "ПЕРЕСЕЧЕНИЕ", "уступает тот, у кого судно справа")
    cx2 = x2 + pw / 2
    boat(c, P, cx2 - 8 * mm, cy - 4 * mm, 0, 12 * mm)
    boat(c, P, cx2 + 7 * mm, cy + 5 * mm, 270, 12 * mm)
    arrow(c, P, cx2 - 8 * mm, cy + 3 * mm, cx2 - 3 * mm, cy + 9 * mm, P["ACCENT"], 0.7, 1.6 * mm)
    _t(P, c, cx2 - 8 * mm, cy - 12.5 * mm, "УСТУПАЕТ", 4.4, P["ACCENT"], P["LBLB"], "c", 0.3)

    x3 = x2 + pw + 3 * mm
    _panel(c, P, x3, y, pw, h, "ОБГОН", "уступает обгоняющий")
    cx3 = x3 + pw / 2
    boat(c, P, cx3 + 3 * mm, cy + 7 * mm, 0, 12 * mm)
    boat(c, P, cx3 + 3 * mm, cy - 9 * mm, 0, 12 * mm)
    arrow(c, P, cx3 + 1 * mm, cy - 3 * mm, cx3 - 6 * mm, cy + 7 * mm,
          P["ACCENT"], 0.7, 1.6 * mm)
    _t(P, c, cx3 - 9 * mm, cy - 9 * mm, "УСТУПАЕТ", 4.4, P["ACCENT"], P["LBLB"], "r", 0.3)
    return h + 3 * mm


def fig_light_sectors(c, P, x, y, w):
    h = 62 * mm
    cx, cy = x + w / 2, y - h / 2 - 2 * mm
    R = 24 * mm

    def sector(start, extent, col, lw=2.6, dash=None):
        c.setStrokeColor(col)
        c.setLineWidth(lw)
        if dash:
            c.setDash(*dash)
        c.arc(cx - R, cy - R, cx + R, cy + R, start, extent)
        c.setDash()

    # нос вверх = 90°; arc отсчитывает от 3 часов против часовой
    sector(-22.5, 112.5, P["LABEL"])       # правый борт: от траверза до носа
    sector(90, 112.5, P["LABEL"], 2.6, (2.4, 1.8))   # левый борт
    sector(202.5, 135, P["INK"])           # кормовой

    c.setStrokeColor(P["GRID"])
    c.setLineWidth(0.4)
    c.circle(cx, cy, R, stroke=1, fill=0)
    for a in (90 - 112.5, 90 + 112.5, 180 + 22.5, 360 - 22.5):
        c.line(cx, cy, cx + R * math.cos(math.radians(a)),
               cy + R * math.sin(math.radians(a)))
    boat(c, P, cx, cy, 0, 20 * mm)

    _t(P, c, cx + R + 2 * mm, cy + 6 * mm, "ПРАВЫЙ БОРТ 112,5°", 4.8, P["LABEL"],
       P["LBLB"], "l", 0.3)
    _t(P, c, cx - R - 2 * mm, cy + 6 * mm, "ЛЕВЫЙ БОРТ 112,5°", 4.8, P["LABEL"],
       P["LBLB"], "r", 0.3)
    _t(P, c, cx - R - 2 * mm, cy + 2.4 * mm, "пунктиром", 4.4, P["LABEL2"],
       P["LBL"], "r", 0.2)
    _t(P, c, cx, cy - R - 5 * mm, "КОРМОВОЙ 135°", 4.8, P["INK"], P["LBLB"], "c", 0.3)
    _t(P, c, cx, cy + R + 4 * mm, "ТОПОВЫЙ 225° — ВПЕРЁД", 4.8, P["LABEL"],
       P["LBLB"], "c", 0.3)
    return h


def fig_light_stacks(c, P, x, y, w):
    """Вертикальные комбинации круговых огней."""
    groups = [("БЕЗ ХОДА", ["К", "К"]),
              ("ОГРАНИЧЕНО", ["К", "Б", "К"]),
              ("ТРАЛ", ["З", "Б"]),
              ("ПРОЧИЙ ЛОВ", ["К", "Б"]),
              ("ЛОЦМАН", ["Б", "К"]),
              ("НА ЯКОРЕ", ["Б"])]
    h = 40 * mm
    step = w / len(groups)
    for i, (name, lights) in enumerate(groups):
        cx = x + step * (i + 0.5)
        top = y - 6 * mm
        for j, code in enumerate(lights):
            cy = top - j * 6 * mm
            c.setLineWidth(0.7)
            c.setStrokeColor(P["INK"])
            c.setFillColor(P["FAINT"] if code == "Б" else P["GRID"])
            c.circle(cx, cy, 2.2 * mm, stroke=1, fill=1)
            _t(P, c, cx, cy - 1.2 * mm, code, 5.0, P["INK"], P["LBLB"], "c", 0)
        c.setStrokeColor(P["GRID"])
        c.setLineWidth(0.4)
        c.line(cx, top - len(lights) * 6 * mm + 3.4 * mm, cx, y - 30 * mm)
        for k, ln in enumerate(name.split("\n")):
            _t(P, c, cx, y - 33 * mm - k * 3.8 * mm, ln, 4.6, P["LABEL"],
               P["LBLB"], "c", 0.3)
    _t(P, c, x, y - h + 1 * mm, "К — КРАСНЫЙ · Б — БЕЛЫЙ · З — ЗЕЛЁНЫЙ, ВСЕ КРУГОВЫЕ",
       4.6, P["LABEL2"], P["LBL"], "l", 0.4)
    return h


def fig_buoys(c, P, x, y, w):
    h = 56 * mm
    items = [
        ("ЛЕВАЯ", "цилиндр", "cyl", [(0, 1)]),
        ("ПРАВАЯ", "конус", "cone", [(0, 1)]),
        ("СЕВЕРНЫЙ", "конусы вверх", "pillar", [("up", "up")]),
        ("ВОСТОЧНЫЙ", "основаниями", "pillar", [("down", "up")]),
        ("ЮЖНЫЙ", "конусы вниз", "pillar", [("down", "down")]),
        ("ЗАПАДНЫЙ", "вершинами", "pillar", [("up", "down")]),
    ]
    step = w / len(items)
    base = y - 34 * mm
    for i, (name, sub, shape, top) in enumerate(items):
        cx = x + step * (i + 0.5)
        c.setStrokeColor(P["INK"])
        c.setFillColor(P["FAINT"])
        c.setLineWidth(0.7)
        if shape == "cyl":
            c.rect(cx - 3 * mm, base, 6 * mm, 10 * mm, stroke=1, fill=1)
        elif shape == "cone":
            p = c.beginPath()
            p.moveTo(cx - 3.4 * mm, base)
            p.lineTo(cx + 3.4 * mm, base)
            p.lineTo(cx, base + 10 * mm)
            p.close()
            c.drawPath(p, stroke=1, fill=1)
        else:
            c.rect(cx - 2.2 * mm, base, 4.4 * mm, 10 * mm, stroke=1, fill=1)
            c.setFillColor(P["GRID"])
            c.rect(cx - 2.2 * mm, base + 3.4 * mm, 4.4 * mm, 3.4 * mm, stroke=1, fill=1)
        # топовые знаки
        ty = base + 11 * mm
        for k, d in enumerate(top[0] if shape == "pillar" else []):
            yy = ty + k * 4.4 * mm
            p = c.beginPath()
            if d == "up":
                p.moveTo(cx - 2 * mm, yy)
                p.lineTo(cx + 2 * mm, yy)
                p.lineTo(cx, yy + 3.6 * mm)
            else:
                p.moveTo(cx - 2 * mm, yy + 3.6 * mm)
                p.lineTo(cx + 2 * mm, yy + 3.6 * mm)
                p.lineTo(cx, yy)
            p.close()
            c.setFillColor(P["INK"])
            c.drawPath(p, stroke=1, fill=1)
        _t(P, c, cx, base - 4.4 * mm, name, 4.8, P["INK"], P["LBLB"], "c", 0.3)
        _t(P, c, cx, base - 8 * mm, sub, 4.4, P["LABEL2"], P["LBL"], "c", 0.2)
    c.setStrokeColor(P["RULE"])
    c.setLineWidth(0.5)
    c.line(x, base, x + w, base)
    return h


def fig_twelfths(c, P, x, y, w):
    h = 40 * mm
    parts = [1, 2, 3, 3, 2, 1]
    bw = w / 6
    base = y - h + 10 * mm
    maxh = 22 * mm
    cum = 0
    pts = [(x, base)]
    for i, v in enumerate(parts):
        bh = maxh * v / 3
        c.setStrokeColor(P["ACCENT"])
        c.setFillColor(P["FAINT"])
        c.setLineWidth(0.6)
        c.rect(x + bw * i + 1.2 * mm, base, bw - 2.4 * mm, bh, stroke=1, fill=1)
        _t(P, c, x + bw * (i + 0.5), base + bh + 1.6 * mm, "%d/12" % v, 5.2,
           P["INK"], P["LBLB"], "c", 0.3)
        _t(P, c, x + bw * (i + 0.5), base - 4 * mm, "%d-й час" % (i + 1), 4.6,
           P["LABEL2"], P["LBL"], "c")
        cum += v
        pts.append((x + bw * (i + 1), base + maxh * cum / 12 * (3 / 3)))
    c.setStrokeColor(P["RULE"])
    c.setLineWidth(0.6)
    c.line(x, base, x + w, base)
    _t(P, c, x, base - 9 * mm,
       "ЗА 6 ЧАСОВ УРОВЕНЬ ПРОХОДИТ ВЕСЬ ДИАПАЗОН ПРИЛИВА НЕРАВНОМЕРНО",
       4.8, P["LABEL2"], P["LBLB"], "l", 0.4)
    return h


def fig_mob(c, P, x, y, w):
    h = 58 * mm
    cy = y - h * 0.52
    wind_band(c, P, x, y - 2 * mm, w * 0.22, "ВЕТЕР", 2)

    # человек в воде
    mx, my = x + w * 0.66, cy + 6 * mm
    c.setFillColor(P["ACCENT"])
    c.setStrokeColor(P["ACCENT"])
    c.circle(mx, my, 1.7 * mm, stroke=0, fill=1)
    c.setLineWidth(0.5)
    c.setDash(1.2, 1.2)
    c.circle(mx, my, 6 * mm, stroke=1, fill=0)
    c.setDash()
    _t(P, c, mx, my + 8.4 * mm, "ЧЕЛОВЕК ЗА БОРТОМ", 4.8, P["ACCENT"],
       P["LBLB"], "c", 0.4)

    # момент падения
    b1x, b1y = x + w * 0.14, cy + 6 * mm
    boat(c, P, b1x, b1y, 90, 13 * mm, sail=1)
    _t(P, c, b1x, b1y - 10 * mm, "ПАДЕНИЕ", 4.6, P["LABEL2"], P["LBLB"], "c", 0.4)

    # петля возврата: отходим, разворачиваемся и заходим снизу, носом на ветер
    path = [(b1x + 8 * mm, b1y), (x + w * 0.42, cy + 2 * mm),
            (x + w * 0.60, cy - 10 * mm), (x + w * 0.72, cy - 20 * mm),
            (x + w * 0.66, cy - 26 * mm), (x + w * 0.60, cy - 22 * mm),
            (mx, cy - 12 * mm)]
    polyline(c, P, path, P["LABEL2"], 0.7, dash=(2, 2))

    # подход с подветра
    boat(c, P, mx, cy - 8 * mm, 0, 13 * mm, sail=None)
    arrow(c, P, mx, cy - 2 * mm, mx, my - 3 * mm, P["ACCENT"], 0.8, 1.8 * mm)
    _t(P, c, mx + 8 * mm, cy - 8 * mm, "ПОДХОД С ПОДВЕТРА,", 4.6, P["INK"],
       P["LBLB"], "l", 0.3)
    _t(P, c, mx + 8 * mm, cy - 11.6 * mm, "НОСОМ НА ВЕТЕР", 4.6, P["INK"],
       P["LBLB"], "l", 0.3)
    _t(P, c, x + w * 0.06, cy - 20 * mm, "ОТХОД И РАЗВОРОТ", 4.6, P["LABEL2"],
       P["LBLB"], "l", 0.3)
    return h


def fig_scope(c, P, x, y, w):
    h = 44 * mm
    surf = y - 6 * mm
    bed = surf - 24 * mm
    c.setStrokeColor(P["RULE"])
    c.setLineWidth(0.6)
    c.line(x, surf, x + w, surf)
    c.setStrokeColor(P["GRID"])
    c.setLineWidth(0.8)
    c.line(x, bed, x + w, bed)
    _t(P, c, x + w, surf + 1.6 * mm, "ПОВЕРХНОСТЬ", 4.8, P["LABEL2"], P["LBLB"], "r")
    _t(P, c, x + w, bed - 4 * mm, "ГРУНТ", 4.8, P["LABEL2"], P["LBLB"], "r")

    bx = x + w * 0.78
    boat(c, P, bx, surf + 1 * mm, 270, 15 * mm, sail=None)
    ax = x + w * 0.16
    polyline(c, P, [(bx - 6 * mm, surf), (x + w * 0.45, bed + 5 * mm),
                    (ax + 6 * mm, bed + 0.6 * mm), (ax, bed + 0.6 * mm)],
             P["ACCENT"], 1.0)
    c.setFillColor(P["ACCENT"])
    c.setStrokeColor(P["ACCENT"])
    c.setLineWidth(0.8)
    c.line(ax, bed + 3 * mm, ax, bed)
    c.line(ax - 2.6 * mm, bed + 1 * mm, ax + 2.6 * mm, bed + 1 * mm)

    c.setStrokeColor(P["LABEL2"])
    c.setLineWidth(0.4)
    c.setDash(1.6, 1.6)
    c.line(bx, surf, bx, bed)
    c.setDash()
    _t(P, c, bx + 1.6 * mm, (surf + bed) / 2, "ГЛУБИНА + ПРИЛИВ", 4.6, P["LABEL2"],
       P["LBLB"], "l", 0.3)
    arrow(c, P, ax, bed - 4 * mm, bx, bed - 4 * mm, P["LABEL2"], 0.5, 1.6 * mm)
    arrow(c, P, bx, bed - 4 * mm, ax, bed - 4 * mm, P["LABEL2"], 0.5, 1.6 * mm)
    _t(P, c, (ax + bx) / 2, bed - 8 * mm,
       "ТИПОВОЙ ОРИЕНТИР: ЦЕПЬ ≈ 4–5 × ПОЛНОЙ ГЛУБИНЫ", 5.0, P["INK"], P["LBLB"], "c", 0.4)
    return h


def _ball(c, P, cx, cy, r):
    c.setFillColor(P["INK"]); c.setStrokeColor(P["INK"]); c.setLineWidth(0.5)
    c.circle(cx, cy, r, stroke=1, fill=1)


def _diamond(c, P, cx, cy, r):
    p = c.beginPath()
    p.moveTo(cx, cy + r); p.lineTo(cx + r * 0.72, cy)
    p.lineTo(cx, cy - r); p.lineTo(cx - r * 0.72, cy); p.close()
    c.setFillColor(P["INK"]); c.setStrokeColor(P["INK"]); c.setLineWidth(0.5)
    c.drawPath(p, stroke=1, fill=1)


def _cone(c, P, cx, cy, r, up=True):
    p = c.beginPath()
    if up:
        p.moveTo(cx, cy + r); p.lineTo(cx + r * 0.8, cy - r); p.lineTo(cx - r * 0.8, cy - r)
    else:
        p.moveTo(cx, cy - r); p.lineTo(cx + r * 0.8, cy + r); p.lineTo(cx - r * 0.8, cy + r)
    p.close()
    c.setFillColor(P["INK"]); c.setStrokeColor(P["INK"]); c.setLineWidth(0.5)
    c.drawPath(p, stroke=1, fill=1)


def fig_day_shapes(c, P, x, y, w):
    """Дневные сигнальные знаки. Формы простые, поэтому рисуются вектором:
    перепутанный конус в печатном справочнике — навигационная ошибка."""
    items = [("ЯКОРЬ", "anchor", ["ball"]),
             ("НА МЕЛИ", "aground", ["ball", "ball", "ball"]),
             ("ПОД МОТОРОМ", "motor-sailing", ["cone_down"]),
             ("БЕЗ ХОДА", "not under command", ["ball", "ball"]),
             ("ОГРАНИЧЕНО", "restricted", ["ball", "diamond", "ball"]),
             ("ЛОВ РЫБЫ", "fishing", ["cone_up", "cone_down"]),
             ("БУКСИР > 200 М", "towing", ["diamond"])]
    h = 54 * mm
    step = w / len(items)
    r = 3.0 * mm
    base = y - 8 * mm
    for i, (ru, en, shapes) in enumerate(items):
        cx = x + step * (i + 0.5)
        c.setStrokeColor(P["GRID"]); c.setLineWidth(0.4)
        c.line(cx, base - 26 * mm, cx, base + 2 * mm)
        for k, sh in enumerate(shapes):
            cy = base - k * 8 * mm
            if sh == "ball":
                _ball(c, P, cx, cy, r)
            elif sh == "diamond":
                _diamond(c, P, cx, cy, r * 1.15)
            elif sh == "cone_up":
                _cone(c, P, cx, cy, r, up=True)
            else:
                _cone(c, P, cx, cy, r, up=False)
        _t(P, c, cx, base - 30 * mm, ru, 4.8, P["INK"], P["LBLB"], "c", 0.3)
        _t(P, c, cx, base - 33.6 * mm, en.upper(), 4.2, P["LABEL2"], P["LBL"], "c", 0.2)
    _t(P, c, x, base - 42 * mm,
       "ЗНАКИ ЧЁРНЫЕ, НЕСУТСЯ ТАМ, ГДЕ ИХ ЛУЧШЕ ВИДНО. ЛОВ РЫБЫ — КОНУСЫ ВЕРШИНАМИ ВМЕСТЕ",
       4.6, P["LABEL2"], P["LBLB"], "l", 0.3)
    return h


def fig_blasts(c, P, x, y, w, pattern, label_ru, label_en):
    """Один ряд звуковых сигналов: короткий — квадрат, продолжительный — полоса."""
    bx = x
    hgt = 2.6 * mm
    for kind in pattern:
        ln = 2.6 * mm if kind == "s" else 8.0 * mm
        c.setFillColor(P["INK"]); c.setStrokeColor(P["INK"]); c.setLineWidth(0.4)
        c.rect(bx, y, ln, hgt, stroke=1, fill=1)
        bx += ln + 1.8 * mm
    lx = x + 34 * mm
    avail = x + w - lx
    ru, en = label_ru.upper(), "/ " + label_en.upper()
    sz = 5.4
    while sz > 4.0:
        need = (c.stringWidth(ru, P["LBLB"], sz) + 0.3 * len(ru) + 1.6 * mm
                + c.stringWidth(en, P["LBL"], sz * 0.85) + 0.2 * len(en))
        if need <= avail:
            break
        sz -= 0.1
    tw = _t(P, c, lx, y + 0.4 * mm, ru, sz, P["INK"], P["LBLB"], "l", 0.3)
    _t(P, c, lx + tw + 1.6 * mm, y + 0.4 * mm, en, sz * 0.85, P["LABEL2"], P["LBL"], "l", 0.2)
    return 6.6 * mm
