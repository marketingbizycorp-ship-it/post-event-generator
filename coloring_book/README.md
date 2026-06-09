# K-Pop Demon Hunters — Children's Coloring Book 🎤🗡️👹

Print-ready, black-line-art coloring pages with a *K-pop-idol-meets-demon-hunter*
theme — built for small hands and big crayons: thick outlines, big shapes, and
plenty of white space to color.

> **About the characters:** these are **original, theme-inspired** chibi idols
> and friendly demons. They evoke the "singing demon hunters" vibe without
> reproducing any specific copyrighted film designs, so they're safe to print,
> photocopy, and share at home, classrooms, or parties.

## Pages

| # | Page | What's on it |
|---|------|--------------|
| 0 | **Cover** | Title, crossed mic + sword emblem, and a "this book belongs to" line |
| 1 | **Star Singer** | Idol girl singing into a microphone |
| 2 | **Dance Idol** | Idol boy with headphones and a heart light-stick |
| 3 | **Demon Buddy** | A cute, fluffy little demon with horns and a tail |
| 4 | **Showtime!** | Two idols on a spotlit stage |
| 5 | **Hunter Gear** | Sword, light stick, talisman & headphones to color |
| 6 | **Pattern Power** | Stars, hearts & music notes (great for the youngest) |
| 7 | **Design Your Idol** | A blank idol to give a face, hair & outfit |

## Build it

No third-party libraries needed — just Python 3.

```bash
python coloring_book/generate.py        # build all SVGs + the printable book
python coloring_book/generate.py --list # list the pages
```

This writes:

- `coloring_book/pages/*.svg` — one crisp vector page each (print any single page)
- `coloring_book/coloring-book.html` — the whole book in one file

## Print it

Open `coloring-book.html` in any browser, press **Ctrl/Cmd + P**, and choose
**Save as PDF** (or send straight to the printer). Pages are sized for US Letter
with one coloring page per sheet. The individual `.svg` files print on their own
too, and being vectors they stay sharp at any size.

## Add your own page

Each page is just a small Python function returning an SVG string. To add one:

1. Write a `page_*()` function that builds the art from the helpers
   (`circle`, `star`, `heart`, `chibi_eyes`, `friendly_demon`, …) and wraps it
   with `page(title, body_svg)`.
2. Add an entry to the `PAGES` list at the bottom of `generate.py`.
3. Re-run the build.
