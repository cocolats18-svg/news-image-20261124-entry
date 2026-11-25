#!/usr/bin/env python3
"""Render a one-page newspaper front page for 24 November 2026.

Fresh, self-contained renderer: draws the masthead, a lead panel, five
story cards and a bottom ticker with Pillow, using only the verified
24 November wire slate baked into STORIES below. Deterministic: no
timestamps, no randomness, no network; the same input always yields the
same PNG bytes.
"""

from PIL import Image, ImageDraw, ImageFont

PAGE_W, PAGE_H = 1024, 1024
MARGIN = 40

# Palette: warm newsprint, ink black, crimson accents, slate blue.
PAPER = (246, 241, 229)
PANEL = (238, 229, 210)
INK = (24, 22, 18)
SOFT_INK = (74, 68, 58)
CRIMSON = (154, 27, 30)
SLATE = (36, 52, 77)
GOLD = (176, 141, 60)
HAIRLINE = (150, 140, 120)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"

LEAD = {
    "kicker": "FRANCE  ·  LIBYA CAMPAIGN-FUNDING PROBE",
    "headline": "Sarkozy and Bruni ordered to stand trial",
    "deck": (
        "French judges send the former president and his wife to trial in the "
        "witness-tampering and criminal-conspiracy case. A pre-trial hearing "
        "is set for 1 April 2027, with the trial to follow in November–December "
        "2027. The charges carry up to 10 years in prison."
    ),
}

STORIES = [
    {
        "tag": "NATO · SPACE",
        "headline": "NATO vows to defend against threats in space",
        "body": (
            "Alliance chief Mark Rutte says NATO will defend against threats "
            "in space, after reports that Russia is preparing to launch a "
            "nuclear-armed satellite."
        ),
    },
    {
        "tag": "UKRAINE · ZAPORIZHZHIA",
        "headline": "Overnight strike on Zaporizhzhia flats kills two",
        "body": (
            "A Russian overnight strike hits an apartment building, killing "
            "two people and wounding about 40, including four children."
        ),
    },
    {
        "tag": "COLOMBIA",
        "headline": "Car bomb outside government office injures 20+",
        "body": (
            "A car bomb detonates outside a Colombian government office, "
            "injuring more than 20 people."
        ),
    },
    {
        "tag": "GAZA",
        "headline": "Israeli strikes kill Hamas security chief",
        "body": (
            "Israeli airstrikes in Gaza kill Hamas internal security chief "
            "Naeem Abu Nahel and six others, including two police officers."
        ),
    },
    {
        "tag": "GERMANY · UKRAINE",
        "headline": "Germany first to gain access to Ukraine's Delta system",
        "body": (
            "Germany becomes the first country to gain access to Ukraine's "
            "Delta battlefield management system, under a preliminary deal "
            "on more interceptor missiles."
        ),
    },
]

TICKER = [
    ("BANTEN", "Toll from Indonesia's candy-factory fire rises to 26."),
    ("ECHR", "Nations may expel migrants in hybrid border emergencies."),
    ("YEMEN", "Army says Houthi forces are closing in on Aden."),
    ("MARKETS", "Nvidia shares cool about 6% in Tuesday's pullback."),
]


def load_typefaces():
    """Return the (serif, serif-bold, sans, sans-bold) fonts by size."""
    def at(path, size):
        return ImageFont.truetype(path, size)

    return {
        "nameplate": at(f"{FONT_DIR}/DejaVuSerif-Bold.ttf", 62),
        "lead_head": at(f"{FONT_DIR}/DejaVuSerif-Bold.ttf", 47),
        "card_head": at(f"{FONT_DIR}/DejaVuSerif-Bold.ttf", 24),
        "wide_head": at(f"{FONT_DIR}/DejaVuSerif-Bold.ttf", 26),
        "deck": at(f"{FONT_DIR}/DejaVuSerif.ttf", 20),
        "body": at(f"{FONT_DIR}/DejaVuSans.ttf", 16),
        "kicker": at(f"{FONT_DIR}/DejaVuSans-Bold.ttf", 15),
        "tag": at(f"{FONT_DIR}/DejaVuSans-Bold.ttf", 13),
        "ticker_head": at(f"{FONT_DIR}/DejaVuSans-Bold.ttf", 13),
        "ticker_body": at(f"{FONT_DIR}/DejaVuSans.ttf", 13),
        "dateline": at(f"{FONT_DIR}/DejaVuSans-Bold.ttf", 14),
        "footer": at(f"{FONT_DIR}/DejaVuSans.ttf", 12),
    }


def wrap_words(draw, text, font, max_width):
    """Greedy word wrap; returns a list of lines fitting max_width."""
    lines, current = [], ""
    for word in text.split(" "):
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_rule(draw, x0, y, x1, colour=INK, width=2):
    draw.line([(x0, y), (x1, y)], fill=colour, width=width)


def text_block(draw, x, y, lines, font, colour=INK, leading=None):
    """Draw wrapped lines top-down; returns the y below the last line."""
    if leading is None:
        leading = font.size + 6
    for line in lines:
        draw.text((x, y), line, font=font, fill=colour)
        y += leading
    return y


def paint_masthead(draw, fonts):
    """Nameplate, dateline row and the double rule beneath it."""
    title = "THE DAILY GLOBE"
    tw = draw.textlength(title, font=fonts["nameplate"])
    draw.text(((PAGE_W - tw) / 2, 26), title, font=fonts["nameplate"], fill=INK)
    draw_rule(draw, MARGIN, 108, PAGE_W - MARGIN, GOLD, 2)
    draw.text((MARGIN, 118), "TUESDAY 24 NOVEMBER 2026",
              font=fonts["dateline"], fill=CRIMSON)
    right = "ONE PAGE · WORLD NEWS"
    rw = draw.textlength(right, font=fonts["dateline"])
    draw.text((PAGE_W - MARGIN - rw, 118), right,
              font=fonts["dateline"], fill=SLATE)
    draw_rule(draw, MARGIN, 142, PAGE_W - MARGIN, INK, 3)
    draw_rule(draw, MARGIN, 147, PAGE_W - MARGIN, INK, 1)


def paint_lead(draw, fonts):
    """Tinted lead panel: kicker, two-line headline, deck."""
    x0, y0 = MARGIN, 162
    x1, y1 = PAGE_W - MARGIN, 424
    draw.rectangle([x0, y0, x1, y1], fill=PANEL, outline=HAIRLINE, width=1)
    draw.rectangle([x0, y0, x0 + 6, y1], fill=CRIMSON)
    inner = x0 + 26
    draw.text((inner, y0 + 18), LEAD["kicker"], font=fonts["kicker"],
              fill=CRIMSON)
    lines = wrap_words(draw, LEAD["headline"], fonts["lead_head"],
                       x1 - inner - 26)
    y = text_block(draw, inner, y0 + 48, lines, fonts["lead_head"],
                   leading=56)
    draw_rule(draw, inner, y + 8, x1 - 26, GOLD, 1)
    deck = wrap_words(draw, LEAD["deck"], fonts["deck"], x1 - inner - 26)
    text_block(draw, inner, y + 20, deck, fonts["deck"], colour=SOFT_INK,
               leading=27)


def paint_card(draw, fonts, story, x0, y0, x1, y1, wide=False):
    """One story card: crimson top rule, tag, headline, body."""
    head_font = fonts["wide_head"] if wide else fonts["card_head"]
    head_lead = 32 if wide else 30
    draw_rule(draw, x0, y0, x1, CRIMSON, 2)
    draw.text((x0, y0 + 10), story["tag"], font=fonts["tag"], fill=SLATE)
    lines = wrap_words(draw, story["headline"], head_font, x1 - x0)
    y = text_block(draw, x0, y0 + 32, lines, head_font, leading=head_lead)
    body = wrap_words(draw, story["body"], fonts["body"], x1 - x0)
    text_block(draw, x0, y + 6, body, fonts["body"], colour=SOFT_INK,
               leading=22)


def paint_grid(draw, fonts):
    """Two columns for stories 1–4, full-width card for story 5."""
    gutter = 28
    col_w = (PAGE_W - 2 * MARGIN - gutter) // 2
    left, right = MARGIN, MARGIN + col_w + gutter
    paint_card(draw, fonts, STORIES[0], left, 448, left + col_w, 596)
    paint_card(draw, fonts, STORIES[1], right, 448, right + col_w, 596)
    draw_rule(draw, MARGIN, 612, PAGE_W - MARGIN, HAIRLINE, 1)
    paint_card(draw, fonts, STORIES[2], left, 628, left + col_w, 776)
    paint_card(draw, fonts, STORIES[3], right, 628, right + col_w, 776)
    draw_rule(draw, MARGIN, 792, PAGE_W - MARGIN, HAIRLINE, 1)
    paint_card(draw, fonts, STORIES[4], MARGIN, 808,
               PAGE_W - MARGIN, 900, wide=True)


def paint_ticker(draw, fonts):
    """Bottom strip: 'ALSO TODAY' label plus four small items."""
    y0 = 918
    draw_rule(draw, MARGIN, y0, PAGE_W - MARGIN, INK, 2)
    draw.text((MARGIN, y0 + 12), "ALSO TODAY", font=fonts["kicker"],
              fill=CRIMSON)
    col_w = (PAGE_W - 2 * MARGIN) // 4
    for i, (head, body) in enumerate(TICKER):
        x = MARGIN + i * col_w
        if i:
            draw.line([(x - 10, y0 + 36), (x - 10, y0 + 66)],
                      fill=HAIRLINE, width=1)
        draw.text((x, y0 + 34), head, font=fonts["ticker_head"],
                  fill=SLATE)
        lines = wrap_words(draw, body, fonts["ticker_body"], col_w - 18)
        text_block(draw, x, y0 + 50, lines[:2], fonts["ticker_body"],
                   colour=SOFT_INK, leading=15)
    note = "All stories from 24 November 2026 · Compiled from wire reports"
    nw = draw.textlength(note, font=fonts["footer"])
    draw.text(((PAGE_W - nw) / 2, 1004), note, font=fonts["footer"],
              fill=SOFT_INK)


def compose_page():
    """Build the full 1024×1024 front page and return the image."""
    canvas = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(canvas)
    fonts = load_typefaces()
    paint_masthead(draw, fonts)
    paint_lead(draw, fonts)
    paint_grid(draw, fonts)
    paint_ticker(draw, fonts)
    return canvas


if __name__ == "__main__":
    import sys

    out_path = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    page = compose_page()
    page.save(out_path, format="PNG", optimize=True)
    print(f"wrote {out_path} {page.size[0]}x{page.size[1]}")
