"""Preview board only — does NOT overwrite app icons. Run: python scripts/preview_icons.py"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "icon-previews" / "preview-board.png"
REF = Path(r"C:\Users\Admin\Desktop\github\proxy-switch\src-tauri\icons\app-source.png")

SIZE = 1024
TILE_RADIUS = 71
TILE = (8, 21, 51, 255)
GLYPH = (254, 253, 254, 255)
CHECKER = (48, 48, 48, 255)
CHECKER_ALT = (32, 32, 32, 255)


def checker(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size))
    px = img.load()
    step = 32
    for y in range(size):
        for x in range(size):
            px[x, y] = CHECKER if ((x // step) + (y // step)) % 2 == 0 else CHECKER_ALT
    return img


def tile_canvas() -> Image.Image:
    base = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=TILE_RADIUS, fill=TILE)
    return base


def draw_option_a(img: Image.Image) -> None:
    """Socket: rounded rect frame + 3 pin bars inside."""
    draw = ImageDraw.Draw(img)
    frame = [300, 330, 724, 694]
    draw.rounded_rectangle(frame, radius=36, outline=GLYPH, width=28)
    for i, top in enumerate([390, 480, 570]):
        draw.rounded_rectangle([360, top, 664, top + 52], radius=26, fill=GLYPH)


def draw_option_b(img: Image.Image) -> None:
    """Bindings: left nodes + horizontal links (proxy-switch family)."""
    draw = ImageDraw.Draw(img)
    xs = [280, 280, 280]
    ys = [390, 512, 634]
    r = 46
    for x, y in zip(xs, ys):
        draw.ellipse([x - r, y - r, x + r, y + r], fill=GLYPH)
        draw.rounded_rectangle([x + r + 24, y - 22, 744, y + 22], radius=22, fill=GLYPH)


def draw_option_c(img: Image.Image) -> None:
    """Port hash: colon dots + two digit bars."""
    draw = ImageDraw.Draw(img)
    for y in [420, 520]:
        draw.ellipse([330, y - 28, 386, y + 28], fill=GLYPH)
    draw.rounded_rectangle([430, 390, 690, 462], radius=36, fill=GLYPH)
    draw.rounded_rectangle([430, 562, 690, 634], radius=36, fill=GLYPH)


def draw_option_d(img: Image.Image) -> None:
    """Listen hub: center dot + three outward ports."""
    draw = ImageDraw.Draw(img)
    cx, cy = 512, 512
    draw.ellipse([cx - 52, cy - 52, cx + 52, cy + 52], fill=GLYPH)
    arms = [(512, 360, 512, 300), (512, 664, 512, 724), (360, 512, 300, 512), (664, 512, 724, 512)]
    for x1, y1, x2, y2 in arms:
        draw.line([x1, y1, x2, y2], fill=GLYPH, width=56)
        draw.ellipse([x2 - 34, y2 - 34, x2 + 34, y2 + 34], fill=GLYPH)


OPTIONS = [
    ("参考 proxy-switch", None),
    ("A · 端口插槽", draw_option_a),
    ("B · 绑定列表", draw_option_b),
    ("C · 端口编号", draw_option_c),
    ("D · 监听 hub", draw_option_d),
]


def render_option(title: str, drawer) -> Image.Image:
    if drawer is None:
        ref = Image.open(REF).convert("RGBA")
        if ref.size != (SIZE, SIZE):
            ref = ref.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
        canvas = ref
    else:
        canvas = tile_canvas()
        drawer(canvas)
    bg = checker(SIZE)
    bg.alpha_composite(canvas)
    return bg


def label(img: Image.Image, text: str) -> Image.Image:
    out = img.copy()
    draw = ImageDraw.Draw(out)
    try:
        font = ImageFont.truetype("arial.ttf", 42)
    except OSError:
        font = ImageFont.load_default()
    pad = 20
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.rounded_rectangle(
        [24, 24, 24 + tw + pad * 2, 24 + th + pad * 2],
        radius=12,
        fill=(0, 0, 0, 180),
    )
    draw.text((24 + pad, 24 + pad), text, fill=(255, 255, 255, 255), font=font)
    return out


def main() -> None:
    cell = 512
    cols, rows = 3, 2
    board = Image.new("RGBA", (cols * cell, rows * cell), (24, 24, 24, 255))

    for i, (title, drawer) in enumerate(OPTIONS):
        icon = render_option(title, drawer)
        icon = icon.resize((cell, cell), Image.Resampling.LANCZOS)
        icon = label(icon, title)
        x = (i % cols) * cell
        y = (i // cols) * cell
        board.paste(icon, (x, y))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    board.save(OUT, "PNG")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
