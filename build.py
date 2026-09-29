"""Build the A4-printable HTML package (Thai + English sets) from content.py.

Usage:  python build.py        -> writes package/index.html, package/th/*, package/en/*, package/fonts/*
Then:   python render.py       -> writes package/pdf/{th,en}/*.pdf and pages.json (page counts used on the next build)
"""
import json
import os
import shutil

from markdown_it import MarkdownIt

import content as C
from figs import DEFS, svg, shape, cell_frame, text

OUT = "package"
LANGS = ("th", "en")
PAGES = json.load(open("pages.json")) if os.path.exists("pages.json") else {}


def en_check(lang):
    p = f"templates/en_check_{lang}.md"
    if os.path.exists(p):
        return open(p, encoding="utf-8").read().strip()
    return "(pending)" if lang == "en" else "(รอตรวจ)"


def font_css(prefix):
    thai = "unicode-range:U+0E01-0E5B,U+200C-200D,U+25CC"
    latin = ("unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,"
             "U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD")
    out = ""
    for sub, rng in (("thai", thai), ("latin", latin)):
        for w in (400, 700):
            out += (f"@font-face{{font-family:'Sarabun';font-weight:{w};font-style:normal;font-display:block;"
                    f"src:url({prefix}fonts/sarabun-{sub}-{w}-normal.woff2) format('woff2');{rng}}}\n")
    return out


BASE_CSS = """
:root{--ink:#111;--muted:#555;--rule:#bbb;--soft:#f3f3f3;--paper:#fff;--desk:#e6e6e6}
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;background:var(--paper);color:var(--ink);font-family:'Sarabun','Leelawadee UI','Tahoma',sans-serif;line-height:1.55}
.sheet{width:100%;max-width:180mm;margin:0 auto}
h1,h2,h3{line-height:1.25;margin:0 0 .5em}
table{border-collapse:collapse}
.toolbar{display:none}
@media screen{
  body{background:var(--desk)}
  .sheet{background:var(--paper);max-width:210mm;padding:14mm 15mm;margin:0 auto 12mm;box-shadow:0 1px 6px rgba(0,0,0,.18)}
  .toolbar{display:flex;gap:12px;align-items:center;justify-content:space-between;max-width:210mm;margin:0 auto;padding:12px 4px;
    font-size:15px;color:#333;flex-wrap:wrap}
  .toolbar a{color:#333}
  .toolbar button{font:inherit;font-weight:700;padding:8px 18px;border:2px solid #111;background:#fff;border-radius:6px;cursor:pointer;margin-left:6px}
  .toolbar button:hover{background:#111;color:#fff}
  .pb{border-top:2px dashed #aaa;margin-top:10mm;padding-top:10mm}
}
@media screen and (max-width:760px){
  .sheet{padding:16px;max-width:none}
  .toolbar{padding:10px 16px}
  svg{max-width:100%}
}
@media print{ .pb{break-before:page;padding-top:2mm} .toolbar{display:none} }
"""

S = {
    "th": dict(
        title="แบบทดสอบการคิดและการใช้เหตุผล", sub="ภาษา · ตัวเลข · รูปแบบ · ความเร็ว", foot="แบบทดสอบการคิดและการใช้เหตุผล  ·  หน้า ",
        label=lambda n: f"ข้อ {n}.", print="พิมพ์ (A4)", home="← หน้าแรก",
        fields=("ชื่อ", "อายุ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ปี", "วันที่", "การศึกษาสูงสุด"),
        instr_h="คำชี้แจง",
        instr=["แบบทดสอบมี <b>4 ส่วน</b> ในส่วนที่ 1–3 ข้อแรกๆ จะง่าย แล้วค่อยๆ <b>ยากขึ้นเรื่อยๆ</b> &nbsp;<b>ตอบได้ไม่ครบทุกข้อเป็นเรื่องปกติ</b>",
               "แต่ละข้อมีคำตอบที่ถูกต้องที่สุด <b>เพียงข้อเดียว</b> ให้ <b>วงกลม</b> รอบตัวอักษร ก ข ค หรือ ง",
               "ส่วนที่ 1–3 <b>ไม่จำกัดเวลา</b> ทำตามจังหวะปกติ ไม่ต้องรีบ (ผู้ดูแลจะจดเวลาไว้เท่านั้น)",
               "ถ้าไม่แน่ใจ ให้เลือกข้อที่คิดว่าใกล้เคียงที่สุด <b>อย่าเว้นว่าง</b>",
               "ใช้กระดาษทดได้ <b>ห้ามใช้เครื่องคิดเลขหรือโทรศัพท์</b>",
               "โจทย์แบบ <b>“นก : บิน = ปลา : ?”</b> หมายถึง นกคู่กับบินแบบไหน ปลาก็คู่กับอะไรแบบเดียวกัน"],
        part4=("ส่วนที่ 4", "ความเร็วในการจับคู่ (เขียน)", "จับเวลา 90 วินาที"),
        practice_h=("ตัวอย่าง", "ไม่นับคะแนน · ถามผู้ดูแลได้"),
        code_how=("<b>วิธีทำ:</b> ตารางรหัสบอกว่ารูปแต่ละรูปคู่กับตัวเลขอะไร ให้<b>เขียนตัวเลข</b>ของรูปนั้นลงในช่องว่างใต้รูป "
                  "เรียงจากซ้ายไปขวา ทีละแถว ให้<b>เร็วและถูกต้องที่สุด</b> <b>ห้ามข้ามช่อง</b> "
                  "ถ้าเขียนผิดไม่ต้องลบ ให้เขียนตัวที่ถูกไว้ข้างๆ"),
        code_key="ตารางรหัส", code_prac="<b>แถวฝึก</b> (ไม่จับเวลา) ช่องแรกเขียนให้ดูเป็นตัวอย่างแล้ว ทำช่องที่เหลือกับผู้ดูแล",
        code_turn="เมื่อพร้อมแล้ว พลิกไปหน้าถัดไป แล้วรอผู้ดูแลบอก <b>“เริ่ม”</b>",
        code_start=("ส่วนที่ 4", "ความเร็วในการจับคู่ (จับเวลา)", "90 วินาที"), end="จบแบบทดสอบ ขอบคุณที่ช่วยทำ",
        tb_booklet="แบบทดสอบ (สำหรับผู้ทำแบบทดสอบ) · พิมพ์ขนาด A4 · Scale 100%",
        size_large="ตัวอักษรใหญ่", size_normal="ตัวอักษรปกติ",
        stop="หยุด · รอผู้ดูแลก่อนทำส่วนต่อไป",
    ),
    "en": dict(
        title="Thinking and Reasoning Test", sub="Language · Numbers · Patterns · Speed", foot="Thinking and Reasoning Test  ·  page ",
        label=lambda n: f"{n}.", print="Print (A4)", home="← Home",
        fields=("Name", "Age &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; years", "Date", "Highest level of education"),
        instr_h="Instructions",
        instr=["The test has <b>4 parts</b>. In parts 1–3 the questions start easy and <b>gradually get harder</b>. "
               "<b>Nobody is expected to get them all right.</b>",
               "Each question has only <b>one</b> best answer. <b>Circle</b> the letter A, B, C or&nbsp;D.",
               "Parts 1–3 have <b>no time limit</b>. Work at your normal pace; there is no need to hurry. (The tester only notes the time.)",
               "If you are not sure, make your best guess. <b>Don’t leave any question blank.</b>",
               "You may use scrap paper. <b>No calculators or phones.</b>",
               "A question like <b>“bird : fly = fish : ?”</b> means: find the word that relates to “fish” in the same way that “fly” relates to “bird”."],
        part4=("Part 4", "Matching speed (writing)", "Timed: 90 seconds"),
        practice_h=("Practice questions", "Not scored · you may ask the tester for help"),
        code_how=("<b>How to do it:</b> The key shows which number goes with each shape. In the empty box under each shape, "
                  "<b>write the number</b> that goes with it. Work from left to right, row by row, as <b>quickly and accurately as you can</b>. "
                  "<b>Don’t skip any boxes.</b> If you make a mistake, don’t rub it out; just write the correct number next to it."),
        code_key="Key", code_prac="<b>Practice row</b> (not timed). The first box is done for you. Do the rest with the tester.",
        code_turn="When you are ready, turn to the next page and wait for the tester to say <b>“Start”</b>.",
        code_start=("Part 4", "Matching speed (timed)", "90 seconds"), end="End of the test. Thank you!",
        tb_booklet="Test booklet (for the person taking the test) · Print on A4 · Scale 100%",
        size_large="Large print", size_normal="Normal print",
        stop="Stop · wait for the tester before going on",
    ),
}

BOOKLET_CSS = """
@page{size:A4;margin:12mm 13mm 14mm;
  @bottom-center{content:"__FOOT__" counter(page);font-family:Sarabun,sans-serif;font-size:9pt;color:#666}}
body{--k:1;--fk:.7;font-size:calc(12.5pt*var(--k))}
body.large{--k:1.3;--fk:1}
.cover h1{font-size:calc(21pt*var(--k));margin:2mm 0 1mm}
.cover .sub{font-size:calc(11pt*var(--k));color:var(--muted);margin-bottom:5mm}
.fields{display:grid;grid-template-columns:1fr 1fr;gap:3mm 8mm;margin:0 0 5mm}
.fields div{border-bottom:1.3px solid #111;padding:.8mm 0;font-size:calc(11.5pt*var(--k))}
.fields .wide{grid-column:1/-1}
.instr{border:1.6px solid #111;border-radius:2.5mm;padding:3mm 5mm;margin-bottom:4mm;font-size:calc(12pt*var(--k))}
.instr h2{font-size:calc(14pt*var(--k));margin-bottom:1mm}
.instr ol{margin:0;padding-left:1.3em}
.instr li{margin:.15em 0}
.parts{width:100%;font-size:calc(11pt*var(--k));margin-bottom:6mm}
.parts td{padding:1mm 2mm;border-bottom:1px solid var(--rule)}
.sechead{border-bottom:2.5px solid #111;padding-bottom:1.5mm;margin-bottom:4mm;display:flex;justify-content:space-between;align-items:baseline;gap:4mm}
.sechead h2{font-size:calc(15.5pt*var(--k));margin:0}
.sechead span{font-size:calc(10pt*var(--k));color:var(--muted)}
.item{break-inside:avoid;margin:0 0 calc(3.5mm*var(--k));padding-top:2mm}
.stem{margin-bottom:1.2mm}
.num{font-weight:700;margin-right:.35em;white-space:nowrap}
.hint{font-size:calc(10.5pt*var(--k));color:var(--muted)}
.lead{font-weight:700;margin-bottom:1.5mm}
blockquote{margin:0 0 3mm;padding:2mm 4mm;border-left:4px solid #111;background:var(--soft);font-size:calc(12pt*var(--k))}
.facts{margin:1mm 0 1.5mm 4mm;padding:1.5mm 4mm;border:1.3px solid var(--rule);border-radius:2mm;width:fit-content;max-width:100%}
.fig{margin:1.5mm 0 2.5mm 5mm}
.series{font-size:calc(16pt*var(--k));font-weight:700;letter-spacing:.02em;margin:.5mm 0 2mm 5mm}
.figcap{display:flex;align-items:center;gap:4mm}
.figcap span{font-size:calc(9.5pt*var(--k));color:var(--muted)}
.datafig{display:flex;gap:6mm;align-items:flex-end;margin:1.5mm 0 3mm;flex-wrap:wrap}
table.data{font-size:calc(11.5pt*var(--k))}
table.data caption{font-weight:700;text-align:left;padding-bottom:1mm;caption-side:top;white-space:nowrap}
.grp{break-inside:avoid}
table.data th,table.data td{border:1.3px solid #111;padding:.6mm 4mm;text-align:center}
table.data th{background:var(--soft)}
table.op{margin:1mm 0 2mm 5mm;font-size:calc(13pt*var(--k))}
ol.opts{list-style:none;margin:0;padding:0 0 0 5mm}
ol.opts li{display:flex;gap:2.5mm;align-items:baseline;margin:.6mm 0;min-width:0}
ol.opts li span:last-child{min-width:0;overflow-wrap:anywhere}
.let{font-weight:700;min-width:1.4em}
ol.opts.c2{display:grid;grid-template-columns:1fr 1fr;column-gap:7mm}
ol.opts.c4{display:grid;grid-template-columns:repeat(4,1fr);column-gap:5mm}
.popts{display:grid;gap:2.5mm;margin:1mm 0 0 5mm}
.popts.c4{grid-template-columns:repeat(4,1fr)}
.popts.c2{grid-template-columns:1fr 1fr}
.popt{border:1.3px solid var(--rule);border-radius:2mm;padding:1.5mm;display:flex;flex-direction:column;align-items:center;gap:.5mm}
.popt .let{font-size:calc(12.5pt*var(--k))}
.popt svg{max-width:100%}
.iconlab{font-size:calc(10.5pt*var(--k))}
.code-key{margin:2mm 0 5mm}
.endnote{text-align:center;font-weight:700;margin-top:4mm}
.stopline{text-align:center;font-weight:700;margin:2mm 0 6mm;padding:1.2mm;border-top:1.3px dashed #888;border-bottom:1.3px dashed #888;
  font-size:calc(11pt*var(--k));break-before:avoid}
section.flow{padding-top:2mm}
.pc-sizebtn{margin-left:8px}
@media screen and (max-width:760px){ol.opts.c2{grid-template-columns:1fr} .popts.c2{grid-template-columns:1fr} ol.opts{padding-left:0} .fig,.popts{margin-left:0}}
"""


def page(title, body, css, note, lang, prefix="../", home=True, extra=""):
    home_link = f'<a href="{prefix}index.html">{S[lang]["home"]}</a> · ' if home else ""
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{font_css(prefix)}{BASE_CSS}{css}</style></head>
<body>{DEFS}
<div class="toolbar"><span>{home_link}{note}</span><span>{extra}<button onclick="window.print()">{S[lang]["print"]}</button></span></div>
<main class="sheet">{body}</main>
</body></html>"""


# ------------------------------------------------------------------ booklet
def opts_html(it, LET):
    if it["kind"] == "text":
        longest = max(len(o) for o in it["opts"])
        cls = "c4" if longest <= 12 else ("c2" if longest <= 34 else "")
        lis = "".join(f'<li><span class="let">{LET[i]}.</span><span>{o}</span></li>' for i, o in enumerate(it["opts"]))
        return f'<ol class="opts {cls}">{lis}</ol>'
    cells = "".join(f'<div class="popt">{o}<div class="let">{LET[i]}.</div></div>' for i, o in enumerate(it["opts"]))
    return f'<div class="popts c{it.get("cols", 4)}">{cells}</div>'


def item_html(it, lang, LET):
    n = it["n"]
    label = n if isinstance(n, str) else S[lang]["label"](n)
    parts = [it.get("intro", ""), f'<div class="stem"><span class="num">{label}</span> {it["stem"]}</div>']
    if it.get("fig"):
        parts.append(f'<div class="fig">{it["fig"]}</div>')
    if it.get("stem2"):
        parts.append(f'<div class="stem">{it["stem2"]}</div>')
    parts.append(opts_html(it, LET))
    return f'<div class="item">{"".join(parts)}</div>'


def code_key_svg(mm=118):
    W = 70
    body = ""
    for i, k in enumerate(C.CODE_SYMS):
        x = i * W
        body += cell_frame(x + 1, 1, W - 2, 64) + shape(k, x + W / 2, 33, 17)
        body += cell_frame(x + 1, 65, W - 2, 44) + text(x + W / 2, 98, str(i + 1), size=30, weight=700)
    return svg(6 * W, 110, body, mm, scale=False)


SYM_H, BOX_H, ROW_GAP, CELL_W = 38, 44, 8, 50


def write_cells(digits, y0=0, prefill=None):
    """One row of written-coding cells: shape on top, empty writing box below."""
    body = ""
    for i, d in enumerate(digits):
        x = i * CELL_W
        body += cell_frame(x + 1, y0 + 1, CELL_W - 2, SYM_H - 1) + shape(C.CODE_SYMS[d - 1], x + CELL_W / 2, y0 + SYM_H / 2 + 1, 11.5)
        body += (f'<rect x="{x + 1}" y="{y0 + SYM_H}" width="{CELL_W - 2}" height="{BOX_H - 1}" fill="#fff" '
                 f'stroke="#111" stroke-width="2.2"/>')
        if prefill is not None and i == 0:
            body += text(x + CELL_W / 2, y0 + SYM_H + BOX_H * 0.72, str(prefill), size=30, weight=400, fill="#666")
    return body


def code_practice_svg(mm=100):
    d = C.CODE_PRACTICE
    return svg(len(d) * CELL_W, SYM_H + BOX_H, write_cells(d, prefill=d[0]), mm, scale=False)


def code_grid_svg(mm=156):
    body = "".join(write_cells(row, r * (SYM_H + BOX_H + ROW_GAP)) for r, row in enumerate(C.CODE_ROWS))
    n = len(C.CODE_ROWS)
    return svg(12 * CELL_W, n * (SYM_H + BOX_H + ROW_GAP) - ROW_GAP, body, mm, scale=False)


def items_html(items, lang, LET):
    out, i = "", 0
    while i < len(items):
        g = items[i].get("group")
        if g:
            j = i
            while j < len(items) and items[j].get("group") == g:
                j += 1
            out += '<div class="grp">' + "".join(item_html(it, lang, LET) for it in items[i:j]) + "</div>"
            i = j
        else:
            out += item_html(items[i], lang, LET)
            i += 1
    return out


def build_booklet(lang):
    s, D = S[lang], C.build(lang)
    LET = D["LET"]
    f = s["fields"]
    parts_rows = "".join(f"<tr><td><b>{tag}</b></td><td>{name}</td><td>{rng}</td></tr>" for tag, name, rng, _ in D["SECTIONS"])
    parts_rows += "<tr><td><b>{}</b></td><td>{}</td><td>{}</td></tr>".format(*s["part4"])
    cover = (f'<section class="cover"><h1>{s["title"]}</h1><div class="sub">{s["sub"]}</div>'
             f'<div class="fields"><div class="wide">{f[0]}</div><div>{f[1]}</div><div>{f[2]}</div><div class="wide">{f[3]}</div></div>'
             f'<div class="instr"><h2>{s["instr_h"]}</h2><ol>' + "".join(f"<li>{x}</li>" for x in s["instr"]) + "</ol></div>"
             f'<table class="parts">{parts_rows}</table></section>')
    practice = (f'<section class="practice"><div class="sechead" style="margin-top:2mm"><h2>{s["practice_h"][0]}</h2><span>{s["practice_h"][1]}</span></div>'
                + "".join(item_html(it, lang, LET) for it in D["PRACTICE"]) + f'<div class="stopline">{s["stop"]}</div></section>')
    # Parts carry straight on from each other (with a stop line between them) to save paper.
    secs = "".join(f'<section class="flow"><div class="sechead"><h2>{tag} &nbsp;{name}</h2><span>{rng}</span></div>'
                   + items_html(items, lang, LET) + f'<div class="stopline">{s["stop"]}</div></section>'
                   for i, (tag, name, rng, items) in enumerate(D["SECTIONS"]))
    p4, st = s["part4"], s["code_start"]
    code = (f'<section class="flow"><div class="sechead"><h2>{p4[0]} &nbsp;{p4[1]}</h2><span>{p4[2]}</span></div>'
            f'<p>{s["code_how"]}</p><div class="code-key"><b>{s["code_key"]}</b>{code_key_svg()}</div>'
            f'<p style="margin:0 0 1mm">{s["code_prac"]}</p>{code_practice_svg()}'
            f'<p style="margin:8mm 0 0">{s["code_turn"]}</p></section>'
            f'<section class="pb"><div class="sechead"><h2>{st[0]} &nbsp;{st[1]}</h2><span>{st[2]}</span></div>'
            f'<div class="code-key" style="margin:0 0 3mm">{code_key_svg(mm=78)}</div>{code_grid_svg()}'
            f'<div class="endnote">{s["end"]}</div></section>')
    css = BOOKLET_CSS.replace("__FOOT__", s["foot"])
    size_btn = ('<button class="pc-sizebtn" onclick="document.body.classList.toggle(\'large\');'
                'this.textContent=document.body.classList.contains(\'large\')?\'{0}\':\'{1}\'">{1}</button> ').format(
                    s["size_normal"], s["size_large"])
    return page(s["title"], cover + practice + secs + code, css, s["tb_booklet"], lang, extra=size_btn)


# ------------------------------------------------------------------ guide
DOC_CSS = """
@page{size:A4;margin:14mm 15mm 16mm;
  @bottom-right{content:"__PAGE__ " counter(page);font-family:Sarabun,sans-serif;font-size:9pt;color:#666}
  @bottom-left{content:"__FOOT__";font-family:Sarabun,sans-serif;font-size:9pt;color:#666}}
body{font-size:11pt}
h1{font-size:22pt;margin-top:0}
h2{font-size:15pt;margin:8mm 0 3mm;padding-top:1mm;padding-bottom:1.5mm;border-bottom:2px solid #111;break-after:avoid}
h3{font-size:12.5pt;margin:5mm 0 2mm;break-after:avoid}
p,li{orphans:3;widows:3}
table{width:100%;margin:2mm 0 4mm;font-size:10pt;break-inside:auto}
tr{break-inside:avoid}
th,td{border:1px solid #999;padding:1.3mm 2mm;text-align:left;vertical-align:top}
th{background:var(--soft)}
blockquote{margin:2mm 0 3mm;padding:2.5mm 4mm;border-left:4px solid #111;background:var(--soft);font-size:11.5pt;break-inside:avoid}
blockquote p{margin:.4em 0}
code{font-size:10pt;background:var(--soft);padding:0 3px;border-radius:3px}
.warn{border:2px solid #111;padding:2.5mm 4mm;border-radius:2mm;background:#fff6d6}
"""

GUIDE_S = {
    "th": dict(title="คู่มือผู้ดูแลการทดสอบและเฉลย", page="หน้า", foot="คู่มือผู้ดูแลและเฉลย — เก็บเป็นความลับ",
               key=["ข้อ", "เฉลย", "กลุ่ม", "ความผิดพลาดที่บ่งบอก"], fwd=["ความยาว", "ครั้ง A", "ครั้ง B"],
               bwd=["ความยาว", "ครั้ง A (อ่าน)", "คำตอบที่ถูก", "ครั้ง B (อ่าน)", "คำตอบที่ถูก"],
               note="คู่มือผู้ดูแล · เก็บเป็นความลับ · A4", pages="ประมาณ {}"),
    "en": dict(title="Tester Guide & Answer Key", page="page", foot="Tester guide & answer key — keep private",
               key=["#", "Answer", "Scale", "Error it suggests"], fwd=["Length", "Trial A", "Trial B"],
               bwd=["Length", "Trial A (say)", "Correct reply", "Trial B (say)", "Correct reply"],
               note="Tester guide · keep private · A4", pages="{}"),
}


def md_table(header, rows):
    out = "| " + " | ".join(header) + " |\n|" + "---|" * len(header) + "\n"
    for r in rows:
        out += "| " + " | ".join(str(c) for c in r) + " |\n"
    return out


def both_letters(k, lang):
    th, en = C.LETTERS["th"][k], C.LETTERS["en"][k]
    return f"**{th}** ({en})" if lang == "th" else f"**{en}** ({th})"


def build_guide(lang):
    g, D = GUIDE_S[lang], C.build(lang)
    key_md = md_table(g["key"], [(it["n"], both_letters(it["key"], lang), it["scale"], it.get("err", "")) for it in D["ALL"]])
    fwd = md_table(g["fwd"], [(n, a, b) for n, a, b in C.DS_FWD])
    bwd = md_table(g["bwd"], [(n, a, C.rev(a), b, C.rev(b)) for n, a, b in C.DS_BWD])
    bp = PAGES.get(f"{lang}/1-test-booklet", 22)
    fp = PAGES.get(f"{lang}/3-record-form", 3)
    md = (open(f"templates/guide_{lang}.md", encoding="utf-8").read()
          .replace("{{KEY_TABLE}}", key_md).replace("{{DS_FWD}}", fwd).replace("{{DS_BWD}}", bwd)
          .replace("{{BOOKLET_PAGES}}", g["pages"].format(bp)).replace("{{FORM_PAGES}}", str(fp))
          .replace("{{EN_CHECK}}", en_check(lang)))
    body = MarkdownIt("commonmark", {"html": True}).enable("table").render(md)
    css = DOC_CSS.replace("__PAGE__", g["page"]).replace("__FOOT__", g["foot"])
    return page(g["title"], body, css, g["note"], lang)


# ------------------------------------------------------------------ record form
FORM_CSS = """
@page{size:A4;margin:12mm 13mm 14mm;
  @bottom-right{content:"__FOOT__ " counter(page);font-family:Sarabun,sans-serif;font-size:9pt;color:#666}}
body{font-size:10.5pt}
h1{font-size:17pt;margin:0 0 2mm}
h2{font-size:12.5pt;margin:5mm 0 2mm;border-bottom:2px solid #111;padding:1mm 0}
table{width:100%;margin:1mm 0 3mm}
th,td{border:1px solid #777;padding:1.1mm 1.6mm;text-align:center}
th{background:var(--soft);font-weight:700}
td.l{text-align:left}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm}
.keycol{color:#666}
.box{display:inline-block;width:4.2mm;height:4.2mm;border:1.3px solid #111;vertical-align:middle;margin:0 1.2mm 0 2mm}
.fields td{text-align:left;height:9mm}
.small{font-size:9pt;color:#555}
.code td{height:6.2mm;width:7mm;font-size:10pt}
.ans th,.ans td{padding:.45mm 1.2mm;font-size:9.5pt}
.scales{break-inside:avoid}
.obs td{text-align:left;height:8mm}
@media screen and (max-width:760px){.grid3{grid-template-columns:1fr}}
"""

FORM_S = {
    "th": dict(
        title="แบบบันทึกคะแนน", foot="แบบบันทึกคะแนน · หน้า", sub="(คนละ 1 ชุด · สำหรับผู้ดูแลเท่านั้น · มีเฉลย)",
        name="ชื่อ / รหัส:", group="กลุ่ม:", g=("คุณแม่", "A (คนหนุ่มสาวจบ ป.ตรี)", "B (ผู้สูงอายุรุ่นเดียวกัน)"),
        age="อายุ:", school="จำนวนปีที่เรียน:", date="วันที่:", tester="ผู้ดูแล:",
        lang_q="ภาษาของแบบทดสอบ:", langs=("ไทย", "อังกฤษ"), aids="ใส่แว่น / เครื่องช่วยฟัง:", yn=("ใช่", "ไม่", "ไม่มี"),
        split="แบ่งทำ 2 วัน:", timing="เวลา", tcols=("", "เริ่ม", "จบ", "นาที", "หมายเหตุ (พัก ถูกขัดจังหวะ)"),
        part=lambda i: f"ส่วนที่ {i}", answers="คำตอบ: ลอกตัวอักษรที่วงไว้ในแบบทดสอบ แล้วทำ ✓ ถ้าตรงกับเฉลย",
        acols=("ข้อ", "กลุ่ม", "คำตอบ", "เฉลย", "✓"), total=lambda i: f"รวมส่วนที่ {i}", scales="คะแนนแต่ละกลุ่ม", tot45="รวม /45",
        ds_f="การจำตัวเลข — ไปข้างหน้า (คะแนน = ความยาวมากที่สุดที่ถูก): ______",
        ds_b="การจำตัวเลข — ย้อนกลับ (ฝึก 5-1 → 1-5; คะแนน = ความยาวมากที่สุดที่ถูก): ______",
        dcols=("ความยาว", "ครั้ง A (อ่าน)", "คำตอบ", "ครั้ง B (อ่าน)"),
        code="งานจับคู่แบบเขียน — 90 วินาที (เฉลยแถวฝึก: 5 2 6 4 1 3)",
        code_note=("เทียบช่องที่เขียนกับเฉลยด้านล่าง ขีดทับช่องที่ผิดหรือข้าม และทำเครื่องหมายช่องสุดท้ายที่ทำถึงเมื่อครบ 90 วินาที "
                   "ถ้าเขียนผิดแล้วเขียนตัวที่ถูกไว้ข้างๆ นับว่าถูก ถ้าทำครบ 108 ช่องก่อน 90 วินาที ให้จดเวลาที่ใช้: ______ วินาที "
                   "&nbsp; วิธีทำ: ☐ เขียน &nbsp;☐ พูด (ใช้เมื่อเขียนลำบากจริงๆ เท่านั้น)"),
        row="แถว", ctot=("จำนวนช่องที่ทำถึง", "ผิดหรือข้าม", "ถูกใน 90 วินาที"), obs="สิ่งที่สังเกตได้ (มักมีประโยชน์ต่อแพทย์พอๆ กับคะแนน)",
        obs_items=["ต้องอธิบายคำชี้แจงหรือข้อตัวอย่างซ้ำ", "ลืมโจทย์กลางทาง / อ่านซ้ำหลายรอบ", "ช้ากว่าที่คาดมาก แต่รอบคอบ",
                   "เร็วแต่ผิดแบบสะเพร่าในข้อง่าย", "นึกคำไม่ออก หรือตอบแปลกๆ อย่างมั่นใจ", "เหนื่อย หงุดหงิด หรือไม่สบายใจ (ตอนไหน?)",
                   "การได้ยินหรือการมองเห็นดูเป็นอุปสรรค", "อื่นๆ"],
        note="แบบบันทึกคะแนน · พิมพ์คนละ 1 ชุด · ผู้ดูแลเท่านั้น"),
    "en": dict(
        title="Record form", foot="record form · page", sub="(one per person · tester only · shows the key)",
        name="Name / code:", group="Group:", g=("Mom", "A (young grad)", "B (age peer)"),
        age="Age:", school="Years of schooling:", date="Date(s):", tester="Tester:",
        lang_q="Booklet language:", langs=("Thai", "English"), aids="Glasses / hearing aid used:", yn=("yes", "no", "n/a"),
        split="Split over two days:", timing="Timing", tcols=("", "Start", "End", "Minutes", "Notes (breaks, interruptions)"),
        part=lambda i: f"Part {i}", answers="Answers: copy the letter circled in the booklet; tick ✓ if it matches the key",
        acols=("#", "Scale", "Answer", "Key", "✓"), total=lambda i: f"Part {i} total", scales="Scale scores", tot45="Total /45",
        ds_f="Digit span — forward (score = longest length passed): ______",
        ds_b="Digit span — backward (practice 5-1 → 1-5; score = longest length passed): ______",
        dcols=("Length", "Trial A (say)", "Reply", "Trial B (say)"),
        code="Coding, written — 90 seconds (practice answers: 5 2 6 4 1 3)",
        code_note=("Compare the booklet with the answers below. Slash every wrong or skipped box and mark the last box reached at 90 s. "
                   "A mistake with the right number written beside it counts as correct. If the person finishes all 108 boxes before 90 s, "
                   "write the finishing time: ______ s &nbsp; Mode: ☐ written &nbsp;☐ spoken (only if writing is physically hard)"),
        row="Row", ctot=("Boxes reached", "Wrong or skipped", "Correct in 90 s"), obs="Observations (often as useful to a doctor as the score)",
        obs_items=["Needed instructions or a practice item repeated", "Lost track of a question midway / re-read many times",
                   "Much slower than expected, but careful", "Fast but careless errors on easy items",
                   "Word-finding trouble or odd answers given confidently", "Tired, frustrated or upset (when?)",
                   "Hearing or vision seemed to limit performance", "Other notes"],
        note="Record form · print one per person · tester only"),
}


def build_form(lang):
    F, D = FORM_S[lang], C.build(lang)
    box = '<span class="box"></span>'
    head = (f'<h1>{F["title"]} &nbsp;<span class="small">{F["sub"]}</span></h1><table class="fields">'
            f'<tr><td style="width:50%">{F["name"]}</td><td>{F["group"]}' + "".join(box + x for x in F["g"]) + "</td></tr>"
            f'<tr><td>{F["age"]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {F["school"]}</td>'
            f'<td>{F["date"]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {F["tester"]}</td></tr>'
            f'<tr><td>{F["lang_q"]}' + "".join(box + x for x in F["langs"]) + f'</td><td>{F["split"]}'
            + "".join(box + x for x in F["yn"][:2]) + "</td></tr>"
            f'<tr><td colspan="2">{F["aids"]}' + "".join(box + x for x in F["yn"]) + "</td></tr></table>"
            f'<h2>{F["timing"]}</h2><table><tr>' + "".join(f"<th>{c}</th>" for c in F["tcols"]) + "</tr>"
            + "".join(f'<tr><td>{F["part"](i)}</td><td></td><td></td><td></td><td></td></tr>' for i in (1, 2, 3))
            + f'</table><h2>{F["answers"]}</h2>')
    cols = ""
    for si, (_, _, _, items) in enumerate(D["SECTIONS"], start=1):
        rows = "".join(f'<tr><td>{it["n"]}</td><td>{it["scale"]}</td><td></td>'
                       f'<td class="keycol">{C.LETTERS[lang][it["key"]]} · {C.LETTERS["en" if lang == "th" else "th"][it["key"]]}</td><td></td></tr>'
                       for it in items)
        cols += (f'<div><table class="ans"><tr>' + "".join(f"<th>{c}</th>" for c in F["acols"]) + f"</tr>{rows}"
                 f'<tr><td colspan="4" class="l"><b>{F["total"](si)}</b></td><td></td></tr></table></div>')
    scores = (f'<h2>{F["scales"]}</h2><table class="scales"><tr><th>K /7<br><span class="small">1,2,3,4,7,8,10</span></th>'
              '<th>VR /8<br><span class="small">5,6,9,11–15</span></th><th>N /15<br><span class="small">16–30</span></th>'
              f'<th>P /15<br><span class="small">31–45</span></th><th>{F["tot45"]}</th></tr>'
              '<tr><td style="height:10mm"></td><td></td><td></td><td></td><td></td></tr></table>')
    dc = F["dcols"]

    def ds_table(title, rows, backward):
        h = f"<tr><th>{dc[0]}</th><th>{dc[1]}</th>" + (f"<th>{dc[2]}</th>" if backward else "") + f"<th>✓</th><th>{dc[3]}</th>" \
            + (f"<th>{dc[2]}</th>" if backward else "") + "<th>✓</th></tr>"
        body = "".join(f"<tr><td>{n}</td><td>{a}</td>" + (f'<td class="keycol">{C.rev(a)}</td>' if backward else "")
                       + f"<td></td><td>{b}</td>" + (f'<td class="keycol">{C.rev(b)}</td>' if backward else "") + "<td></td></tr>"
                       for n, a, b in rows)
        return f"<h2>{title}</h2><table>{h}{body}</table>"

    ds = ds_table(F["ds_f"], C.DS_FWD, False) + ds_table(F["ds_b"], C.DS_BWD, True)
    code_rows = "".join(f"<tr><th>{r + 1}</th>" + "".join(f"<td>{d}</td>" for d in row) + "</tr>" for r, row in enumerate(C.CODE_ROWS))
    code = (f'<h2>{F["code"]}</h2><p class="small">{F["code_note"]}</p><table class="code"><tr><th>{F["row"]}</th>'
            + "".join(f"<th>{i}</th>" for i in range(1, 13)) + f"</tr>{code_rows}</table><table><tr>"
            + "".join(f"<th>{c}</th>" for c in F["ctot"]) + '</tr><tr><td style="height:10mm"></td><td></td><td></td></tr></table>')
    obs = (f'<h2>{F["obs"]}</h2><table class="obs">'
           + "".join(f"<tr><td style='width:45%'>{box}{o}</td><td></td></tr>" for o in F["obs_items"]) + "</table>")
    body = head + f'<div class="grid3">{cols}</div>' + scores + '<div class="pb">' + ds + '</div><div class="pb">' + code + obs + "</div>"
    return page(F["title"], body, FORM_CSS.replace("__FOOT__", F["foot"]), F["note"], lang)


# ------------------------------------------------------------------ comparison summary
SUMMARY_CSS = """
@page{size:A4 landscape;margin:11mm 12mm 12mm}
body{font-size:10pt}
@media screen{.sheet{max-width:297mm}.toolbar{max-width:297mm}.tw{overflow-x:auto}}
.sheet{max-width:273mm}
h1{font-size:16pt;margin:0 0 1mm}
table{width:100%}
th,td{border:1px solid #777;padding:1.2mm 1.5mm;text-align:center}
th{background:var(--soft)}
td{height:8.4mm}
.small{font-size:8.5pt;color:#555}
"""

SUM_S = {
    "th": dict(title="ตารางสรุปผลเปรียบเทียบ",
               note="กลุ่ม A = คนหนุ่มสาวจบปริญญาตรี (20–30 ปี) · กลุ่ม B = ผู้สูงอายุรุ่นเดียวกัน (70–85 ปี) · "
                    "เทียบโดยเรียงลำดับภายในแต่ละกลุ่ม ทีละคอลัมน์ (ดูคู่มือข้อ 8–9) · เทียบ K และ VR เฉพาะคนที่ทำฉบับภาษาเดียวกัน",
               cols=["ชื่อ / รหัส", "กลุ่ม", "ภาษา", "อายุ", "ปีที่เรียน", "K /7", "VR /8", "N /15", "P /15", "รวม /45", "DS-F", "DS-B",
                     "จับคู่ 90 วิ", "เวลา ส.1", "เวลา ส.2", "เวลา ส.3"],
               mom="คุณแม่", ra="คุณแม่อยู่ตรงไหนในกลุ่ม A", ra_eg="(เช่น “ต่ำกว่าทั้ง 8 คน”)", rb="คุณแม่อยู่ตรงไหนในกลุ่ม B",
               tb="ตารางสรุปผล · A4 แนวนอน"),
    "en": dict(title="Comparison summary",
               note="Group A = young graduates (20–30) · Group B = age peers (70–85) · compare by rank within each group, one column at a "
                    "time (guide §8–9) · compare K and VR only between people who took the same language version",
               cols=["Person / code", "Group", "Lang.", "Age", "Yrs school", "K /7", "VR /8", "N /15", "P /15", "Total /45", "DS-F",
                     "DS-B", "Coding 90 s", "Time P1", "Time P2", "Time P3"],
               mom="Mom", ra="Where Mom falls in Group A", ra_eg="(e.g. “below all 8”)", rb="Where Mom falls in Group B",
               tb="Comparison summary · A4 landscape"),
}


def build_summary(lang):
    s = SUM_S[lang]
    n = len(s["cols"])
    rows = f"<tr><td><b>{s['mom']}</b></td>" + "<td></td>" * (n - 1) + "</tr>" + ("<tr>" + "<td></td>" * n + "</tr>") * 14
    rank = (f"<tr><td colspan='5' style='text-align:left'><b>{s['ra']}</b> <span class='small'>{s['ra_eg']}</span></td>"
            + "<td></td>" * (n - 5) + f"</tr><tr><td colspan='5' style='text-align:left'><b>{s['rb']}</b></td>" + "<td></td>" * (n - 5) + "</tr>")
    body = (f"<h1>{s['title']}</h1><p class='small'>{s['note']}</p><div class='tw'><table><tr>"
            + "".join(f"<th>{c}</th>" for c in s["cols"]) + f"</tr>{rows}{rank}</table></div>")
    return page(s["title"], body, SUMMARY_CSS, s["tb"], lang)


# ------------------------------------------------------------------ index
INDEX_CSS = """
@page{size:A4;margin:15mm}
body{font-size:12pt}
h1{font-size:22pt;margin-bottom:1mm}
.sub{color:#555;margin-bottom:6mm}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:8mm}
@media screen and (max-width:760px){.cols{grid-template-columns:1fr}}
.cols h2{font-size:16pt;border-bottom:2px solid #111;padding-bottom:1mm}
.files{display:grid;gap:3mm;margin:3mm 0}
.files a{display:block;border:2px solid #111;border-radius:3mm;padding:3mm 4mm;color:#111;text-decoration:none}
.files a:hover{background:#f3f3f3}
.files b{font-size:12.5pt}
.files span{display:block;color:#555;font-size:10.5pt}
.warn{border:2px solid #111;padding:3mm 4mm;border-radius:2mm;background:#fff6d6;font-size:11pt}
ol{padding-left:1.2em} ol li{margin:1mm 0;font-size:11pt}
.pc-link{display:block;margin:0 0 7mm;padding:4mm 5mm;border-radius:3mm;background:#111;color:#fff;text-decoration:none}
.pc-link b{font-size:15pt;display:block}
.pc-link span{font-size:11pt;opacity:.9}
.pc-link:hover{background:#333}
"""

IDX = {
    "th": dict(h="ภาษาไทย", files=[("1-test-booklet.html", "1 · แบบทดสอบ", "พิมพ์คนละ 1 ชุด ({} หน้า A4)"),
                                    ("2-tester-guide.html", "2 · คู่มือผู้ดูแลและเฉลย", "อ่านก่อน · เก็บเป็นความลับ"),
                                    ("3-record-form.html", "3 · แบบบันทึกคะแนน", "พิมพ์คนละ 1 ชุด · มีเฉลย"),
                                    ("4-comparison-summary.html", "4 · ตารางสรุปผล", "1 แผ่น A4 แนวนอน")],
               warn="<b>ก่อนเริ่ม:</b> อ่านคู่มือก่อน โดยเฉพาะข้อ 2 (ข้อจำกัด) และข้อ 8–9 (วิธีเทียบและอ่านผล) อย่าให้ผู้ทำแบบทดสอบเห็นไฟล์ 2–4",
               print=["เก็บโฟลเดอร์ <code>fonts</code> ไว้ที่เดิม", "เปิดไฟล์ด้วย Chrome หรือ Edge แล้วกด Ctrl+P (Mac: ⌘P)",
                      "กระดาษ <b>A4</b> · Scale <b>100%</b> · Margins <b>Default</b> · ปิด “Headers and footers”",
                      "พิมพ์แบบทดสอบ<b>หน้าเดียว</b> (ไม่พิมพ์สองหน้า) เพื่อไม่ให้เห็นตารางจับเวลาก่อนเริ่ม และลองพิมพ์ข้อ 43 ดูว่าลายขีดแยกจากสีดำได้ชัด",
                      "หรือพิมพ์จากไฟล์ในโฟลเดอร์ <code>pdf/th</code>"]),
    "en": dict(h="English", files=[("1-test-booklet.html", "1 · Test booklet", "Print one per person ({} A4 pages)"),
                                   ("2-tester-guide.html", "2 · Tester guide & answer key", "Read first · keep private"),
                                   ("3-record-form.html", "3 · Record form", "Print one per person · shows the key"),
                                   ("4-comparison-summary.html", "4 · Comparison summary", "One A4 landscape sheet")],
               warn="<b>Before testing:</b> read the guide, especially §1 (which language), §2 (limits) and §8–9 (comparing and reading "
                    "results). Keep files 2–4 away from test-takers.",
               print=["Keep the <code>fonts</code> folder where it is", "Open a file in Chrome or Edge → Ctrl+P (Mac: ⌘P)",
                      "Paper <b>A4</b> · Scale <b>100%</b> · Margins <b>Default</b> · “Headers and footers” off",
                      "Print the booklet <b>single-sided</b>, so the timed grid isn't visible before “Start”. Test-print item 43 to check the hatched shapes look clearly different from the black ones",
                      "Or print the ready-made files in <code>pdf/en</code>"]),
}


def build_index():
    cols = ""
    for lang in LANGS:
        x = IDX[lang]
        bp = PAGES.get(f"{lang}/1-test-booklet", 22)
        links = "".join(f'<a href="{lang}/{f}"><b>{t}</b><span>{d.format(bp)}</span></a>' for f, t, d in x["files"])
        cols += (f'<div lang="{lang}"><h2>{x["h"]}</h2><div class="files">{links}</div><p class="warn">{x["warn"]}</p>'
                 "<ol>" + "".join(f"<li>{p}</li>" for p in x["print"]) + "</ol></div>")
    body = ('<h1>แบบทดสอบการคิดและการใช้เหตุผล<br>Thinking and Reasoning Test</h1>'
            '<div class="sub">ภาษา · ตัวเลข · รูปแบบ · ความจำ · ความเร็ว &nbsp;/&nbsp; Language · Numbers · Patterns · Memory · Speed</div>'
            '<a class="pc-link" href="print.html"><b>🖨 เลือกพิมพ์ · Print center</b><span>ติ๊กเลือกเอกสารหรือเฉพาะบางส่วนของแบบทดสอบ แล้วพิมพ์ทีเดียว A4 · '
            'Tick the documents or booklet parts you need and print them in one go on A4</span></a>'
            f'<div class="cols">{cols}</div>')
    return page("Thinking and Reasoning Test", body, INDEX_CSS, "ภาษาไทย / English", "th", prefix="", home=False)


if __name__ == "__main__":
    C.self_check()
    os.makedirs(os.path.join(OUT, "fonts"), exist_ok=True)
    for f in os.listdir("fonts"):
        shutil.copy(os.path.join("fonts", f), os.path.join(OUT, "fonts", f))
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(build_index())
    for lang in LANGS:
        os.makedirs(os.path.join(OUT, lang), exist_ok=True)
        for name, fn in [("1-test-booklet.html", build_booklet), ("2-tester-guide.html", build_guide),
                         ("3-record-form.html", build_form), ("4-comparison-summary.html", build_summary)]:
            path = os.path.join(OUT, lang, name)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(fn(lang))
            print("wrote", path, os.path.getsize(path) // 1024, "KB")
    import printcenter  # noqa: E402  (builds package/print.html from the same content)
    printcenter.main()
