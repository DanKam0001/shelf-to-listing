"""Isolate the item from its background -- a clean, marketplace-ready product shot."""
from PIL import Image
from rembg import new_session, remove

_SESSION = new_session("u2net")  # small, fast, well-tested -- not rembg's 1GB default model


def isolate_item(image_path: str) -> Image.Image:
    """Returns an RGBA image with the background removed, item on transparent."""
    with open(image_path, "rb") as f:
        return remove(Image.open(f), session=_SESSION)


def isolate_on_white(image_path: str) -> Image.Image:
    """Same, but flattened onto a plain white background -- what most marketplaces expect."""
    cut = isolate_item(image_path).convert("RGBA")
    bg = Image.new("RGBA", cut.size, (255, 255, 255, 255))
    bg.paste(cut, (0, 0), cut)
    return bg.convert("RGB")
