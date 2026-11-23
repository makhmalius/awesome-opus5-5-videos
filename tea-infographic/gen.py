# -*- coding: utf-8 -*-
"""A3 tea infographic generator. Units: 0.1 mm (viewBox 2970 x 4200)."""
import json, base64, os, sys, math

S = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(S)
MAPS = json.load(open(os.path.join(ROOT, 'geo', 'maps.json')))
FONTDIR = os.path.join(ROOT, 'font', 'package', 'fonts', 'webfonts')
EMBED = '--no-embed' not in sys.argv

# ---------- palette ----------
BG = "#F5EEDF"; CARD = "#FBF7EE"; CREAM2 = "#EADDC3"; LINE = "#D8C8AA"
INK = "#2A2019"; MUTED = "#7A6A58"
G1 = "#2E5B3A"; G2 = "#5E8B4C"; G3 = "#A9C38E"; G4 = "#DDE7CD"
C1 = "#8E4722"; C2 = "#C0763A"; C3 = "#E4BB90"; C4 = "#F1DEC6"
BR = "#4E2C1A"
EA, EU, IR = G1, C2, BR          # track colours
STROKE = 4.2                      # icon stroke (0.42 mm)

FA = str.maketrans("0123456789.", "۰۱۲۳۴۵۶۷۸۹٫")
def fa(s):
    """Persian digits; '.' between digits -> Persian decimal sign."""
    out = []
    s = str(s)
    for i, ch in enumerate(s):
        if ch.isdigit():
            out.append(ch.translate(FA))
        elif ch == '.' and 0 < i < len(s) - 1 and s[i-1].isdigit() and s[i+1].isdigit():
            out.append('٫')
        else:
            out.append(ch)
    return ''.join(out)

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

O = []
def add(s): O.append(s)

HALO = [None]
def T(x, y, s, size=22, w=400, fill=INK, a='r', extra='', latin=False, halo=None):
    anchor = {'r': 'start', 'l': 'end', 'm': 'middle'}[a]
    txt = s if latin else fa(s)
    hc = HALO[0] if halo is None else (halo if isinstance(halo, str) else None)
    if hc:
        extra += f' stroke="{hc}" stroke-width="6" stroke-linejoin="round" paint-order="stroke"'
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}" {extra}>{esc(txt)}</text>')

def R(x, y, w, h, fill='none', stroke='none', sw=0, rx=0, extra=''):
    add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

def L(x1, y1, x2, y2, stroke=INK, sw=2, extra=''):
    add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

def C(x, y, r, fill='none', stroke='none', sw=0, extra=''):
    add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

# ---------- icon set (24-unit grid, line style) ----------
ICONS = {
 'leaf': ['M5 19c0-8.5 6-14 14.5-14.5C19 13 13.5 19 5 19z', 'M5 19l8.5-8.5'],
 'village': ['M2.5 12l5.5-4.5 5.5 4.5v8h-11z', 'M6.5 20v-4h3v4', 'M13.5 12.5l4-3.5 4 3.5v7.5h-8'],
 'family': ['C8 7.5 2.6', 'C16.5 8.5 2.2', 'M3 20.5v-2a5 5 0 0 1 10 0v2', 'M12.5 20.5v-1.5a4 4 0 0 1 8 0v1.5'],
 'worker': ['C12 10.5 3', 'M7.5 8.5a4.5 4.5 0 0 1 9 0', 'M6 8.5h12', 'M5 21a7 6 0 0 1 14 0'],
 'factory': ['M3 20.5V10l5 3v-3l5 3v-3l5 3V4h3v16.5z', 'M2 20.5h20', 'M7 17h2', 'M12 17h2'],
 'book': ['M3.5 5.5C6 4.5 9 4.6 12 6.2c3-1.6 6-1.7 8.5-.7v13c-2.5-1-5.5-.9-8.5.7-3-1.6-6-1.7-8.5-.7z', 'M12 6.2v13'],
 'cloud': ['M7 18.5a4 4 0 0 1-.6-7.9A5.6 5.6 0 0 1 17.2 9.4a4.6 4.6 0 0 1 .3 9.1z'],
 'ship': ['M3 15.5h18l-3.2 4.5H6.2z', 'M12 3.5v12', 'M12 5l6 8h-6', 'M12 7.5l-5 5.5h5'],
 'estekan': ['M8 4h8l-.9 4.5c-.5 2.3.7 4 .9 6.2.2 2-.4 3.8-1.4 5.3H9.4C8.4 18.5 7.8 16.7 8 14.7c.2-2.2 1.4-3.9.9-6.2z', 'M4.5 21h15'],
 'pagoda': ['M3.5 9.5C7 9.5 10 7.5 12 4c2 3.5 5 5.5 8.5 5.5', 'M6.5 9.5v3.5', 'M17.5 9.5v3.5', 'M4.5 15.5C8 15.5 10 14 12 12.5c2 1.5 4 3 7.5 3', 'M7 15.5V20.5h10V15.5', 'M11 20.5v-3h2v3'],
 'cup': ['M4 9h12v4a5 5 0 0 1-5 5h-2a5 5 0 0 1-5-5z', 'M16 10h1.5a2.5 2.5 0 0 1 0 5H15.6', 'M2.5 20.5h16', 'M8 3.5c0 1.2 1 1.3 1 2.5', 'M12 3.5c0 1.2 1 1.3 1 2.5'],
 'samovar': ['M9.5 2.5h5', 'M12 2.5v2', 'M7 4.5h10l1 9.5H6z', 'M6 14c0 2 2.5 3 6 3s6-1 6-3', 'M18 8.5h2.5v3.5', 'M10 17l-1.2 3.5h6.4L14 17', 'M7.5 20.5h9'],
 'gaiwan': ['M4 11h16c0 4.2-3.5 7.5-8 7.5S4 15.2 4 11z', 'M6.5 11c0-2.6 2.5-4.2 5.5-4.2s5.5 1.6 5.5 4.2', 'M12 4.5v2.3', 'M7.5 21h9'],
 'matcha': ['M2.5 11.5h14c0 4.2-3 7.5-7 7.5s-7-3.3-7-7.5z', 'M5 21h9', 'M20 3v6.5', 'M18.3 9.5h3.4l-.6 4.5h-2.2z'],
 'mint': ['M7 8.5h7l1 9.5H6z', 'M8.5 8.5c0-2 1-3.2 2-3.2s2 1.2 2 3.2', 'M10.5 3.5v1.8', 'M6.5 11.5c-2 0-3.3-1.2-4-3', 'M15 11c2 .3 3 1.8 3 3.5', 'M5 21h11', 'M17 7.5c0-2.6 1.8-4.3 4.5-4.3 0 2.6-1.8 4.3-4.5 4.3z', 'M17 7.5l2.3-2.3'],
 'kulhad': ['M5.5 9h13l-1.8 11.5H7.3z', 'M9 3c0 1.3 1.2 1.6 1.2 3', 'M13.5 3c0 1.3 1.2 1.6 1.2 3', 'M7 13.5h10'],
 'irancup': ['M9 6h6l-.7 3.5c-.4 1.8.5 3.1.7 4.8.2 1.5-.3 3-1.1 4.2h-3.8c-.8-1.2-1.3-2.7-1.1-4.2.2-1.7 1.1-3 .7-4.8z', 'M5 20.5h14', 'M11 2.2c0 1 .8 1.2.8 2.2', 'M13.5 2.2c0 1 .8 1.2.8 2.2', 'M18.5 14.5a1.6 1.6 0 1 0 0 .1'],
 'magnifier': ['C10.5 10.5 6.5', 'M15.3 15.3l5.5 5.5', 'M7.5 10.5h6', 'M10.5 7.5v6'],
 'wither': ['M10 6.5c2.6 3.7 4 5.8 4 7.8a4 4 0 0 1-8 0c0-2 1.4-4.1 4-7.8z', 'M18.5 4v8', 'M16 9.8l2.5 2.5 2.5-2.5'],
 'roll': ['M12 12.5a1.2 1.2 0 1 1 1.2-1.2 3 3 0 1 1-3-3 5 5 0 1 1-5 5 7 7 0 1 1 7 7'],
 'oxid': ['C8.5 14.5 4.2', 'C16.5 8 3', 'C17.5 17 2.2', 'M7 14.5h3'],
 'flame': ['M12 2.8c.6 3.4 5.2 5.4 5.2 10.4a5.2 5.2 0 0 1-10.4 0c0-2.6 1.6-3.8 2-6 1 1 1.4 2 1.5 3.2 1.3-2.2 1.9-4.5 1.7-7.6z'],
 'sun': ['C12 12 4', 'M12 2.5v2.5', 'M12 19v2.5', 'M2.5 12H5', 'M19 12h2.5', 'M5.3 5.3l1.8 1.8', 'M16.9 16.9l1.8 1.8', 'M5.3 18.7l1.8-1.8', 'M16.9 7.1l1.8-1.8'],
 'box': ['M3 7.8l9-4 9 4v9l-9 4-9-4z', 'M3 7.8l9 4 9-4', 'M12 11.8v9', 'M7.5 5.8l9 4'],
 'bolt': ['M13.5 2.5L5 14h6.5l-1 7.5L19 10h-6.5z'],
 'hexring': ['M12 2.8l8 4.6v9.2l-8 4.6-8-4.6V7.4z', 'C12 12 4.3'],
 'hexleaf': ['M10 4l6 3.5v7L10 18l-6-3.5v-7z', 'M15 20.5c0-4 2.5-6.5 6.5-6.5 0 4-2.5 6.5-6.5 6.5z', 'M15 20.5l3.5-3.5'],
 'chain': ['C4.5 12 2.2', 'C12 12 2.2', 'C19.5 12 2.2', 'M6.7 12h3.1', 'M14.2 12h3.1', 'M12 9.8V5', 'M12 5h3.5'],
 'purine': ['M10 5l5 2.9v5.8L10 16.6 5 13.7V7.9z', 'M15 7.9l4.3-1.6 2.2 4-3 3.1-3.5.3', 'M10 16.6v4'],
 'aroma': ['M7 21c-2.2-3 2.2-5 0-8.5s2.2-5.5 0-9', 'M12 21c-2.2-3 2.2-5 0-8.5s2.2-5.5 0-9', 'M17 21c-2.2-3 2.2-5 0-8.5s2.2-5.5 0-9'],
 'pin': ['M12 21.5s-6.5-6.8-6.5-11.5a6.5 6.5 0 0 1 13 0c0 4.7-6.5 11.5-6.5 11.5z', 'C12 10 2.3'],
 'warn': ['M12 3l10 18H2z', 'M12 10v5', 'M12 18.2v.3'],
 'mountain': ['M2 20l7-11 4 5.5 3-3.5 6 9z'],
 'plain': ['M2 18.5h20', 'M2 14.5c3.3-1.6 6.7-1.6 10 0s6.7 1.6 10 0', 'M6 10.5c2-1 4-1 6 0'],
 'herb': ['M12 21V9', 'M12 13c-3.5 0-6-2.5-6-6 3.5 0 6 2.5 6 6z', 'M12 11c3 0 5.5-2.2 5.5-5.5-3 0-5.5 2.2-5.5 5.5z', 'M7 21h10'],
 'globe': ['C12 12 9', 'M3 12h18', 'M12 3c2.7 2.6 4 5.6 4 9s-1.3 6.4-4 9c-2.7-2.6-4-5.6-4-9s1.3-6.4 4-9z'],
}

def icon(name, x, y, size, color, sw=STROKE, fill_bg=None):
    """Draw icon with top-left at (x,y). Visual stroke stays sw regardless of size."""
    k = size / 24.0
    parts = [f'<g transform="translate({x:.1f},{y:.1f}) scale({k:.4f})" fill="none" stroke="{color}" stroke-width="{sw/k:.3f}" stroke-linecap="round" stroke-linejoin="round">']
    for p in ICONS[name]:
        if p.startswith('C '):
            cx, cy, r = p[2:].split()
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}"/>')
        else:
            parts.append(f'<path d="{p}"/>')
    parts.append('</g>')
    add(''.join(parts))

def badge(name, cx, cy, r, color, ring=None, bg=CARD):
    C(cx, cy, r, fill=bg, stroke=ring or color, sw=3)
    s = r * 1.15
    icon(name, cx - s/2, cy - s/2, s, color)

def section_title(x_right, y, num, title, sub=None, color=G1):
    # number chip + title, right aligned
    C(x_right - 30, y - 14, 30, fill=color)
    T(x_right - 30, y - 3, num, 34, 800, CARD, 'm')
    T(x_right - 76, y, title, 46, 800, INK, 'r')
    if sub:
        T(x_right - 76, y + 40, sub, 23, 400, MUTED, 'r')

# =====================================================================
W, H = 2970, 4200
M = 60                                  # outer margin
add(f'<rect width="{W}" height="{H}" fill="{BG}"/>')

# ---------------- HEADER ----------------
R(0, 0, W, 300, fill=G1)
# decorative leaf pattern (subtle)
for i, (lx, ly, ls) in enumerate([(70, 40, 220), (250, 150, 120), (330, 30, 90)]):
    icon('leaf', lx, ly, ls, "#3F7049", sw=6)
T(W - M, 78, 'دی‌کودینگ بصری · گرافیک خبری', 28, 500, G3, 'r')
T(W - M, 190, 'چای؛ از افسانه تا استکان', 112, 900, CARD, 'r')
T(W - M, 255, 'تاریخ، تجارت، صنعت و فرهنگ چای در یک نگاه — همه اعداد از سند «تاریخچه چای»', 30, 400, G4, 'r')
# legend box in header (left)
lx0 = 560; ly0 = 52
R(lx0, ly0, 1000, 210, fill="#264D31", rx=14)
T(lx0 + 975, ly0 + 42, 'راهنمای خط زمانی', 24, 700, G3, 'r')
leg = [('pagoda', EA, '#9CC59A', 'چین / آسیای شرقی'), ('ship', EU, C3, 'اروپا / غرب'), ('irancup', IR, C4, 'ایران')]
for i, (ic, col, lc, lab) in enumerate(leg):
    yy = ly0 + 70 + i * 46
    C(lx0 + 955, yy + 14, 17, fill=CARD)
    icon(ic, lx0 + 942, yy + 1, 26, col if col != IR else BR)
    T(lx0 + 925, yy + 23, lab, 24, 500, CARD, 'r')
# symbols legend
sx = lx0 + 560
C(sx, ly0 + 84, 11, fill=CARD, stroke=CARD, sw=3)
T(sx - 24, ly0 + 92, 'رویداد نقطه‌ای', 22, 400, CARD, 'r')
R(sx - 14, ly0 + 120, 28, 16, fill=G3)
T(sx - 24, ly0 + 136, 'دوره / بازه زمانی', 22, 400, CARD, 'r')
C(sx, ly0 + 172, 11, fill='none', stroke=CARD, sw=3, extra='stroke-dasharray="5 4"')
T(sx - 24, ly0 + 180, 'افسانه، بدون سند قطعی', 22, 400, CARD, 'r')

# =====================================================================
# 1. TIMELINE
# =====================================================================
TOP = 340
section_title(W - M, TOP + 20, '۱', 'خط زمانی چای', None, G1)
T(W - M - 380, TOP + 20, '— محور با مقیاس واقعی: فاصله رویدادها متناسب با اختلاف سال‌هاست', 25, 400, MUTED, 'r')

XR, XL = 2860, 160          # right = oldest, left = newest
def astro(y):               # BCE as negative input -> astronomical year
    return y + 1 if y < 0 else y
Y0, Y1 = astro(-2737), 1960
K = (XR - XL) / (Y1 - Y0)
def X(y): return XR - (astro(y) - Y0) * K

AX = 560     # main axis y
ZT, ZB = 800, 1560
ZXR, ZXL = 2740, 160
ZK = (ZXR - ZXL) / (1960 - 1600)
def ZX(y): return ZXR - (y - 1600) * ZK
ratio = ZK / K
zx0, zx1 = X(1960), X(1600)
# light beam (drawn first, behind everything)
add(f'<path d="M{zx0:.1f},{AX+20} L{zx1:.1f},{AX+20} L{ZXR+20},{ZT} L{ZXL-20},{ZT} Z" fill="{C4}" opacity="0.5"/>')
add(f'<path d="M{zx1:.1f},{AX+20} L{ZXR+20},{ZT} M{zx0:.1f},{AX+20} L{ZXL-20},{ZT}" stroke="{C3}" stroke-width="2" fill="none" stroke-dasharray="8 5"/>')
# zoom highlight on main axis
R(zx0, AX - 150, zx1 - zx0, 170, fill=C4, stroke=C2, sw=2.5, rx=6, extra='stroke-dasharray="8 5"')
T((zx0 + zx1) / 2, AX - 160, 'بزرگ‌نمایی در پایین', 21, 600, C1, 'm')
icon('magnifier', (zx0 + zx1) / 2 - 22, AX - 132, 44, C1)

HALO[0] = BG
L(XL, AX, XR, AX, INK, 4)
for yv in [-2500, -2000, -1500, -1000, -500, 500, 1000, 1500]:
    x = X(yv)
    L(x, AX - 10, x, AX + 10, INK, 2.5)
    lab = f'{abs(yv)} ق.م' if yv < 0 else f'{yv} م'
    T(x, AX + 38, lab, 21, 500, MUTED, 'm')
x = X(1)
L(x, AX - 14, x, AX + 14, INK, 3.5)
T(x, AX + 38, '۱ م', 21, 700, INK, 'm')
T(XR, AX + 38, '۲۷۳۷ ق.م', 21, 700, INK, 'm')
sb = 100 * K
T(XR - 290, AX + 92, 'مقیاس: هر ۱۰۰ سال =', 20, 400, MUTED, 'r')
L(XR - 520, AX + 86, XR - 520 + sb, AX + 86, INK, 4)
L(XR - 520, AX + 78, XR - 520, AX + 94, INK, 2); L(XR - 520 + sb, AX + 78, XR - 520 + sb, AX + 94, INK, 2)

DY = AX + 108
dyn = [('هان', -206, 220, '۲۰۶ ق.م – ۲۲۰ م'), ('تانگ', 618, 907, '۶۱۸–۹۰۷ م'),
       ('سونگ', 960, 1279, '۹۶۰–۱۲۷۹ م'), ('مینگ', 1368, 1644, '۱۳۶۸–۱۶۴۴ م')]
T(XR, DY + 22, 'دوره‌های حکومتی چین', 21, 700, EA, 'r')
for name, a, b, lab in dyn:
    xa, xb = X(a), X(b)
    R(xb, DY, xa - xb, 30, fill=G2, rx=4)
    T((xa + xb) / 2, DY + 23, name, 21, 700, CARD, 'm', halo=False)
    T((xa + xb) / 2, DY + 58, lab, 19, 500, EA, 'm')
EY = DY + 82
xa, xb = X(1501), X(1600)
R(xb, EY, xa - xb, 16, fill=EU, rx=3)
L((xa + xb) / 2, AX + 4, (xa + xb) / 2, EY, EU, 2, 'stroke-dasharray="4 3"')
T(xa + 10, EY + 15, 'قرن ۱۶ م · آشنایی اروپاییان با چای', 21, 600, C1, 'l')

def event(x, level_y, year, title, col, side='l', extra_line=None, dashed=False, r=11, axis=AX, ysize=24, down=False):
    """circle on axis + stem to label; side='l' label extends left, 'r' extends right."""
    da = 'stroke-dasharray="5 4"' if dashed else ''
    if down:
        L(x, axis, x, level_y - 18, col, 2.2, da)
    else:
        L(x, axis, x, level_y - 22, col, 2.2, da)
    if dashed:
        C(x, axis, r, fill=BG, stroke=col, sw=3, extra=da)
    elif r > 1:
        C(x, axis, r, fill=col, stroke=CARD, sw=3)
    tx = x - 10 if side == 'l' else x + 10
    a = 'r' if side == 'l' else 'l'
    T(tx, level_y, year, ysize, 800, col, a)
    T(tx, level_y + 27, title, 21, 500, INK, a)
    if extra_line:
        T(tx, level_y + 53, extra_line, 19, 400, MUTED, a)

LA, LB = AX - 140, AX - 72
event(XR, LA - 10, '۲۷۳۷ ق.م', 'افسانه شن‌نونگ', MUTED, 'l', 'تاریخ افسانه‌ای؛ سند تاریخی قطعی ندارد', dashed=True, r=12)
icon('cloud', XR - 190, LA - 52, 40, MUTED)
xj0, xj1 = X(801), X(850)
R(xj1, AX - 8, xj0 - xj1, 16, fill=EA, rx=3, extra='opacity="0.55"')
event((xj0 + xj1) / 2, LA, 'اوایل قرن ۹ م', 'ورود چای به ژاپن', EA, 'r', r=0.1)
event(X(760), LB, 'حدود ۷۶۰ م', 'چا جینگ (لو یو)', EA, 'r')
event(X(1211), LA, '۱۲۱۱ م', 'کتاب Kissa Yojoki (ایسای)', EA, 'l')
for yv, col in [(1606, EU), (1652, EU), (1658, EU), (1664, EU), (1773, EU), (1850, IR), (1884, IR), (1902, IR), (1932, IR), (1958, IR)]:
    C(X(yv), AX, 5, fill=col)

# ---------------- ZOOM PANEL ----------------
R(ZXL - 20, ZT, ZXR - ZXL + 40, ZB - ZT, fill=CARD, stroke=C2, sw=3, rx=12)
R(ZXR + 40, ZT, W - M - ZXR - 40, ZB - ZT, fill=CREAM2, rx=12)
HALO[0] = CARD
icon('magnifier', ZXR - 50, ZT + 18, 44, C1)
T(ZXR - 64, ZT + 52, 'ذره‌بین: ۱۶۰۰ تا ۱۹۶۰ میلادی', 34, 800, C1, 'r')
T(ZXR - 560, ZT + 52, f'مقیاس جداگانه، حدود {round(ratio)} برابر محور اصلی', 24, 500, MUTED, 'r')

ZA = ZB - 90
EAa = ZT + 98
EUa = ZT + 318
IRa = ZT + 518
lanes = [('pagoda', EA, 'آسیای شرقی', ZT + 72, ZT + 124), ('ship', EU, 'اروپا / غرب', ZT + 124, ZT + 338), ('irancup', IR, 'ایران', ZT + 338, ZA - 6)]
for i, (ic, col, lab, y0, y1) in enumerate(lanes):
    if i < 2:
        L(ZXL - 20, y1, W - M, y1, LINE, 1.5, 'stroke-dasharray="3 5"')
    cy_ = (y0 + y1) / 2
    icon(ic, (ZXR + W - M) / 2 + 20 - 17, cy_ - 34, 34, col)
    T((ZXR + W - M) / 2 + 20, cy_ + 28, lab, 20, 800, col, 'm', halo=False)

L(ZXL, ZA, ZXR, ZA, INK, 4)
for yv in range(1600, 1961, 10):
    x = ZX(yv)
    big = yv % 50 == 0
    L(x, ZA - (10 if big else 5), x, ZA + (10 if big else 5), INK, 2.5 if big else 1.5)
    if big:
        T(x, ZA + 38, f'{yv}', 22, 600, MUTED, 'm')
def brk(x, y, col=C1):
    R(x - 10, y - 6, 20, 12, fill=CARD)
    add(f'<path d="M{x-12},{y+16} L{x-2},{y-16} M{x+4},{y+16} L{x+14},{y-16}" stroke="{col}" stroke-width="4" fill="none"/>')
brk(ZXR + 2, ZA)
brk(ZXL - 4, ZA)
sb2 = 50 * ZK
T(ZXR - 20, ZA + 74, 'مقیاس ذره‌بین: هر ۵۰ سال =', 20, 400, MUTED, 'r')
L(ZXR - 290 - sb2, ZA + 68, ZXR - 290, ZA + 68, INK, 4)
L(ZXR - 290 - sb2, ZA + 60, ZXR - 290 - sb2, ZA + 76, INK, 2); L(ZXR - 290, ZA + 60, ZXR - 290, ZA + 76, INK, 2)
T(ZXL + 10, ZA + 74, '⫽ علامت شکست مقیاس: این بخش مقیاسی متفاوت با محور اصلی دارد', 20, 500, C1, 'l')

def guide(x, y_from):
    L(x, y_from, x, ZA, MUTED, 1.2, 'stroke-dasharray="2 5" opacity="0.55"')

# East Asia lane : Ming
xa, xb = ZX(1600), ZX(1644)
guide(xb, EAa + 13)
R(xb, EAa - 13, xa - xb, 26, fill=G2, rx=4)
T((xa + xb) / 2, EAa + 7, 'مینگ', 20, 700, CARD, 'm', halo=False)
T(xb - 12, EAa + 8, '← ادامه دوره مینگ (۱۳۶۸–۱۶۴۴ م)', 20, 500, EA, 'r')

# Europe lane
for y in (1606, 1652, 1658, 1664, 1773):
    guide(ZX(y), EUa + 11)
event(ZX(1606), ZT + 165, 'حدود ۱۶۰۶', 'تجارت دریایی هلندی‌ها (VOC)', EU, 'l', axis=EUa)
event(ZX(1652), ZT + 165, '۱۶۵۲', 'یکی از نخستین چایخانه‌های لندن', EU, 'l', axis=EUa)
event(ZX(1658), ZT + 220, '۱۶۵۸', 'نخستین مطلب روزنامه لندن درباره چای', EU, 'l', axis=EUa)
event(ZX(1664), ZT + 275, '۱۶۶۴', 'واردات گسترده چای به انگلستان', EU, 'l', axis=EUa)
event(ZX(1773), ZT + 165, '۱۶ دسامبر ۱۷۷۳', 'مهمانی چای بوستون', EU, 'l', axis=EUa)
xa, xb = ZX(1801), ZX(1900)
guide(xa, EUa + 10); guide(xb, EUa + 10)
R(xb, EUa - 10, xa - xb, 20, fill=C3, rx=4)
L(xa, EUa - 14, xa, EUa + 14, C1, 2.5); L(xb, EUa - 14, xb, EUa + 14, C1, 2.5)
T(xa - 12, EUa - 60, 'قرن ۱۹ م', 24, 800, C1, 'r')
T(xa - 12, EUa - 33, 'توسعه گسترده مزارع چای در هند و سیلان — کشت استعماری', 21, 500, INK, 'r')

# Iran lane
for y in (1850, 1884, 1902, 1932, 1958):
    guide(ZX(y), IRa + 11)
event(ZX(1850), IRa - 62, '۱۸۵۰', 'هدیه سماور نقره‌ای به امیرکبیر', IR, 'l', axis=IRa)
event(ZX(1902), IRa - 88, '۱۹۰۲', 'کشت آزمایشی کاشف‌السلطنه (نزدیک لاهیجان)', IR, 'l', 'ورود به تهران: ۱۰ آبان ۱۲۷۹ ش (برخی منابع)', axis=IRa)
event(ZX(1958), IRa - 158, '۱۹۵۸ | ۱۳۳۷ ش', 'تأسیس سازمان چای', IR, 'r', axis=IRa)
# 1884-1885 small range, label below
x84, x85 = ZX(1884), ZX(1885)
xm = (x84 + x85) / 2
R(x85, IRa - 10, x84 - x85, 20, fill=IR)
L(xm, IRa + 10, xm, IRa + 34, IR, 2.2)
T(xm - 10, IRa + 54, '۱۸۸۴–۱۸۸۵ | ۱۲۶۱ یا ۱۲۶۲ ش', 23, 800, IR, 'r')
T(xm - 10, IRa + 81, 'تلاش حاج محمدحسین اصفهانی', 21, 500, INK, 'r')
# 1932 first factory (label below, extends right)
x32 = ZX(1932)
C(x32, IRa, 11, fill=IR, stroke=CARD, sw=3)
L(x32, IRa + 10, x32, IRa + 96, IR, 2.2)
T(x32 + 10, IRa + 114, '۱۹۳۲ | ۱۳۱۱ ش', 23, 800, IR, 'l')
T(x32 + 10, IRa + 141, 'نخستین کارخانه چای ایران (لاهیجان)', 21, 500, INK, 'l')
HALO[0] = None

# =====================================================================
# 2. IRAN STATS
# =====================================================================
ST = 1640
section_title(W - M, ST, '۲', 'صنعت چای ایران در یک نگاه', None, IR)
T(W - M - 670, ST, '— منبع: سازمان چای کشور · تاریخ به‌روزرسانی صفحه: ۱۷ اردیبهشت ۱۳۹۹ (آمار تاریخی؛ نه وضعیت امروز)', 23, 400, MUTED, 'r')
cards = [('leaf', 'حدود', '۲۶ هزار', 'هکتار باغ چای'),
         ('village', 'بیش از', '۹۰۰', 'روستای چایکار'),
         ('family', 'حدود', '۵۵ هزار', 'خانوار فعال در کشت چای'),
         ('worker', 'حدود', '۶۰۰۰', 'نفر شاغل کارخانه و بسته‌بندی'),
         ('factory', '', '۱۸۲', 'کارخانه چای‌سازی')]
cw = (W - 2 * M - 4 * 28) / 5
for i, (ic, q, num, lab) in enumerate(cards):
    x1 = W - M - i * (cw + 28)
    x0 = x1 - cw
    R(x0, ST + 30, cw, 185, fill=CARD, stroke=LINE, sw=2, rx=14)
    R(x0, ST + 30, cw, 10, fill=IR if i % 2 == 0 else C2, rx=4)
    badge(ic, x1 - 70, ST + 110, 44, IR if i % 2 == 0 else C1)
    T(x1 - 136, ST + 90, q, 22, 500, MUTED, 'r')
    T(x1 - 136, ST + 156, num, 64, 900, INK, 'r')
    T(x1 - 26, ST + 198, lab, 23, 600, INK, 'r')

# ---- donut + plain/foothill ----
DT = ST + 245
PX0 = 1980; PX1 = W - M
R(PX0, DT, PX1 - PX0, 450, fill=CARD, stroke=LINE, sw=2, rx=14)
T(PX1 - 30, DT + 50, 'سهم تولید داخلی از نیاز کشور', 30, 800, INK, 'r')
cx, cy, rr, th = PX1 - 190, DT + 205, 125, 50
def arc(cx, cy, r, a0, a1):
    x0 = cx + r * math.sin(a0); y0 = cy - r * math.cos(a0)
    x1 = cx + r * math.sin(a1); y1 = cy - r * math.cos(a1)
    lg = 1 if (a1 - a0) > math.pi else 0
    return f'M{x0:.1f},{y0:.1f} A{r},{r} 0 {lg} 1 {x1:.1f},{y1:.1f}'
add(f'<path d="{arc(cx, cy, rr, 0, 2*math.pi*0.25)}" stroke="{G1}" stroke-width="{th}" fill="none"/>')
add(f'<path d="{arc(cx, cy, rr, 2*math.pi*0.25, 2*math.pi*0.99999)}" stroke="{C3}" stroke-width="{th}" fill="none"/>')
L(cx, cy - rr - th/2 - 4, cx, cy - rr + th/2 + 4, CARD, 5)
L(cx + rr - th/2 - 4, cy, cx + rr + th/2 + 4, cy, CARD, 5)
T(cx, cy + 6, '۱/۴', 64, 900, G1, 'm')
T(cx, cy + 46, 'حدود یک‌چهارم', 21, 500, MUTED, 'm')
lx = cx - 210
R(lx - 30, DT + 130, 30, 30, fill=G1, rx=4)
T(lx - 44, DT + 156, '۲۵٪ تولید داخلی', 30, 800, G1, 'r')
T(lx - 44, DT + 188, 'حدود یک‌چهارم نیاز کشور', 21, 400, MUTED, 'r')
R(lx - 30, DT + 225, 30, 30, fill=C3, rx=4)
T(lx - 44, DT + 251, '۷۵٪ واردات', 30, 800, C1, 'r')
T(lx - 44, DT + 283, 'بقیه نیاز از راه واردات', 21, 400, MUTED, 'r')
# plain / foothill one-line bar
by = DT + 385
T(PX1 - 30, by - 30, 'پراکندگی باغ‌های چای', 24, 700, INK, 'r')
bw = PX1 - PX0 - 60
bx1 = PX1 - 30
R(bx1 - bw * 0.30, by, bw * 0.30, 34, fill=G3)
R(bx1 - bw, by, bw * 0.70, 34, fill=G1)
icon('plain', bx1 - 44, by + 1, 32, G1)
T(bx1 - 52, by + 26, 'جلگه ۳۰٪', 22, 800, G1, 'r')
icon('mountain', bx1 - bw + 8, by + 1, 32, CARD)
T(bx1 - bw + 48, by + 26, 'کوهپایه ۷۰٪ (بقیه)', 22, 800, CARD, 'l')
T(PX1 - 30 - 300, by - 30, '(حدود؛ سازمان چای کشور)', 20, 400, MUTED, 'r')

# ---- three bar charts ----
BX0, BX1 = M, 1950
R(BX0, DT, BX1 - BX0, 450, fill=CARD, stroke=LINE, sw=2, rx=14)
T(BX1 - 30, DT + 50, '۳ · مقایسه در گذر زمان', 30, 800, INK, 'r')
T(BX1 - 360, DT + 50, '— همه محورها از صفر شروع می‌شوند', 21, 400, MUTED, 'r')
charts = [
    ('سطح زیر کشت', 'هکتار', [('۱۳۰۹', 600, '۶۰۰'), ('۱۳۱۹', 4000, '۴۰۰۰')], G1, True),
    ('مصرف کل چای', 'هزار تن', [('۱۳۷۸', 41, '۴۱'), ('۱۳۹۸', 126, '۱۲۶')], C2, False),
    ('مصرف سرانه', 'کیلوگرم برای هر نفر', [('۱۳۵۶', 1.2, '۱٫۲'), ('۱۳۹۵', 1.5, '۱٫۵')], IR, False),
]
chw = (BX1 - BX0 - 60) / 3
base = DT + 398
ph = 215
for i, (tt, unit, vals, col, fac) in enumerate(charts):
    cx1 = BX1 - 30 - i * chw
    cx0 = cx1 - chw + 40
    T(cx1, DT + 98, tt, 25, 800, col, 'r')
    T(cx1, DT + 126, f'({unit})', 20, 400, MUTED, 'r')
    vmax = max(v for _, v, _ in vals)
    L(cx0, base, cx1, base, INK, 2.5)
    T(cx1 + 6, base + 7, '۰', 18, 500, MUTED, 'l')
    bwid = 120
    for j, (yr, v, lab) in enumerate(vals):
        bcx = cx1 - 110 - j * 220
        h = ph * v / vmax
        R(bcx - bwid / 2, base - h, bwid, h, fill=col if j == 1 else (G3 if col == G1 else (C3 if col == C2 else "#A88C77")), rx=3)
        T(bcx, base - h - 12, lab, 28, 800, INK, 'm')
        T(bcx, base - h - 44, 'حدود', 18, 500, MUTED, 'm')
        T(bcx, base + 30, yr, 22, 700, MUTED, 'm')
    if fac:
        bcx = cx1 - 110 - 220
        icon('factory', bcx - 112, base - ph + 6, 30, CARD)
        T(bcx - 16, base - ph + 30, '۱۴ کارخانه', 19, 700, CARD, 'm')

# =====================================================================
# 6. MAPS
# =====================================================================
MT = 2395
section_title(W - M, MT, '۶', 'مسیرهای انتقال چای و کشورهای تولیدکننده', None, G1)
# routes map panel (right, wide)
MX0, MX1 = 1130, W - M
MY0, MY1 = MT + 25, MT + 650
R(MX0, MY0, MX1 - MX0, MY1 - MY0, fill=CARD, stroke=LINE, sw=2, rx=14)
mox, moy = MX0 + 30, MY0 + 45       # map origin (map is ~1130 x 600)
add(f'<g transform="translate({mox},{moy})">')
add(f'<path d="{MAPS["grat"]}" fill="none" stroke="{LINE}" stroke-width="1"/>')
for d in MAPS['world']:
    add(f'<path d="{d}" fill="{CREAM2}" stroke="{CARD}" stroke-width="1"/>')
for k, d in MAPS['prod'].items():
    add(f'<path d="{d}" fill="{G3}" stroke="{CARD}" stroke-width="1.2"/>')
P = MAPS['pts']
add('<defs>'
    f'<marker id="ahG" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{G1}"/></marker>'
    f'<marker id="ahC" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{C1}"/></marker>'
    f'<pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="10" stroke="{C1}" stroke-width="3.5"/></pattern>'
    f'<pattern id="waves" width="40" height="18" patternUnits="userSpaceOnUse"><path d="M0,9 q10,-7 20,0 t20,0" fill="none" stroke="{G3}" stroke-width="1.6"/></pattern>'
    '</defs>')
# colonial cultivation hatch over India & Sri Lanka
for k in ('india', 'srilanka'):
    add(f'<path d="{MAPS["prod"][k]}" fill="url(#hatch)" opacity="0.55"/>')
def p(k): return P[k]
def qcurve(a, b, bend=0.2):
    (x0, y0), (x1, y1) = a, b
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    cx, cy = mx - dy * bend, my + dx * bend
    return f'M{x0},{y0} Q{cx:.1f},{cy:.1f} {x1},{y1}'
# land route: China -> Tibet -> Central Asia -> Iran
add(f'<path d="M{p("yunnan")[0]},{p("yunnan")[1]} Q{p("tibet")[0]+40},{p("tibet")[1]+40} {p("tibet")[0]},{p("tibet")[1]} Q{p("casia")[0]+60},{p("casia")[1]-10} {p("casia")[0]},{p("casia")[1]} Q{p("iran")[0]+50},{p("iran")[1]-60} {p("iran")[0]+10},{p("iran")[1]-8}" fill="none" stroke="{G1}" stroke-width="6" stroke-linecap="round" marker-end="url(#ahG)"/>')
# East: China -> Korea / Japan
add(f'<path d="{qcurve(p("china"), (p("korea")[0]-10, p("korea")[1]), -0.18)}" fill="none" stroke="{G1}" stroke-width="5" stroke-dasharray="12 7" marker-end="url(#ahG)"/>')
add(f'<path d="{qcurve(p("china"), (p("japan")[0]-6, p("japan")[1]+8), -0.25)}" fill="none" stroke="{G1}" stroke-width="5" stroke-dasharray="12 7" marker-end="url(#ahG)"/>')
# Sea: Canton -> Malacca -> Indian Ocean (exit bottom) ... Atlantic (enter left) -> Netherlands -> England
cz, ml, i1, i2 = p('canton'), p('malacca'), p('io1'), p('io2')
add(f'<path d="M{cz[0]},{cz[1]} Q{cz[0]-30},{cz[1]+120} {ml[0]},{ml[1]} Q{i1[0]+40},{i1[1]-10} {i1[0]},{i1[1]} L{i2[0]},{i2[1]-6}" fill="none" stroke="{C1}" stroke-width="5" stroke-dasharray="14 8" marker-end="url(#ahC)"/>')
at, ne, en = p('atl'), p('neth'), p('eng')
add(f'<path d="M{at[0]-40},{at[1]+30} Q{at[0]+60},{at[1]-20} {ne[0]-4},{ne[1]+10}" fill="none" stroke="{C1}" stroke-width="5" stroke-dasharray="14 8" marker-end="url(#ahC)"/>')
add(f'<path d="{qcurve((ne[0]-6, ne[1]-6), (en[0]+8, en[1]-4), 0.6)}" fill="none" stroke="{C1}" stroke-width="5" marker-end="url(#ahC)"/>')
add('</g>')
def mp(k):
    return mox + P[k][0], moy + P[k][1]
# map labels
x, y = mp('china');  C(x, y, 8, fill=G1); T(x + 14, y - 12, 'چین', 26, 800, G1, 'l', halo=CARD)
x, y = mp('tibet');  T(x, y - 26, 'تبت', 22, 700, INK, 'm', halo=CARD)
T(x + 30, y + 52, 'مسیر چای و اسب', 20, 800, G1, 'm', halo=CARD)
x, y = mp('casia');  T(x, y - 20, 'آسیای مرکزی', 22, 700, INK, 'm', halo=CARD)
x, y = mp('iran');   C(x, y, 7, fill=IR); T(x - 12, y + 34, 'ایران', 24, 800, IR, 'm', halo=CARD)
x, y = mp('korea');  T(x - 4, y - 22, 'کره', 21, 700, INK, 'm', halo=CARD)
x, y = mp('japan');  T(x + 8, y - 28, 'ژاپن', 21, 700, INK, 'm', halo=CARD)
x, y = mp('neth');   T(x + 10, y + 32, 'هلند', 21, 700, C1, 'l', halo=CARD)
x, y = mp('eng');    T(x - 6, y - 16, 'انگلستان', 21, 700, C1, 'm', halo=CARD)
x, y = mp('io1');    T(x + 40, y + 28, 'مسیر دریایی (VOC)', 20, 700, C1, 'l', latin=False, halo=CARD)
x, y = mp('atl');    T(x + 10, y + 74, 'ادامه مسیر دریایی', 19, 500, C1, 'l', halo=CARD)
x, y = mp('indc');   T(x - 60, y + 20, 'هند و سیلان:', 20, 800, C1, 'r', halo=CARD); T(x - 60, y + 44, 'کشت استعماری، قرن ۱۹', 19, 500, C1, 'r', halo=CARD)
# map legend (bottom-left inside panel)
lgx, lgy = MX0 + 30, MY1 - 140
legs = [('solid', G1, 'مسیر زمینی چین ← تبت ← آسیای مرکزی ← ایران'),
        ('dash', G1, 'چین ← کره و ژاپن'),
        ('dashC', C1, 'دریایی: چین ← هلند ← انگلستان'),
        ('hatch', C1, 'کشت استعماری (هند و سیلان)')]
for i, (st, col, lab) in enumerate(legs):
    yy = lgy + i * 32
    if st == 'hatch':
        R(lgx, yy - 14, 46, 18, fill='url(#hatch)', stroke=C1, sw=1)
    else:
        da = '' if st == 'solid' else 'stroke-dasharray="10 6"'
        L(lgx, yy - 5, lgx + 46, yy - 5, col, 5, da)
    T(lgx + 58, yy + 2, lab, 20, 500, INK, 'l')
# producers list (right column inside panel)
plx = MX1 - 30
T(plx, MY0 + 50, '۱۰ کشور مهم تولیدکننده', 25, 800, G1, 'r')
T(plx, MY0 + 78, '(بدون رتبه‌بندی؛ رتبه در منبع نیامده)', 18, 400, MUTED, 'r')
prods = ['چین', 'هند', 'کنیا', 'سریلانکا', 'ترکیه', 'ویتنام', 'اندونزی', 'ژاپن', 'بنگلادش', 'ایران']
for i, n in enumerate(prods):
    yy = MY0 + 112 + i * 40
    icon('pin', plx - 26, yy - 24, 28, G1 if n != 'ایران' else IR)
    T(plx - 36, yy - 2, n, 23, 700 if n == 'ایران' else 500, INK, 'r')
R(plx - 26, MY0 + 112 + 10 * 40 - 10, 26, 18, fill=G3)
T(plx - 36, MY0 + 112 + 10 * 40 + 6, 'سایه سبز روی نقشه', 18, 400, MUTED, 'r')

# Iran north map (left panel)
NX0, NX1 = M, 1100
R(NX0, MY0, NX1 - NX0, MY1 - MY0, fill=CARD, stroke=LINE, sw=2, rx=14)
T(NX1 - 30, MY0 + 50, 'نقشه چایکاری شمال ایران', 28, 800, INK, 'r')
T(NX1 - 30, MY0 + 80, 'گیلان و مازندران (شماتیک)', 20, 400, MUTED, 'r')
ix, iy, sc = NX0 + 30, MY0 + 70, 0.88
add(f'<g transform="translate({ix},{iy}) scale({sc})">')
add(f'<defs><clipPath id="irclip"><rect x="4" y="4" width="1122" height="552"/></clipPath></defs>')
add(f'<rect x="0" y="0" width="1130" height="560" fill="url(#waves)"/>')
add('<g clip-path="url(#irclip)">')
for d in MAPS['ir']['land']:
    add(f'<path d="{d}" fill="{C4}" stroke="{C2}" stroke-width="3"/>')
add('</g>')
dv, dv2 = MAPS['ir']['c']['divider'], MAPS['ir']['c']['divider2']
add('</g>')
def ip(k):
    c = MAPS['ir']['c'][k]
    return ix + c[0] * sc, iy + c[1] * sc
# sea label
T(ix + 330 * sc, iy + 70 * sc, 'دریای خزر', 30, 700, G2, 'm')
# province divider (approximate)
ax_, ay_ = ip('divider'); bx_, by_ = ip('divider2')
L(ax_ + 4, ay_ + 60, bx_ + 4, by_ - 10, MUTED, 2.5, 'stroke-dasharray="10 7"')
T(ax_ - 20, by_ - 40, 'گیلان', 40, 900, G2, 'r', 'opacity="0.55"')
T(ax_ + 30, by_ - 40, 'مازندران', 40, 900, C2, 'l', 'opacity="0.6"')
T(ax_ + 4, by_ - 4, 'مرز تقریبی', 17, 400, MUTED, 'm')
cities = [  # key, name, dx, dy, anchor, prov
    ('rasht', 'رشت', 0, -28, 'm', 'g'), ('someh', 'صومعه‌سرا', -16, -10, 'r', 'g'),
    ('fuman', 'فومن', -16, 4, 'r', 'g'), ('shaft', 'شفت', 0, 32, 'm', 'g'),
    ('astaneh', 'آستانه اشرفیه', 6, -30, 'm', 'g'), ('lahijan', 'لاهیجان', -30, 0, 'r', 'g'),
    ('siahkal', 'سیاهکل', -6, 34, 'm', 'g'), ('langarud', 'لنگرود', 10, -24, 'l', 'g'),
    ('amlash', 'املش', 0, 34, 'm', 'g'), ('rudsar', 'رودسر', 16, 4, 'l', 'g'),
    ('ramsar', 'رامسر', 16, -6, 'l', 'm'), ('tonekabon', 'تنکابن', 16, -4, 'l', 'm')]
for k, n, dx, dy, a, pv in cities:
    x, y = ip(k)
    col = G1 if pv == 'g' else C1
    C(x, y, 9 if k != 'lahijan' else 12, fill=col, stroke=CARD, sw=3)
    T(x + dx, y + dy + 8, n, 22 if k != 'lahijan' else 25, 800 if k == 'lahijan' else 600, col, a, halo=C4)
x, y = ip('lahijan')
C(x, y, 20, fill='none', stroke=G1, sw=2.5)
# map note
icon('leaf', NX0 + 34, MY1 - 64, 32, G1)
T(NX0 + 76, MY1 - 40, 'لاهیجان: نخستین کشت آزمایشی (۱۹۰۲ م) و نخستین کارخانه (۱۳۱۱ ش)', 20, 600, INK, 'l')

# =====================================================================
# 4. PROCESSING
# =====================================================================
PT = 3105
section_title(W - M, PT, '۴', 'از برگ تا استکان: فرآوری و انواع چای', None, C1)
RX0, RX1 = 1310, W - M
R(RX0, PT + 25, RX1 - RX0, 480, fill=CARD, stroke=LINE, sw=2, rx=14)
# oxidation spectrum
T(RX1 - 30, PT + 75, 'طیف میزان اکسیداسیون', 26, 800, INK, 'r')
T(RX1 - 330, PT + 75, '(ترتیبی؛ فاصله‌ها کمّی نیستند)', 19, 400, MUTED, 'r')
gx1, gx0 = RX1 - 50, RX0 + 300
gy = PT + 160
add('<defs><linearGradient id="oxg" x1="1" x2="0" y1="0" y2="0">'
    f'<stop offset="0" stop-color="#EEF0D6"/><stop offset="0.3" stop-color="{G3}"/><stop offset="0.5" stop-color="#C9B25A"/>'
    f'<stop offset="0.72" stop-color="{C2}"/><stop offset="1" stop-color="{BR}"/></linearGradient></defs>')
R(gx0, gy - 16, gx1 - gx0, 32, fill='url(#oxg)', rx=16)
types = [('سفید', 'اکسیداسیون محدود'), ('سبز', 'توقف زودهنگام با حرارت'), ('زرد', 'مرحله اضافه زردشدن'),
         ('اولانگ', 'نیمه‌اکسید'), ('سیاه', 'اکسیداسیون گسترده')]
step = (gx1 - gx0 - 60) / (len(types) - 1)
for i, (n, d) in enumerate(types):
    x = gx1 - 30 - i * step
    C(x, gy, 13, fill=CARD, stroke=INK, sw=3)
    T(x, gy - 32, n, 26, 800, INK, 'm')
    T(x, gy + 48, d, 18, 500, MUTED, 'm')
# pu-erh separate (aging)
px = RX0 + 170
L(gx0 - 20, gy - 40, gx0 - 20, gy + 40, MUTED, 2, 'stroke-dasharray="4 4"')
C(px, gy, 13, fill=BR, stroke=INK, sw=3)
T(px, gy - 32, 'پوئر', 26, 800, BR, 'm')
T(px, gy + 48, 'کهنگی و فرآوری میکروبی', 18, 500, MUTED, 'm')
add(f'<path d="M{gx1-10},{gy+80} L{gx0+10},{gy+80}" stroke="{INK}" stroke-width="2.5" marker-end="url(#ahC)"/>')
T(gx1, gy + 88, 'کم', 20, 700, INK, 'l')
T(gx0, gy + 88, 'زیاد', 20, 700, INK, 'r')
# 6-step flowchart
T(RX1 - 30, PT + 305, 'شش مرحله فرآوری', 26, 800, INK, 'r')
steps = [('wither', 'پژمردن', 'کاهش رطوبت اولیه'), ('roll', 'مالش و پیچاندن', 'آزاد شدن ترکیبات'),
         ('oxid', 'اکسیداسیون', 'در برخی انواع چای'), ('flame', 'حرارت‌دهی', 'کنترل یا توقف آنزیم‌ها'),
         ('sun', 'خشک‌کردن', 'آماده نگهداری'), ('box', 'درجه‌بندی و بسته‌بندی', 'بر اساس اندازه و شکل')]
sw_ = (RX1 - RX0 - 60) / 6
for i, (ic, n, d) in enumerate(steps):
    cxs = RX1 - 30 - sw_ / 2 - i * sw_
    cys = PT + 385
    badge(ic, cxs, cys, 38, C1 if ic == 'oxid' else G1)
    C(cxs + 30, cys - 30, 14, fill=C1 if ic == 'oxid' else G1)
    T(cxs + 30, cys - 23, f'{i+1}', 18, 800, CARD, 'm')
    T(cxs, cys + 72, n, 22, 800, INK, 'm')
    T(cxs, cys + 100, d, 18, 400, MUTED, 'm')
    if i < 5:
        ax1 = cxs - 50; ax2 = cxs - sw_ + 52
        add(f'<path d="M{ax1:.1f},{cys} L{ax2:.1f},{cys}" stroke="{C2}" stroke-width="3" marker-end="url(#ahC)"/>')

# Iranian black tea table (left)
TX0, TX1 = M, 1280
R(TX0, PT + 25, TX1 - TX0, 480, fill=CARD, stroke=LINE, sw=2, rx=14)
T(TX1 - 30, PT + 75, 'انواع چای سیاه ایرانی', 26, 800, INK, 'r')
cols = [TX1 - 30, TX1 - 230, TX1 - 340, TX1 - 760]    # name | size icon | material | feature
hy = PT + 125
R(TX0 + 20, hy - 30, TX1 - TX0 - 40, 44, fill=CREAM2, rx=6)
T(cols[0], hy, 'نام', 21, 800, INK, 'r')
T(cols[1] - 50, hy, 'اندازه', 21, 800, INK, 'm')
T(cols[2], hy, 'ماده اولیه / اندازه', 21, 800, INK, 'r')
T(cols[3], hy, 'ویژگی', 21, 800, INK, 'r')
rows = [('سرگل', 'برگ و جوانه‌های ظریف بالای بوته', 'عطر قابل‌توجه؛ نوع بهاره محبوب', 5),
        ('قلم', 'برگ‌های درشت‌تر و پیچیده', 'نام از شکل ظاهری برگ‌ها', 4),
        ('ممتاز', 'ترکیبی از برگ‌های مختلف', 'میان سرگل و انواع شکسته', 3),
        ('شکسته', 'برگ‌های کوچک‌تر', 'خردشده در فرایند تولید', 2),
        ('باروتی (کله‌مورچه‌ای)', 'ذرات ریزتر چای', 'نام از شکل ظاهری ذرات', 1)]
for i, (n, m_, f_, sz) in enumerate(rows):
    yy = hy + 64 + i * 61
    if i % 2 == 1:
        R(TX0 + 20, yy - 38, TX1 - TX0 - 40, 60, fill="#F4ECDD", rx=4)
    T(cols[0], yy, n, 22 if i < 4 else 20, 800, IR, 'r')
    # size glyph: leaf size decreases
    s = 12 + sz * 6
    if sz >= 3:
        icon('leaf', cols[1] - 50 - s / 2, yy - 10 - s / 2, s, G1, sw=3.2)
    elif sz == 2:
        for dx in (-12, 4):
            icon('leaf', cols[1] - 50 + dx - 8, yy - 18, 16, G1, sw=3)
    else:
        for dx, dy in ((-14, -14), (-2, -6), (10, -14), (-8, 0), (6, 0)):
            C(cols[1] - 50 + dx, yy + dy - 4, 3.5, fill=G1)
    T(cols[2], yy, m_, 20, 500, INK, 'r')
    T(cols[3], yy, f_, 20, 400, MUTED, 'r')
T(TX1 - 30, PT + 478, 'این نام‌ها بیشتر درجه‌بندی تجاری و اندازه برگ‌اند و به‌تنهایی تضمین کیفیت نیستند.', 18, 400, MUTED, 'r')

# =====================================================================
# 5. CULTURE
# =====================================================================
CT = 3665
section_title(W - M, CT, '۵', 'فرهنگ چای در جهان', None, C2)
cul = [('gaiwan', 'چین', 'تعارف چای، نشانه احترام به مهمان'),
       ('matcha', 'ژاپن', 'چادو (راه چای) و ماچا'),
       ('cup', 'انگلستان', 'چای عصرانه (Afternoon Tea)'),
       ('samovar', 'روسیه', 'سماور و دورهمی خانوادگی'),
       ('mint', 'مراکش', 'چای سبز با نعناع و شکر'),
       ('kulhad', 'هند', 'چای ماسالا و چای‌والای خیابانی'),
       ('irancup', 'ایران', 'مهمان‌نوازی؛ با قند، نبات و خرما')]
gap = 22
ccw = (W - 2 * M - 6 * gap) / 7
for i, (ic, n, d) in enumerate(cul):
    x1 = W - M - i * (ccw + gap)
    x0 = x1 - ccw
    hi = n == 'ایران'
    R(x0, CT + 25, ccw, 150, fill=G1 if hi else CARD, stroke=LINE if not hi else G1, sw=2, rx=14)
    badge(ic, x1 - 58, CT + 80, 36, C1 if not hi else G1, bg=CARD)
    T(x1 - 112, CT + 92, n, 30, 800, CARD if hi else INK, 'r')
    T(x1 - 18, CT + 152, d, 19.5, 500, G4 if hi else MUTED, 'r', latin=False)

# =====================================================================
# 7. COMPOUNDS + WARNING
# =====================================================================
KT = 3925
CX0 = 1000
T(W - M, KT, '۷ · در یک فنجان چای چه هست؟', 30, 800, INK, 'r')
comp = [('bolt', 'کافئین', 'محرک؛ افزایش هوشیاری'), ('hexring', 'پلی‌فنول‌ها', 'شامل آنتی‌اکسیدان‌ها'),
        ('hexleaf', 'کاتچین‌ها', 'به‌ویژه در چای سبز'), ('chain', 'تیانین', 'یک اسیدآمینه'),
        ('purine', 'تئوفیلین / تئوبرومین', 'از گروه متیل‌گزانتین‌ها'), ('aroma', 'ترکیبات معطر', 'سازنده رایحه چای')]
kw = (W - M - CX0 - 20) / 6
for i, (ic, n, d) in enumerate(comp):
    x1 = W - M - i * kw
    badge(ic, x1 - 36, KT + 66, 32, G1)
    T(x1 - 80, KT + 62, n, 21, 800, INK, 'r')
    T(x1 - 80, KT + 90, d, 18, 400, MUTED, 'r')
# warning box
R(M, KT - 36, CX0 - M - 40, 150, fill=C4, stroke=C1, sw=3, rx=14)
icon('warn', CX0 - 40 - 74, KT - 12, 52, C1)
T(CX0 - 40 - 92, KT + 18, 'چای واقعی فقط از Camellia sinensis است.', 25, 800, C1, 'r')
T(CX0 - 40 - 92, KT + 56, 'چای ترش، بابونه و گل‌گاوزبان دمنوش‌اند، نه چای.', 22, 500, INK, 'r')
icon('herb', M + 24, KT + 52, 40, C1)

# =====================================================================
# FOOTER
# =====================================================================
FT = 4120
L(M, FT - 30, W - M, FT - 30, LINE, 2)
T(W - M, FT, 'منابع: دانشنامه ایرانیکا (مدخل Tea، دانیل بالان و مارسل بازن) · سازمان چای کشور — تاریخ به‌روزرسانی آمار: ۱۷ اردیبهشت ۱۳۹۹', 21, 600, INK, 'r')
T(W - M, FT + 34, 'داده‌ها فقط از سند «تاریخچه چای»؛ جایی که منابع اختلاف دارند، هر دو روایت یا «حدود» درج شده است. نقشه‌ها شماتیک‌اند.', 19, 400, MUTED, 'r')
T(M, FT + 34, 'اینفوگرافیک درس گرافیک خبری · A3', 19, 500, MUTED, 'l')

# =====================================================================
def font_css():
    if not EMBED:
        return ''
    css = []
    for wname, wv in [('Regular', 400), ('Medium', 500), ('SemiBold', 600), ('Bold', 700), ('ExtraBold', 800), ('Black', 900)]:
        b = base64.b64encode(open(os.path.join(FONTDIR, f'Vazirmatn-{wname}.woff2'), 'rb').read()).decode()
        css.append(f"@font-face{{font-family:'Vazirmatn';font-weight:{wv};src:url(data:font/woff2;base64,{b}) format('woff2');}}")
    return '\n'.join(css)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="420mm" viewBox="0 0 {W} {H}" direction="rtl" lang="fa">\n'
       f'<title>چای؛ از افسانه تا استکان</title>\n'
       f'<style>{font_css()}\ntext{{font-family:Vazirmatn,Tahoma,sans-serif;direction:rtl}}</style>\n'
       + '\n'.join(O) + '\n</svg>\n')
out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else os.path.join(S, 'tea.svg')
open(out, 'w', encoding='utf-8').write(svg)
print('wrote', out, len(svg) // 1024, 'KB')
