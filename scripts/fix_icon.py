"""Generate Port Manager app-source — same shape language as proxy-switch.

proxy-switch: 1024 RGBA, rounded tile to edges, transparent outer corners (~71px radius).
Pipeline: python scripts/fix_icon.py && npx tauri icon src-tauri/icons/app-source.png
Do NOT run build_icon_assets.py — it strips alpha and breaks Windows icons.
"""

from PIL import Image, ImageDraw
from pathlib import Path

SIZE = 1024
# Match proxy-switch corner radius proportion (diagonal transparent until ~71px).
TILE_RADIUS = 71
TILE = (8, 21, 51)  # same navy tile as proxy-switch — Windows handles this alpha correctly
STROKE = (232, 234, 237)
DOT = (22, 163, 74)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "src-tauri" / "icons" / "app-source.png"


def main() -> None:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=TILE_RADIUS, fill=TILE)

    left, right = 260, 700
    height = 88
    gap = 56
    top0 = 300
    pill_r = height // 2
    stroke = 28

    for i in range(3):
        top = top0 + i * (height + gap)
        draw.rounded_rectangle(
            [left, top, right, top + height],
            radius=pill_r,
            outline=STROKE,
            width=stroke,
        )

    cy = top0 + height // 2
    cx = right + 90
    r = 36
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=DOT)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG")
    print(f"wrote {OUT}")
    for pt in [(0, 0), (50, 50), (512, 512), (SIZE - 1, SIZE - 1)]:
        print(f"  {pt} = {img.getpixel(pt)}")


if __name__ == "__main__":
    main()
