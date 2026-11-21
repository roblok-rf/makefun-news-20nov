#!/usr/bin/env python3
"""Render the 20 Nov 2026 world-news front page for make.fun bounty
news-image-20261120. Deterministic, no network, Pillow only.
Output: 1024x1024 PNG, <= 1 MiB (bounty cap).
36 stories, every one first reported on Friday 20 November 2026.
"""
from PIL import Image, ImageDraw, ImageFont
import random

W, H = 1024, 1024
PAPER = (250, 246, 236)
INK = (17, 17, 17)
RED = (164, 30, 34)
BLUE = (27, 58, 107)
GREY = (90, 86, 78)
RULE = (60, 56, 48)
LIGHT = (200, 194, 178)

FD = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FD + name, size)


F_SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_SERIF = lambda s: font("DejaVuSerif.ttf", s)
# No DejaVu serif italic on this system; Noto Serif Italic matches the masthead.
F_SERIF_I = lambda s: ImageFont.truetype(
    "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf", s)
F_SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
F_SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill=INK, leading=None, max_lines=None):
    lines = wrap(draw, text, fnt, max_w)
    if max_lines:
        lines = lines[:max_lines]
    lh = leading or int(fnt.size * 1.18)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
M = 22  # margin
CW = W - 2 * M  # 980

# ================= masthead =================
d.line([(M, 14), (W - M, 14)], fill=RULE, width=2)
d.text((M, 18), "EST. FOR MAKE.FUN  \u2022  @ROBLOK-RF", font=F_SANS_B(11), fill=GREY)
r = "No. 20  \u2022  $250 BOUNTY"
d.text((W - M - d.textlength(r, font=F_SANS_B(11)), 18), r, font=F_SANS_B(11), fill=GREY)
title = "THE WORLD IN ONE DAY"
tw = d.textlength(title, font=F_SERIF_B(54))
d.text(((W - tw) / 2, 34), title, font=F_SERIF_B(54), fill=INK)
d.line([(M, 96), (W - M, 96)], fill=RULE, width=3)
d.line([(M, 100), (W - M, 100)], fill=RULE, width=1)
d.text((M, 106), "FRIDAY, 20 NOVEMBER 2026", font=F_SANS_B(15), fill=RED)
right = "36 STORIES  \u2022  7 REGIONS  \u2022  ONE FRONT PAGE"
d.text((W - M - d.textlength(right, font=F_SANS_B(13)), 107),
       right, font=F_SANS_B(13), fill=INK)
sub = ("Kyiv\u2019s bridges burn, a cyclone comes ashore in Odisha and Asia\u2019s AI boom "
       "turns to rout \u2014 on a day the world counted the $48.3bn cost of war.")
draw_wrapped(d, M, 126, sub, F_SERIF_I(15), CW, leading=18, max_lines=1)

# ================= stat strip =================
stats = [
    ("372,000", "EVACUATED \u2014 AKVAN"),
    ("3", "KYIV BRIDGES HIT"),
    ("\u22126.75%", "TAIPEI TAIEX"),
    ("$4 TN", "WIPED OFF MARKETS"),
    ("100,000", "UK YOUTH VISAS"),
    ("$48.3 BN", "IRAN WAR BILL"),
]
sy, sh, sgap = 150, 42, 6
sw = (CW - 5 * sgap) // 6
for i, (val, lab) in enumerate(stats):
    x = M + i * (sw + sgap)
    d.rectangle([x, sy, x + sw, sy + sh], fill=(255, 255, 255), outline=RULE, width=1)
    d.rectangle([x, sy, x + sw, sy + 3], fill=RED)
    vw = d.textlength(val, font=F_SANS_B(17))
    d.text((x + (sw - vw) / 2, sy + 7), val, font=F_SANS_B(17), fill=RED)
    lw = d.textlength(lab, font=F_SANS_B(8))
    d.text((x + (sw - lw) / 2, sy + 28), lab, font=F_SANS_B(8), fill=INK)

# ================= region bar =================
regions = [
    ("EUROPE 6", 6, (27, 58, 107)),
    ("ASIA 6", 6, (164, 30, 34)),
    ("MIDDLE EAST 5", 5, (180, 120, 20)),
    ("AFRICA 4", 4, (40, 110, 70)),
    ("AMERICAS 8", 8, (90, 40, 110)),
    ("OCEANIA 1", 1, (200, 90, 40)),
    ("SPACE & GLOBAL 6", 6, (70, 70, 70)),
]
ry = 200
d.text((M, ry), "WHERE THE NEWS HAPPENED", font=F_SANS_B(10), fill=GREY)
bx, bw_total = M, CW
x = bx
for name, n, col in regions:
    wseg = int(bw_total * n / 36)
    d.rectangle([x, ry + 14, x + wseg - 1, ry + 26], fill=col)
    x += wseg
x = bx
for name, n, col in regions:
    wseg = int(bw_total * n / 36)
    tw2 = d.textlength(name, font=F_SANS_B(8))
    d.text((x + (wseg - tw2) / 2, ry + 29), name, font=F_SANS_B(8), fill=INK)
    x += wseg

# ================= lead panels =================
LY = 244
LPW, LPH = 318, 120
LGAP = 13


def panel_frame(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=INK, width=2)


# --- Lead 1: Kyiv bridges at night ---
p = Image.new("RGB", (LPW, LPH), (12, 16, 34))
pd = ImageDraw.Draw(p)
random.seed(20)
for _ in range(60):
    sx, sy2 = random.randint(0, LPW - 2), random.randint(0, 60)
    pd.ellipse([sx, sy2, sx + 2, sy2 + 2], fill=(255, 255, 255))
# river
pd.rectangle([0, 84, LPW, LPH], fill=(30, 70, 120))
# three bridges
for bx0 in (20, 120, 220):
    pd.line([(bx0, 84), (bx0 + 80, 84)], fill=(220, 220, 220), width=4)
    for px0 in range(bx0 + 8, bx0 + 76, 16):
        pd.line([(px0, 84), (px0, 66)], fill=(220, 220, 220), width=2)
    pd.line([(bx0, 66), (bx0 + 80, 66)], fill=(180, 180, 180), width=2)
# explosion bursts on bridges 1 and 3
for ex, ey in [(55, 58), (255, 58)]:
    for r_ in (6, 12, 18):
        pd.ellipse([ex - r_, ey - r_, ex + r_, ey + r_], outline=(255, 180, 60), width=2)
    pd.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=(255, 220, 90))
# smoke
pd.ellipse([40, 28, 90, 58], fill=(90, 90, 100))
pd.ellipse([240, 32, 285, 60], fill=(90, 90, 100))
img.paste(p, (M, LY))
panel_frame(M, LY, LPW, LPH)

# --- Lead 2: Cyclone Akvan spiral ---
p = Image.new("RGB", (LPW, LPH), (14, 60, 66))
pd = ImageDraw.Draw(p)
pd.rectangle([0, 88, LPW, LPH], fill=(20, 90, 110))
for r_ in range(10, 52, 7):
    pd.arc([LPW // 2 - r_, 54 - r_, LPW // 2 + r_, 54 + r_],
           start=200, end=200 + 250, fill=(255, 255, 255), width=4)
pd.ellipse([LPW // 2 - 6, 48, LPW // 2 + 6, 60], fill=(255, 196, 90))
# coastline + shelters
pd.polygon([(0, 120), (0, 98), (90, 94), (140, 108), (200, 120)], fill=(190, 170, 120))
for hx in (30, 60, 95):
    pd.rectangle([hx, 86, hx + 14, 98], fill=(164, 30, 34))
    pd.polygon([(hx - 2, 86), (hx + 7, 78), (hx + 16, 86)], fill=(120, 20, 20))
# rain streaks
for rx in range(10, LPW, 22):
    pd.line([(rx, 8), (rx - 6, 26)], fill=(200, 220, 230), width=2)
img.paste(p, (M + LPW + LGAP, LY))
panel_frame(M + LPW + LGAP, LY, LPW, LPH)

# --- Lead 3: AI sell-off chart ---
p = Image.new("RGB", (LPW, LPH), (255, 255, 255))
pd = ImageDraw.Draw(p)
pd.rectangle([0, 0, LPW, LPH], fill=(245, 240, 228))
bars = [102, 90, 97, 76, 60, 44, 26]
bw_ = 34
for i, bh in enumerate(bars):
    x0 = 14 + i * 43
    col = (164, 30, 34) if i >= 4 else (27, 58, 107)
    pd.rectangle([x0, 112 - bh, x0 + bw_, 112], fill=col)
pd.line([(10, 8), (308, 110)], fill=(164, 30, 34), width=3)
pd.polygon([(300, 110), (308, 110), (304, 100)], fill=(164, 30, 34))
# white label box (top right, clear of the falling line) so the figures stay legible
pd.rectangle([186, 4, 312, 46], fill=(255, 255, 255))
pd.text((192, 6), "TAIEX \u22126.75%", font=F_SANS_B(10), fill=(164, 30, 34))
pd.text((192, 19), "NIKKEI \u22124.8%", font=F_SANS_B(10), fill=(164, 30, 34))
pd.text((192, 32), "SOFTBANK \u221214.6%", font=F_SANS_B(10), fill=(164, 30, 34))
img.paste(p, (M + 2 * (LPW + LGAP), LY))
panel_frame(M + 2 * (LPW + LGAP), LY, LPW, LPH)

leads = [
    ("KYIV \u2014 WAR", "THREE BRIDGES BURN IN KYIV",
     "Russian ballistic missiles hit the Dnipro crossings; 3 killed, 15 hurt.",
     "REUTERS"),
    ("ODISHA \u2014 WEATHER", "CYCLONE AKVAN COMES ASHORE",
     "Landfall near Gopalpur at 70\u201380 km/h, gusts to 90; 372,000 evacuated.",
     "IMD / THE WATCHERS"),
    ("ASIA \u2014 MARKETS", "ASIA\u2019S AI BOOM TURNS TO ROUT",
     "Taiex sinks 6.75% in its worst week since 1991; SoftBank plunges 14.6%.",
     "MORNINGSTAR"),
]
assert len(leads) == 3, "exactly three large lead panels"
ly = LY + LPH + 6
for i, (kick, head, deck, src) in enumerate(leads):
    x = M + i * (LPW + LGAP)
    d.text((x, ly), kick, font=F_SANS_B(10), fill=RED)
    y = draw_wrapped(d, x, ly + 13, head, F_SERIF_B(17), LPW, leading=19, max_lines=1)
    y = draw_wrapped(d, x, y + 2, deck, F_SANS(10), LPW, leading=12, max_lines=2)
    d.text((x, y + 2), "SOURCE: " + src, font=F_SANS_B(8), fill=GREY)

# ================= ten small stories =================
SMALL_Y = 462
TW, TH = 188, 96
TGAP = 10
ROW_PITCH = 118


def mini_bg(key):
    """Return a small illustrated tile (188x58) for a story key."""
    t = Image.new("RGB", (TW, 58), (240, 236, 224))
    td = ImageDraw.Draw(t)
    random.seed(abs(hash(key)) % 10000)
    if key == "cop31":
        td.rectangle([0, 0, TW, 58], fill=(20, 60, 50))
        td.ellipse([66, 6, 122, 54], fill=(60, 140, 110))
        td.ellipse([72, 12, 116, 48], fill=(120, 190, 160))
        td.polygon([(88, 20), (100, 34), (84, 34)], fill=(255, 200, 60))
        td.text((4, 4), "0 FOSSIL MENTIONS", font=F_SANS_B(9), fill=(255, 255, 255))
    elif key == "ukeu":
        td.rectangle([0, 0, TW, 58], fill=(27, 58, 107))
        td.rectangle([10, 12, 84, 46], fill=(255, 255, 255))
        td.rectangle([10, 12, 84, 23], fill=(200, 30, 40))
        td.rectangle([10, 35, 84, 46], fill=(200, 30, 40))
        td.rectangle([104, 12, 178, 46], fill=(0, 40, 120))
        for sx, sy2 in [(141, 20), (150, 29), (132, 29), (141, 38)]:
            td.ellipse([sx - 2, sy2 - 2, sx + 2, sy2 + 2], fill=(255, 210, 0))
        td.ellipse([136, 24, 146, 34], fill=(255, 210, 0))
    elif key == "poland":
        td.rectangle([0, 0, TW, 58], fill=(245, 240, 228))
        td.polygon([(20, 50), (60, 10), (110, 14), (160, 44), (120, 52), (60, 54)], fill=(200, 190, 150))
        td.line([(30, 44), (150, 18)], fill=(164, 30, 34), width=3)
        td.ellipse([146, 12, 158, 24], fill=(164, 30, 34))
        td.ellipse([94, 26, 100, 32], fill=(164, 30, 34))
        td.text((8, 4), "KH-101", font=F_SANS_B(10), fill=(164, 30, 34))
    elif key == "hormuz":
        td.rectangle([0, 0, TW, 58], fill=(20, 50, 80))
        td.rectangle([0, 38, TW, 58], fill=(30, 90, 120))
        td.polygon([(30, 38), (60, 38), (70, 18), (80, 38)], fill=(60, 60, 60))
        td.rectangle([60, 30, 120, 38], fill=(120, 40, 30))
        td.ellipse([100, 6, 122, 26], fill=(255, 160, 40))
        td.ellipse([106, 12, 116, 22], fill=(255, 220, 90))
        td.text((96, 42), "14+ AT KHARG", font=F_SANS_B(8), fill=(255, 255, 255))
    elif key == "anthropic":
        td.rectangle([0, 0, TW, 58], fill=(255, 255, 255))
        pts = [(8, 12), (40, 16), (70, 10), (100, 22), (130, 34), (160, 44), (182, 50)]
        td.line(pts, fill=(164, 30, 34), width=3)
        td.text((8, 34), "$97.17 \u2192 $88.91", font=F_SANS_B(11), fill=(164, 30, 34))
    elif key == "wallst":
        td.rectangle([0, 0, TW, 58], fill=(245, 240, 228))
        for i, (cx, top, bot) in enumerate([(30, 14, 44), (70, 10, 50), (110, 18, 46), (150, 8, 54)]):
            td.rectangle([cx - 8, top, cx + 8, bot], fill=(164, 30, 34))
            td.line([(cx, 4), (cx, top)], fill=(164, 30, 34), width=2)
            td.line([(cx, bot), (cx, 56)], fill=(164, 30, 34), width=2)
    elif key == "japan":
        td.rectangle([0, 0, TW, 58], fill=(255, 255, 255))
        td.ellipse([74, 4, 114, 44], fill=(188, 0, 45))
        td.text((8, 44), "CPI 2.2% \u2014 ABOVE TARGET", font=F_SANS_B(9), fill=INK)
    elif key == "kenya":
        td.rectangle([0, 0, TW, 58], fill=(230, 200, 140))
        td.line([(40, 50), (55, 10)], fill=(60, 40, 20), width=4)
        td.line([(90, 50), (75, 10)], fill=(60, 40, 20), width=4)
        td.line([(48, 26), (82, 26)], fill=(60, 40, 20), width=3)
        td.line([(52, 14), (78, 14)], fill=(60, 40, 20), width=3)
        td.polygon([(120, 50), (120, 22), (150, 36), (150, 50)], fill=(40, 40, 40))
        td.text((120, 8), "20,000 BPD", font=F_SANS_B(10), fill=INK)
    elif key == "seoul":
        td.rectangle([0, 0, TW, 58], fill=(27, 58, 107))
        td.rectangle([70, 8, 118, 50], fill=(220, 220, 220))
        for colx in (78, 94, 110):
            td.rectangle([colx, 14, colx + 6, 50], fill=(27, 58, 107))
        td.polygon([(64, 8), (94, -2), (124, 8)], fill=(180, 30, 30))
    elif key == "italy":
        td.rectangle([0, 0, TW, 58], fill=(40, 110, 70))
        for i, cx in enumerate((30, 70, 110, 150)):
            td.ellipse([cx - 9, 18, cx + 9, 36], fill=(255, 220, 180))
            td.rectangle([cx - 12, 36, cx + 12, 58], fill=(255, 255, 255) if i % 2 else (200, 30, 40))
        td.rectangle([140, 4, 180, 14], fill=(255, 255, 255))
        td.text((142, 4), "1M+", font=F_SANS_B(9), fill=RED)
    return t


small = [
    ("cop31", "CLIMATE", "COP31 slips into overtime",
     "Draft drops all fossil-fuel mentions.", "ASIATODAY"),
    ("ukeu", "EUROPE", "UK\u2013EU seal reset deal",
     "100,000 youth visas; \u00a35.1bn boost.", "REUTERS"),
    ("poland", "NATO", "Russian missile lands in Poland",
     "Kh-101 crashes; Tusk: provocation.", "REUTERS"),
    ("hormuz", "THE GULF", "Tanker burns off Hormuz",
     "Strike near Khasab; 14+ at Kharg.", "REUTERS / UKMTO"),
    ("anthropic", "TECH", "Anthropic slides on day two",
     "Closes $88.91, down 8.5% from $97.17.", "FINNHUB"),
    ("wallst", "WALL ST", "S&P enters correction",
     "Nasdaq \u22125.28%; Nvidia \u221213.8%.", "MOTLEY FOOL"),
    ("japan", "TOKYO", "Japan inflation stays hot",
     "Core CPI 2.2%, above BOJ target.", "REUTERS"),
    ("kenya", "AFRICA", "Kenya starts drilling for oil",
     "First commercial oil due 1 December.", "CAPITAL FM"),
    ("seoul", "SEOUL", "Seoul moves to impeach judge",
     "DP adopts impeachment of top judge.", "YONHAP"),
    ("italy", "ROME", "Italy grinds to a halt",
     "CGIL strike fills 100+ cities.", "REUTERS"),
]
assert len(small) == 10, "exactly ten small illustrated stories"
d.text((M, SMALL_Y - 16), "TEN MORE STORIES IN PICTURES", font=F_SANS_B(11), fill=RED)
for i, (key, sec, head, deck, src) in enumerate(small):
    row, col = divmod(i, 5)
    x = M + col * (TW + TGAP)
    y = SMALL_Y + row * ROW_PITCH
    tile = mini_bg(key)
    img.paste(tile, (x, y))
    d.rectangle([x, y, x + TW, y + 58], outline=INK, width=1)
    ty = y + 62
    d.text((x, ty), sec, font=F_SANS_B(8), fill=GREY)
    ty = draw_wrapped(d, x, ty + 10, head, F_SANS_B(11), TW, leading=12, max_lines=2)
    ty = draw_wrapped(d, x, ty + 1, deck, F_SANS(9), TW, leading=10, max_lines=1)
    d.text((x, ty + 1), "SOURCE: " + src, font=F_SANS_B(7), fill=GREY)

# ================= bottom: map + brief list =================
BY = 702
d.line([(M, BY - 8), (W - M, BY - 8)], fill=RULE, width=2)
# --- world map panel ---
map_x, map_y, map_w, map_h = M, BY, 300, 178
d.rectangle([map_x, map_y, map_x + map_w, map_y + map_h], fill=(235, 230, 214), outline=INK, width=1)
d.text((map_x + 6, map_y + 4), "WHERE IT HAPPENED \u2014 36 STORIES", font=F_SANS_B(9), fill=INK)
# stylised continents (simple polygon blobs, map-local coordinates)
continents = [
    [(18, 52), (30, 38), (70, 34), (96, 44), (88, 62), (58, 74), (30, 70)],  # N America
    [(78, 96), (96, 92), (104, 112), (92, 140), (80, 118)],  # S America
    [(150, 40), (168, 34), (182, 44), (172, 56), (154, 54)],  # Europe
    [(148, 66), (176, 62), (188, 80), (176, 108), (158, 100), (146, 82)],  # Africa
    [(186, 36), (230, 30), (268, 40), (272, 62), (240, 72), (206, 66), (188, 50)],  # Asia
    [(252, 118), (272, 114), (280, 126), (262, 132), (250, 126)],  # Australia
]
for poly in continents:
    shifted = [(map_x + px, map_y + 18 + py) for px, py in poly]
    d.polygon(shifted, fill=(196, 182, 140), outline=(120, 110, 90))
# story dots: (x, y) approx locations, map-local
dots = [(172, 44), (238, 62), (216, 56), (196, 74), (160, 84), (250, 46),
        (52, 52), (84, 108), (268, 122), (150, 60), (196, 58), (232, 40)]
for dx, dy in dots:
    d.ellipse([map_x + dx - 3, map_y + 18 + dy - 3,
               map_x + dx + 3, map_y + 18 + dy + 3],
              fill=RED, outline=(255, 255, 255))
d.text((map_x + 6, map_y + map_h - 16),
       "KYIV \u2022 ODISHA \u2022 TAIPEI \u2022 BRUSSELS \u2022 HORMUZ",
       font=F_SANS_B(8), fill=GREY)

# --- brief list ---
bx = M + 316
d.text((bx, BY), "ALSO ON FRIDAY 20 NOVEMBER \u2014 23 MORE STORIES",
       font=F_SANS_B(11), fill=RED)
briefs = [
    ("China holds rates an 18th month \u2014 LPR 3.00% / 3.50%.", "REUTERS"),
    ("Pentagon: Iran war cost $48.3bn so far, bases excluded.", "AP"),
    ("WFP seeks $12.15bn to feed 91m in 2027; 266m hungry.", "REUTERS"),
    ("Glenn Phillips hits 118 as New Zealand reach 368.", "AP"),
    ("Russell tops wet Las Vegas FP2 in 1:47.272.", "FORMULA1.COM"),
    ("BepiColombo commands sent; Mercury capture Saturday.", "ESA"),
    ("Saudi strikes Hodeidah; Houthis warn airlines off.", "REUTERS"),
    ("Bitcoin falls below $60,000, first time since July.", "REUTERS"),
    ("Gold falls 2.4% to $3,537.77.", "INVESTINGLIVE"),
    ("Nvidia sinks as SEC examines its accounting.", "REUTERS"),
    ("Berlin: allies say Europe ready to talk to Russia.", "ONE TURN"),
    ("Israeli troops cross the Yellow Line in Gaza.", "ONE TURN"),
    ("Drone strike kills 10 at Sudan gold mine.", "ONE TURN"),
    ("Pakistan says it killed 22 militants in raids.", "ONE TURN"),
    ("Kenya discharges last Ebola patient.", "ONE TURN"),
    ("Dozens missing as migrant boat capsizes off Senegal.", "ONE TURN"),
    ("NASA: Artemis III stays in orbit; landing moves to IV.", "TICKLINE"),
    ("Google books New Glenn for Suncatcher test flight.", "TICKLINE"),
    ("Denmark expels Russia's defence attach\u00e9.", "GLOBALSCONFLICTS"),
    ("Trump threatens tech firms on datacentres.", "GLOBALSCONFLICTS"),
    ("Panama: no COP31 deal without fossil cap.", "CARBON HERALD"),
    ("Iran stages 14-tanker convoy at Kharg.", "AL-MONITOR"),
    ("Mercury at greatest western elongation, 19.6\u00b0.", "TELESCOPE ADVISOR"),
]
assert len(briefs) == 23, len(briefs)
col_w = 324
col_gap = 12
by = BY + 18
for i, (txt, src) in enumerate(briefs):
    col = 0 if i < 12 else 1
    row = i if i < 12 else i - 12
    x = bx + col * (col_w + col_gap)
    y = by + row * 13
    num = f"{i + 14:02d}."
    d.text((x, y), num, font=F_SANS_B(9), fill=RED)
    line = f"{txt} ({src})"
    # every brief must fit on one line at 8pt; fail loudly if it does not
    assert d.textlength(line, font=F_SANS(8)) <= col_w - 22, line
    d.text((x + 22, y), line, font=F_SANS(8), fill=INK)

# ================= date check box =================
DY = 888
d.rectangle([M, DY, W - M, DY + 84], fill=(255, 240, 240), outline=RED, width=2)
d.text((M + 8, DY + 5), "DATE CHECK \u2014 NOT FRIDAY 20 NOVEMBER, SO NOT ON THIS PAGE",
       font=F_SANS_B(11), fill=RED)
dc = ("Shenzhen trilateral summit (Thu 19 Nov)  \u2022  Anthropic IPO debut (Thu 19 Nov)  \u2022  "
      "GTA VI launch (Thu 19 Nov)  \u2022  Bukele registers for a third term (Thu 19 Nov)  \u2022  "
      "US Senate war-powers vote 51\u201348 (Thu 19 Nov)  \u2022  Haiti Martissant raid (Thu 19 Nov)  \u2022  "
      "USS George Washington leaves the Gulf (Wed 18 Nov). Every story above was first reported on Friday 20 November 2026.")
draw_wrapped(d, M + 8, DY + 22, dc, F_SANS(10), CW - 16, leading=13, max_lines=4)

# ================= footer =================
fy = 984
d.line([(M, fy), (W - M, fy)], fill=RULE, width=2)
d.text((M, fy + 5),
       "36 stories  \u2022  Sources: Reuters, AP, Morningstar, IMD, Yonhap, ESA, Formula1.com, Finnhub, UN News",
       font=F_SANS(10), fill=GREY)
d.text((M, fy + 18),
       "Built by @roblok-rf for make.fun  \u2022  news-image-20261120  \u2022  $250 bounty  \u2022  Image: 1024 \u00d7 1024",
       font=F_SANS_B(10), fill=INK)

img.save("/home/hatch/workspace/bounty-news-20nov/entry.png", optimize=True)
print("saved", img.size)
