"""Restore original Port Manager icon — only make outer white corners transparent."""

from __future__ import annotations

import io
import shutil
import subprocess
import sys
from collections import deque
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "src-tauri" / "icons"
PUBLIC = ROOT / "public"
PREVIEW = ROOT / "icon-previews" / "restore-preview.png"
DESKTOP_PREVIEW = ROOT / "icon-previews" / "desktop-preview.png"

# Initial release artwork — do not redraw or recolor.
ORIGINAL_COMMIT = "d701291:src-tauri/icons/app-source.png"


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


def clean_white_rim(img: Image.Image) -> Image.Image:
    """Remove white fringe pixels touching transparency (proxy-switch pipeline)."""
    out = img.convert("RGBA").copy()
    px = out.load()
    w, h = out.size
    changed = True
    passes = 0
    while changed and passes < 8:
        changed = False
        passes += 1
        rim: list[tuple[int, int]] = []
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                if a == 0:
                    continue
                if not (r >= 220 and g >= 220 and b >= 220):
                    continue
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if not (0 <= nx < w and 0 <= ny < h) or px[nx, ny][3] == 0:
                        rim.append((x, y))
                        break
        for x, y in rim:
            px[x, y] = (0, 0, 0, 0)
            changed = True
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


def fix_source(img: Image.Image) -> Image.Image:
    return defringe_rounded_edge(clean_white_rim(make_outer_white_transparent(img)))


def downscale_icon(source: Image.Image, size: int) -> Image.Image:
    return source.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)


def write_png(source: Image.Image, path: Path, size: int) -> None:
    downscale_icon(source, size).save(path, "PNG")


def npx_command() -> list[str]:
    return ["npx.cmd" if sys.platform == "win32" else "npx", "tauri", "icon"]


def write_platform_icons(source: Image.Image, path_ico: Path, path_icns: Path) -> None:
    """Delegate ICO/ICNS to Tauri CLI (32px-first ICO, same as proxy-switch)."""
    tmp = ICONS / ".tauri-icon-build"
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
        ico = tmp / "icon.ico"
        icns = tmp / "icon.icns"
        if ico.exists():
            shutil.copy2(ico, path_ico)
            print(f"wrote {path_ico}")
        else:
            print("warning: tauri icon did not produce icon.ico", file=sys.stderr)
        if icns.exists():
            shutil.copy2(icns, path_icns)
            print(f"wrote {path_icns}")
    finally:
        if tmp.exists():
            shutil.rmtree(tmp, ignore_errors=True)


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
    for idx, img in enumerate([before, after]):
        tile = checker(cell)
        layer = img.resize((cell, cell), Image.Resampling.LANCZOS)
        tile.alpha_composite(layer)
        board.paste(tile, (idx * cell, 0))
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    board.save(PREVIEW, "PNG")


def save_desktop_preview(ico_path: Path) -> None:
    """Simulate desktop shortcut icon (uses 32px ICO layer)."""
    import struct

    data = ico_path.read_bytes()
    _, _, count = struct.unpack_from("<HHH", data, 0)
    offset = 6
    icon32 = None
    for _ in range(count):
        w, h, *_rest, size, img_offset = struct.unpack_from("<BBBBHHII", data, offset)
        w = 256 if w == 0 else w
        h = 256 if h == 0 else h
        if w == 32:
            icon32 = Image.open(io.BytesIO(data[img_offset : img_offset + size])).convert("RGBA")
            break
        offset += 16
    if icon32 is None:
        icon32 = Image.open(ico_path).convert("RGBA")

    cell = 128
    desktop = Image.new("RGBA", (cell, cell + 40), (196, 196, 196, 255))
    tile = checker(cell)
    tile.alpha_composite(icon32.resize((cell, cell), Image.Resampling.LANCZOS))
    desktop.paste(tile, (0, 0))
    DESKTOP_PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    desktop.save(DESKTOP_PREVIEW, "PNG")
    print(f"desktop preview: {DESKTOP_PREVIEW}")


def main() -> None:
    original = load_original()
    fixed = fix_source(original)
    save_restore_preview(original, fixed)

    ICONS.mkdir(parents=True, exist_ok=True)
    PUBLIC.mkdir(parents=True, exist_ok=True)

    fixed.save(ICONS / "app-source.png", "PNG")
    write_png(fixed, ICONS / "32x32.png", 32)
    write_png(fixed, ICONS / "64x64.png", 64)
    write_png(fixed, ICONS / "128x128.png", 128)
    write_png(fixed, ICONS / "128x128@2x.png", 256)
    write_png(fixed, ICONS / "icon.png", 512)
    write_platform_icons(fixed, ICONS / "icon.ico", ICONS / "icon.icns")
    shutil.copy2(ICONS / "128x128.png", PUBLIC / "favicon.png")
    save_desktop_preview(ICONS / "icon.ico")

    print(f"preview: {PREVIEW}")
    print(f"corner before: {original.getpixel((0, 0))}")
    print(f"corner after:  {fixed.getpixel((0, 0))}")
    print("done")


if __name__ == "__main__":
    main()
