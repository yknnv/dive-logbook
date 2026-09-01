<div align="center">

<img src="docs/preview/cover.png" alt="Cover of the DIVE logbook printable A5 scuba diving log book" width="300">

# DIVE logbook — a printable A5 scuba diving log book

**A paper dive log, quick reference and emergency card in one.** 130 pages,
42 spreads for dive records, every field labelled in Russian and English.
The layout is written as Python code, not stored in a binary design file:
the whole book rebuilds from source with one command.

[**Download the PDF**](https://github.com/yknnv/dive-logbook/releases/latest) ·
[Русский](README.md) ·
[Printing](#printing) ·
[Build it yourself](#build-it-yourself)

[![Build](https://github.com/yknnv/dive-logbook/actions/workflows/build.yml/badge.svg)](https://github.com/yknnv/dive-logbook/actions/workflows/build.yml)
[![Release](https://img.shields.io/github/v/release/yknnv/dive-logbook?label=PDF)](https://github.com/yknnv/dive-logbook/releases/latest)
[![Code: MIT](https://img.shields.io/badge/code-MIT-black)](LICENSE)
[![Content: CC BY-NC-SA 4.0](https://img.shields.io/badge/content-CC%20BY--NC--SA%204.0-black)](LICENSE-CONTENT)

</div>

---

## What this is

A personal scuba diving logbook meant to be printed — at home or at a print
shop — punched for a ring binder and filled in with a pen. Not an app and not
a spreadsheet: paper does not run out of battery, needs no signal, and an
instructor can sign it on the spot.

- **130 pages**, of which **42 two-page spreads** are dive records
- **A5, 148 × 210 mm**, punched for ring binding
- **single-colour black** printing — cheap at any print shop
- field labels in **Russian and English**, so a foreign instructor can sign it
- **reference section**: safety and planning figures, BWRAF pre-dive check,
  ascent, lost buddy procedure, DSMB, hand signals, emergency procedure,
  decompression illness, emergency contacts, pressure and depth, gas planning,
  RMV in litres, rock-bottom reserve, nitrox and MOD, oxygen exposure,
  no-fly limits, weighting, baseline parameters

A sister project for another discipline: `sail-logbook`.

## What it looks like

| Dive record spread | Hand signals | Lost buddy |
|---|---|---|
| <img src="docs/preview/spread-record.png" alt="Dive record spread: dive profile, gas, equipment, self-assessment"> | <img src="docs/preview/hand-signals.png" alt="Reference page with the essential scuba hand signals"> | <img src="docs/preview/lost-buddy.png" alt="Reference page with the lost buddy procedure"> |

---

## Download and print

Ready-made PDFs are on the [latest release page](https://github.com/yknnv/dive-logbook/releases/latest) —
nothing to build. They are not committed to the repository: every rebuild
would add 12 MB of binary to the history.

| file | what for |
|---|---|
| `dive-logbook-A5-final.pdf` | main file, trimmed page exactly 148 × 210 mm |
| `dive-logbook-A5-final-bleed3mm-cropmarks.pdf` | 154 × 216 mm with 3 mm bleed and crop marks, for a shop that guillotines a stack |
| `punch-template-A5.pdf` | one 1:1 sheet to check the hole pattern |

**Start with the punch template.** Print it at 100 % scale — not "fit to
page" — and hold it against your own binder: ring spacing varies. The
parameters live at the top of `src/logbook.py`.

---

## Build it yourself

```bash
git clone https://github.com/yknnv/dive-logbook.git
cd dive-logbook
pip install -r requirements.txt
./build.sh
```

Requires Python 3.10+. Output lands in `dist/`, which is gitignored. The
build runs the layout checks on its own: anything outside the type area,
horizontal glyph overlaps, vertical word overlaps.

### Settings you can change without touching the layout

At the top of `src/logbook.py`:

```python
VERSION = "1.0"               # goes into the file name and the PDF metadata
N_DIVES = 42                  # number of dive record spreads
N_NOTES = 10                  # note pages at the end
KEEP_CREATED_WITH_AI = True   # the line on the title page
HOLE_D = 6 * mm               # hole diameter
HOLE_INSET = 11 * mm          # sheet edge to hole centre
HOLE_SPACING = 47 * mm        # between adjacent hole centres
HOLE_MARKS = True             # print punch guides
M_BIND = 23 * mm              # binding-side margin
```

---

## Layout

```
src/logbook.py        page geometry, primitives, cover, dive cards, assembly
src/reference.py      reference section, one function per page
src/figures.py        vector diagrams
src/check_margins.py  margin and overlap checks
assets/fonts/         Carlito, SIL OFL 1.1
assets/images/        illustrations, monochrome PNG
dist/                 build output, not committed
docs/                 illustration brief template, page previews
tools/                illustration preparation
CLAUDE.md             instructions for an AI agent working on the book
```

---

## Typesetting rules

Worth keeping to in any change — the full set is in [CLAUDE.md](CLAUDE.md)
and [CONTRIBUTING.md](CONTRIBUTING.md).

**Spacing comes from constants.** `src/reference.py` declares `GAP_TEXT`,
`GAP_LIST`, `GAP_TABLE`, `GAP_FIG`, `GAP_NOTE`. One kind of element, one gap
throughout the book. If something does not fit, cut the content, never the
gap: tuning gaps per page is exactly what pulls a book out of alignment.

**Overflow is caught by the build.** Every page ends with `assert y >= MB`.
If it does not fit, the build fails and names the page and the missing
millimetres. The right response is to shorten the text, shrink the image, or
split the page in two.

**Labels are bilingual.** `field(c, x, y, w, "русский", "english")` sets the
Russian name in solid black and the English one lighter and smaller, with the
size fitted to the column width automatically.

**Monochrome.** The whole palette is shades of black.

**No page numbers**, deliberately: sheets are removable and the owner decides
the order.

---

## Pre-press check

```bash
python3 src/check_margins.py dist/dive-logbook-A5-final.pdf
```

Three checks: anything outside the type area with a 0.15 mm tolerance,
horizontal glyph overlaps, vertical word overlaps. Punch marks in the binding
margin are accounted for separately and are not violations. The same check
runs in CI on every push.

---

## Printing

- 100–120 gsm offset paper
- 23 mm binding-side margin, 10 mm outer, alternating by page parity
- double-sided, page count is always even
- a dive record occupies a spread and always starts on an even page
- give the print shop the bleed-and-crop-marks file; use the main file at home

---

## Working on it with an AI agent

[CLAUDE.md](CLAUDE.md) in the repository root is the agent brief: layout
invariants, a file map, templates for adding pages and diagrams, the format
for stating an edit, and a list of mistakes this project has actually made.
Claude Code picks it up automatically; any other tool can simply be given it
as context.

---

## Licences and disclaimer

The code is MIT. The book content — reference text, diagrams, illustrations
and the built PDFs — is CC BY-NC-SA 4.0: print it for yourself, your club or
your group, modify it, pass it on, but do not sell it. The file-by-file
breakdown is in [NOTICE](NOTICE).

The Carlito typeface is under the SIL Open Font License 1.1; the licence text
is in `assets/fonts/Carlito-COPYRIGHT.txt`. It is metrically compatible with
Calibri and has full Cyrillic coverage.

Illustrations were generated with AI and cleaned up by hand. The diagrams in
`figures.py` are drawn in code.

**The reference section does not replace training.** Every figure in it
depends on your certification, your equipment, local rules and the dive plan;
where that matters, the text says so.
