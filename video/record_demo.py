"""Record the LIVE Shelf-to-Listing Streamlit app for the 02-demo scene: real upload, real API call, real
result -- one continuous session (fast, fits the narration window), but the brief blank-page flash that
Streamlit shows while clearing/re-uploading between items is cut out and crossfaded over in post, rather
than ever being shown on screen.
Usage: python record_demo.py photo1.jpg photo2.jpg
"""
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
WORK = HERE / "work"
WORK.mkdir(exist_ok=True)
URL = "http://localhost:8501"
W, H = 1920, 1080
XF = 0.3  # crossfade used both to bridge the cut and to match render.py's scene crossfades

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

cuts = []  # (start, end) ranges, in seconds from recording start, to EXCLUDE

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(
        viewport={"width": W, "height": H},
        record_video_dir=str(raw_dir),
        record_video_size={"width": W, "height": H},
        color_scheme="dark",
    )
    page = ctx.new_page()
    t0 = time.perf_counter()
    def mark(label):
        print(f"  t={time.perf_counter() - t0:6.2f}s  {label}", flush=True)
    page.goto(URL)
    mark("goto done")
    page.wait_for_load_state("networkidle")
    mark("networkidle")
    page.wait_for_timeout(800)
    page.locator("input[type='file']").set_input_files(str(photos[0]))
    page.wait_for_timeout(1000)
    mark("photo 0 uploaded")

    for i, photo in enumerate(photos):
        gen_btn = page.get_by_role("button", name="Generate listing")
        gen_btn.wait_for(state="visible", timeout=10000)
        page.wait_for_timeout(250)
        gen_btn.click()
        mark(f"item {i}: clicked generate")

        title_heading = page.locator("h3").first
        title_heading.wait_for(state="visible", timeout=30000)
        mark(f"item {i}: title visible (API done)")
        page.wait_for_timeout(500)
        box = title_heading.bounding_box()
        cur_scroll = page.eval_on_selector("[data-testid='stMain']", "el => el.scrollTop")
        target = cur_scroll + box["y"] - 130
        page.eval_on_selector("[data-testid='stMain']",
                               "(el, y) => el.scrollTo({top: y, behavior: 'smooth'})", target)
        page.wait_for_timeout(900)
        page.wait_for_timeout(1400 if i < len(photos) - 1 else 2200)

        if i < len(photos) - 1:
            cut_start = time.perf_counter() - t0
            page.eval_on_selector("[data-testid='stMain']", "el => el.scrollTo(0, 0)")
            clear_btn = page.locator("button[aria-label='Remove file']")
            if clear_btn.count():
                clear_btn.first.click()
            # resume recording once the NEXT photo's thumbnail is actually on screen --
            # this is what skips over Streamlit's blank rerun flash in between.
            next_uploader = page.locator("input[type='file']")
            next_uploader.set_input_files(str(photos[i + 1]))
            page.locator("img").last.wait_for(state="visible", timeout=10000)
            page.wait_for_timeout(200)
            cut_end = time.perf_counter() - t0
            cuts.append((cut_start, cut_end))
            page.wait_for_timeout(300)

    page.wait_for_timeout(600)
    ctx.close()
    browser.close()

webm = next(raw_dir.glob("*.webm"))
full = WORK / "demo_full.mp4"
subprocess.run([
    "ffmpeg", "-v", "error", "-y", "-i", str(webm),
    "-vf", f"scale={W}:{H}:flags=lanczos,fps=30,format=yuv420p",
    "-c:v", "libx264", "-crf", "16", str(full),
], check=True)


def dur(path):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True).stdout)


total = dur(full)
out = WORK / "rec_02-demo.mp4"

if not cuts:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(full),
                     "-vf", "tpad=stop_mode=clone:stop_duration=20", "-c:v", "libx264", "-crf", "16", str(out)],
                    check=True)
else:
    # build the keep-ranges (the inverse of the cut-ranges) and crossfade them together
    bounds = [0.0] + [t for c in cuts for t in c] + [total]
    keep = [(bounds[j], bounds[j + 1]) for j in range(0, len(bounds), 2)]
    segs = []
    for j, (s, e) in enumerate(keep):
        seg = WORK / f"demo_seg{j}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(full), "-ss", f"{s:.3f}", "-to", f"{e:.3f}",
                         "-c:v", "libx264", "-crf", "16", str(seg)], check=True)
        segs.append(seg)

    inputs = []
    for s in segs:
        inputs += ["-i", str(s)]
    filt, prev, off = [], "[0:v]", 0.0
    for j in range(1, len(segs)):
        off += dur(segs[j - 1]) - XF
        filt.append(f"{prev}[{j}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[v{j}]")
        prev = f"[v{j}]"
    filt.append(f"{prev}tpad=stop_mode=clone:stop_duration=20[vout]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filt),
                     "-map", "[vout]", "-c:v", "libx264", "-crf", "16", str(out)], check=True)

print(f"-> {out}")
