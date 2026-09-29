# eldertest — Thinking and Reasoning Test (Thai / English)

This is a printable A4 reasoning test in **Thai and English**. It helps compare one person, here a 78-year-old parent, with a small comparison group you collect yourself: young graduates and people of a similar age.

What it covers:

- verbal reasoning;
- numerical reasoning;
- pattern reasoning;
- working memory (digit span);
- processing speed (a 90-second coding task).

> **This is not a clinical or diagnostic test.** It has no population norms. The tester guide explains its limits and how to read the results. If you are worried about someone's memory or thinking, see a doctor. **This repo contains the answer key, so keep it private.**

## Use it

1. Open **`package/index.html`** in Chrome or Edge.
2. Pick a language: `th/` (ภาษาไทย) or `en/` (English).
3. Read the tester guide first (`2-tester-guide.html`).
4. Print on A4 at 100% scale with default margins:
   - Print the booklet **single-sided**, so the timed grid isn't seen early.
   - Ready-made PDFs are in `package/pdf/`.

Each language set has the same four files:

| File | What it is | Print |
|---|---|---|
| `1-test-booklet.html` | The test itself: 4 practice items, 45 questions and a timed coding task | One per person |
| `2-tester-guide.html` | Scripts, answer key, digit span, how to compare and interpret | One, for the tester |
| `3-record-form.html` | Scoring sheet (shows the key) | One per person |
| `4-comparison-summary.html` | Everyone's scores on one landscape sheet | One |

Both languages have the same items, pictures and answer positions: ก = A, ข = B, ค = C, ง = D. The number, pattern, memory and speed parts are identical in both. The word items are translations, so compare the K and VR scales only between people who took the same language.

## Rebuild it

Everything is generated from one source, `content.py`, so the Thai and English booklets, keys and record forms can't drift apart.

```bash
pip install -r requirements.txt
python -m playwright install chromium   # only needed for PDFs
python build.py      # writes package/ (HTML for both languages + fonts)
python render.py     # writes package/pdf/ and pages.json
python build.py      # second pass puts the page counts into the guides
```

| File | Role |
|---|---|
| `content.py` | Every item in both languages, with keys, scales and error notes. `self_check()` asserts that the keys match across languages. |
| `figs.py` | All figures as inline SVG: shapes, grids, arrows, chart, clock, icons |
| `build.py` | Builds the HTML pages and the A4 print CSS |
| `render.py` | Renders the PDFs with headless Chromium |
| `templates/guide_*.md` | Tester guide text for each language (the key and tables are filled in at build time) |
| `fonts/` | Sarabun (SIL Open Font License 1.1, see `fonts/OFL.txt`) |

## Checks done

Independent reviewers who never saw the key solved every item blind. They worked on the Thai text version, twice on the printed Thai booklet, and once on the printed English booklet with a re-check after fixes. Every answer matched the key. Items where a reviewer found a second defensible answer, or a way to guess without solving, were rewritten.

The difficulty figures in the guide are estimates, not measurements.
