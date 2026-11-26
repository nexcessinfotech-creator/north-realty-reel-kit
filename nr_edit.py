#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
North Realty Edit Kit  -  nr_edit.py  v7  "NEXT LEVEL"  (kinetic hook, transitions, impact, kinetic captions,
cinematic look, whole-room B-roll, popping bubble, pace)
Turns any raw clip from Umesh Patel (North Realty NT) into a finished 1080x1920 Instagram reel.
No questions asked: it measures the clip, decides the style, edits, checks itself and renders.

v7 "NEXT LEVEL" - everything from v6, plus (each can be switched off):
  1 KINETIC HOOK  (0-1.5 s): starts 115 % zoomed, eases to 100 % in 10 frames with zoom motion blur (frame 0 stays
    clean = cover, no flash); hook words pop in one by one (60->105->100 %, slight blur, 3 frames apart), still
    behind his head. A clean cover image (<name>_cover.jpg, full title) is written too.   --no-kinetic-hook
  2 TRANSITIONS on about every 2nd-3rd cut and on every B-roll in/out: zoom-blur (6 f), whip-pan with horizontal
    motion blur (6 f), light-leak sweep (8 f); never two of the same in a row; each with a whoosh. --no-transitions
  3 IMPACT on the big word and the key line: camera shake (max 6 px, decays over 8 frames) + soft low hit.
                                                                                                    --no-impact
  4 KINETIC CAPTIONS: every word pops in (90->108->100 %); the active word is Orange at 108 %. --no-kinetic-captions
  5 CINEMATIC LOOK: S-curve, warm skin, cooler shadows, highlight roll-off, 1.5 % fine grain, 15 % vignette;
    B-roll colour-matched to the talking shots before the grade.                               --no-cinematic
  6 WHOLE-ROOM B-ROLL: a 16:9 shot is never cut to a tight 9:16 middle - wide rooms PAN across the full width over
    the shot (direction = camera motion), details slowly zoom in. Every shot is scored (sharpness, exposure / blown
    windows, clean composition) and the best per label is used. Labels: laundry is not bathroom; a shed is
    "garage/shed", not gym. Offline super-resolution if a model is on disk, else lanczos + halo-free sharpen.
                                                                                                --no-whole-room
  7 BUBBLE bottom-left, >= 60 px above the captions, visible soft shadow, pops in 0->110->100 % over 8 frames.
                                                                                                --no-bubble-pop
  8 PACE: something changes every 1.5-2.5 s (cut, transition, visual, B-roll, punch) - never added during the
    call-to-action line or the end card.                                                            --no-pace

v6: --footage tour.mp4 --shots shots.json = a SHOT LIBRARY of the real property (scene-detected shots, each labelled
    by a person: drone, front, street, living, kitchen, dining, bedroom, bathroom, laundry, pool, outdoor, garage,
    gym, hallway; shots with burned-in text / a logo are marked "use": false). When he SAYS a room ("kitchen",
    "pool", "yard" -> outdoor ...) that shot fills the 9:16 frame (centred crop, slow push-in, light sharpen);
    "home / house / property" -> drone or front, "presenting / well-presented" -> best-looking living or kitchen,
    "buyers / inspection" -> front. Never a shot of a different room, never AI or stock footage.
    Umesh stays on screen as a round cut-out BUBBLE (segmentation, white 6 px ring, soft shadow, 32 % of the width)
    bottom-left above the captions; captions keep running. Each B-roll 1.5-3 s, at most one every 3 s, never in the
    hook, the key line, the call to action or the end card. An icon that would meet a B-roll moves to the next time
    the same idea is said, or is dropped. A WALKTHROUGH clip keeps the v5 behaviour (footage ignored).
    python nr_edit.py --detect-shots shots.json --footage tour.mp4  -> draft shot list (+ contact sheet) to label
    python nr_edit.py --shot-sheet sheet.jpg --shots shots.json       -> contact sheet of the labelled library
    Everything else exactly as v5.
v5: label comes in WITH the icon and is fully readable <= 0.2 s after the word (draw-on 8 frames, all strokes
    at once, solid fills); single-word labels Orange; the reframing at the end of the hook eases over 9 frames
    (the visual glides with him); arrow keeps its shape in its loop. Everything else as v4.
v4: every spoken visual STARTS on its word (+-0.2 s; holds shortened to >= 1.2 s or cross-faded, never delayed);
    no icon + big word for the same idea; the hook title is fully visible from frame 0 (cover); visuals fit the
    real space beside / above his head (>= 45 % width, no moving him down, no blurred band); labels bigger
    (cap height >= 45 % of the icon); big words get a Navy outline; complete end card held >= 2 s.
v3: spoken visuals are HERO graphics (icon 300-360 px, label 80-90 px, 55-75 % of the width) with draw-on +
    pop IN, icon-specific hold loops, 90 %-fade OUT, whoosh + pop; one for every matched concept (>= 1.8 s apart);
    the hook title sits higher so (almost) every letter stays readable. Everything else as v2.
v2 adds (each can be switched off):
  big pop-in captions (Montserrat Black)           --no-big-captions
  hook title BEHIND Umesh's head (segmentation)    --no-text-behind
  background pop (blur + darken behind Umesh)      --no-bg-pop
  1-2 big keyword words with zoom-punch            --no-big-words
  push-in inside every shot + zoom-punches         --no-motion
  self-made whoosh / pop sound effects             --no-sfx
  spoken visuals: 53 code-drawn HERO icons         --no-visuals
  real property photos when he names the room      --photos photos.json
  animated end card                                --no-end-anim
  orange progress bar                              --no-progress
fixes: drops false starts / repeated takes / an unfinished last sentence; renders a 30 s clip in a few minutes.

usage:
    python nr_edit.py raw.mp4                 -> raw_NR_edit_v7.mp4 next to the input  (--name NAME to rename)
    python nr_edit.py raw.mp4 --footage tour.mp4 --shots shots.json   -> with B-roll of the real home
    python nr_edit.py raw.mp4 --out DIR       -> output folder
    python nr_edit.py raw.mp4 --checks        -> also writes 6 check frames + a contact sheet
    python nr_edit.py --icon-sheet icons.png  -> draws every icon of the library with its name
    options: --whisper small.en  --type TALKING_HEAD|SELFIE|WALKTHROUGH|MIXED  --keep-work
    photos.json: [{"file": "kitchen.jpg", "label": "kitchen"}, ...]   (labels: bedroom, bathroom, kitchen,
                 living, garden, pool, garage, front, ...; a photo is shown only when he says that word)

needs: ffmpeg + ffprobe, Python 3.10+, numpy, opencv-python, pillow, fonttools, faster-whisper
       (faster-whisper needs PyAV: pip install "av>=11,<16"), mediapipe (selfie segmentation; model file
       models/selfie_segmenter.tflite from the claude-video-effects folder - runs offline)
"""
import argparse, difflib, glob, json, math, os, re, shutil, subprocess, sys, time, urllib.request, wave
from fractions import Fraction

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

VERSION = 'v7'

# ------------------------------------------------------------------ brand + rules
W, H = 1080, 1920
ORANGE, NAVY, BLUE = (0xF3, 0x98, 0x40), (0x25, 0x40, 0x53), (0x1B, 0x7A, 0xAA)
WARM, WHITE, BLACK = (0xF0, 0xE8, 0xE0), (255, 255, 255), (0, 0, 0)
NAME, PHONE, BRAND, TAGLINE = "Umesh Patel", "0404 748 528", "north realty", "Where every journey finds home."

PAD, MIN_PAUSE, AFADE = 0.08, 0.25, 0.010          # pause cutting
CAP_X0, CAP_X1 = 0.06 * W, 0.82 * W                 # caption safe x range (IG buttons on the right)
CAP_CX = (CAP_X0 + CAP_X1) / 2
CAP_MAXW = min(0.80 * W, CAP_X1 - CAP_X0)
CAP_MIN_Y, CAP_MAX_Y = 0.58 * H, 0.75 * H           # caption top >= 58%, bottom <= 75%
TOP_SAFE = 200                                      # only the progress bar may live above this line
TOPMIN = 236                                        # top of hook / visuals (shadows stay below 200 px)
TOP0, TOP1 = TOPMIN, 0.19 * H                       # fallback hook box band
HOOK_T0, HOOK_T1 = 0.0, 3.0                         # hook on frame 0 = Instagram cover
HOOK_EASE = 9                                       # frames: reframing glide when the hook ends
DRAW_F, LABEL_F = 8, 5                              # icon draw-on frames, label fully in after LABEL_F frames
END_DUR, END_FADE = 2.9, 0.3                        # animation 0.8 s + complete card 2.1 s
MAX_SHIFT = 0.30 * H                                # max headroom shift for top elements (hero visuals)
HEAD_GAP = 30                                       # visuals keep this many px above the top of the head
LEVELS = {  # wide, tight, first 1.5s, key line
    'TALKING_HEAD': dict(WIDE=1.00, TIGHT=1.12, FIRST=1.18, KEY=1.28),
    'MIXED':        dict(WIDE=1.00, TIGHT=1.12, FIRST=1.18, KEY=1.28),
    'SELFIE':       dict(WIDE=1.00, TIGHT=1.06, FIRST=1.08, KEY=1.12),
    'WALKTHROUGH':  dict(WIDE=1.00, TIGHT=1.00, FIRST=1.00, KEY=1.00),
}
CAP_EM_V1, CAP_EM = 72, 94          # caption font size (px em): v1 ~72 (cap height ~50), v2 +30% (cap height ~66)
HB_MIN, HB_MAX = 118, 160           # text-behind-head em range
BIG_MIN, BIG_MAX = 150, 220         # big keyword em range
PUSH, PUNCH = 0.04, 0.08            # push-in inside every shot, zoom-punch on key words / visuals
SFX_UNDER = 18.0                    # dB under the voice
# v7 NEXT LEVEL
KH_F, KH_ZOOM, KH_STEP, KH_WORD_F = 10, 0.15, 3, 5   # kinetic hook: 115->100 % in 10 f; words 3 f apart, 5 f pop
TR_FRAMES = {'zoom': 6, 'whip': 6, 'leak': 8}        # transition lengths (frames)
TR_ORDER = ['whip', 'zoom', 'leak']
SHAKE_PX, SHAKE_F = 6.0, 8                           # impact camera shake
GRAIN = 0.015                                        # 1.5 % fine film grain
KC_GAP = 0.10                                        # kinetic captions: extra word gap (em) for the 108 % word
PACE_MAX = 2.5                                       # something changes at least every 2.5 s
BUB_GAP_CAP, BUB_POP_F = 60, 8                       # bubble >= 60 px above captions, pop 0->110->100 % in 8 f

BRAND_PROMPT = "Umesh Patel from North Realty NT, Darwin and Palmerston real estate."
SUBURBS = ['Darwin', 'Palmerston', 'Zuccoli', 'Fannie Bay', 'Woodroffe', 'Rosebery', 'Bakewell', 'Muirhead',
           'Nightcliff', 'Rapid Creek', 'Parap', 'Stuart Park', 'Larrakeyah', 'Casuarina', 'Leanyer', 'Karama',
           'Malak', 'Marrara', 'Coconut Grove', 'Millner', 'Jingili', 'Wanguri', 'Wagaman', 'Wulagi', 'Anula',
           'Nakara', 'Brinkin', 'Alawa', 'Moil', 'Tiwi', 'Lyons', 'Durack', 'Moulden', 'Bellamack', 'Farrar',
           'Mitchell', 'Johnston', 'Gunn', 'Driver', 'Gray', 'Yarrawonga', 'Berrimah', 'Howard Springs',
           'Humpty Doo', 'Coolalinga', 'Virginia', 'Bees Creek', 'Girraween', 'Holtze', 'Lee Point', 'Cullen Bay',
           'Bayview', 'Woolner', 'Ludmilla', 'The Narrows', 'Winnellie', 'Pinelands', 'Knuckey Lagoon',
           'Northcrest', 'Berry Springs', 'Noonamah', 'Batchelor', 'Litchfield', 'Larrimah', 'The Gardens']
COMMON_SUBURB_WORDS = {'driver', 'gray', 'gunn', 'mitchell', 'johnston', 'virginia', 'lyons', 'moil', 'the gardens',
                       'the narrows'}
UMESH = {'umesh', 'umash', 'umesch', 'oomesh', 'umeesh', 'ummesh', 'umish', 'yumesh', 'youmesh', 'umes', 'umeshh'}
JARGON = [  # (phrase, pill label) - label is a category, never a fact
    ('stamp duty', 'BUYING COST'), ('lenders mortgage insurance', 'LOAN COST'), ('lmi', 'LOAN COST'),
    ('settlement', 'FINAL STEP'), ('appraisal', 'PRICE CHECK'), ('auction', 'SALE METHOD'),
    ('offers over', 'PRICE GUIDE'), ('deposit', 'DEPOSIT'), ('first home buyers', 'FIRST HOME'),
    ('first home buyer', 'FIRST HOME'), ('pre-approval', 'FINANCE'), ('preapproval', 'FINANCE'),
    ('interest rates', 'RATE'), ('interest rate', 'RATE'), ('rental yield', 'INVESTORS'), ('equity', 'FINANCE'),
    ('capital growth', 'GROWTH'), ('valuation', 'BANK VALUE'), ('conveyancer', 'LEGAL'), ('cooling off', 'CONTRACT'),
    ('body corporate', 'UNITS'), ('strata', 'UNITS'), ('open home', 'VIEWING'), ('just sold', 'SOLD'),
    ('sold', 'SOLD'), ('just listed', 'LISTED'), ('under contract', 'UNDER CONTRACT'), ('price guide', 'PRICE GUIDE'),
    ('expressions of interest', 'SALE METHOD'), ('dry season', 'TIMING'), ('wet season', 'TIMING'),
    ('well-presented', 'SELLER TIP'), ('well presented', 'SELLER TIP'), ('presentation', 'SELLER TIP'),
    ('styling', 'SELLER TIP'), ('offers', 'BUYERS'), ('mortgage', 'FINANCE')]
NUMW = dict(zero=0, one=1, two=2, three=3, four=4, five=5, six=6, seven=7, eight=8, nine=9, ten=10, eleven=11,
            twelve=12, thirteen=13, fourteen=14, fifteen=15, sixteen=16, seventeen=17, eighteen=18, nineteen=19,
            twenty=20, thirty=30, forty=40, fifty=50, sixty=60, seventy=70, eighty=80, ninety=90)
SCALEW = {'hundred': 100, 'thousand': 1000, 'k': 1000, 'grand': 1000, 'million': 10 ** 6, 'mil': 10 ** 6}
UNITS = {'bedroom', 'bedrooms', 'bed', 'beds', 'bathroom', 'bathrooms', 'bath', 'baths', 'car', 'cars', 'year',
         'years', 'week', 'weeks', 'day', 'days', 'month', 'months', 'sqm', 'square', 'metres', 'meters', 'acres',
         'acre', 'homes', 'houses', 'properties', 'offers', 'buyers', 'minutes', 'hectares', 'percent'}
CTA_RE = re.compile(r"\b(call|ring|dm|message|contact|reach out|book|get in touch|follow|click|link|text me|"
                    r"let me know|comment|free appraisal|appraisal)\b", re.I)
FILLERS = {'so', 'hi', 'hey', 'hello', 'guys', 'everyone', 'okay', 'ok', 'well', 'um', 'uh', 'alright', 'right',
           'yeah', 'and', 'now', 'look'}
STOPS = {'the', 'a', 'an', 'to', 'of', 'and', 'or', 'for', 'at', 'in', 'on', 'with', 'is', 'are', 'you', 'your',
         'this', 'that', 'be', 'it', 'by', 'from', 'my', 'our', 'should', 'these', 'those'}
LEAD_INS = ['are you thinking of', 'are you thinking about', 'thinking of', 'thinking about', 'are you', 'do you want to',
            'do you', 'did you know', 'want to', 'i want to talk about', 'today', 'so', 'hey guys', 'hi guys']
DANGLING = {'and', 'but', 'or', 'so', 'because', 'the', 'a', 'an', 'to', 'of', 'with', 'if', 'that', 'which', 'for',
            'your', 'my', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'then', 'like', 'um', 'uh', 'as', 'when'}
REPEAT_OK = {'very', 'really', 'no', 'so', 'bye', 'yeah', 'yes', 'go', 'big', 'ha'}
BIG_TERMS = {'offers': 2, 'offer': 2, 'sold': 1, 'buyers': 3, 'profit': 2, 'record': 2, 'demand': 2, 'free': 2,
             'growth': 2, 'premium': 3, 'value': 3, 'price': 3, 'now': 5, 'first': 5}


def log(*a):
    print(*a, flush=True)


def run(cmd, cwd=None):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd)
    if r.returncode:
        raise RuntimeError("command failed: %s\n%s" % (' '.join(map(str, cmd[:8])), r.stderr[-3000:]))
    return r.stdout, r.stderr


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def rect_hit(a, b, margin=0):
    """a,b = (x0,y0,x1,y1); True if they overlap (with margin around b)."""
    return not (a[2] <= b[0] - margin or a[0] >= b[2] + margin or a[3] <= b[1] - margin or a[1] >= b[3] + margin)


def ease_out(u):
    u = clamp(u, 0.0, 1.0)
    return 1 - (1 - u) ** 3


def ease_io(u):
    u = clamp(u, 0.0, 1.0)
    return u * u * (3 - 2 * u)


# ------------------------------------------------------------------ fonts
FONT_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf"


def _fetch(url, dest):
    data = None
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'nr-edit'}), timeout=30).read()
    except Exception:
        try:
            data = subprocess.run(['curl', '-sSLf', '--max-time', '60', url], stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, check=True).stdout
        except Exception:
            data = None
    if not data or data[:4] not in (b'\x00\x01\x00\x00', b'true', b'OTTO') or len(data) < 50000:
        return False
    with open(dest, 'wb') as f:
        f.write(data)
    return True


def setup_fonts(cache):
    os.makedirs(cache, exist_ok=True)
    meta_p = os.path.join(cache, 'fonts.json')
    if os.path.exists(meta_p):
        meta = json.load(open(meta_p))
        if all(os.path.exists(meta.get(k, '')) for k in ('xb', 'blk')):
            return meta
    var = os.path.join(cache, 'Montserrat[wght].ttf')
    src, source = None, ''
    if os.path.exists(var) or _fetch(FONT_URL, var):
        src, source = var, 'Montserrat ExtraBold/Black (downloaded from github.com/google/fonts)'
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        cands = (glob.glob('/usr/share/fonts/**/Montserrat*.ttf', recursive=True) +
                 glob.glob(os.path.expanduser('~/Library/Fonts/Montserrat*.ttf')) +
                 glob.glob('/Library/Fonts/Montserrat*.ttf') + glob.glob('C:/Windows/Fonts/Montserrat*.ttf') +
                 [os.path.join(d, 'fonts', 'Montserrat.ttf') for d in
                  (here, os.path.join(here, 'claude-video-effects'), os.path.expanduser('~/claude-video-effects'),
                   '/home/claude/claude-video-effects')])
        cands = [c for c in cands if os.path.exists(c) and 'Italic' not in c]
        cands.sort(key=lambda c: (0 if 'wght' in c or c.endswith('Montserrat.ttf') else 1))
        if cands:
            src, source = cands[0], 'Montserrat (GitHub blocked; local copy %s)' % cands[0]
        else:
            for c in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/Library/Fonts/Arial Bold.ttf',
                      'C:/Windows/Fonts/arialbd.ttf'):
                if os.path.exists(c):
                    src, source = c, 'FALLBACK %s - Montserrat could not be downloaded or found' % os.path.basename(c)
                    break
    if not src:
        raise SystemExit('No usable bold font found.')
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    meta = {'source': source}
    for key, wght, fam in (('xb', 800, 'NR Montserrat ExtraBold'), ('blk', 900, 'NR Montserrat Black')):
        f = TTFont(src)
        if 'fvar' in f:
            loc = {a.axisTag: (clamp(wght, a.minValue, a.maxValue) if a.axisTag == 'wght' else a.defaultValue)
                   for a in f['fvar'].axes}
            f = instancer.instantiateVariableFont(f, loc)
        nm = f['name']
        nm.removeNames(platformID=1)
        for nid in (16, 17, 21, 22, 25):
            nm.removeNames(nameID=nid)
        for nid, val in ((1, fam), (2, 'Regular'), (3, fam + ';nr'), (4, fam), (6, fam.replace(' ', '-'))):
            nm.setName(val, nid, 3, 1, 0x409)
        if 'OS/2' in f:
            f['OS/2'].usWeightClass = 400
            f['OS/2'].fsSelection = (f['OS/2'].fsSelection & ~0b100001) | 0b1000000
        f['head'].macStyle = 0
        out = os.path.join(cache, fam.replace(' ', '') + '.ttf')
        f.save(out)
        meta[key], meta[key + '_fam'] = out, fam
    json.dump(meta, open(meta_p, 'w'))
    return meta


_FCACHE = {}
FONTS = {}


def font(key, em):
    k = (key, int(round(em)))
    if k not in _FCACHE:
        _FCACHE[k] = ImageFont.truetype(FONTS[key], k[1])
    return _FCACHE[k]


def tw(key, text, em):
    return font(key, em).getlength(text)


def cap_h(key, em):
    return -font(key, em).getbbox('H', anchor='ls')[1]


# ------------------------------------------------------------------ sprites (premultiplied BGRA float32)
def pil_to_pm(img):
    a = np.asarray(img.convert('RGBA'), np.float32) / 255.0
    pm = np.empty_like(a)
    pm[..., 0] = a[..., 2] * a[..., 3] * 255
    pm[..., 1] = a[..., 1] * a[..., 3] * 255
    pm[..., 2] = a[..., 0] * a[..., 3] * 255
    pm[..., 3] = a[..., 3]
    return pm


class Blitter:
    def __init__(self):
        self.min_y = 1e9          # topmost overlay pixel (progress bar excluded)
        self.top_hits = []

    def blit(self, frame, spr, x, y, mul=1.0, tag=''):
        if spr is None or mul <= 0.004:
            return None
        h, w = spr.shape[:2]
        x, y = int(round(x)), int(round(y))
        x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return None
        s = spr[y0 - y:y1 - y, x0 - x:x1 - x]
        a = s[..., 3:4] * mul
        if tag != 'progress':
            rows = np.where(a[..., 0].max(1) > 0.02)[0]
            if len(rows):
                top = y0 + rows[0]
                if top < self.min_y:
                    self.min_y = top
                if top < TOP_SAFE:
                    self.top_hits.append((tag, int(top)))
        reg = frame[y0:y1, x0:x1].astype(np.float32)
        frame[y0:y1, x0:x1] = np.clip(s[..., :3] * mul + reg * (1 - a), 0, 255).astype(np.uint8)
        return (x0, y0, x1, y1)

    def blit_scaled(self, frame, spr, cx, cy, s, mul=1.0, tag=''):
        """spr scaled by s, its centre placed at (cx, cy)."""
        if spr is None:
            return None
        if abs(s - 1) > 1e-3:
            h, w = spr.shape[:2]
            nw, nh = max(1, int(round(w * s))), max(1, int(round(h * s)))
            spr = cv2.resize(spr, (nw, nh), interpolation=cv2.INTER_LINEAR if s > 1 else cv2.INTER_AREA)
        h, w = spr.shape[:2]
        return self.blit(frame, spr, cx - w / 2.0, cy - h / 2.0, mul, tag)


def text_sprite(runs, key, em, shadow=(0, 5, 9, 0.6, BLACK), pad=None, box=None, stroke=None):
    """runs = [(text, rgb), ...] on one line. Returns (pm sprite, info) where info has cap-box offsets.
    box = (rgb, alpha, padx, pady, radius) draws a rounded box behind the text."""
    f = font(key, em)
    full = ''.join(t for t, _ in runs)
    width = f.getlength(full)
    ch = cap_h(key, em)
    desc = 0.24 * em
    pad = pad if pad is not None else int(em * 0.35 + (shadow[2] * 2 if shadow else 0))
    bx = (box[2], box[3]) if box else (0, 0)
    Wd, Hd = int(width + 2 * pad + 2 * bx[0]) + 2, int(ch + desc + 2 * pad + 2 * bx[1]) + 2
    img = Image.new('RGBA', (Wd, Hd), (0, 0, 0, 0))
    ox, oy = pad + bx[0], pad + bx[1]
    if box:
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([pad, pad + 0.0, pad + width + 2 * bx[0], pad + ch + 2 * bx[1] + 0.10 * em],
                            box[4], fill=tuple(box[0]) + (int(255 * box[1]),))
    txt = Image.new('L', (Wd, Hd), 0)
    col = Image.new('RGBA', (Wd, Hd), (0, 0, 0, 0))
    dt, dc = ImageDraw.Draw(txt), ImageDraw.Draw(col)
    x = ox
    for t, rgb in runs:
        if stroke:
            dc.text((x, oy + ch), t, font=f, fill=tuple(rgb) + (255,), anchor='ls', stroke_width=stroke[0],
                    stroke_fill=tuple(stroke[1]) + (255,))
            dt.text((x, oy + ch), t, font=f, fill=255, anchor='ls', stroke_width=stroke[0])
        else:
            dc.text((x, oy + ch), t, font=f, fill=tuple(rgb) + (255,), anchor='ls')
            dt.text((x, oy + ch), t, font=f, fill=255, anchor='ls')
        x += f.getlength(t)
    if shadow:
        dx, dy, blur, op, scol = shadow
        sh = txt.filter(ImageFilter.GaussianBlur(blur)) if blur else txt
        sh = sh.point(lambda v: int(v * op))
        sl = Image.new('RGBA', (Wd, Hd), tuple(scol) + (0,))
        sl.putalpha(Image.new('L', (Wd, Hd), 0))
        tmp = Image.new('RGBA', (Wd, Hd), tuple(scol) + (255,))
        shifted = Image.new('L', (Wd, Hd), 0)
        shifted.paste(sh, (dx, dy))
        tmp.putalpha(shifted)
        img = Image.alpha_composite(img, tmp)
    img = Image.alpha_composite(img, col)
    letters, acc = [], 0.0
    for i, chh in enumerate(full):
        nxt = f.getlength(full[:i + 1])
        if not chh.isspace():
            letters.append((ox + acc, ox + nxt))
        acc = nxt
    info = dict(w=Wd, h=Hd, cap_x0=ox, cap_y0=oy, text_w=width, cap_h=ch, em=em,
                mask=np.asarray(txt, np.float32) / 255.0, letters=letters)
    return pil_to_pm(img), info


# ------------------------------------------------------------------ icon library (drawn in code, 100x100 grid)
def _arc(cx, cy, r, a0, a1, n=None):
    n = n or max(6, int(abs(a1 - a0) / 7.5))
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


def _rr(x0, y0, x1, y1, r):
    pts = []
    pts += _arc(x1 - r, y0 + r, r, -90, 0, 6)
    pts += _arc(x1 - r, y1 - r, r, 0, 90, 6)
    pts += _arc(x0 + r, y1 - r, r, 90, 180, 6)
    pts += _arc(x0 + r, y0 + r, r, 180, 270, 6)
    return pts + [pts[0]]


def _wave(x0, x1, y, amp=4.0, per=20.0):
    n = int((x1 - x0) / 2)
    return [(x0 + (x1 - x0) * k / n, y + amp * math.sin(2 * math.pi * ((x1 - x0) * k / n) / per)) for k in range(n + 1)]


def _star(cx, cy, r1, r2, n=5, rot=-90):
    pts = []
    for k in range(2 * n):
        r = r1 if k % 2 == 0 else r2
        a = math.radians(rot + 180.0 * k / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def _circ(cx, cy, r):
    return _arc(cx, cy, r, -90, 270, 40)


def S(c, pts, closed=False):
    pts = list(pts)
    if closed:
        pts = pts + [pts[0]]
    return ('S', c, pts)


def F(c, pts):
    return ('F', c, list(pts))


def FC(c, cx, cy, r):
    return ('F', c, _circ(cx, cy, r))


def FR(c, x0, y0, x1, y1, r):
    return ('F', c, _rr(x0, y0, x1, y1, r))


def T(c, x, y, txt, size):
    return ('T', c, (x, y, txt, size))


def _house(x0=14, x1=86, roof=14, eave=46, base=86, door=True, c='N'):
    cx = (x0 + x1) / 2
    out = [S(c, [(x0 - 6, eave + 4), (cx, roof), (x1 + 6, eave + 4)]),
           S(c, [(x0 + 6, eave - 4), (x0 + 6, base), (x1 - 6, base), (x1 - 6, eave - 4)])]
    if door:
        out.append(S('O', [(cx - 9, base), (cx - 9, base - 24), (cx + 9, base - 24), (cx + 9, base)]))
    return out


def _cloud():
    pts = _arc(30, 52, 12, 90, 270) + _arc(52, 40, 18, 200, 340) + _arc(72, 52, 12, 270, 450)
    return pts + [pts[0]]


ICONS = {
    'bed': [FR('O', 20, 36, 40, 47, 4), S('N', [(12, 28), (12, 82)]), S('N', _rr(12, 47, 88, 66, 5)),
            S('N', [(88, 66), (88, 82)]), S('N', [(12, 74), (88, 74)])],
    'bath': [S('N', [(8, 50), (92, 50)]), S('N', [(13, 50), (15, 64), (24, 74), (76, 74), (85, 64), (87, 50)]),
             S('N', [(26, 74), (22, 86)]), S('N', [(74, 74), (78, 86)]), S('N', [(22, 50), (22, 24), (30, 16), (40, 22)]),
             FC('O', 41, 32, 3.2), FC('O', 47, 40, 3.2), S('O', [(24, 61), (76, 61)])],
    'car': [S('N', [(8, 64), (8, 52), (20, 47), (31, 32), (69, 32), (80, 47), (92, 52), (92, 64), (8, 64)]),
            S('N', [(26, 47), (74, 47)]), S('N', [(50, 33), (50, 47)]), S('N', _circ(28, 68, 9)), S('N', _circ(72, 68, 9)),
            FC('O', 28, 68, 3.5), FC('O', 72, 68, 3.5)],
    'garage': [S('N', [(6, 42), (50, 14), (94, 42)]), S('N', [(16, 36), (16, 88)]), S('N', [(84, 36), (84, 88)]),
               S('N', [(28, 88), (28, 52), (72, 52), (72, 88)]), S('O', [(28, 64), (72, 64)]), S('O', [(28, 76), (72, 76)])],
    'pool': [S('N', [(32, 62), (32, 22)] + _arc(40, 22, 8, 180, 300)), S('N', [(56, 62), (56, 22)] + _arc(64, 22, 8, 180, 300)),
             S('N', [(32, 34), (56, 34)]), S('N', [(32, 48), (56, 48)]), S('O', _wave(10, 90, 72)), S('O', _wave(10, 90, 86))],
    'garden': [F('O', _circ(50, 38, 25)), S('N', _circ(50, 38, 25)), S('N', [(50, 90), (50, 56)]),
               S('N', [(50, 72), (62, 62)]), S('N', [(50, 66), (40, 58)]), S('N', [(26, 90), (74, 90)])],
    'kitchen': [S('N', _rr(20, 46, 80, 84, 7)), S('N', [(12, 46), (88, 46)]), S('N', [(42, 38), (58, 38)]),
                S('N', [(20, 58), (10, 58)]), S('N', [(80, 58), (90, 58)]),
                S('O', [(36, 30), (40, 24), (36, 18), (40, 12)]), S('O', [(52, 30), (56, 24), (52, 18), (56, 12)]),
                S('O', [(68, 30), (72, 24), (68, 18), (72, 12)])],
    'sofa': [S('N', _rr(20, 28, 80, 56, 8)), S('N', _rr(6, 46, 22, 76, 6)), S('N', _rr(78, 46, 94, 76, 6)),
             S('N', [(22, 58), (78, 58)]), S('N', [(14, 76), (14, 86)]), S('N', [(86, 76), (86, 86)]),
             FR('O', 26, 34, 48, 52, 5)],
    'school': [S('N', [(12, 44), (50, 22), (88, 44)]), S('N', [(20, 40), (20, 88), (80, 88), (80, 40)]),
               S('N', [(50, 22), (50, 6)]), F('O', [(50, 6), (66, 10), (50, 15)]), S('O', [(42, 88), (42, 66), (58, 66), (58, 88)]),
               S('N', _circ(50, 46, 6))],
    'beach': [F('O', _arc(50, 50, 18, 180, 360) + [(32, 50)]), S('O', _arc(50, 50, 18, 180, 360)),
              S('N', [(10, 50), (90, 50)]), S('N', _wave(10, 90, 64, 3, 26)), S('N', _wave(18, 82, 78, 3, 26))],
    'shops': [S('N', _rr(16, 34, 84, 90, 7)), S('N', [(36, 46), (36, 30)] + _arc(50, 30, 14, 180, 360) + [(64, 46)]),
              FC('O', 36, 48, 4), FC('O', 64, 48, 4), S('O', [(30, 70), (70, 70)])],
    'park': [S('N', [(16, 38), (84, 38)]), S('N', [(16, 50), (84, 50)]), S('N', [(10, 62), (90, 62)]),
             S('N', [(24, 38), (24, 82)]), S('N', [(76, 38), (76, 82)]), F('O', _circ(84, 18, 9)), S('N', _circ(84, 18, 9))],
    'sun': [F('O', _circ(50, 50, 17)), S('O', _circ(50, 50, 17))] +
           [S('N', [(50 + 26 * math.cos(math.radians(a)), 50 + 26 * math.sin(math.radians(a))),
                    (50 + 38 * math.cos(math.radians(a)), 50 + 38 * math.sin(math.radians(a)))]) for a in range(0, 360, 45)],
    'rain': [S('N', _cloud()), S('O', [(34, 72), (30, 82)]), S('O', [(52, 72), (48, 82)]), S('O', [(70, 72), (66, 82)])],
    'solar': [F('O', [(18, 28), (82, 28), (90, 64), (10, 64)]), S('N', [(18, 28), (82, 28), (90, 64), (10, 64)], True),
              S('N', [(50, 28), (50, 64)]), S('N', [(14, 46), (86, 46)]), S('N', [(34, 28), (30, 64)]),
              S('N', [(66, 28), (70, 64)]), S('N', [(50, 64), (50, 84)]), S('N', [(36, 84), (64, 84)])],
    'aircon': ([S('N', [(50 + 38 * math.cos(math.radians(a)), 50 + 38 * math.sin(math.radians(a))),
                        (50 - 38 * math.cos(math.radians(a)), 50 - 38 * math.sin(math.radians(a)))]) for a in (90, 30, 150)] +
               [S('O', [(50 + 26 * math.cos(math.radians(a)) + 9 * math.cos(math.radians(a + 120)),
                         50 + 26 * math.sin(math.radians(a)) + 9 * math.sin(math.radians(a + 120))),
                        (50 + 34 * math.cos(math.radians(a)), 50 + 34 * math.sin(math.radians(a))),
                        (50 + 26 * math.cos(math.radians(a)) + 9 * math.cos(math.radians(a - 120)),
                         50 + 26 * math.sin(math.radians(a)) + 9 * math.sin(math.radians(a - 120)))]) for a in range(30, 390, 60)]),
    'ruler': [S('N', [(12, 62), (62, 12), (88, 38), (38, 88)], True)] +
             [S('O', [(12 + 50 * u, 62 - 50 * u), (12 + 50 * u + (9 if k % 2 else 15) * 0.707,
                                                   62 - 50 * u + (9 if k % 2 else 15) * 0.707)])
              for k, u in enumerate((0.2, 0.35, 0.5, 0.65, 0.8))],
    'pin': [S('N', _arc(50, 40, 24, 150, 390) + [(50, 90)], True), F('O', _circ(50, 40, 9))],
    'dollar': [S('N', _circ(50, 50, 38)), T('O', 50, 52, '$', 58)],
    'coins': [S('N', _rr(20, 64, 72, 80, 8)), S('N', _rr(20, 48, 72, 64, 8)), S('N', _rr(20, 32, 72, 48, 8)),
              F('O', _circ(74, 30, 14)), S('N', _circ(74, 30, 14))],
    'percent': [S('N', _circ(30, 30, 11)), S('N', _circ(70, 70, 11)), S('O', [(78, 16), (22, 84)])],
    'sold': [F('O', [(8, 32), (66, 32), (92, 56), (66, 80), (8, 80)]),
             S('N', [(8, 32), (66, 32), (92, 56), (66, 80), (8, 80)], True), S('N', _circ(78, 56, 4)),
             T('N', 38, 57, 'SOLD', 16)],
    'calendar': [S('N', _rr(12, 22, 88, 88, 7)), S('N', [(12, 40), (88, 40)]), S('N', [(32, 12), (32, 30)]),
                 S('N', [(68, 12), (68, 30)]), FC('O', 30, 56, 4.5), FC('O', 50, 56, 4.5), FC('O', 70, 56, 4.5),
                 FC('O', 30, 72, 4.5), FR('O', 42, 64, 78, 80, 4)],
    'key': [S('N', _circ(28, 50, 17)), F('O', _circ(28, 50, 6)), S('N', [(45, 50), (90, 50)]),
            S('N', [(76, 50), (76, 64)]), S('N', [(88, 50), (88, 62)])],
    'door': [S('N', [(24, 88), (24, 12), (76, 12), (76, 88)]), FC('O', 64, 54, 4.5), S('O', _rr(34, 22, 66, 44, 3)),
             S('N', [(12, 88), (88, 88)])],
    'clipboard': [S('N', _rr(18, 18, 82, 90, 7)), FR('O', 36, 10, 64, 26, 5), S('N', [(32, 44), (68, 44)]),
                  S('N', [(32, 58), (68, 58)]), S('O', [(32, 72), (40, 80), (56, 66)])],
    'handshake': [S('N', _rr(4, 36, 16, 62, 3)), S('O', _rr(84, 36, 96, 62, 3)),
                  S('N', [(16, 42), (34, 40), (50, 32), (68, 42), (60, 48)]),
                  S('O', [(84, 42), (68, 40), (54, 50), (46, 58)]),
                  S('N', [(16, 58), (30, 64), (40, 72), (48, 72)]), S('N', [(36, 58), (46, 68)]),
                  S('N', [(44, 52), (54, 62)]), S('N', [(52, 48), (60, 56)])],
    'people': [S('N', _circ(20, 44, 8.5)), S('N', _arc(20, 82, 15, 180, 360)),
               S('N', _circ(80, 44, 8.5)), S('N', _arc(80, 82, 15, 180, 360)),
               F('O', _circ(50, 32, 11)), S('N', _circ(50, 32, 11)), S('O', _arc(50, 84, 21, 180, 360))],
    'houses': [S('N', [(2, 60), (22, 42), (42, 60)]), S('N', [(8, 56), (8, 88), (36, 88), (36, 56)]),
               S('O', [(44, 48), (70, 18), (96, 48)]), S('N', [(50, 44), (50, 88), (90, 88), (90, 44)]),
               S('O', [(62, 88), (62, 66), (78, 66), (78, 88)])],
    'badge': [F('O', _circ(50, 40, 27)), S('N', _circ(50, 40, 27)),
              S('N', [(36, 63), (28, 92), (40, 86), (46, 94), (50, 68)]),
              S('N', [(64, 63), (72, 92), (60, 86), (54, 94), (50, 68)]), T('N', 50, 42, '1', 36)],
    'house_tag': _house(8, 66, 20, 48, 84, door=False) + [
        F('O', [(54, 56), (78, 56), (92, 70), (78, 84), (54, 84)]),
        S('N', [(54, 56), (78, 56), (92, 70), (78, 84), (54, 84)], True), FC('N', 79, 70, 3.2)],
    'arrow_up': [S('N', [(10, 82), (36, 54), (54, 66), (86, 30)]), S('O', [(64, 28), (88, 28), (88, 52)]),
                 S('N', [(10, 90), (90, 90)])],
    'sparkle_house': _house(10, 74, 24, 54, 88) + [F('O', _star(82, 18, 12, 4, 4)), F('O', _star(92, 42, 6, 2, 4)),
                                                   F('O', _star(14, 20, 6, 2, 4))],
    'house': _house(),
    'clock': [S('N', _circ(50, 50, 38)), S('O', [(50, 50), (50, 26)]), S('O', [(50, 50), (68, 60)]), FC('N', 50, 50, 4.5)],
    'chart': [S('N', [(8, 88), (92, 88)]), S('N', _rr(16, 58, 32, 88, 3)), S('N', _rr(42, 40, 58, 88, 3)),
              FR('O', 68, 20, 84, 88, 3), S('N', _rr(68, 20, 84, 88, 3))],
    'bank': [S('N', [(10, 36), (50, 12), (90, 36), (10, 36)]), FC('O', 50, 27, 4.5), S('N', [(20, 44), (20, 76)]),
             S('N', [(40, 44), (40, 76)]), S('N', [(60, 44), (60, 76)]), S('N', [(80, 44), (80, 76)]),
             S('N', [(10, 84), (90, 84)])],
    'document': [S('N', [(22, 10), (60, 10), (80, 30), (80, 90), (22, 90), (22, 10)]), S('N', [(60, 10), (60, 30), (80, 30)]),
                 S('O', [(34, 48), (68, 48)]), S('O', [(34, 62), (68, 62)]), S('O', [(34, 76), (56, 76)])],
    'search': [S('N', _circ(42, 42, 25)), S('O', [(61, 61), (88, 88)]), S('N', _arc(42, 42, 14, 200, 260))],
    'phone': [S('N', _rr(28, 8, 72, 92, 9)), S('N', [(43, 18), (57, 18)]), FC('O', 50, 80, 5)],
    'star': [F('O', _star(50, 52, 40, 17)), S('N', _star(50, 52, 40, 17), True)],
    'heart': [F('O', [(50 + 2.3 * 16 * math.sin(t) ** 3,
                       48 - 2.3 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)))
                      for t in np.linspace(0, 2 * math.pi, 60)]),
              S('N', [(50 + 2.3 * 16 * math.sin(t) ** 3,
                       48 - 2.3 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)))
                      for t in np.linspace(0, 2 * math.pi, 60)])],
    'bulb': [S('N', [(40, 70)] + _arc(50, 38, 24, 155, 385) + [(60, 70)]), S('N', [(40, 70), (60, 70)]),
             S('N', [(42, 80), (58, 80)]), S('N', [(46, 90), (54, 90)]), S('O', [(42, 46), (50, 56), (58, 46)])],
    'check': [S('N', _circ(50, 50, 38)), S('O', [(31, 52), (45, 66), (71, 37)])],
    'camera': [S('N', _rr(10, 30, 90, 82, 8)), S('N', [(32, 30), (39, 18), (61, 18), (68, 30)]),
               S('O', _circ(50, 56, 15)), FC('O', 78, 42, 3.5)],
    'roller': [S('N', _rr(12, 12, 72, 34, 7)), S('N', [(72, 23), (86, 23), (86, 46), (50, 52), (50, 64)]),
               FR('O', 43, 64, 57, 92, 5)],
    'tools': [S('N', _rr(12, 14, 52, 32, 4)), S('N', [(32, 32), (32, 90)]), S('O', [(58, 90), (76, 44)]),
              S('O', _arc(80, 32, 13, 140, 400))],
    'paw': [F('N', [(50 + 20 * math.cos(t), 66 + 15 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 40)]),
            FC('O', 24, 44, 8), FC('O', 40, 28, 8), FC('O', 60, 28, 8), FC('O', 76, 44, 8)],
    'plane': [S('N', [(10, 64), (82, 30), (92, 32), (86, 42), (22, 70), (10, 64)]), S('O', [(48, 47), (36, 24), (46, 22), (62, 40)]),
              S('O', [(54, 58), (64, 80), (72, 78), (68, 52)]), S('N', [(20, 64), (12, 52)])],
    'bus': [S('N', _rr(18, 10, 82, 80, 9)), S('O', _rr(26, 20, 74, 46, 3)), FC('O', 30, 64, 4.5), FC('O', 70, 64, 4.5),
            S('N', [(28, 80), (28, 90)]), S('N', [(72, 80), (72, 90)])],
    'medical': [S('N', _rr(14, 14, 86, 86, 12)), F('O', [(42, 26), (58, 26), (58, 42), (74, 42), (74, 58), (58, 58), (58, 74),
                                                        (42, 74), (42, 58), (26, 58), (26, 42), (42, 42)])],
}
ICONS['badge2'] = ICONS['badge'][:-1] + [T('N', 50, 42, '2', 36)]
ICONS['badge3'] = ICONS['badge'][:-1] + [T('N', 50, 42, '3', 36)]
ICON_NAMES = {'houses': 'two houses / stand out', 'badge': 'badge / tip 1', 'badge2': 'badge / tip 2',
              'badge3': 'badge / tip 3', 'bed': 'bed', 'bath': 'bath', 'car': 'car', 'garage': 'garage', 'pool': 'pool', 'garden': 'garden / tree',
              'kitchen': 'kitchen', 'sofa': 'sofa / living', 'school': 'school', 'beach': 'beach / waves',
              'shops': 'shops / bag', 'park': 'park', 'sun': 'sun (dry season)', 'rain': 'rain (wet season)',
              'solar': 'solar panel', 'aircon': 'air-con', 'ruler': 'ruler / land', 'pin': 'map pin / suburb',
              'dollar': 'dollar / price', 'coins': 'coins / deposit', 'percent': 'percent / rates', 'sold': 'SOLD tag',
              'calendar': 'calendar / days', 'key': 'key / open home', 'door': 'door / inspection',
              'clipboard': 'clipboard / appraisal', 'handshake': 'handshake / settlement', 'people': 'people / buyers',
              'house_tag': 'house + tag / sellers', 'arrow_up': 'arrow up / offers', 'sparkle_house': 'sparkle house',
              'house': 'house / property', 'clock': 'clock / time', 'chart': 'chart / market', 'bank': 'bank / finance',
              'document': 'document / contract', 'search': 'search', 'phone': 'phone / call', 'star': 'star / reviews',
              'heart': 'heart / dream home', 'bulb': 'bulb / tip', 'check': 'check / ready', 'camera': 'camera / photos',
              'roller': 'paint roller / reno', 'tools': 'tools / repairs', 'paw': 'paw / pets', 'plane': 'plane / airport',
              'bus': 'bus / transport', 'medical': 'medical / hospital'}

ICON_SW, ICON_OW = 7.0, 3.4         # stroke weight, white outline (100-unit grid)
_ICACHE = {}


def _plen(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts[:-1], pts[1:]))


def _cut(pts, L):
    out, acc = [pts[0]], 0.0
    for a, b in zip(pts[:-1], pts[1:]):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        if acc + d >= L:
            u = (L - acc) / d if d else 0
            out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
            return out
        out.append(b)
        acc += d
    return out


def render_icon(key, px, prog=1.0, t=None):
    """flat line icon, Orange/Navy, white outline, one stroke weight. prog<1 = stroke draw-on;
    t = seconds into the hold loop (icon-specific animation)."""
    ck = (key, px, round(prog, 3))
    if t is None and ck in _ICACHE:
        return _ICACHE[ck]
    ss = 3 if t is None and px <= 200 else 2
    Sz = px * ss
    k = Sz / 100.0
    col = {'N': NAVY, 'O': ORANGE}
    prims = loop_prims(key, ICONS[key], t)
    strokes = [p for p in prims if p[0] == 'S']
    parts = []                                       # v5: every stroke draws at the same time (no lone pieces)
    for p in strokes:
        if prog >= 1:
            parts.append((p[1], p[2]))
        elif prog > 0:
            parts.append((p[1], _cut(p[2], max(0.5, _plen(p[2]) * (0.3 + 0.7 * prog)))))   # recognisable from frame 1
    fa = 1.0 if prog >= 0.5 else 0.0                 # fills / digits appear solid, never half-transparent
    sw, ow = ICON_SW * k, ICON_OW * k
    base = Image.new('RGBA', (Sz, Sz), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)

    def poly(dd, pts, fill, width):
        pp = [(x * k, y * k) for x, y in pts]
        if len(pp) >= 2:
            dd.line(pp, fill=fill, width=int(round(width)), joint='curve')
        r = width / 2.0
        for x, y in (pp[0], pp[-1]):
            dd.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    # 1 white outline under everything
    for c, pts in parts:
        poly(d, pts, (255, 255, 255, 255), sw + 2 * ow)
    if fa > 0:
        fl = Image.new('RGBA', (Sz, Sz), (0, 0, 0, 0))
        df = ImageDraw.Draw(fl)
        for p in prims:
            if p[0] == 'F':
                pp = [(x * k, y * k) for x, y in p[2]]
                df.line(pp + [pp[0]], fill=(255, 255, 255, 255), width=int(round(2 * ow)), joint='curve')
                df.polygon(pp, fill=col[p[1]] + (255,))
            elif p[0] == 'T':
                x, y, txt, size = p[2]
                fnt = font('blk', size * k)
                df.text((x * k, y * k), txt, font=fnt, fill=col[p[1]] + (255,), anchor='mm',
                        stroke_width=int(round(ow * 0.9)), stroke_fill=(255, 255, 255, 255))
        if fa < 1:
            fl.putalpha(fl.getchannel('A').point(lambda v: int(v * fa)))
        base = Image.alpha_composite(base, fl)
        d = ImageDraw.Draw(base)
    for c, pts in parts:
        poly(d, pts, col[c] + (255,), sw)
    img = base.resize((px, px), Image.LANCZOS)
    if t is None:
        _ICACHE[ck] = img
    return img


def icon_sheet(path):
    keys = list(ICONS)
    cols, cw, chh = 7, 230, 270
    rows = int(math.ceil(len(keys) / float(cols)))
    sheet = Image.new('RGB', (cols * cw + 40, rows * chh + 150), (0xC9, 0xCF, 0xD4))
    d = ImageDraw.Draw(sheet)
    d.text((sheet.width / 2, 62), 'North Realty icon library  -  %d icons (%s)' % (len(keys), VERSION),
           font=font('blk', 40), fill=NAVY, anchor='mm')
    for i, kk in enumerate(keys):
        x, y = 20 + (i % cols) * cw, 120 + (i // cols) * chh
        d.rounded_rectangle([x + 10, y + 6, x + cw - 10, y + chh - 12], 22, fill=(0xB4, 0xBC, 0xC3))
        im = render_icon(kk, 160)
        sheet.paste(im, (int(x + (cw - 160) / 2), y + 22), im)
        d.text((x + cw / 2, y + 214), kk, font=font('blk', 24), fill=NAVY, anchor='mm')
        d.text((x + cw / 2, y + 240), ICON_NAMES.get(kk, ''), font=font('xb', 17), fill=(0x33, 0x44, 0x50), anchor='mm')
    sheet.save(path, quality=92)
    return len(keys)


# keyword map: (phrases, icon, label, priority)  priority 1 = feature, 2 = concept, 3 = generic
VISUAL_MAP = [
    (['other properties', 'other property', 'other homes', 'other houses', 'stand out'], 'houses', 'STAND OUT', 1),
    (['get offers', 'more offers', 'multiple offers', 'offer'], 'arrow_up', 'MORE OFFERS', 1),
    (['buyer'], 'people', 'BUYERS', 1),
    (['first', 'firstly', 'number one', 'tip one'], 'badge', 'TIP 1', 1),
    (['second', 'secondly', 'number two', 'tip two'], 'badge2', 'TIP 2', 1),
    (['third', 'thirdly', 'number three', 'tip three'], 'badge3', 'TIP 3', 1),
    (['first home buyers', 'first home buyer', 'first home'], 'key', 'FIRST HOME', 1),
    (['days on market'], 'calendar', 'DAYS ON MARKET', 1),
    (['open home', 'open homes', 'open house'], 'key', 'OPEN HOME', 1),
    (['dry season'], 'sun', 'DRY SEASON', 1),
    (['wet season', 'build up', 'build-up', 'cyclone', 'rain', 'storm'], 'rain', 'WET SEASON', 1),
    (['air conditioning', 'air conditioned', 'air-con', 'aircon', 'split system', 'ducted'], 'aircon', 'AIR-CON', 1),
    (['solar panels', 'solar'], 'solar', 'SOLAR', 1),
    (['bedroom', 'bed'], 'bed', 'BEDROOM', 1),
    (['bathroom', 'bath', 'ensuite', 'toilet', 'shower'], 'bath', 'BATHROOM', 1),
    (['car space', 'carport', 'car', 'parking'], 'car', 'CAR SPACE', 1),
    (['garage', 'shed', 'workshop'], 'garage', 'GARAGE', 1),
    (['swimming pool', 'pool', 'swimming'], 'pool', 'POOL', 1),
    (['backyard', 'garden', 'yard', 'lawn', 'landscaping', 'tree', 'greenery'], 'garden', 'GARDEN', 1),
    (['kitchen', 'benchtop', 'cooking'], 'kitchen', 'KITCHEN', 1),
    (['living room', 'living area', 'family room', 'living', 'lounge', 'sofa', 'couch'], 'sofa', 'LIVING', 1),
    (['school'], 'school', 'SCHOOLS', 1),
    (['water views', 'waterfront', 'beach', 'ocean', 'marina', 'esplanade', 'sea'], 'beach', 'BEACH', 1),
    (['shopping centre', 'shopping', 'shops', 'mall', 'cafe'], 'shops', 'SHOPS', 1),
    (['playground', 'park', 'reserve'], 'park', 'PARK', 1),
    (['land size', 'square metres', 'square meters', 'sqm', 'acre', 'hectare', 'block', 'land'], 'ruler', 'LAND SIZE', 1),
    (['just sold', 'sold'], 'sold', 'SOLD', 1),
    (['inspection', 'inspect', 'viewing'], 'door', 'INSPECTION', 1),
    (['keys', 'key', 'move in', 'moving in'], 'key', 'KEYS', 2),
    (['appraisal', 'valuation'], 'clipboard', 'APPRAISAL', 1),
    (['settlement', 'settle', 'settled'], 'handshake', 'SETTLEMENT', 1),
    (['deposit', 'savings'], 'coins', 'DEPOSIT', 1),
    (['interest rate', 'rate', 'percent'], 'percent', 'RATES', 1),
    (['price', 'value', 'worth', 'budget', 'asking'], 'dollar', 'PRICE', 2),
    (['mortgage', 'loan', 'finance', 'pre-approval', 'preapproval', 'lender', 'bank', 'borrowing'], 'bank', 'FINANCE', 2),
    (['contract', 'paperwork', 'cooling off'], 'document', 'CONTRACT', 2),
    (['rental yield', 'investment', 'investor', 'market', 'yield'], 'chart', 'MARKET', 2),
    (['well-presented', 'well presented'], 'sparkle_house', 'WELL-PRESENTED', 1),
    (['presenting', 'presentation', 'presented', 'styling', 'staging', 'declutter'], 'sparkle_house', 'WELL-PRESENTED', 1),
    (['families', 'family', 'tenant'], 'people', 'FAMILIES', 2),
    (['seller', 'selling', 'sell', 'listing'], 'house_tag', 'SELLING', 2),
    (['capital growth', 'growth', 'demand', 'increase'], 'arrow_up', 'GROWTH', 2),
    (['review', 'five star', '5 star', 'rating'], 'star', 'REVIEWS', 2),
    (['tip', 'advice', 'hack'], 'bulb', 'TIP', 2),
    (['photo', 'photography', 'picture'], 'camera', 'PHOTOS', 2),
    (['renovation', 'renovated', 'renovate', 'fresh paint', 'paint', 'painting'], 'roller', 'RENOVATION', 2),
    (['repair', 'maintenance', 'handyman'], 'tools', 'REPAIRS', 2),
    (['pet friendly', 'pet', 'dog'], 'paw', 'PET FRIENDLY', 2),
    (['airport', 'flight'], 'plane', 'AIRPORT', 2),
    (['public transport', 'transport', 'bus'], 'bus', 'TRANSPORT', 2),
    (['hospital', 'medical'], 'medical', 'HOSPITAL', 2),
    (['dream home', 'dream', 'love'], 'heart', 'DREAM HOME', 3),
    (['quick', 'quickly', 'fast', 'minutes'], 'clock', 'FAST', 3),
    (['call me', 'give me a call', 'call', 'phone'], 'phone', 'CALL ME', 3),
    (['property', 'house', 'home'], 'house', 'PROPERTY', 3),
]
PHOTO_ICON = {'bedroom': 'bed', 'bed': 'bed', 'master': 'bed', 'bathroom': 'bath', 'ensuite': 'bath', 'bath': 'bath',
              'kitchen': 'kitchen', 'living': 'sofa', 'lounge': 'sofa', 'family': 'sofa', 'garden': 'garden',
              'yard': 'garden', 'backyard': 'garden', 'pool': 'pool', 'garage': 'garage', 'carport': 'car',
              'front': 'house', 'facade': 'house', 'exterior': 'house', 'street': 'house', 'house': 'house',
              'aerial': 'pin', 'view': 'beach', 'beach': 'beach', 'solar': 'solar', 'patio': 'garden',
              'deck': 'garden', 'alfresco': 'garden', 'laundry': 'bath', 'dining': 'kitchen'}


def stem(t):
    t = t.lower().strip("'")
    if len(t) > 4 and t.endswith('ies'):
        return t[:-3] + 'y'
    if len(t) > 3 and t.endswith('s') and not t.endswith('ss'):
        return t[:-1]
    return t


# ------------------------------------------------------------------ media helpers
def probe(path):
    out, _ = run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', path])
    j = json.loads(out)
    v = next((s for s in j['streams'] if s['codec_type'] == 'video'), None)
    a = next((s for s in j['streams'] if s['codec_type'] == 'audio'), None)
    if v is None:
        raise SystemExit('No video stream in %s' % path)
    rot = 0
    for sd in v.get('side_data_list', []) or []:
        if 'rotation' in sd:
            rot = int(round(float(sd['rotation'])))
    if 'rotate' in (v.get('tags') or {}):
        rot = int(v['tags']['rotate'])
    w, h = int(v['width']), int(v['height'])
    sar = v.get('sample_aspect_ratio', '1:1')
    if sar and sar not in ('1:1', '0:1', 'N/A'):
        n, d = map(int, sar.split(':'))
        w = int(round(w * n / d))
    if abs(rot) % 180 == 90:
        w, h = h, w
    fr = v.get('avg_frame_rate', '0/0')
    if fr in ('0/0', '', None):
        fr = v.get('r_frame_rate', '30/1')
    fps = Fraction(fr).limit_denominator(1001)
    if fps <= 5 or fps > 120:
        fps = Fraction(30)
    dur = float(j['format'].get('duration') or v.get('duration') or 0)
    return dict(w=w, h=h, rot=rot, fps=fps, dur=dur, has_audio=a is not None)


class FrameReader:
    def __init__(self, path, size=(W, H)):
        self.n = size[0] * size[1] * 3
        self.shape = (size[1], size[0], 3)
        vf = [] if size == (W, H) else ['-vf', 'scale=%d:%d:flags=area' % size]
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, *vf, '-f', 'rawvideo', '-pix_fmt', 'bgr24',
                                   '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10 ** 8)

    def read(self):
        b = self.p.stdout.read(self.n)
        if len(b) < self.n:
            return None
        return np.frombuffer(b, np.uint8).reshape(self.shape)

    def close(self):
        try:
            self.p.stdout.close()
            self.p.kill()
            self.p.wait()
        except Exception:
            pass


def grab(path, t, size=(W, H)):
    out = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '%.4f' % max(0, t), '-i', path, '-frames:v', '1',
                          '-vf', 'scale=%d:%d' % size, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'],
                         stdout=subprocess.PIPE).stdout
    if len(out) < size[0] * size[1] * 3:
        return None
    return np.frombuffer(out[:size[0] * size[1] * 3], np.uint8).reshape(size[1], size[0], 3)


# ------------------------------------------------------------------ 1. normalise
def normalise(src, info, out):
    w, h, fps = info['w'], info['h'], info['fps']
    ar = w / float(h)
    if abs(ar / (9 / 16.) - 1) < 0.03:
        up = max(W / float(w), H / float(h)) > 1.001
        sharp = ',unsharp=5:5:0.6:5:5:0.0' if up else ''
        fc = ("[0:v]scale=%d:%d:force_original_aspect_ratio=increase:flags=lanczos,crop=%d:%d%s,setsar=1,"
              "fps=%s,format=yuv420p[v]" % (W, H, W, H, sharp, fps))
        mode = 'cover-crop'
    else:
        up = min(W / float(w), H / float(h)) > 1.001
        sharp = ',unsharp=5:5:0.6:5:5:0.0' if up else ''
        fc = ("[0:v]split=2[a][b];[a]scale=%d:%d:force_original_aspect_ratio=increase:flags=bicubic,crop=%d:%d,"
              "gblur=sigma=45,eq=brightness=-0.05:saturation=0.9[bg];[b]scale=%d:%d:force_original_aspect_ratio="
              "decrease:flags=lanczos%s[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=%s,format=yuv420p[v]"
              % (W, H, W, H, W, H, sharp, fps))
        mode = 'blur-fill'
    cmd = ['ffmpeg', '-v', 'error', '-y', '-i', src]
    if info['has_audio']:
        amap = ['-map', '0:a:0']
    else:
        cmd += ['-f', 'lavfi', '-t', '%.3f' % info['dur'], '-i', 'anullsrc=r=48000:cl=stereo']
        amap = ['-map', '1:a:0']
    cmd += ['-filter_complex', fc, '-map', '[v]', *amap, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '12',
            '-c:a', 'pcm_s16le', '-ar', '48000', '-ac', '2', out]
    run(cmd)
    return mode, up


# ------------------------------------------------------------------ 2. transcribe
def transcribe(wav16, model_name):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'av>=11,<16', 'faster-whisper'], check=True)
        from faster_whisper import WhisperModel
    model = None
    for name in (model_name, 'base.en', 'base'):
        try:
            model = WhisperModel(name, device='cpu', compute_type='int8')
            break
        except Exception as e:
            log('  (whisper model %s unavailable: %s)' % (name, str(e)[:80]))
    if model is None:
        raise SystemExit('No whisper model could be loaded.')
    segs, _ = model.transcribe(wav16, language='en', word_timestamps=True, beam_size=5,
                               initial_prompt=BRAND_PROMPT, condition_on_previous_text=False, vad_filter=False)
    words = []
    for s in segs:
        for w in (s.words or []):
            t = w.word.strip()
            if not t:
                continue
            if words and (t.startswith('-') or words[-1]['w'].endswith('-')) and w.start - words[-1]['e'] < 0.3:
                words[-1]['w'] += t
                words[-1]['e'] = max(words[-1]['e'], float(w.end))
                continue
            words.append(dict(w=t, s=float(w.start), e=float(max(w.end, w.start + 0.04))))
    return words


def core(t):
    return re.sub(r"[^\w'%$.-]", '', t).strip('.').lower()


def _repl(orig, new):
    m = re.match(r"^(\W*)(.*?)([^\w%]*)$", orig)
    return m.group(1) + new + m.group(3)


def fix_brand_words(words):
    fixes = []
    singles = {s.lower(): s for s in SUBURBS if ' ' not in s}
    doubles = {s.lower(): s for s in SUBURBS if ' ' in s}
    i = 0
    while i < len(words):
        c = core(words[i]['w'])
        n = core(words[i + 1]['w']) if i + 1 < len(words) else ''
        if c == 'north' and n in ('realty', 'reality', 'realities', 'really', 'realtie', 'royalty', 'realdy', 'rielty'):
            if words[i + 1]['w'].strip('.,!?').lower() != 'realty' or words[i]['w'][0] != 'N':
                fixes.append('%s %s -> North Realty' % (words[i]['w'], words[i + 1]['w']))
            words[i]['w'], words[i + 1]['w'] = _repl(words[i]['w'], 'North'), _repl(words[i + 1]['w'], 'Realty')
            i += 2
            continue
        if c in ('northrealty', 'northreality'):
            words[i]['w'] = _repl(words[i]['w'], 'North Realty')
            fixes.append('-> North Realty')
        elif c in UMESH and words[i]['w'].strip('.,!?') != 'Umesh':
            fixes.append('%s -> Umesh' % words[i]['w'])
            words[i]['w'] = _repl(words[i]['w'], 'Umesh')
        elif c in ('patil', 'pattel', 'pathel', 'pattle') and i and core(words[i - 1]['w']) == 'umesh':
            words[i]['w'] = _repl(words[i]['w'], 'Patel')
            fixes.append('-> Patel')
        elif n:
            pair = c + ' ' + n
            best = max(doubles, key=lambda d: difflib.SequenceMatcher(None, pair, d).ratio())
            if best not in COMMON_SUBURB_WORDS and difflib.SequenceMatcher(None, pair, best).ratio() >= 0.86:
                a, b = doubles[best].split(' ', 1)
                if words[i]['w'].strip('.,') + ' ' + words[i + 1]['w'].strip('.,') != doubles[best]:
                    fixes.append('%s %s -> %s' % (words[i]['w'], words[i + 1]['w'], doubles[best]))
                words[i]['w'], words[i + 1]['w'] = _repl(words[i]['w'], a), _repl(words[i + 1]['w'], b)
                i += 2
                continue
        if c in singles and c not in COMMON_SUBURB_WORDS and words[i]['w'].strip('.,!?') != singles[c]:
            words[i]['w'] = _repl(words[i]['w'], singles[c])
            fixes.append('-> ' + singles[c])
        elif len(c) >= 5 and words[i]['w'][:1].isupper() and c not in singles:
            best = max(singles, key=lambda d: difflib.SequenceMatcher(None, c, d).ratio())
            if (best not in COMMON_SUBURB_WORDS and best[0] == c[0]
                    and difflib.SequenceMatcher(None, c, best).ratio() >= 0.84):
                fixes.append('%s -> %s' % (words[i]['w'], singles[best]))
                words[i]['w'] = _repl(words[i]['w'], singles[best])
        i += 1
    return fixes


def sentences_of(words):
    sents, cur = [], []
    for k, w in enumerate(words):
        cur.append(k)
        end = re.search(r"[.?!]['\"]?$", w['w']) is not None
        gap = words[k + 1]['s'] - w['e'] if k + 1 < len(words) else 0
        if end or (gap > 0.7 and len(cur) >= 4) or len(cur) >= 40:
            sents.append(cur)
            cur = []
    if cur:
        sents.append(cur)
    return sents


def sentence_complete(words, idx):
    if not idx:
        return False
    last = words[idx[-1]]['w']
    return bool(re.search(r"[.?!]['\"]?$", last)) and core(last) not in DANGLING


def clean_takes(words):
    """v2 FIX: mark false starts, repeated takes and an unfinished last sentence as dropped.
    Returns list of (index, reason). Every real word stays."""
    n = len(words)
    keep = [True] * n
    why = {}
    toks = [re.sub(r"[^\w'%$]", '', w['w']).lower() for w in words]
    for k, w in enumerate(words):                                   # cut-off word fragments ("presen-")
        if w['w'].rstrip(',.?!').endswith('-') and len(toks[k]) <= 12:
            keep[k], why[k] = False, 'cut-off word'
    changed = True
    while changed:                                                  # immediate repeats: "you should you should"
        changed = False
        idx = [i for i in range(n) if keep[i]]
        for m in range(6, 0, -1):
            for a in range(len(idx) - 2 * m + 1):
                A = [toks[idx[a + j]] for j in range(m)]
                B = [toks[idx[a + m + j]] for j in range(m)]
                if A == B and all(A) and not (m == 1 and A[0] in REPEAT_OK):
                    gap = words[idx[a + m]]['s'] - words[idx[a + m - 1]]['e']
                    if m == 1 and gap > 0.8:
                        continue
                    for j in range(m):
                        keep[idx[a + j]], why[idx[a + j]] = False, 'repeated take'
                    changed = True
                    break
            if changed:
                break
    kept = [i for i in range(n) if keep[i]]
    sub = [words[i] for i in kept]
    sents = [[kept[j] for j in s] for s in sentences_of(sub)] if sub else []
    for si in range(len(sents) - 1):                                # restarted sentence = repeated take
        a, b = sents[si], sents[si + 1]
        ta, tb = [toks[i] for i in a], [toks[i] for i in b]
        if len(ta) < 2 or len(tb) <= len(ta):
            continue
        same = sum(1 for x, y in zip(ta, tb) if x == y) / float(len(ta))
        if (same >= 0.75 and ta[:2] == tb[:2]) or (not sentence_complete(words, a) and ta[:2] == tb[:2]):
            for i in a:
                keep[i], why[i] = False, 'repeated take'
    kept = [i for i in range(n) if keep[i]]
    sub = [words[i] for i in kept]
    sents = [[kept[j] for j in s] for s in sentences_of(sub)] if sub else []
    while len(sents) > 1 and not sentence_complete(words, sents[-1]):   # never end mid-sentence
        for i in sents[-1]:
            keep[i], why[i] = False, 'unfinished last sentence'
        sents.pop()
    return sorted(why.items())


# ------------------------------------------------------------------ audio envelope
def audio_env(wav, sr=16000, hop=0.01):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', wav, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'],
                         stdout=subprocess.PIPE).stdout
    x = np.frombuffer(raw, np.float32)
    n = int(sr * hop)
    m = len(x) // n
    if m == 0:
        return np.full(1, -90.0)
    fr = x[:m * n].reshape(m, n)
    return 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-7)


# ------------------------------------------------------------------ faces
def find_model(name):
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (os.environ.get('NR_' + name.split('.')[0].upper(), ''), os.path.join(here, 'models', name),
              os.path.join(here, 'claude-video-effects', 'models', name),
              os.path.expanduser('~/claude-video-effects/models/' + name),
              '/home/claude/claude-video-effects/models/' + name):
        if p and os.path.exists(p):
            return p
    return None


class FaceDet:
    def __init__(self, size):
        self.size = size
        p = find_model('yunet.onnx')
        self.yn = None
        if p:
            try:
                self.yn = cv2.FaceDetectorYN.create(p, '', size, 0.7, 0.3, 50)
            except Exception:
                self.yn = None
        self.haar = None
        if self.yn is None:
            try:
                self.haar = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades,
                                                               'haarcascade_frontalface_default.xml'))
            except Exception:
                self.haar = None
        self.kind = 'YuNet' if self.yn is not None else ('Haar' if self.haar is not None else 'none')

    def detect(self, img):
        """returns best face as dict in FULL 1080x1920 coords, or None"""
        sx, sy = W / float(img.shape[1]), H / float(img.shape[0])
        if self.yn is not None:
            _, f = self.yn.detect(img)
            if f is None or len(f) == 0:
                return None
            f = max(f, key=lambda r: r[2] * r[3] * r[-1])
            if f[-1] < 0.75:
                return None
            lm = [(f[4 + 2 * k] * sx, f[5 + 2 * k] * sy) for k in range(5)]
            return dict(x=f[0] * sx, y=f[1] * sy, w=f[2] * sx, h=f[3] * sy, score=float(f[-1]), lm=lm)
        if self.haar is not None:
            g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            r = self.haar.detectMultiScale(g, 1.1, 6, minSize=(30, 30))
            if len(r) == 0:
                return None
            x, y, w, h = max(r, key=lambda q: q[2] * q[3])
            return dict(x=x * sx, y=y * sy, w=w * sx, h=h * sy, score=0.8, lm=None)
        return None


def analyse(upright, fps, dur):
    aw, ah = 540, 960
    det = FaceDet((aw, ah))
    step = max(1, int(round(float(fps) / 10)))
    rd = FrameReader(upright, (aw, ah))
    win = cv2.createHanningWindow((135, 240), cv2.CV_64F)
    samples, motion, prev_small, prev_pc = [], [], None, None
    i = 0
    while True:
        f = rd.read()
        if f is None:
            break
        small = cv2.cvtColor(cv2.resize(f, (135, 240), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
        sm = small.astype(np.float32)
        motion.append(0.0 if prev_small is None else float(np.mean(np.abs(sm - prev_small))))
        prev_small = sm
        if i % step == 0:
            face = det.detect(f)
            pc = small.astype(np.float64)
            shift = 0.0
            if prev_pc is not None:
                (dx, dy), _ = cv2.phaseCorrelate(prev_pc, pc, win)
                shift = math.hypot(dx, dy) / 135.0 / (step / float(fps))   # frame-widths per second
            prev_pc = pc
            sharp = 0.0
            if face:
                x0, y0 = int(max(0, face['x'] / 2)), int(max(0, face['y'] / 2))
                x1, y1 = int(min(aw, (face['x'] + face['w']) / 2)), int(min(ah, (face['y'] + face['h']) / 2))
                if x1 - x0 > 8 and y1 - y0 > 8:
                    sharp = float(cv2.Laplacian(cv2.cvtColor(f[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY), cv2.CV_64F).var())
            samples.append(dict(i=i, t=i / float(fps), face=face, shift=shift, sharp=sharp))
        i += 1
    rd.close()
    return samples, np.array(motion), det.kind, i


class FaceTrack:
    def __init__(self, samples):
        self.s = [(x['t'], x['face']) for x in samples]
        self.t = np.array([a for a, _ in self.s]) if self.s else np.zeros(0)

    def at(self, t, win=0.3):
        """median face box (x0,y0,x1,y1) around time t (source seconds) or None"""
        if not len(self.t):
            return None
        for wnd in (win, 0.8):
            lo, hi = np.searchsorted(self.t, t - wnd), np.searchsorted(self.t, t + wnd)
            fs = [self.s[k][1] for k in range(lo, hi) if self.s[k][1]]
            if fs:
                b = np.median([[f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h']] for f in fs], axis=0)
                return tuple(float(v) for v in b)
        return None

    def span(self, t0, t1):
        if not len(self.t):
            return []
        lo, hi = np.searchsorted(self.t, t0 - 0.05), np.searchsorted(self.t, t1 + 0.05)
        return [self.s[k][1] for k in range(lo, hi) if self.s[k][1]]


# ------------------------------------------------------------------ segmentation (person mask)
def guided(I, p, r=8, eps=2e-3):
    box = lambda x: cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
    mI, mp_ = box(I), box(p)
    a = (box(I * p) - mI * mp_) / (box(I * I) - mI * mI + eps)
    b = mp_ - a * mI
    return np.clip(box(a) * I + box(b), 0, 1)


class Segmenter:
    """mediapipe selfie segmentation (offline .tflite). Mask at 360x640, smoothed over 3 frames, feathered."""
    SW, SH = 360, 640

    def __init__(self):
        self.ok, self.kind, self.err = False, 'none', ''
        self.buf = []
        self.ts = 0
        self.flick = []
        self.last = None
        model = find_model('selfie_segmenter.tflite')
        try:
            import mediapipe as mp
            from mediapipe.tasks.python import vision
            from mediapipe.tasks.python.core.base_options import BaseOptions
            if not model:
                raise RuntimeError('selfie_segmenter.tflite not found')
            self.mp = mp
            self.seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
                base_options=BaseOptions(model_asset_path=model), running_mode=vision.RunningMode.VIDEO,
                output_confidence_masks=True, output_category_mask=False))
            self.ok, self.kind = True, 'mediapipe selfie segmenter'
        except Exception as e:
            self.err = str(e)[:120]

    def reset(self):
        self.buf = []
        self.last = None

    def close(self):
        try:
            if self.ok:
                self.seg.close()
                self.ok = False
        except Exception:
            pass

    def __call__(self, bgr):
        small = cv2.resize(bgr, (self.SW, self.SH), interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        self.ts += 40
        img = self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb))
        ms = self.seg.segment_for_video(img, self.ts).confidence_masks
        m = ms[-1].numpy_view().astype(np.float32)
        m = m.reshape(m.shape[0], m.shape[1])
        if m.shape[:2] != (self.SH, self.SW):
            m = cv2.resize(m, (self.SW, self.SH), interpolation=cv2.INTER_LINEAR)
        m = guided(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255, m)
        m = np.clip((m - 0.5) * 1.8 + 0.5, 0, 1)
        self.buf = (self.buf + [m])[-3:]                              # smooth over 3 frames
        sm = np.mean(self.buf, axis=0) if len(self.buf) > 1 else m
        sm = cv2.GaussianBlur(sm, (0, 0), 1.6)                        # feathered edge
        if self.last is not None:
            self.flick.append(float(np.mean(np.abs(sm - self.last))))
        self.last = sm
        return sm


def mask_full(m):
    return cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)


# ------------------------------------------------------------------ 3. classify
def classify(words, samples, dur):
    speech = 0.0
    if words:
        iv = sorted((w['s'], w['e']) for w in words)
        a, b = iv[0]
        for s, e in iv[1:]:
            if s - b < 0.35:
                b = max(b, e)
            else:
                speech += b - a
                a, b = s, e
        speech += b - a
    speech_ratio = speech / max(dur, 0.1)
    faces = [s['face'] for s in samples if s['face']]
    face_ratio = len(faces) / float(max(1, len(samples)))
    face_h = float(np.median([f['h'] / H for f in faces])) if faces else 0.0
    shifts = [s['shift'] for s in samples[1:]]
    cam = float(np.median(shifts)) if shifts else 0.0
    cam90 = float(np.percentile(shifts, 90)) if shifts else 0.0
    jit = 0.0
    if len(faces) > 3:
        c = np.array([[f['x'] + f['w'] / 2, f['y'] + f['h'] / 2] for f in faces])
        jit = float(np.median(np.abs(np.diff(c, axis=0)).sum(1)) / max(1, np.median([f['h'] for f in faces])))
    nofacerun, run_ = 0.0, 0.0
    dt = (samples[1]['t'] - samples[0]['t']) if len(samples) > 1 else 0.1
    for s in samples:
        run_ = run_ + dt if not s['face'] else 0.0
        nofacerun = max(nofacerun, run_)
    m = dict(speech_ratio=round(speech_ratio, 2), face_ratio=round(face_ratio, 2), face_height=round(face_h, 3),
             camera_motion=round(cam, 3), camera_motion_p90=round(cam90, 3), face_jitter=round(jit, 3),
             longest_no_face_s=round(nofacerun, 1))
    if speech_ratio >= 0.3 and face_ratio >= 0.6 and nofacerun < 2.0:
        if face_h >= 0.28 or (cam >= 0.06 and jit >= 0.08):
            t, why = 'SELFIE', 'speech + face present; face very large or handheld movement'
        else:
            t, why = 'TALKING_HEAD', 'speech + steady face most of the time'
    elif speech_ratio >= 0.3:
        t, why = 'MIXED', 'speech, but face missing for long stretches (property shots)'
    elif face_ratio < 0.5 or cam >= 0.03:
        t, why = 'WALKTHROUGH', 'little speech, moving camera / no presenter'
    else:
        t, why = ('MIXED' if speech_ratio >= 0.12 else 'WALKTHROUGH'), 'little speech'
    return t, why, m


# ------------------------------------------------------------------ 4. cut
class Timeline:
    def __init__(self, segs, fps):
        self.segs, self.fps = segs, float(fps)
        self.offs, o = [], 0
        for fa, fb in segs:
            self.offs.append(o)
            o += fb - fa
        self.nout = o

    @property
    def dur(self):
        return self.nout / self.fps

    def s2o(self, t):
        f = t * self.fps
        for (fa, fb), off in zip(self.segs, self.offs):
            if f < fa:
                return off / self.fps
            if f <= fb:
                return (off + f - fa) / self.fps
        return self.dur

    def o2s(self, t):
        f = t * self.fps
        for (fa, fb), off in zip(self.segs, self.offs):
            if f < off + (fb - fa):
                return (fa + max(0.0, f - off)) / self.fps
        return self.segs[-1][1] / self.fps if self.segs else 0.0

    def cut_points(self):
        return [o / self.fps for o in self.offs[1:]]


def refine_words(words, env, hop=0.01):
    """Make word edges follow the audio. Whisper often stretches a word over the silence next to it;
    silence is trimmed off the word (it is a pause, not part of the word), sound is never trimmed."""
    if not words:
        return 0.0
    n = len(env)
    sm = np.array([np.median(env[max(0, k - 2):k + 3]) for k in range(n)]) if n > 5 else env
    noise = float(np.percentile(sm, 20))
    vals = [sm[int(w['s'] / hop):max(int(w['s'] / hop) + 1, int(w['e'] / hop))] for w in words]
    speech_lvl = float(np.median(np.concatenate([v for v in vals if len(v)])))
    thr = max(noise + 10.0, speech_lvl - 14.0)
    snd_thr = noise + 7.0
    deep_thr = noise + 4.0
    snd = lambda k: 0 <= k < n and sm[k] > snd_thr
    deep = lambda k: 0 <= k < n and sm[k] < deep_thr
    for w in words:
        s, e = w['s'], w['e']
        for _ in range(3):
            a, b = int(round(s / hop)), int(round(e / hop))
            best, k = None, a
            while k < b:
                if deep(k):
                    j = k
                    while j < b and deep(j):
                        j += 1
                    if (j - k) * hop >= 0.2 and (best is None or j - k > best[1] - best[0]):
                        best = (k, j)
                    k = j
                else:
                    k += 1
            if best is None:
                break
            before = sum(1 for q in range(a, best[0]) if snd(q))
            after = sum(1 for q in range(best[1], b) if snd(q))
            if before <= after:
                s = best[1] * hop - 0.02
            else:
                e = best[0] * hop + 0.02
            if e - s < 0.06:
                s, e = w['s'], w['e']
                break
        a, b = int(round(s / hop)), int(round(e / hop))
        j = a
        while j < b - 4 and not snd(j):
            j += 1
        s = max(s, j * hop - 0.02)
        j = b - 1
        while j > int(s / hop) + 4 and not snd(j):
            j -= 1
        e = min(e, (j + 1) * hop + 0.02)
        w['rs'], w['re'] = s, max(e, s + 0.04)
    for k, w in enumerate(words):
        lo = words[k - 1]['re'] if k else 0.0
        hi = words[k + 1]['rs'] if k + 1 < len(words) else n * hop
        j = int(w['rs'] / hop) - 1
        while j * hop > max(lo, w['rs'] - 0.25) and snd(j):
            j -= 1
        w['rs'] = max(lo, min(w['rs'], (j + 1) * hop))
        j = int(w['re'] / hop)
        while j * hop < min(hi, w['re'] + 0.25) and snd(j):
            j += 1
        w['re'] = min(max(w['re'], j * hop), max(hi, w['re']))
    for k in range(1, len(words)):
        if words[k]['rs'] < words[k - 1]['re']:
            m = (words[k]['rs'] + words[k - 1]['re']) / 2
            words[k]['rs'] = words[k - 1]['re'] = m
    return thr


def quiet_runs(env, a, b, thr, hop=0.01):
    ka, kb = int(math.ceil(a / hop)), int(b / hop)
    if kb <= ka:
        return [(a, b)]
    loud = env[ka:kb] > thr
    runs, k = [], 0
    while k < len(loud):
        if loud[k]:
            j = k
            while j < len(loud) and loud[j]:
                j += 1
            if (j - k) * hop >= 0.12:
                runs.append(((ka + k) * hop, (ka + j) * hop))
            k = j
        else:
            k += 1
    out, cur = [], a
    for s, e in runs:
        out.append((cur, s))
        cur = e
    out.append((cur, b))
    return [(x, y) for x, y in out if y > x]


def plan_cuts_speech(words, env, thr, dur, ctype, track, dropped=()):
    """words = KEPT words only; dropped = removed words (false starts etc.) - their audio is cut out."""
    removed = []
    dropped = sorted(dropped, key=lambda w: w['rs'])
    has_drop = lambda a, b: any(a - 1e-3 <= d['rs'] and d['re'] <= b + 1e-3 for d in dropped)
    for k in range(len(words) - 1):
        a, b = words[k]['re'], words[k + 1]['rs']
        if has_drop(a, b):
            removed.append((a + PAD, b - PAD))
            continue
        if b - a <= MIN_PAUSE:
            continue
        if ctype == 'MIXED' and b - a > 1.5 and not track.span(a, b):
            mid = (a + b) / 2
            keep = min(2.5, b - a - 2 * PAD)
            if mid - keep / 2 - (a + PAD) > 0.02:
                removed.append((a + PAD, mid - keep / 2))
            if (b - PAD) - (mid + keep / 2) > 0.02:
                removed.append((mid + keep / 2, b - PAD))
            continue
        for x, y in quiet_runs(env, a, b, thr):
            if y - x > MIN_PAUSE:
                removed.append((x + PAD, y - PAD))
    lead = PAD
    if ctype == 'MIXED' and words[0]['rs'] > 1.5 and not track.span(0, words[0]['rs']):
        lead = min(2.5, words[0]['rs'])
    first_drop = [d['re'] for d in dropped if d['re'] <= words[0]['rs']]
    start = max(0.0, words[0]['rs'] - lead, (max(first_drop) + 0.02) if first_drop else 0.0)
    tail = 0.12
    if ctype == 'MIXED' and dur - words[-1]['re'] > 1.5 and not track.span(words[-1]['re'], dur):
        tail = 2.5
    end = min(dur, words[-1]['re'] + tail)
    after = [d['rs'] for d in dropped if d['rs'] >= words[-1]['re']]
    if after:
        end = min(end, max(words[-1]['re'] + 0.02, min(after) - 0.03))
    return start, end, removed


def plan_cuts_walkthrough(motion, fps, words, dur):
    fps = float(fps)
    m = np.convolve(motion, np.ones(5) / 5, mode='same') if len(motion) > 5 else motion
    med = float(np.median(m)) if len(m) else 0
    in_word = lambda t: any(w['s'] - 0.05 <= t <= w['e'] + 0.05 for w in words)
    scenes, last = [0.0], 0.0
    for k, v in enumerate(motion):
        t = k / fps
        if v > max(12.0, 5 * med) and t - last > 1.0:
            scenes.append(t)
            last = t
    scenes.append(dur)
    removed = []
    for s0, s1 in zip(scenes[:-1], scenes[1:]):
        t = s0
        while s1 - t > 4.0:
            lo, hi = int((t + 2.5) * fps), int(min(t + 4.0, s1) * fps)
            if hi <= lo:
                break
            c = (lo + int(np.argmax(m[lo:hi]))) / fps if hi > lo else (t + 3.2)
            while in_word(c) and c < s1:
                c += 0.05
            skip = 0.8 if (s1 - c) > 3.3 else 0.0
            if skip and not any(in_word(c + q * 0.1) for q in range(9)):
                removed.append((c, c + skip))
                t = c + skip
            else:
                t = c
        if s1 - s0 < 1.0 and not any(in_word(s0 + q * 0.1) for q in range(int((s1 - s0) * 10))):
            removed.append((s0, s1))
    return 0.0, dur, removed


def to_segments(start, end, removed, fps):
    fps = float(fps)
    removed = sorted((a, b) for a, b in removed if b - a > 1.0 / fps)
    keep, cur = [], start
    for a, b in removed:
        if a > cur:
            keep.append((cur, a))
        cur = max(cur, b)
    if end > cur:
        keep.append((cur, end))
    segs = []
    for a, b in keep:
        fa, fb = int(round(a * fps)), int(round(b * fps))
        if fb - fa < 1:
            continue
        if segs and fa - segs[-1][1] <= 1:
            segs[-1] = (segs[-1][0], fb)
        else:
            segs.append((fa, fb))
    return segs


# ------------------------------------------------------------------ 5-8. plan the edit
class Plan:
    pass


def make_zones(P):
    lv = LEVELS[P.ctype]
    tl, words = P.tl, P.words
    if not words or P.ctype == 'WALKTHROUGH':
        return [dict(t0=0.0, t1=tl.dur, level='WIDE', z=1.0)]
    cuts = tl.cut_points()
    bounds = [0.0]
    for si in P.sents[1:]:
        w0 = words[si[0]]
        prev_end = words[si[0] - 1]['eo']
        cand = [c for c in cuts if prev_end - 0.02 <= c <= w0['so'] + 0.02]
        b = min(cand, key=lambda c: abs(c - w0['so'])) if cand else max(prev_end, w0['so'] - 0.06)
        bounds.append(b)
    bounds.append(tl.dur)
    zones = []
    for k in range(len(P.sents)):
        t0, t1 = bounds[k], bounds[k + 1]
        if t1 - t0 < 0.05:
            continue
        level = 'KEY' if k == P.key_sent else ('TIGHT' if k % 2 == 1 else 'WIDE')
        pieces = [(t0, t1)]
        while pieces[-1][1] - pieces[-1][0] > 5.0:
            a, b = pieces.pop()
            target = a + min(3.5, (b - a) / 2)
            opts = [c for c in cuts if a + 1.5 < c < b - 1.5] + \
                   [words[j]['so'] - 0.03 for j in P.sents[k] if a + 1.5 < words[j]['so'] < b - 1.5]
            c = min(opts, key=lambda c: abs(c - target)) if opts else target
            pieces += [(a, c), (c, b)]
        for j, (a, b) in enumerate(pieces):
            L = level if j == 0 else ('WIDE' if zones and zones[-1]['level'] != 'WIDE' else 'TIGHT')
            zones.append(dict(t0=a, t1=b, level=L, z=lv[L]))
    if zones:
        z0 = zones[0]
        if z0['t1'] > 1.5 + 0.4:
            zones.insert(1, dict(t0=1.5, t1=z0['t1'], level='WIDE', z=lv['WIDE']))
            z0['t1'] = 1.5
        z0['level'], z0['z'] = 'FIRST', lv['FIRST']
        if len(zones) > 1 and zones[1]['level'] in ('TIGHT', 'FIRST') and zones[1]['level'] != 'KEY':
            zones[1]['level'], zones[1]['z'] = 'WIDE', lv['WIDE']
    out = []
    for z in zones:
        if out and abs(out[-1]['z'] - z['z']) < 1e-3:
            out[-1]['t1'] = z['t1']
        else:
            out.append(z)
    return out


def split_zones(P, t):
    lv = LEVELS[P.ctype]
    for k, z in enumerate(P.zones):
        if z['t0'] + 0.5 < t < z['t1'] - 0.5:
            nl = 'WIDE' if z['level'] != 'WIDE' else 'TIGHT'
            nxt = P.zones[k + 1] if k + 1 < len(P.zones) else None
            if nxt is not None and abs(nxt['z'] - lv[nl]) < 1e-3:
                return False
            P.zones.insert(k + 1, dict(t0=t, t1=z['t1'], level=nl, z=lv[nl]))
            z['t1'] = t
            return True
    return False


def zone_at(P, t):
    for z in P.zones:
        if z['t0'] - 1e-6 <= t < z['t1']:
            return z
    return P.zones[-1]


def head_top(f):
    return f[1] - 0.35 * (f[3] - f[1])


def zone_crop(P, z):
    """crop window for a zone: horizontally centred on the face, vertical headroom shift applied.
    Also sets the motion anchor (centre of the top of the head) so push-ins never move the head top."""
    zz = z['z']
    cw, ch = W / zz, H / zz
    if z.get('face'):
        fx = (z['face'][0] + z['face'][2]) / 2
        fy = (z['face'][1] + z['face'][3]) / 2
    else:
        fx, fy = W / 2, H / 2
    x0 = clamp(fx - cw / 2, 0, W - cw)
    y0 = clamp(fy - max(fy, 0.28 * H) / zz, 0, H - ch)
    y0 -= z.get('shift', 0.0) / zz
    z['x0'], z['y0'] = x0, y0
    if z.get('face'):
        f = z['face']
        z['anchor'] = (((f[0] + f[2]) / 2 - x0) * zz, clamp((head_top(f) - y0) * zz, 0, H))
    else:
        z['anchor'] = (W / 2, H / 2)
    return x0, y0


def refresh_crops(P):
    for z in P.zones:
        mid0, mid1 = P.tl.o2s(z['t0']), P.tl.o2s(max(z['t0'], z['t1'] - 1e-3))
        fs = P.track.span(mid0, mid1)
        z['face'] = (tuple(np.median([[f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h']] for f in fs], axis=0))
                     if fs else None)
        if z['face'] is None and z['z'] > 1.0:
            z['z'], z['level'] = 1.0, 'WIDE'
        zone_crop(P, z)


# ---- motion
def kh_zoom(f):
    """v7 kinetic hook: extra zoom at output frame f (115 % -> 100 %, ease-out over KH_F frames)."""
    if f < 0 or f >= KH_F:
        return 1.0
    return 1.0 + KH_ZOOM * (1 - ease_out(f / float(KH_F)))


def motion_scale(P, t, z=None):
    kz = kh_zoom(int(round(t * float(P.fps)))) if getattr(P, 'kh_on', False) else 1.0
    if not P.opt.motion:
        return kz
    return kz * _motion_scale(P, t, z)


def _motion_scale(P, t, z=None):
    z = z or zone_at(P, t)
    d = max(1e-3, z['t1'] - z['t0'])
    s = 1.0 + PUSH * ease_io((t - z['t0']) / d)
    fpsf = float(P.fps)
    pk = 0.0
    for tp in P.punches:
        f = (t - tp) * fpsf
        if 0 <= f < 3:
            pk = max(pk, PUNCH * ease_out(f / 3.0))
        elif 3 <= f < 9:
            pk = max(pk, PUNCH * (1 - ease_io((f - 3) / 6.0)))
    return s * (1 + pk)


def compose(A, B):
    M = np.zeros((2, 3))
    M[:, :2] = A[:, :2] @ B[:, :2]
    M[:, 2] = A[:, :2] @ B[:, 2] + A[:, 2]
    return M


def photo_at(P, t):
    for v in P.visuals:
        if v.get('photo') and v['t0'] <= t < v['t1']:
            return v
    return None


def _hook_ease(P, t):
    """(previous zone, weight of the NEW framing) while the reframing at the end of the hook glides, else None."""
    if not getattr(P, 'hook_on', False):
        return None
    d = HOOK_EASE / float(P.fps)
    if not (P.hook_t1 - 1e-6 <= t < P.hook_t1 + d):
        return None
    k = next((i for i, z in enumerate(P.zones) if abs(z['t0'] - P.hook_t1) < 1e-3), None)
    if not k:
        return None
    return P.zones[k - 1], ease_io((t - P.hook_t1) / d)


def xforms(P, t):
    """(Mbase, Mphoto|None): source(upright) -> output for the frame; Mphoto moves the person layer
    (Umesh scaled to 80% and moved down) while a property photo is on screen."""
    Mb, Mp = _xforms(P, t)
    he = _hook_ease(P, t)
    if he is not None and he[1] < 1:
        Mo, _ = _xforms(P, t, he[0])
        Mb = Mo * (1 - he[1]) + Mb * he[1]
    return Mb, Mp


def _xforms(P, t, z=None):
    z = z or zone_at(P, t)
    zz = z['z']
    Mz = np.array([[zz, 0, -z['x0'] * zz], [0, zz, -z['y0'] * zz]], float)
    s = motion_scale(P, t, z)
    ax, ay = z['anchor']
    Mm = np.array([[s, 0, ax * (1 - s)], [0, s, ay * (1 - s)]], float)
    Mb = compose(Mm, Mz)
    Mp = None
    v = photo_at(P, t)
    if v is not None:
        dy = v['person_dy']
        Mp = np.array([[0.8, 0, ax * 0.2], [0, 0.8, ay * 0.2 + dy]], float)
    return Mb, Mp


def face_out(P, t_out):
    b = P.track.at(P.tl.o2s(min(t_out, P.tl.dur - 1e-3)))
    if b is None:
        return None
    Mb, Mp = xforms(P, t_out)
    M = compose(Mp, Mb) if Mp is not None else Mb
    x0, y0 = M[0, 0] * b[0] + M[0, 2], M[1, 1] * b[1] + M[1, 2]
    x1, y1 = M[0, 0] * b[2] + M[0, 2], M[1, 1] * b[3] + M[1, 2]
    return (x0, y0, x1, y1)


def faces_out(P, t0, t1, step=0.04):
    out, t = [], t0
    while t <= t1 + 1e-6:
        f = face_out(P, t)
        if f:
            out.append((t, f))
        t += step
    return out


# ---- hook
def hook_clause(P):
    if not P.words or not P.sents:
        return None, False
    toks = [P.words[k]['w'] for k in P.sents[0]]
    clause = []
    for t in toks:
        clause.append(t)
        if re.search(r"[,;:]$", t) and len(clause) >= 3:
            break
    clean = [re.sub(r"[^\w'%$-]", '', t) for t in clause]
    clean = [c for c in clean if c]
    q = bool(re.match(r"(thinking|want|wanting|looking|planning|are you|do you|is |should|how|what|why|can|will|ready)",
                      ' '.join(clean).lower())) or toks[len(clause) - 1].endswith('?')
    return clean, q


def make_hook_text(P):
    """v1 hook (box style): up to 6 words of the first clause."""
    clean, q = hook_clause(P)
    if not clean:
        return None
    clean = list(clean)
    while clean and clean[0].lower() in FILLERS and len(clean) > 3:
        clean.pop(0)
    if len(clean) > 6:
        clean = clean[:6]
        while len(clean) > 3 and clean[-1].lower() in STOPS:
            clean.pop()
    txt = ' '.join(clean).upper()
    return txt + ('?' if q and not txt.endswith('?') else '')


def hb_fit(words):
    """best 2-line split of words for the text-behind-head title -> (lines, em) or None."""
    best = None
    maxw = 0.92 * W
    cands = [[' '.join(words)]] if len(words) == 1 else []
    for k in range(1, len(words)):
        cands.append([' '.join(words[:k]), ' '.join(words[k:])])
    for lines in cands:
        em = min(HB_MAX, min(maxw / max(1.0, tw('blk', l, 100) / 100.0) for l in lines))
        if best is None or em > best[1]:
            best = (lines, em)
    return best


def make_hook_behind_text(P):
    """BIG 2-line hook from his first clause, lead-ins dropped so it fits at ~140-160 px."""
    clean, q = hook_clause(P)
    if not clean:
        return None
    ws = [c for c in clean]
    low = ' '.join(ws).lower()
    for li in LEAD_INS:
        if low.startswith(li + ' ') and len(ws) - len(li.split()) >= 2:
            ws = ws[len(li.split()):]
            break
    while ws and ws[0].lower() in FILLERS and len(ws) > 2:
        ws.pop(0)
    tries = []
    for a in range(0, len(ws)):
        for b in range(len(ws), a, -1):
            sub = ws[a:b]
            if len(sub) < 2 and len(ws) >= 2:
                continue
            if sub[-1].lower() in STOPS or sub[0].lower() in ('and', 'or', 'to', 'of'):
                continue
            txt = [s.upper() for s in sub]
            if q:
                txt[-1] = txt[-1].rstrip('?') + '?'
            fit = hb_fit(txt)
            if fit and fit[1] >= HB_MIN:
                tries.append((len(sub), -a, fit))
    if not tries:
        return None
    tries.sort(key=lambda x: (x[0], x[1], x[2][1]), reverse=True)
    lines, em = tries[0][2]
    return dict(lines=lines, em=em, text=' '.join(lines))


def build_hook_behind(P, hb):
    em = int(hb['em'])
    sprs = []
    ch = cap_h('blk', em)
    gap = 0.20 * em
    for ln in hb['lines']:
        spr, inf = text_sprite([(ln, WHITE)], 'blk', em, shadow=(0, 6, 16, 0.85, NAVY))
        sprs.append((spr, inf))
    hb['sprites'] = sprs
    hb['cap'] = ch
    hb['gap'] = gap
    hb['block_h'] = len(sprs) * ch + (len(sprs) - 1) * gap
    hb['width'] = max(i['text_w'] for _, i in sprs)
    hb['words'] = []                                   # v7: one sprite per word for the kinetic hook
    f = font('blk', em)
    for li, ln in enumerate(hb['lines']):
        toks = ln.split(' ')
        for k, tok in enumerate(toks):
            xl = f.getlength(' '.join(toks[:k]) + (' ' if k else ''))
            spr, inf = text_sprite([(tok, WHITE)], 'blk', em, shadow=(0, 6, 16, 0.85, NAVY))
            n = len(hb['words'])
            start = -KH_WORD_F if n == 0 else 1 + (n - 1) * KH_STEP     # word 1 already landed on frame 0
            hb['words'].append(dict(line=li, xl=xl, w=f.getlength(tok), spr=spr, inf=inf, start=start, text=tok))
    hb['landed_f'] = hb['words'][-1]['start'] + KH_WORD_F
    return hb


def word_pop(fr_):
    """kinetic hook word scale/alpha at frames since its start: 60 -> 105 -> 100 %."""
    if fr_ < 0:
        return 0.0, 0.0
    if fr_ < 3:
        return 0.60 + 0.45 * ease_out((fr_ + 1) / 3.0), (0.55 if fr_ < 1 else 1.0)
    if fr_ < KH_WORD_F:
        return 1.05 - 0.05 * ease_io((fr_ - 2) / float(KH_WORD_F - 2)), 1.0
    return 1.0, 1.0


def draw_hook_words(P, img, fi, bl, a_in):
    hb = P.hb
    for wd in hb['words']:
        s, a = word_pop(fi - wd['start'])
        if a <= 0:
            continue
        lspr, linf = hb['sprites'][wd['line']]
        lx, ly = hb['pos'][wd['line']]
        X, Y = lx + linf['cap_x0'], ly + linf['cap_y0']
        wc, yc = X + wd['xl'] + wd['w'] / 2.0, Y + hb['cap'] / 2.0
        spr, inf = wd['spr'], wd['inf']
        h, w = spr.shape[:2]
        ox, oy = w / 2.0 - inf['cap_x0'] - inf['text_w'] / 2.0, h / 2.0 - inf['cap_y0'] - inf['cap_h'] / 2.0
        if fi - wd['start'] < 3:                                    # slight motion blur: a faint leading ghost
            g = s * 1.07
            bl.blit_scaled(img, spr, wc + ox * g, yc + oy * g, g, 0.28 * a * a_in, 'hook')
        bl.blit_scaled(img, spr, wc + ox * s, yc + oy * s, s, a * a_in, 'hook')


def place_hook_behind(hb, top):
    hb['top'] = top
    hb['pos'] = []
    y = top
    for spr, inf in hb['sprites']:
        hb['pos'].append((W / 2 - inf['cap_x0'] - inf['text_w'] / 2, y - inf['cap_y0']))
        y += hb['cap'] + hb['gap']
    hb['rect'] = (W / 2 - hb['width'] / 2, top, W / 2 + hb['width'] / 2, top + hb['block_h'])


def layout_hook_box(P, text):
    """v1 fallback hook: Navy box with white title + orange underline in the 10-19% band."""
    maxw = 0.86 * W
    words = text.split()
    options = [[text]]
    if len(words) >= 3:
        cut = min(range(1, len(words)), key=lambda k: abs(len(' '.join(words[:k])) - len(' '.join(words[k:]))))
        options.append([' '.join(words[:cut]), ' '.join(words[cut:])])
    best = None
    for lines in options:
        for em in range(92, 52, -3):
            wmax = max(tw('blk', l, em) for l in lines)
            if wmax > maxw - 2 * 34:
                continue
            ch = cap_h('blk', em)
            lead = 0.30 * em
            hbox = 22 + len(lines) * ch + (len(lines) - 1) * lead + 12 + 6 + 20
            if TOP0 + hbox <= TOP1 + 1:
                if best is None or em > best['em'] * 1.05:
                    best = dict(lines=lines, em=em, w=wmax + 68, h=hbox, ch=ch, lead=lead)
                break
    if best is None:
        return None
    x0 = W / 2 - best['w'] / 2
    best['rect'] = (x0, TOP0, x0 + best['w'], TOP0 + best['h'])
    img = Image.new('RGBA', (int(best['w']) + 2, int(best['h']) + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, best['w'], best['h']], 16, fill=NAVY + (247,))
    y = 22
    for ln in best['lines']:
        d.text((best['w'] / 2, y + best['ch']), ln, font=font('blk', best['em']), fill=WHITE, anchor='ms')
        y += best['ch'] + best['lead']
    y = y - best['lead'] + 12
    uw = min(wmax, best['w'] - 40)
    d.rounded_rectangle([best['w'] / 2 - uw / 2, y, best['w'] / 2 + uw / 2, y + 6], 3, fill=ORANGE)
    best['sprite'] = pil_to_pm(img)
    best['text'] = text
    return best


# ---- numbers (v1) and spoken visuals
def words2num(toks):
    total, cur, seen = 0, 0, False
    for t in toks:
        if t in NUMW:
            cur += NUMW[t]
            seen = True
        elif t == 'hundred':
            cur = max(cur, 1) * 100
            seen = True
        elif t in SCALEW:
            total += max(cur, 1) * SCALEW[t]
            cur = 0
            seen = True
        elif t == 'and':
            continue
        else:
            return None
    return total + cur if seen else None


def find_numbers(P):
    """v1 key-graphic number finder: money, %, numbers with units."""
    words = P.words
    toks = [core(w['w']) for w in words]
    sent_of = {}
    for si, s in enumerate(P.sents):
        for k in s:
            sent_of[k] = si
    sent_text = [' '.join(toks[k] for k in s) for s in P.sents]
    cands = []
    numish = lambda t: bool(re.search(r'\d', t)) or t in NUMW or t in SCALEW or t in ('$', '%', 'percent', 'dollars')
    k = 0
    while k < len(words):
        t = toks[k]
        if numish(t) and t not in ('and',):
            j = k
            while j + 1 < len(words) and (numish(toks[j + 1]) or (toks[j + 1] in ('and', 'point', 'per', 'cent')
                                                                  and j + 2 < len(words) and numish(toks[j + 2]))
                                          or toks[j + 1] in ('percent', 'dollars', 'cent')):
                j += 1
            run_ = toks[k:j + 1]
            raw = [words[q]['w'].strip(',.;:!?') for q in range(k, j + 1)]
            money = any('$' in r for r in raw) or 'dollars' in run_
            pct = any('%' in r for r in raw) or 'percent' in run_ or 'cent' in run_
            digits = any(re.search(r'\d', r) for r in raw)
            unit = toks[j + 1] if j + 1 < len(words) and toks[j + 1] in UNITS else None
            val = None
            if digits:
                txt = ' '.join(r for r in raw if r.lower() not in ('dollars', 'percent', 'per', 'cent'))
                try:
                    num = float(re.sub(r'[^\d.]', '', txt) or 'x')
                    mult = 1000 if any(r in SCALEW for r in run_) else 1
                    val = num * (SCALEW.get(next((r for r in run_ if r in SCALEW), ''), 1) if mult > 1 else 1)
                except ValueError:
                    val = None
                if pct and '%' not in txt:
                    txt += '%'
                if money and '$' not in txt:
                    txt = '$' + txt
            else:
                val = words2num([r for r in run_ if r not in ('dollars', 'percent', 'per', 'cent')])
                txt = None
                if val is not None:
                    txt = '{:,}'.format(val)
                    if money:
                        txt = '$' + txt
                    if pct:
                        txt += '%'
            ok = txt and (digits or money or pct or unit or (val is not None and val >= 10))
            if ok:
                st = sent_text[sent_of.get(k, 0)] if P.sents else ''
                if not money and val is not None and val >= 50000 and not unit:
                    money = True                                  # "650 thousand" in property talk = a price
                cands.append(dict(k0=k, k1=j, txt=txt, val=val, money=money, pct=pct, unit=unit,
                                  sold='sold' in st.split()))
            k = j + 1
            continue
        k += 1
    return cands


def compact_money(v, txt):
    if v is None:
        return txt.upper()
    if v >= 10 ** 6:
        s = ('%.2f' % (v / 1e6)).rstrip('0').rstrip('.')
        return '$%sM' % s
    if v >= 10000:
        return '$%dK' % int(round(v / 1000.0))
    return '${:,}'.format(int(v))


def visual_candidates(P):
    words = P.words
    toks = [core(w['w']).replace("'", '') for w in words]
    st = [stem(t) for t in toks]
    cands, used = [], set()
    nums = find_numbers(P)
    for n in nums:
        if n['money'] or n['pct']:
            lab = 'SOLD' if n['sold'] else ('PRICE' if n['money'] else 'RATE')
            big = compact_money(n['val'], n['txt']) if n['money'] else n['txt'].upper()
            cands.append(dict(k0=n['k0'], k1=n['k1'], icon='dollar' if n['money'] else 'percent', label=big + ' ' + lab,
                              number=big, prio=0, word=' '.join(words[q]['w'] for q in range(n['k0'], n['k1'] + 1))))
            used.update(range(n['k0'], n['k1'] + 1))
    for s in SUBURBS:                                                # suburb -> map pin
        parts = s.lower().split()
        for k in range(len(words)):
            if toks[k:k + len(parts)] == parts and s.lower() not in COMMON_SUBURB_WORDS and k not in used:
                cands.append(dict(k0=k, k1=k + len(parts) - 1, icon='pin', label=s.upper(), number=None, prio=1,
                                  word=s))
                used.update(range(k, k + len(parts)))
    phrases = []
    for ph_list, icon, label, prio in VISUAL_MAP:
        for ph in ph_list:
            phrases.append(([stem(p) for p in ph.split()], icon, label, prio))
    phrases.sort(key=lambda x: -len(x[0]))
    k = 0
    while k < len(words):
        if k in used:
            k += 1
            continue
        hit = None
        for parts, icon, label, prio in phrases:
            L = len(parts)
            if st[k:k + L] == parts:
                hit = (parts, icon, label, prio)
                break
        if hit is None:
            k += 1
            continue
        parts, icon, label, prio = hit
        L = len(parts)
        if icon.startswith('badge'):                     # "First," / "Second" only when it starts a point
            raw = words[k]['w']
            lead = k == 0 or re.search(r'[.?!,:]$', words[k - 1]['w']) or re.search(r'[,:]$', raw)
            if not lead:
                k += 1
                continue
        num = None
        if k > 0 and (k - 1) not in used:
            pt = toks[k - 1]
            if re.fullmatch(r'\d+(\.\d+)?', pt):
                num = pt
            elif pt in NUMW and NUMW[pt] > 0:
                num = str(NUMW[pt])
        lab = label
        if num is not None:
            lab = num + ' ' + label + ('S' if num not in ('1',) and not label.endswith('S') else '')
            prio = 0
        cands.append(dict(k0=k - (1 if num else 0), k1=k + L - 1, icon=icon, label=lab, number=num, prio=prio,
                          word=' '.join(words[q]['w'].strip(',.?!') for q in range(k - (1 if num else 0), k + L))))
        used.update(range(k, k + L))
        k += L
    for c in cands:
        c['t'] = words[c['k0']]['so']
        tw_ = ' '.join(toks[c['k0']:c['k1'] + 1])
        c['pill'] = next((lab for ph, lab in JARGON if (ph == tw_ or ph == c['label'].lower()
                                                        or ph == c['label'].lower().replace('-', ' '))
                          and lab not in ('BUYERS',)), None)
        if c['pill'] and c['pill'].replace(' ', '') == c['label'].replace(' ', ''):
            c['pill'] = None
    return sorted(cands, key=lambda c: c['t'])


def choose_big_words(P):
    if not P.opt.big_words or not P.words or P.ctype == 'WALKTHROUGH':
        return []
    words = P.words
    vis_k, vis_st = set(), set()                      # v4: never an icon AND a big word for the same idea
    for g in getattr(P, 'visuals', []):
        for c in g['chips']:
            vis_k.update(range(c['k0'], c['k1'] + 1))
            vis_st.update(stem(x) for x in re.findall(r'[A-Za-z]+', c['label'] + ' ' + c['word']))
    hook_end = P.hook_t1 if P.hook_on else 0.0
    cands = []
    for s in P.sents:
        core_ws = [re.sub(r"[^\w'?!]", '', words[k]['w']) for k in s]
        if 1 <= len(s) <= 2 and re.search(r'[?!]$', words[s[-1]]['w']):
            txt = ' '.join(core_ws).upper()
            m = re.match(r"^(.*?)([?!]+)$", txt)
            runs = [(m.group(1), WHITE), (m.group(2), ORANGE)] if m else [(txt, ORANGE)]
            cands.append(dict(k0=s[0], k1=s[-1], runs=runs, text=txt, prio=0))
    for k, w in enumerate(words):
        c = core(w['w']).replace("'", '')
        if c in BIG_TERMS:
            prev = core(words[k - 1]['w']) if k else ''
            same_sent = k and not re.search(r'[.?!]$', words[k - 1]['w'])
            if prev and same_sent and prev not in STOPS and prev not in FILLERS and len(prev) <= 6:
                runs = [(prev.upper() + ' ', WHITE), (c.upper(), ORANGE)]
                k0 = k - 1
            else:
                runs = [(c.upper(), ORANGE)]
                k0 = k
            cands.append(dict(k0=k0, k1=k, runs=runs, text=''.join(r for r, _ in runs), prio=BIG_TERMS[c]))
    for n in find_numbers(P):
        if n['money'] or n['pct']:
            big = compact_money(n['val'], n['txt']) if n['money'] else n['txt'].upper()
            cands.append(dict(k0=n['k0'], k1=n['k1'], runs=[(big, ORANGE)], text=big, prio=1))
    limit = 1 if P.tl.dur < 15 else 2
    chosen = []
    cands = [c for c in cands if not (set(range(c['k0'], c['k1'] + 1)) & vis_k)
             and not any(stem(x) in vis_st for x in re.findall(r'[A-Za-z]+', c['text'].lower())
                         if x not in STOPS and len(x) > 2)]
    for c in sorted(cands, key=lambda c: (c['prio'], words[c['k0']]['so'])):
        t0 = words[c['k0']]['so'] - 0.05
        dur_w = words[c['k1']]['eo'] - words[c['k0']]['so']
        t1 = t0 + clamp(dur_w + 0.45, 0.6, 1.0)
        if t0 < hook_end + 0.2 or t1 > P.speech_end - 0.1:
            continue
        if broll_overlaps(P, t0, t1, 0.05):                    # v6: no big word over the B-roll / bubble
            continue
        if any(abs(t0 - o['t0']) < 4.0 for o in chosen):
            continue
        c.update(t0=t0, t1=t1)
        chosen.append(c)
        if len(chosen) >= limit:
            break
    return sorted(chosen, key=lambda c: c['t0'])


# ---------------------------------------------------------------- v3 icon loops
def _xf(prim, fn):
    k, c, d = prim
    if k == 'T':
        x, y, txt, size = d
        nx, ny = fn(x, y)
        return (k, c, (nx, ny, txt, size))
    return (k, c, [fn(x, y) for x, y in d])


def _tr(p, dx, dy):
    return _xf(p, lambda x, y: (x + dx, y + dy))


def _rot(p, cx, cy, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return _xf(p, lambda x, y: (cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca))


def _sc(p, cx, cy, s):
    return _xf(p, lambda x, y: (cx + (x - cx) * s, cy + (y - cy) * s))


def _bbox(prims):
    pts = [q for p in prims for q in ([p[2][:2]] if p[0] == 'T' else p[2])]
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    return min(xs), min(ys), max(xs), max(ys)


def loop_prims(key, prims, t):
    """icon-specific hold loop (t = seconds since the icon landed)."""
    if t is None:
        return prims
    P_ = list(prims)
    lift = -5.0 * (0.5 - 0.5 * math.cos(2 * math.pi * t / 1.3))
    if key == 'sun':                                             # rays slowly rotate
        return P_[:2] + [_rot(p, 50, 50, 30 * t) for p in P_[2:]]
    if key == 'arrow_up':                                        # whole arrow climbs, then repeats
        d = 7.0 * (0.5 - 0.5 * math.cos(2 * math.pi * t / 1.4))
        return [_tr(P_[0], 0.6 * d, -d), _tr(P_[1], 0.6 * d, -d)] + P_[2:]
    if key == 'sparkle_house':                                   # sparkles twinkle, roof lifts
        out = [_tr(P_[0], 0, lift)] + P_[1:-3]
        for j, p in enumerate(P_[-3:]):
            x0, y0, x1, y1 = _bbox([p])
            out.append(_sc(p, (x0 + x1) / 2, (y0 + y1) / 2, 0.45 + 0.75 * abs(math.sin(math.pi * (t / 0.9 + j / 3.0)))))
        return out
    if key == 'people':                                          # people pop in one by one
        out = list(P_)
        for gi, grp in enumerate(([0, 1], [2, 3], [4, 5, 6])):
            u = (t - gi * 0.3) % 1.8
            s = 1 + 0.22 * math.sin(math.pi * u / 0.32) if 0 <= u < 0.32 else 1.0
            x0, y0, x1, y1 = _bbox([P_[i] for i in grp])
            for i in grp:
                out[i] = _sc(P_[i], (x0 + x1) / 2, y1, s)
        return out
    if key == 'coins':                                           # top coin drops in again and again
        u = (t % 1.4) / 0.45
        dy = -46 * (1 - ease_out(u)) if u < 1 else 0.0
        return P_[:3] + [_tr(p, 0, dy) for p in P_[3:]]
    if key in ('house', 'house_tag'):                            # roof lifts slightly
        return [_tr(P_[0], 0, lift)] + P_[1:]
    if key == 'houses':                                          # the orange house rises above the others
        return P_[:2] + [_tr(p, 0, lift * 1.4) for p in P_[2:]]
    if key.startswith('badge'):
        a = 7 * math.sin(2 * math.pi * t / 1.6)
        return [_rot(p, 50, 50, a) for p in P_]
    if key == 'garden':
        a = 4 * math.sin(2 * math.pi * t / 1.8)
        return [_rot(p, 50, 90, a) for p in P_[:2]] + P_[2:]
    return prims


# ---------------------------------------------------------------- v3 hero visuals
HERO_W0, HERO_W1 = 0.55 * W, 0.75 * W
BAND_Y1 = 0.35 * H                       # hero visuals live between 8 % (TOPMIN) and 35 % from the top
LABEL_KEY = {'DRY SEASON': 'DRY', 'WET SEASON': 'WET', 'WELL-PRESENTED': 'PRESENTED', 'MORE OFFERS': 'MORE',
             'STAND OUT': 'OUT', 'TIP 1': '1', 'TIP 2': '2', 'TIP 3': '3', 'FIRST HOME': 'FIRST',
             'OPEN HOME': 'OPEN', 'DAYS ON MARKET': 'DAYS', 'CAR SPACE': 'CAR', 'LAND SIZE': 'LAND',
             'AIR-CON': 'AIR', 'PET FRIENDLY': 'PET', 'DREAM HOME': 'DREAM', 'CALL ME': 'CALL'}
VIS_GAP, VIS_HOLD_MIN, VIS_HOLD_MAX = 1.8, 1.7, 3.0


def label_lines(c, lines):
    lab = c['label']
    key = c.get('number') or LABEL_KEY.get(lab)
    if key is None:
        parts = lab.split()
        key = parts[-1] if len(parts) > 1 else lab      # single word = the key part, Orange
    i = lab.find(key) if key else -1
    mark = [False] * len(lab)
    if i >= 0:
        for j in range(i, i + len(key)):
            mark[j] = True
    out, pos = [], 0
    for ln in lines:
        j = lab.find(ln, pos)
        runs = []
        for k, ch in enumerate(ln):
            col = ORANGE if (j >= 0 and mark[j + k]) else NAVY
            if runs and runs[-1][1] == col:
                runs[-1] = (runs[-1][0] + ch, col)
            else:
                runs.append((ch, col))
        out.append(runs)
        pos = j + len(ln) if j >= 0 else pos
    return out


def build_hero(c):
    """HERO graphic: icon 300-360 px + label 80-90 px Montserrat Black (Navy, white outline, key part Orange).
    Total width 55-75 % of the frame. Icon beside the label (1-2 lines) or on top of it."""
    lab = c['label']
    words = lab.split()
    opts = [[lab]]
    if len(words) >= 2:
        k = min(range(1, len(words)), key=lambda k: abs(len(' '.join(words[:k])) - len(' '.join(words[k:]))))
        opts.append([' '.join(words[:k]), ' '.join(words[k:])])
    best = None
    for lines in opts:                                              # icon beside the label
        for em in (86, 88, 90, 84, 82, 80):
            ol = max(5, int(round(em * 0.085)))
            lw = max(tw('blk', l, em) for l in lines) + 2 * ol
            for isz in (300, 320, 340, 360):
                w = isz + 26 + lw
                if HERO_W0 <= w <= HERO_W1:
                    sc = (abs(em - 86) + abs(isz - 320) / 10.0 + (len(lines) - 1) * 2)
                    if best is None or sc < best[0]:
                        best = (sc, 'h', lines, em, isz, w, ol)
    if best is None:                                                # icon on top of the label
        for em in (86, 84, 82, 80, 88, 90):
            ol = max(5, int(round(em * 0.085)))
            lw = tw('blk', lab, em) + 2 * ol
            for isz in (330, 300, 360):
                w = max(isz, lw)
                if HERO_W0 - 1 <= w <= HERO_W1 + 1:
                    best = (0, 'v', [lab], em, isz, w, ol)
                    break
            if best:
                break
    if best is None:                                                # last resort: fit the width
        em = 80
        ol = 7
        while tw('blk', lab, em) + 2 * ol > HERO_W1 and em > 56:
            em -= 2
        best = (0, 'v', [lab], em, 330, max(330, tw('blk', lab, em) + 2 * ol), ol)
    _, layout, lines, em, isz, w, ol = best
    sprs = [text_sprite(r, 'blk', em, shadow=(0, 7, 10, 0.45, BLACK), stroke=(ol, WHITE))
            for r in label_lines(c, lines)]
    ch = cap_h('blk', em)
    lgap = 0.24 * em
    block = len(lines) * ch + (len(lines) - 1) * lgap
    lw = max(i['text_w'] for _, i in sprs) + 2 * ol
    if layout == 'h':
        h = isz
        icon_c = (isz / 2.0, isz / 2.0)
        y = isz / 2.0 - block / 2.0
        labs = []
        for spr, inf in sprs:
            labs.append((spr, inf, isz + 26 + ol + inf['text_w'] / 2.0, y + ch / 2.0))
            y += ch + lgap
    else:
        h = isz + 16 + ch + 2 * ol
        icon_c = (w / 2.0, isz / 2.0)
        labs = [(sprs[0][0], sprs[0][1], w / 2.0, isz + 16 + ol + ch / 2.0)]
    ext = max(0.05 * isz, 24 if layout == 'v' else 0.0, 0.015 * h) + 4
    return dict(c=c, layout=layout, lines=lines, em=em, isz=isz, w=w, h=h, icon_c=icon_c, labs=labs, ol=ol,
                ch=ch, ext=ext)


# ---------------------------------------------------------------- v4 spoken visuals: in sync, in real space
VIS_HOLD_MIN, VIS_HOLD_MAX = 1.2, 3.0
VIS_MIN_W = 0.45 * W                      # a visual is never narrower than 45 % of the frame
SIDE_GAP = 26                             # px between a visual and the face (plus the slack)
EDGE = 16


def schedule_visuals(P):
    """every matched concept gets a visual that STARTS on its word (0.1 s before it). Close visuals: the first
    one's hold is shortened (min 1.2 s) or they cross-fade - a visual is never delayed."""
    if not P.opt.visuals or not P.words:
        return []
    cands = visual_candidates(P)
    if getattr(P, 'broll', None):                       # v6: B-roll wins; the icon moves to the next free time
        P.icon_moves = []                               # the same idea is said, or is dropped
        free = [c for c in cands if not broll_overlaps(P, c['t'] - 0.1, c['t'] - 0.1 + VIS_HOLD_MIN, 0.05)]
        for c in cands:
            if c in free:
                continue
            nxt = next((o for o in free if o['label'] == c['label'] and o['t'] > c['t']), None)
            P.icon_moves.append((c['label'], c['t'], nxt['t'] if nxt else None))
        cands = free
    keep = [c for c in cands
            if not any(o is not c and abs(o['t'] - c['t']) < 1.2 and o['prio'] < c['prio'] for o in cands)]
    end_lim = P.speech_end - 0.05
    fpsf = float(P.fps)
    groups, used = [], set()
    for c in keep:
        if c['label'] in used:
            continue
        t0 = max(0.0, c['t'] - 0.1)
        if t0 + VIS_HOLD_MIN > end_lim + 1e-6:
            continue
        photo = P.photos.get(c['icon']) if P.photos else None
        groups.append(dict(chips=[c], t0=t0, photo=photo, moved=t0 - c['t'], why=''))
        used.add(c['label'])
    for gi, g in enumerate(groups):
        t1 = min(g['t0'] + (2.6 if g['photo'] else VIS_HOLD_MAX), end_lim)
        t1 = min([t1] + [b['t0'] - 0.05 for b in getattr(P, 'broll', []) if b['t0'] > g['t0']])
        if gi + 1 < len(groups):
            nxt = groups[gi + 1]['t0']
            if nxt < t1:
                if nxt - g['t0'] >= VIS_HOLD_MIN:
                    t1 = nxt                                   # shorten the hold
                else:
                    t1 = nxt + 6 / fpsf                        # cross-fade into the next one
                    g['xfade'] = True
        g['t1'] = t1
    return groups


def trim_for_bigwords(P):
    for g in P.visuals:
        for b in P.bigwords:
            if g['t0'] < b['t0'] < g['t1'] and b['t0'] - g['t0'] >= VIS_HOLD_MIN:
                g['t1'] = b['t0']


def side_room(P, t0, t1):
    fs = faces_out(P, t0, t1, 1.0 / float(P.fps))
    if not fs:
        return W - 48.0, 'R', fs
    fx0, fx1 = min(f[0] for _, f in fs), max(f[2] for _, f in fs)
    right = (W - EDGE) - (fx1 + SIDE_GAP)
    left = (fx0 - SIDE_GAP) - EDGE
    return max(left, right), ('R' if right >= left else 'L'), fs


def force_wide_for_visuals(P):
    """a zoomed shot that leaves no room (>= 45 % width) beside his head becomes the wide shot for that visual
    (no moving him down, no blurred band)."""
    need = VIS_MIN_W / 0.97 + 2
    widened = []
    for g in P.visuals:
        if g.get('photo'):
            continue
        room, _, _ = side_room(P, g['t0'], g['t1'])
        if room >= need:
            continue
        new = []
        for z in P.zones:
            if z['t1'] <= g['t0'] or z['t0'] >= g['t1'] or z['z'] <= 1.0 + 1e-3:
                new.append(z)
                continue
            a, b = max(z['t0'], g['t0']), min(z['t1'], g['t1'])
            if a - z['t0'] < 0.3:
                a = z['t0']
            if z['t1'] - b < 0.3:
                b = z['t1']
            if a > z['t0']:
                new.append(dict(z, t0=z['t0'], t1=a))
            new.append(dict(z, t0=a, t1=b, z=1.0, level='WIDE'))
            if b < z['t1']:
                new.append(dict(z, t0=b, t1=z['t1']))
        P.zones = new
        refresh_crops(P)
        widened.append(g['chips'][0]['label'])
    merged = []
    for z in P.zones:
        if merged and abs(merged[-1]['z'] - z['z']) < 1e-3 and abs(merged[-1].get('shift', 0) - z.get('shift', 0)) < 1:
            merged[-1]['t1'] = z['t1']
        else:
            merged.append(z)
    P.zones = merged
    refresh_crops(P)
    return widened


def build_hero_fit(c, rw, rh):
    """biggest hero that fits rw x rh: label cap height >= 45 % of the icon, width >= 45 % of the frame."""
    lab = c['label']
    words = lab.split()
    opts = [[lab]]
    if len(words) >= 2:
        k = min(range(1, len(words)), key=lambda k: abs(len(' '.join(words[:k])) - len(' '.join(words[k:]))))
        opts.append([' '.join(words[:k]), ' '.join(words[k:])])
    elif '-' in lab:
        a, b = lab.split('-', 1)
        opts.append([a + '-', b])
    best = None
    for lines in opts:
        n = len(lines)
        for em in range(150, 44, -2):
            ol = max(5, int(round(em * 0.10)))
            lw = max(tw('blk', l, em) for l in lines) + 2 * ol
            ch = cap_h('blk', em)
            block = n * ch + (n - 1) * 0.24 * em + 2 * ol
            for layout in ('v', 'h'):
                if layout == 'v':
                    I = min(ch / 0.45, 300, rh - 14 - block)
                    w, h = max(I, lw), I + 14 + block
                else:
                    I = min(ch / 0.45, 300, rh, rw - 24 - lw)
                    w, h = I + 24 + lw, max(I, block)
                if I < 90 or w > rw or h > rh:
                    continue
                wide = w >= VIS_MIN_W - 1
                sc = (1000 if wide else 0) + ch + 0.5 * I - 3 * (n - 1) - (500 if min(len(l) for l in lines) <= 3 else 0)
                if best is None or sc > best[0]:
                    best = (sc, layout, lines, em, int(I), w, h, ol, ch)
    if best is None:
        return None
    _, layout, lines, em, I, w, h, ol, ch = best
    sprs = [text_sprite(r, 'blk', em, shadow=(0, 7, 10, 0.45, BLACK), stroke=(ol, WHITE))
            for r in label_lines(c, lines)]
    lgap = 0.24 * em
    labs = []
    if layout == 'h':
        block = len(lines) * ch + (len(lines) - 1) * lgap
        y = h / 2.0 - block / 2.0
        icon_c = (I / 2.0, h / 2.0)
        for spr, inf in sprs:
            labs.append((spr, inf, I + 24 + ol + inf['text_w'] / 2.0, y + ch / 2.0))
            y += ch + lgap
    else:
        icon_c = (w / 2.0, I / 2.0)
        y = I + 14 + ol
        for spr, inf in sprs:
            labs.append((spr, inf, w / 2.0, y + ch / 2.0))
            y += ch + lgap
    return dict(c=c, layout=layout, lines=lines, em=em, isz=I, w=w, h=h, icon_c=icon_c, labs=labs, ol=ol, ch=ch,
                ext=max(0.05 * I, 24 if layout == 'v' else 0.0, 0.015 * h) + 4)


def vis_rect(g, t, P=None):
    rs = g.get('rects', [])
    for i, (a, b, r) in enumerate(rs):
        if a - 1e-6 <= t < b:
            if i and P is not None and abs(a - P.hook_t1) < 1e-3:
                he = _hook_ease(P, t)
                if he is not None and he[1] < 1:
                    r0, w = rs[i - 1][2], he[1]
                    return tuple(r0[j] * (1 - w) + r[j] * w for j in range(4))
            return r
    return g['rect']


def _regions(P, t0, t1, top):
    fs = faces_out(P, t0, t1, 1.0 / float(P.fps))
    if not fs:
        return {'upper area': (EDGE, top, W - EDGE, 0.35 * H)}
    fx0, fx1 = min(f[0] for _, f in fs), max(f[2] for _, f in fs)
    chin = max(f[3] for _, f in fs)
    htop = min(head_top(f) for _, f in fs)
    bot = min(chin + 10, CAP_MIN_Y - 40)
    return {'beside his head (right)': (fx1 + SIDE_GAP, top, W - EDGE, bot),
            'beside his head (left)': (EDGE, top, fx0 - SIDE_GAP, bot),
            'above his head': (EDGE, top, W - EDGE, htop - HEAD_GAP)}


def place_visuals(P):
    """fit each hero into the REAL free space beside his head (or above it if there is room) - framing untouched.
    If the framing cuts while a visual is up (end of the hook), the visual jumps with the cut."""
    hook_r = None
    if P.hook_on and P.hb:
        hook_r = P.hb['rect']
    elif P.hook_on and P.hookbox:
        hook_r = P.hookbox['rect']
    out = []
    for g in P.visuals:
        if g.get('photo'):
            out.append(g)
            continue
        c = g['chips'][0]
        cuts = [g['t0']]
        prev = None
        for z in P.zones:
            if g['t0'] < z['t0'] < g['t1'] and prev is not None and abs(z.get('shift', 0) - prev.get('shift', 0)) > 0.5:
                cuts.append(z['t0'])
            prev = z
        cuts.append(g['t1'])
        segs = []
        for a, b in zip(cuts[:-1], cuts[1:]):
            top = TOPMIN
            if hook_r is not None and a < P.hook_t1:
                top = max(top, hook_r[3] + 44)
            a_m = a + (HOOK_EASE / float(P.fps) if abs(a - P.hook_t1) < 1e-3 and P.hook_on else 0.0)
            segs.append((a, b, _regions(P, min(a_m, b - 0.04), b, top)))
        best = None
        for name in segs[0][2]:
            rs = [sg[2][name] for sg in segs]
            rw = min(r[2] - r[0] for r in rs)
            rh = min(r[3] - r[1] for r in rs)
            if rw < 200 or rh < 120:
                continue
            hr = build_hero_fit(c, rw * 0.97, rh - 30)
            if hr is None:
                continue
            sc = (1000 if hr['w'] >= VIS_MIN_W - 1 else 0) + hr['ch'] + 0.5 * hr['isz']
            if best is None or sc > best[0]:
                best = (sc, name, hr, rs)
        if best is None:
            log('    (visual "%s" dropped: no free space next to his head)' % c['label'])
            continue
        _, name, hr, rs = best
        g['hero'], g['w'], g['h'], g['ext'], g['mode'] = hr, hr['w'], hr['h'], hr['ext'], name
        rects = []
        for (a, b, _), (x0, y0, x1, y1) in zip(segs, rs):
            if 'right' in name:
                rx = x1 - 0.015 * hr['w'] - hr['w']                # outer edge: the slack stays next to his face
            elif 'left' in name:
                rx = x0 + 0.015 * hr['w']
            else:
                rx = (x0 + x1) / 2.0 - hr['w'] / 2.0
            cy = (y0 + y1) / 2.0 - 6
            rects.append((a, b, (rx, cy - hr['h'] / 2.0, rx + hr['w'], cy + hr['h'] / 2.0)))
        g['rects'] = rects
        g['rect'] = rects[0][2]
        out.append(g)
    P.visuals = out


def layout_group(P, g):
    if not g.get('photo'):                       # heroes are sized later by place_visuals()
        g['w'], g['h'], g['ext'], g['rect'] = 0, 0, 0, (0, 0, 0, 0)
        return g
    if g.get('photo'):
        cw, chh = int(0.87 * W), int(0.45 * H - TOPMIN)
        g['w'], g['h'], g['ext'] = cw, chh, 4
        g['rect'] = (W / 2 - cw / 2, TOPMIN, W / 2 + cw / 2, TOPMIN + chh)
        return g
    hr = build_hero(g['chips'][0])
    g['hero'] = hr
    g['w'], g['h'], g['ext'] = hr['w'], hr['h'], hr['ext']
    return g


def place_group(P, g, top, cx=None):
    g['top'] = top
    cx = W / 2 if cx is None else cx
    g['rect'] = (cx - g['w'] / 2, top, cx + g['w'] / 2, top + g['h'])


def draw_visuals(P, fr, t, bl, stats):
    fpsf = float(P.fps)
    for g in P.visuals:
        if not (g['t0'] <= t < g['t1']):
            continue
        fo = (g['t1'] - t) * fpsf
        if g.get('photo'):
            draw_photo(P, fr, t, g, bl, clamp(fo / 4.0, 0, 1))
            continue
        hr = g['hero']
        c = hr['c']
        f = (t - g['t0']) * fpsf
        out_a = clamp(fo / 6.0, 0, 1)                                    # OUT: 90 % + fade over 6 frames
        out_s = 0.90 + 0.10 * out_a
        tl = t - g['t0'] - DRAW_F / fpsf
        br = 1 + 0.015 * (1 - math.cos(2 * math.pi * tl / 1.6)) if tl > 0 else 1.0   # breathe 1.00<->1.03
        S_ = br * out_s
        x0, y0 = vis_rect(g, t, P)[0], vis_rect(g, t, P)[1]
        gx, gy = x0 + hr['w'] / 2.0, y0 + hr['h'] / 2.0
        prog = clamp(f / float(DRAW_F), 0, 1)                            # IN: draw-on over 8 frames
        if f < DRAW_F / 2.0:
            pop = 0.70 + 0.40 * ease_out(f / (DRAW_F / 2.0))             # pop 70 -> 110 -> 100 %
        elif f < DRAW_F:
            pop = 1.10 - 0.10 * ease_io((f - DRAW_F / 2.0) / (DRAW_F / 2.0))
        else:
            pop = 1.0
        lt = (t - g['t0'] - DRAW_F / fpsf) if f >= DRAW_F else None
        ic = pil_to_pm(render_icon(c['icon'], hr['isz'], prog, lt))
        icx, icy = x0 + hr['icon_c'][0], y0 + hr['icon_c'][1]
        sx, sy = gx + (icx - gx) * S_, gy + (icy - gy) * S_
        boxes = [bl.blit_scaled(fr, ic, sx, sy, pop * S_, clamp(f / 3.0, 0, 1) * out_a, 'visual')]
        iz = hr['isz'] / 2.0 * pop * S_
        drawn = [(sx - iz, sy - iz, sx + iz, sy + iz)]
        fl = f
        if fl >= 0:                                                      # label comes in WITH the icon (5 frames)
            a = ease_out((fl + 1) / float(LABEL_F + 1))
            dy = 24 * (1 - a)
            for spr, inf, lcx, lcy in hr['labs']:
                h_, w_ = spr.shape[:2]
                ox = w_ / 2.0 - inf['cap_x0'] - inf['text_w'] / 2.0
                oy = h_ / 2.0 - inf['cap_y0'] - inf['cap_h'] / 2.0
                px, py = gx + (x0 + lcx - gx) * S_, gy + (y0 + lcy + dy - gy) * S_
                bl.blit_scaled(fr, spr, px + ox * S_, py + oy * S_, S_, a * out_a, 'visual')
                hw, hh = (inf['text_w'] / 2.0 + hr['ol']) * S_, (inf['cap_h'] / 2.0 + hr['ol']) * S_
                drawn.append((px - hw, py - hh, px + hw, py + hh))
        u = (min(r[0] for r in drawn), min(r[1] for r in drawn), max(r[2] for r in drawn), max(r[3] for r in drawn))
        stats['vis_rects'].append((t, u, P.visuals.index(g)))
        del boxes


def top_elements(P):
    """(kind, t0, t1, bottom, margin) - head top must stay at least margin below 'bottom'. v4: hook only -
    spoken visuals never move him down."""
    els = []
    if P.hook_on and P.hb:
        els.append(('hookb', P.hook_t0, P.hook_t1, P.hb['want_head'], 0))
    elif P.hook_on and P.hookbox:
        els.append(('hook', P.hook_t0, P.hook_t1, P.hookbox['rect'][3], 24))
    return els


def solve_headroom(P):
    if P.hook_on and not split_zones(P, P.hook_t1):
        for k, z in enumerate(P.zones):                   # plain split: headroom must end with the hook
            if z['t0'] + 0.05 < P.hook_t1 < z['t1'] - 0.05:
                P.zones.insert(k + 1, dict(z, t0=P.hook_t1))
                z['t1'] = P.hook_t1
                break
    for z in P.zones:
        z['shift'] = 0.0
    refresh_crops(P)
    for g in P.visuals:
        if g.get('photo'):
            place_group(P, g, TOPMIN)
    dropped = []
    for it in range(4):
        changed = False
        for z in P.zones:
            need = 0.0
            for kind, t0, t1, bottom, margin in top_elements(P):
                a, b = max(t0, z['t0']), min(t1, z['t1'])
                if b <= a:
                    continue
                saved = z['shift']
                z['shift'] = 0.0
                zone_crop(P, z)
                fs = faces_out(P, a, b, 0.08)
                z['shift'] = saved
                zone_crop(P, z)
                if not fs:
                    continue
                top = min(head_top(f) for _, f in fs)
                need = max(need, bottom + margin - top)
            ns = float(math.ceil(max(0.0, need) / 4.0) * 4)
            if abs(ns - z['shift']) > 0.5:
                z['shift'] = ns
                zone_crop(P, z)
                changed = True
        for z in [z for z in P.zones if z['shift'] > MAX_SHIFT]:
            if z['z'] > 1.0:                               # try the wide shot first
                z['z'], z['level'] = 1.0, 'WIDE'
                z['shift'] = 0.0
                zone_crop(P, z)
                changed = True
                continue
        if not changed:
            break
    for z in P.zones:
        z['shift'] = min(z['shift'], MAX_SHIFT)
        zone_crop(P, z)
    merged = []
    for z in P.zones:
        if merged and abs(merged[-1]['z'] - z['z']) < 1e-3 and abs(merged[-1]['shift'] - z['shift']) < 1:
            merged[-1]['t1'] = z['t1']
        else:
            merged.append(z)
    P.zones = merged
    for z in P.zones:
        mid0, mid1 = P.tl.o2s(z['t0']), P.tl.o2s(max(z['t0'], z['t1'] - 1e-3))
        fs = P.track.span(mid0, mid1)
        z['face'] = (tuple(np.median([[f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h']] for f in fs], axis=0))
                     if fs else None)
        zone_crop(P, z)
    return dropped


# ---- captions
def cap_word(w):
    return re.sub(r"[,.;:]+$", '', w)


def phrases_of(P):
    """split each sentence into ONE-line phrases of 2-4 words (DP: best partition that fits the width)."""
    out = []
    em = P.cap_em
    maxw = CAP_MAXW - 2 * 26
    for s in P.sents:
        ws = list(s)
        n = len(ws)
        best = [0.0] + [1e18] * n
        back = [0] * (n + 1)
        for j in range(1, n + 1):
            for size in range(1, 5):
                i = j - size
                if i < 0:
                    break
                g = ws[i:j]
                txt = ' '.join(cap_word(P.words[q]['w']) for q in g)
                if size > 1 and tw('blk', txt, em) > maxw:
                    continue
                gaps = [P.words[b]['so'] - P.words[a]['eo'] for a, b in zip(g[:-1], g[1:])]
                cost = {1: 8.0, 2: 1.2, 3: 0.0, 4: 0.6}[size] + (5.0 if gaps and max(gaps) > 0.6 else 0.0)
                if best[i] + cost < best[j]:
                    best[j], back[j] = best[i] + cost, i
        groups, j = [], n
        while j > 0:
            groups.insert(0, ws[back[j]:j])
            j = back[j]
        out += groups
    return out


def layout_captions(P):
    caps = []
    groups = phrases_of(P)
    for gi, g in enumerate(groups):
        t0 = P.words[g[0]]['so']
        nxt = P.words[groups[gi + 1][0]]['so'] if gi + 1 < len(groups) else None
        t1 = P.words[g[-1]]['eo'] + 0.25
        if nxt is not None:
            t1 = nxt if nxt - P.words[g[-1]]['eo'] < 0.6 else min(t1, nxt)
        t1 = min(t1, P.tl.dur - 1.0 / float(P.fps))
        txts = [cap_word(P.words[q]['w']) for q in g]
        full = ' '.join(txts)
        em = P.cap_em
        kg = KC_GAP * (len(txts) - 1) if (P.opt.kinetic_captions and P.opt.big_captions) else 0.0
        while tw('blk', full, em) + kg * em > CAP_MAXW - 52 and em > 56:
            em -= 2
        caps.append(dict(words=g, txts=txts, text=full, t0=t0, t1=t1, em=em, w=tw('blk', full, em) + kg * em))
    for c in caps:
        place_caption(P, c)
    return caps


def place_caption(P, c, extra_drop=0.0):
    em = c['em']
    fsx = faces_out(P, c['t0'], c['t1'], 0.04)
    fb = max([f[3] for _, f in fsx], default=0.0)
    ch = cap_h('blk', em)
    pad_y, pad_x = 16, 26
    hbox = ch + 0.22 * em + 2 * pad_y
    top = max(fb + 40 + extra_drop + 0.025 * hbox, CAP_MIN_Y)
    if broll_overlaps(P, c['t0'], c['t1']):              # v6: lowest line during B-roll, the bubble sits above it
        top = CAP_MAX_Y
    if top + hbox > CAP_MAX_Y - 0.025 * hbox:
        top = CAP_MAX_Y - 0.025 * hbox - hbox
    box = (CAP_CX - c['w'] / 2 - pad_x, top, CAP_CX + c['w'] / 2 + pad_x, top + hbox)
    c.update(cx=CAP_CX, cy=top + hbox / 2, box_rect=box, face_bottom=fb, faces=fsx, pad=(pad_x, pad_y))


def caption_sprite(P, c, j):
    key = (id(c), j, c.get('boxed', False))
    if key in P.capcache:
        return P.capcache[key]
    runs = []
    for k, t in enumerate(c['txts']):
        runs.append((t + (' ' if k + 1 < len(c['txts']) else ''), ORANGE if k == j else WHITE))
    box = (NAVY, 0.70, c['pad'][0], c['pad'][1], 14) if c.get('boxed') else None
    spr = text_sprite(runs, 'blk', c['em'], shadow=(0, 5, 9, 0.62, BLACK), box=box)
    P.capcache[key] = spr
    return spr


# ------------------------------------------------------------------ self-check (planning)
def self_check(P):
    res = []

    def chk(ok, msg):
        res.append((ok, msg))

    for i, c in enumerate(P.caps):
        br = c['box_rect']
        sc = 1.05                                                # pop overshoot
        cx, cy = (br[0] + br[2]) / 2, (br[1] + br[3]) / 2
        brs = (cx - (cx - br[0]) * sc, cy - (cy - br[1]) * sc, cx + (br[2] - cx) * sc, cy + (br[3] - cy) * sc)
        hit = [f for _, f in c['faces'] if rect_hit(brs, f)]
        chk(not hit, 'caption %02d "%s"  y %d-%d  face bottom %d  -> %s' % (
            i + 1, c['text'], brs[1], brs[3], c['face_bottom'], 'clear of face' if not hit else 'OVERLAPS FACE'))
        chk(brs[3] <= CAP_MAX_Y + 0.5, 'caption %02d bottom %d <= 75%% (%d)' % (i + 1, brs[3], CAP_MAX_Y))
        chk(br[0] >= CAP_X0 - 0.5 and br[2] <= CAP_X1 + 0.5,
            'caption %02d x %d-%d inside 6%%-82%% (%d-%d)' % (i + 1, br[0], br[2], CAP_X0, CAP_X1))
    for gi, g in enumerate(P.visuals):
        c = g['chips'][0]
        names = c['label']
        d = g['t0'] - c['t']
        chk(abs(d) <= 0.2 + 1e-6, 'visual "%s" starts %.2fs, "%s" said %.2fs (%+.2fs, within +-0.2 s)'
            % (names, g['t0'], c['word'], c['t'], d))
        g['readable'] = g['t0'] + LABEL_F / float(P.fps)
        chk(g['readable'] - c['t'] <= 0.2 + 1e-6, 'visual "%s" label fully readable at %.2fs (%+.2fs after the word, <= 0.2 s)'
            % (names, g['readable'], g['readable'] - c['t']))
        hold = g['t1'] - g['t0']
        chk(hold >= VIS_HOLD_MIN - 1e-6 or g.get('xfade'), 'visual "%s" holds %.2fs (>= 1.2 s%s)'
            % (names, hold, ', cross-fades into the next' if g.get('xfade') else ''))
        if g.get('photo'):
            fs = faces_out(P, g['t0'], g['t1'], 1.0 / float(P.fps))
            gap = min([head_top(f) for _, f in fs], default=1e9) - g['rect'][3]
            chk(gap >= 20, 'photo "%s" %dpx above the top of the head' % (names, gap if gap < 1e8 else -1))
            continue
        hr = g['hero']
        chk(hr['ch'] >= 0.45 * hr['isz'] - 0.5 and hr['w'] >= VIS_MIN_W - 1,
            'visual "%s" %s: icon %dpx, label %dpx Montserrat Black, cap %dpx = %d%% of the icon (>= 45%%), '
            'width %d%% of the frame (>= 45%%)' % (names, g.get('mode', ''), hr['isz'], hr['em'], hr['ch'],
                                                 round(100 * hr['ch'] / hr['isz']), round(100 * hr['w'] / W)))
    for b in P.bigwords:
        dup = [g['chips'][0]['label'] for g in P.visuals
               if set(range(b['k0'], b['k1'] + 1)) & set(range(g['chips'][0]['k0'], g['chips'][0]['k1'] + 1))]
        chk(not dup, 'big word "%s" is not also an icon%s' % (b['text'], (' (duplicate of %s)' % dup) if dup else ''))
    for b in P.bigwords:
        fs = faces_out(P, b['t0'], b['t1'], 1.0 / float(P.fps))
        hit = [f for _, f in fs if rect_hit(b['rect'], f)]
        chk(not hit, 'big word "%s" %.1f-%.1fs  y %d-%d  -> %s' % (b['text'], b['t0'], b['t1'], b['rect'][1],
                                                                   b['rect'][3], 'clear of face' if not hit else 'ON FACE'))
    if P.hook_on and P.hookbox and not P.hb:
        fs = faces_out(P, P.hook_t0, P.hook_t1)
        gap = min([f[1] for _, f in fs], default=1e9) - P.hookbox['rect'][3]
        chk(gap >= 0, 'hook box "%s" %d-%dpx, %dpx above the face' % (
            P.hookbox['text'], P.hookbox['rect'][1], P.hookbox['rect'][3], gap if gap < 1e8 else -1))
    return res


# ------------------------------------------------------------------ 9. look
def make_grade(cinematic=False):
    x = np.arange(256) / 255.0
    if cinematic:                                       # v7 cinematic look
        s = x + 0.30 * (x * x * (3 - 2 * x) - x)        # gentle S-curve
        k = 0.78                                        # highlight roll-off: soft shoulder above 78 %
        hi = s > k
        s = np.where(hi, k + (1 - k) * np.tanh((s - k) / (1 - k) * 1.25) / np.tanh(1.25), s)
        ws = np.clip(1 - s / 0.45, 0, 1) ** 1.4         # shadows weight -> cooler
        wh = np.clip((s - 0.30) / 0.55, 0, 1) * np.clip((1.02 - s) / 0.25, 0, 1)   # mids / skin -> warmer
        r = np.clip(s + 0.040 * wh - 0.018 * ws, 0, 1)
        g = np.clip(s + 0.010 * wh - 0.002 * ws, 0, 1)
        b = np.clip(s - 0.036 * wh + 0.030 * ws, 0, 1)
    else:
        con = np.clip(x - 0.035 * np.sin(2 * np.pi * x), 0, 1)
        b = np.clip(con * 0.965, 0, 1)
        g = np.clip(con * 1.005, 0, 1)
        r = np.clip(con * 1.035 + 0.004, 0, 1)
    lut = np.stack([b, g, r], -1).reshape(1, 256, 3)
    lut = (lut * 255 + 0.5).astype(np.uint8)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rr = np.sqrt(((xx / W) * 2 - 1) ** 2 + ((yy / H) * 2 - 1) ** 2) / math.sqrt(2)
    vig = 1.0 - 0.15 * np.clip((rr - 0.30) / 0.70, 0, 1) ** 1.5
    return lut, vig[..., None].astype(np.float32)


def grade(img, lut, vig):
    img = cv2.LUT(img, lut)
    f = img.astype(np.float32)
    gray = f[..., 0:1] * 0.114 + f[..., 1:2] * 0.587 + f[..., 2:3] * 0.299
    f = gray + 0.95 * (f - gray)
    f *= vig
    return np.clip(f, 0, 255).astype(np.uint8)


def make_grain(n=6, seed=5):
    """1.5 % fine luminance grain (sigma = 1.5 % of full scale), a few pre-made plates."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        g = rng.standard_normal((H, W)).astype(np.float32)
        g = cv2.GaussianBlur(g, (0, 0), 0.6)
        g *= (GRAIN * 255.0) / (g.std() + 1e-6)
        out.append(g[..., None].astype(np.int16))
    return out


def add_grain(P, img, fi):
    if not getattr(P, 'grain', None):
        return img
    g = P.grain[(fi * 7 + 3) % len(P.grain)]
    return np.clip(img.astype(np.int16) + g, 0, 255).astype(np.uint8)


def zoom_blur(img, cx, cy, r, n=5):
    """radial / zoom motion blur: average of n copies scaled 1 .. r about (cx, cy)."""
    if abs(r - 1) < 1e-3:
        return img
    acc = img.astype(np.float32)
    for k in range(1, n):
        s = 1 + (r - 1) * k / (n - 1.0)
        M = np.array([[s, 0, cx * (1 - s)], [0, s, cy * (1 - s)]], np.float32)
        acc += cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
    return (acc / n).astype(np.uint8)


# ------------------------------------------------------------------ v7 transitions, impact, pace
def cta_start(P):
    for s in P.sents:
        if CTA_RE.search(' '.join(P.words[k]['w'] for k in s)):
            return P.words[s[0]]['so'] - 0.1
    return P.speech_end


def plan_transitions(P):
    """every B-roll in / out + about every 2nd-3rd other cut; never in the hook, the call to action or the end card;
    never two of the same type in a row."""
    P.transitions = []
    if not P.opt.transitions or not P.words:
        return []
    fpsf = float(P.fps)
    lo = (P.hook_t1 + HOOK_EASE / fpsf + 0.15) if P.hook_on else 1.6
    cta0 = min(cta_start(P), P.speech_end)
    items = []
    for b in P.broll:
        items.append((b['t0'], 'B-roll in "%s"' % b['word'], True))
        items.append((b['t1'], 'B-roll out', True))
    for zp, z in zip(P.zones[:-1], P.zones[1:]):
        t = z['t0']
        if broll_at(P, t - 0.02) or broll_at(P, t + 0.02) or any(abs(t - i[0]) < 0.35 for i in items if i[2]):
            continue
        if abs(zp['z'] - z['z']) < 1e-3:
            continue
        items.append((t, 'cut %d%% -> %d%%' % (round(zp['z'] * 100), round(z['z'] * 100)), False))
    items.sort()
    pattern, pi, count, last = (2, 3), 0, 0, -9.0
    for t, why, forced in items:
        if t < lo:
            continue
        typ = TR_ORDER[len(P.transitions) % len(TR_ORDER)]
        D = TR_FRAMES[typ]
        if t + D / 2.0 / fpsf > cta0 + 0.12 or t > P.speech_end - 0.3:
            continue
        count += 1
        prevD = P.transitions[-1]['D'] if P.transitions else 0
        if (t - last) * fpsf < (prevD + D) / 2.0 + 2:
            continue
        if forced or count >= pattern[pi]:
            P.transitions.append(dict(t=t, f=int(math.ceil(t * fpsf - 1e-6)), type=typ, D=D, why=why,
                                      dir=1 if len(P.transitions) % 2 == 0 else -1))
            if not forced:
                pi ^= 1
            count, last = 0, t
    return P.transitions


_LEAK = {}


def leak_layer(p):
    """warm light-leak band at sweep position p (0..1): (H, W, 3) BGR float 0..1 alpha-like intensity."""
    key = round(p, 3)
    if key in _LEAK:
        return _LEAK[key]
    sw, sh = W // 4, H // 4
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    xc = (-0.30 + 1.60 * p) * sw - 0.35 * (yy - sh / 2.0)
    band = np.exp(-0.5 * ((xx - xc) / (0.20 * sw)) ** 2)
    glow = np.exp(-0.5 * ((xx - xc) / (0.55 * sw)) ** 2) * 0.35
    a = np.clip(band + glow, 0, 1)
    col = np.array([150, 205, 255], np.float32) / 255.0             # warm peach (BGR)
    lay = cv2.resize(a, (W, H), interpolation=cv2.INTER_LINEAR)[..., None] * col
    _LEAK[key] = lay.astype(np.float32)
    return _LEAK[key]


def apply_transition(P, img, fi, stats=None):
    for tr in getattr(P, 'transitions', []):
        h = tr['D'] // 2
        d = fi - tr['f']
        if not (-h <= d < h):
            continue
        e = (h + d + 1) / float(h) if d < 0 else (h - d) / float(h)   # 1/h .. 1 .. 1/h, peak on both cut frames
        e = e ** 1.3
        if stats is not None:
            stats.setdefault('tr_frames', []).append((fi, tr['type'], round(e, 2)))
        if tr['type'] == 'zoom':
            s = 1 + 0.16 * e
            cx, cy = W / 2.0, H * 0.42
            M = np.array([[s, 0, cx * (1 - s)], [0, s, cy * (1 - s)]], np.float32)
            img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
            img = zoom_blur(img, cx, cy, 1 + 0.11 * e, 6)
        elif tr['type'] == 'whip':
            sgn = tr['dir'] * (-1 if d < 0 else 1)                       # out: slides away, in: arrives
            dx = sgn * 0.32 * W * e * e
            M = np.array([[1, 0, dx], [0, 1, 0]], np.float32)
            img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
            L = int(9 + 190 * e)
            img = cv2.blur(img, (L, 1))
        else:                                                           # light-leak sweep over 8 frames
            p = (d + h + 0.5) / float(2 * h)
            lay = leak_layer(p) * (0.92 * e)
            f = img.astype(np.float32) / 255.0
            f = 1 - (1 - f) * (1 - lay)                                 # screen blend
            f = f * (1 + 0.10 * e)
            img = np.clip(f * 255, 0, 255).astype(np.uint8)
    return img


def plan_impacts(P):
    """camera shake + soft hit on the big word(s) and on the key line (never in the call to action)."""
    P.impacts = []
    if not P.opt.impact or not P.words:
        return []
    fpsf = float(P.fps)
    cta0 = min(cta_start(P), P.speech_end)
    lo = P.hook_t1 + 0.2 if P.hook_on else 0.5
    cands = [(b['t0'] + 0.05, 'big word "%s"' % b['text']) for b in P.bigwords]
    key = next((z for z in P.zones if z['level'] == 'KEY'), None)
    if key is not None and P.key_sent is not None:
        w0 = P.words[P.sents[P.key_sent][0]]
        cands.append((max(key['t0'], w0['so'] - 0.03), 'key line "%s ..."' % ' '.join(
            P.words[k]['w'] for k in P.sents[P.key_sent][:4])))
    for t, why in sorted(cands):
        if t < lo or t >= cta0 or broll_at(P, t) or any(abs(t - o['t']) < 0.6 for o in P.impacts):
            continue
        P.impacts.append(dict(t=t, f=int(round(t * fpsf)), why=why))
    return P.impacts


def shake_offset(P, fi):
    dx = dy = 0.0
    for im in getattr(P, 'impacts', []):
        k = fi - im['f']
        if 0 <= k < SHAKE_F:
            d = (1 - k / float(SHAKE_F)) ** 1.5
            ang = 1.1 + 2.4 * k
            dx += SHAKE_PX * d * math.cos(ang)
            dy += SHAKE_PX * d * math.sin(ang)
    m = math.hypot(dx, dy)
    if m > SHAKE_PX:
        dx, dy = dx * SHAKE_PX / m, dy * SHAKE_PX / m
    return dx, dy


def apply_shake(P, img, fi, stats=None):
    dx, dy = shake_offset(P, fi)
    if abs(dx) < 0.05 and abs(dy) < 0.05:
        return img
    if stats is not None:
        stats.setdefault('shake', []).append((fi, round(math.hypot(dx, dy), 2)))
    M = np.array([[1, 0, dx], [0, 1, dy]], np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)


def pace_events(P, final=False):
    ev = [(0.0, 'hook')] + ([(P.hook_t1, 'hook out + reframe')] if getattr(P, 'hook_on', False) else [])
    ev += [(z['t0'], 'cut') for zp, z in zip(P.zones[:-1], P.zones[1:]) if abs(zp['z'] - z['z']) > 1e-3]
    for b in getattr(P, 'broll', []):
        ev += [(b['t0'], 'B-roll in'), (b['t1'], 'B-roll out')]
    ev += [(g['t0'], 'visual') for g in getattr(P, 'visuals', [])]
    ev += [(b['t0'], 'big word') for b in getattr(P, 'bigwords', [])]
    if final:
        ev += [(tr['t'], 'transition') for tr in getattr(P, 'transitions', [])]
        ev += [(im['t'], 'impact') for im in getattr(P, 'impacts', [])]
    return sorted(ev)


def pace_gaps(P, final=False):
    end = min(cta_start(P), P.speech_end)
    ts = sorted(set([round(t, 3) for t, _ in pace_events(P, final) if 0 <= t <= end] + [0.0, round(end, 3)]))
    return [(round(b - a, 2), a, b) for a, b in zip(ts[:-1], ts[1:])], end


def plan_pace(P):
    """fill every stretch > 2.5 s without a change with a punch-in cut (alternate framing) at a word start.
    Never in the hook, a B-roll, a spoken visual, a big word or the call to action."""
    P.pace_added = []
    if not P.opt.pace or not P.words or P.ctype == 'WALKTHROUGH':
        return []
    lv = LEVELS[P.ctype]
    fpsf = float(P.fps)
    hook_end = (P.hook_t1 + HOOK_EASE / fpsf + 0.2) if P.hook_on else 1.6
    busy = [(g['t0'] - 0.15, g['t1'] + 0.15) for g in P.visuals] + \
           [(b['t0'] - 0.15, b['t1'] + 0.15) for b in P.bigwords] + \
           [(b['t0'] - 0.3, b['t1'] + 0.3) for b in P.broll]
    for _ in range(40):
        gaps, end = pace_gaps(P)
        gaps = [g for g in gaps if g[0] > PACE_MAX + 1e-6]
        if not gaps:
            break
        done = False
        for g, a, b in sorted(gaps, reverse=True):
            n = int(math.ceil(g / 2.0))
            target = a + g / n
            opts = [w['so'] - 0.03 for w in P.words
                    if a + 0.9 < w['so'] - 0.03 < b - 0.9 and w['so'] > hook_end
                    and not any(x0 <= w['so'] <= x1 for x0, x1 in busy)]
            for c in sorted(opts, key=lambda c: abs(c - target)):
                k = next((i for i, z in enumerate(P.zones) if z['t0'] < c < z['t1']), None)
                if k is None:
                    continue
                z = P.zones[k]
                nxt = P.zones[k + 1]['z'] if k + 1 < len(P.zones) else None
                choice = [(nm, lv[nm]) for nm in ('TIGHT', 'WIDE', 'FIRST')
                          if abs(lv[nm] - z['z']) > 0.03 and (nxt is None or abs(lv[nm] - nxt) > 0.03)]
                if not choice:
                    continue
                nm, zz = choice[0]
                nz = dict(z, t0=c, level='PACE' if nm == 'FIRST' else nm, z=zz)
                z['t1'] = c
                P.zones.insert(k + 1, nz)
                P.pace_added.append((round(c, 2), round(zz * 100)))
                done = True
                break
            if done:
                break
        if not done:
            break
    refresh_crops(P)
    return P.pace_added


def warp(frame, M):
    out = cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT_101)
    band = int(math.ceil(M[1, 2])) if M[1, 2] > 0.5 else 0
    if band > 0:                         # synthetic headroom: soft, darkened reflection
        e = min(H, band + 24)
        top = cv2.GaussianBlur(out[:e], (0, 0), 22)
        top = (top.astype(np.float32) * 0.85)
        a = np.ones((e, 1, 1), np.float32)
        a[band:] = np.linspace(1, 0, e - band)[:, None, None]
        out[:e] = (top * a + out[:e].astype(np.float32) * (1 - a)).astype(np.uint8)
    return out


# ------------------------------------------------------------------ 10. end card (animated)
def best_headshot(P, upright):
    best, bs = None, -1
    for s in P.samples:
        f = s['face']
        if not f or not f.get('lm'):
            continue
        (rx, ry), (lx, ly), (nx, _) = f["lm"][0], f["lm"][1], f["lm"][2]
        d = math.hypot(lx - rx, ly - ry) + 1e-3
        frontal = max(0.0, 1 - abs(nx - (rx + lx) / 2) / d * 2.5) * max(0.0, 1 - abs(ly - ry) / d * 3)
        score = f['score'] * frontal * math.sqrt(s['sharp'] + 1) * math.sqrt(f['h'])
        if score > bs:
            best, bs = s, score
    if best is None:
        cand = [s for s in P.samples if s['face']]
        if not cand:
            return None
        best = max(cand, key=lambda s: s['face']['h'])
    fr = grab(upright, best['t'])
    f = best['face']
    cx, cy = f['x'] + f['w'] / 2, f['y'] + f['h'] * 0.48
    side = max(f['w'], f['h']) * 1.75
    x0, y0 = int(clamp(cx - side / 2, 0, W - side)), int(clamp(cy - side / 2, 0, H - side))
    crop = fr[y0:y0 + int(side), x0:x0 + int(side)]
    lut, vig = P.grade
    crop = cv2.LUT(crop, lut)
    return Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)), best['t']


def _layer(draw_fn):
    S = 2
    lay = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
    draw_fn(lay, ImageDraw.Draw(lay), S)
    lay = lay.resize((W, H), Image.LANCZOS)
    bb = lay.getbbox()
    if not bb:
        return None, 0, 0
    crop = lay.crop(bb)
    return pil_to_pm(crop), bb[0], bb[1]


def make_end_card(P, last_frame, headshot):
    """v1 end card content, split into layers for the animation. Returns (bg, layers, rects)."""
    base = cv2.GaussianBlur(last_frame, (0, 0), 28)
    base = (base.astype(np.float32) * 0.60).astype(np.uint8)
    fxb, fblk = FONTS['xb'], FONTS['blk']
    rects, layers = {}, {}
    bar_cy, bar_h, bar_x0, bar_x1 = int(0.615 * H), 128, 70, W - 70
    circ_d, ring = 236, 6
    cx = W // 2
    R = circ_d // 2

    def shadow_text(d, xy, text, fnt, fill, sh):
        d.text((xy[0] + sh[0], xy[1] + sh[1]), text, font=fnt, fill=sh[2], anchor='mm')
        d.text(xy, text, font=fnt, fill=fill, anchor='mm')

    def fit(txt, a, b, S):
        em = 52
        while em > 26:
            fnt = ImageFont.truetype(fxb, em * S)
            if fnt.getlength(txt) / S <= (b - a):
                return fnt
            em -= 2
        return ImageFont.truetype(fxb, 26 * S)

    inner_l = (bar_x0 + 22, cx - circ_d // 2 - ring - 14)
    inner_r = (cx + circ_d // 2 + ring + 14, bar_x1 - 22)

    def blue(lay, d, S):
        d.rounded_rectangle([bar_x0 * S, (bar_cy - bar_h // 2) * S, cx * S, (bar_cy + bar_h // 2) * S], 26 * S,
                            fill=BLUE + (255,), corners=(True, False, False, True))
        shadow_text(d, (((inner_l[0] + inner_l[1]) / 2) * S, bar_cy * S), NAME, fit(NAME, *inner_l, S),
                    WHITE + (255,), (0, 2 * S, (0, 0, 0, 70)))

    def orange(lay, d, S):
        d.rounded_rectangle([cx * S, (bar_cy - bar_h // 2) * S, bar_x1 * S, (bar_cy + bar_h // 2) * S], 26 * S,
                            fill=ORANGE + (255,), corners=(False, True, True, False))
        shadow_text(d, (((inner_r[0] + inner_r[1]) / 2) * S, bar_cy * S), PHONE, fit(PHONE, *inner_r, S),
                    WHITE + (255,), (0, 2 * S, (0, 0, 0, 70)))

    def head(lay, d, S):
        d.ellipse([(cx - R - ring) * S, (bar_cy - R - ring) * S, (cx + R + ring) * S, (bar_cy + R + ring) * S],
                  fill=WHITE + (255,))
        if headshot is not None:
            hs = headshot.resize((circ_d * S, circ_d * S), Image.LANCZOS).convert('RGBA')
            m = Image.new('L', (circ_d * S, circ_d * S), 0)
            ImageDraw.Draw(m).ellipse([0, 0, circ_d * S - 1, circ_d * S - 1], fill=255)
            lay.paste(hs, ((cx - R) * S, (bar_cy - R) * S), m)
        else:
            d.ellipse([(cx - R) * S, (bar_cy - R) * S, (cx + R) * S, (bar_cy + R) * S], fill=NAVY + (255,))

    tag_cy = bar_cy - R - ring - 64

    def tagline(lay, d, S):
        ft = ImageFont.truetype(fxb, 46 * S)
        shadow_text(d, (cx * S, tag_cy * S), TAGLINE, ft, WHITE + (255,), (0, 3 * S, (0, 0, 0, 120)))

    fb = ImageFont.truetype(fblk, 74)
    bw = fb.getlength(BRAND) + 2 * 46
    bh = 112
    pill_cy = tag_cy - 52 - bh // 2 - 8

    def brand(lay, d, S):
        fbs = ImageFont.truetype(fblk, 74 * S)
        d.rounded_rectangle([(cx - bw / 2) * S, (pill_cy - bh / 2) * S, (cx + bw / 2) * S, (pill_cy + bh / 2) * S],
                            bh // 2 * S, fill=WARM + (255,))
        d.text((cx * S, (pill_cy - 4) * S), BRAND, font=fbs, fill=NAVY + (255,), anchor='mm')

    for name, fn in (('brand', brand), ('tagline', tagline), ('blue', blue), ('orange', orange), ('headshot', head)):
        layers[name] = _layer(fn)
    tw_ = ImageFont.truetype(fxb, 46).getlength(TAGLINE)
    rects['bar'] = (bar_x0, bar_cy - bar_h // 2, bar_x1, bar_cy + bar_h // 2)
    rects['headshot'] = (cx - R - ring, bar_cy - R - ring, cx + R + ring, bar_cy + R + ring)
    rects['tagline'] = (cx - tw_ / 2, tag_cy - 30, cx + tw_ / 2, tag_cy + 30)
    rects['brand'] = (cx - bw / 2, pill_cy - bh / 2, cx + bw / 2, pill_cy + bh / 2)
    return base, layers, rects


END_ANIM = [  # layer, start (s), duration (s), kind  - ease-out, no bounce
    ('brand', 0.00, 0.35, 'drop'), ('tagline', 0.15, 0.35, 'fade'), ('blue', 0.30, 0.40, 'left'),
    ('orange', 0.30, 0.40, 'right'), ('headshot', 0.45, 0.35, 'pop')]


def end_card_frame(P, u, last, bg, layers, bl, animate=True):
    a_bg = min(1.0, (u + 1.0 / float(P.fps)) / END_FADE)
    fr = bg.copy() if a_bg >= 1 else cv2.addWeighted(last, 1 - a_bg, bg, a_bg, 0)
    for name, st, du, kind in END_ANIM:
        spr, x, y = layers[name]
        if spr is None:
            continue
        a = ease_out((u - st) / du) if animate else 1.0
        if a <= 0:
            continue
        h, w = spr.shape[:2]
        if kind == 'drop':
            bl.blit(fr, spr, x, y - 140 * (1 - a), min(1.0, a * 1.6), 'end')
        elif kind == 'fade':
            bl.blit(fr, spr, x, y, a, 'end')
        elif kind == 'left':
            bl.blit(fr, spr, x - (x + w) * (1 - a), y, min(1.0, a * 2), 'end')
        elif kind == 'right':
            bl.blit(fr, spr, x + (W - x) * (1 - a), y, min(1.0, a * 2), 'end')
        elif kind == 'pop':
            bl.blit_scaled(fr, spr, x + w / 2, y + h / 2, 0.55 + 0.45 * a, min(1.0, a * 1.5), 'end')
    return fr


# ------------------------------------------------------------------ overlays per frame
def draw_progress(P, fr, t):
    if not P.opt.progress:
        return
    p = clamp(t / max(1e-3, P.card_t0), 0, 1)
    x1 = int(round(W * p))
    if x1 > 0:
        reg = fr[0:6, 0:x1].astype(np.float32)
        fr[0:6, 0:x1] = (reg * 0.0 + np.array(ORANGE[::-1], np.float32)).astype(np.uint8)


def load_photo_card(P, g):
    if 'card_img' in g:
        return
    src = cv2.imread(g['photo']['file'])
    if src is None:
        g['card_img'] = None
        return
    g['card_img'] = src
    lab = g['photo']['label'].upper()
    pe = 34
    pw = int(tw('blk', lab, pe) + 44)
    ph = int(cap_h('blk', pe) + 28)
    pimg = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pimg)
    pd.rounded_rectangle([0, 0, pw - 1, ph - 1], ph // 2, fill=ORANGE + (255,))
    pd.text((pw / 2, ph / 2 + cap_h('blk', pe) / 2), lab, font=font('blk', pe), fill=WHITE, anchor='ms')
    g['label_spr'] = pil_to_pm(pimg)
    m = Image.new('L', (g['w'], g['h']), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, g['w'] - 1, g['h'] - 1], 36, fill=255)
    g['card_mask'] = np.asarray(m, np.float32)[..., None] / 255.0
    sh = Image.new('L', (g['w'] + 80, g['h'] + 80), 0)
    ImageDraw.Draw(sh).rounded_rectangle([40, 48, 40 + g['w'], 48 + g['h']], 36, fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    sa = np.asarray(sh, np.float32)[..., None] / 255.0
    g['shadow_spr'] = np.concatenate([np.zeros(sa.shape[:2] + (3,), np.float32), sa], -1)


def draw_photo(P, fr, t, g, bl, out_a):
    load_photo_card(P, g)
    if g['card_img'] is None:
        return
    fpsf = float(P.fps)
    f = (t - g['t0']) * fpsf
    a = ease_out(f / 6.0) * out_a
    dy = -30 * (1 - ease_out(f / 6.0))
    u = (t - g['t0']) / max(0.1, g['t1'] - g['t0'])
    z = 1.0 + 0.07 * u                                                     # slow zoom
    src = g['card_img']
    sh, sw = src.shape[:2]
    ar = g['w'] / float(g['h'])
    cw, chh = (sh * ar, sh) if sw / float(sh) > ar else (sw, sw / ar)
    cw, chh = cw / z, chh / z
    x0, y0 = (sw - cw) / 2, (sh - chh) / 2
    crop = src[int(y0):int(y0 + chh), int(x0):int(x0 + cw)]
    img = cv2.resize(crop, (g['w'], g['h']), interpolation=cv2.INTER_AREA).astype(np.float32)
    lut, vig = P.grade
    m = g['card_mask']
    spr = np.concatenate([img * m, m], -1)
    x, y = g['rect'][0], g['rect'][1] + dy
    bl.blit(fr, g['shadow_spr'], x - 40, y - 40, a, 'visual')
    border = np.zeros((g['h'] + 12, g['w'] + 12, 4), np.float32)
    bm = Image.new('L', (g['w'] + 12, g['h'] + 12), 0)
    ImageDraw.Draw(bm).rounded_rectangle([0, 0, g['w'] + 11, g['h'] + 11], 42, fill=255)
    bma = np.asarray(bm, np.float32)[..., None] / 255.0
    border[..., :3] = 255 * bma
    border[..., 3:] = bma
    bl.blit(fr, border, x - 6, y - 6, a, 'visual')
    bl.blit(fr, spr, x, y, a, 'visual')
    ls = g['label_spr']
    bl.blit(fr, ls, x + 28, y + g['h'] - ls.shape[0] - 26, a, 'visual')


def draw_bigword(P, fr, t, bl):
    fpsf = float(P.fps)
    for b in P.bigwords:
        if b['t0'] <= t < b['t1']:
            f = (t - b['t0']) * fpsf
            if f < 3:
                s = 1.35 - 0.40 * ease_out(f / 3.0)
            elif f < 6:
                s = 0.95 + 0.05 * ease_io((f - 3) / 3.0)
            else:
                s = 1.0 + 0.015 * (t - b['t0'] - 6 / fpsf)
            a = clamp(f / 2.0, 0, 1) * clamp((b['t1'] - t) * fpsf / 3.0, 0, 1)
            spr, inf = b['sprite']
            h, w = spr.shape[:2]
            cy = b['cy']
            bl.blit_scaled(fr, spr, b['cx'] + (w / 2 - inf['cap_x0'] - inf['text_w'] / 2),
                           cy + (h / 2 - inf['cap_y0'] - inf['cap_h'] / 2), s, a, 'bigword')
            return True
    return False


def draw_caption(P, fr, t, bl, stats):
    fpsf = float(P.fps)
    for ci, c in enumerate(P.caps):
        if not (c['t0'] <= t < c['t1']):
            continue
        if 'boxed' not in c:                                               # bright / busy background -> Navy box
            x0, y0, x1, y1 = [int(v) for v in c['box_rect']]
            reg = fr[max(0, y0 - 10):y1 + 10, max(0, x0 - 10):x1 + 10]
            g = cv2.cvtColor(reg, cv2.COLOR_BGR2GRAY)
            c['bg_lum'] = float((g > 170).mean())
            c['bg_edges'] = float((cv2.Canny(g, 80, 160) > 0).mean())
            c['boxed'] = c['bg_lum'] > 0.12 or c['bg_edges'] > 0.07 or broll_overlaps(P, c['t0'], c['t1'])
        if P.opt.kinetic_captions and P.opt.big_captions:              # v7 word-by-word pop
            draw_caption_kinetic(P, fr, t, bl, c)
            stats['cap_frames'] += 1
            return
        j = 0
        for k, q in enumerate(c['words']):
            if t >= P.words[q]['so'] - 1e-3:
                j = k
        spr, inf = caption_sprite(P, c, j)
        f = (t - c['t0']) * fpsf
        if not P.opt.big_captions:
            s = 0.9 + 0.1 * ease_out(f / 4.0)
        elif f < 3:
            s = 0.85 + 0.20 * ease_out(f / 3.0)
        elif f < 6:
            s = 1.05 - 0.05 * ease_io((f - 3) / 3.0)
        else:
            s = 1.0
        h, w = spr.shape[:2]
        ox = w / 2 - inf['cap_x0'] - inf['text_w'] / 2
        cap_mid = inf['cap_y0'] + inf['cap_h'] / 2
        cym = c['cy'] - 0.08 * c['em']
        bl.blit_scaled(fr, spr, c['cx'] + ox * s, cym + (h / 2 - cap_mid) * s, s, 1.0, 'caption')
        stats['cap_frames'] += 1
        return


def kc_assets(P, c):
    boxed = bool(c.get('boxed'))
    if c.get('kc') and c['kc'][0] == boxed:
        return c['kc'][1]
    em = c['em']
    f = font('blk', em)
    words = []
    for k, tx in enumerate(c['txts']):
        xl = f.getlength(' '.join(c['txts'][:k]) + (' ' if k else '')) + k * KC_GAP * em
        words.append(dict(xl=xl, w=f.getlength(tx),
                          white=text_sprite([(tx, WHITE)], 'blk', em, shadow=(0, 5, 9, 0.62, BLACK)),
                          orange=text_sprite([(tx, ORANGE)], 'blk', em, shadow=(0, 5, 9, 0.62, BLACK))))
    c['kc'] = (boxed, dict(words=words, box={} if boxed else None))
    return c['kc'][1]


def kc_box(A, c, bw):
    """Navy 70 % box of width bw (cached in 6 px steps) - it grows with the words that are already shown."""
    bw = int(math.ceil(bw / 6.0) * 6)
    if bw not in A['box']:
        em = c['em']
        bh = cap_h('blk', em) + 2 * c['pad'][1] + 0.10 * em
        img = Image.new('RGBA', (bw + 2, int(bh) + 2), (0, 0, 0, 0))
        ImageDraw.Draw(img).rounded_rectangle([0, 0, bw, bh], 14, fill=NAVY + (int(255 * 0.70),))
        A['box'][bw] = pil_to_pm(img)
    return A['box'][bw]


def draw_caption_kinetic(P, fr, t, bl, c):
    """v7: every word pops in on its word (90 -> 108 %), the active word stays Orange at 108 %, then settles 100 %."""
    A = kc_assets(P, c)
    fpsf = float(P.fps)
    em = c['em']
    ch = cap_h('blk', em)
    cym = c['cy'] - 0.08 * em
    X0 = c['cx'] - c['w'] / 2.0
    started = [k for k, q in enumerate(c['words']) if t >= P.words[q]['so'] - 1e-3] or [0]
    j = started[-1]
    if A['box'] is not None:
        f0 = (t - c['t0']) * fpsf
        s = 0.90 + 0.10 * ease_out((f0 + 1) / 4.0)
        bx0 = c['box_rect'][0]
        wj = A['words'][j]
        fj = (t - max(c['t0'], P.words[c['words'][j]]['so'])) * fpsf
        prev_r = (A['words'][j - 1]['xl'] + A['words'][j - 1]['w']) if j else 0.0
        right = prev_r + (wj['xl'] + wj['w'] * 1.04 - prev_r) * ease_out((fj + 1) / 3.0)
        bw = (X0 + right + c['pad'][0]) - bx0
        box = kc_box(A, c, bw)
        by0 = cym - ch / 2.0 - c['pad'][1]
        bh, bww = box.shape[:2]
        bl.blit_scaled(fr, box, bx0 + bww / 2.0, by0 + bh / 2.0, s, 1.0, 'caption')
    for k in started:
        q = c['words'][k]
        ts = max(c['t0'], P.words[q]['so'])
        f = (t - ts) * fpsf
        if k == j:
            s = 0.90 + 0.18 * ease_out((f + 1) / 3.0) if f < 2 else 1.08
            spr, inf = A['words'][k]['orange']
        else:
            tn = max(c['t0'], P.words[c['words'][k + 1]]['so'])
            s = 1.08 - 0.08 * ease_io(((t - tn) * fpsf + 1) / 3.0)
            spr, inf = A['words'][k]['white']
        wc = X0 + A['words'][k]['xl'] + A['words'][k]['w'] / 2.0
        h, w = spr.shape[:2]
        ox, oy = w / 2.0 - inf['cap_x0'] - inf['text_w'] / 2.0, h / 2.0 - inf['cap_y0'] - inf['cap_h'] / 2.0
        bl.blit_scaled(fr, spr, wc + ox * s, cym + oy * s, s, 1.0, 'caption')


# ------------------------------------------------------------------ v6: SHOW THE HOME WHILE HE TALKS (B-roll)
SHOT_LABELS = ['drone', 'front', 'street', 'living', 'kitchen', 'dining', 'bedroom', 'bathroom', 'laundry', 'pool',
               'outdoor', 'garage/shed', 'gym', 'hallway']           # v7: a shed is garage/shed, never gym
LABEL_ALIAS = {'garage': 'garage/shed', 'shed': 'garage/shed', 'carport': 'garage/shed', 'laundry room': 'laundry'}
# spoken word(s) -> allowed shot labels (in order of preference), priority (0 = most specific)
BROLL_MAP = [
    (['swimming pool', 'pool', 'pools'], ['pool'], 0),
    (['kitchen', 'kitchens'], ['kitchen'], 0),
    (['master bedroom', 'bedroom', 'bedrooms'], ['bedroom'], 0),
    (['bathroom', 'bathrooms', 'ensuite', 'en suite'], ['bathroom'], 0),
    (['laundry'], ['laundry'], 0),
    (['living room', 'living area', 'living', 'lounge', 'family room'], ['living'], 0),
    (['dining room', 'dining'], ['dining'], 0),
    (['backyard', 'back yard', 'yard', 'garden', 'gardens', 'alfresco', 'patio', 'outdoor area', 'outdoors',
      'outdoor', 'entertaining area'], ['outdoor'], 0),
    (['garage', 'shed', 'carport'], ['garage/shed'], 0),
    (['home gym', 'gym'], ['gym'], 0),
    (['hallway', 'hall'], ['hallway'], 0),
    (['street', 'neighbourhood', 'neighborhood'], ['street'], 0),
    (['aerial', 'drone'], ['drone'], 0),
    (['wellpresented', 'well presented', 'presenting', 'presented', 'presentation'], ['living', 'kitchen'], 1),
    (['buyers', 'buyer', 'inspection', 'inspections', 'open home'], ['front'], 2),
    (['your property', 'your home', 'property', 'properties', 'home', 'homes', 'house', 'houses'], ['drone', 'front'], 3),
]
BR_MIN, BR_MAX, BR_TARGET = 1.5, 3.0, 2.4      # each B-roll 1.5-3 s
BR_EVERY, BR_GAP = 3.0, 0.8                    # at most one every 3 s; >= 0.8 s of full-screen Umesh between
BR_MIN_SPEED = 0.7                             # a short shot may play slower (>= 70 % speed)
BR_PUSH = 0.06                                 # slow push-in inside each B-roll
BUB_D = int(round(0.32 * W))                   # Umesh bubble diameter (32 % of the width)
BUB_RING, BUB_X0 = 6, int(0.055 * W)
BUB_IN_F, BUB_OUT_F = 7, 4


def _ntok(t):
    return re.sub(r'[^a-z]', '', t.lower())


def detect_shots(path):
    """scene detection: HSV-histogram + pixel change per frame; transition frames (cuts, whips, dissolves) are
    grouped, shots are the steady parts between them (trimmed 0.12 s each side)."""
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    prev, diffs, n = None, [], 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        s = cv2.resize(f, (160, 90), interpolation=cv2.INTER_AREA)
        h = cv2.normalize(cv2.calcHist([cv2.cvtColor(s, cv2.COLOR_BGR2HSV)], [0, 1, 2], None, [16, 8, 8],
                                       [0, 180, 0, 256, 0, 256]), None).flatten()
        g = cv2.cvtColor(s, cv2.COLOR_BGR2GRAY).astype(np.float32)
        if prev is not None:
            diffs.append((cv2.compareHist(prev[0], h, cv2.HISTCMP_BHATTACHARYYA), float(np.abs(g - prev[1]).mean())))
        else:
            diffs.append((0.0, 0.0))
        prev, n = (h, g), n + 1
    cap.release()
    trans = [i for i, (b, m) in enumerate(diffs) if b > 0.42 or m > 45]
    wins = []
    for i in trans:
        if wins and i - wins[-1][1] <= int(0.6 * fps):
            wins[-1][1] = i
        else:
            wins.append([i, i])
    edges = [(-1, -1)] + [tuple(w) for w in wins] + [(n, n)]
    shots, trim = [], int(round(0.12 * fps))
    for (a0, a1), (b0, b1) in zip(edges[:-1], edges[1:]):
        s0, s1 = a1 + 1 + (trim if a1 >= 0 else 0), b0 - (trim if b0 < n else 0)
        if (s1 - s0) / fps >= 0.6:
            shots.append(dict(id=len(shots) + 1, t0=round(s0 / fps, 2), t1=round(s1 / fps, 2), label='', use=True,
                              score=3, note=''))
    return shots, fps, n / fps


def load_shots(path, footage=None):
    d = json.load(open(path))
    shots = d['shots'] if isinstance(d, dict) else d
    foot = footage or (d.get('footage') if isinstance(d, dict) else None)
    if foot and not os.path.isabs(foot) and not os.path.exists(foot):
        foot = os.path.join(os.path.dirname(os.path.abspath(path)), foot)
    for s in shots:
        s['label'] = (s.get('label') or '').lower().strip()
        s['label'] = LABEL_ALIAS.get(s['label'], s['label'])
        if s['label'] and s['label'] not in SHOT_LABELS:
            raise SystemExit('shots.json: unknown label "%s" (use one of %s)' % (s['label'], ', '.join(SHOT_LABELS)))
        s.setdefault('use', True)
        s.setdefault('score', 3)
    return shots, foot


def shot_sheet(footage, shots, path, cols=4):
    """contact sheet: the middle frame of every shot, its number, label and time; dropped shots marked red.
    The white box shows the centred 9:16 crop used in the reel."""
    tw_, th_ = 420, 236
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * (tw_ + 16) + 16, 90 + rows * (th_ + 70)), WARM)
    d = ImageDraw.Draw(sheet)
    d.text((16, 22), 'SHOT LIBRARY  -  %s  (%d shots, %d usable)' % (
        os.path.basename(footage), len(shots), sum(1 for s in shots if s['use'] and s['label'])),
        font=font('blk', 34), fill=NAVY)
    cap = cv2.VideoCapture(footage)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    for k, s in enumerate(shots):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(round((s['t0'] + s['t1']) / 2 * fps)))
        ok, fr = cap.read()
        x, y = 16 + (k % cols) * (tw_ + 16), 90 + (k // cols) * (th_ + 70)
        if ok:
            im = cv2.resize(fr, (tw_, th_), interpolation=cv2.INTER_AREA)
            if not s['use']:
                im = (im.astype(np.float32) * 0.45).astype(np.uint8)
            pim = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
            sheet.paste(pim, (x, y))
            if s['use']:
                cw = th_ * 9 / 16.0
                d.rectangle([x + tw_ / 2 - cw / 2, y, x + tw_ / 2 + cw / 2, y + th_ - 1], outline=WHITE, width=2)
        ok_ = s['use'] and s['label']
        col = BLUE if ok_ else (200, 40, 40)
        lab = ('#%02d  %s' % (s['id'], s['label'].upper() if s['label'] else '?'))
        d.rounded_rectangle([x, y + th_ + 6, x + tw_, y + th_ + 60], 10, fill=col)
        d.text((x + 12, y + th_ + 12), lab, font=font('blk', 24), fill=WHITE)
        d.text((x + 12, y + th_ + 38), '%.2f-%.2fs (%.1fs)%s' % (s['t0'], s['t1'], s['t1'] - s['t0'],
                                                                ('  DROPPED: ' + s.get('note', '')[:30]) if not s['use']
                                                                else ('  ' + s.get('note', '')[:34] if s.get('note') else '')),
               font=font('xb', 16), fill=WHITE)
    cap.release()
    sheet.save(path, quality=90)
    return path


def broll_candidates(P):
    words = P.words
    toks = [_ntok(w['w']) for w in words]
    phr = []
    for ph_list, labels, prio in BROLL_MAP:
        for ph in ph_list:
            phr.append(([_ntok(p) for p in ph.split()], labels, prio))
    phr.sort(key=lambda x: -len(x[0]))
    out, k = [], 0
    while k < len(words):
        hit = next((p for p in phr if toks[k:k + len(p[0])] == p[0]), None)
        if hit is None:
            k += 1
            continue
        L = len(hit[0])
        out.append(dict(k0=k, k1=k + L - 1, t=words[k]['so'], labels=hit[1], prio=hit[2],
                        word=' '.join(words[q]['w'].strip(',.?!') for q in range(k, k + L))))
        k += L
    return out


def broll_forbidden(P):
    """intervals where Umesh must stay full-screen: hook (+glide), key line, call to action, end card."""
    iv = []
    if P.hook_on:
        iv.append((0.0, P.hook_t1 + HOOK_EASE / float(P.fps) + 0.05, 'hook'))
    else:
        iv.append((0.0, HOOK_T1, 'hook'))
    for z in P.zones:
        if z['level'] == 'KEY':
            iv.append((z['t0'], z['t1'], 'key line'))
    for s in P.sents:
        if CTA_RE.search(' '.join(P.words[k]['w'] for k in s)):
            iv.append((P.words[s[0]]['so'] - 0.1, P.speech_end, 'call to action'))
    iv.append((P.speech_end - 0.05, 1e9, 'end card'))
    return iv


def schedule_broll(P):
    P.broll, P.broll_log = [], []
    if not P.shots or not P.words or P.ctype == 'WALKTHROUGH':
        return []
    shots = [s for s in P.shots if s['use'] and s['label']]
    forb = broll_forbidden(P)
    P.broll_forb = forb
    cands = broll_candidates(P)
    chosen, used = [], set()
    word_ends = sorted(w['eo'] for w in P.words)
    for c in sorted(cands, key=lambda c: (c['prio'], c['t'])):
        t0 = max(0.0, c['t'] - 0.1)
        why = None
        blk = next((f for f in forb if f[0] - 1e-6 <= t0 < f[1]), None)
        if blk:
            why = 'in the %s' % blk[2]
        lim = min([f[0] for f in forb if f[0] > t0] + [P.speech_end - 0.05])
        for o in chosen:
            if abs(o['t0'] - t0) < BR_EVERY - 1e-6:
                why = why or '%.1fs after another B-roll (< %.0f s)' % (abs(o['t0'] - t0), BR_EVERY)
            if o['t0'] <= t0 < o['t1'] + BR_GAP:
                why = why or 'overlaps the B-roll at %.1fs' % o['t0']
            if o['t0'] > t0:
                lim = min(lim, o['t0'] - BR_GAP)
        if why is None and lim - t0 < BR_MIN - 1e-6:
            why = 'only %.1fs free before the %s' % (lim - t0, 'next B-roll / key line / end')
        if why:
            P.broll_log.append((c['t'], c['word'], 'skipped: ' + why))
            continue
        ends = [e for e in word_ends if t0 + BR_MIN <= e + 0.05 <= min(lim, t0 + BR_MAX)]
        t1 = min(ends + [min(lim, t0 + BR_MAX)], key=lambda e: abs(e + 0.05 - (t0 + BR_TARGET)))
        t1 = min(t1 + 0.05, lim, t0 + BR_MAX)
        pick = None                                   # unused first, then best-looking, then label preference
        pool = [s for s in shots if s['label'] in c['labels']]
        pool.sort(key=lambda s: (s['id'] in used, -s.get('score10', s['score']), c['labels'].index(s['label']),
                                 -(s['t1'] - s['t0'])))
        for s in pool:
            L = s['t1'] - s['t0']
            d = min(t1 - t0, L / BR_MIN_SPEED)
            if d >= BR_MIN - 1e-6:
                pick = (s, d)
                break
        if pick is None:
            P.broll_log.append((c['t'], c['word'], 'skipped: no usable %s shot' % '/'.join(c['labels'])))
            continue
        s, d = pick
        L = s['t1'] - s['t0']
        speed = min(1.0, L / d)
        src0 = s['t0'] + (L - d * speed) / 2.0
        b = dict(t0=t0, t1=t0 + d, t=c['t'], word=c['word'], k0=c['k0'], allowed=c['labels'], label=s['label'],
                 shot=s, speed=speed, src0=src0)
        chosen.append(b)
        used.add(s['id'])
        P.broll_log.append((c['t'], c['word'], 'B-roll shot #%02d %s %.1f-%.1fs' % (s['id'], s['label'], t0, t0 + d)))
    P.broll = sorted(chosen, key=lambda b: b['t0'])
    return P.broll


def broll_at(P, t):
    for b in getattr(P, 'broll', []):
        if b['t0'] <= t < b['t1']:
            return b
    return None


def broll_overlaps(P, t0, t1, pad=0.0):
    return any(t0 < b['t1'] + pad and t1 > b['t0'] - pad for b in getattr(P, 'broll', []))


def load_broll_frames(P):
    cap = cv2.VideoCapture(P.footage)
    P.foot_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    for b in P.broll:
        f0 = int(math.floor(b['src0'] * P.foot_fps))
        f1 = int(math.ceil((b['src0'] + (b['t1'] - b['t0']) * b['speed']) * P.foot_fps)) + 1
        cap.set(cv2.CAP_PROP_POS_FRAMES, f0)
        frs = []
        for _ in range(f1 - f0):
            ok, fr = cap.read()
            if not ok:
                break
            if P.opt.whole_room:                                          # v7: sharpen once, after the upscale
                frs.append(fr)
            else:
                blur = cv2.GaussianBlur(fr, (0, 0), 1.0)                 # light sharpen at source size
                frs.append(cv2.addWeighted(fr, 1.45, blur, -0.45, 0))
        b['frames'], b['f0'] = frs, f0
        b['xfer'] = None
        if P.opt.cinematic and getattr(P, 'talk_lab', None) is not None and frs:   # v7: match the talking shots
            st = lab_stats(frs[::max(1, len(frs) // 6)])
            b['xfer'] = match_params(st, P.talk_lab)
            b['lab_before'] = st[0]
            b['lab_after'] = lab_stats([apply_xfer(x, b['xfer']) for x in frs[::max(1, len(frs) // 6)]])[0]
        b['x_range'] = [1e9, -1e9]
    cap.release()


def footage_frame(P, b, t):
    """footage fills the 9:16 frame: centred crop, slow push-in, lanczos upscale + light sharpen, brand grade."""
    u = t - b['t0']
    d = b['t1'] - b['t0']
    fi = int(round((b['src0'] + u * b['speed']) * P.foot_fps)) - b['f0']
    src = b['frames'][int(clamp(fi, 0, len(b['frames']) - 1))]
    if b.get('xfer') is not None:
        src = apply_xfer(src, b['xfer'])
    sh, sw = src.shape[:2]
    if P.opt.whole_room:                                    # v7: show the WHOLE room - never the tight middle only
        p = clamp(u / max(0.1, d), 0, 1)
        p = 0.65 * p + 0.35 * ease_io(p)                    # slow, near-constant speed
        if b['shot'].get('kind') == 'detail':
            z = 1.0 + 0.08 * p                              # details: slow zoom-in
            ch = sh / z
            cw = ch * W / float(H)
            x0, y0 = (sw - cw) / 2.0, (sh - ch) / 2.0
        else:                                               # wide rooms: pan across the full width
            ch = float(sh)
            cw = min(sw, ch * W / float(H))
            if cw * H / float(W) < ch:
                ch = cw * H / float(W)
            q = p if b['shot'].get('pan_dir', 1) > 0 else 1 - p
            x0, y0 = (sw - cw) * q, (sh - ch) / 2.0
        b['x_range'] = [min(b['x_range'][0], x0), max(b['x_range'][1], x0 + cw)]
        b['src_w'] = sw
        s = W / cw
        M = np.array([[s, 0, -s * x0], [0, s, -s * y0]], np.float32)
        if P.sr is not None:
            src = P.sr.upsample(src)
            k_ = src.shape[1] / float(sw)
            M = np.array([[s / k_, 0, -s * x0], [0, s / k_, -s * y0]], np.float32)
        out = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
        out = sharpen_nohalo(out)
        lut, vig = P.grade
        return grade(out, lut, vig)
    z = 1.0 + BR_PUSH * ease_io(u / max(0.1, d))
    ch = sh / z
    cw = ch * W / float(H)
    if cw > sw / z:
        cw = sw / z
        ch = cw * H / float(W)
    s = W / cw
    M = np.array([[s, 0, W / 2.0 - s * sw / 2.0], [0, s, H / 2.0 - s * sh / 2.0]], np.float32)
    out = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    blur = cv2.GaussianBlur(out, (0, 0), 2.4)
    out = cv2.addWeighted(out, 1.35, blur, -0.35, 0)
    lut, vig = P.grade
    return grade(out, lut, vig)


def sharpen_nohalo(img, amount=0.55, sigma=1.3):
    """mild unsharp mask clamped to the local 3x3 min/max - no bright/dark halos around edges."""
    blur = cv2.GaussianBlur(img, (0, 0), sigma)
    sh = cv2.addWeighted(img, 1 + amount, blur, -amount, 0)
    k = np.ones((3, 3), np.uint8)
    return np.minimum(np.maximum(sh, cv2.erode(img, k)), cv2.dilate(img, k))


def load_sr():
    """offline super-resolution: only if OpenCV dnn_superres AND a model file are already on disk (no download)."""
    try:
        from cv2 import dnn_superres
    except Exception:
        return None, 'no offline super-resolution available (cv2.dnn_superres missing) -> lanczos + halo-free sharpen'
    for name, algo, sc in (('FSRCNN_x4.pb', 'fsrcnn', 4), ('ESPCN_x4.pb', 'espcn', 4), ('EDSR_x4.pb', 'edsr', 4),
                           ('FSRCNN_x3.pb', 'fsrcnn', 3), ('ESPCN_x3.pb', 'espcn', 3)):
        p = find_model(name)
        if p:
            try:
                sr = dnn_superres.DnnSuperResImpl_create()
                sr.readModel(p)
                sr.setModel(algo, sc)
                return sr, 'offline super-resolution %s' % name
            except Exception:
                pass
    return None, 'no offline super-resolution model on disk -> lanczos + halo-free sharpen'


def lab_stats(frames):
    a = np.concatenate([cv2.cvtColor(f, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32) for f in frames])
    return a.mean(0), a.std(0)


def match_params(src, ref, strength=(0.55, 0.75, 0.75)):
    """moderated Reinhard transfer in Lab: means move part of the way, contrast within 0.8-1.25x."""
    (ms, ss), (mr, sr) = src, ref
    st = np.array(strength, np.float32)
    k = 1 + (np.clip(sr / np.maximum(ss, 1e-3), 0.8, 1.25) - 1) * st
    return k.astype(np.float32), ms.astype(np.float32), (ms + (mr - ms) * st).astype(np.float32)


def apply_xfer(img, xf):
    k, ms, tgt = xf
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    lab = (lab - ms) * k + tgt
    return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)


def talk_reference(upright, dur, n=6):
    frs = []
    for k in range(n):
        f = grab(upright, dur * (k + 0.5) / n, (270, 480))
        if f is not None:
            frs.append(f)
    return lab_stats(frs) if frs else None


def score_shots(footage, shots):
    """v7 shot score 0-10: sharpness (40 %), exposure - no blown windows (35 %), clean composition (25 %).
    Also measures the camera direction (pan_dir) for the whole-room pan."""
    cap = cv2.VideoCapture(footage)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    for s in shots:
        if not s['use'] or not s['label']:
            continue
        f0, f1 = int(round(s['t0'] * fps)), int(round(s['t1'] * fps))
        cap.set(cv2.CAP_PROP_POS_FRAMES, f0)
        sh, bl, mn, ed, dxs, prev = [], [], [], [], [], None
        for i in range(f0, f1):
            ok, fr = cap.read()
            if not ok:
                break
            if (i - f0) % 2:
                continue
            g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
            if (i - f0) % 6 == 0:
                sh.append(cv2.Laplacian(g, cv2.CV_64F).var())
                bl.append(float((fr.max(2) >= 248).mean()))
                mn.append(float(g.mean()) / 255.0)
                ed.append(float((cv2.Canny(g, 80, 180) > 0).mean()))
            smf = cv2.resize(g, (160, 90), interpolation=cv2.INTER_AREA).astype(np.float64)
            if prev is not None:
                (dx, dy), _ = cv2.phaseCorrelate(prev, smf)
                dxs.append(dx)
            prev = smf
        if not sh:
            continue
        s_sharp = clamp((math.log10(float(np.median(sh)) + 1) - 1.6) / 1.4, 0, 1)
        blown, mean = float(np.mean(bl)), float(np.mean(mn))
        s_exp = 0.7 * clamp(1 - blown / 0.06, 0, 1) + 0.3 * clamp(1 - abs(mean - 0.5) / 0.35, 0, 1)
        s_clean = clamp(1 - (float(np.mean(ed)) - 0.04) / 0.14, 0, 1)
        s['q'] = dict(sharp=round(s_sharp, 2), exposure=round(s_exp, 2), clean=round(s_clean, 2),
                      blown_pct=round(100 * blown, 1), edges_pct=round(100 * float(np.mean(ed)), 1))
        s['score10'] = round(10 * (0.40 * s_sharp + 0.35 * s_exp + 0.25 * s_clean), 1)
        tot = float(np.sum(dxs)) if dxs else 0.0
        s['pan_dir'] = 1 if tot <= 0 else -1             # content drifts left = camera moves right -> pan L->R
        s['cam_dx'] = round(tot, 1)
        s.setdefault('kind', 'wide')
    cap.release()
    return shots


def plan_bubbles(P):
    """bubble: bottom-left, just above the lowest caption that runs during the B-roll."""
    for b in P.broll:
        caps = [c for c in P.caps if c['t0'] < b['t1'] and c['t1'] > b['t0']]
        top = min([c['box_rect'][1] for c in caps] + [CAP_MAX_Y])
        if P.opt.bubble_pop:                                 # v7: >= 60 px above the captions, even at 110 % pop
            cy = top - BUB_GAP_CAP - (BUB_RING + BUB_D / 2.0) * 1.10
        else:
            cy = top - 40 - BUB_RING - BUB_D / 2.0
        b['cap_top'] = top
        b['bub'] = (BUB_X0 + BUB_RING + BUB_D / 2.0, cy)
        fs = P.track.span(P.tl.o2s(b['t0']), P.tl.o2s(b['t1'] - 1e-3))
        if fs:
            f = np.median([[q['x'], q['y'], q['x'] + q['w'], q['y'] + q['h']] for q in fs], axis=0)
        else:
            f = np.array([W * 0.4, H * 0.25, W * 0.6, H * 0.35])
        fh = f[3] - f[1]
        side = clamp(2.5 * fh, 0.3 * W, W)
        cx, cy_ = (f[0] + f[2]) / 2.0, (f[1] + f[3]) / 2.0 + 0.22 * side
        b['bub_crop'] = (int(clamp(cx - side / 2, 0, W - side)), int(clamp(cy_ - side / 2, 0, H - side)), int(side))


def _disk(d, ss=4):
    m = Image.new('L', (d * ss, d * ss), 0)
    ImageDraw.Draw(m).ellipse([0, 0, d * ss - 1, d * ss - 1], fill=255)
    return np.asarray(m.resize((d, d), Image.LANCZOS), np.float32)[..., None] / 255.0


def bubble_assets(P):
    if getattr(P, 'bub_assets', None):
        return P.bub_assets
    D, R = BUB_D, BUB_RING
    yy = np.linspace(0, 1, D, dtype=np.float32)[:, None, None]
    top, bot = np.array(BLUE[::-1], np.float32), np.array(NAVY[::-1], np.float32)
    bg = np.broadcast_to(top * (1 - yy) + bot * yy, (D, D, 3)).copy()
    inner = _disk(D)
    ring = _disk(D + 2 * R)
    ring_spr = np.concatenate([np.full(ring.shape[:2] + (3,), 255, np.float32) * ring, ring], -1)
    pad = 40
    sh = Image.new('L', (D + 2 * R + 2 * pad, D + 2 * R + 2 * pad), 0)
    if P.opt.bubble_pop:                                     # v7: visible soft shadow
        ImageDraw.Draw(sh).ellipse([pad, pad + 14, pad + D + 2 * R, pad + 14 + D + 2 * R], fill=185)
        sh = np.asarray(sh.filter(ImageFilter.GaussianBlur(13)), np.float32)[..., None] / 255.0
    else:
        ImageDraw.Draw(sh).ellipse([pad, pad + 10, pad + D + 2 * R, pad + 10 + D + 2 * R], fill=125)
        sh = np.asarray(sh.filter(ImageFilter.GaussianBlur(16)), np.float32)[..., None] / 255.0
    sh_spr = np.concatenate([np.zeros(sh.shape[:2] + (3,), np.float32), sh], -1)
    P.bub_assets = dict(bg=bg, inner=inner, ring=ring_spr, shadow=sh_spr, pad=pad)
    return P.bub_assets


def draw_bubble(P, fr, t, b, upright_frame, mask_full_):
    """Umesh as a round cut-out: person (segmentation) on a Blue->Navy disc, white 6 px ring, soft shadow."""
    A = bubble_assets(P)
    D, R = BUB_D, BUB_RING
    x0, y0, side = b['bub_crop']
    lut, vig = P.grade
    crop = upright_frame[y0:y0 + side, x0:x0 + side]
    crop = cv2.resize(grade(np.ascontiguousarray(crop), lut, np.ones((side, side, 1), np.float32) * 1.0),
                      (D, D), interpolation=cv2.INTER_AREA).astype(np.float32)
    mk = cv2.resize(mask_full_[y0:y0 + side, x0:x0 + side], (D, D), interpolation=cv2.INTER_LINEAR)[..., None]
    img = crop * mk + A['bg'] * (1 - mk)
    spr = np.concatenate([img * A['inner'], A['inner']], -1)
    fpsf = float(P.fps)
    f_in, f_out = (t - b['t0']) * fpsf, (b['t1'] - t) * fpsf
    if f_in < BUB_IN_F * 0.6:
        s = 0.55 + 0.53 * ease_out(f_in / (BUB_IN_F * 0.6))              # pop 55 -> 108 -> 100 %
    elif f_in < BUB_IN_F:
        s = 1.08 - 0.08 * ease_io((f_in - BUB_IN_F * 0.6) / (BUB_IN_F * 0.4))
    else:
        s = 1.0
    a = clamp(f_in / 2.0, 0, 1) * clamp(f_out / BUB_OUT_F, 0, 1)
    s *= 0.85 + 0.15 * clamp(f_out / BUB_OUT_F, 0, 1)
    if P.opt.bubble_pop:                                     # v7: pop 0 -> 110 -> 100 % over 8 frames, no fade
        fi_ = math.floor(f_in + 1e-6) + 0.4                       # whole frames since the B-roll started
        if fi_ < 5:
            s = 1.10 * ease_out(fi_ / 5.0)
        elif fi_ < BUB_POP_F:
            s = 1.10 - 0.10 * ease_io((fi_ - 5) / float(BUB_POP_F - 5))
        else:
            s = 1.0
        s *= clamp(f_out / 3.0, 0, 1) ** 0.6                 # pops out again on the last 3 frames
        a = 1.0 if s > 0.03 else 0.0
        P.bub_scales = getattr(P, 'bub_scales', []) + [(round(f_in, 1), round(s, 3))]
    cx, cy = b['bub']
    bl = P.blitter
    bl.blit_scaled(fr, A['shadow'], cx, cy, s, a, 'bubble')
    r1 = bl.blit_scaled(fr, A['ring'], cx, cy, s, a, 'bubble')
    bl.blit_scaled(fr, spr, cx, cy, s, a, 'bubble')
    return r1


# ------------------------------------------------------------------ render
def iter_out(P, upright):
    rd = FrameReader(upright)
    seg_i, src_i, out_i = 0, 0, 0
    segs = P.tl.segs
    try:
        while seg_i < len(segs):
            fr = rd.read()
            if fr is None:
                break
            fa, fb = segs[seg_i]
            if src_i >= fa:
                yield out_i, src_i, fr
                out_i += 1
                if src_i + 1 >= fb:
                    seg_i += 1
            src_i += 1
    finally:
        rd.close()


def hb_visibility(hb, m):
    """m = person mask (rows from y=0), float 0..1. Returns (pixel share readable, [visible share per letter])."""
    num = den = 0.0
    letters = []
    for (spr, inf), (x, y) in zip(hb['sprites'], hb['pos']):
        mk = inf['mask']
        h, w = mk.shape
        x0, y0 = int(round(x)), int(round(y))
        sx0, sy0 = max(0, -x0), max(0, -y0)
        X0, Y0, X1, Y1 = x0 + sx0, y0 + sy0, min(W, x0 + w), min(m.shape[0], y0 + h)
        if X1 <= X0 or Y1 <= Y0:
            continue
        a = (mk[sy0:sy0 + Y1 - Y0, sx0:sx0 + X1 - X0] > 0.5).astype(np.float32)
        vis = a * (1 - m[Y0:Y1, X0:X1])
        num += float(vis.sum())
        den += float(a.sum())
        for lx0, lx1 in inf['letters']:
            c0, c1 = max(0, int(lx0) - sx0), max(0, int(math.ceil(lx1)) - sx0)
            la = float(a[:, c0:c1].sum())
            if la > 0:
                letters.append(float(vis[:, c0:c1].sum()) / la)
    return num / max(1.0, den), letters


def hook_prepass(P, upright):
    """segment the hook frames once, then place the title behind his head: as low as possible while every
    letter keeps >= 55 % of its pixels (>= 80 % of all text pixels readable); fallback >= 80 % of the letters
    readable; otherwise the normal hook box."""
    seg = Segmenter()
    if not seg.ok:
        return None, 'no segmenter (%s)' % seg.err
    lut, vig = P.grade
    fpsf = float(P.fps)
    masks = []
    prev_src, prev_z = None, None
    for out_i, src_i, fr in iter_out(P, upright):
        t = out_i / fpsf
        if t > P.hook_t1:
            break
        z = zone_at(P, t)
        if prev_src is not None and (src_i != prev_src + 1 or z is not prev_z):
            seg.reset()
        prev_src, prev_z = src_i, z
        Mb, _ = xforms(P, t)
        img = grade(warp(fr, Mb), lut, vig)
        m = seg(img)
        if t >= P.hook_t0 and out_i % 2 == 0:
            masks.append((cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)[:1100] * 255).astype(np.uint8))
    seg.close()
    if not masks:
        return None, 'no frames'
    hb = P.hb
    fmasks = [mm.astype(np.float32) / 255.0 for mm in masks]
    res = []
    tops = list(range(int(TOPMIN), int(max(TOPMIN, hb['want_head'] - 0.15 * hb['block_h'])) + 1, 6))
    for top in sorted(tops, reverse=True):                        # lowest (most "behind") first
        place_hook_behind(hb, top)
        pix, lread, worst = [], [], []
        for m in fmasks:
            pv, lv = hb_visibility(hb, m)
            pix.append(pv)
            lread.append(sum(1 for v in lv if v >= 0.6) / float(max(1, len(lv))))
            worst.append(min(lv) if lv else 1.0)
        res.append((top, min(pix), min(lread), min(worst), float(np.mean(pix))))
    pick = next((r for r in res if r[3] >= 0.55 and r[1] >= 0.80), None)
    if pick is None:
        pick = next((r for r in res if r[2] >= 0.80 and r[1] >= 0.60), None)
    if pick is None:
        r = max(res, key=lambda r: r[2])
        return None, 'only %d%% of the letters readable at the highest position' % round(r[2] * 100)
    place_hook_behind(hb, pick[0])
    return (pick[0], pick[1], pick[4], pick[2], pick[3]), ''


def render(P, upright, out_video, stats):
    lut, vig = P.grade
    fpsf = float(P.fps)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '%dx%d' % (W, H),
                            '-r', str(P.fps), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                            '-maxrate', '20M', '-bufsize', '40M',                # v7: grain would push ~45 Mbps
                            '-profile:v', 'high', '-pix_fmt', 'yuv420p', out_video], stdin=subprocess.PIPE)
    bl = Blitter()
    P.blitter = bl
    need_seg = P.opt.bg_pop or P.hb is not None or any(g.get('photo') for g in P.visuals)
    seg = Segmenter() if need_seg else None
    if seg is not None and not seg.ok:
        log('    (segmentation unavailable: %s - background pop / text-behind / photo layout off)' % seg.err)
        seg = None
    P.seg_kind = seg.kind if seg else 'none'
    prev_src, prev_z, prev_photo = None, None, None
    last = None
    hb = P.hb
    if hb is not None:
        grad = np.zeros((int(hb['top'] + hb['block_h'] + 120), 1, 1), np.float32)
        gy = np.arange(grad.shape[0], dtype=np.float32)
        grad[:, 0, 0] = 0.42 * np.clip(1 - gy / grad.shape[0], 0, 1) ** 1.2
    hook_flick = []
    bseg, prev_br = None, None
    if P.broll:                                                           # v6: Umesh bubble over the B-roll
        bseg = Segmenter()
        if not bseg.ok:
            log('    (segmentation unavailable: %s - bubble shows the plain crop)' % bseg.err)
            bseg = None
        load_broll_frames(P)
    for out_i, src_i, fr in iter_out(P, upright):
        t = out_i / fpsf
        br = broll_at(P, t)
        if br is not None:
            if br is not prev_br and bseg is not None:
                bseg.reset()
            mb = mask_full(bseg(fr)) if bseg is not None else np.ones((H, W), np.float32)
            img = footage_frame(P, br, t)
            img = apply_transition(P, img, out_i, stats)                 # v7
            r = draw_bubble(P, img, t, br, fr, mb)
            stats['bub_rects'].append((t, r, P.broll.index(br)))
            if any(g['t0'] <= t < g['t1'] for g in P.visuals) or any(b['t0'] <= t < b['t1'] for b in P.bigwords):
                stats['icon_in_broll'].append(round(t, 2))
            draw_caption(P, img, t, bl, stats)
            img = apply_shake(P, img, out_i, stats)
            img = add_grain(P, img, out_i)
            draw_progress(P, img, t)
            enc.stdin.write(img.tobytes())
            last = img
            stats['frames'] += 1
            stats['broll_frames'] += 1
            prev_br = br
            if seg is not None:
                seg.reset()
            prev_src = None
            continue
        prev_br = None
        z = zone_at(P, t)
        Mb, Mp = xforms(P, t)
        img = grade(warp(fr, Mb), lut, vig)
        if getattr(P, 'kh_on', False) and 1 <= out_i < KH_F:           # v7 kinetic hook: zoom motion blur
            img = zoom_blur(img, z['anchor'][0], z['anchor'][1], kh_zoom(out_i - 1) / kh_zoom(out_i))
        photo = photo_at(P, t)
        hb_on = hb is not None and P.hook_t0 <= t < P.hook_t1
        m = None
        if seg is not None and (P.opt.bg_pop or hb_on or Mp is not None):
            if prev_src is not None and (src_i != prev_src + 1 or z is not prev_z or photo is not prev_photo):
                seg.reset()
            n0 = len(seg.flick)
            ms = seg(img)
            if hb_on and len(seg.flick) > n0:
                hook_flick.append(seg.flick[-1])
            m = mask_full(ms)[..., None]
        prev_src, prev_z, prev_photo = src_i, z, photo
        if m is not None:
            if Mp is not None:
                bg = cv2.GaussianBlur(img, (0, 0), 18).astype(np.float32) * 0.62
                pers = cv2.warpAffine(img, Mp, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
                mp_ = cv2.warpAffine(m[..., 0], Mp, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)[..., None]
                img = (pers.astype(np.float32) * mp_ + bg * (1 - mp_)).clip(0, 255).astype(np.uint8)
            else:
                if P.opt.bg_pop and P.ctype != 'WALKTHROUGH':
                    bg = cv2.GaussianBlur(img, (0, 0), 5).astype(np.float32) * 0.85
                else:
                    bg = img.astype(np.float32)
                if hb_on:
                    gh = grad.shape[0]
                    k = (t - P.hook_t0) * fpsf
                    a_in = clamp((P.hook_t1 - t) * fpsf / 5.0, 0, 1)            # full from frame 0
                    bg[:gh] = bg[:gh] * (1 - grad * a_in) + np.array(NAVY[::-1], np.float32) * grad * a_in
                    tmp = np.clip(bg, 0, 255).astype(np.uint8)
                    if getattr(P, 'kh_on', False):
                        draw_hook_words(P, tmp, out_i, bl, a_in)              # v7 words pop in one by one
                    else:
                        for (spr, inf), (x, y) in zip(hb['sprites'], hb['pos']):
                            bl.blit(tmp, spr, x, y, a_in, 'hook')
                    if out_i == 0:
                        stats['cover'] = a_in
                    if a_in > 0.99 and (not getattr(P, 'kh_on', False) or out_i >= hb['landed_f']):
                        pv, lv = hb_visibility(hb, m[..., 0])
                        stats['hb_vis'].append(pv)
                        stats['hb_letters'].append(sum(1 for v in lv if v >= 0.6) / float(max(1, len(lv))))
                        stats['hb_worst'].append(min(lv) if lv else 1.0)
                    bg = tmp.astype(np.float32)
                img = (img.astype(np.float32) * m + bg * (1 - m)).clip(0, 255).astype(np.uint8)
        elif hb_on:
            pass
        if P.hook_on and P.hb is None and P.hookbox and P.hook_t0 <= t < P.hook_t1:
            k = (t - P.hook_t0) * fpsf
            a = clamp((P.hook_t1 - t) * fpsf / 4.0, 0, 1)
            if out_i == 0:
                stats['cover'] = a
            bl.blit(img, P.hookbox['sprite'], P.hookbox['rect'][0], P.hookbox['rect'][1], a, 'hook')
        img = apply_transition(P, img, out_i, stats)                     # v7 (picture only, not the text)
        draw_visuals(P, img, t, bl, stats)
        big = draw_bigword(P, img, t, bl)
        if not big:
            draw_caption(P, img, t, bl, stats)
        img = apply_shake(P, img, out_i, stats)
        img = add_grain(P, img, out_i)
        draw_progress(P, img, t)
        enc.stdin.write(img.tobytes())
        last = img
        stats['frames'] += 1
    P.card_t0_real = stats['frames'] / fpsf
    # end card
    clean_last = last
    bg, layers, rects = make_end_card(P, clean_last, P.headshot)
    nend = int(round(END_DUR * fpsf))
    P.card_layers = (bg, layers, rects)
    for k in range(nend):
        u = k / fpsf
        frc = end_card_frame(P, u, clean_last, bg, layers, bl, animate=P.opt.end_anim)
        enc.stdin.write(frc.tobytes())
    enc.stdin.close()
    enc.wait()
    P.card_rects = rects
    P.total = (stats['frames'] + nend) / fpsf
    stats['flicker'] = seg.flick if seg else []
    if bseg is not None:
        stats['bub_flicker'] = bseg.flick
        bseg.close()
    for b in P.broll:
        b.pop('frames', None)
    if seg is not None:
        seg.close()
    stats['hook_flicker'] = hook_flick


# ------------------------------------------------------------------ audio: voice + self-made SFX
SR = 48000


def read_wav_f32(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                         stdout=subprocess.PIPE).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def sfx_whoosh(dur=0.25, seed=7):
    """filtered noise sweep (state-variable band-pass, 350 Hz -> 3.2 kHz) with a soft swell and L->R pan."""
    rng = np.random.default_rng(seed)
    n = int(SR * dur)
    x = rng.standard_normal(n).astype(np.float64)
    u = np.arange(n) / float(n)
    fc = 350.0 * (3200.0 / 350.0) ** u
    f = 2 * np.sin(np.pi * fc / SR)
    q = 1 / 1.4
    low = band = 0.0
    y = np.empty(n)
    for i in range(n):
        high = x[i] - low - q * band
        band += f[i] * high
        low += f[i] * band
        y[i] = band
    env = np.sin(np.pi * np.clip(u, 0, 1)) ** 1.6 * (0.6 + 0.4 * u)
    y *= env
    y /= (np.abs(y).max() + 1e-9)
    pan = 0.25 + 0.5 * u
    return np.stack([y * np.cos(pan * np.pi / 2), y * np.sin(pan * np.pi / 2)], 1) * 1.2


def sfx_pop(dur=0.09):
    n = int(SR * dur)
    t = np.arange(n) / float(SR)
    fr = 380 + 620 * np.exp(-t / 0.018)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    env = np.exp(-t / 0.024) * np.clip(t / 0.003, 0, 1)
    y = np.sin(ph) * env
    rng = np.random.default_rng(3)
    click = rng.standard_normal(n) * np.exp(-t / 0.002) * 0.25
    y = y + np.diff(np.concatenate([[0], click]))
    y /= (np.abs(y).max() + 1e-9)
    return np.stack([y, y], 1)


def sfx_hit(dur=0.42):
    """v7 soft low 'hit': sub thump 78 -> 38 Hz + low-passed noise transient."""
    n = int(SR * dur)
    t = np.arange(n) / float(SR)
    fr = 38 + 40 * np.exp(-t / 0.05)
    y = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.clip(t / 0.004, 0, 1) * np.exp(-t / 0.13)
    rng = np.random.default_rng(11)
    nz = rng.standard_normal(n) * np.exp(-t / 0.018)
    lp, acc = np.empty(n), 0.0
    for i in range(n):
        acc += 0.07 * (nz[i] - acc)
        lp[i] = acc
    y = y + 0.5 * lp / (np.abs(lp).max() + 1e-9)
    y /= (np.abs(y).max() + 1e-9)
    return np.stack([y, y], 1)


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-9)


def build_audio(P, wav48, out_wav, work, stats):
    fpsf = float(P.fps)
    lines = []
    for k, (fa, fb) in enumerate(P.tl.segs):
        a, b = fa / fpsf, fb / fpsf
        d = b - a
        lines.append('[0:a]atrim=start=%.6f:end=%.6f,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=%.3f,'
                     'afade=t=out:st=%.6f:d=%.3f[a%d];' % (a, b, AFADE, max(0, d - AFADE), AFADE, k))
    lines.append(''.join('[a%d]' % k for k in range(len(P.tl.segs))) +
                 'concat=n=%d:v=0:a=1[cat]' % len(P.tl.segs))
    fcs = os.path.join(work, 'audio_cut.txt')
    open(fcs, 'w').write('\n'.join(lines))
    cut = os.path.join(work, 'cut.wav')
    run(['ffmpeg', '-v', 'error', '-y', '-i', wav48, '-filter_complex_script', fcs, '-map', '[cat]',
         '-c:a', 'pcm_s16le', '-ar', str(SR), '-ac', '2', cut])
    voice = read_wav_f32(cut)
    n_total = int(round(P.total * SR))
    mix = np.zeros((n_total, 2), np.float32)
    mix[:min(len(voice), n_total)] = voice[:n_total]
    # voice level while he speaks (50 ms windows)
    win = int(0.05 * SR)
    vm = voice.mean(1)
    nw = len(vm) // win
    vw = 20 * np.log10(np.sqrt(np.mean(vm[:nw * win].reshape(nw, win) ** 2, 1)) + 1e-9) if nw else np.array([-90.0])
    speech_db = float(np.percentile(vw[vw > vw.max() - 30], 60)) if nw else -30.0
    voice_peak = 20 * np.log10(np.abs(voice).max() + 1e-9)
    in_word = np.zeros(n_total, bool)
    for w in P.words:
        in_word[int(w['so'] * SR):int(w['eo'] * SR)] = True
    events = []
    if P.opt.sfx:
        wh, pop = sfx_whoosh(), sfx_pop()
        if P.hook_on:
            events.append(('whoosh', P.hook_t0 - 0.12, wh, 'hook'))
        for b in P.bigwords:
            events.append(('whoosh', b['t0'] - 0.18, wh, 'big word "%s"' % b['text']))
        trs = getattr(P, 'transitions', [])
        for tr in trs:                                  # v7: every transition has its whoosh
            events.append(('whoosh', tr['t'] - 0.12, wh, 'transition %s (%s)' % (tr['type'], tr['why'])))
        if getattr(P, 'impacts', []):
            hit = sfx_hit()
            for im in P.impacts:
                events.append(('hit', im['t'] - 0.01, hit, 'impact %s' % im['why']))
        for g in P.visuals:
            if g.get('photo'):
                events.append(('pop', g['t0'] + 0.02, pop, 'photo "%s"' % g['chips'][0]['label']))
            else:                                       # whoosh on IN, soft pop when the label lands
                if not any(abs(g['t0'] - tr['t']) < 0.35 for tr in trs):
                    events.append(('whoosh', g['t0'] - 0.08, wh, 'visual IN "%s"' % g['chips'][0]['label']))
                events.append(('pop', g['t0'] + LABEL_F / fpsf - 0.02, pop, 'label "%s"' % g['chips'][0]['label']))
        for b in (getattr(P, 'broll', []) if not trs else []):   # v6: whoosh on every cut to the home
            events.append(('whoosh', b['t0'] - 0.08, wh, 'B-roll %s "%s"' % (b['label'], b['word'])))
        events.append(('whoosh', P.card_t0 - 0.15, wh, 'end card'))
    sfx = np.zeros((n_total, 2), np.float32)
    rep = []
    for kind, t0, snd, what in events:
        i0 = max(0, int(t0 * SR))
        seg = snd[:max(0, min(len(snd), n_total - i0))]
        if not len(seg):
            continue
        act = seg[np.abs(seg).mean(1) > 0.1 * np.abs(seg).max()]
        g_db = (speech_db - SFX_UNDER) - rms_db(act)
        gain = 10 ** (g_db / 20.0)
        # never cover a word: during words the effect stays >= 15 dB under the voice in every 20 ms window
        w2 = int(0.02 * SR)
        worst = -99.0
        for _ in range(6):
            worst = -99.0
            for j in range(0, len(seg) - w2, w2):
                a, b = i0 + j, i0 + j + w2
                if not in_word[a:b].any():
                    continue
                d = rms_db(seg[j:j + w2] * gain) - rms_db(voice[a:b] if b <= len(voice) else voice[-w2:])
                worst = max(worst, d)
            if worst <= -15.0:
                break
            gain *= 10 ** ((-15.0 - worst - 0.5) / 20.0)
        sfx[i0:i0 + len(seg)] += seg * gain
        rep.append((kind, t0, what, 20 * np.log10(np.abs(seg * gain).max() + 1e-9), worst))
    mix += sfx
    raw = os.path.join(work, 'mix_raw.wav')
    write_wav(raw, mix)
    _, err = run(['ffmpeg', '-hide_banner', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json',
                  '-f', 'null', '-'])
    m = json.loads(err[err.rfind('{'):err.rfind('}') + 1])
    ln = ('loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:'
          'offset=%s:linear=true' % (m['input_i'], m['input_tp'], m['input_lra'], m['input_thresh'],
                                     m['target_offset']))
    run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', ln + ',aresample=48000,apad=whole_dur=%.4f' % P.total,
         '-t', '%.4f' % P.total, '-c:a', 'pcm_s16le', '-ar', '48000', '-ac', '2', out_wav])
    _, err = run(['ffmpeg', '-hide_banner', '-i', out_wav, '-af', 'ebur128', '-f', 'null', '-'])
    mm = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)
    lufs = float(mm[-1]) if mm else None
    stats['sfx'] = rep
    stats['voice_peak'] = voice_peak
    stats['speech_db'] = speech_db
    stats['sfx_peak'] = 20 * np.log10(np.abs(sfx).max() + 1e-9) if events else None
    return lufs


def mux(video, wav, out, total):
    run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
         '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', '-t', '%.4f' % total,
         os.path.abspath(out)])


# ------------------------------------------------------------------ post-render check
def post_render_check(P, final):
    det = FaceDet((540, 960))
    problems = []
    for i, c in enumerate(P.caps):
        if any(b['t0'] <= (c['t0'] + c['t1']) / 2 < b['t1'] for b in P.bigwords):
            continue
        for t in (c['t0'] + 0.15, (c['t0'] + c['t1']) / 2):
            fr = grab(final, t, (540, 960))
            if fr is None:
                continue
            f = det.detect(fr)
            if f and rect_hit(c['box_rect'], (f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h'])):
                problems.append(('caption', i, f['y'] + f['h']))
                break
    for gi, g in enumerate(P.visuals):
        tm = (g['t0'] + g['t1']) / 2
        fr = grab(final, tm, (540, 960))
        if fr is not None:
            f = det.detect(fr)
            if f and rect_hit(vis_rect(g, tm), (f['x'], f['y'] - 0.35 * f['h'], f['x'] + f['w'], f['y'] + f['h']), 8):
                problems.append(('visual', gi, f['y']))
    return problems


# ------------------------------------------------------------------ v7 self-check
def v7_checks(P, final, stats, line, log):
    fpsf = float(P.fps)
    log('    --- v7 NEXT LEVEL ---')
    if getattr(P, 'kh_on', False):
        f0, f1, f13 = grab(final, 0.0), grab(final, 1 / fpsf - 0.002), grab(final, (KH_F + 3) / fpsf - 0.002)
        y0, y1 = int(0.30 * H), int(0.75 * H)                          # picture area below the hook title
        lv = lambda im: float(cv2.Laplacian(cv2.cvtColor(im[y0:y1], cv2.COLOR_BGR2GRAY), cv2.CV_64F).var())
        mb = lambda im: float(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).mean())
        sh0, sh1, b0, b1 = lv(f0), lv(f1), mb(f0), mb(f13)
        line(sh0 > sh1 and b0 <= 1.06 * b1,
             'kinetic hook: frame 0 (cover) clean - sharper than the motion-blurred frame 1 (%.0f vs %.0f), '
             'brightness %.0f vs %.0f later (no flash); 115%% -> 100%% in %d frames, zoom blur on frames 1-%d'
             % (sh0, sh1, b0, b1, KH_F, KH_F - 1))
        if P.hb:
            ws = P.hb['words']
            line(all(b['start'] - a['start'] == KH_STEP for a, b in zip(ws[1:-1], ws[2:])),
                 'kinetic hook: %d words pop in 60->105->100%% (%s), 3 frames apart, behind his head; '
                 'whole title in by frame %d (%.2fs) - cover image written' % (
                     len(ws), ' '.join(w['text'] for w in ws), P.hb['landed_f'], P.hb['landed_f'] / fpsf))
    if P.opt.transitions:
        trs = P.transitions
        types = [tr['type'] for tr in trs]
        same = [i for i in range(1, len(types)) if types[i] == types[i - 1]]
        line(trs and not same, 'transitions: %d (%s) - never two of the same in a row' % (len(trs), ' > '.join(types)))
        need = [x for b in P.broll for x in (b['t0'], b['t1'])]
        miss = [x for x in need if not any(abs(x - tr['t']) < 1e-3 for tr in trs)]
        line(not miss, 'transitions on every B-roll in/out (%d of %d)' % (len(need) - len(miss), len(need)))
        cta0 = min(cta_start(P), P.speech_end)
        bad = [tr['t'] for tr in trs if tr['t'] < P.hook_t1 or tr['t'] + tr['D'] / 2.0 / fpsf > cta0 + 0.12]
        line(not bad, 'no transition in the hook, the call to action (from %.2fs) or the end card%s'
             % (cta0, (': %s' % bad) if bad else ''))
        nwh = len([r for r in stats.get('sfx', []) if r[2].startswith('transition')])
        line(nwh == len(trs), 'each transition has a whoosh (%d/%d)' % (nwh, len(trs)))
    if P.opt.impact and P.impacts:
        mx = max([v for _, v in stats.get('shake', [])], default=0)
        hits = [r for r in stats.get('sfx', []) if r[0] == 'hit']
        line(mx <= SHAKE_PX + 1e-6 and len(hits) == len(P.impacts),
             'impact: %d (%s) - shake max %.1f px (<= 6), decays over %d frames, soft low hit under the voice'
             % (len(P.impacts), '; '.join('%.2fs %s' % (im['t'], im['why']) for im in P.impacts), mx, SHAKE_F))
    if P.opt.kinetic_captions:
        log('    [INFO] kinetic captions: %d phrases, every word pops 90->108->100%%, active word Orange 108%%'
            % len(P.caps))
    if P.opt.cinematic:
        log('    [INFO] cinematic look: S-curve, warm mids, cool shadows, highlight roll-off, grain %.1f%%, vignette 15%%'
            % (100 * GRAIN))
        if P.broll and getattr(P, 'talk_lab', None) is not None:
            ref = P.talk_lab[0]
            dE = lambda m: float(np.linalg.norm((m - ref) * np.array([100 / 255.0, 1, 1])))
            for b in P.broll:
                if b.get('lab_before') is not None:
                    line(dE(b['lab_after']) <= dE(b['lab_before']) + 1e-6,
                         'B-roll "%s" colour-matched to the talking shots: Lab distance %.1f -> %.1f'
                         % (b['word'], dE(b['lab_before']), dE(b['lab_after'])))
    if P.broll and P.opt.whole_room:
        for b in P.broll:
            sw = b.get('src_w') or 1
            cov = (b['x_range'][1] - b['x_range'][0]) / float(sw)
            kind = b['shot'].get('kind', 'wide')
            line(cov >= 0.98 if kind == 'wide' else True,
                 'B-roll "%s" #%02d %s (%s): %s - %d%% of the frame width shown'
                 % (b['word'], b['shot']['id'], b['label'], kind,
                    ('pan ' + ('left->right' if b['shot'].get('pan_dir', 1) > 0 else 'right->left')
                     + ' (follows the camera)') if kind == 'wide' else 'slow zoom-in', round(100 * cov)))
            pool = [s for s in P.shots if s['use'] and s['label'] in b['allowed'] and 'score10' in s]
            best = max(s['score10'] for s in pool) if pool else 0
            log('    [INFO] B-roll "%s": shot #%02d score %.1f (best of %d %s shots: %.1f)' % (
                b['word'], b['shot']['id'], b['shot'].get('score10', 0), len(pool), '/'.join(b['allowed']), best))
    if P.broll and P.opt.bubble_pop:
        gaps = [b['cap_top'] - (b['bub'][1] + (BUB_D / 2.0 + BUB_RING) * 1.10) for b in P.broll]
        sc = [x[1] for x in getattr(P, 'bub_scales', [])]
        line(min(gaps) >= BUB_GAP_CAP - 0.5 and sc and max(sc) <= 1.101 and max(sc) >= 1.09,
             'bubble: bottom-left, %d px above the captions even at 110%% (>= 60), shadow visible, pops 0->110->100%% '
             'in 8 frames (first frame %.0f%%, peak %.0f%%)' % (min(gaps), 100 * sc[0] if sc else 0,
                                                                100 * max(sc) if sc else 0))
    if P.opt.pace:
        gaps, end = pace_gaps(P, final=True)
        mg = max([g[0] for g in gaps], default=0)
        n_ev = len([1 for t, _ in pace_events(P, True) if t <= end])
        line(mg <= PACE_MAX + 0.05, 'pace: %d changes before %.2fs, longest stretch without a change %.2fs (<= 2.5 s)%s'
             % (n_ev, end, mg, (' at %.2f-%.2fs' % max(gaps)[1:]) if gaps and mg > PACE_MAX + 0.05 else ''))


# ------------------------------------------------------------------ check frames
def export_checks(P, final, outdir, stem, stats):
    os.makedirs(outdir, exist_ok=True)
    fpsf = float(P.fps)
    paths = []

    def shot(name, t):
        p = os.path.join(outdir, '%s_%s.jpg' % (stem, name))
        run(['ffmpeg', '-v', 'error', '-y', '-ss', '%.3f' % max(0.0, t), '-i', final, '-frames:v', '1', '-q:v', '2', p])
        paths.append((name, t, p))
        return p

    shot('t00.0_cover', 0.0)
    shot('t03.0', 3.0)
    shot('t03.2_glide', 3.0 + 4.0 / fpsf)                                 # mid-glide at the end of the hook
    shot('t06.0', 6.0)
    for k, g in enumerate(P.visuals):
        lab = re.sub(r'[^A-Z0-9]+', '_', g['chips'][0]['label'].upper()).strip('_')
        t = min(g['t1'] - 0.05, g['t0'] + (DRAW_F + 0.5) / fpsf)          # icon + label landed
        shot('visual%d_%s_landed' % (k + 1, lab), t)
    for k, b in enumerate(getattr(P, 'broll', [])):                       # v6: B-roll with the bubble
        wd = re.sub(r'[^a-z0-9]+', '_', b['word'].lower()).strip('_')
        shot('broll%d_%s_%s' % (k + 1, b['label'], wd), b['t0'] + min(1.0, (b['t1'] - b['t0']) / 2))
    key = [dict(t0=f[0], t1=f[1]) for f in getattr(P, 'broll_forb', []) if f[2] == 'key line'] or \
        [z for z in P.zones if z['level'] == 'KEY']
    if key:
        shot('fullscreen_key_line', (key[0]['t0'] + key[0]['t1']) / 2)
    shot('end_card_complete', P.total - 0.3)
    fk = lambda k: max(0.0, k / fpsf - 0.002)                              # exact frame k
    shot('v7_1_hook_0.00s_cover', 0.0)                                     # v7 check frames
    shot('v7_2_hook_mid_animation', fk(5))
    trs = getattr(P, 'transitions', [])
    tr = next((x for x in trs if x['type'] == 'whip'), trs[0] if trs else None)
    if tr:
        shot('v7_3_transition_%s_mid' % tr['type'], fk(tr['f'] - 1))
    if P.broll:
        b = P.broll[0]
        k0, k1 = int(math.ceil(b['t0'] * fpsf - 1e-6)), int(math.ceil(b['t1'] * fpsf - 1e-6))
        shot('v7_4_broll_pan_start', fk(k0 + 4))
        shot('v7_5_broll_pan_end', fk(k1 - 4))
        shot('v7_6_bubble', fk((k0 + k1) // 2))
    if getattr(P, 'impacts', []):
        shot('v7_7_impact', fk(P.impacts[0]['f'] + 1))
    shot('v7_8_end_card', P.total - 0.3)
    if getattr(P, 'kh_on', False) and P.hb:                                # clean cover image with the full title
        cov = os.path.join(outdir, '%s_cover.jpg' % stem)
        run(['ffmpeg', '-v', 'error', '-y', '-ss', '%.4f' % fk(max(KH_F, P.hb['landed_f']) + 2), '-i', final,
             '-frames:v', '1', '-q:v', '2', cov])
        paths.append(('cover', 0, cov))
    return paths, None


# ------------------------------------------------------------------ main
class Opt:
    pass


def load_photos(path):
    if not path:
        return {}
    data = json.load(open(path))
    if isinstance(data, dict):
        data = [dict(file=v, label=k) for k, v in data.items()]
    base = os.path.dirname(os.path.abspath(path))
    out = {}
    for d in data:
        f = d['file'] if os.path.isabs(d['file']) else os.path.join(base, d['file'])
        lab = d['label'].lower().strip()
        icon = PHOTO_ICON.get(lab) or PHOTO_ICON.get(stem(lab))
        if icon is None:
            for ph_list, ic, _, _ in VISUAL_MAP:
                if lab in ph_list or stem(lab) in [stem(p) for p in ph_list]:
                    icon = ic
                    break
        if icon and os.path.exists(f) and icon not in out:
            out[icon] = dict(file=f, label=d['label'])
    return out


def main():
    ap = argparse.ArgumentParser(description='North Realty Edit Kit ' + VERSION)
    ap.add_argument('input', nargs='?')
    ap.add_argument('--out', default=None)
    ap.add_argument('--whisper', default=os.environ.get('NR_WHISPER', 'small.en'))
    ap.add_argument('--type', default=None, choices=list(LEVELS))
    ap.add_argument('--checks', action='store_true')
    ap.add_argument('--keep-work', action='store_true')
    ap.add_argument('--photos', default=None, help='JSON list of {"file":..., "label":...}')
    ap.add_argument('--icon-sheet', default=None, help='write an image of every icon with its name')
    ap.add_argument('--footage', default=None, help='v6: property tour video = the B-roll library')
    ap.add_argument('--shots', default=None, help='v6: labelled shot list (JSON) for --footage')
    ap.add_argument('--detect-shots', default=None, help='v6: write a draft shot list (to label) for --footage')
    ap.add_argument('--shot-sheet', default=None, help='v6: contact sheet image of the shot library')
    ap.add_argument('--suffix', default='_NR_edit_' + VERSION)
    for fl, hlp in (('big-captions', 'v1-size captions, no pop'), ('text-behind', 'normal hook box instead'),
                    ('bg-pop', 'no background blur/darken'), ('big-words', 'no big keyword words'),
                    ('motion', 'no push-in / zoom-punch'), ('sfx', 'no sound effects'),
                    ('visuals', 'no spoken visuals (icons/photos)'), ('end-anim', 'static end card'),
                    ('progress', 'no progress bar'), ('hook', 'no hook title at all'),
                    ('kinetic-hook', 'v7: no 115%% zoom-in / word-by-word hook'),
                    ('transitions', 'v7: hard cuts only'), ('impact', 'v7: no shake + hit'),
                    ('kinetic-captions', 'v7: v6 phrase pop captions'), ('cinematic', 'v7: v6 grade, no grain'),
                    ('whole-room', 'v7: v6 centre-crop B-roll'), ('bubble-pop', 'v7: v6 bubble'),
                    ('pace', 'v7: no extra punch-ins for pace')):
        ap.add_argument('--no-' + fl, action='store_true', help=hlp)
    ap.add_argument('--name', default=None, help='output file name (without .mp4), default <input><suffix>')
    args = ap.parse_args()
    t_start = time.time()
    opt = Opt()
    for fl in ('big_captions', 'text_behind', 'bg_pop', 'big_words', 'motion', 'sfx', 'visuals', 'end_anim',
               'progress', 'hook', 'kinetic_hook', 'transitions', 'impact', 'kinetic_captions', 'cinematic',
               'whole_room', 'bubble_pop', 'pace'):
        setattr(opt, fl, not getattr(args, 'no_' + fl))

    if args.icon_sheet and not args.input:
        FONTS.update(setup_fonts(os.path.join(os.path.dirname(os.path.abspath(args.icon_sheet)), '.nr_cache')))
        n = icon_sheet(args.icon_sheet)
        log('icon sheet: %d icons -> %s' % (n, args.icon_sheet))
        return
    if (args.detect_shots or args.shot_sheet) and not args.input:      # v6 shot-library tools
        cache = os.path.join(os.path.dirname(os.path.abspath(args.detect_shots or args.shot_sheet)), '.nr_cache')
        FONTS.update(setup_fonts(cache))
        if args.detect_shots:
            if not args.footage:
                ap.error('--detect-shots needs --footage')
            shots, ffps, fdur = detect_shots(args.footage)
            json.dump(dict(footage=os.path.abspath(args.footage), labels=SHOT_LABELS, shots=shots),
                      open(args.detect_shots, 'w'), indent=1)
            log('shot detection: %d shots in %.1fs of footage -> %s (fill in "label", set "use": false for shots '
                'with burned-in text or a logo)' % (len(shots), fdur, args.detect_shots))
            sp = os.path.splitext(args.detect_shots)[0] + '_sheet.jpg'
            shot_sheet(args.footage, load_shots(args.detect_shots)[0], sp)
            log('contact sheet -> ' + sp)
        if args.shot_sheet:
            shots, foot = load_shots(args.shots, args.footage)
            shot_sheet(foot, shots, args.shot_sheet)
            log('contact sheet -> ' + args.shot_sheet)
        return
    if not args.input:
        ap.error('input clip required')
    src = os.path.abspath(args.input)
    stem_ = os.path.splitext(os.path.basename(src))[0]
    outdir = os.path.abspath(args.out or os.path.dirname(src))
    os.makedirs(outdir, exist_ok=True)
    work = os.path.join(outdir, stem_ + '_nr_work')
    os.makedirs(work, exist_ok=True)
    final = os.path.join(outdir, (args.name or (stem_ + args.suffix)) + '.mp4')
    stem_ = args.name or stem_
    P = Plan()
    P.opt = opt
    P.capcache = {}

    log('=' * 70 + '\nNORTH REALTY EDIT KIT %s  -  %s' % (VERSION, os.path.basename(src)))
    fonts = setup_fonts(os.path.join(outdir, '.nr_cache'))
    FONTS.update(fonts)
    log('font: ' + fonts['source'])
    if args.icon_sheet:
        icon_sheet(args.icon_sheet)
    P.photos = load_photos(args.photos) if (args.photos and opt.visuals) else {}
    if args.photos:
        log('photos: ' + (', '.join('%s -> %s' % (v['label'], k) for k, v in P.photos.items()) or 'none usable'))
    P.shots, P.footage, P.broll, P.broll_log, P.icon_moves = [], None, [], [], []
    P.sr, P.transitions, P.impacts, P.pace_added = None, [], [], []
    if args.footage or args.shots:                                     # v6 shot library
        if not (args.footage and args.shots):
            ap.error('--footage and --shots go together')
        P.shots, P.footage = load_shots(args.shots, args.footage)
        if not os.path.exists(P.footage):
            raise SystemExit('footage not found: %s' % P.footage)
        score_shots(P.footage, P.shots)                                 # v7 shot scores + camera direction
        P.sr, sr_note = load_sr() if opt.whole_room else (None, 'v6 crop')
        log('shot scores (0-10 = 40 % sharp + 35 % exposure + 25 % clean): ' + ', '.join(
            '#%02d %s %.1f' % (s['id'], s['label'], s['score10']) for s in P.shots if 'score10' in s))
        log('B-roll upscale: ' + sr_note)
        us = [s for s in P.shots if s['use'] and s['label']]
        log('shot library: %d shots, %d usable (%s); dropped: %s' % (
            len(P.shots), len(us), ', '.join(sorted(set(s['label'] for s in us))),
            ', '.join('#%02d %s' % (s['id'], s.get('note', '')) for s in P.shots if not s['use']) or 'none'))

    # 1 NORMALISE
    info = probe(src)
    P.fps = info['fps']
    upright = os.path.join(work, 'upright.mkv')
    mode, up = normalise(src, info, upright)
    ui = probe(upright)
    dur = ui['dur']
    log('[1] normalise: source %dx%d (rotation %d), %.3f fps -> upright 1080x1920 %s%s, %.2fs'
        % (info['w'], info['h'], info['rot'], float(info['fps']), mode,
           ' (upscaled lanczos + unsharp)' if up else '', dur))
    wav48, wav16 = os.path.join(work, 'voice48.wav'), os.path.join(work, 'voice16.wav')
    run(['ffmpeg', '-v', 'error', '-y', '-i', upright, '-vn', '-ac', '2', '-ar', '48000', wav48])
    run(['ffmpeg', '-v', 'error', '-y', '-i', upright, '-vn', '-ac', '1', '-ar', '16000', wav16])

    # 2 TRANSCRIBE
    words = transcribe(wav16, args.whisper)
    fixes = fix_brand_words(words)
    P.transcript = ' '.join(w['w'] for w in words)
    log('[2] transcript (%d words)%s:\n    %s' % (len(words), ('; brand fixes: ' + ', '.join(fixes)) if fixes else '',
                                                  P.transcript or '(no speech)'))

    # 3 CLASSIFY
    samples, motion, detkind, nfr = analyse(upright, P.fps, dur)
    P.samples, P.track = samples, FaceTrack(samples)
    ctype, why, m = classify(words, samples, dur)
    if args.type:
        ctype, why = args.type, 'forced with --type'
    P.ctype = ctype
    log('[3] TYPE = %s  (%s)\n    measured: %s  [face detector: %s, %d frames sampled]'
        % (ctype, why, ', '.join('%s=%s' % kv for kv in m.items()), detkind, len(samples)))

    # 4 CUT (+ v2: drop false starts, repeated takes, unfinished last sentence)
    env = audio_env(wav16)
    thr = refine_words(words, env)
    drop = clean_takes(words) if words else []
    drop_idx = {i for i, _ in drop}
    dropped_words = [words[i] for i in sorted(drop_idx)]
    kept = [w for i, w in enumerate(words) if i not in drop_idx]
    if drop:
        log('    dropped (not real words of the take): ' +
            '; '.join('"%s" (%s)' % (words[i]['w'], r) for i, r in drop))
    if ctype == 'WALKTHROUGH' or not kept:
        start, end, removed = plan_cuts_walkthrough(motion, P.fps, kept, dur)
    else:
        start, end, removed = plan_cuts_speech(kept, env, thr, dur, ctype, P.track, dropped_words)
    segs = to_segments(start, end, removed, P.fps)
    P.tl = Timeline(segs, P.fps)
    for w in kept:
        w['so'], w['eo'] = P.tl.s2o(w.get('rs', w['s'])), P.tl.s2o(w.get('re', w['e']))
    P.words = kept
    P.sents = sentences_of(kept) if kept else []
    P.speech_end = P.tl.dur
    P.n_cuts = len(segs) - 1
    P.last_complete = sentence_complete(kept, P.sents[-1]) if P.sents else True
    log('[4] cut: %d pauses/breaths removed, kept %d pieces, %.2fs -> %.2fs (+%.1fs end card)'
        % (len([r for r in removed if r[1] - r[0] > 1 / float(P.fps)]), len(segs), dur, P.tl.dur, END_DUR))
    if P.sents:
        log('    last sentence: "%s" -> %s' % (' '.join(kept[k]['w'] for k in P.sents[-1]),
                                               'complete' if P.last_complete else 'INCOMPLETE'))

    # 5-8 PLAN
    P.key_sent = None
    if P.sents:
        cta = [i for i, s in enumerate(P.sents) if CTA_RE.search(' '.join(kept[k]['w'] for k in s))]
        num = [i for i, s in enumerate(P.sents) if any(re.search(r'\d|\$|%', kept[k]['w']) for k in s)]
        P.key_sent = cta[-1] if cta else (num[0] if num else len(P.sents) - 1)
        if P.key_sent == 0 and len(P.sents) > 1:
            P.key_sent = len(P.sents) - 1
    P.zones = make_zones(P)
    refresh_crops(P)
    P.cap_em = CAP_EM if opt.big_captions else CAP_EM_V1
    P.grade = make_grade(opt.cinematic)
    P.grain = make_grain() if opt.cinematic else None
    P.kh_on = bool(opt.kinetic_hook and kept and ctype != 'WALKTHROUGH')
    P.talk_lab = talk_reference(upright, dur) if (P.shots and opt.cinematic) else None
    # hook
    P.hook_on = bool(opt.hook and kept)
    P.hook_t0, P.hook_t1 = HOOK_T0, min(HOOK_T1, P.speech_end)
    P.hb, P.hookbox = None, None
    if P.hook_on:
        if ctype == 'WALKTHROUGH':
            pg = [c for c in find_numbers(P) if c['money']]
            ht = (compact_money(pg[0]['val'], pg[0]['txt']) if pg else None)
            P.hook_on = bool(ht)
        else:
            ht = make_hook_text(P)
        if P.hook_on and opt.text_behind and ctype != 'WALKTHROUGH' and any(s['face'] for s in samples):
            hb = make_hook_behind_text(P)
            if hb:
                P.hb = build_hook_behind(P, hb)
                P.hb['want_head'] = TOPMIN + 0.86 * P.hb['block_h']
                place_hook_behind(P.hb, TOPMIN)
        if P.hook_on and ht:
            P.hookbox = layout_hook_box(P, ht) or layout_hook_box(P, ' '.join(ht.split()[:4]))
        if P.hook_on and not P.hb and not P.hookbox:
            P.hook_on = False
    # v6: B-roll of the real home first (it wins over icons), then spoken visuals, big words, punches
    if P.shots:
        if ctype == 'WALKTHROUGH' or not kept:
            log('    footage given, but this is a WALKTHROUGH clip without talk - v5 WALKTHROUGH behaviour, no B-roll')
        else:
            schedule_broll(P)
    P.visuals = schedule_visuals(P)
    P.bigwords = choose_big_words(P)
    trim_for_bigwords(P)
    for b in P.bigwords:
        em = BIG_MAX
        while em > BIG_MIN and tw('blk', b['text'], em) > 0.84 * W:
            em -= 4
        b['em'] = em
        b['sprite'] = text_sprite(b['runs'], 'blk', em, shadow=(0, 10, 16, 0.75, NAVY),
                                  stroke=(max(4, int(round(em * 0.045))), NAVY))
    for g in P.visuals:
        layout_group(P, g)
    P.punches = sorted([b['t0'] for b in P.bigwords] + [g['t0'] for g in P.visuals])
    for g in P.visuals:                                     # photo: move him down so his head sits under the card
        if g.get('photo'):
            g['person_dy'] = 0.0
    P.widened = force_wide_for_visuals(P)
    dropped_vis = solve_headroom(P)
    plan_pace(P)                                            # v7: a change every 1.5-2.5 s
    if getattr(P, 'pace_added', None):
        log('    pace: added punch-in cuts at ' + ', '.join('%.2fs (%d%%)' % x for x in P.pace_added))
    for g in P.visuals:
        if g.get('photo'):
            z = zone_at(P, g['t0'])
            g['person_dy'] = max(0.0, (0.45 * H + 50) - z['anchor'][1])
    # big word placement (where the caption would be - below the chin)
    for b in list(P.bigwords):
        fs = faces_out(P, b['t0'], b['t1'], 0.04)
        fb = max([f[3] for _, f in fs], default=0.0)
        spr, inf = b['sprite']
        while True:
            hh = inf['cap_h'] * 1.0
            top = max(fb + 46, CAP_MIN_Y - 60)
            if top + hh * 1.05 <= CAP_MAX_Y or b['em'] <= BIG_MIN:
                break
            b['em'] -= 10
            b['sprite'] = text_sprite(b['runs'], 'blk', b['em'], shadow=(0, 10, 16, 0.75, NAVY),
                                      stroke=(max(4, int(round(b['em'] * 0.045))), NAVY))
            spr, inf = b['sprite']
        top = min(top, CAP_MAX_Y - hh * 1.05)
        b['cx'], b['cy'] = CAP_CX, top + hh / 2
        b['rect'] = (CAP_CX - inf['text_w'] / 2 * 1.35, b['cy'] - hh / 2 * 1.35, CAP_CX + inf['text_w'] / 2 * 1.35,
                     b['cy'] + hh / 2 * 1.35)
        if any(rect_hit((b['rect'][0], b['cy'] - hh / 2, b['rect'][2], b['cy'] + hh / 2), f) for _, f in fs):
            P.bigwords.remove(b)
            log('    (big word "%s" dropped: no room under the chin)' % b['text'])
    P.punches = sorted([b['t0'] for b in P.bigwords] + [g['t0'] for g in P.visuals])
    hs = best_headshot(P, upright)
    P.headshot, P.headshot_t = (hs if hs else (None, None))
    # text-behind-head: segment the hook frames, keep >= 60 % readable or fall back to the hook box
    P.hb_note = ''
    if P.hb is not None:
        res, why_ = hook_prepass(P, upright)
        if res is None:
            P.hb_note = 'text-behind-head fallback to the hook box: ' + why_
            log('    ' + P.hb_note)
            P.hb = None
            solve_headroom(P)
        else:
            P.hb['plan_vis'] = res
    place_visuals(P)
    P.caps = layout_captions(P) if kept else []
    plan_bubbles(P)

    log('[5] punch-ins: ' + '  '.join('%.1f-%.1fs %s %d%%%s' % (z['t0'], z['t1'], z['level'], round(z['z'] * 100),
                                                                ' +%dpx headroom' % z['shift'] if z['shift'] else '')
                                       for z in P.zones))
    log('    motion: %s' % ('push-in 100->104%% in every shot, %d zoom-punches (+8%%)' % len(P.punches)
                            if opt.motion else 'off'))
    log('[6] captions: %d phrases (2-4 words), Montserrat Black %dpx em (cap height %dpx), pop 85->105->100%%, '
        'karaoke orange' % (len(P.caps), P.cap_em, cap_h('blk', P.cap_em)))
    log('[7] spoken visuals (HERO): ' + ('; '.join('%.1f-%.1fs %s' % (g['t0'], g['t1'], ' + '.join(
        '%s"%s"->%s "%s"' % (('photo ' if g.get('photo') else ''), c['word'], c['icon'], c['label']) for c in g['chips']))
        for g in P.visuals) or 'none') + (('  (dropped, no room: %s)' % ', '.join(dropped_vis)) if dropped_vis else ''))
    if P.widened:
        log('    wide shot kept during: %s (no room beside his head in the zoomed shot)' % ', '.join(P.widened))
    log('    big words: ' + (', '.join('"%s" %.1f-%.1fs' % (b['text'], b['t0'], b['t1']) for b in P.bigwords) or 'none'))
    if P.shots:
        log('[7b] B-roll of the home: ' + ('; '.join('%.1f-%.1fs "%s" -> shot #%02d %s (%d%% speed)' % (
            b['t0'], b['t1'], b['word'], b['shot']['id'], b['label'], round(100 * b['speed'])) for b in P.broll)
            or 'none'))
        for t, w, what in sorted(P.broll_log):
            log('      %5.2fs "%s": %s' % (t, w, what))
        for lab, t, nt in P.icon_moves:
            log('      icon "%s" at %.2fs meets a B-roll -> %s' % (lab, t, ('moved to %.2fs (said again)' % nt)
                                                                    if nt is not None else 'dropped'))
    if P.hook_on:
        if P.hb:
            log('[8] hook BEHIND the head: "%s" (%s) %dpx, top %dpx, planned: letters readable %d%%, worst letter '
                '%d%% visible, pixels %d%%' % (P.hb['text'], ' / '.join(P.hb['lines']), P.hb['em'], P.hb['top'],
                                              round(P.hb['plan_vis'][3] * 100), round(P.hb['plan_vis'][4] * 100),
                                              round(P.hb['plan_vis'][1] * 100)))
        else:
            log('[8] hook box: "%s"' % (P.hookbox['text'] if P.hookbox else '-'))

    # pre-render self-check + fixes
    for attempt in range(3):
        checks = self_check(P)
        bad = [c for c in checks if not c[0]]
        if not bad:
            break
        log('    self-check found %d problem(s) - re-planning:' % len(bad))
        for _, msg in bad:
            log('      x ' + msg)
        for c in P.caps:
            if any(rect_hit(c['box_rect'], f) for _, f in c['faces']):
                for z in P.zones:
                    if z['t0'] < c['t1'] and z['t1'] > c['t0'] and z['z'] > 1.0:
                        z['z'], z['level'] = 1.0, 'WIDE'
        refresh_crops(P)
        solve_headroom(P)
        place_visuals(P)
        for c in P.caps:
            place_caption(P, c)
        plan_bubbles(P)

    plan_transitions(P)                                     # v7
    plan_impacts(P)
    log('[9] transitions: ' + ('; '.join('%.2fs %s %df (%s)' % (tr['t'], tr['type'], tr['D'], tr['why'])
                                         for tr in P.transitions) or 'none'))
    log('    impacts: ' + ('; '.join('%.2fs %s' % (im['t'], im['why']) for im in P.impacts) or 'none'))

    # RENDER
    vid = os.path.join(work, 'video.mp4')
    wav = os.path.join(work, 'mix.wav')
    t_r = time.time()
    for attempt in range(1, 3):
        stats = dict(frames=0, hb_vis=[], hb_letters=[], hb_worst=[], vis_rects=[], cap_frames=0, cover=0.0,
                     bub_rects=[], icon_in_broll=[], broll_frames=0)
        P.card_t0 = P.tl.dur
        render(P, upright, vid, stats)
        P.card_t0 = P.card_t0_real
        lufs = build_audio(P, wav48, wav, work, stats)
        mux(vid, wav, final, P.total)
        problems = post_render_check(P, final)
        if problems and attempt < 2:
            log('    rendered-frame check found %d problem(s) - fixing and re-rendering' % len(problems))
            for kind, i, fb in problems:
                if kind == 'caption':
                    place_caption(P, P.caps[i], extra_drop=max(0, fb + 40 - P.caps[i]['box_rect'][1]))
                else:
                    P.visuals.pop(i)
            plan_bubbles(P)
            P.capcache = {}
            continue
        break
    render_s = time.time() - t_r

    # 12 SELF-CHECK REPORT
    oi = probe(final)
    log('\n[12] SELF-CHECK')
    log('    type detected: %s' % P.ctype)
    log('    duration: before %.2fs -> after %.2fs (speech %.2fs + end card %.1fs)' % (dur, oi['dur'], P.card_t0,
                                                                                    END_DUR))
    log('    cuts: %d (pauses/breaths > %.2fs removed, %.2fs padding, %dms audio fades); dropped words: %d'
        % (P.n_cuts, MIN_PAUSE, PAD, AFADE * 1000, len(drop)))
    ok_all = True

    def line(ok, msg):
        nonlocal ok_all
        ok_all &= bool(ok)
        log('    [%s] %s' % ('PASS' if ok else 'FAIL', msg))

    line(lufs is not None and abs(lufs - (-14)) <= 1.0, 'loudness %.1f LUFS (target -14)' % (lufs or 0))
    for ok, msg in checks:
        line(ok, msg)
    line(P.last_complete, 'last sentence complete: "%s"' % (' '.join(P.words[k]['w'] for k in P.sents[-1])
                                                           if P.sents else ''))
    if P.hb:
        v, lr, wl = stats['hb_vis'], stats['hb_letters'], stats['hb_worst']
        line(v and min(v) >= 0.60, 'text behind head "%s": pixels readable min %d%% / mean %d%% over %d frames (>= 60%%)'
             % (P.hb['text'], round(100 * min(v)) if v else 0, round(100 * np.mean(v)) if v else 0, len(v)))
        line(lr and min(lr) >= 0.80, 'text behind head: letters readable (>= 60%% of the letter visible) min %d%% '
             '(>= 80%%); worst single letter %d%% visible' % (round(100 * min(lr)) if lr else 0,
                                                            round(100 * min(wl)) if wl else 0))
        hf = stats['hook_flicker']
        line(hf and max(hf) < 0.035, 'mask flicker (hook): mean %.4f, max %.4f mask change per frame (< 0.035)'
             % (np.mean(hf) if hf else 0, max(hf) if hf else 0))
    elif P.hook_on:
        log('    [INFO] hook shown as a box%s' % ((' - ' + P.hb_note) if P.hb_note else ''))
    fl = stats['flicker']
    if fl:
        line(np.percentile(fl, 95) < 0.035, 'mask flicker (whole reel, %s): mean %.4f, p95 %.4f (< 0.035)'
             % (P.seg_kind, float(np.mean(fl)), float(np.percentile(fl, 95))))
    # visuals vs face, every frame
    vgap, capx, bwx, hkx = 1e9, [], [], []
    hook_r = P.hb['rect'] if P.hb else (P.hookbox['rect'] if (P.hook_on and P.hookbox) else None)
    for t, u, gi in stats['vis_rects']:
        f = face_out(P, t)
        if f:
            fb = (f[0], head_top(f), f[2], f[3])
            dx = max(fb[0] - u[2], u[0] - fb[2], 0)
            dy = max(fb[1] - u[3], u[1] - fb[3], 0)
            vgap = min(vgap, math.hypot(dx, dy) if (dx or dy) else -1)
        for c in P.caps:
            if c['t0'] <= t < c['t1'] and not any(b['t0'] <= t < b['t1'] for b in P.bigwords) and rect_hit(u, c['box_rect']):
                capx.append((round(t, 2), c['text']))
        for b in P.bigwords:
            if b['t0'] <= t < b['t1'] and rect_hit(u, b['rect']):
                bwx.append((round(t, 2), b['text']))
        if hook_r and P.hook_t0 <= t < P.hook_t1 and rect_hit(u, hook_r):
            hkx.append(round(t, 2))
    if stats['vis_rects']:
        line(vgap >= 15, 'spoken visuals never touch the face: closest %dpx from the head (every frame, motion included)'
             % vgap)
        line(not capx and not bwx and not hkx, 'spoken visuals never overlap a caption, the hook or a big word '
             '(every frame)%s' % ('' if not (capx or bwx or hkx) else ': %s %s %s' % (capx[:3], bwx[:3], hkx[:3])))
    fpsf_ = float(P.fps)
    sh = [z for z in P.zones if z['shift'] > 0.5 and z['t1'] > P.hook_t1 + 0.05]
    if P.hook_on:
        jumps = []
        for k in range(1, HOOK_EASE + 2):
            ta, tb = P.hook_t1 + (k - 2) / fpsf_, P.hook_t1 + (k - 1) / fpsf_
            fa_, fb_ = face_out(P, ta), face_out(P, tb)
            if fa_ and fb_:
                jumps.append(abs(fb_[1] - fa_[1]))
        line(jumps and max(jumps) < 60, 'end of hook (%.1fs): reframing glides over %d frames, biggest step %dpx per frame '
             '(no hard cut)' % (P.hook_t1, HOOK_EASE, max(jumps) if jumps else -1))
    line(not sh, 'no blurred band: Umesh is never moved down for a visual (headroom only under the hook title, '
         '0-%.1fs)' % P.hook_t1 if P.hook_on else 'no blurred band')
    if P.hook_on and not getattr(P, 'kh_on', False):
        line(stats['cover'] >= 0.999, 'frame 0.00s = cover: hook title fully visible from the first frame (alpha %.2f)'
             % stats['cover'])
    card_done = max(st + du for _, st, du, _ in END_ANIM) if opt.end_anim else 0.0
    line(END_DUR - card_done >= 2.0 - 1e-6, 'end card complete from %.2fs and held %.1fs (>= 2.0 s)'
         % (P.card_t0 + card_done, END_DUR - card_done))
    caps_ok = all(ok for ok, msg in checks if msg.startswith('caption') and 'face' in msg)
    line(caps_ok, 'captions never on the face (%d captions, overshoot included)' % len(P.caps))
    if P.shots and P.broll:                                                  # v6 B-roll checks
        log('    B-ROLL TABLE (time, spoken word, shot shown, allowed labels):')
        log('      %-13s %-26s %-20s %-6s %-18s %s' % ('time', 'word', 'shot label', 'score', 'allowed', 'match'))
        for b in P.broll:
            ok = b['label'] in b['allowed']
            log('      %5.2f-%5.2fs %-26s #%02d %-16s %-6s %-18s %s' % (
                b['t0'], b['t1'], '"%s" @%.2fs' % (b['word'], b['t']), b['shot']['id'], b['label'],
                '%.1f' % b['shot'].get('score10', b['shot'].get('score', 0)), '/'.join(b['allowed']),
                'OK' if ok else 'WRONG ROOM'))
        for b in P.broll:
            line(b['label'] in b['allowed'] and b['shot']['use'],
                 'B-roll "%s" -> shot #%02d labelled %s (allowed: %s; usable shot, no text/logo)'
                 % (b['word'], b['shot']['id'], b['label'], '/'.join(b['allowed'])))
            line(BR_MIN - 1e-6 <= b['t1'] - b['t0'] <= BR_MAX + 1e-6 and abs(b['t0'] - b['t']) <= 0.2 + 1e-6,
                 'B-roll "%s" %.2f-%.2fs: %.2fs long (1.5-3 s), starts %+.2fs from the word, shot at %d%% speed'
                 % (b['word'], b['t0'], b['t1'], b['t1'] - b['t0'], b['t0'] - b['t'], round(100 * b['speed'])))
            hit = [f[2] for f in P.broll_forb if b['t0'] < f[1] and b['t1'] > f[0]]
            line(not hit and b['t1'] <= P.card_t0 + 1e-6,
                 'B-roll "%s" not in the hook (0-%.1fs), key line, call to action or end card (from %.2fs)%s'
                 % (b['word'], P.hook_t1, P.card_t0, (': in ' + ', '.join(hit)) if hit else ''))
        st = [b['t0'] for b in P.broll]
        gaps = [b2['t0'] - b1['t1'] for b1, b2 in zip(P.broll[:-1], P.broll[1:])]
        line(all(y - x >= BR_EVERY - 1e-6 for x, y in zip(st[:-1], st[1:])) and all(g >= BR_GAP - 1e-6 for g in gaps),
             'B-roll at most one every %.0f s (starts %s; full-screen Umesh between them %s)'
             % (BR_EVERY, ', '.join('%.2f' % x for x in st), ', '.join('%.1fs' % g for g in gaps) or '-'))
        br_rects = [r for _, r, _ in stats['bub_rects'] if r]
        capx = []
        for t, r, bi in stats['bub_rects']:
            for c in P.caps:
                if r and c['t0'] <= t < c['t1'] and rect_hit(r, c['box_rect']):
                    capx.append((round(t, 2), c['text']))
        lowest = max([r[3] for r in br_rects], default=0)
        line(not capx, 'bubble never covers a caption (%d frames checked, pop-in included; bubble bottom <= %dpx, '
             'caption tops >= %dpx)%s' % (len(stats['bub_rects']), lowest,
                                          min([c['box_rect'][1] for c in P.caps if broll_overlaps(P, c['t0'], c['t1'])],
                                              default=0), (': ' + str(capx[:3])) if capx else ''))
        line(abs(BUB_D / float(W) - 0.32) < 0.01 and all(r[0] >= 0 and r[1] >= TOP_SAFE for r in br_rects),
             'bubble %dpx = %d%% of the width + %dpx white ring, bottom-left (x %d-%dpx), inside the frame'
             % (BUB_D, round(100 * BUB_D / W), BUB_RING, min(r[0] for r in br_rects), max(r[2] for r in br_rects)))
        line(not stats['icon_in_broll'], 'no icon or big word during a B-roll (every frame)%s'
             % ((': ' + str(stats['icon_in_broll'][:5])) if stats['icon_in_broll'] else ''))
        fd = FaceDet((320, 320))
        seen, tot = 0, 0
        for b in P.broll:
            cx, cy = b['bub']
            R_ = BUB_D / 2 + BUB_RING
            for u in (0.4, 0.5, 0.65, 0.8):
                tt = b['t0'] + (b['t1'] - b['t0']) * u
                fr = grab(final, tt, (W, H))
                if fr is None:
                    continue
                tot += 1
                crop = fr[int(cy - R_):int(cy + R_), int(cx - R_):int(cx + R_)]
                f = fd.detect(cv2.resize(crop, (320, 320)))
                if f and f.get('lm'):
                    mx = [(p[0] * 320 / W, p[1] * 320 / H) for p in f['lm'][3:5]]
                    if all(math.hypot(x - 160, y - 160) < 150 for x, y in mx):
                        seen += 1
        line(tot and seen >= 0.75 * tot, 'bubble shows his face with the mouth inside the circle in %d of %d sampled '
             'B-roll frames (rendered video re-scanned)' % (seen, tot))
        bf = stats.get('bub_flicker', [])
        if bf:
            line(np.percentile(bf, 95) < 0.035, 'bubble mask flicker: p95 %.4f (< 0.035)' % float(np.percentile(bf, 95)))
    elif P.shots:
        log('    [INFO] footage given but no B-roll used (%s)' % ('walkthrough clip' if P.ctype == 'WALKTHROUGH'
                                                                  else 'no spoken word matched a usable shot'))
    if P.opt.sfx:
        sp, vp = stats['sfx_peak'], stats['voice_peak']
        line(sp is not None and sp <= vp - 12, 'SFX peak %.1f dBFS vs voice peak %.1f dBFS (%.1f dB under; RMS set %d dB '
             'under speech)' % (sp or -99, vp, vp - (sp or -99), SFX_UNDER))
        worst = max([r[4] for r in stats['sfx']], default=-99)
        line(worst <= -14.9, 'SFX never cover a word: loudest SFX/voice during words %.1f dB (<= -15)' % worst)
    v7_checks(P, final, stats, line, log)
    bl = P.blitter
    line(not bl.top_hits, 'nothing in the top %dpx except the progress bar (topmost overlay pixel y=%d)'
         % (TOP_SAFE, bl.min_y if bl.min_y < 1e8 else -1))
    pr = post_render_check(P, final)
    line(not pr, 'rendered frames re-scanned for faces: %s' % ('no text on the face' if not pr else pr))
    rc = P.card_rects
    clean = all(not rect_hit(rc[a], rc[b]) for a, b in (('brand', 'tagline'), ('tagline', 'headshot'),
                                                         ('brand', 'headshot')))
    clean &= all(0 <= r[0] and r[2] <= W and r[3] <= CAP_MAX_Y for r in rc.values())
    line(clean, 'end card %s: %.2f-%.2fs, elements inside frame, above 75%%, not overlapping, no captions'
         % ('animated' if opt.end_anim else 'static', P.card_t0, P.total))
    line(render_s < 600, 'render time %.0fs for %.1fs of video (< 10 min)' % (render_s, oi['dur']))
    log('    output: %s  %dx%d  %.2fs  H.264 CRF18 + AAC 192k' % (os.path.basename(final), W, H, oi['dur']))
    log('    ALL CHECKS ' + ('PASSED' if ok_all else 'NOT ALL PASSED - see above'))
    log('\n    SPOKEN VISUALS (word spoken at, label fully readable at, shown until, icon, label):')
    for g in P.visuals:
        c = g['chips'][0]
        log('      spoken %5.2fs  readable %5.2fs (%+.2fs)  until %5.2fs  "%s"  ->  %s%s  "%s"  [%s%s]' % (
            c['t'], g['t0'] + LABEL_F / fpsf_, g['t0'] + LABEL_F / fpsf_ - c['t'], g['t1'], c['word'],
            'PHOTO ' if g.get('photo') else '', c['icon'], c['label'],
            g.get('mode', 'photo card'), ', cross-fade' if g.get('xfade') else ''))
    for b in P.bigwords:
        log('      spoken %5.2fs  shown %5.2f-%5.2fs  "%s"  ->  BIG WORD' % (b['t0'] + 0.05, b['t0'], b['t1'], b['text']))
    if args.checks:
        paths, sheet = export_checks(P, final, outdir, stem_, stats)
        log('    check frames: ' + ', '.join('%s @%.2fs' % (n, t) for n, t, _ in paths))
    json.dump(dict(version=VERSION, type=P.ctype, metrics=m, transcript=P.transcript, dropped=[(words[i]['w'], r) for i, r in drop],
                   cuts=P.n_cuts, duration_in=dur, duration_out=oi['dur'], lufs=lufs,
                   hook=(P.hb['text'] if P.hb else (P.hookbox['text'] if P.hookbox else None)),
                   big_words=[(b['text'], round(b['t0'], 2)) for b in P.bigwords],
                   visuals=[(round(g['t0'], 2), round(g['t1'], 2), round(g['chips'][0]['t'], 2), g['chips'][0]['word'],
                             g['chips'][0]['icon'], g['chips'][0]['label']) for g in P.visuals],
                   zones=[(round(z['t0'], 2), round(z['t1'], 2), z['level'], z['z'], z['shift']) for z in P.zones],
                   broll=[dict(t0=round(b['t0'], 2), t1=round(b['t1'], 2), word=b['word'], said=round(b['t'], 2),
                               shot=b['shot']['id'], label=b['label'], allowed=b['allowed'],
                               speed=round(b['speed'], 2)) for b in P.broll],
                   icon_moves=P.icon_moves,
                   transitions=[(round(tr['t'], 2), tr['type'], tr['why']) for tr in P.transitions],
                   impacts=[(round(im['t'], 2), im['why']) for im in P.impacts], pace_added=P.pace_added,
                   shot_scores=[dict(id=s['id'], label=s['label'], score=s.get('score10'), q=s.get('q'),
                                     kind=s.get('kind'), pan_dir=s.get('pan_dir')) for s in P.shots]),
              open(os.path.join(outdir, stem_ + '_NR_report.json'), 'w'), indent=1)
    if not args.keep_work:
        shutil.rmtree(work, ignore_errors=True)
    log('done in %.0fs -> %s' % (time.time() - t_start, final))


if __name__ == '__main__':
    main()
