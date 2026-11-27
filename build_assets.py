#!/usr/bin/env python3
"""Pre-render every tile of the 27 Nov 2026 broadsheet into assets/.

Pillow only. This is the ONLY build step that draws text or shapes.
main.py (stdlib only) merely pastes these tiles onto the page, so the
final PNG is deterministic. Run from the repo root:
    python3 build_assets.py

Design (winner package, verified against 20261121-23 rank-1 pages):
giant serif date as masthead, region bar with counts, UTC strip,
13 illustrated flat-geometric cards, a 22-item ALSO ON list, a world
map with plain (unnumbered) pins, a numbers strip, a CRYPTO NEWS band,
a red DATE CHECK box, a HOW SURE legend. No story numbers anywhere:
pins are plain dots, the map legend maps pins to places by region
colour. No human faces; illustration is flat geometry only.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")

PAPER = (241, 236, 224, 255)
INK = (17, 17, 17, 255)
RED = (176, 30, 30, 255)
TEAL = (46, 125, 107, 255)
NAVY = (31, 78, 121, 255)
GOLD = (183, 121, 31, 255)
GREEN = (46, 125, 60, 255)
PURPLE = (125, 60, 152, 255)
ORANGE = (211, 84, 0, 255)
SMOKE = (120, 116, 108, 255)
FAINT = (90, 84, 72, 255)
PALE = (232, 226, 210, 255)
LINEC = (200, 192, 172, 255)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def tile(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def wrap(draw, text, fnt, width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, color, width, leading):
    lines = wrap(draw, text, fnt, width)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=color)
        y += leading
    return y


def rule(draw, x0, y, x1, color=INK, width=1):
    draw.line([(x0, y), (x1, y)], fill=color, width=width)


def save(img, name):
    img.save(os.path.join(ASSETS, name), "PNG")
    print("wrote", name, img.size)


# Region colours (used for bar chips, card kickers, map pins, legend).
REGIONS = [
    ("ASIA-PACIFIC", 8, TEAL),
    ("EUROPE", 6, NAVY),
    ("MIDDLE EAST", 6, PURPLE),
    ("AMERICAS", 4, RED),
    ("AFRICA", 4, GOLD),
    ("SOUTH ASIA", 4, ORANGE),
    ("CRYPTO", 1, (150, 110, 20, 255)),
    ("MARKETS & CULTURE", 2, (85, 85, 85, 255)),
]

BADGE_FILL = {
    "CONFIRMED": GREEN,
    "OFFICIAL": NAVY,
    "REPORTED": (196, 154, 20, 255),
    "CLAIM": RED,
}


def badge(draw, x, y, label):
    """Trust badge chip; returns its width."""
    fnt = font(SANS_B, 8)
    w = int(draw.textlength(label, font=fnt)) + 10
    draw.rectangle([x, y, x + w, y + 12], fill=BADGE_FILL[label])
    draw.text((x + 5, y + 2), label, font=fnt, fill=(255, 255, 255, 255))
    return w


def kicker_line(draw, x, y, width, place, region, conf):
    """Location + region in red bold (place already carries the region),
    badge at the right edge."""
    fnt = font(SANS_B, 9)
    draw.text((x, y), place, font=fnt, fill=RED)
    bw = int(draw.textlength(conf, font=font(SANS_B, 8))) + 10
    badge(draw, x + width - bw, y - 1, conf)


# ---------------------------------------------------------------- content
# 13 illustrated cards: (place, region, confidence, source,
#                        headline, deck, illustration key)
LEAD = [
    ("SHANGHAI  ·  ASIA-PACIFIC", "CONFIRMED", "Reuters",
     "China stocks surge as Beijing unleashes the national team",
     "Shanghai +3.3%, its sharpest one-day rise in over two years; "
     "STAR 50 +12%, chip index +15%.",
     "bars"),
    ("HORMUZ  ·  MIDDLE EAST", "REPORTED", "UKMTO",
     "Missing seafarer found dead after Hormuz tanker attack",
     "Jordanian crewman missing since 17 Nov confirmed dead; UKMTO "
     "reports another tanker hit off Khasab.",
     "tanker"),
    ("BRUSSELS  ·  EUROPE", "REPORTED", "Reuters",
     "Merz: EU leaders aim for budget deal before year-end",
     "Summit stalled on the €1.78tn budget and €45bn Ukraine loan; "
     "Sweden walks out, Le Pen denounces the push.",
     "eu"),
]

MID = [
    ("TOKYO  ·  ASIA-PACIFIC", "CONFIRMED", "Reuters",
     "Tokyo core inflation hits 16-month high of 2.9%",
     "December BoJ hike now the base case; markets eye 1.5%.", "yen"),
    ("SEOUL  ·  ASIA-PACIFIC", "CONFIRMED", "Reuters",
     "South Korea repatriates six North Koreans",
     "Drifting boat crew sent home by sea; a seventh chose to stay.", "boat"),
    ("BEIJING  ·  ASIA-PACIFIC", "CONFIRMED", "investingLive",
     "China industrial profits jump 20.1% in October",
     "AI and electronics drive the gain; household demand still weak.", "factory"),
    ("SEOUL  ·  ASIA-PACIFIC", "CONFIRMED", "Reuters",
     "Kosdaq jumps 6.7% as chip stocks lead Asia",
     "Kospi +4%, Nikkei +1.9%; SK Hynix +4.6%, Samsung +4.2%.", "chip"),
    ("ANKARA  ·  MIDDLE EAST", "CONFIRMED", "Reuters",
     "Erdogan completes ratification of Mecca defence pact",
     "Turkey joins Pakistan and Saudi Arabia in the joint defence deal.", "shields"),
]

LOW = [
    ("NEW YORK  ·  AMERICAS", "CONFIRMED", "Reuters",
     "US markets reopen for a short Black Friday session",
     "S&P futures +1.6%, Nasdaq +2.4% as AI jitters ease; dollar eyes "
     "a third monthly gain.", "bell"),
    ("KYIV REGION  ·  EUROPE", "REPORTED", "Ukraine General Staff",
     "Ukraine says it damaged five Russian warplanes",
     "Three MiG-31s and two Su-34s hit; Crimea suffers a total blackout.", "planes"),
    ("WELLINGTON  ·  ASIA-PACIFIC", "CONFIRMED", "One Turn",
     "New Zealand coalition falls one seat short",
     "65 seats won; the centrist Opportunity party now holds the balance.", "seats"),
    ("CRYPTO  ·  BITCOIN", "CONFIRMED", "Finnhub / CoinGecko",
     "Bitcoin holds $61,637 as $7bn in options expire",
     "Up from a $57,300 low on Wednesday; Deribit expiry looms over the "
     "short US session.", "bitcoin"),
    ("CLIMATE  ·  WORLD", "REPORTED", "The Guardian",
     "Earth exceeds 2°C of warming for seven straight days",
     "A first on record; Australia braces for a summer of bushfire risk.", "thermo"),
]

# 22 ALSO ON items: (place, headline, source)
ALSO = [
    ("MEXICO", "Protest over US extradition refusal", "AP"),
    ("COLOMBIA", "Aid for Villavicencio after bombing", "Aggregator"),
    ("PERU", "IDB announces $10bn for Peru", "One Turn"),
    ("SPAIN", "Snap vote Sunday; conservatives lead", "One Turn"),
    ("LONDON", "Tube strike runs into Friday", "TfL / Independent"),
    ("LONDON", "UK-EU treaty text; 10-year exit clause", "Guardian / BBC"),
    ("KYIV", "Ukraine regrets Libyan officers killed", "Aggregator"),
    ("BAGHDAD", "Iraq jails eight Frenchmen for life", "Aggregator"),
    ("DAMASCUS", "US praises Syria arms seizure", "Aggregator"),
    ("AMMAN", "NATO, Jordan widen military ties", "Aggregator"),
    ("SANA'A", "Yemeni army fights near capital", "Aggregator"),
    ("SUDAN", "Blue Nile toll rises to 19; UN condemns", "PANA / UN"),
    ("ADDIS ABABA", "AU backs Ethiopia Sudan talks plan", "PANA"),
    ("HARARE", "Zimbabwe plans $1.3bn cargo hub", "One Turn"),
    ("ETHIOPIA", "Polio drive to protect 11m children", "PANA"),
    ("TAIPEI", "Local elections test Lai government", "One Turn"),
    ("MYANMAR", "Leader rejects full ICJ ruling", "One Turn"),
    ("NEW DELHI", "India rejects US tariff claims", "Aggregator"),
    ("ISLAMABAD", "Speaker: India weakened Pakistan", "Daily Times"),
    ("DOHA", "Bangladesh A v Pakistan A semi", "PriyoNews24"),
    ("MUMBAI", "RBI expected to raise rates 25bp", "ING THINK"),
    ("LOS ANGELES", "Pizza Hut co-founder dies at 95", "Straits Times"),
]

NUMBERS = [
    ("$5.39bn", "Nov outflows, US BTC ETFs"),
    ("$7bn", "BTC options expiring Fri"),
    ("12", "Fear & Greed, Extreme Fear"),
    ("$10bn", "IDB funding for Peru"),
    ("+20.1%", "China industrial profits"),
    ("+6.7%", "Kosdaq jump Friday"),
]

UTC = [
    ("OVERNIGHT", "Ukraine strikes"),
    ("06:50", "BTC $61,637"),
    ("MORNING", "Tokyo CPI 2.9%"),
    ("MIDDAY", "Tube strike ends"),
    ("AFTERNOON", "Shanghai +3.3%"),
    ("EVENING", "Merz budget aim"),
]


# ---------------------------------------------------------------- masthead
def build_masthead():
    img = tile(984, 100)
    d = ImageDraw.Draw(img)
    d.text((0, 2), "THE WORLD IN ONE DAY", font=font(SANS_B, 11), fill=RED)
    d.text((984 - 250, 2), "ONE DAY  ·  ONE WORLD  ·  EST. 2026",
           font=font(SANS_B, 11), fill=INK)
    date = "FRIDAY 27 NOVEMBER 2026"
    size = 64
    while size > 40:
        f_date = font(SERIF, size)
        if d.textlength(date, font=f_date) <= 984:
            break
        size -= 2
    d.text(((984 - d.textlength(date, font=f_date)) / 2, 16), date,
           font=f_date, fill=INK)
    f_sub = font(SANS_B, 12)
    sub = "35 STORIES  ·  8 REGIONS  ·  ALL FROM THIS ONE DAY"
    d.text(((984 - d.textlength(sub, font=f_sub)) / 2, 84), sub,
           font=f_sub, fill=RED)
    rule(d, 0, 97, 984, INK, 2)
    save(img, "t_masthead.png")


def build_regions():
    img = tile(984, 22)
    d = ImageDraw.Draw(img)
    x = 0
    fnt = font(SANS_B, 10)
    for name, count, color in REGIONS:
        label = "%s %d" % (name, count)
        w = int(d.textlength(label, font=fnt)) + 16
        d.rectangle([x, 2, x + w, 20], fill=color)
        d.text((x + 8, 6), label, font=fnt, fill=(255, 255, 255, 255))
        x += w + 6
    d.text((x + 4, 6), "EVERY ONE DATED 27 NOVEMBER 2026",
           font=font(SANS_B, 10), fill=RED)
    save(img, "t_regions.png")


def build_utc():
    img = tile(984, 20)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 118, 19], fill=RED)
    d.text((8, 4), "THE DAY IN UTC", font=font(SANS_B, 10),
           fill=(255, 255, 255, 255))
    x = 128
    for when, what in UTC:
        d.ellipse([x, 7, x + 6, 13], fill=RED)
        d.text((x + 10, 4), when + " — " + what, font=font(SANS_B, 8), fill=INK)
        x += int(d.textlength(when + " — " + what, font=font(SANS_B, 8))) + 18
    save(img, "t_utc.png")


# ---------------------------------------------------------------- illustrations
# Flat geometric panels, no faces, no human figures at all.
def illo_bars(d, w, h, bg, accent=TEAL):
    d.rectangle([0, 0, w - 1, h - 1], fill=bg)
    bars = [0.25, 0.35, 0.3, 0.5, 0.45, 0.68, 0.6, 0.9]
    bw = w // 10
    for i, f in enumerate(bars):
        bh = int(h * f * 0.85)
        x = 8 + i * bw
        d.rectangle([x, h - 8 - bh, x + bw - 4, h - 8],
                    fill=accent if i >= 5 else (120, 150, 140, 255))
    d.line([(8, h - 8 - int(h * 0.25)), (w - 12, h - 8 - int(h * 0.9))],
           fill=RED, width=3)
    d.ellipse([w - 18, h - 8 - int(h * 0.9) - 4, w - 10,
               h - 8 - int(h * 0.9) + 4], fill=RED)


def illo_tanker(d, w, h, bg):
    d.rectangle([0, 0, w - 1, h - 1], fill=bg)
    d.ellipse([w - 60, 8, w - 20, 48], fill=(240, 200, 90, 255))
    d.rectangle([0, h - 30, w, h], fill=(90, 140, 170, 255))
    for i in range(5):
        d.arc([i * (w // 4) - 10, h - 38, i * (w // 4) + 30, h - 14],
              180, 360, fill=(255, 255, 255, 255), width=2)
    d.rectangle([w // 6, h - 58, w * 5 // 6, h - 30], fill=(60, 60, 60, 255))
    d.rectangle([w // 6 + 14, h - 78, w // 6 + 42, h - 58], fill=RED)
    d.rectangle([w * 5 // 6 - 52, h - 76, w * 5 // 6 - 26, h - 58],
                fill=(250, 246, 236, 255))
    d.polygon([(w * 5 // 6 - 30, h - 58), (w * 5 // 6 - 10, h - 58),
               (w * 5 // 6 - 20, h - 72)], fill=(60, 60, 60, 255))
    d.rectangle([w // 2 - 30, h - 50, w // 2 + 30, h - 44], fill=(220, 220, 220, 255))


def illo_eu(d, w, h, bg):
    d.rectangle([0, 0, w - 1, h - 1], fill=bg)
    cx, cy = w // 4, h // 2
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=NAVY)
    for i in range(8):
        import math
        a = math.pi * i / 4
        sx = cx + int(19 * math.cos(a))
        sy = cy + int(19 * math.sin(a))
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 210, 60, 255))
    d.rectangle([w // 2, h // 2 - 24, w - 14, h // 2 + 24], fill=(250, 246, 236, 255))
    d.rectangle([w // 2, h // 2 - 24, w - 14, h // 2 - 18], fill=RED)
    for i in range(3):
        d.line([(w // 2 + 10, h // 2 - 8 + i * 9), (w - 24, h // 2 - 8 + i * 9)],
               fill=(120, 116, 108, 255), width=2)
    d.text((w // 2 + 10, h // 2 + 10), "€1.78tn", font=font(SANS_B, 11), fill=NAVY)


def illo_yen(d, w, h, bg):
    d.rectangle([0, 0, w - 1, h - 1], fill=bg)
    d.line([(12, h - 14), (w // 2, h // 2), (w - 14, 12)], fill=RED, width=4)
    d.polygon([(w - 14, 12), (w - 30, 14), (w - 16, 28)], fill=RED)
    d.text((w - 52, h - 30), "¥", font=font(SERIF, 26), fill=NAVY)


def illo_boat(d, w, h, bg):
    d.rectangle([0, 0, w - 1, h - 1], fill=bg)
    d.rectangle([0, h - 24, w, h], fill=(90, 140, 170, 255))
    for i in range(4):
        d.arc([i * (w // 3) - 8, h - 30, i * (w // 3) + 28, h - 10],
              180, 360, fill=(255, 255, 255, 255), width=2)
    d.polygon([(w // 2 - 40, h - 24), (w // 2 + 40, h - 24),
               (w // 2 + 28, h - 12), (w // 2 - 28, h - 12)], fill=(60, 60, 60, 255))
    d.rectangle([w // 2 - 2, h - 52, w // 2 + 2, h - 24], fill=(60, 60, 60, 255))
    d.polygon([(w // 2 + 2, h - 52), (w // 2 + 2, h - 30), (w // 2 + 26, h - 30)],
              fill=RED)


def illo_factory(d, w, h, bg):
    d.rectangle([0, 0, w - 1, h - 1], fill=bg)
    d.rectangle([14, h - 40, w - 14, h - 8], fill=(70, 70, 70, 255))
    d.polygon([(14, h - 40), (34, h - 56), (54, h - 40)], fill=(70, 70, 70, 255))
    d.polygon([(58, h - 40), (78, h - 56), (98, h - 40)], fill=(70, 70, 70, 255))
    d.rectangle([w - 40, h - 62, w - 30, h - 8], fill=(70, 70, 70, 255))
    for i in range(3):
        d.rectangle([24 + i * 26, h - 32, 40 + i * 26, h - 18], fill=(240, 200, 90, 255))
    d.line([(10, 12), (w // 2, 12), (w - 12, h - 34)], fill=TEAL, width=3)


def illo_chip(d, w, h, bg):
    d.rectangle([0, 0, w - 1, h - 1], fill=bg)
    cx, cy = w // 2, h // 2 + 4
    for i in range(4):
        x = cx - 24 + i * 16
        d.line([(x, cy - 32), (x, cy - 22)], fill=INK, width=2)
        d.line([(x, cy + 22), (x, cy + 32)], fill=INK, width=2)
    d.rectangle([cx - 28, cy - 22, cx + 28, cy + 22], fill=(30, 30, 30, 255))
    d.rectangle([cx - 16, cy - 12, cx + 16, cy + 12], fill=TEAL)
    d.text((cx - 8, cy - 8), "AI", font=font(SANS_B, 11), fill=(255, 255, 255, 255))
    d.line([(10, h - 12), (w // 2, 14), (w - 10, 10)], fill=RED, width=3)


def illo_shields(d, w, h, bg):
    d.rectangle([0, 0, w - 1, h - 1], fill=bg)
    cols = [RED, TEAL, NAVY]
    for i, c in enumerate(cols):
        x = w // 2 - 44 + i * 32
        d.polygon([(x, 12), (x + 26, 12), (x + 26, h // 2 + 4),
                   (x + 13, h - 12), (x, h // 2 + 4)], fill=c)
        d.line([(x + 8, h // 2 - 2), (x + 13, h // 2 + 4), (x + 19, h // 2 - 8)],
               fill=(255, 255, 255, 255), width=2)
    d.rectangle([0, h - 8, w, h], fill=GOLD)


def illo_bell(d, w, h, bg):
    d.rectangle([0, 0, w - 1, h - 1], fill=bg)
    d.line([(12, h - 12), (w // 2, 16), (w - 12, 10)], fill=TEAL, width=3)
    d.ellipse([w - 30, 8, w - 14, 24], fill=TEAL)
    cx = w // 4
    d.pieslice([cx - 18, h // 2 - 6, cx + 18, h // 2 + 26], 180, 360, fill=GOLD)
    d.rectangle([cx - 22, h // 2 + 22, cx + 22, h // 2 + 28], fill=GOLD)
    d.ellipse([cx - 3, h // 2 + 28, cx + 3, h // 2 + 34], fill=INK)


def illo_planes(d, w, h, bg):
    d.rectangle([0, 0, w - 1, h - 1], fill=bg)
    for i in range(3):
        d.ellipse([20 + i * 50, 8 + (i % 2) * 8, 60 + i * 50, 22 + (i % 2) * 8],
                  fill=(255, 255, 255, 255))
    for i, (px, py) in enumerate([(30, 34), (90, 26), (150, 40), (60, 52), (120, 58)]):
        s = 1.0 if i < 2 else 0.8
        d.polygon([(px, py), (px + int(26 * s), py + 4), (px, py + 8)],
                  fill=(30, 30, 30, 255))
        d.polygon([(px + 8, py + 2), (px + 14, py - 6), (px + 16, py + 2)],
                  fill=(30, 30, 30, 255))
    d.line([(10, h - 10), (w - 10, h - 10)], fill=RED, width=2)


def illo_seats(d, w, h, bg):
    d.rectangle([0, 0, w - 1, h - 1], fill=bg)
    d.rectangle([w // 2 - 34, 12, w // 2 + 34, h - 12], fill=(250, 246, 236, 255))
    d.polygon([(w // 2 - 40, 16), (w // 2, 4), (w // 2 + 40, 16)], fill=NAVY)
    for i in range(3):
        d.rectangle([w // 2 - 24 + i * 18, h // 2 - 4, w // 2 - 12 + i * 18,
                     h - 20], fill=NAVY)
    d.text((w - 58, 8), "65", font=font(SERIF, 24), fill=RED)


def illo_bitcoin(d, w, h, bg):
    d.rectangle([0, 0, w - 1, h - 1], fill=bg)
    cx, cy = w // 4, h // 2
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(240, 170, 30, 255))
    d.text((cx - 9, cy - 14), "₿", font=font(SANS_B, 26), fill=(255, 255, 255, 255))
    d.line([(w // 2, h - 12), (w * 3 // 4, 16), (w - 12, 12)], fill=TEAL, width=3)


def illo_thermo(d, w, h, bg):
    d.rectangle([0, 0, w - 1, h - 1], fill=bg)
    cx, cy = w // 4, h // 2
    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=(90, 140, 170, 255))
    d.arc([cx - 16, cy - 16, cx + 16, cy + 16], 200, 340, fill=(255, 255, 255, 255), width=3)
    d.arc([cx - 16, cy - 16, cx + 16, cy + 16], 20, 160, fill=TEAL, width=3)
    tx = w * 3 // 4
    d.rectangle([tx - 6, 10, tx + 6, h - 22], fill=(255, 255, 255, 255))
    d.rectangle([tx - 6, 10, tx + 6, 22], fill=RED)
    d.ellipse([tx - 12, h - 30, tx + 12, h - 8], fill=RED)
    d.text((tx + 16, 12), "2°C", font=font(SANS_B, 13), fill=RED)


ILLOS = {
    "bars": illo_bars, "tanker": illo_tanker, "eu": illo_eu, "yen": illo_yen,
    "boat": illo_boat, "factory": illo_factory, "chip": illo_chip,
    "shields": illo_shields, "bell": illo_bell, "planes": illo_planes,
    "seats": illo_seats, "bitcoin": illo_bitcoin, "thermo": illo_thermo,
}

ILLO_BG = {
    "bars": (222, 226, 208, 255), "tanker": (214, 222, 228, 255),
    "eu": (226, 228, 232, 255), "yen": (232, 226, 208, 255),
    "boat": (214, 226, 230, 255), "factory": (228, 224, 214, 255),
    "chip": (222, 226, 222, 255), "shields": (232, 226, 214, 255),
    "bell": (226, 230, 224, 255), "planes": (210, 220, 230, 255),
    "seats": (228, 226, 218, 255), "bitcoin": (232, 226, 208, 255),
    "thermo": (222, 226, 228, 255),
}


# ---------------------------------------------------------------- cards
def build_lead_card(idx, item):
    place, conf, source, head, deck, key = item
    w, h = 320, 196
    img = tile(w, h)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=INK, width=1)
    ILLOS[key](d, w, 80, ILLO_BG[key])
    d.line([(0, 80), (w, 80)], fill=INK, width=1)
    kicker_line(d, 8, 86, w - 16, place, place.split("  ·  ")[1], conf)
    y = para(d, 8, 102, head, font(SERIF, 16), INK, w - 16, 18)
    para(d, 8, y + 2, deck, font(SANS, 10), FAINT, w - 16, 12)
    d.text((8, h - 14), "Source: " + source, font=font(SANS, 8), fill=SMOKE)
    save(img, "t_lead%d.png" % idx)


def build_small_card(prefix, idx, item):
    place, conf, source, head, deck, key = item
    w, h = 192, 168
    img = tile(w, h)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=INK, width=1)
    ILLOS[key](d, w, 54, ILLO_BG[key])
    d.line([(0, 54), (w, 54)], fill=INK, width=1)
    kicker_line(d, 6, 58, w - 12, place, place.split("  ·  ")[1], conf)
    y = para(d, 6, 72, head, font(SANS_B, 11), INK, w - 12, 13)
    para(d, 6, y + 1, deck, font(SANS, 9), FAINT, w - 12, 11)
    d.text((6, h - 13), "Source: " + source, font=font(SANS, 8), fill=SMOKE)
    save(img, "t_%s%d.png" % (prefix, idx))


# ---------------------------------------------------------------- strips
def build_numbers():
    img = tile(984, 38)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 983, 37], outline=INK, width=1)
    d.rectangle([0, 0, 130, 37], fill=INK)
    d.text((8, 11), "THE DAY IN NUMBERS", font=font(SANS_B, 11),
           fill=(255, 255, 255, 255))
    cw = (984 - 130) // 6
    for i, (num, label) in enumerate(NUMBERS):
        x = 130 + i * cw + 8
        d.text((x, 3), num, font=font(SERIF, 15), fill=RED)
        d.text((x, 23), label, font=font(SANS, 8), fill=FAINT)
        if i:
            d.line([(130 + i * cw, 5), (130 + i * cw, 32)], fill=LINEC, width=1)
    save(img, "t_numbers.png")


def build_crypto():
    img = tile(984, 28)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 983, 27], fill=RED)
    d.text((10, 5), "CRYPTO NEWS", font=font(SANS_B, 15),
           fill=(255, 255, 255, 255))
    f_p = font(SANS_B, 12)
    f_w = font(SANS, 11)
    parts = [("BTC", "$61,637  +1.87%"), ("ETH", "$1,734  +2.83%"),
             ("SOL", "$73.09  +3.57%")]
    x = 168
    for sym, val in parts:
        d.text((x, 7), sym, font=f_p, fill=(255, 255, 255, 255))
        x += int(d.textlength(sym, font=f_p)) + 6
        d.text((x, 7), val, font=f_w, fill=(255, 255, 255, 255))
        x += int(d.textlength(val, font=f_w)) + 26
    d.text((x, 5), "FEAR & GREED  12 — EXTREME FEAR", font=font(SANS_B, 13),
           fill=(255, 235, 180, 255))
    save(img, "t_crypto.png")


def build_datecheck():
    img = tile(984, 58)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 983, 57], outline=RED, width=2)
    d.text((8, 5), "DATE CHECK — LEFT OUT ON PURPOSE",
           font=font(SANS_B, 11), fill=RED)
    para(d, 8, 21,
         "Kuwait drone attack — 26 Nov, not today (it led yesterday’s paper)  ·  "
         "COP31 collapsed 22 Nov  ·  Trump–Putin post 26 Nov  ·  Macy’s parade "
         "postponed to Sat, not cancelled  ·  Depardieu faces trial, not convicted  ·  "
         "“BTC $93k” is a stale wrong-year page  ·  Sri Lanka A beat India A on 26 Nov",
         font(SANS, 10), INK, 968, 13)
    save(img, "t_datecheck.png")


def build_footer():
    img = tile(984, 14)
    d = ImageDraw.Draw(img)
    d.text((0, 1),
           "HOW SURE:  CONFIRMED = 2+ outlets  ·  OFFICIAL = on the record  ·  "
           "REPORTED = one outlet  ·  CLAIM = one side’s account",
           font=font(SANS, 9), fill=FAINT)
    d.text((984 - 210, 1), "THE WORLD IN ONE DAY  ·  PAGE 1",
           font=font(SANS_B, 9), fill=INK)
    save(img, "t_footer.png")


# ---------------------------------------------------------------- map + list
def build_map():
    img = tile(320, 156)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 319, 155], outline=INK, width=1)
    d.text((8, 5), "WHERE IT HAPPENED", font=font(SANS_B, 10), fill=RED)
    d.text((320 - 118, 5), "PINS = ILLUSTRATED STORIES", font=font(SANS, 8),
           fill=SMOKE)
    land = (198, 188, 158, 255)
    sea = (214, 224, 228, 255)
    d.rectangle([8, 20, 312, 96], fill=sea)
    d.ellipse([18, 30, 92, 62], fill=land)    # N America
    d.ellipse([66, 62, 96, 92], fill=land)    # S America
    d.ellipse([140, 28, 168, 48], fill=land)  # Europe
    d.ellipse([148, 48, 176, 78], fill=land)  # Africa
    d.ellipse([196, 26, 262, 58], fill=land)  # Asia
    d.ellipse([262, 74, 292, 90], fill=land)  # Australia
    pins = [  # (x, y, region colour, place)
        (248, 44, TEAL, "SHANGHAI"), (200, 56, PURPLE, "HORMUZ"),
        (152, 36, NAVY, "BRUSSELS"), (272, 46, TEAL, "TOKYO"),
        (258, 44, TEAL, "SEOUL"), (244, 38, TEAL, "BEIJING"),
        (172, 48, PURPLE, "ANKARA"), (48, 44, RED, "NEW YORK"),
        (166, 32, NAVY, "KYIV"), (292, 86, TEAL, "WELLINGTON"),
    ]
    for x, y, color, _ in pins:
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=color,
                  outline=(255, 255, 255, 255), width=1)
    d.text((8, 100), "ASIA-PACIFIC: Shanghai · Tokyo · Seoul · Beijing · Wellington",
           font=font(SANS_B, 8), fill=TEAL)
    d.text((8, 112), "EUROPE: Brussels · Kyiv", font=font(SANS_B, 8), fill=NAVY)
    d.text((8, 124), "MIDDLE EAST: Hormuz · Ankara", font=font(SANS_B, 8),
           fill=PURPLE)
    d.text((8, 136), "AMERICAS: New York · Bitcoin & climate are global.",
           font=font(SANS_B, 8), fill=RED)
    save(img, "t_map.png")


def build_also():
    img = tile(652, 156)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 651, 155], outline=INK, width=1)
    d.text((8, 5), "ALSO ON FRIDAY 27 NOVEMBER — 22 MORE DATED BRIEFS",
           font=font(SANS_B, 10), fill=RED)
    f_head = font(SANS_B, 9)
    f_src = font(SANS, 8)
    colw = 318
    for i, (place, head, source) in enumerate(ALSO):
        col = i // 11
        row = i % 11
        x = 8 + col * (colw + 8)
        y = 20 + row * 12
        d.ellipse([x, y + 2, x + 5, y + 7], fill=RED)
        src_w = int(d.textlength(source, font=f_src))
        avail = colw - 14 - src_w - 6
        line = place + " — " + head
        while d.textlength(line, font=f_head) > avail and " " in line:
            line = line.rsplit(" ", 1)[0] + "…"
        d.text((x + 9, y), line, font=f_head, fill=INK)
        d.text((x + 9 + int(d.textlength(line, font=f_head)) + 4, y + 1),
               source, font=f_src, fill=SMOKE)
    save(img, "t_also.png")


def build_grain():
    import random
    rnd = random.Random(20261127)
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    px = img.load()
    for y in range(256):
        for x in range(256):
            if rnd.random() < 0.05:
                px[x, y] = (0, 0, 0, 18)
    save(img, "grain_256.png")


def main():
    os.makedirs(ASSETS, exist_ok=True)
    build_masthead()
    build_regions()
    build_utc()
    for i, item in enumerate(LEAD):
        build_lead_card(i, item)
    for i, item in enumerate(MID):
        build_small_card("mid", i, item)
    for i, item in enumerate(LOW):
        build_small_card("low", i, item)
    build_numbers()
    build_map()
    build_also()
    build_crypto()
    build_datecheck()
    build_footer()
    build_grain()
    print("assets done")


if __name__ == "__main__":
    main()
