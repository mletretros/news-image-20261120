"""Draw an original, illustrated newspaper front page using Pillow only."""

from functools import lru_cache
from math import cos, sin, pi
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SIZE, SCALE = 1024, 3
PAPER = "#F6F1E7"
INK, RED, BLUE, GOLD, GREY = "#1A1A1A", "#B3202C", "#1F4E79", "#E8B33A", "#6B6257"
WHITE = "#FFFFFF"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
FONTS = {"serif": "DejaVuSerif-Bold.ttf", "bold": "DejaVuSans-Bold.ttf", "regular": "DejaVuSans.ttf"}
image = Image.new("RGB", (SIZE * SCALE, SIZE * SCALE), PAPER)
draw = ImageDraw.Draw(image)


@lru_cache(maxsize=None)
def font(size, style="regular"):
    return ImageFont.truetype(str(FONT_DIR / FONTS[style]), round(size * SCALE))


class Pen:
    """Local coordinates, rendered at high resolution for smooth print graphics."""

    def __init__(self, x=0, y=0, scale=1):
        self.x, self.y, self.scale = x, y, scale

    def point(self, xy):
        x, y = xy
        return ((self.x + x * self.scale) * SCALE, (self.y + y * self.scale) * SCALE)

    def box(self, box):
        return self.point(box[:2]) + self.point(box[2:])

    def rectangle(self, box, fill, outline=None, width=1):
        draw.rectangle(self.box(box), fill=fill, outline=outline, width=max(1, round(width * self.scale * SCALE)))

    def ellipse(self, box, fill, outline=None, width=1):
        draw.ellipse(self.box(box), fill=fill, outline=outline, width=max(1, round(width * self.scale * SCALE)))

    def polygon(self, points, fill):
        draw.polygon([self.point(p) for p in points], fill=fill)

    def line(self, points, fill=INK, width=1):
        draw.line([self.point(p) for p in points], fill=fill, width=max(1, round(width * self.scale * SCALE)), joint="curve")


pen = Pen()


def text_width(text, size, style):
    return draw.textlength(text, font=font(size, style)) / SCALE


def wrap(text, width, size, style):
    lines, line = [], ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if line and text_width(candidate, size, style) > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def fit_to_box(text, width, height, size, style="regular", max_lines=20, leading=1.2):
    for candidate in range(size, 0, -1):
        lines = [line for paragraph in text.splitlines() for line in wrap(paragraph, width, candidate, style)]
        step = candidate * leading
        if (len(lines) <= max_lines and len(lines) * step <= height
                and all(text_width(line, candidate, style) <= width for line in lines)):
            return lines, candidate, step
    raise ValueError(f"Text box is too small: {text}")


def draw_block(text, box, size, style="regular", fill=INK, max_lines=20, leading=1.2, align="left"):
    x, y, width, height = box
    lines, fitted, step = fit_to_box(text, width, height, size, style, max_lines, leading)
    for line in lines:
        dx = (width - text_width(line, fitted, style)) / 2 if align == "center" else 0
        draw.text(((x + dx) * SCALE, y * SCALE), line, font=font(fitted, style), fill=fill, anchor="lt")
        y += step
    return len(lines) * step


def star(p, x, y, radius, color=GOLD, rotation=-pi / 2):
    points = []
    for n in range(10):
        angle = rotation + n * pi / 5
        r = radius if n % 2 == 0 else radius * .42
        points.append((x + cos(angle) * r, y + sin(angle) * r))
    p.polygon(points, color)


def flag(p, kind, x, y, w, h):
    if kind == "us":
        p.rectangle((x, y, x + w, y + h), WHITE)
        for i in range(0, 13, 2):
            p.rectangle((x, y + h * i / 13, x + w, y + h * (i + 1) / 13), RED)
        p.rectangle((x, y, x + w * .43, y + h * 7 / 13), BLUE)
        for row in range(9):
            for col in range(6 - row % 2):
                star(p, x + w * (.04 + (col + .5 * (row % 2)) * .07),
                     y + h * (.055 + row * .054), h * .023, WHITE)
    elif kind == "china":
        p.rectangle((x, y, x + w, y + h), RED)
        star(p, x + w * .21, y + h * .29, h * .17)
        for sx, sy in [(.4, .12), (.49, .28), (.49, .47), (.4, .61)]:
            star(p, x + w * sx, y + h * sy, h * .055)
    elif kind == "russia":
        for i, color in enumerate([WHITE, BLUE, RED]):
            p.rectangle((x, y + h * i / 3, x + w, y + h * (i + 1) / 3), color)
    elif kind == "uk":
        p.rectangle((x, y, x + w, y + h), BLUE)
        for color, inset in [(WHITE, .17), (RED, .07)]:
            diagonal = [(0, 0), (inset, 0), (1, 1 - inset), (1, 1), (1 - inset, 1), (0, inset)]
            p.polygon([(x + u * w, y + v * h) for u, v in diagonal], color)
            p.polygon([(x + (1 - u) * w, y + v * h) for u, v in diagonal], color)
        p.rectangle((x + w * .38, y, x + w * .62, y + h), WHITE)
        p.rectangle((x, y + h * .34, x + w, y + h * .66), WHITE)
        p.rectangle((x + w * .44, y, x + w * .56, y + h), RED)
        p.rectangle((x, y + h * .42, x + w, y + h * .58), RED)
    elif kind == "eu":
        p.rectangle((x, y, x + w, y + h), BLUE)
        for i in range(12):
            angle = i * pi / 6 - pi / 2
            star(p, x + w / 2 + cos(angle) * h * .32, y + h / 2 + sin(angle) * h * .32, h * .065)
    p.line([(x, y + h), (x, y), (x + w, y), (x + w, y + h), (x, y + h)], INK, .6)


def summit_icon(p):
    for x, kind in [(10, "us"), (90, "china"), (170, "russia")]:
        p.line([(x, 160), (x, 18)], INK, 3)
        p.ellipse((x - 3, 12, x + 3, 18), GOLD)
        flag(p, kind, x + 2, 22, 70, 46)
        p.ellipse((x - 9, 156, x + 9, 161), GREY)
    for x, top in [(60, 105), (119, 98), (180, 105)]:
        person(p, x, top, 53)
    p.rectangle((65, 191, 73, 222), INK)
    p.rectangle((176, 191, 184, 222), INK)
    p.ellipse((20, 150, 231, 205), INK)
    p.ellipse((20, 143, 231, 193), BLUE, INK, 2)
    p.ellipse((70, 155, 181, 181), PAPER)
    p.line([(92, 168), (159, 168)], GOLD, 3)


def person(p, x, top, height, color=INK):
    """A round head, short neck, sloped shoulders, and a tapered torso."""
    r = height * .15
    p.ellipse((x - r, top, x + r, top + 2 * r), color)
    p.rectangle((x - r * .45, top + r * 1.8, x + r * .45, top + r * 2.6), color)
    p.polygon([(x - r * .65, top + height * .36),
               (x - r * 1.9, top + height * .47),
               (x - r * 2.2, top + height * .70),
               (x - r * 1.55, top + height),
               (x + r * 1.55, top + height),
               (x + r * 2.2, top + height * .70),
               (x + r * 1.9, top + height * .47),
               (x + r * .65, top + height * .36)], color)


def partnership_icon(p):
    flag(p, "uk", 0, 13, 65, 43)
    flag(p, "eu", 75, 13, 65, 43)
    p.polygon([(0, 91), (24, 79), (51, 102), (30, 126), (0, 113)], BLUE)
    p.polygon([(140, 91), (116, 79), (89, 102), (110, 126), (140, 113)], BLUE)
    p.polygon([(27, 85), (46, 75), (66, 82), (84, 78), (115, 96), (94, 118), (77, 122), (42, 104)], GOLD)
    p.line([(46, 75), (64, 83), (57, 94), (66, 99), (81, 89), (107, 103)], INK, 2)
    for x in [61, 73, 85]:
        p.line([(x, 105), (x + 13, 116)], INK, 1.5)


def bridge_icon(p):
    for y in [108, 120, 132]:
        p.line([(0, y), (22, y - 3), (45, y + 2), (70, y - 3), (96, y + 2), (140, y - 2)], BLUE, 2)
    for x in [18, 62, 116]:
        p.rectangle((x, 76, x + 10, 119), GREY)
    p.rectangle((0, 70, 140, 80), INK)
    p.line([(0, 63), (140, 63)], GREY, 3)
    for x in range(4, 141, 15):
        p.line([(x, 62), (x, 72)], INK, 2)
    burst = []
    for i in range(20):
        a = i * pi / 10
        r = 43 if i % 2 == 0 else 22
        burst.append((88 + cos(a) * r, 56 + sin(a) * r))
    p.polygon(burst, RED)
    p.polygon([(68, 67), (74, 37), (85, 49), (94, 26), (104, 61), (95, 78)], GOLD)


def market_icon(p):
    p.line([(5, 5), (5, 98), (138, 98)], GREY, 2)
    for y in [30, 55, 80]:
        p.line([(9, y), (138, y)], "#DDD8CD", 1)
    for x, low, high in [(23, 87, 65), (46, 79, 49), (69, 67, 37), (92, 51, 24), (119, 36, 10)]:
        p.line([(x, high - 5), (x, low + 5)], BLUE, 2)
        p.rectangle((x - 5, high + 3, x + 5, low - 3), BLUE)
    p.line([(17, 72), (48, 55), (69, 60), (103, 29), (131, 15)], RED, 3)
    p.polygon([(131, 15), (117, 17), (129, 29)], RED)
    # A separate protest placard sits below the chart with a clear paper gap.
    p.line([(79, 137), (79, 155)], INK, 4)
    p.rectangle((45, 110, 113, 138), PAPER, INK, 2)
    p.line([(55, 120), (103, 120)], RED, 3)
    p.line([(55, 129), (91, 129)], INK, 2)


def justice_icon(p):
    p.line([(70, 14), (70, 89)], INK, 4)
    p.ellipse((64, 7, 76, 19), GOLD, INK, 1)
    p.line([(22, 31), (118, 31)], INK, 4)
    for x in [29, 111]:
        p.line([(x, 31), (x - 21, 66), (x + 21, 66), (x, 31)], INK, 1.7)
        p.polygon([(x - 23, 66), (x + 23, 66), (x + 14, 77), (x - 14, 77)], GOLD)
    p.rectangle((51, 87, 89, 92), INK)
    for x, top in [(18, 110), (53, 104), (88, 108), (123, 102)]:
        person(p, x, top, 43)


def tile_icon(icon, x, y, width=132, height=140):
    """Normalize ink bounds into one shared, centered illustration viewport."""
    global draw
    layer = Image.new("RGBA", (160 * SCALE, 180 * SCALE))
    page_draw = draw
    try:
        draw = ImageDraw.Draw(layer)
        icon(Pen(5, 5))
    finally:
        draw = page_draw
    artwork = layer.crop(layer.getbbox())
    artwork.thumbnail((width * SCALE, height * SCALE), Image.Resampling.LANCZOS)
    px = round((x + width / 2) * SCALE - artwork.width / 2)
    py = round((y + height / 2) * SCALE - artwork.height / 2)
    image.paste(artwork, (px, py), artwork)


def tile(x, y, category, headline, caption, icon):
    width, height = 472, 218
    pen.rectangle((x, y, x + width, y + height), WHITE, INK, 1)
    pen.rectangle((x, y, x + 4, y + height), RED)
    draw_block(category, (x + 16, y + 13, width - 32, 17), 11, "bold", RED)
    # All four icon viewports share the same size and the card's vertical center.
    tile_icon(icon, x + 14, y + (height - 140) / 2)
    tx, tw = x + 158, width - 174
    used = draw_block(headline, (tx, y + 39, tw, 87), 25, "bold", max_lines=3, leading=1.12)
    caption_y = y + 39 + used + 10
    draw_block(caption, (tx, caption_y, tw, y + height - 14 - caption_y), 17, fill=GREY, leading=1.25)


def main():
    pen.rectangle((0, 0, SIZE, SIZE), PAPER)
    draw_block("THE WORLD TODAY", (32, 37, 960, 75), 62, "serif", align="center", max_lines=1)
    draw_block("GLOBAL EDITION · WORLD NEWS BRIEFING", (32, 100, 960, 14),
               11, "regular", GREY, align="center", max_lines=1)
    pen.line([(32, 118), (992, 118)], INK, 3)
    pen.line([(32, 124), (992, 124)], INK, 1)
    draw_block("FRIDAY · 20 NOVEMBER 2026", (32, 142, 960, 43), 34, "bold", RED, align="center", max_lines=1)
    pen.line([(32, 193), (992, 193)], INK, 1)
    draw_block("DIPLOMACY  /  APEC SUMMIT", (32, 208, 960, 20), 13, "bold", RED)
    pen.line([(290, 236), (290, 456)], GREY, .6)
    headline = "XI, TRUMP AND PUTIN\nSIGN 'PEACE\nDECLARATION'"
    used = draw_block(headline, (306, 234, 686, 145), 40, "bold", max_lines=3, leading=1.12)
    caption_y = 234 + used + 10
    caption = "First US-China-Russia trilateral: 90 minutes in Shenzhen at the APEC summit. The joint declaration omits the Ukraine and Iran wars."
    caption_box = (306, caption_y, 680, 461 - caption_y)
    draw_block(caption, caption_box, 22, fill=GREY, leading=1.22)
    lines, fitted, step = fit_to_box(caption, caption_box[2], caption_box[3], 22, leading=1.22)
    last_bottom = draw.textbbox((0, 0), lines[-1], font=font(fitted), anchor="lt")[3] / SCALE
    caption_bottom = caption_y + (len(lines) - 1) * step + last_bottom
    summit_icon(Pen(35, caption_bottom - 222 * .98, .98))
    pen.line([(32, 466), (992, 466)], INK, 2)

    tile(32, 482, "EUROPE  /  BREXIT RESET", "UK AND EU CLOSE TO POST-BREXIT DEAL",
         "A 100,000 youth-mobility cap is agreed ahead of Friday's summit, with food-trade and carbon deals on the table.", partnership_icon)
    tile(520, 482, "UKRAINE  /  WAR ESCALATES", "PUTIN VOWS 'PAINFUL' RESPONSE TO KERCH BRIDGE BOMBING",
         "Ukraine strikes the Crimea bridge; Moscow threatens retaliation as the war escalates.", bridge_icon)
    tile(32, 714, "BUSINESS  /  AI & MARKETS", "ANTHROPIC HITS $2TN IN STOCK DEBUT AS PROTESTS ERUPT",
         "The AI giant's record listing draws rallies in New York and San Francisco.", market_icon)
    tile(520, 714, "WORLD COURT  /  MYANMAR", "ICJ RULES ON ROHINGYA CASE AS REFUGEES CHEER",
         "The World Court issues its ruling on Myanmar; Rohingya refugees watch the broadcast.", justice_icon)

    pen.rectangle((32, 948, 992, 1000), INK)
    draw_block("ALSO TODAY", (44, 968, 121, 22), 16, "bold", RED, max_lines=1)
    pen.line([(171, 957), (171, 991)], GREY, 1)
    ticker = [
        "California opens Nvidia China AI chip probe  •  White House cyber director ousted after tech outages",
        "Race for UN secretary general exposes world-power divisions  •  China snubs Japan PM at APEC",
    ]
    ticker_size = min(fit_to_box(line, 795, 20, 16, max_lines=1)[1] for line in ticker)
    for line, y in zip(ticker, (958, 979)):
        draw_block(line, (184, y, 795, 20), ticker_size, fill=WHITE, max_lines=1, align="center")
    draw_block("Sources: BBC, The Guardian, Reuters · 20 Nov 2026", (32, 1007, 960, 13),
               9, fill=GREY, max_lines=1, align="center")
    output = Path(__file__).resolve().with_name("entry.png")
    image.resize((SIZE, SIZE), Image.Resampling.LANCZOS).save(output, optimize=True)
    with Image.open(output) as check:
        assert check.format == "PNG" and check.size == (1024, 1024)
        check.verify()
    assert output.stat().st_size < 1_048_576
    print(f"{output.name}: 1024x1024 PNG, {output.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
