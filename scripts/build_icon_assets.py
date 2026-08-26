"""Rebuild icon assets from app-source, preserving transparency (no white matte)."""

from PIL import Image
from pathlib import Path

ICONS = Path(__file__).resolve().parents[1] / "src-tauri" / "icons"
PUBLIC = Path(__file__).resolve().parents[1] / "public"


def resize_rgba(src: Image.Image, size: int) -> Image.Image:
    """LANCZOS resize on RGBA; never composite onto white."""
    return src.resize((size, size), Image.Resampling.LANCZOS)


def scrub_white_fringe(im: Image.Image, ring: int = 2) -> Image.Image:
    """Remove near-white opaque fringe only; keep intentional transparent corners."""
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            near_edge = x < ring or y < ring or x >= w - ring or y >= h - ring
            if not near_edge:
                continue
            # Semi-transparent light fringe from bad mattes → make fully transparent
            if a > 0 and a < 255 and r > 200 and g > 200 and b > 200:
                px[x, y] = (0, 0, 0, 0)
            # Opaque pure-white edge pixels that shouldn't exist → transparent
            elif a == 255 and r > 250 and g > 250 and b > 250:
                px[x, y] = (0, 0, 0, 0)
    return im


def main() -> None:
    src = Image.open(ICONS / "app-source.png").convert("RGBA")

    exports = [
        ("32x32.png", 32),
        ("64x64.png", 64),
        ("128x128.png", 128),
        ("128x128@2x.png", 256),
        ("icon.png", 512),
    ]
    for name, size in exports:
        im = scrub_white_fringe(resize_rgba(src, size))
        im.save(ICONS / name)
        print(f"wrote {name} corner={im.getpixel((0, 0))}")

    # icon.ico / icon.icns are produced by `npx tauri icon` — Pillow multi-size ICO
    # save is unreliable here; do not overwrite them from this script.

    PUBLIC.mkdir(exist_ok=True)
    fav = scrub_white_fringe(resize_rgba(src, 128))
    fav.save(PUBLIC / "favicon.png")
    print(f"wrote favicon corner={fav.getpixel((0, 0))}")


if __name__ == "__main__":
    main()
