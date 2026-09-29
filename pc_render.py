"""Measure how many A4 pages each print-center item takes (writes pc_pages.json) and sanity-check combinations."""
import json, os, re, subprocess, sys
from playwright.sync_api import sync_playwright

PC = "file://" + os.path.abspath("package/print.html")
KEYS = [f"{l}-{k}" for l in ("th", "en") for k in ("cover", "practice", "p1", "p2", "p3", "p4", "guide", "form", "summary")]
KEYS += ["L:" + k for k in KEYS if k.split("-")[1] in ("cover", "practice", "p1", "p2", "p3", "p4")]
tmp = sys.argv[1] if len(sys.argv) > 1 else "/tmp"


def pages(pdf):
    out = subprocess.run(["pdfinfo", "-f", "1", "-l", "999", pdf], capture_output=True, text=True).stdout
    n = int(re.search(r"Pages:\s+(\d+)", out).group(1))
    sizes = re.findall(r"Page\s+\d+ size:\s+([\d.]+) x ([\d.]+)", out)
    return n, sizes


res, checks = {}, {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for k in KEYS + ["COMBO_TH_BOOKLET", "COMBO_EN_BOOKLET", "COMBO_TH_LARGE", "COMBO_EN_LARGE", "COMBO_MIX"]:
        sel = {"COMBO_TH_BOOKLET": "th-cover,th-practice,th-p1,th-p2,th-p3,th-p4",
               "COMBO_EN_BOOKLET": "en-cover,en-practice,en-p1,en-p2,en-p3,en-p4",
               "COMBO_TH_LARGE": "large,th-cover,th-practice,th-p1,th-p2,th-p3,th-p4",
               "COMBO_EN_LARGE": "large,en-cover,en-practice,en-p1,en-p2,en-p3,en-p4",
               "COMBO_MIX": "th-p4,th-form,th-summary"}.get(k, k.replace("L:", "large,"))
        ctx = b.new_context()
        pg = ctx.new_page()
        pg.goto(PC + "#" + sel)
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        out = os.path.join(tmp, f"pc_{k.replace(':', '_')}.pdf")
        pg.pdf(path=out, prefer_css_page_size=True, print_background=True)
        n, sizes = pages(out)
        if k in KEYS:
            res[k] = n
        elif k in ("COMBO_TH_BOOKLET", "COMBO_EN_BOOKLET", "COMBO_TH_LARGE", "COMBO_EN_LARGE"):
            res[{"COMBO_TH_BOOKLET": "th-booklet", "COMBO_EN_BOOKLET": "en-booklet",
                 "COMBO_TH_LARGE": "L:th-booklet", "COMBO_EN_LARGE": "L:en-booklet"}[k]] = n
        else:
            checks[k] = (n, sorted(set(sizes)))
        ctx.close()
    b.close()
json.dump(res, open("pc_pages.json", "w"), indent=1)
print(res)
print(checks)
