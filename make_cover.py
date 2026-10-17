"""Generate cover.png for the lablab submission: dark gradient card, matches the demo video style."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 840
BG = (11, 14, 20)
ACC = (94, 234, 212)
ACC2 = (56, 189, 248)
INK = (232, 236, 244)
MUTE = (139, 149, 169)

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# radial-ish gradient approximation: vertical bands blending toward a teal glow top-right
for y in range(H):
    t = y / H
    r = int(BG[0] + (16 - BG[0]) * (1 - t) * 0.6)
    g = int(BG[1] + (32 - BG[1]) * (1 - t) * 0.6)
    b = int(BG[2] + (42 - BG[2]) * (1 - t) * 0.6)
    draw.line([(0, y), (W, y)], fill=(r, g, b))

FONT_DIR = "C:/Windows/Fonts/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


title_f = font("segoeuib.ttf", 96)
tag_f = font("segoeui.ttf", 40)
mono_f = font("consolab.ttf", 28)
badge_f = font("consolab.ttf", 24)

# tag emoji substitute: draw a simple rounded tag shape instead of relying on emoji glyph support
tag_x, tag_y = 110, 260
draw.rounded_rectangle([tag_x, tag_y, tag_x + 90, tag_y + 90], radius=22, fill=ACC)
draw.ellipse([tag_x + 58, tag_y + 18, tag_x + 76, tag_y + 36], fill=BG)

draw.text((tag_x + 115, tag_y + 2), "Shelf to Listing", font=title_f, fill=INK)
draw.text((tag_x + 118, tag_y + 115), "Photo in. Ready-to-post listing out.", font=tag_f, fill=MUTE)

badge_text = "BUILT ON AMD INSTINCT GPUs  ·  COMMERCE TRACK"
bbox = draw.textbbox((0, 0), badge_text, font=badge_f)
bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
bx, by = tag_x + 118, tag_y + 200
pad = 16
draw.rounded_rectangle([bx - pad, by - pad, bx + bw + pad, by + bh + pad * 2], radius=999,
                        outline=ACC, width=2, fill=(16, 40, 38))
draw.text((bx, by), badge_text, font=badge_f, fill=ACC)

draw.text((110, H - 70), "AMD Developer Hackathon: ACT III", font=mono_f, fill=MUTE)

img.save("cover.png")
print("wrote cover.png", img.size)
