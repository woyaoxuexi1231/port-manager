"""Restore original Port Manager icon — only make outer white corners transparent."""

from __future__ import annotations

import io
import shutil
import struct
import subprocess
import sys
from collections import deque
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "src-tauri" / "icons"
PUBLIC = ROOT / "public"
PREVIEW = ROOT / "icon-previews" / "restore-preview.png"

# Initial release artwork — do not redraw or recolor.
ORIGINAL_COMMIT = "d701291:src-tauri/icons/app-source.png"

ICO_SIZES = (16, 24, 32, 48, 64, 128, 256)


def load_original() -> Image.Image:
    data = subprocess.check_output(
        ["git", "-C", str(ROOT), "show", ORIGINAL_COMMIT],
    )
    return Image.open(io.BytesIO(data)).convert("RGBA")


def make_outer_white_transparent(img: Image.Image) -> Image.Image:
    """Flood-fill only the outer white matte; keep glyph + tile pixels intact."""
    out = img.convert("RGBA").copy()
    px = out.load()
    w, h = out.size

    def is_outer_white(r: int, g: int, b: int, a: int) -> bool:
        return a > 0 and r >= 230 and g >= 230 and b >= 230

    seen = [[False] * h for _ in range(w)]
    q: deque[tuple[int, int]] = deque()

    for x, y in (
        (0, 0),
        (w - 1, 0),
        (0, h - 1),
        (w - 1, h - 1),
        (w // 2, 0),
        (0, h // 2),
        (w - 1, h // 2),
        (w // 2, h - 1),
    ):
        if is_outer_white(*px[x, y]):
            seen[x][y] = True
            q.append((x, y))

    while q:
        x, y = q.popleft()
        px[x, y] = (0, 0, 0, 0)
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and 0 <= ny < h and not seen[nx][ny]:
                if is_outer_white(*px[nx, ny]):
                    seen[nx][ny] = True
                    q.append((nx, ny))

    return out


def defringe_rounded_edge(img: Image.Image) -> Image.Image:
    """Recompute edge alpha after removing the white matte (smooth rounded corners)."""
    out = img.convert("RGBA").copy()
    px = out.load()
    w, h = out.size
    fg = (27, 29, 33)

    def keep_as_is(r: int, g: int, b: int) -> bool:
        if min(r, g, b) > 200:
            return True
        if g > 120 and g > r + 40:
            return True
        return False

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0 or keep_as_is(r, g, b):
                continue
            if max(r, g, b) >= 90:
                continue

            alphas: list[float] = []
            for channel, target in zip((r, g, b), fg):
                denom = 255 - target
                if denom <= 0:
                    continue
                alphas.append(max(0.0, min(1.0, (255 - channel) / denom)))

            if not alphas:
                continue

            alpha = min(alphas)
            if alpha < 0.04:
                px[x, y] = (0, 0, 0, 0)
            elif alpha > 0.98:
                px[x, y] = (*fg, 255)
            else:
                px[x, y] = (*fg, int(alpha * 255))

    return out


def downscale_icon(source: Image.Image, size: int) -> Image.Image:
    """Keep anti-aliased rounded corners when generating smaller assets."""
    return source.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)


def write_png(source: Image.Image, path: Path, size: int) -> None:
    downscale_icon(source, size).save(path, "PNG")


def write_ico(source: Image.Image, path: Path) -> None:
    frames = [downscale_icon(source, size) for size in ICO_SIZES]
    png_payloads: list[bytes] = []
    for frame in frames:
        buffer = io.BytesIO()
        frame.save(buffer, format="PNG")
        png_payloads.append(buffer.getvalue())

    count = len(frames)
    header = struct.pack("<HHH", 0, 1, count)
    directory = bytearray()
    image_data = bytearray()
    offset = 6 + (16 * count)

    for frame, payload in zip(frames, png_payloads):
        width = frame.width if frame.width < 256 else 0
        height = frame.height if frame.height < 256 else 0
        directory.extend(
            struct.pack(
                "<BBBBHHII",
                width,
                height,
                0,
                0,
                1,
                32,
                len(payload),
                offset,
            )
        )
        image_data.extend(payload)
        offset += len(payload)

    path.write_bytes(header + bytes(directory) + bytes(image_data))


def checker(size: int) -> Image.Image:
    base = Image.new("RGBA", (size, size), (32, 32, 32, 255))
    px = base.load()
    step = 32
    for y in range(size):
        for x in range(size):
            if ((x // step) + (y // step)) % 2 == 0:
                px[x, y] = (48, 48, 48, 255)
    return base


def save_restore_preview(before: Image.Image, after: Image.Image) -> None:
    cell = 512
    board = Image.new("RGBA", (cell * 2, cell), (24, 24, 24, 255))
    for idx, (title, img) in enumerate(
        [("原版（白角）", before), ("修复（透明角）", after)]
    ):
        tile = checker(cell)
        layer = img.resize((cell, cell), Image.Resampling.LANCZOS)
        tile.alpha_composite(layer)
        board.paste(tile, (idx * cell, 0))
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    board.save(PREVIEW, "PNG")


def npx_command() -> list[str]:
    return ["npx.cmd" if sys.platform == "win32" else "npx", "tauri", "icon"]


def write_icns(source: Image.Image, path: Path) -> None:
    tmp = ICONS / ".icns-build"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    staging = tmp / "app-source.png"
    source.save(staging, "PNG")
    try:
        subprocess.run(
            [*npx_command(), str(staging), "-o", str(tmp)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        generated = tmp / "icon.icns"
        if generated.exists():
            shutil.copy2(generated, path)
    finally:
        if tmp.exists():
            shutil.rmtree(tmp, ignore_errors=True)


def main() -> None:
    original = load_original()
    fixed = defringe_rounded_edge(make_outer_white_transparent(original))
    save_restore_preview(original, fixed)

    ICONS.mkdir(parents=True, exist_ok=True)
    PUBLIC.mkdir(parents=True, exist_ok=True)

    fixed.save(ICONS / "app-source.png", "PNG")
    write_png(fixed, ICONS / "32x32.png", 32)
    write_png(fixed, ICONS / "64x64.png", 64)
    write_png(fixed, ICONS / "128x128.png", 128)
    write_png(fixed, ICONS / "128x128@2x.png", 256)
    write_png(fixed, ICONS / "icon.png", 512)
    write_ico(fixed, ICONS / "icon.ico")
    write_icns(fixed, ICONS / "icon.icns")
    shutil.copy2(ICONS / "128x128.png", PUBLIC / "favicon.png")

    print(f"preview: {PREVIEW}")
    print(f"corner before: {original.getpixel((0, 0))}")
    print(f"corner after:  {fixed.getpixel((0, 0))}")
    print(f"center kept:   {fixed.getpixel((512, 512))}")
    print("done")


if __name__ == "__main__":
    main()
