"""An original, self-contained world-news front page drawn with Pillow."""

from functools import lru_cache
from math import cos, sin, pi
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SIZE, SCALE = 1024, 3
PAPER, INK = "#F6F1E7", "#1A1A1A"
RED, BLUE, GREY = "#B3202C", "#1F4E79", "#6B6257"
GOLD, WHITE = "#E8B33A", "#FFFFFF"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
FONTS = {"serif": "DejaVuSerif-Bold.ttf", "bold": "DejaVuSans-Bold.ttf", "regular": "DejaVuSans.ttf"}

# Transcribed from the supplied stories.txt, preserving every regional headline.
# Embedding the brief keeps regeneration independent of external files or networks.
STORIES = {
    "LEAD": [
        ("Xi, Trump and Putin sign 'peace declaration'", "First US-China-Russia trilateral, 90 minutes in Shenzhen at APEC; declaration omits Ukraine and Iran wars."),
        ("Russia strikes Kyiv bridges and rail stations", "One of its biggest air attacks, days after Ukraine badly damaged the Crimean (Kerch) Bridge; Putin vows a 'painful' response."),
    ],
    "EUROPE": [
        ("UK and EU close to post-Brexit deal", "100,000 youth-mobility cap agreed; Burnham says it 'is for you', Badenoch calls it unfair."),
        ("Russian missiles and drones hit Poland", "Stray strikes during attacks on Ukraine raise NATO alarm."),
        ("Cost-of-living protests sweep Europe", "Thousands marched across European cities on Friday."),
        ("French police sentenced over Michel Zecler beating", "Court finds racist assault on the Black music producer."),
        ("Denmark expels Russian diplomat", "Alleged Moscow link to an attempted killing of a rapper."),
        ("Spain frees US-sought activist on bail", "Irish police raid a Dublin home in the same case."),
    ],
    "MIDDLE EAST": [
        ("Trump warns over any Iranian plot against Washington", "US taking it 'very seriously'; Tehran rejects any such plan."),
        ("Houthi advance in Yemen threatens global economy", "Iran-backed rebels besiege a city; Red Sea shipping at risk."),
    ],
    "ASIA": [
        ("Myanmar committed genocide against Rohingya, ICJ rules", "Unprecedented International Court of Justice ruling; refugees cheer."),
        ("China issues Mount Fuji warning", "Family of a missing climber offers a $75,000 reward."),
        ("China gives Japan PM frosty welcome at APEC", "Fanfare for other leaders contrasts with the snub."),
        ("Philippines pet cremation scandal", "Dead pets meant to be cremated appeared on a livestream."),
    ],
    "AFRICA": [
        ("ANC fights to keep South Africa's key cities", "Election setback threatens control of major metros."),
        ("US consortium wins huge Kenya mining deal", "Mrima Hill site, beating Chinese rivals."),
        ("Springboks face Ireland without Erasmus", "Defiant Boks prepare for the test."),
    ],
    "AMERICAS": [
        ("Venezuela signs military deal with US", "Less than a year after Maduro's removal."),
        ("Mexican drug lord Felix Gallardo dies at 80", "The 'Boss of Bosses' of the Guadalajara cartel."),
        ("Wife of slain ex-Haiti leader registers for presidency", "First election since the assassination."),
        ("Botched Texas prison execution", "Onlookers say it was like nothing they had seen."),
        ("Trump turns press conference into 2028 audition", "Succession talk dominates the White House event."),
        ("Senator blocks Trump cyber nominee", "Over January 6 denial; cyber director ousted after tech outages."),
        ("California probes Nvidia over China AI chips", "Follows Jensen Huang's departure."),
        ("Anthropic hits $2tn in stock debut", "Record AI listing draws protests in New York and San Francisco."),
    ],
    "GLOBAL": [
        ("Race for UN secretary general exposes divisions", "UK and France believed to have vetoed the UAE choice."),
        ("Pancreatic cancer pill hailed as breakthrough", "Called the biggest advance in decades."),
    ],
}


@lru_cache(maxsize=None)
def font(size, style="regular"):
    return ImageFont.truetype(str(FONT_DIR / FONTS[style]), round(size * SCALE))


class FrontPage:
    def __init__(self):
        self.image = Image.new("RGB", (SIZE * SCALE, SIZE * SCALE), PAPER)
        self.draw = ImageDraw.Draw(self.image)
        self.text_bounds = []
        self.shown = []
        self.region_fonts = {}

    def rectangle(self, box, fill, outline=None, width=1):
        self.draw.rectangle(tuple(round(n * SCALE) for n in box), fill=fill,
                            outline=outline, width=max(1, round(width * SCALE)))

    def line(self, points, fill=INK, width=1):
        self.draw.line([(round(x * SCALE), round(y * SCALE)) for x, y in points],
                       fill=fill, width=max(1, round(width * SCALE)), joint="curve")

    def polygon(self, points, fill):
        self.draw.polygon([(round(x * SCALE), round(y * SCALE)) for x, y in points], fill=fill)

    def ellipse(self, box, fill):
        self.draw.ellipse(tuple(round(n * SCALE) for n in box), fill=fill)

    def width(self, text, size, style):
        return self.draw.textlength(text, font=font(size, style)) / SCALE

    def wrap(self, text, width, size, style):
        lines, current = [], ""
        for word in text.split():
            candidate = (current + " " + word).strip()
            if current and self.width(candidate, size, style) > width:
                lines.append(current)
                current = word
            else:
                current = candidate
        return lines + ([current] if current else [])

    def measure(self, lines, size, style, leading=1.18):
        if not lines:
            return 0
        glyph_height = max(self.draw.textbbox((0, 0), line, font=font(size, style), anchor="lt")[3]
                           / SCALE for line in lines)
        return (len(lines) - 1) * size * leading + glyph_height

    def fit(self, text, width, height, size, style="regular", max_lines=2, minimum=9):
        for half in range(round(size * 2), round(minimum * 2) - 1, -1):
            candidate = half / 2
            lines = self.wrap(text, width, candidate, style)
            if (len(lines) <= max_lines and self.measure(lines, candidate, style) <= height
                    and all(self.width(line, candidate, style) <= width for line in lines)):
                return lines, candidate
        raise ValueError(f"Text does not fit: {text}")

    def text(self, text, box, size, style="regular", color=INK, max_lines=2, align="left", minimum=9):
        x, y, width, height = box
        lines, fitted = self.fit(text, width, height, size, style, max_lines, minimum)
        for i, line in enumerate(lines):
            dx = (width - self.width(line, fitted, style)) / 2 if align == "center" else 0
            xy = ((x + dx) * SCALE, (y + i * fitted * 1.18) * SCALE)
            bounds = self.draw.textbbox(xy, line, font=font(fitted, style), anchor="lt")
            assert bounds[0] >= x * SCALE - 1 and bounds[2] <= (x + width) * SCALE + 1
            assert bounds[1] >= y * SCALE - 1 and bounds[3] <= (y + height) * SCALE + 1
            self.text_bounds.append(tuple(n / SCALE for n in bounds))
            self.draw.text(xy, line, font=font(fitted, style), fill=color, anchor="lt")
        return self.measure(lines, fitted, style)

    def star(self, x, y, radius, color=GOLD):
        self.polygon([(x + cos(-pi / 2 + i * pi / 5) * radius * (1 if i % 2 == 0 else .42),
                       y + sin(-pi / 2 + i * pi / 5) * radius * (1 if i % 2 == 0 else .42))
                      for i in range(10)], color)

    def flags(self, x, y):
        for i, country in enumerate(("US", "CHINA", "RUSSIA")):
            left, top, w, h = x + i * 28, y + (6 if i == 1 else 13), 25, 20
            self.line([(left, top - 4), (left, y + 70)], INK, 1)
            self.ellipse((left - 1.5, top - 6, left + 1.5, top - 3), GOLD)
            if country == "US":
                self.rectangle((left, top, left + w, top + h), WHITE)
                for band in range(0, 13, 2):
                    self.rectangle((left, top + band * h / 13, left + w, top + (band + 1) * h / 13), RED)
                self.rectangle((left, top, left + 11, top + 11), BLUE)
                for row in range(3):
                    for col in range(3):
                        self.star(left + 2 + col * 3.3, top + 2 + row * 3.2, .7, WHITE)
            elif country == "CHINA":
                self.rectangle((left, top, left + w, top + h), RED)
                self.star(left + 6, top + 6, 3)
                for dx, dy in [(11, 3), (14, 6), (14, 10), (11, 13)]:
                    self.star(left + dx, top + dy, 1)
            else:
                for band, color in enumerate((WHITE, BLUE, RED)):
                    self.rectangle((left, top + band * h / 3, left + w, top + (band + 1) * h / 3), color)
            self.line([(left, top), (left + w, top), (left + w, top + h), (left, top + h)], GREY, .4)
        self.ellipse((x - 3, y + 59, x + 83, y + 78), BLUE)
        self.line([(x + 16, y + 80), (x + 64, y + 80)], INK, 1)

    def bridge(self, x, y):
        for yy in [65, 73, 81]:
            self.line([(x, y + yy), (x + 18, y + yy - 2), (x + 39, y + yy + 1),
                       (x + 61, y + yy - 2), (x + 84, y + yy)], BLUE, 1)
        for xx in [10, 38, 70]:
            self.rectangle((x + xx, y + 46, x + xx + 6, y + 71), GREY)
        self.rectangle((x, y + 41, x + 84, y + 47), INK)
        self.line([(x, y + 36), (x + 84, y + 36)], INK, 1)
        for xx in range(3, 84, 9):
            self.line([(x + xx, y + 36), (x + xx, y + 42)], INK, 1)
        self.polygon([(x + 54 + cos(i * pi / 10) * (25 if i % 2 == 0 else 13),
                       y + 29 + sin(i * pi / 10) * (25 if i % 2 == 0 else 13)) for i in range(20)], RED)
        self.polygon([(x + 44, y + 39), (x + 48, y + 19), (x + 55, y + 27),
                      (x + 60, y + 10), (x + 65, y + 37), (x + 56, y + 45)], GOLD)

    def lead(self, index, x, y, width):
        headline, _ = STORIES["LEAD"][index]
        self.text("APEC / DIPLOMACY" if index == 0 else "UKRAINE / ESCALATION",
                  (x, y, width, 14), 10.5, "bold", RED, max_lines=1)
        (self.flags if index == 0 else self.bridge)(x + 2, y + 24)
        self.text(headline, (x + 99, y + 23, width - 99, 55), 22, "bold", max_lines=2, minimum=17)
        caption = ("90 minutes at APEC; declaration omits Ukraine and Iran wars." if index == 0 else
                   "After the Kerch Bridge attack, Putin vows a 'painful' response.")
        self.text(caption, (x + 99, y + 86, width - 99, 18), 13, color=GREY, max_lines=1, minimum=10)
        self.shown.append(headline)

    def region(self, label, box):
        x, y, width, height = box
        items = STORIES[label]
        self.rectangle((x, y, x + width, y + height), WHITE, INK, .7)
        self.rectangle((x, y, x + width, y + 3), RED)
        self.text(label, (x + 13, y + 13, width - 65, 22), 15, "bold", RED, max_lines=1)
        self.text(f"{len(items):02d}", (x + width - 37, y + 15, 24, 18), 11, "bold", GREY, max_lines=1)
        self.line([(x + 13, y + 40), (x + width - 13, y + 40)], INK, .6)
        inner_width = width - 26
        available = height - 65
        # Start with every caption. Remove caption lines evenly before shrinking
        # headlines, keeping all stories and a six-pixel inter-brief gutter.
        for headline_size in (13, 12.5, 12, 11.5, 11):
            heads = [self.fit(h, inner_width, 40, headline_size, "bold", 2, headline_size)[0] for h, _ in items]
            head_heights = [self.measure(lines, headline_size, "bold") for lines in heads]
            for caption_limit in (3, 2, 1, 0):
                captions = [self.wrap(c, inner_width, 11, "regular") for _, c in items]
                # Captions are included whole or omitted; never silently truncated.
                captions = [lines if len(lines) <= caption_limit else [] for lines in captions]
                heights = [hh + (5 + self.measure(cc, 11, "regular") if cc else 0)
                           for hh, cc in zip(head_heights, captions)]
                total = sum(heights) + (len(items) - 1) * 13
                if total <= available:
                    break
            else:
                continue
            break
        else:
            raise ValueError(f"Regional card cannot fit all stories: {label}")
        self.region_fonts[label] = headline_size
        cursor = y + 51
        # A little extra leading is useful in sparse regions without creating
        # giant empty cells; dense regions retain the exact minimum gutter.
        gap = 13 + min(18, (available - total) / max(1, len(items) - 1))
        for i, ((headline, caption), hh, cc, item_height) in enumerate(zip(items, head_heights, captions, heights)):
            self.text(headline, (x + 13, cursor, inner_width, hh + .4), headline_size,
                      "bold", max_lines=2, minimum=headline_size)
            if cc:
                self.text(caption, (x + 13, cursor + hh + 5, inner_width,
                                   self.measure(cc, 11, "regular") + .4), 11,
                          color=GREY, max_lines=3, minimum=11)
            self.shown.append(headline)
            cursor += item_height
            assert cursor <= y + height - 13, (label, headline, cursor)
            if i < len(items) - 1:
                self.line([(x + 13, cursor + gap / 2), (x + width - 13, cursor + gap / 2)], GREY, .35)
                cursor += gap

    def render(self):
        self.text("THE WORLD TODAY", (24, 24, 976, 57), 46, "serif", max_lines=1, align="center")
        self.text("GLOBAL EDITION · WORLD NEWS BRIEFING", (24, 83, 976, 15),
                  10.5, color=GREY, max_lines=1, align="center")
        self.line([(24, 105), (1000, 105)], INK, 2)
        self.line([(24, 110), (1000, 110)], INK, .6)
        self.text("FRIDAY · 20 NOVEMBER 2026", (24, 121, 976, 32),
                  24, "bold", RED, max_lines=1, align="center")
        self.line([(24, 161), (1000, 161)], INK, .6)
        self.lead(0, 24, 173, 476)
        self.lead(1, 524, 173, 476)
        self.line([(512, 173), (512, 280)], GREY, .5)
        self.line([(24, 284), (1000, 284)], INK, 1.5)
        regions = ("EUROPE", "MIDDLE EAST", "ASIA", "AFRICA", "AMERICAS", "GLOBAL")
        for i, region in enumerate(regions):
            self.region(region, (24 + (i % 3) * 330, 297 + (i // 3) * 343, 316, 330))
        self.rectangle((24, 983, 1000, 1006), INK)
        self.text("Sources: BBC, The Guardian · 20 Nov 2026", (34, 989, 700, 13),
                  10, color=WHITE, max_lines=1)
        self.text("make.fun / NEWS IMAGE", (778, 989, 210, 13),
                  10, "bold", WHITE, max_lines=1, align="center")
        expected = [headline for group in STORIES.values() for headline, _ in group]
        assert sorted(self.shown) == sorted(expected), "Missing or duplicated news stories"
        assert len(self.shown) == 27
        # Check actual glyph rectangles, including lines in different text blocks.
        for i, a in enumerate(self.text_bounds):
            for b in self.text_bounds[i + 1:]:
                assert not (min(a[2], b[2]) > max(a[0], b[0]) + .5 and
                            min(a[3], b[3]) > max(a[1], b[1]) + .5), (a, b)
        return self.image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def main():
    page = FrontPage()
    output = Path(__file__).resolve().with_name("entry.png")
    page.render().save(output, format="PNG", optimize=True)
    with Image.open(output) as check:
        assert check.format == "PNG" and check.size == (1024, 1024)
        check.verify()
    byte_count = output.stat().st_size
    assert byte_count < 1_048_576, f"PNG exceeds size budget: {byte_count}"
    print(f"entry.png: 1024x1024 PNG, {byte_count:,} bytes; {len(page.shown)} stories")
    print("All headlines present; glyph bounds and non-overlap checks passed.")
    print("Regional headline sizes:", page.region_fonts)


if __name__ == "__main__":
    main()
