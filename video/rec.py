"""Record the LIVE Parity site (Render), each action on a narration word, with a caption bar."""
import json, re, shutil, subprocess, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE = Path(__file__).resolve().parent
URL = "http://localhost:8080/"  # set to the live app
VO, W, OFF = HERE / "vo", HERE / "work", 0.45
SCALE = float(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].replace(".", "").isdigit() else 4 / 3
OUTW, OUTH = int(1440 * SCALE), int(810 * SCALE)
CAP = """(() => { if (document.getElementById('vcap')) return; const c = document.createElement('div'); c.id = 'vcap';
 c.style.cssText = 'position:fixed;left:50%;bottom:34px;transform:translateX(-50%);max-width:1180px;padding:14px 26px;border-radius:14px;background:rgba(8,10,14,.9);border:1px solid #2a3346;color:#e8ecf4;font:600 26px Inter,system-ui;text-align:center;z-index:9999;opacity:0;transition:opacity .35s';
 document.body.appendChild(c); window.cap = t => { c.innerHTML = t; c.style.opacity = t ? 1 : 0; }; })()"""
SCENES = {
    # "04-demo": ("demo.scroll('#main')", [("word", "demo.glow('#thing'); cap('Caption on that word')")]),
}
norm = lambda w: re.sub(r"[^a-z0-9%$]", "", w.lower())
def cue(words, c):
    w, n = (c.split("#") + ["1"])[:2]
    hits = [x["t"] for x in words if norm(x["w"]) == w] or [x["t"] for x in words if norm(x["w"]).startswith(w)]
    if len(hits) < int(n): raise SystemExit(f"cue {c!r} missing")
    return hits[int(n) - 1]
dur = lambda p: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)
W.mkdir(exist_ok=True)
names = [a for a in sys.argv[1:] if a in SCENES] or list(SCENES)
with sync_playwright() as p:
    b = p.chromium.launch()
    for name in names:
        setup, steps = SCENES[name]
        words = json.loads((VO / f"{name}.words.json").read_text(encoding="utf-8"))
        d = OFF + dur(VO / f"{name}.mp3") + 0.7
        pg = b.new_page(viewport={"width": 1440, "height": 810}, device_scale_factor=SCALE, color_scheme="dark")
        pg.goto(URL); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(2500); pg.evaluate("document.fonts.ready")
        pg.evaluate(CAP); pg.evaluate("document.documentElement.style.scrollBehavior='auto'"); pg.evaluate(setup); pg.wait_for_timeout(1200)
        pg.evaluate("document.documentElement.style.scrollBehavior='smooth'")
        tl = "[" + ",".join(f"[{cue(words, c) + OFF:.2f}, () => {{ {js} }}]" for c, js in steps) + "]"
        pg.evaluate(f"(tl => tl.forEach(([t, f]) => setTimeout(f, t * 1000)))({tl})")
        fdir = W / f"rec_{name}"; shutil.rmtree(fdir, ignore_errors=True); fdir.mkdir()
        t0, frames = time.perf_counter(), []
        while (t := time.perf_counter() - t0) < d:
            fp = fdir / f"{len(frames):05d}.jpg"; fp.write_bytes(pg.screenshot(type="jpeg", quality=93)); frames.append((t, fp))
        with (fdir / "list.txt").open("w") as fh:
            for i, (t, fp) in enumerate(frames):
                fh.write(f"file '{fp.as_posix()}'\nduration {(frames[i + 1][0] if i + 1 < len(frames) else d) - t:.4f}\n")
            fh.write(f"file '{frames[-1][1].as_posix()}'\n")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(fdir / "list.txt"),
                        "-vf", f"fps=30,scale={OUTW}:{OUTH}:flags=lanczos,format=yuv420p", "-t", f"{d:.3f}", "-c:v", "libx264", "-crf", "16", str(W / f"rec_{name}.mp4")], check=True)
        print(f"  {name:10} {d:5.1f}s {len(frames)} frames ({len(frames) / d:.1f} fps)"); pg.close()
    b.close()
