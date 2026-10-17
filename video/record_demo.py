"""Record the LIVE Shelf-to-Listing Streamlit app for the 02-demo scene: real upload, real API call, real
result -- scrolled down so the price/condition/description actually appear on screen, not just the title.
Usage: python record_demo.py photo1.jpg photo2.jpg
"""
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
WORK = HERE / "work"
WORK.mkdir(exist_ok=True)
URL = "http://localhost:8501"
W, H = 1920, 1080

photos = [Path(p).resolve() for p in sys.argv[1:]]
if not photos:
    raise SystemExit("usage: python record_demo.py photo1.jpg [photo2.jpg ...]")
for p in photos:
    if not p.exists():
        raise SystemExit(f"missing: {p}")

raw_dir = WORK / "raw_demo"
raw_dir.mkdir(exist_ok=True)
for f in raw_dir.glob("*.webm"):
    f.unlink()

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(
        viewport={"width": W, "height": H},
        record_video_dir=str(raw_dir),
        record_video_size={"width": W, "height": H},
        color_scheme="dark",
    )
    page = ctx.new_page()
    page.goto(URL)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1500)

    for i, photo in enumerate(photos):
        uploader = page.locator("input[type='file']")
        uploader.set_input_files(str(photo))
        page.wait_for_timeout(1000)
        gen_btn = page.get_by_role("button", name="Generate listing")
        gen_btn.wait_for(state="visible", timeout=10000)
        page.wait_for_timeout(250)
        gen_btn.click()
        page.get_by_text("Listing ready").wait_for(state="visible", timeout=30000)
        page.wait_for_timeout(500)  # let the title settle on screen first

        # the result (title, price/category/condition, description) renders BELOW the fold --
        # Streamlit scrolls its own [data-testid="stMain"] container, not the window, so scroll
        # THAT element. Compute the exact offset so the title sits near the top of the viewport,
        # guaranteeing the metrics row and description below it are visible too.
        title_heading = page.locator("h3").last
        title_heading.wait_for(state="visible", timeout=5000)
        box = title_heading.bounding_box()
        cur_scroll = page.eval_on_selector("[data-testid='stMain']", "el => el.scrollTop")
        target = cur_scroll + box["y"] - 130
        page.eval_on_selector("[data-testid='stMain']",
                               "(el, y) => el.scrollTo({top: y, behavior: 'instant'})", target)
        page.wait_for_timeout(2200)

        if i < len(photos) - 1:
            page.eval_on_selector("[data-testid='stMain']", "el => el.scrollTo(0, 0)")
            page.wait_for_timeout(350)
            clear_btn = page.locator("button[aria-label='Remove file']")
            if clear_btn.count():
                clear_btn.first.click()
                page.wait_for_timeout(450)

    page.wait_for_timeout(600)
    ctx.close()
    browser.close()

webm = next(raw_dir.glob("*.webm"))
out = WORK / "rec_02-demo.mp4"
subprocess.run([
    "ffmpeg", "-v", "error", "-y", "-i", str(webm),
    "-vf", f"tpad=stop_mode=clone:stop_duration=20,scale={W}:{H}:flags=lanczos,fps=30,format=yuv420p",
    "-c:v", "libx264", "-crf", "16", str(out),
], check=True)
print(f"-> {out}")
