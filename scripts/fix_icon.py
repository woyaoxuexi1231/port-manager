"""Generate Port Manager icon: rounded tile + transparent corners (no white)."""

from PIL import Image, ImageDraw
from pathlib import Path

SIZE = 1024
BG = (26, 28, 32, 255)  # #1A1C20
STROKE = (232, 234, 237, 255)  # #E8EAED
DOT = (22, 163, 74, 255)  # #16A34A
# Corner radius for the app tile (Windows-style rounded square)
TILE_RADIUS = 220

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "src-tauri" / "icons" / "app-source.png"


def main() -> None:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded tile — corners stay transparent
    margin = 0
    tile = [margin, margin, SIZE - 1 - margin, SIZE - 1 - margin]
    draw.rounded_rectangle(tile, radius=TILE_RADIUS, fill=BG)

    left, right = 260, 700
    height = 88
    gap = 56
    top0 = 300
    radius = height // 2
    stroke = 28

    for i in range(3):
        top = top0 + i * (height + gap)
        box = [left, top, right, top + height]
        draw.rounded_rectangle(box, radius=radius, outline=STROKE, width=stroke)

    cy = top0 + height // 2
    cx = right + 90
    r = 36
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=DOT)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG")

    # Sanity: corners must be fully transparent, center opaque dark
    print(f"wrote {OUT}")
    for pt in [(0, 0), (SIZE - 1, 0), (0, SIZE - 1), (SIZE - 1, SIZE - 1), (SIZE // 2, SIZE // 2)]:
        print(f"  {pt} = {img.getpixel(pt)}")


if __name__ == "__main__":
    main()
