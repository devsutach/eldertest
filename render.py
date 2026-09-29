"""Render every HTML page to an A4 PDF with Chromium (print CSS) and record page counts in pages.json."""
import json
import os
import re
import subprocess

from playwright.sync_api import sync_playwright

PKG = os.path.abspath("package")
DOCS = ["1-test-booklet", "2-tester-guide", "3-record-form", "4-comparison-summary"]
pages = {}

with sync_playwright() as p:
    browser = p.chromium.launch()
    pg = browser.new_page()
    for lang in ("th", "en"):
        os.makedirs(os.path.join(PKG, "pdf", lang), exist_ok=True)
        for doc in DOCS:
            pg.goto("file://" + os.path.join(PKG, lang, doc + ".html"))
            pg.wait_for_load_state("networkidle")
            pg.evaluate("document.fonts.ready")
            fonts = pg.evaluate("[...document.fonts].filter(f=>f.status==='loaded').length")
            out = os.path.join(PKG, "pdf", lang, doc + ".pdf")
            pg.pdf(path=out, prefer_css_page_size=True, print_background=True)
            info = subprocess.run(["pdfinfo", out], capture_output=True, text=True).stdout
            n = int(re.search(r"Pages:\s+(\d+)", info).group(1))
            pages[f"{lang}/{doc}"] = n
            print(f"{lang}/{doc}: {n} pages, {fonts} font faces loaded")
    browser.close()

json.dump(pages, open("pages.json", "w"), indent=1)
