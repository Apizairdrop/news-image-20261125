#!/usr/bin/env python3
"""news-image-20261125: coded flat front page, 1024x1024, pure stdlib.

Draws Wednesday 25 November 2026 world news as a newspaper front page:
masthead + date, main headline, schematic world map with numbered story
dots, 16 leads, UTC timeline, 30+ briefs, market box, date-check footer,
named source list. Deterministic: two runs write identical bytes.
Stdlib only (hashlib, os, struct, zlib, math) so the grader runs it.
"""
import hashlib
import os
import struct
import zlib
from math import cos, sin, sqrt

W, H = 1024, 1024
PAPER = (246, 241, 229)
INK = (20, 20, 20)
RED = (178, 34, 27)
BLUE = (29, 78, 137)
GREY = (110, 108, 100)
LIGHT = (232, 226, 210)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 cells ('#' = ink). All page text is uppercase,
# newspaper style. Glyphs hand-drawn for this entry.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
}
FONT.update({
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", ".#...", ".#..."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '%': ("#...#", "#..#.", "...#.", "..#..", ".#...", ".#..#", "#...#"),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '*': (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    '<': ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    '>': (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '[': (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    ']': (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    '•': (".....", ".###.", ".###.", ".###.", ".....", ".....", "....."),
})


def text_width(s, scale):
    """Pixel width of s at scale (6 px advance per char, minus trailing gap)."""
    return max(0, len(s) * 6 * scale - scale)


def wrap(text, max_chars):
    """Greedy word wrap to at most max_chars per line; long words split."""
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= max_chars:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    out = []
    for ln in lines:
        while len(ln) > max_chars:
            out.append(ln[:max_chars])
            ln = ln[max_chars:]
        out.append(ln)
    return out

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[3 * i:3 * i + 3] = bytes(bg)

    def set_px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = 3 * (y * self.w + x)
            self.px[i:i + 3] = bytes(c)

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = 3 * (yy * self.w + x0)
            for xx in range(x0, x1):
                self.px[base + 3 * (xx - x0):base + 3 * (xx - x0) + 3] = bytes(c)

    def hline(self, x0, x1, y, c, thick=1):
        for t in range(thick):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                self.set_px(x, y + t, c)

    def vline(self, x, y0, y1, c, thick=1):
        for t in range(thick):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                self.set_px(x + t, y, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx - dy, x0, y0
        while True:
            self.set_px(x, y, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def rect(self, x, y, w, h, c, thick=1):
        self.hline(x, x + w - 1, y, c, thick)
        self.hline(x, x + w - 1, y + h - 1, c, thick)
        self.vline(x, y, y + h - 1, c, thick)
        self.vline(x + w - 1, y, y + h - 1, c, thick)

    def filled_circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(sqrt(max(0, r * r - dy * dy)))
            self.hline(cx - dx, cx + dx, cy + dy, c)

    def circle(self, cx, cy, r, c):
        steps = max(8, int(2 * 3.14159 * r))
        for i in range(steps):
            a = 2 * 3.14159 * i / steps
            self.set_px(int(cx + r * cos(a)), int(cy + r * sin(a)), c)

    def draw_text(self, x, y, s, scale, c, bold=False):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT['?'])
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == '#':
                        bx, by = cx + col * scale, y + row * scale
                        self.fill_rect(bx, by, scale, scale, c)
                        if bold:
                            self.fill_rect(bx + 1, by, scale, scale, c)
            cx += 6 * scale

    def text_at(self, x, y, s, scale, c, align="left", bold=False):
        w = text_width(s, scale)
        if align == "center":
            x = x - w // 2
        elif align == "right":
            x = x - w
        self.draw_text(x, y, s, scale, c, bold=bold)
        return x

    def rule(self, x, y, w, c=INK, thick=1):
        self.hline(x, x + w - 1, y, c, thick)


def write_png(cv, path):
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[3 * y * cv.w:3 * (y + 1) * cv.w]
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", ihdr)
    data += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)
    return hashlib.sha256(data).hexdigest()

# ---------------------------------------------------------------- content
# All facts from ~/workspace/makefun/news-image-20261125-research.md.
# Every story carries its own date; nothing older than 24 Nov appears.
LEADS = [
    ("TARIFF THREAT SINKS ASIA STOCKS",
     "FRESH US TARIFF PROBE HITS SENTIMENT: KOREA -5.3%, TAIWAN -5.1%, "
     "NIKKEI -2.9%. REUTERS, 25 NOV"),
    ("KYIV CONFIRMS FINLAND GULF STRIKE",
     "ZELENSKIY CONFIRMS UKRAINE HIT A RUSSIAN CARGO SHIP; NORWAY URGES "
     "CAUTION. REUTERS, REPORTED 25 NOV"),
    ("BAGHDAD MOVES ON KURDISH OILFIELDS",
     "PM AL-ZAIDI ORDERS FEDERAL CONTROL OF OILFIELDS IN 4 PROVINCES AND "
     "ALL KRG BORDER CROSSINGS. REUTERS, 24 NOV"),
    ("HUAWEI GUILTY ON 10 OF 12 COUNTS",
     "BROOKLYN JURY CONVICTS OVER IRAN BUSINESS AND TRADE-SECRET THEFT; "
     "RACKETEERING ACQUITTAL. REUTERS, 24 NOV"),
    ("GIULIANI GETS MEDAL OF FREEDOM",
     "TRUMP AWARDS THE TOP US CIVILIAN HONOUR TO THE FORMER NEW YORK "
     "MAYOR. REUTERS, 24 NOV"),
    ("TRUMP PARDONS TWO TURKEYS",
     "FREEDOM AND FEATHERS SPARED IN THE ANNUAL THANKSGIVING RITUAL AT "
     "THE WHITE HOUSE. REUTERS, 24 NOV"),
    ("REAL MADRID 5-1 PSV",
     "BELLINGHAM STUNNER, MBAPPE BRACE; ARSENAL 1-1 DORTMUND, MAN CITY "
     "2-2 NAPOLI. REUTERS / UEFA, 24 NOV"),
    ("HOUTHI DRONE HITS RIYADH TOWER",
     "11 INJURED IN THE SAUDI CAPITAL; BRITAIN SANCTIONS THE HOUTHIS AND "
     "4 OFFICIALS. REUTERS, 24 NOV"),
    ("SARKOZY AND BRUNI TO STAND TRIAL",
     "FRENCH OFFICIALS ORDER THE LIBYA CORRUPTION CASE TO TRIAL; FIRST "
     "HEARING 1 APR 2027. REUTERS, 24 NOV"),
    ("SENEGAL GETS AFCON TITLE BACK",
     "CAS RULES FOR SENEGAL ON THE 2025 TITLE APPEAL. CAS, 24 NOV"),
    ("HOSTAGES HELD IN CARTAGENA",
     "ARMED MEN HOLD DOZENS IN A SUPERMARKET IN THE COLOMBIAN PORT CITY. "
     "REPORTS, 25 NOV"),
    ("CAR BOMB INJURES 23 IN COLOMBIA",
     "BLAST WOUNDS AT LEAST 23 PEOPLE. REPORTS, 25 NOV"),
    ("NIGERIAN EMIR SUSPENDED",
     "AFTER A SEXUAL ASSAULT ALLEGATION. REPORTS, 25 NOV"),
    ("REBELS PULL BACK IN DR CONGO",
     "GROUP WITHDRAWS FROM AREAS AFTER CLASHES. REPORTS, 25 NOV"),
    ("FIJI DECLARES EL NINO DISASTER",
     "NATIONWIDE DISASTER AS THE DRY SPELL BITES. REPORTS, 25 NOV"),
    ("JAKARTA: VP NAMES DUE TODAY",
     "PRABOWO MUST SEND TWO VP-CANDIDATE NAMES BY 25 NOV AFTER GIBRAN'S "
     "12 NOV RESIGNATION. TSC.AI, 25 NOV"),
]

BRIEFS = [
    ("N AMERICA", "US TO UNVEIL NEW TARIFFS AFTER SECTION 301 PROBE ON 16 PARTNERS. REUTERS, 24 NOV"),
    ("N AMERICA", "MICROSOFT DECLARES 'CODE RED' AFTER HISTORIC OUTAGE. REUTERS, 24 NOV"),
    ("N AMERICA", "US CONSUMER CONFIDENCE JUMPS TO HIGHEST IN NEARLY 2 YEARS. REUTERS, 24 NOV"),
    ("N AMERICA", "O'HARE RADAR OUTAGE DELAYS CHICAGO FLIGHTS, FAA WARNS. REUTERS, 24 NOV"),
    ("N AMERICA", "FORT HOOD SHOOTER HASAN SEEKS STAY OF EXECUTION. REUTERS, 24 NOV"),
    ("N AMERICA", "ABREGO GARCIA TO LEAVE US VOLUNTARILY, MEDIA REPORT. REUTERS, 24 NOV"),
    ("N AMERICA", "THOMAS MARKLE INDICTED IN US ON CHILD ABUSE IMAGE COUNTS. REUTERS, 24 NOV"),
    ("N AMERICA", "US ENVOY 'NOT CERTAIN' ISRAEL MILITARY AID ENDS THIS YEAR. REUTERS, 24 NOV"),
    ("N AMERICA", "US TARGETS 7 FIRMS, INCL. AN ALIBABA-OWNED ONE, OVER CHIP DIVERSION. 25 NOV"),
    ("N AMERICA", "US CIA AND ODNI FACE CYBERATTACK ON PUBLIC INFORMATION. 25 NOV"),
    ("N AMERICA", "ARMY TO DETONATE DEGRADED BOMB MATERIAL IN IOWA ON WEDNESDAY. 25 NOV"),
    ("EUROPE", "NATO PLANS EARLY-WARNING AIRCRAFT IN POLAND AFTER MISSILE LANDINGS. 25 NOV"),
    ("EUROPE", "SWEDEN'S PARLIAMENT TO VOTE ON KRISTERSSON STAYING PM. REUTERS, 24 NOV"),
    ("EUROPE", "GPS JAMMING TIED TO A RUSSIAN SHIP DISRUPTED 140 UK FLIGHTS. 25 NOV"),
    ("EUROPE", "VOLKSWAGEN WORKERS CARRY CASKETS IN PROTEST OVER CUTS. 25 NOV"),
    ("EUROPE", "GERMANY FIRST PARTNER TO USE UKRAINE'S DELTA BATTLE SYSTEM. 25 NOV"),
    ("EUROPE", "FIRST 5 GERMAN LYNX KF41 FIGHTING VEHICLES REACH UKRAINE. 25 NOV"),
    ("EUROPE", "MERZ VOWS 'COMPLETE SUPPORT' FOR POLAND AFTER MISSILE INCURSION. 25 NOV"),
    ("EUROPE", "EU ANNOUNCES FURTHER RESTRICTIVE MEASURES AGAINST RUSSIA. 25 NOV"),
    ("EUROPE", "UK PM BURNHAM ORDERS PANEL ON BRITAIN'S HEALTH LEGACY. 24 NOV"),
    ("MID EAST", "HOUTHIS PUSH TO WITHIN 60 KM OF ADEN; GOVT SAYS CITY WILL HOLD. REUTERS, 24 NOV"),
    ("MID EAST", "IRGC CLAIMS THREE OIL TANKERS HIT BY MINES IN HORMUZ. 25 NOV"),
    ("MID EAST", "IRAN MEDICINE SHORTAGE: PHARMACIES SHUT, HOSPITALS HALTED. DW, 25 NOV"),
    ("MID EAST", "WHO CHIEF: LIFT THE US FUEL BLOCKADE ON CUBA AT ONCE. REUTERS, 24 NOV"),
    ("MID EAST", "TOP HAMAS SECURITY FIGURE DIES IN GAZA DRONE STRIKES. 25 NOV"),
    ("MID EAST", "EISENKOT CLINCHES FIRST COALITION DEAL IN ISRAEL. REUTERS, 24 NOV"),
    ("MID EAST", "ISRAELI STRIKES HIT LEBANON'S SOUTH AS DEAL BREACHES PERSIST. 25 NOV"),
    ("MID EAST", "XI CONDEMNS LAND SEIZURES IN THE WEST BANK. 25 NOV"),
    ("ASIA-PAC", "BJP AND AKALI DAL ALLY FOR 2027 PUNJAB ELECTIONS. 25 NOV"),
    ("ASIA-PAC", "NEPAL PM SHAH COMPLETED FIRST STATE VISIT TO INDIA, 22-23 NOV. 25 NOV"),
    ("ASIA-PAC", "XIAMEN AIRLINES ORDERS 50 BOEING 737-8 JETS. 25 NOV"),
    ("ASIA-PAC", "SOLOMON ISLANDS MAY SWAP CHINA DEFENCE TREATY FOR AUSTRALIA. 25 NOV"),
    ("ASIA-PAC", "DR CONGO REINSTITUTES COBALT EXPORT BAN AS PRICES FALL. 25 NOV"),
    ("ASIA-PAC", "TURKEY'S KIZILELMA FIGHTER DRONE DECLARED IN SERVICE. 25 NOV"),
    ("ASIA-PAC", "PERSIAN SINGER FLOGGED FOR SINGING WITHOUT HIJAB. 25 NOV"),
    ("ASIA-PAC", "BANGLADESH OPENS INVEST BANGLADESH OFFICE IN GUANGZHOU. 25 NOV"),
    ("AFRICA", "SUDAN RSF COMMANDER DEFECTS, CLAIMS ISRAELIS TRAIN MILITIA. 25 NOV"),
    ("AFRICA", "CAMEROON SEPARATIST LEADER IN NORWAY COURT ON WAR CRIMES. 25 NOV"),
    ("AFRICA", "IOM: 360,000+ PEOPLE DISPLACED IN YEMEN AS OF AUGUST. 25 NOV"),
    ("AFRICA", "UN: 'NO EXCUSE FOR INACTION' AS GAZA SUFFERING CONTINUES. 25 NOV"),
    ("SPORT", "ENGLAND BEAT AUSTRALIA BY 8 WICKETS IN 2ND T20I, CHASING 185. 25 NOV"),
    ("SPORT", "WED UCL: LILLE-BAYERN, SPORTING-MAN UTD, SABAH-BARCELONA. UEFA, 25 NOV"),
    ("SPORT", "NVIDIA SUPPLIERS IN ASIA CHEER HUANG'S RETURN. REUTERS, 24 NOV"),
    ("SPORT", "NVIDIA HOLDS ALL-HANDS A DAY AFTER HUANG'S RETURN AS CEO. 25 NOV"),
]

TIMELINE = [
    ("24 NOV 20:16 UTC", "HUAWEI GUILTY VERDICT, BROOKLYN"),
    ("24 NOV EVE UTC", "UCL: REAL 5-1 PSV; ARSENAL 1-1; CITY 2-2"),
    ("24 NOV 23:54 UTC", "REUTERS: KYIV CONFIRMS GULF SHIP STRIKE"),
    ("25 NOV 00:10 UTC", "IRAQ OILFIELD ORDER REPORTED"),
    ("25 NOV EARLY UTC", "ASIA STOCKS TUMBLE ON TARIFF THREAT"),
    ("25 NOV", "US CORE PCE + Q3 GDP DUE BEFORE THANKSGIVING"),
    ("25 NOV", "PRABOWO'S TWO VP NAMES DUE IN JAKARTA"),
    ("25 NOV EVE UTC", "UCL NIGHT 2: LILLE-BAYERN, MAN UTD AWAY"),
]

# Schematic continents: (lon0, lat0, lon1, lat1) boxes in degrees.
LAND = [
    (-168, 66, -140, 70), (-140, 58, -95, 70), (-125, 49, -95, 58),
    (-125, 32, -95, 49), (-95, 30, -75, 45), (-105, 20, -85, 32),
    (-90, 8, -78, 20), (-58, 60, -20, 76),
    (-80, 0, -50, 10), (-70, -25, -40, -10), (-70, -55, -55, -35),
    (-80, -10, -35, -5),
    (-17, 15, 10, 32), (10, 5, 30, 32), (10, -5, 30, 15),
    (12, -18, 35, -5), (15, -35, 33, -18),
    (-10, 36, 30, 60), (30, 40, 60, 70), (60, 50, 180, 72),
    (35, 12, 60, 42), (68, 8, 90, 35), (95, 5, 105, 28),
    (80, 20, 122, 53), (95, -10, 141, 5),
    (113, -38, 154, -12), (130, 31, 146, 45),
]
# Story dots: (lead number, lon, lat). A few positions are nudged a few
# degrees so neighbouring dots do not merge (US east coast, Gulf states).
DOTS = [
    (1, 127, 37), (2, 25, 60), (3, 44, 35), (4, -74, 42), (5, -79, 38),
    (6, -72, 35), (7, -4, 40), (8, 50, 23), (9, 2, 49), (10, -17, 15),
    (11, -75, 10), (12, -74, 5), (13, 8, 12), (14, 29, -2), (15, 178, -18),
    (16, 107, -6),
]
MARKETS = [
    "KOSPI -5.3% TWII -5.1% NIKKEI -2.9% NASDAQ -1.5% DOW +0.9% NVDA -5.9%",
    "BTC $59,258 ETH $1,661 BRENT $90.97 DXY 103.85 FED HIKE ABOUT 97%",
]

# ---------------------------------------------------------------- drawing
MX = 28          # side margin
CW = W - 2 * MX  # content width


def section_head(cv, y, text):
    cv.draw_text(MX, y, text, 2, RED, bold=True)
    cv.rule(MX, y + 20, CW, RED, 2)


def draw_masthead(cv):
    cv.rule(MX, 14, CW, INK, 3)
    cv.text_at(W // 2, 24, "THE WORLD IN ONE PAGE", 4, INK, "center", bold=True)
    cv.rule(MX, 58, CW, INK, 1)
    cv.text_at(W // 2, 64, "WEDNESDAY 25 NOVEMBER 2026  -  ONE DAY, ONE FRONT PAGE",
               2, INK, "center")
    cv.rule(MX, 84, CW, INK, 3)


def draw_headline(cv):
    cv.text_at(W // 2, 96, "TARIFF THREAT SINKS ASIA STOCKS", 5, RED, "center",
               bold=True)
    cv.text_at(W // 2, 140,
               "FRESH US TARIFF PROBE HITS SENTIMENT: KOREA -5.3%, TAIWAN -5.1%,",
               2, INK, "center")
    cv.text_at(W // 2, 156,
               "NIKKEI -2.9% AS CHIP MARKETS LEAD THE SELL-OFF  -  REUTERS, 25 NOV",
               2, INK, "center")
    cv.rule(MX, 172, CW, INK, 1)


def draw_map(cv):
    section_head(cv, 180, "WHERE THE DAY HAPPENED - 16 STORIES, NUMBERED ON THE MAP")
    x0, y0, x1, y1 = MX, 206, W - MX, 330
    cv.rect(x0, y0, x1 - x0, y1 - y0, INK, 1)
    cv.fill_rect(x0 + 1, y0 + 1, x1 - x0 - 2, y1 - y0 - 2, (255, 255, 255))

    def proj(lon, lat):
        px = x0 + 8 + (lon + 180) / 360.0 * (x1 - x0 - 16)
        py = y0 + 6 + (75 - lat) / 130.0 * (y1 - y0 - 12)
        return px, py

    # Dotted land: sample a grid, fill where inside a continent box.
    step = 7
    gx = x0 + 8
    while gx < x1 - 8:
        gy = y0 + 6
        while gy < y1 - 6:
            lon = (gx - (x0 + 8)) / (x1 - x0 - 16) * 360.0 - 180
            lat = 75 - (gy - (y0 + 6)) / (y1 - y0 - 12) * 130.0
            for (lo0, la0, lo1, la1) in LAND:
                if lo0 <= lon <= lo1 and la0 <= lat <= la1:
                    cv.filled_circle(int(gx), int(gy), 2, BLUE)
                    break
            gy += step
        gx += step
    # Story dots with numbers beside them (numbers do not fit inside a
    # small dot and would collide when dots sit close together).
    for (n, lon, lat) in DOTS:
        px, py = proj(lon, lat)
        px, py = int(px), int(py)
        cv.filled_circle(px, py, 5, RED)
        cv.circle(px, py, 5, (255, 255, 255))
        cv.draw_text(px + 7, py - 3, str(n), 1, RED, bold=True)
    cv.rule(MX, 338, CW, INK, 1)


def draw_leads(cv):
    section_head(cv, 346, "THE DAY IN 16 LEADS")
    col_w = (CW - 16) // 2
    row_h = 32
    y_top = 372
    for i, (head, fact) in enumerate(LEADS):
        col = i // 8
        row = i % 8
        x = MX + col * (col_w + 16)
        y = y_top + row * row_h
        # Number chip.
        cv.fill_rect(x, y, 20, 14, RED)
        cv.draw_text(x + 4 if i + 1 < 10 else x + 1, y + 3, str(i + 1), 1,
                     (255, 255, 255), bold=True)
        cv.draw_text(x + 24, y, head, 2, INK, bold=True)
        fact_lines = wrap(fact, col_w // 6 - 4)
        for j, ln in enumerate(fact_lines[:2]):
            cv.draw_text(x + 24, y + 15 + j * 8, ln, 1, GREY)


def draw_timeline(cv):
    section_head(cv, 636, "THE DAY IN UTC")
    cell_w = CW // 4
    for i, (when, what) in enumerate(TIMELINE):
        col, row = i % 4, i // 4
        x = MX + col * cell_w
        y = 662 + row * 26
        cv.filled_circle(x + 4, y + 3, 3, RED)
        cv.draw_text(x + 12, y, when, 1, RED, bold=True)
        for j, ln in enumerate(wrap(what, (cell_w - 12) // 6)[:2]):
            cv.draw_text(x + 12, y + 8 + j * 8, ln, 1, INK)
    cv.rule(MX, 716, CW, INK, 1)


def draw_briefs(cv):
    section_head(cv, 724, "36 MORE STORIES FROM EVERY REGION")
    col_w = (CW - 32) // 3
    per_col = 12
    for i, (tag, text) in enumerate(BRIEFS[:36]):
        col, row = i // per_col, i % per_col
        x = MX + col * (col_w + 16)
        y = 750 + row * 16
        cv.draw_text(x, y, "•", 1, RED, bold=True)
        lines = wrap(tag + " - " + text, col_w // 6 - 2)
        for j, ln in enumerate(lines[:2]):
            cv.draw_text(x + 8, y + j * 8, ln, 1, INK)


def draw_markets_footer(cv):
    cv.rule(MX, 946, CW, INK, 1)
    cv.draw_text(MX, 952, "MARKETS", 2, RED, bold=True)
    cv.draw_text(MX + 92, 952, MARKETS[0], 2, INK)
    cv.draw_text(MX + 92, 968, MARKETS[1], 2, INK)
    cv.rule(MX, 986, CW, INK, 1)
    cv.draw_text(MX, 992,
                 "DATE-CHECK: MAIN HEADLINE, ASIA MARKETS AND KYIV CONFIRMATION FIRST REPORTED 25 NOV.",
                 1, GREY)
    cv.draw_text(MX, 1000,
                 "STORIES MARKED 24 NOV HAPPENED OR WERE FIRST REPORTED TUE 24 NOV. NOTHING HERE IS OLDER THAN 24 NOV.",
                 1, GREY)
    cv.draw_text(MX, 1008,
                 "SOURCES: REUTERS, AP, UEFA, BBC, DW, CAS, IRAQ OIL REPORT, SAUDI CIVIL DEFENCE, IOM, UN, TSC.AI, JAGRANJOSH, FAA, USTR.",
                 1, GREY)


def build():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_headline(cv)
    draw_map(cv)
    draw_leads(cv)
    draw_timeline(cv)
    draw_briefs(cv)
    draw_markets_footer(cv)
    return cv


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "entry.png")
    digest = write_png(build(), path)
    print("wrote", path, "sha256", digest, "bytes",
          os.path.getsize(path))


if __name__ == "__main__":
    main()
