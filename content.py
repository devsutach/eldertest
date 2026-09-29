"""Single source of truth for both language versions: every item, its options, key, scale and error notes.

`build(lang)` returns the items for "th" or "en". Keys, figures and option ORDER are identical in both
languages, so an answer position (ก = A, ข = B, ค = C, ง = D) means the same thing in either booklet.
"""
from figs import (inline_shape, seq, grid, single, c_n, c_shapes, c_arrow, c_num, c_dot_arrow, CORNERS, shape,
                  houses_figure, bar_chart, walk_figure, clock_face, icon, svg, text, cell_frame, qmark)

LETTERS = {"th": ["ก", "ข", "ค", "ง"], "en": ["A", "B", "C", "D"]}


def pic(f, W=90, H=90, mm=22):
    return single(f, W, H, mm)


def T(*opts):
    return {"kind": "text", "opts": list(opts)}


def P(*opts, cols=4):
    return {"kind": "pic", "opts": list(opts), "cols": cols}


S = 26  # default shape size in 100-unit cells


def strip(cells, label=None, W=60, lab_w=0):
    """6-cell strip for item 39. cells: list of 'dot' | 'star' | '' | '?'."""
    body = ""
    if label is not None:
        body += text(lab_w / 2, 40, label, size=22, weight=700)
    for i, c in enumerate(cells):
        x = lab_w + i * W
        body += cell_frame(x + 1, 1, W - 2, 58)
        if c == "dot":
            body += shape("circle", x + W / 2, 30, 16)
        elif c == "star":
            body += shape("star", x + W / 2, 31, 15)
        elif c == "?":
            body += qmark(x + W / 2, 30, 32)
    return body


def fig39(row_word):
    rows = [["dot", "", "", "", "", "star"], ["", "dot", "", "", "star", ""], ["", "", "dot", "star", "", ""], ["?"] * 6]
    body = "".join(text(80 + i * 60 + 30, 20, str(i + 1), size=18, weight=700) for i in range(6))
    for r, row in enumerate(rows):
        body += f'<g transform="translate(0,{28 + r * 64})">' + strip(row, f"{row_word} {r + 1}", lab_w=80) + "</g>"
    return svg(80 + 360, 28 + 4 * 64, body, 112)


def opt39(cells):
    nums = "".join(text(i * 60 + 30, 18, str(i + 1), size=16) for i in range(6))
    return svg(360, 86, nums + '<g transform="translate(0,26)">' + strip(cells) + "</g>", 76)


def fig43_cell(i, j):
    shapes = ["circle", "triangle", "square"]
    fills = ["black", "white", "stripe"]
    return c_n(shapes[(i + j) % 3], j + 1, fills[(i + 2 * j) % 3], s=15, gap=9)


ANG = [0, 270, 180, 90]  # up, left, down, right (counter-clockwise order)


def fig45_cell(i, j):
    return c_dot_arrow(CORNERS[(i + j) % 4], ANG[(2 * i + j) % 4])


def pair(*ks, s=15):
    return c_shapes([(k, "black") for k in ks], s=s, gap=8)


def series(*vals):
    return "<div class='series'>" + ",&ensp;".join(str(v) for v in vals) + "</div>"


def build(lang):
    en = lang == "en"

    def t(th, eng):
        return eng if en else th

    Q = t("อะไรควรอยู่ในช่อง ?", "What belongs in the ?&nbsp;box?")
    NEXT = t("ตัวเลขถัดไปคืออะไร", "What number comes next?")
    FACTS = t("ข้อเท็จจริง:", "Facts:")
    WHICH = t("ข้อใดถูกต้อง", "Which statement is correct?")
    baht = t(" บาท", " baht")

    practice = [
        dict(n=t("ตัวอย่าง 1", "Practice 1"),
             stem=t("นก : บิน &nbsp;=&nbsp; ปลา : ?<div class='hint'>(นกคู่กับบิน ปลาคู่กับอะไรแบบเดียวกัน)</div>",
                    "bird : fly &nbsp;=&nbsp; fish : ?<div class='hint'>(A bird flies. What does a fish do?)</div>"),
             **T(*t(("น้ำ", "ว่าย", "เกล็ด", "ทะเล"), ("water", "swim", "scales", "sea"))), key=1),
        dict(n=t("ตัวอย่าง 2", "Practice 2"), stem=NEXT, fig=series(1, 2, 3, 4, "?"), **T("5", "6", "7", "8"), key=0),
        dict(n=t("ตัวอย่าง 3", "Practice 3"), stem=Q,
             fig=grid([[c_n("circle", 1, s=22)] * 3, [c_n("triangle", 1, s=22)] * 3,
                       [c_n("square", 1, s=22), c_n("square", 1, s=22), None]], 100, 90, 60),
             **P(*[pic(c_n(k, 1, s=22), mm=16) for k in ("circle", "triangle", "square", "star")]), key=2),
        dict(n=t("ตัวอย่าง 4", "Practice 4"),
             stem=FACTS + t("<div class='facts'>• สุนัขทุกตัวมีสี่ขา<br>• เจ้าด่างเป็นสุนัข</div>",
                            "<div class='facts'>• All dogs have four legs.<br>• Spot is a dog.</div>") + WHICH,
             **T(*t(("เจ้าด่างมีสี่ขา", "เจ้าด่างมีสองขา", "สัตว์สี่ขาทุกตัวเป็นสุนัข", "ข้อมูลไม่พอจะบอกได้"),
                    ("Spot has four legs.", "Spot has two legs.", "Every four-legged animal is a dog.", "There is not enough information to tell."))),
             key=0),
    ]

    s1 = [
        dict(n=1, scale="K", stem=t("ร้อน : เย็น &nbsp;=&nbsp; สูง : ?", "hot : cold &nbsp;=&nbsp; high : ?"),
             **T(*t(("ใหญ่", "ยาว", "ต่ำ", "หนัก"), ("big", "long", "low", "heavy"))), key=2),
        dict(n=2, scale="K", stem=t("หมอ : โรงพยาบาล &nbsp;=&nbsp; ครู : ?", "doctor : hospital &nbsp;=&nbsp; teacher : ?"),
             **T(*t(("โรงเรียน", "นักเรียน", "หนังสือ", "ชอล์ก"), ("school", "student", "book", "chalk"))), key=0,
             err=("ข = เลือกสิ่งที่เกี่ยวข้อง แทนที่จะดูความสัมพันธ์", "B = picked an association instead of the relation")),
        dict(n=3, scale="K",
             stem=t("สำนวน “เข้าเมืองตาหลิ่ว ต้องหลิ่วตาตาม” หมายความว่าอย่างไร",
                    "What does the saying “When in Rome, do as the Romans do” mean?"),
             **T(*t(("ควรเชื่อฟังและทำตามคำสั่งของผู้ใหญ่เสมอ", "ควรปรับตัวตามธรรมเนียมของถิ่นที่ไปอยู่",
                     "ควรระวังตัวเมื่อต้องอยู่กับคนแปลกหน้า", "อย่าเชื่อทุกสิ่งที่ได้เห็นด้วยตาตัวเอง"),
                    ("Always obey and follow the orders of your elders.", "Adapt to the customs of the place where you are.",
                     "Be careful when you are among strangers.", "Don’t believe everything you see with your own eyes."))), key=1),
        dict(n=4, scale="K",
             stem=t("คำว่า <b>“ถี่ถ้วน”</b> มีความหมายใกล้เคียงกับข้อใดมากที่สุด",
                    "Which is closest in meaning to the word <b>“thorough”</b>?"),
             **T(*t(("บ่อยครั้งสม่ำเสมอ", "เข้มงวดกวดขัน", "รวดเร็วฉับไว", "ละเอียดรอบคอบ"),
                    ("passing from one side to the other", "strict and demanding", "quick and efficient", "careful and complete"))),
             key=3, err=("ก = หลงตามเสียงของคำว่า “ถี่”", "A = sound-alike lure (TH: ถี่ “frequent”; EN: “through”)")),
        dict(n=5, scale="VR",
             stem=t("เพื่อน 4 คนชื่อ แดง ดำ ขาว และเขียว มาถึงงานเลี้ยงไม่พร้อมกัน "
                    "แดงมาถึงก่อนดำ แต่มาถึงหลังขาว ส่วนเขียวมาถึงหลังดำ ใครมาถึง<b>เป็นคนที่สอง</b>",
                    "Four friends — Ben, Lucy, Sara and Tom — arrived at a party at different times. "
                    "Ben arrived before Lucy but after Sara. Tom arrived after Lucy. Who arrived <b>second</b>?"),
             **T(*t(("เขียว", "แดง", "ขาว", "ดำ"), ("Tom", "Ben", "Sara", "Lucy"))), key=1,
             err=("ค = เลือกคนที่มาถึงคนแรก ลืมว่าถาม “คนที่สอง”", "C = picked the first arrival and lost “second”")),
        dict(n=6, scale="VR", stem=t("ภัยแล้ง : น้ำ &nbsp;=&nbsp; ความอดอยาก : ?", "drought : water &nbsp;=&nbsp; famine : ?"),
             **T(*t(("ความหิว", "ความยากจน", "อาหาร", "ฝน"), ("hunger", "poverty", "food", "rain"))), key=2,
             err=("ก = เลือกผลที่ตามมา ไม่ใช่ “สิ่งที่ขาด”", "A = picked a consequence, not “what is lacking”")),
        dict(n=7, scale="K",
             stem=t("คำว่า <b>“ผลีผลาม”</b> มีความหมายใกล้เคียงกับข้อใดมากที่สุด",
                    "Which is closest in meaning to the word <b>“rash”</b> (as in “a rash decision”)?"),
             **T(*t(("รีบร้อนทำโดยไม่ไตร่ตรอง", "ร่ำรวยขึ้นอย่างรวดเร็ว", "ขี้อายไม่กล้าแสดงออก", "ร่าเริงแจ่มใสและยิ้มแย้มอยู่เสมอ"),
                    ("hasty and careless", "harsh and unkind", "slow and cautious", "sad and regretful"))),
             key=0),
        dict(n=8, scale="K",
             stem=t("สำนวน “ขี่ช้างจับตั๊กแตน” หมายความว่าอย่างไร",
                    "What does the expression “to use a sledgehammer to crack a nut” mean?"),
             **T(*t(("ผู้มีอำนาจมากรังแกผู้ที่อ่อนแอกว่าตน", "ทำงานเล็กให้สำเร็จก่อน แล้วค่อยทำงานใหญ่",
                     "พยายามทำสิ่งที่เกินกว่าความสามารถของตน", "ลงทุนลงแรงมาก แต่ได้ผลเพียงเล็กน้อย"),
                    ("The powerful bullying those who are weaker.", "Finishing small jobs first, then the big ones.",
                     "Trying to do something beyond your ability.", "Using far too much effort for a small result."))), key=3,
             err=("ก = ตีความตามตัวอักษรว่า “ใหญ่รังแกเล็ก”", "A = literal “big versus small” reading")),
        dict(n=9, scale="VR",
             stem=t("ข้อใดมีความสัมพันธ์แบบเดียวกับ &nbsp;<b>หนอน : ผีเสื้อ</b>",
                    "Which pair has the same relationship as &nbsp;<b>caterpillar : butterfly</b>?"),
             **T(*t(("น้ำผึ้ง : ผึ้ง", "ลูกอ๊อด : กบ", "รัง : นก", "อุ้งเท้า : สุนัข"),
                    ("honey : bee", "tadpole : frog", "nest : bird", "paw : dog"))), key=1,
             err=("ก / ค / ง = เลือกความสัมพันธ์คนละแบบ (ผลผลิต ที่อยู่ ส่วนของร่างกาย) ไม่ใช่ “ช่วงชีวิต”",
                  "A / C / D = a different kind of relation (product, home, body part), not a life stage")),
        dict(n=10, scale="K",
             stem=t("คำว่า <b>“ตระหนัก”</b> มีความหมายใกล้เคียงกับข้อใดมากที่สุด",
                    "Which is closest in meaning to the word <b>“eminent”</b>?"),
             **T(*t(("ตกใจกลัว", "หนักแน่นมั่นคง", "รู้ชัดแจ้ง", "ขยันขันแข็ง"),
                    ("about to happen", "firm and steady", "famous and respected", "hard-working"))), key=2,
             err=("ก = สับสนระหว่าง ตระหนัก กับ ตระหนก", "A = look-alike word (TH: ตระหนก; EN: “imminent”)")),
        dict(n=11, scale="VR", group="g11",
             intro=t("<div class='lead'>อ่านข้อความต่อไปนี้ แล้วตอบข้อ 11–12</div><blockquote>จากการศึกษาหนึ่ง โดยเฉลี่ยแล้ว "
                     "ผู้ที่ดื่มกาแฟวันละ 2–3 แก้ว มีอายุยืนกว่าผู้ที่ไม่ดื่มกาแฟ อย่างไรก็ตาม ผู้ที่ดื่มกาแฟในการศึกษานี้มักมีรายได้สูงกว่า "
                     "และออกกำลังกายสม่ำเสมอกว่าผู้ที่ไม่ดื่มด้วย นักวิจัยจึงยังสรุปไม่ได้ว่ากาแฟทำให้อายุยืนขึ้นจริง</blockquote>",
                     "<div class='lead'>Read the passage, then answer questions 11–12.</div><blockquote>In one study, people who drank "
                     "2–3 cups of coffee a day lived longer, on average, than people who did not drink coffee. However, the coffee "
                     "drinkers in this study also tended to have higher incomes and to exercise more regularly than the non-drinkers. "
                     "So the researchers could not yet conclude that coffee really makes people live longer.</blockquote>"),
             stem=t("ข้อใดสรุปได้ถูกต้องที่สุดจากข้อความนี้", "Which conclusion is best supported by the passage?"),
             **T(*t(("คนดื่มกาแฟอายุยืนกว่า อาจเป็นเพราะรายได้หรือการออกกำลังกาย", "การดื่มกาแฟวันละ 2–3 แก้ว ช่วยให้คนเราอายุยืนขึ้นได้จริง",
                     "การดื่มกาแฟเกินวันละ 3 แก้ว อาจทำให้คนเราอายุสั้นลงได้", "การออกกำลังกายสม่ำเสมอ ไม่มีผลใดๆ ต่ออายุของคนเรา"),
                    ("Coffee drinkers may live longer because of their income or exercise.",
                     "Drinking 2–3 cups of coffee a day really does make people live longer.",
                     "Drinking more than 3 cups a day may make people’s lives shorter.",
                     "Regular exercise has no effect at all on how long people live."))), key=0,
             err=("ข = ถือว่าความสัมพันธ์คือสาเหตุ", "B = took correlation as causation")),
        dict(n=12, scale="VR", group="g11",
             stem=t("ถ้าต้องการรู้ว่ากาแฟทำให้อายุยืนจริงหรือไม่ ควรเปรียบเทียบระหว่างคนกลุ่มใด",
                    "To find out whether coffee really makes people live longer, which groups should be compared?"),
             **T(*t(("คนดื่มกาแฟที่รายได้สูง กับคนไม่ดื่มกาแฟที่รายได้ต่ำ", "คนที่ออกกำลังกายเป็นประจำ กับคนที่ไม่ได้ออกกำลังกายเลย",
                     "คนดื่มกับไม่ดื่มกาแฟ ที่รายได้และการออกกำลังกายใกล้เคียงกัน", "คนที่ดื่มกาแฟวันละ 2 แก้ว กับคนที่ดื่มกาแฟวันละ 3 แก้ว"),
                    ("High-income coffee drinkers and low-income non-drinkers.", "People who exercise regularly and people who never exercise.",
                     "Coffee drinkers and non-drinkers with similar income and exercise.",
                     "People who drink 2 cups a day and people who drink 3 cups a day."))), key=2),
        dict(n=13, scale="VR",
             stem=FACTS + t("<div class='facts'>• นักดนตรีทุกคนในวงนี้อ่านโน้ตเพลงได้<br>• สมศักดิ์อ่านโน้ตเพลงได้</div>",
                            "<div class='facts'>• Every musician in this band can read music.<br>• Sam can read music.</div>") + WHICH,
             **T(*t(("สมศักดิ์เป็นนักดนตรีคนหนึ่งในวงนี้แน่นอน", "ข้อมูลไม่พอจะบอกว่าสมศักดิ์อยู่ในวงนี้หรือไม่",
                     "สมศักดิ์ไม่ได้เป็นนักดนตรีในวงนี้แน่นอน", "ทุกคนที่อ่านโน้ตได้เป็นนักดนตรีในวงนี้"),
                    ("Sam is definitely one of the musicians in this band.", "There is not enough information to tell.",
                     "Sam is definitely not a musician in this band.", "Everyone who can read music plays in this band."))), key=1,
             err=("ก = สรุปย้อนกลับ (affirming the consequent)", "A = affirming the consequent")),
        dict(n=14, scale="VR",
             stem=FACTS + t("<div class='facts'>• ทุกคนที่ได้รางวัล ส่งผลงานก่อนกำหนด<br>• มานีไม่ได้ส่งผลงานก่อนกำหนด</div>",
                            "<div class='facts'>• Everyone who won a prize handed in their work early.<br>• Mary did not hand in her work early.</div>")
             + WHICH,
             **T(*t(("มานีได้รางวัลอย่างแน่นอน", "ข้อมูลไม่พอที่จะสรุปได้", "คนที่ส่งก่อนกำหนดได้รางวัลทุกคน", "มานีไม่ได้รางวัลอย่างแน่นอน"),
                    ("Mary definitely won a prize.", "There is not enough information to tell.",
                     "Everyone who handed in early won a prize.", "Mary definitely did not win a prize."))), key=3,
             err=("ข = ระวังเกินไป (ตอบ “สรุปไม่ได้” ทุกครั้ง)", "B = over-caution (“cannot conclude” everywhere)")),
        dict(n=15, scale="VR",
             stem=t("บ้าน 5 หลังเรียงกันเป็นแถวจากซ้ายไปขวา เจ้าของคือ แก้ว นิด ป้อม หน่อย และอ้อย (ไม่ได้เรียงตามนี้)"
                    "<div class='facts'>• บ้านของแก้วอยู่ซ้ายสุด<br>• บ้านของนิดอยู่ตรงกลาง<br>• บ้านของป้อมอยู่ติดกับบ้านของนิด<br>"
                    "• บ้านของอ้อยอยู่ทางซ้ายของบ้านของหน่อย (ไม่จำเป็นต้องติดกัน)</div>",
                    "Five houses stand in a row from left to right. Their owners are Kate, Nick, Pam, Nora and Olivia (listed in no particular order)."
                    "<div class='facts'>• Kate’s house is at the far left.<br>• Nick’s house is in the middle.<br>"
                    "• Pam’s house is next to Nick’s.<br>• Olivia’s house is somewhere to the left of Nora’s (not necessarily next to it).</div>"),
             fig=houses_figure(lang), stem2=t("ข้อใด<b>ต้องเป็นจริงเสมอ</b>", "Which statement <b>must</b> be true?"),
             **T(*t(("บ้านของหน่อยอยู่ขวาสุด", "บ้านของป้อมเป็นหลังที่ 2 นับจากซ้าย", "บ้านของอ้อยอยู่ติดกับบ้านของแก้ว",
                     "บ้านของป้อมอยู่ติดกับบ้านของหน่อย"),
                    ("Nora’s house is at the far right.", "Pam’s house is 2nd from the left.", "Olivia’s house is next to Kate’s.",
                     "Pam’s house is next to Nora’s."))), key=0),
    ]

    table = (t("<div class='lead'>ดูตารางและกราฟต่อไปนี้ แล้วตอบข้อ 23–24</div>",
               "<div class='lead'>Look at the table and chart, then answer questions 23–24.</div>")
             + "<div class='datafig'><table class='data'><caption>"
             + t("ยอดขายของร้านข้าวแกงแห่งหนึ่ง", "Sales of a small rice-and-curry shop") + "</caption><tr><th>"
             + t("เดือน", "Month") + "</th><th>" + t("ยอดขาย (บาท)", "Sales (baht)") + "</th></tr>"
             + "".join(f"<tr><td>{m}</td><td>{v}</td></tr>" for m, v in zip(
                 t(("มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน"), ("January", "February", "March", "April")),
                 ("20,000", "30,000", "42,000", "38,000")))
             + "</table>" + bar_chart(lang) + "</div>")

    s2 = [
        dict(n=16, scale="N",
             stem=t("ซื้อของ 3 อย่าง ราคา 45 บาท 30 บาท และ 25 บาท จ่ายด้วยธนบัตร 500 บาท จะได้เงินทอนเท่าไร",
                    "You buy three items costing 45, 30 and 25&nbsp;baht, and pay with a 500&#8209;baht note. How much change do you get?"),
             **T(*[f"{v}{baht}" for v in (375, 400, 425, 450)]), key=1),
        dict(n=17, scale="N", stem=NEXT, fig=series(2, 5, 8, 11, "?"), **T("12", "13", "14", "17"), key=2),
        dict(n=18, scale="N", stem=t("เสื้อราคา 400 บาท ลดราคา 25% ต้องจ่ายเงินเท่าไร",
                                     "A shirt normally costs 400 baht. It is on sale at 25% off. How much do you pay?"),
             **T(*[f"{v}{baht}" for v in (100, 250, 300, 375)]), key=2,
             err=("ก = ตอบจำนวนส่วนลด; ง = ลบออก 25 บาท", "A = gave the discount itself; D = subtracted 25 baht")),
        dict(n=19, scale="N", stem=NEXT, fig=series(1, 4, 9, 16, 25, "?"), **T("30", "34", "35", "36"), key=3,
             err=("ข = ใช้ผลต่างเดิมซ้ำ", "B = repeated the last difference")),
        dict(n=20, scale="N",
             stem=t("รถวิ่งด้วยความเร็ว 60 กิโลเมตรต่อชั่วโมง ถ้าเดินทางเป็นระยะทาง 150 กิโลเมตร จะใช้เวลานานเท่าไร",
                    "A car travels at 60 kilometres per hour. How long does it take to travel 150 kilometres?"),
             **T(*t(("2 ชั่วโมง", "2 ชั่วโมง 15 นาที", "2 ชั่วโมง 30 นาที", "2 ชั่วโมง 50 นาที"),
                    ("2 hours", "2 hours 15 minutes", "2 hours 30 minutes", "2 hours 50 minutes"))), key=2,
             err=("ง = อ่าน 2.5 ชั่วโมงเป็น 2 ชั่วโมง 50 นาที", "D = read 2.5 hours as 2 h 50 min")),
        dict(n=21, scale="N",
             stem=t("ผสมน้ำหวานเข้มข้น 1 ส่วน กับน้ำเปล่า 4 ส่วน ถ้าต้องการน้ำหวานที่ผสมแล้วทั้งหมด 1,000 มิลลิลิตร "
                    "ต้องใช้น้ำหวานเข้มข้นกี่มิลลิลิตร",
                    "You mix 1 part syrup with 4 parts water. To make 1,000 millilitres of the mixed drink in total, "
                    "how much syrup do you need?"),
             **T(*[f"{v} {t('มิลลิลิตร', 'millilitres')}" for v in (200, 250, 400, 800)]), key=0,
             err=("ข = คิด 1/4 ของทั้งหมด", "B = took 1/4 of the total")),
        dict(n=22, scale="N", stem=NEXT, fig=series(2, 3, 5, 8, 12, 17, "?"), **T("20", "21", "22", "23"), key=3,
             err=("ค = บวก 5 ซ้ำ", "C = repeated +5")),
        dict(n=23, scale="N", group="g23", intro=table,
             stem=t("ยอดขายเฉลี่ยต่อเดือน (ทั้ง 4 เดือน) เท่ากับเท่าไร", "What were the average monthly sales over the 4 months?"),
             **T(*[f"{v}{baht}" for v in ("26,000", "30,000", "32,000", "32,500")]), key=3,
             err=("ก = หารด้วย 5; ค = คำนวณพลาด", "A = divided by 5; C = arithmetic slip")),
        dict(n=24, scale="N", group="g23",
             stem=t("เดือนใดมียอดขายเพิ่มขึ้นจากเดือนก่อนหน้า <b>คิดเป็นร้อยละ (เปอร์เซ็นต์)</b> มากที่สุด",
                    "Which month had the largest <b>percentage</b> increase over the month before?"),
             **T(*t(("กุมภาพันธ์", "มีนาคม", "เมษายน", "กุมภาพันธ์และมีนาคมเพิ่มขึ้นเท่ากัน"),
                    ("February", "March", "April", "February and March rose by the same percentage"))), key=0,
             err=("ข = ดูยอดเพิ่มเป็นบาท ไม่ใช่ร้อยละ", "B = largest rise in baht, not in %")),
        dict(n=25, scale="N",
             stem=t("ปัจจุบันพ่ออายุเป็น 3 เท่าของลูก อีก 12 ปีข้างหน้า พ่อจะอายุเป็น 2 เท่าของลูก ปัจจุบันลูกอายุเท่าไร",
                    "A father is now 3 times as old as his son. In 12 years he will be twice as old as his son. How old is the son now?"),
             **T(*[f"{v} {t('ปี', 'years')}" for v in (12, 18, 24, 36)]), key=0,
             err=("ค = อายุลูกในอีก 12 ปี; ง = อายุพ่อตอนนี้", "C = son’s age in 12 years; D = father’s age now")),
        dict(n=26, scale="N",
             stem=t("งานชิ้นหนึ่ง ถ้าสมชายทำคนเดียวจะเสร็จใน 6 ชั่วโมง ถ้าสมหญิงทำคนเดียวจะเสร็จใน 3 ชั่วโมง "
                    "ถ้าทั้งสองคนช่วยกันทำ จะเสร็จในกี่ชั่วโมง",
                    "Adam can finish a job alone in 6 hours. Beth can finish the same job alone in 3 hours. "
                    "If they work on it together, how long will it take?"),
             **T(*t(("1 ชั่วโมงครึ่ง", "2 ชั่วโมง", "4 ชั่วโมงครึ่ง", "9 ชั่วโมง"), ("1½ hours", "2 hours", "4½ hours", "9 hours"))), key=1,
             err=("ค = เฉลี่ยเวลา; ง = บวกเวลา", "C = averaged the times; D = added them")),
        dict(n=27, scale="N",
             stem=t("สินค้าชิ้นหนึ่ง ขึ้นราคา 20% ต่อมาลดราคาลง 20% (คิดจากราคาใหม่) ราคาสุดท้ายเป็นอย่างไรเมื่อเทียบกับราคาเดิม",
                    "A price goes up by 20%, then comes down by 20% (of the new price). Compared with the original price, the final price is:"),
             **T(*t(("เท่ากับราคาเดิม", "ถูกกว่าราคาเดิม 20%", "แพงกว่าราคาเดิม 4%", "ถูกกว่าราคาเดิม 4%"),
                    ("the same as the original", "20% lower than the original", "4% higher than the original", "4% lower than the original"))),
             key=3, err=("ก = คิดว่า +20% กับ −20% หักล้างกัน", "A = assumed +20% and −20% cancel out")),
        dict(n=28, scale="N",
             stem=t("ห้องเรียนหนึ่งมีนักเรียน 30 คน เป็นชาย 12 คน และหญิง 18 คน คะแนนเฉลี่ยของนักเรียนชายคือ 60 คะแนน "
                    "ส่วนคะแนนเฉลี่ยของทั้งห้องคือ 66 คะแนน คะแนนเฉลี่ยของนักเรียนหญิงเท่ากับเท่าไร",
                    "A class has 30 students: 12 boys and 18 girls. The boys’ average score is 60, and the average for the whole class is 66. "
                    "What is the girls’ average score?"),
             **T(*[f"{v} {t('คะแนน', 'points')}" for v in (68, 70, 72, 76)]), key=1,
             err=("ค = บวกส่วนต่างสะท้อนกลับ (66 + 6)", "C = mirrored the gap (66 + 6)")),
        dict(n=29, scale="N",
             stem=t("เดินจากบ้านไปวัดด้วยความเร็ว 4 กิโลเมตรต่อชั่วโมง แล้วเดินกลับบ้านทางเดิมด้วยความเร็ว 6 กิโลเมตรต่อชั่วโมง",
                    "You walk from home to the temple at 4 kilometres per hour, then walk back home the same way at 6 kilometres per hour."),
             fig=walk_figure(lang),
             stem2=t("ถ้าคิดตลอดการเดินทั้งไปและกลับ โดยเฉลี่ยแล้วเดินได้ชั่วโมงละกี่กิโลเมตร",
                     "What was your average speed over the whole trip, there and back?"),
             **T(*[f"{v} {t('กิโลเมตร', 'km/h')}" for v in ("4.4", "4.5", "4.8", "5.0")]), key=2,
             err=("ง = เฉลี่ยความเร็วสองค่า (กับดักคลาสสิก)", "D = averaged the two speeds (classic trap)")),
        dict(n=30, scale="N",
             stem=t("เมื่อนาฬิกาบอกเวลา 15.30 น. (บ่ายสามโมงครึ่ง) เข็มสั้นกับเข็มยาวทำมุมกันกี่องศา (ให้ตอบมุมที่เล็กกว่า)",
                    "When a clock shows 3:30 in the afternoon, what is the angle between the hour hand and the minute hand? "
                    "(Give the smaller angle.)"),
             fig="<div class='figcap'>" + clock_face(lang) + "<span>" + t("รูปหน้าปัดนาฬิกา (ไม่มีเข็ม)", "Clock face (hands not shown)")
                 + "</span></div>",
             **T(*[f"{v} {t('องศา', 'degrees')}" for v in (60, 75, 90, 105)]), key=1,
             err=("ค = ลืมว่าเข็มสั้นเคลื่อนด้วย", "C = forgot that the hour hand moves")),
    ]

    s3 = [
        dict(n=31, scale="P", stem=Q,
             fig=seq([c_n("ocircle", 1, s=S), c_n("circle", 1, s=S)] * 2 + [c_n("ocircle", 1, s=S), None], 90, 90, 132),
             **P(pic(c_n("triangle", 1, s=S)), pic(c_n("ocircle", 1, s=S)), pic(c_n("square", 1, s=S)), pic(c_n("circle", 1, s=S))), key=3),
        dict(n=32, scale="P", stem=Q,
             fig=seq([c_n(k, 1, s=24) for k in ("triangle", "square", "circle", "triangle", "square", "circle", "triangle")] + [None],
                     80, 80, 158),
             **P(*[pic(c_n(k, 1, s=S)) for k in ("square", "triangle", "circle", "star")]), key=0),
        dict(n=33, scale="P", stem=t("ลูกศรถัดไปคืออะไร", "Which arrow comes next?"),
             fig=seq([c_arrow(a) for a in (0, 90, 180, 270, 0)] + [None], 90, 90, 132),
             **P(*[pic(c_arrow(a)) for a in (0, 180, 90, 270)]), key=2),
        dict(n=34, scale="P", stem=t("วันต่อไปในลำดับนี้ (ช่อง ?) คือวันอะไร", "Which day comes next in this sequence?"),
             fig="<div class='series'>" + t("จันทร์ &nbsp;→&nbsp; พุธ &nbsp;→&nbsp; ศุกร์ &nbsp;→&nbsp; ?",
                                            "Monday &nbsp;→&nbsp; Wednesday &nbsp;→&nbsp; Friday &nbsp;→&nbsp; ?") + "</div>",
             **T(*t(("เสาร์", "อาทิตย์", "พฤหัสบดี", "พุธ"), ("Saturday", "Sunday", "Thursday", "Wednesday"))), key=1),
        dict(n=35, scale="P", stem=t("ข้อใด<b>ไม่เข้าพวก</b>", "Which one does <b>not</b> belong with the others?"),
             **P(*[icon(k) + f"<div class='iconlab'>{lab}</div>" for k, lab in zip(
                 ("ruler", "scissors", "clock", "scale"),
                 t(("ไม้บรรทัด", "กรรไกร", "นาฬิกา", "ตาชั่ง"), ("ruler", "scissors", "clock", "scales")))]), key=1),
        dict(n=36, scale="P", stem=Q,
             fig=grid([[c_n("circle", k, s=12, gap=6) for k in (1, 2, 3)], [c_n("triangle", k, s=12, gap=6) for k in (2, 3, 4)],
                       [c_n("square", 3, s=12, gap=6), c_n("square", 4, s=12, gap=6), None]], 200, 78, 126),
             **P(*[single(c_n(k, n, s=12, gap=6), 200, 78, 38) for k, n in
                   (("square", 4), ("triangle", 5), ("square", 5), ("triangle", 6))]),
             key=2, err=("ข = จำนวนถูกแต่รูปผิด", "B = right count, wrong shape")),
        dict(n=37, scale="P", stem=Q,
             fig=grid([[c_n(k, 1, s=S) for k in r] for r in (("circle", "triangle", "square"), ("triangle", "square", "circle"))]
                      + [[c_n("square", 1, s=S), c_n("circle", 1, s=S), None]], 100, 90, 78),
             **P(*[pic(c_n(k, 1, s=S)) for k in ("triangle", "circle", "square", "star")]), key=0),
        dict(n=38, scale="P", stem=Q,
             fig=grid([[c_num(v) for v in (2, 3, 6)], [c_num(v) for v in (4, 2, 8)], [c_num(5), c_num(3), None]], 100, 80, 78),
             **T("8", "13", "15", "18"), key=2, err=("ก = บวกแทนการคูณ", "A = added instead of multiplied")),
        dict(n=39, scale="P",
             stem=t("ดูการเคลื่อนที่ของ " + inline_shape("circle") + " และ " + inline_shape("star")
                    + " ในแถว 1 ถึง 3 แล้วเลือกว่าแถวที่ 4 ควรเป็นแบบใด",
                    "Look at how the " + inline_shape("circle") + " and the " + inline_shape("star")
                    + " move in rows 1 to 3. Which option shows row 4?"),
             fig=fig39(t("แถว", "Row")),
             **P(opt39(["", "", "star", "dot", "", ""]), opt39(["", "star", "", "dot", "", ""]),
                 opt39(["", "", "dot", "", "star", ""]), opt39(["", "", "", "dot", "star", ""]), cols=2), key=0),
        dict(n=40, scale="P", stem=NEXT, fig=series(1, 10, 3, 9, 5, 8, 7, 7, "?"), **T("6", "7", "8", "9"), key=3,
             err=("ก = ต่อลำดับผิดชุด", "A = continued the wrong sub-sequence")),
        dict(n=41, scale="P",
             stem=t("ดูข้อมูลในตาราง แล้วตอบว่า <b>5 # 2</b> เท่ากับเท่าไร", "Look at the table. What is <b>5 # 2</b>?"),
             fig=("<table class='data op'><tr><th>" + t("ข้อมูล", "Given") + "</th><th>" + t("ผลลัพธ์", "Result")
                  + "</th></tr><tr><td>2 # 3</td><td>13</td></tr><tr><td>4 # 1</td><td>17</td></tr><tr><td>3 # 3</td><td>18</td></tr>"
                    "<tr><td><b>5 # 2</b></td><td><b>?</b></td></tr></table>"),
             **T("27", "29", "49", "100"), key=1, err=("ก = a² + b; ค = (a + b)²; ง = (a × b)²",) * 2),
        dict(n=42, scale="P", stem=Q,
             fig=grid([[c_n("circle", 1, s=13), c_n("triangle", 2, s=13), c_n("square", 3, s=13)],
                       [c_n("triangle", 3, s=13), c_n("square", 1, s=13), c_n("circle", 2, s=13)],
                       [c_n("square", 2, s=13), c_n("circle", 3, s=13), None]], 150, 84, 105),
             **P(*[single(c_n(k, n, s=13), 150, 84, 36) for k, n in
                   (("triangle", 3), ("circle", 2), ("triangle", 4), ("triangle", 1))]),
             key=3, err=("ก / ค = รูปถูกแต่จำนวนผิด; ข = ลอกช่องในตาราง", "A / C = right shape, wrong count; B = copied a cell")),
        dict(n=43, scale="P", stem=Q,
             fig=grid([[fig43_cell(i, j) if (i, j) != (2, 2) else None for j in range(3)] for i in range(3)], 140, 84, 104),
             **P(single(c_n("triangle", 3, "white", s=15, gap=9), 140, 84, 36),
                 single(c_n("circle", 2, "black", s=15, gap=9), 140, 84, 36),
                 single(c_n("triangle", 3, "black", s=15, gap=9), 140, 84, 36),
                 single(c_n("triangle", 2, "white", s=15, gap=9), 140, 84, 36)),
             key=2, err=("ก = ลวดลายผิด; ข = รูปและจำนวนผิด; ง = ลวดลายและจำนวนผิด",
                         "A = wrong fill; B = wrong shape and count; D = wrong fill and count")),
        dict(n=44, scale="P",
             stem=t("ดูความสัมพันธ์ในแต่ละแถว แล้วเลือกสิ่งที่ควรอยู่ในช่อง ?",
                    "Look at how each row works, then choose what belongs in the ?&nbsp;box."),
             fig=grid([[pair("circle", "triangle", s=14), pair("triangle", "square", "star", s=14), pair("circle", "square", "star", s=14)],
                       [pair("square", "star", s=14), pair("star", "cross", s=14), pair("square", "cross", s=14)],
                       [pair("circle", "cross", "triangle", s=14), pair("cross", "star", s=14), None]], 160, 84, 114),
             **P(*[single(pair(*ks, s=14), 160, 84, 38) for ks in
                   (("circle", "triangle", "star"), ("triangle", "star"), ("circle", "cross", "triangle", "star"), ("cross",))]),
             key=0, err=("ข = ขาดไปหนึ่งรูป; ค = รวมทุกรูป (เก็บรูปที่ซ้ำไว้); ง = เก็บแค่รูปที่ซ้ำ",
                         "B = dropped a shape; C = union (kept the shared one); D = kept only the shared one")),
        dict(n=45, scale="P", stem=Q,
             fig=grid([[fig45_cell(i, j) if (i, j) != (2, 2) else None for j in range(3)] for i in range(3)], 110, 110, 90),
             **P(*[single(c_dot_arrow(c, a), 110, 110, 27) for c, a in (("TL", 90), ("TR", 180), ("TR", 90), ("TL", 180))]),
             key=3, err=("ก = ลูกศรหมุนผิด; ข = จุดเลื่อนผิด; ค = ผิดทั้งสองอย่าง",
                         "A = arrow turned wrongly; B = dot moved wrongly; C = both wrong")),
    ]

    for it in s1 + s2 + s3:
        if "err" in it:
            it["err"] = it["err"][1] if en else it["err"][0]

    sections = [
        (t("ส่วนที่ 1", "Part 1"), t("ภาษาและการใช้เหตุผล", "Language and reasoning"), t("ข้อ 1–15", "Questions 1–15"), s1),
        (t("ส่วนที่ 2", "Part 2"), t("ตัวเลขและการคำนวณ", "Numbers and calculation"), t("ข้อ 16–30", "Questions 16–30"), s2),
        (t("ส่วนที่ 3", "Part 3"), t("รูปแบบและความสัมพันธ์", "Patterns and relationships"), t("ข้อ 31–45", "Questions 31–45"), s3),
    ]
    return dict(LET=LETTERS[lang], PRACTICE=practice, SECTIONS=sections, ALL=s1 + s2 + s3)


# ---------------------------------------------------------------- coding task (language-neutral)
CODE_SYMS = ["circle", "triangle", "square", "star", "cross", "heart"]  # digits 1..6
CODE_PRACTICE = [5, 2, 6, 4, 1, 3]
CODE_ROWS = [
    [5, 1, 3, 6, 1, 3, 6, 2, 3, 5, 2, 3],
    [2, 3, 5, 4, 5, 6, 1, 3, 6, 4, 5, 2],
    [1, 3, 6, 4, 2, 5, 4, 2, 1, 6, 4, 6],
    [4, 2, 5, 2, 6, 1, 5, 2, 6, 4, 1, 2],
    [3, 6, 4, 5, 1, 3, 4, 3, 5, 1, 6, 2],
    [5, 2, 3, 6, 1, 4, 6, 5, 4, 2, 4, 3],
    [2, 5, 4, 6, 3, 1, 3, 5, 4, 5, 2, 4],
    [1, 2, 6, 1, 5, 2, 1, 5, 6, 2, 1, 4],
    [1, 6, 1, 4, 1, 2, 6, 4, 5, 4, 5, 3],
    [5, 2, 1, 5, 4, 5, 4, 1, 4, 1, 6, 1],
    [3, 5, 6, 3, 1, 5, 2, 3, 2, 6, 2, 3],
    [2, 3, 4, 3, 1, 3, 4, 6, 3, 6, 3, 6],
]

# ---------------------------------------------------------------- digit span (language-neutral)
DS_FWD = [(3, "9-5-6", "1-7-4"), (4, "8-6-5-2", "6-1-4-8"), (5, "5-7-6-9-8", "2-1-9-3-5"), (6, "1-4-8-6-5-3", "6-3-5-2-9-7"),
          (7, "2-4-9-6-3-5-7", "1-9-7-6-3-8-4"), (8, "4-1-5-9-7-6-2-8", "2-6-3-9-5-8-1-7"),
          (9, "9-6-3-8-1-5-7-4-2", "5-3-6-1-9-4-7-8-2")]
DS_BWD = [(2, "2-7", "9-2"), (3, "3-6-1", "3-8-4"), (4, "5-9-7-2", "4-1-2-5"), (5, "7-5-1-4-9", "4-9-8-5-1"),
          (6, "8-7-3-1-9-5", "9-1-2-4-6-5"), (7, "7-9-1-4-8-6-5", "8-5-1-3-4-6-7"), (8, "1-2-5-3-7-6-9-4", "5-1-9-4-7-8-2-3")]


def rev(s):
    return "-".join(s.split("-")[::-1])


def self_check():
    th, en = build("th"), build("en")
    for d in (th, en):
        assert [it["n"] for it in d["ALL"]] == list(range(1, 46))
        for it in d["ALL"] + d["PRACTICE"]:
            assert len(it["opts"]) == 4 and 0 <= it["key"] < 4, it["n"]
    assert [it["key"] for it in th["ALL"]] == [it["key"] for it in en["ALL"]], "keys differ between languages"
    assert [it["key"] for it in th["PRACTICE"]] == [it["key"] for it in en["PRACTICE"]]
    assert [it["scale"] for it in th["ALL"]] == [it["scale"] for it in en["ALL"]]
    flat = [d for r in CODE_ROWS for d in r]
    assert all(len(r) == 12 for r in CODE_ROWS) and all(flat[i] != flat[i + 1] for i in range(len(flat) - 1))
    from collections import Counter
    return "".join(th["LET"][it["key"]] for it in th["ALL"]), Counter(th["LET"][it["key"]] for it in th["ALL"])


if __name__ == "__main__":
    print(self_check())
