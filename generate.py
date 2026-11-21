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

# Headlines follow the supplied stories.txt. Decks are edited to fit a single
# line while retaining a concrete detail from each story.
STORIES = {
    "LEAD": [
        ("Xi, Trump and Putin sign 'peace declaration'", "90 minutes at APEC. Pact omits Ukraine and Iran wars."),
        ("Russia strikes Kyiv bridges and rail stations", "After the Kerch strike, Putin vows a ‘painful’ response."),
    ],
    "EUROPE": [
        ("UK and EU close to post-Brexit deal", "Youth mobility capped at 100,000."),
        ("Russian missiles and drones hit Poland", "Stray strikes raise alarm within NATO."),
        ("Cost-of-living protests sweep Europe", "Thousands march across European cities."),
        ("French police sentenced over Michel Zecler beating", "Court finds racist assault on music producer."),
        ("Denmark expels Russian diplomat", "Moscow linked to alleged plot to kill a rapper."),
        ("Spain frees US-sought activist on bail", "Irish police raid a Dublin home in the case."),
    ],
    "MIDDLE EAST": [
        ("Trump warns over any Iranian plot against Washington", "Tehran denies any such plan."),
        ("Houthi advance in Yemen threatens global economy", "Rebel siege puts Red Sea shipping at risk."),
        ("Iraqi protesters rally against the government", "Iraqi flags fly amid fresh unrest."),
    ],
    "ASIA": [
        ("Cyclone Akvan makes landfall in Odisha", "370,000 evacuated; winds hit 90kmph."),
        ("Asia markets dive in AI sell-off", "Anthropic IPO sparks a chip rout."),
        ("Myanmar committed genocide against Rohingya, ICJ rules", "Refugees cheer the landmark ruling."),
        ("China issues Mount Fuji warning", "$75,000 reward to find a missing climber."),
        ("China gives Japan PM frosty welcome at APEC", "Other leaders receive a warmer welcome."),
        ("Philippines pet cremation scandal", "Pets awaiting cremation shown on livestream."),
        ("Cumin-laced sodas challenge cola giants in India", "Local flavours gain market share."),
    ],
    "AFRICA": [
        ("ANC fights to keep South Africa's key cities", "Election setback threatens control of metros."),
        ("US consortium wins huge Kenya mining deal", "US group beats Chinese rivals for Mrima Hill."),
        ("Springboks face Ireland without Erasmus", "South Africa prepares for the rugby test."),
    ],
    "AMERICAS": [
        ("Venezuela signs military deal with US", "Deal follows Maduro’s removal."),
        ("Mexican drug lord Felix Gallardo dies at 80", "He led the Guadalajara cartel."),
        ("Wife of slain ex-Haiti leader registers for presidency", "First election since the assassination."),
        ("Botched Texas prison execution", "Witnesses call it unlike anything they’d seen."),
        ("Trump turns press conference into 2028 audition", "Succession talk dominates the event."),
        ("Senator blocks Trump cyber nominee", "Nominee’s January 6 denial draws opposition."),
        ("California probes Nvidia over China AI chips", "Probe follows Jensen Huang’s departure."),
        ("Nasdaq erases 2026 gains in AI rout", "Anthropic’s $2tn debut fuels sell-off."),
        ("Fired White House press secretary faces bar probe", "California bar investigates Katie Zacharia."),
        ("Huge waves batter Pacifica promenade", "Storm sends surf over the coastal walkway."),
    ],
    "OCEANIA": [
        ("Arson attack destroys Melbourne shop", "Police investigate the fire."),
        ("Mount Pleasant thermal coalmine under scrutiny", "Australian mine faces environmental pressure."),
    ],
    "GLOBAL": [
        ("COP31 climate talks deadlocked on final day", "Draft drops fossil fuels; talks run over."),
        ("Race for UN secretary general exposes divisions", "UK and France may have vetoed UAE pick."),
        ("Pancreatic cancer pill hailed as breakthrough", "Called the biggest advance in decades."),
        ("Striking snakes released into the wild", "Release aims to save an at-risk species."),
    ],
}

# These are editorial source labels requested for the supplied news brief;
# the generator itself performs no reporting or network retrieval.
SOURCES = {
    "LEAD": ("Reuters", "BBC"),
    "EUROPE": ("Guardian", "AP", "BBC", "AP", "Reuters", "Guardian"),
    "MIDDLE EAST": ("AP", "BBC", "AP"),
    "ASIA": ("IMD", "Bloomberg", "AP", "BBC", "Reuters", "BBC", "Guardian"),
    "AFRICA": ("BBC", "Reuters", "Guardian"),
    "AMERICAS": ("AP", "BBC", "AP", "Guardian", "AP", "BBC", "Reuters", "CNN", "AP", "BBC"),
    "OCEANIA": ("BBC", "Guardian"),
    "GLOBAL": ("Guardian", "AP", "BBC", "Guardian"),
}
ICONS = {
    "Cyclone Akvan makes landfall in Odisha": "cyclone",
    "Asia markets dive in AI sell-off": "chart",
    "COP31 climate talks deadlocked on final day": "earth",
    "Myanmar committed genocide against Rohingya, ICJ rules": "scales",
    "UK and EU close to post-Brexit deal": "flags",
    "Nasdaq erases 2026 gains in AI rout": "chart",
    "California probes Nvidia over China AI chips": "chip",
    "Pancreatic cancer pill hailed as breakthrough": "pill",
    "Huge waves batter Pacifica promenade": "waves",
    "Houthi advance in Yemen threatens global economy": "ship",
    "US consortium wins huge Kenya mining deal": "pick",
}
SHORT_DECKS = {
    "Cyclone Akvan makes landfall in Odisha": "370,000 flee; winds 90kmph.",
    "Asia markets dive in AI sell-off": "Anthropic IPO sparks chip rout.",
    "UK and EU close to post-Brexit deal": "Youth mobility cap: 100,000.",
    "Russian missiles and drones hit Poland": "Stray strikes alarm NATO.",
    "Cost-of-living protests sweep Europe": "Thousands march across Europe.",
    "French police sentenced over Michel Zecler beating": "Court finds racist assault.",
    "Denmark expels Russian diplomat": "Alleged plot to kill a rapper.",
    "Spain frees US-sought activist on bail": "Dublin raid linked to the case.",
    "Houthi advance in Yemen threatens global economy": "Red Sea shipping at risk.",
    "Myanmar committed genocide against Rohingya, ICJ rules": "Refugees cheer historic ruling.",
    "China issues Mount Fuji warning": "Missing climber: $75,000 reward.",
    "China gives Japan PM frosty welcome at APEC": "Other leaders welcomed warmly.",
    "Philippines pet cremation scandal": "Dead pets shown on livestream.",
    "ANC fights to keep South Africa's key cities": "ANC risks losing major metros.",
    "US consortium wins huge Kenya mining deal": "Mrima Hill: US beats China.",
    "Springboks face Ireland without Erasmus": "Boks prepare for rugby test.",
    "Botched Texas prison execution": "Witnesses describe ordeal.",
    "Senator blocks Trump cyber nominee": "Denial of January 6 draws fire.",
    "California probes Nvidia over China AI chips": "After Jensen Huang’s departure.",
    "Fired White House press secretary faces bar probe": "Bar investigates Katie Zacharia.",
    "Huge waves batter Pacifica promenade": "Storm surf floods the walkway.",
    "Mount Pleasant thermal coalmine under scrutiny": "Mine faces environmental pressure.",
    "COP31 climate talks deadlocked on final day": "Fossil fuels cut from draft.",
    "Race for UN secretary general exposes divisions": "UK, France may veto UAE pick.",
    "Pancreatic cancer pill hailed as breakthrough": "Biggest advance in decades.",
    "Striking snakes released into the wild": "Release to save at-risk species.",
}
STORIES = {region: [(headline, SHORT_DECKS.get(headline, deck)) for headline, deck in rows]
           for region, rows in STORIES.items()}

HEADLINE_SIZE = 13.5
DECK_SIZE = 12
LEADING = 1.25
CARD_HEADER = 40
CARD_BOTTOM = 12
CARD_GAP = 10
CARD_INSET = 12
MIN_ITEM_GAP = 10
MAX_ITEM_GAP = 30
# Measured column widths accommodate seven Asia briefs and inline illustrations.
COLUMNS = (
    (322, ("EUROPE", "ASIA")),
    (310, ("MIDDLE EAST", "AFRICA", "GLOBAL")),
    (328, ("AMERICAS", "OCEANIA")),
)


@lru_cache(maxsize=None)
def font(size, style="regular"):
    return ImageFont.truetype(str(FONT_DIR / FONTS[style]), round(size * SCALE))


class FrontPage:
    def __init__(self):
        self.image = Image.new("RGB", (SIZE * SCALE, SIZE * SCALE), PAPER)
        self.draw = ImageDraw.Draw(self.image)
        self.text_bounds = []
        self.shown = []
        self.story_type = []
        self.column_metrics = []
        self.icon_count = 0
        self.source_count = 0
        self.icon_bounds = []

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

    def measure(self, lines, size, style, leading=LEADING):
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
            xy = ((x + dx) * SCALE, (y + i * fitted * LEADING) * SCALE)
            bounds = self.draw.textbbox(xy, line, font=font(fitted, style), anchor="lt")
            assert bounds[0] >= x * SCALE - 1 and bounds[2] <= (x + width) * SCALE + 1, (line, bounds, box)
            assert bounds[1] >= y * SCALE - 1 and bounds[3] <= (y + height) * SCALE + 1
            self.text_bounds.append(tuple(n / SCALE for n in bounds))
            self.draw.text(xy, line, font=font(fitted, style), fill=color, anchor="lt")
        return fitted

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
        headline, deck = STORIES["LEAD"][index]
        self.text("APEC / DIPLOMACY" if index == 0 else "UKRAINE / ESCALATION",
                  (x + 98, y, width - 98, 14), 11, "bold", RED, max_lines=1)
        (self.flags if index == 0 else self.bridge)(x + 3, y + 2)
        head_size = self.text(headline, (x + 98, y + 20, width - 98, 55),
                              24, "bold", minimum=23)
        deck_size = self.text(deck, (x + 98, y + 77, width - 98, 15),
                              13, color=GREY, max_lines=1, minimum=12)
        self.shown.append(headline)
        self.story_type.append((head_size, deck_size))
        self.icon_count += 1
        self.source_count += 1
        self.text(SOURCES["LEAD"][index], (x + 2, y + 86, 88, 12), 9, color=GREY, max_lines=1, align="center")

    def inline_icon(self, kind, x, y):
        """A 24px pictogram; all coordinates stay inside the reserved gutter."""
        def line(points, color=BLUE, width=1.5):
            self.line([(x + a, y + b) for a, b in points], color, width)
        def box(bounds, color):
            self.rectangle(tuple(v + (x if i % 2 == 0 else y) for i, v in enumerate(bounds)), color)
        def ellipse(bounds, color):
            self.ellipse(tuple(v + (x if i % 2 == 0 else y) for i, v in enumerate(bounds)), color)
        if kind == "cyclone":
            for turn in (0, pi):
                line([(12 + cos(t / 14 * 2.5 * pi + turn) * (2 + t * .43),
                       12 + sin(t / 14 * 2.5 * pi + turn) * (2 + t * .43)) for t in range(21)], BLUE, 2)
            ellipse((10, 10, 14, 14), RED)
        elif kind == "chart":
            line([(2, 3), (2, 22), (23, 22)], GREY, 1)
            for a, b in ((7, 5), (13, 10), (19, 14)):
                line([(a, b - 2), (a, b + 7)], BLUE, 1)
                box((a - 2, b, a + 2, b + 5), BLUE)
            line([(4, 4), (10, 8), (15, 7), (22, 18)], RED, 2)
            line([(17, 16), (22, 18), (22, 12)], RED, 2)
        elif kind == "earth":
            ellipse((2, 2, 22, 22), BLUE)
            self.polygon([(x + a, y + b) for a, b in [(5, 6), (12, 4), (17, 9), (11, 13), (7, 19), (5, 13)]], PAPER)
            line([(12, 19), (18, 8)], GOLD, 1.5)
        elif kind == "scales":
            line([(12, 3), (12, 22), (5, 22), (19, 22)], INK)
            line([(3, 7), (21, 7)], INK)
            for a in (5, 19):
                line([(a, 7), (a - 4, 15), (a + 4, 15), (a, 7)], BLUE, 1)
                box((a - 4, 15, a + 4, 17), GOLD)
        elif kind == "flags":
            box((1, 4, 11, 14), BLUE)
            line([(1, 9), (11, 9)], WHITE, 2)
            line([(6, 4), (6, 14)], RED, 2)
            box((14, 4, 24, 14), BLUE)
            for i in range(8):
                ellipse((18 + cos(i * pi / 4) * 3, 8 + sin(i * pi / 4) * 3,
                         19 + cos(i * pi / 4) * 3, 9 + sin(i * pi / 4) * 3), GOLD)
            line([(2, 16), (2, 23), (22, 23), (22, 16)], INK, 1)
        elif kind == "chip":
            box((6, 6, 19, 19), BLUE)
            box((9, 9, 16, 16), PAPER)
            for a in (8, 13, 18):
                line([(a, 2), (a, 5)], INK, 1)
                line([(a, 20), (a, 23)], INK, 1)
                line([(2, a), (5, a)], INK, 1)
                line([(20, a), (23, a)], INK, 1)
        elif kind == "pill":
            ellipse((2, 5, 22, 19), BLUE)
            ellipse((3, 6, 14, 18), PAPER)
            line([(13, 5), (13, 19)], RED, 1)
        elif kind == "waves":
            for b in (7, 13, 19):
                line([(a, b + sin(a * pi / 12) * 2) for a in range(2, 24)], BLUE, 2)
        elif kind == "ship":
            line([(2, 21), (22, 21)], BLUE)
            self.polygon([(x + a, y + b) for a, b in [(2, 14), (23, 14), (19, 19), (6, 19)]], BLUE)
            box((7, 7, 17, 13), INK)
            line([(12, 2), (12, 7)], RED)
        elif kind == "pick":
            line([(5, 22), (17, 4)], GREY, 3)
            line([(3, 8), (11, 3), (20, 5), (23, 10)], INK, 2)
        self.icon_count += 1
        self.icon_bounds.append((x, y, x + 24, y + 24))

    def brief_heights(self, headline, deck, width):
        head_width = width - (30 if headline in ICONS else 0)
        lines, _ = self.fit(headline, head_width, 60, HEADLINE_SIZE, "bold", 3, HEADLINE_SIZE)
        deck_lines, _ = self.fit(deck, width - 55, 16, DECK_SIZE, max_lines=1, minimum=DECK_SIZE)
        return max(24 if headline in ICONS else 0, self.measure(lines, HEADLINE_SIZE, "bold")), self.measure(deck_lines, DECK_SIZE, "regular")

    def region_column(self, labels, x, top, width, bottom):
        inner_width = width - 2 * CARD_INSET
        cards = [(label, [self.brief_heights(*story, inner_width) for story in STORIES[label]])
                 for label in labels]
        separators = sum(len(rows) - 1 for _, rows in cards)
        fixed = (CARD_HEADER + CARD_BOTTOM) * len(cards) + CARD_GAP * (len(cards) - 1)
        fixed += sum(h + 4 + d for _, rows in cards for h, d in rows)
        gap = (bottom - top - fixed) / separators
        if not MIN_ITEM_GAP <= gap <= MAX_ITEM_GAP:
            raise ValueError(f"Column {labels} needs a {gap:.1f}px item gap to fill {bottom - top}px")
        y = top
        for label, rows in cards:
            height = CARD_HEADER + CARD_BOTTOM + sum(h + 4 + d for h, d in rows) + gap * (len(rows) - 1)
            self.rectangle((x, y, x + width, y + height), WHITE, INK, .7)
            self.rectangle((x, y, x + width, y + 2), RED)
            left, right = x + CARD_INSET, x + width - CARD_INSET
            self.text(label, (left, y + 10, inner_width, 18), 16, "bold", RED, max_lines=1)
            self.line([(left, y + 30), (right, y + 30)], INK, .6)
            cursor = y + CARD_HEADER
            for i, ((headline, deck), (head_h, deck_h)) in enumerate(zip(STORIES[label], rows)):
                inset = 30 if headline in ICONS else 0
                if inset:
                    self.inline_icon(ICONS[headline], left, cursor)
                head_size = self.text(headline, (left + inset, cursor, inner_width - inset, head_h + .4),
                                      HEADLINE_SIZE, "bold", max_lines=3, minimum=HEADLINE_SIZE)
                cursor += head_h + 4
                deck_size = self.text(deck, (left, cursor, inner_width - 55, deck_h + .4),
                                      DECK_SIZE, color=GREY, max_lines=1, minimum=DECK_SIZE)
                source = SOURCES[label][i]
                tag_width = self.width(source, 9, "regular")
                self.text(source, (right - tag_width, cursor + 2, tag_width + .1, 11),
                          9, color=GREY, max_lines=1, minimum=9)
                self.source_count += 1
                cursor += deck_h
                self.shown.append(headline)
                self.story_type.append((head_size, deck_size))
                if i < len(rows) - 1:
                    self.line([(left, cursor + gap / 2), (right, cursor + gap / 2)], GREY, .45)
                    cursor += gap
            assert abs(y + height - cursor - CARD_BOTTOM) < .01, label
            y += height + CARD_GAP
        assert abs(y - CARD_GAP - bottom) < .01
        self.column_metrics.append(gap / 2)

    def render(self):
        self.text("THE WORLD TODAY", (24, 24, 976, 57), 46, "serif", max_lines=1, align="center")
        self.text("GLOBAL EDITION · WORLD NEWS BRIEFING", (24, 69, 976, 15),
                  10.5, color=GREY, max_lines=1, align="center")
        self.line([(24, 86), (1000, 86)], INK, 2)
        self.line([(24, 91), (1000, 91)], INK, .6)
        self.text("FRIDAY · 20 NOVEMBER 2026", (24, 100, 976, 28),
                  24, "bold", RED, max_lines=1, align="center")
        self.line([(24, 130), (1000, 130)], INK, .6)
        self.lead(0, 24, 141, 476)
        self.lead(1, 524, 141, 476)
        self.line([(512, 140), (512, 232)], GREY, .5)
        self.line([(24, 239), (1000, 239)], INK, 1.5)
        x = 24
        for width, labels in COLUMNS:
            self.region_column(labels, x, 249, width, 973)
            x += width + 8
        self.rectangle((24, 983, 1000, 1006), INK)
        self.text("Sources: BBC, The Guardian, Reuters, AP, IMD · 20 Nov 2026", (34, 989, 700, 13),
                  10, color=WHITE, max_lines=1)
        self.text("make.fun / NEWS IMAGE", (778, 989, 210, 13),
                  10, "bold", WHITE, max_lines=1, align="center")
        expected = [headline for group in STORIES.values() for headline, _ in group]
        assert sorted(self.shown) == sorted(expected), "Missing or duplicated news stories"
        assert len(self.shown) == len(self.story_type) == self.source_count == 37
        # Check actual glyph rectangles, including lines in different text blocks.
        for i, a in enumerate(self.text_bounds):
            for b in self.text_bounds[i + 1:]:
                assert not (min(a[2], b[2]) > max(a[0], b[0]) + .5 and
                            min(a[3], b[3]) > max(a[1], b[1]) + .5), (a, b)
        for a in self.icon_bounds:
            for b in self.text_bounds:
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
    head_min, deck_min = map(min, zip(*page.story_type))
    print(f"Minimum type: {head_min:g}px headlines, {deck_min:g}px decks")
    print("Padding on each side of separators:", [round(n, 1) for n in page.column_metrics])
    print(f"Icons: {page.icon_count}; source tags: {page.source_count} at 9px")


if __name__ == "__main__":
    main()
