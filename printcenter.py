"""Print center: one page (package/print.html) where you tick the documents or booklet parts you want, then print them
together on A4. All content is embedded, so it works when opened straight from a folder (file://) with no server.
"""
import json
import os
import re

import build
from figs import DEFS

OUT = os.path.join(build.OUT, "print.html")
PC_PAGES = json.load(open("pc_pages.json")) if os.path.exists("pc_pages.json") else {}

# --------------------------------------------------------------------------- CSS scoping
def _match(css, i):
    depth = 0
    for j in range(i, len(css)):
        if css[j] == "{":
            depth += 1
        elif css[j] == "}":
            depth -= 1
            if depth == 0:
                return j
    raise ValueError("unbalanced css")


def scope_css(css, sc):
    """Prefix every selector with `sc`; drop @page and @font-face (the print center defines its own)."""
    out, i = [], 0
    while True:
        b = css.find("{", i)
        if b < 0:
            break
        sel = css[i:b].strip()
        e = _match(css, b)
        inner = css[b + 1:e]
        if sel.startswith("@page") or sel.startswith("@font-face"):
            pass
        elif sel.startswith("@media"):
            out.append(f"{sel}{{{scope_css(inner, sc)}}}")
        else:
            parts = []
            for p in sel.split(","):
                p = p.strip()
                if p in ("body", "html"):
                    parts.append(sc)
                elif p.startswith(":root"):
                    parts.append(p)
                else:
                    parts.append(f"{sc} {p}")
            out.append(",".join(parts) + "{" + inner + "}")
        i = e + 1
    return "\n".join(out)


# --------------------------------------------------------------------------- collect bodies
def collect():
    real_page = build.page
    build.page = lambda title, body, css, note, lang, prefix="../", home=True: body
    try:
        blocks = []
        for lang in build.LANGS:
            secs = re.findall(r"<section\b.*?</section>", build.build_booklet(lang), flags=re.S)
            assert len(secs) == 7, len(secs)  # cover, practice, p1, p2, p3, p4 instructions, p4 grid
            parts = [("cover", secs[0]), ("practice", secs[1]), ("p1", secs[2]), ("p2", secs[3]), ("p3", secs[4]),
                     ("p4", secs[5] + secs[6])]
            for key, html in parts:
                blocks.append((f"{lang}-{key}", lang, "booklet", html))
            blocks.append((f"{lang}-guide", lang, "guide", build.build_guide(lang)))
            blocks.append((f"{lang}-form", lang, "form", build.build_form(lang)))
            blocks.append((f"{lang}-summary", lang, "summary", build.build_summary(lang)))
    finally:
        build.page = real_page
    return blocks


LABELS = {
    "th": {"cover": "หน้าปกและคำชี้แจง", "practice": "ข้อตัวอย่าง (4 ข้อ)", "p1": "ส่วนที่ 1 ภาษา (ข้อ 1–15)",
           "p2": "ส่วนที่ 2 ตัวเลข (ข้อ 16–30)", "p3": "ส่วนที่ 3 รูปแบบ (ข้อ 31–45)", "p4": "ส่วนที่ 4 จับคู่แบบเขียน (จับเวลา)",
           "guide": "คู่มือผู้ดูแลและเฉลย", "form": "แบบบันทึกคะแนน (ต่อ 1 คน)", "summary": "ตารางสรุปผล (A4 แนวนอน)"},
    "en": {"cover": "Cover and instructions", "practice": "Practice questions (4)", "p1": "Part 1 Language (Q1–15)",
           "p2": "Part 2 Numbers (Q16–30)", "p3": "Part 3 Patterns (Q31–45)", "p4": "Part 4 Written matching (timed)",
           "guide": "Tester guide & answer key", "form": "Record form (one per person)", "summary": "Comparison summary (landscape)"},
}
UI = {
    "th": dict(h="ภาษาไทย", booklet="แบบทดสอบ — ให้ผู้ทำแบบทดสอบ", tester="สำหรับผู้ดูแลเท่านั้น (มีเฉลย)",
               all="ทั้งเล่ม", pages="หน้า"),
    "en": dict(h="English", booklet="Test booklet — for the test-taker", tester="Tester only (contains answers)",
               all="Whole booklet", pages="pp"),
}

FOOT = {
    "booklet_th": "แบบทดสอบการคิดและการใช้เหตุผล", "booklet_en": "Thinking and Reasoning Test",
    "guide_th": "คู่มือผู้ดูแลและเฉลย — เก็บเป็นความลับ", "guide_en": "Tester guide & answer key — keep private",
    "form_th": "แบบบันทึกคะแนน", "form_en": "Record form",
}

PC_CSS = """
:root{--ink:#111;--muted:#555;--rule:#bbb;--soft:#f3f3f3;--paper:#fff;--desk:#e6e6e6;--accent:#1f4e79}
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;color:var(--ink);font-family:'Sarabun','Leelawadee UI','Tahoma',sans-serif;line-height:1.55;background:var(--desk);font-size:15px}
table{border-collapse:collapse}
h1,h2,h3{line-height:1.25;margin:0 0 .5em}
.pc-top{background:#fff;border-bottom:1px solid #ccc;padding:14px 20px}
.pc-top h1{font-size:22px;margin:0}
.pc-top p{margin:2px 0 0;color:var(--muted)}
.pc-wrap{display:grid;grid-template-columns:340px 1fr;gap:18px;padding:18px;align-items:start}
.pc-panel{position:sticky;top:12px;background:#fff;border:1px solid #ccc;border-radius:10px;padding:14px 16px;max-height:calc(100vh - 24px);overflow:auto}
.pc-panel h2{font-size:18px;margin:12px 0 4px;padding-bottom:3px;border-bottom:2px solid #111}
.pc-panel h2:first-child{margin-top:0}
.pc-panel .sub{font-size:13px;font-weight:700;color:var(--muted);margin:8px 0 2px}
.pc-panel .sub.warn{color:#8a4b00}
.pc-panel label{display:flex;gap:8px;align-items:center;padding:3px 0;cursor:pointer}
.pc-panel label input{width:18px;height:18px;flex:none}
.pc-panel label .pp{margin-left:auto;color:var(--muted);font-size:12.5px;white-space:nowrap}
.pc-panel .mini{font:inherit;font-size:13px;padding:2px 10px;border:1px solid #999;background:#fff;border-radius:5px;cursor:pointer;margin:2px 0 0}
.pc-actions{display:flex;gap:8px;margin:14px 0 8px;flex-wrap:wrap}
.pc-actions button{font:inherit;font-weight:700;padding:9px 16px;border:2px solid #111;background:#fff;border-radius:7px;cursor:pointer}
.pc-actions button.primary{background:#111;color:#fff}
.pc-count{font-weight:700;margin:4px 0}
.pc-hint{font-size:12.5px;color:var(--muted);margin:6px 0 0}
.pc-hint li{margin:2px 0}
.pc-home{font-size:13px}
.pc-empty{background:#fff;border:1px dashed #999;border-radius:10px;padding:40px;text-align:center;color:var(--muted)}
.blk{display:none}
@media screen{
  .pc-preview .blk.on{display:block;background:#fff;box-shadow:0 1px 6px rgba(0,0,0,.18);margin:0 auto 16px;padding:14mm 15mm;width:210mm;max-width:100%;position:relative}
  .pc-preview .blk.on.d-summary{width:297mm}
  .pc-preview .blk.on::before{content:attr(data-label);position:absolute;top:-1px;right:-1px;background:var(--accent);color:#fff;font-size:12px;padding:2px 8px;border-radius:0 0 0 6px}
  .pc-preview .blk section + section,.pc-preview .blk .pb:not(:first-child){border-top:2px dashed #aaa;margin-top:10mm;padding-top:10mm}
  .pc-preview{min-width:0;overflow-x:auto}
}
@media screen and (max-width:900px){.pc-wrap{grid-template-columns:1fr}.pc-panel{position:static;max-height:none}.pc-preview .blk.on{padding:16px}}
@media print{
  body{background:#fff}
  .pc-top,.pc-panel,.pc-empty{display:none!important}
  .pc-wrap{display:block;padding:0}
  .blk.on{display:block;break-before:page;margin:0;padding:0;width:auto;box-shadow:none}
  .blk.on section,.blk.on .pb{break-before:page;padding-top:2mm}
  .blk.first,.blk.first>:first-child{break-before:auto!important}
  .blk .toolbar{display:none}
}
"""


def page_css():
    # Chromium drops SVGs onto their own pages when they sit inside a *named* page, so only the landscape summary
    # (which has no pictures) gets a named page. Everything else uses the default A4 portrait page.
    return ("@page{size:A4;margin:12.5mm 13.5mm 14mm}\n"
            "@page summary{size:A4 landscape;margin:11mm 12mm 12mm}\n"
            ".blk.d-summary{page:summary}")


def main():
    blocks = collect()
    css = (build.font_css("") + PC_CSS + page_css()
           + scope_css(build.BOOKLET_CSS, ".d-booklet") + scope_css(build.DOC_CSS, ".d-guide")
           + scope_css(build.FORM_CSS, ".d-form") + scope_css(build.SUMMARY_CSS, ".d-summary"))
    # keep summary table readable inside the landscape block
    css += "\n.d-summary .sheet{max-width:none}"

    panel = ""
    for lang in build.LANGS:
        u, L = UI[lang], LABELS[lang]

        def row(key):
            k = f"{lang}-{key}"
            pp = PC_PAGES.get(k)
            pp_txt = f'<span class="pp">{pp} {u["pages"]}</span>' if pp else ""
            return f'<label lang="{lang}"><input type="checkbox" data-k="{k}"> <span>{L[key]}</span>{pp_txt}</label>'

        panel += (f'<h2 lang="{lang}">{u["h"]}</h2><div class="sub">{u["booklet"]}</div>'
                  + "".join(row(k) for k in ("cover", "practice", "p1", "p2", "p3", "p4"))
                  + f'<button class="mini" data-preset="{lang}-booklet">{u["all"]}</button>'
                  + f'<div class="sub warn">{u["tester"]}</div>'
                  + "".join(row(k) for k in ("guide", "form", "summary")))

    body_blocks = "".join(
        f'<div class="blk d-{kind} l-{lang}" data-k="{k}" data-label="{LABELS[lang][k.split("-", 1)[1]]}" lang="{lang}">{html}</div>'
        for k, lang, kind, html in blocks)

    html = f"""<!doctype html>
<html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>เลือกพิมพ์ · Print center — Thinking and Reasoning Test</title>
<style>{css}</style></head>
<body>{DEFS}
<div class="pc-top"><h1>เลือกพิมพ์ · Print center</h1>
<p>ติ๊กเอกสารที่ต้องการ แล้วกดพิมพ์ · Tick what you need, then press Print. &nbsp;<a class="pc-home" href="index.html">← หน้าแรก / Home</a></p></div>
<div class="pc-wrap">
<aside class="pc-panel">
{panel}
<div class="pc-actions"><button class="primary" id="pc-print">🖨 พิมพ์ที่เลือก / Print selected</button><button id="pc-clear">ล้าง / Clear</button></div>
<div class="pc-count" id="pc-count"></div>
<ul class="pc-hint">
<li>Chrome หรือ Edge · กระดาษ A4 · Scale 100% · Margins Default · ปิด Headers and footers</li>
<li>Chrome or Edge · Paper A4 · Scale 100% · Margins Default · Headers and footers off</li>
<li>พิมพ์แบบทดสอบหน้าเดียว (single-sided) · ต้องการหลายชุด ให้ตั้งจำนวนสำเนา (Copies) ในหน้าต่างพิมพ์</li>
<li>Print the booklet single-sided · for several people, set Copies in the print dialog</li>
</ul>
</aside>
<main class="pc-preview">
<div class="pc-empty" id="pc-empty">ยังไม่ได้เลือกเอกสาร · Nothing selected yet — tick something on the left.</div>
{body_blocks}
</main></div>
<script>
(function(){{
  var boxes=[].slice.call(document.querySelectorAll('input[data-k]'));
  var blocks=[].slice.call(document.querySelectorAll('.blk'));
  var PAGES={json.dumps(PC_PAGES)};
  function chosen(){{return boxes.filter(function(b){{return b.checked;}}).map(function(b){{return b.dataset.k;}});}}
  function sync(){{
    var on=chosen(), first=true, pages=0;
    blocks.forEach(function(el){{
      var sel=on.indexOf(el.dataset.k)>=0;
      el.classList.toggle('on',sel);
      el.classList.toggle('first',sel&&first);
      if(sel){{first=false; pages+=PAGES[el.dataset.k]||0;}}
    }});
    document.getElementById('pc-empty').style.display=on.length?'none':'block';
    document.getElementById('pc-count').textContent=on.length?
      ('เลือก '+on.length+' รายการ'+(pages?' · ประมาณ '+pages+' หน้า':'')+' · '+on.length+' selected'+(pages?' · about '+pages+' pages':'')):'';
    try{{localStorage.setItem('pc-sel',JSON.stringify(on));}}catch(e){{}}
  }}
  boxes.forEach(function(b){{b.addEventListener('change',sync);}});
  [].slice.call(document.querySelectorAll('[data-preset]')).forEach(function(btn){{
    btn.addEventListener('click',function(){{
      var lang=btn.dataset.preset.split('-')[0];
      var keys=['cover','practice','p1','p2','p3','p4'].map(function(k){{return lang+'-'+k;}});
      var all=keys.every(function(k){{return boxes.some(function(b){{return b.dataset.k===k&&b.checked;}});}});
      boxes.forEach(function(b){{if(keys.indexOf(b.dataset.k)>=0)b.checked=!all;}});
      sync();
    }});
  }});
  document.getElementById('pc-clear').addEventListener('click',function(){{boxes.forEach(function(b){{b.checked=false;}});sync();}});
  document.getElementById('pc-print').addEventListener('click',function(){{
    if(!chosen().length){{document.getElementById('pc-count').textContent='เลือกอย่างน้อย 1 รายการก่อน · Select at least one item first';return;}}
    sync(); window.print();
  }});
  window.addEventListener('beforeprint',sync);
  var saved=null; try{{saved=JSON.parse(localStorage.getItem('pc-sel')||'null');}}catch(e){{}}
  var q=(location.hash||'').replace('#','');
  var init=q?q.split(','):(saved||['th-cover','th-practice','th-p1','th-p2','th-p3','th-p4']);
  boxes.forEach(function(b){{b.checked=init.indexOf(b.dataset.k)>=0;}});
  sync();
}})();
</script>
</body></html>"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", OUT, os.path.getsize(OUT) // 1024, "KB")
    return [b[0] for b in blocks]


if __name__ == "__main__":
    main()
