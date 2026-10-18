"""Isolate the item from its background -- a clean, marketplace-ready product shot."""
import numpy as np
from PIL import Image
from rembg import new_session, remove

_SESSION = new_session("u2net")  # small, fast, well-tested -- not rembg's 1GB default model
_FASTSAM = None  # loaded lazily -- only needed if the user clicks points


def isolate_item(image_path: str) -> Image.Image:
    """Returns an RGBA image with the background removed, item on transparent.
    Generic saliency-based: works well when the item IS the salient subject, but on a worn/held
    item it will tend to isolate the person instead -- see isolate_from_points for that case."""
    with open(image_path, "rb") as f:
        return remove(Image.open(f), session=_SESSION)


def isolate_on_white(image_path: str) -> Image.Image:
    """Same, but flattened onto a plain white background -- what most marketplaces expect."""
    cut = isolate_item(image_path).convert("RGBA")
    bg = Image.new("RGBA", cut.size, (255, 255, 255, 255))
    bg.paste(cut, (0, 0), cut)
    return bg.convert("RGB")


def _flatten(cut: Image.Image) -> Image.Image:
    bg = Image.new("RGBA", cut.size, (255, 255, 255, 255))
    bg.paste(cut, (0, 0), cut)
    return bg.convert("RGB")


def isolate_from_points(image_path: str, points: list[tuple[int, int]]) -> tuple[Image.Image, Image.Image]:
    """Cut out just the material under the given (x, y) pixel points, via point-prompted
    segmentation (FastSAM) -- unlike isolate_item's generic saliency, this segments exactly what
    the points land on, so it works on items being worn or held: click the item, not the person.
    Returns (transparent RGBA, on-white RGB). Union of all points' masks."""
    global _FASTSAM
    if _FASTSAM is None:
        from ultralytics import FastSAM
        _FASTSAM = FastSAM("FastSAM-s.pt")

    im = Image.open(image_path).convert("RGB")
    w, h = im.size
    results = _FASTSAM(
        source=image_path,
        points=[list(p) for p in points],
        labels=[1] * len(points),
        device="cpu",
        retina_masks=True,
        imgsz=1024,
        verbose=False,
    )
    r = results[0]
    mask = np.zeros((h, w), dtype=bool)
    if r.masks is not None:
        for i in range(len(r.masks.data)):
            m = r.masks.data[i].cpu().numpy().astype(bool)
            if m.shape != (h, w):
                m = np.array(Image.fromarray((m * 255).astype("uint8")).resize((w, h))) > 127
            mask |= m

    arr = np.array(im)
    alpha = (mask * 255).astype("uint8")
    rgba = np.dstack([arr, alpha])
    cutout = Image.fromarray(rgba, mode="RGBA")
    return cutout, _flatten(cutout)
