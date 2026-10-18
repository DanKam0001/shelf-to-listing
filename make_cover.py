"""Generate cover.png for the lablab submission: warm cream card, matches the live app's palette."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 840
BG = (251, 245, 236)
PANEL = (255, 255, 255)
ACCENT = (194, 85, 31)
INK = (36, 31, 26)
MUTE = (110, 98, 85)
LINE = (232, 220, 200)

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

FONT_DIR = "C:/Windows/Fonts/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


title_f = font("georgiab.ttf", 100)
tag_f = font("segoeui.ttf", 40)
mono_f = font("consolab.ttf", 26)
badge_f = font("consolab.ttf", 24)

# camera emoji substitute: a simple rounded badge shape (emoji glyphs don't render reliably via PIL/truetype)
tag_x, tag_y = 110, 260
draw.rounded_rectangle([tag_x, tag_y, tag_x + 90, tag_y + 90], radius=22, fill=ACCENT)
draw.ellipse([tag_x + 24, tag_y + 24, tag_x + 66, tag_y + 66], fill=BG)
draw.ellipse([tag_x + 34, tag_y + 34, tag_x + 56, tag_y + 56], fill=ACCENT)

draw.text((tag_x + 115, tag_y + 2), "Snap Seller", font=title_f, fill=INK)
draw.text((tag_x + 118, tag_y + 118), "One snap. Your listing's ready.", font=tag_f, fill=MUTE)

badge_text = "BUILT ON AMD INSTINCT GPUs  ·  COMMERCE TRACK"
bbox = draw.textbbox((0, 0), badge_text, font=badge_f)
bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
bx, by = tag_x + 118, tag_y + 205
pad = 16
draw.rounded_rectangle([bx - pad, by - pad, bx + bw + pad, by + bh + pad * 2], radius=999,
                        outline=ACCENT, width=2, fill=(250, 232, 218))
draw.text((bx, by), badge_text, font=badge_f, fill=ACCENT)

draw.text((110, H - 70), "AMD Developer Hackathon: ACT III", font=mono_f, fill=MUTE)

img.save("cover.png")
print("wrote cover.png", img.size)
