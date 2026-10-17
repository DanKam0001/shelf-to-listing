"""Screenshot each slide HTML (headless) and assemble into slides.pdf."""
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
names = ["01-title", "02-problem", "03-solution", "04-tech", "05-who", "06-close"]

imgs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1920, "height": 1080})
    for name in names:
        page.goto((HERE / f"{name}.html").as_uri())
        page.wait_for_load_state("networkidle")
        page.evaluate("document.fonts.ready")
        png = HERE / f"{name}.png"
        page.screenshot(path=str(png))
        imgs.append(Image.open(png).convert("RGB"))
    b.close()

out = HERE.parent / "slides.pdf"
imgs[0].save(out, save_all=True, append_images=imgs[1:])
print(f"-> {out}")
