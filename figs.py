"""SVG drawing helpers for the Thai reasoning test. All figures are pure inline SVG."""
import math

INK = "#111"
SW = 3  # outline stroke width
FONT = "Sarabun, 'Leelawadee UI', Tahoma, sans-serif"

DEFS = (
    '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
    '<pattern id="stripe" patternUnits="userSpaceOnUse" width="8" height="8">'
    '<rect width="8" height="8" fill="#fff"/>'
    '<path d="M-2,2 L2,-2 M0,8 L8,0 M6,10 L10,6" stroke="#111" stroke-width="2.4" stroke-linecap="square"/></pattern>'
    '</defs></svg>'
)


def _paint(fill):
    if fill == "black":
        return f'fill="{INK}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"'
    if fill == "white":
        return f'fill="#fff" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"'
    if fill == "stripe":
        return f'fill="url(#stripe)" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"'
    raise ValueError(fill)


def _pts(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def shape(kind, cx, cy, s, fill="black"):
    """Draw one shape centred at (cx, cy); s is roughly the radius."""
    p = _paint(fill)
    if kind == "circle":
        return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{s:.1f}" {p}/>'
    if kind == "ocircle":
        return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{s:.1f}" {_paint("white")}/>'
    if kind == "triangle":
        return f'<polygon points="{_pts([(cx, cy - s * 1.08), (cx + s * 1.08, cy + s * 0.82), (cx - s * 1.08, cy + s * 0.82)])}" {p}/>'
    if kind == "square":
        a = s * 0.88
        return f'<rect x="{cx - a:.1f}" y="{cy - a:.1f}" width="{2 * a:.1f}" height="{2 * a:.1f}" {p}/>'
    if kind == "diamond":
        a = s * 1.15
        return f'<polygon points="{_pts([(cx, cy - a), (cx + a, cy), (cx, cy + a), (cx - a, cy)])}" {p}/>'
    if kind == "star":
        pts = []
        for i in range(10):
            r = s * 1.2 if i % 2 == 0 else s * 0.5
            ang = -math.pi / 2 + i * math.pi / 5
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        return f'<polygon points="{_pts(pts)}" {p}/>'
    if kind == "cross":
        a, L = s * 0.36, s * 1.08
        pts = [(cx - a, cy - L), (cx + a, cy - L), (cx + a, cy - a), (cx + L, cy - a), (cx + L, cy + a),
               (cx + a, cy + a), (cx + a, cy + L), (cx - a, cy + L), (cx - a, cy + a), (cx - L, cy + a),
               (cx - L, cy - a), (cx - a, cy - a)]
        return f'<polygon points="{_pts(pts)}" {p}/>'
    if kind == "heart":
        k = s / 15.0
        d = (f"M{cx:.1f},{cy + 14 * k:.1f} C{cx - 20 * k:.1f},{cy + 1 * k:.1f} {cx - 19 * k:.1f},{cy - 15 * k:.1f} {cx - 8 * k:.1f},{cy - 14 * k:.1f} "
             f"C{cx - 3 * k:.1f},{cy - 14 * k:.1f} {cx:.1f},{cy - 10 * k:.1f} {cx:.1f},{cy - 7 * k:.1f} "
             f"C{cx:.1f},{cy - 10 * k:.1f} {cx + 3 * k:.1f},{cy - 14 * k:.1f} {cx + 8 * k:.1f},{cy - 14 * k:.1f} "
             f"C{cx + 19 * k:.1f},{cy - 15 * k:.1f} {cx + 20 * k:.1f},{cy + 1 * k:.1f} {cx:.1f},{cy + 14 * k:.1f} Z")
        return f'<path d="{d}" {p}/>'
    if kind == "half":
        return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{s:.1f}" fill="#fff"/>'
                f'<path d="M{cx:.1f},{cy - s:.1f} A{s:.1f},{s:.1f} 0 0 0 {cx:.1f},{cy + s:.1f} Z" fill="{INK}"/>'
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{s:.1f}" fill="none" stroke="{INK}" stroke-width="{SW}"/>')
    raise ValueError(kind)


def shapes_row(items, cx, cy, s, gap):
    """items: list of (kind, fill). Lay out in one centred row."""
    n = len(items)
    step = 2 * s * 1.1 + gap
    x0 = cx - step * (n - 1) / 2
    return "".join(shape(k, x0 + i * step, cy, s, f) for i, (k, f) in enumerate(items))


def arrow(cx, cy, length, angle, width=7, head=None):
    """Arrow centred at (cx, cy); angle 0 = up, 90 = right, 180 = down, 270 = left."""
    h = length / 2
    head = head if head is not None else length * 0.38
    return (f'<g transform="rotate({angle} {cx:.1f} {cy:.1f})">'
            f'<line x1="{cx:.1f}" y1="{cy + h:.1f}" x2="{cx:.1f}" y2="{cy - h + head * 0.6:.1f}" stroke="{INK}" '
            f'stroke-width="{width}" stroke-linecap="round"/>'
            f'<polygon points="{_pts([(cx, cy - h), (cx + head * 0.62, cy - h + head), (cx - head * 0.62, cy - h + head)])}" fill="{INK}"/>'
            f'</g>')


def qmark(cx, cy, size=46):
    return (f'<text x="{cx:.1f}" y="{cy + size * 0.36:.1f}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="700" fill="{INK}">?</text>')


def text(x, y, s, size=16, anchor="middle", weight=400, fill=INK):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}">{s}</text>')


def inline_shape(kind):
    """A small shape sized to sit inside a line of text."""
    return (f'<svg viewBox="0 0 40 40" style="width:.85em;height:.85em;vertical-align:-.1em;display:inline" aria-hidden="true">'
            f'{shape(kind, 20, 21, 15)}</svg>')


def svg(w, h, body, width_mm, label=""):
    aria = f' role="img" aria-label="{label}"' if label else ' aria-hidden="true"'
    return (f'<svg viewBox="0 0 {w} {h}" style="width:{width_mm}mm;height:auto;display:block" '
            f'xmlns="http://www.w3.org/2000/svg"{aria}>{body}</svg>')


# ---------- composite figures ----------

def cell_frame(x, y, w, h, dashed=False):
    dash = ' stroke-dasharray="7 6"' if dashed else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="{INK}" stroke-width="2"{dash}/>'


def grid(cells, W, H, width_mm, header=False):
    """cells: 3x3 list of callables f(x, y, W, H) -> svg, or None for the '?' cell."""
    rows, cols = len(cells), len(cells[0])
    top = 30 if header else 0
    body = ""
    if header:
        for c in range(cols):
            body += text(c * W + W / 2, 21, f"ช่อง {c + 1}", size=17)
    for r in range(rows):
        for c in range(cols):
            x, y = c * W, top + r * H
            f = cells[r][c]
            body += cell_frame(x + 1, y + 1, W - 2, H - 2, dashed=(f is None))
            body += qmark(x + W / 2, y + H / 2) if f is None else f(x, y, W, H)
    return svg(cols * W, top + rows * H, body, width_mm)


def seq(cells, W, H, width_mm):
    """A left-to-right sequence of boxes; None = '?' box."""
    body = ""
    for i, f in enumerate(cells):
        x = i * W
        body += cell_frame(x + 1, 1, W - 2, H - 2, dashed=(f is None))
        body += qmark(x + W / 2, H / 2) if f is None else f(x, 0, W, H)
    return svg(len(cells) * W, H, body, width_mm)


def single(f, W, H, width_mm, frame=False):
    body = (cell_frame(1, 1, W - 2, H - 2) if frame else "") + f(0, 0, W, H)
    return svg(W, H, body, width_mm)


# cell content factories -------------------------------------------------

def c_shapes(items, s=15, gap=8):
    """items: list of (kind, fill) drawn in a row."""
    return lambda x, y, W, H: shapes_row(items, x + W / 2, y + H / 2, s, gap)


def c_n(kind, n, fill="black", s=15, gap=8):
    return c_shapes([(kind, fill)] * n, s, gap)


def c_arrow(angle, length=62):
    return lambda x, y, W, H: arrow(x + W / 2, y + H / 2, length, angle)


def c_num(v, size=40):
    return lambda x, y, W, H: text(x + W / 2, y + H / 2 + size * 0.35, str(v), size=size, weight=700)


CORNERS = ["TL", "TR", "BR", "BL"]  # clockwise


def c_dot_arrow(corner, angle):
    def f(x, y, W, H):
        inset = 16
        body = (f'<rect x="{x + inset}" y="{y + inset}" width="{W - 2 * inset}" height="{H - 2 * inset}" '
                f'fill="none" stroke="{INK}" stroke-width="2.5"/>')
        d = 17
        px = x + inset + d if corner in ("TL", "BL") else x + W - inset - d
        py = y + inset + d if corner in ("TL", "TR") else y + H - inset - d
        body += f'<circle cx="{px}" cy="{py}" r="9" fill="{INK}"/>'
        body += arrow(x + W / 2, y + H / 2, 44, angle, width=6)
        return body
    return f


# ---------- illustrations ----------

def houses_figure(lang="th"):
    en = lang == "en"
    W, H = 600, 172
    body = ""
    for i in range(5):
        cx = 60 + i * 120
        body += (f'<polygon points="{_pts([(cx - 40, 62), (cx, 22), (cx + 40, 62)])}" fill="#fff" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
                 f'<rect x="{cx - 32}" y="62" width="64" height="50" fill="#fff" stroke="{INK}" stroke-width="3"/>'
                 f'<rect x="{cx - 9}" y="84" width="18" height="28" fill="#fff" stroke="{INK}" stroke-width="2.5"/>')
        body += text(cx, 138, (f"House {i + 1}" if en else f"หลังที่ {i + 1}"), size=18, weight=700)
    body += (text(60, 164, "(far left)" if en else "(ซ้ายสุด)", size=16)
             + text(540, 164, "(far right)" if en else "(ขวาสุด)", size=16))
    return svg(W, H, body, 150, "Five houses in a row, left to right" if en else "บ้าน 5 หลังเรียงจากซ้ายไปขวา")


def bar_chart(lang="th"):
    en = lang == "en"
    months = ["January", "February", "March", "April"] if en else ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน"]
    data = list(zip(months, [20000, 30000, 42000, 38000]))
    W, H = 560, 320
    left, bottom, top = 88, 266, 40
    maxv = 50000
    scale = (bottom - top) / maxv
    body = ""
    for v in range(0, maxv + 1, 10000):
        y = bottom - v * scale
        body += f'<line x1="{left}" y1="{y:.1f}" x2="{W - 10}" y2="{y:.1f}" stroke="#bbb" stroke-width="1"/>'
        body += text(left - 8, y + 6, f"{v:,}", size=17, anchor="end")
    bw = 70
    for i, (m, v) in enumerate(data):
        x = left + 30 + i * 115
        h = v * scale
        body += f'<rect x="{x}" y="{bottom - h:.1f}" width="{bw}" height="{h:.1f}" fill="#9a9a9a" stroke="{INK}" stroke-width="2"/>'
        body += text(x + bw / 2, bottom - h - 8, f"{v:,}", size=16, weight=700)
        body += text(x + bw / 2, bottom + 26, m, size=18)
    body += f'<line x1="{left}" y1="{bottom}" x2="{W - 10}" y2="{bottom}" stroke="{INK}" stroke-width="2"/>'
    body += text(8, 18, "Sales (baht)" if en else "ยอดขาย (บาท)", size=17, anchor="start", weight=700)
    return svg(W, H, body, 125, "Bar chart of sales" if en else "กราฟแท่งยอดขาย")


def walk_figure(lang="th"):
    en = lang == "en"
    W, H = 560, 170
    # house (left)
    hx = 70
    body = (f'<polygon points="{_pts([(hx - 45, 75), (hx, 32), (hx + 45, 75)])}" fill="#fff" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
            f'<rect x="{hx - 36}" y="75" width="72" height="55" fill="#fff" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="{hx - 10}" y="100" width="20" height="30" fill="#fff" stroke="{INK}" stroke-width="2.5"/>')
    body += text(hx, 158, "Home" if en else "บ้าน", size=18, weight=700)
    # temple (right): tiered roof
    tx = 490
    body += (f'<rect x="{tx - 42}" y="92" width="84" height="38" fill="#fff" stroke="{INK}" stroke-width="3"/>'
             f'<polygon points="{_pts([(tx - 58, 94), (tx, 58), (tx + 58, 94)])}" fill="#fff" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
             f'<polygon points="{_pts([(tx - 38, 66), (tx, 36), (tx + 38, 66)])}" fill="#fff" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
             f'<line x1="{tx}" y1="36" x2="{tx}" y2="14" stroke="{INK}" stroke-width="3"/>'
             f'<rect x="{tx - 9}" y="106" width="18" height="24" fill="#fff" stroke="{INK}" stroke-width="2.5"/>')
    body += text(tx, 158, "Temple" if en else "วัด", size=18, weight=700)
    # arrows
    body += arrow(280, 70, 250, 90, width=4, head=22) + text(280, 52, "There: 4 km/h" if en else "ขาไป  4 กม./ชม.", size=18, weight=700)
    body += arrow(280, 104, 250, 270, width=4, head=22) + text(280, 138, "Back: 6 km/h" if en else "ขากลับ  6 กม./ชม.", size=18, weight=700)
    return svg(W, H, body, 130, "Walking from home to the temple and back" if en else "เดินจากบ้านไปวัดและกลับ")


def clock_face(lang="th"):
    W = H = 220
    cx = cy = 110
    body = f'<circle cx="{cx}" cy="{cy}" r="100" fill="#fff" stroke="{INK}" stroke-width="4"/>'
    for m in range(60):
        a = math.radians(m * 6)
        r1 = 90 if m % 5 == 0 else 95
        body += (f'<line x1="{cx + r1 * math.sin(a):.1f}" y1="{cy - r1 * math.cos(a):.1f}" '
                 f'x2="{cx + 100 * math.sin(a):.1f}" y2="{cy - 100 * math.cos(a):.1f}" stroke="{INK}" '
                 f'stroke-width="{3 if m % 5 == 0 else 1.2}"/>')
    for hnum in range(1, 13):
        a = math.radians(hnum * 30)
        body += text(cx + 74 * math.sin(a), cy - 74 * math.cos(a) + 8, str(hnum), size=22, weight=700)
    body += f'<circle cx="{cx}" cy="{cy}" r="4" fill="{INK}"/>'
    return svg(W, H, body, 52, "Clock face" if lang == "en" else "หน้าปัดนาฬิกา")


def icon(kind):
    W = H = 120
    s = f'stroke="{INK}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "ruler":
        b = f'<rect x="10" y="46" width="100" height="30" fill="#fff" {s}/>'
        for i in range(11):
            x = 16 + i * 8.8
            L = 14 if i % 5 == 0 else 8
            b += f'<line x1="{x:.1f}" y1="46" x2="{x:.1f}" y2="{46 + L}" stroke="{INK}" stroke-width="2"/>'
    elif kind == "scissors":
        b = (f'<line x1="44" y1="76" x2="92" y2="14" {s} stroke-width="7"/>'
             f'<line x1="76" y1="76" x2="28" y2="14" {s} stroke-width="7"/>'
             f'<circle cx="38" cy="92" r="15" fill="#fff" {s}/>'
             f'<circle cx="82" cy="92" r="15" fill="#fff" {s}/>'
             f'<circle cx="60" cy="48" r="4" fill="#fff" stroke="{INK}" stroke-width="2"/>')
    elif kind == "clock":
        b = f'<circle cx="60" cy="60" r="44" fill="#fff" {s}/>'
        for hnum in range(12):
            a = math.radians(hnum * 30)
            b += (f'<line x1="{60 + 36 * math.sin(a):.1f}" y1="{60 - 36 * math.cos(a):.1f}" '
                  f'x2="{60 + 42 * math.sin(a):.1f}" y2="{60 - 42 * math.cos(a):.1f}" stroke="{INK}" stroke-width="3"/>')
        b += (f'<line x1="60" y1="60" x2="{60 + 22 * math.sin(math.radians(305)):.1f}" y2="{60 - 22 * math.cos(math.radians(305)):.1f}" {s}/>'
              f'<line x1="60" y1="60" x2="{60 + 32 * math.sin(math.radians(60)):.1f}" y2="{60 - 32 * math.cos(math.radians(60)):.1f}" {s} stroke-width="3"/>')
    elif kind == "scale":
        b = (f'<line x1="60" y1="24" x2="60" y2="98" {s}/>'
             f'<rect x="36" y="98" width="48" height="8" fill="{INK}"/>'
             f'<line x1="18" y1="30" x2="102" y2="30" {s}/>'
             f'<circle cx="60" cy="24" r="5" fill="{INK}"/>')
        for px in (18, 102):
            b += (f'<line x1="{px}" y1="30" x2="{px - 13}" y2="66" stroke="{INK}" stroke-width="2.5"/>'
                  f'<line x1="{px}" y1="30" x2="{px + 13}" y2="66" stroke="{INK}" stroke-width="2.5"/>'
                  f'<path d="M{px - 17},66 Q{px},84 {px + 17},66 Z" fill="#fff" {s} stroke-width="3"/>')
    else:
        raise ValueError(kind)
    return svg(W, H, b, 26)
