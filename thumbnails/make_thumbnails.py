"""Render 3 sample YouTube thumbnails (1280x720) for Indian tech/finance documentary-style videos.
SAMPLE / DEMO work: background photos are AI-generated stock-style images; all text/layout/grading done in Pillow.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
G = '/usr/share/fonts/truetype/sand-box/google/'
ANTON = G + 'Anton/Anton-Regular.ttf'
POP_B = G + 'Poppins/Poppins-Bold.ttf'
POP_K = G + 'Poppins/Poppins-ExtraBold.ttf'
W, H = 1280, 720
HERE = os.path.dirname(os.path.abspath(__file__))

def grade(img, warm=0.0, contrast=1.15, sat=1.1, bright=1.0):
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Color(img).enhance(sat)
    img = ImageEnhance.Brightness(img).enhance(bright)
    if warm:
        r, g, b = img.split()
        r = r.point(lambda v: min(255, int(v * (1 + warm))))
        b = b.point(lambda v: int(v * (1 - warm * 0.6)))
        img = Image.merge('RGB', (r, g, b))
    return img

def left_shade(img, strength=235, width=0.62):
    """Dark gradient from the left edge so headline text pops."""
    ov = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(ov)
    end = int(W * width)
    for x in range(end):
        a = int(strength * (1 - x / end) ** 1.4)
        d.line([(x, 0), (x, H)], fill=a)
    black = Image.new('RGB', (W, H), (5, 6, 10))
    return Image.composite(black, img, ov)

def vignette(img, strength=150):
    m = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(m)
    for i in range(60):
        a = int(strength * (1 - i / 60) ** 2)
        d.rectangle([i * 6, i * 4, W - i * 6, H - i * 4], outline=a, width=6)
    m = m.filter(ImageFilter.GaussianBlur(40))
    return Image.composite(Image.new('RGB', (W, H), 'black'), img, m)

def shadow_text(base, xy, text, font, fill, shadow=(0, 0, 0), blur=10, offset=(0, 6), stroke=0, stroke_fill=None):
    layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text((xy[0] + offset[0], xy[1] + offset[1]), text, font=font, fill=shadow + (220,), stroke_width=stroke)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)
    d = ImageDraw.Draw(base)
    d.text(xy, text, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return d.textbbox(xy, text, font=font, stroke_width=stroke)

def pill(base, xy, text, font, bg, fg, pad=(18, 8)):
    d = ImageDraw.Draw(base)
    b = d.textbbox((0, 0), text, font=font)
    w, h = b[2] - b[0], b[3] - b[1]
    x, y = xy
    d.rounded_rectangle([x, y, x + w + pad[0] * 2, y + h + pad[1] * 2 + 4], radius=8, fill=bg)
    d.text((x + pad[0] - b[0], y + pad[1] - b[1] + 2), text, font=font, fill=fg)
    return x + w + pad[0] * 2, y + h + pad[1] * 2

def sample_tag(base):
    f = ImageFont.truetype(POP_B, 16)
    d = ImageDraw.Draw(base)
    t = 'SAMPLE DESIGN'
    b = d.textbbox((0, 0), t, font=f)
    x, y = W - (b[2] - b[0]) - 34, 18
    d.rounded_rectangle([x - 10, y - 4, x + b[2] - b[0] + 10, y + b[3] - b[1] + 10], radius=6, fill=(0, 0, 0, 150))
    d.text((x, y - b[1] + 2), t, font=f, fill=(255, 255, 255, 200))

def fit(text, path, max_w, start):
    s = start
    while s > 20:
        f = ImageFont.truetype(path, s)
        if f.getbbox(text)[2] <= max_w:
            return f
        s -= 2
    return ImageFont.truetype(path, s)

def build(bg, out, kicker, kicker_bg, lines, warm=0.0, extra=None, max_w=640):
    img = Image.open(os.path.join(HERE, 'src', bg)).convert('RGB').resize((W, H), Image.LANCZOS)
    img = grade(img, warm=warm)
    img = left_shade(img)
    img = vignette(img)
    base = img.convert('RGBA')
    x = 64
    kf = ImageFont.truetype(POP_K, 26)
    _, y = pill(base, (x, 70), kicker, kf, kicker_bg, (10, 10, 10))
    y += 22
    for text, color, size, hl in lines:
        f = fit(text, ANTON, max_w, size)
        if hl:  # highlighted word on a solid colour block
            d = ImageDraw.Draw(base)
            b = d.textbbox((x, y), text, font=f)
            d.rectangle([b[0] - 14, b[1] - 10, b[2] + 14, b[3] + 12], fill=hl)
            d.text((x, y), text, font=f, fill=color)
            bb = b
        else:
            bb = shadow_text(base, (x, y), text, f, color)
        y = bb[3] + 18
    if extra:
        extra(base)
    sample_tag(base)
    base.convert('RGB').save(os.path.join(HERE, out), 'PNG', optimize=True)
    print('saved', out)

AMBER = (255, 196, 0)
if __name__ == '__main__':
    build('bg_upi.jpg', 'thumb_01_upi_story.png', 'THE ₹0 PAYMENT REVOLUTION', AMBER,
          [('HOW UPI', (255, 255, 255), 150, None),
           ('CHANGED', (255, 255, 255), 150, None),
           ('INDIA', (10, 10, 10), 150, AMBER)], warm=0.06)
    build('bg_chip.jpg', 'thumb_02_india_chip_gamble.png', 'DOCUMENTARY', (90, 200, 255),
          [("INDIA'S", (255, 255, 255), 120, None),
           ('₹76,000 CR', (90, 200, 255), 150, None),
           ('CHIP GAMBLE', (255, 255, 255), 130, None)])
    def arrow(base):
        d = ImageDraw.Draw(base)
        f = ImageFont.truetype(POP_B, 30)
        d.text((66, 610), 'Mutual funds, explained simply', font=f, fill=(210, 210, 210))
    build('bg_sip.jpg', 'thumb_03_sip_money.png', 'PERSONAL FINANCE', (0, 230, 118),
          [('WHERE DOES', (255, 255, 255), 120, None),
           ('YOUR SIP', (0, 230, 118), 160, None),
           ('MONEY GO?', (255, 255, 255), 130, None)], max_w=540)
