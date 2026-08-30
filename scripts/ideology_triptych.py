"""Compose the three-ideology featured image (hammer & sickle, circle-A, $).

Two deterministic layouts on a 1600x900 canvas:
  row      — spectrum order: hammer & sickle, circle-A (center, larger), $
  triangle — circle-A on top, the other two below ("off the spectrum")

Usage:
  uv run scripts/ideology_triptych.py --symbols-dir DIR --layout row --out out.png
"""

import argparse
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

CANVAS = (1600, 900)
BACKGROUND = "#0b0b0b"
INK = "#f2efe9"


def rasterize_svg(svg_path: Path, height: int) -> Image.Image:
    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        subprocess.run(
            ["rsvg-convert", "-h", str(height), str(svg_path), "-o", tmp.name],
            check=True,
        )
        return Image.open(tmp.name).convert("RGBA")


def tint(img: Image.Image, color: str) -> Image.Image:
    """Recolor a symbol to a flat ink color, keeping its alpha."""
    solid = Image.new("RGBA", img.size, color)
    solid.putalpha(img.getchannel("A"))
    return solid


def load_ink_png(path: Path, color: str) -> Image.Image:
    """Turn black line art on a white/checkered background into a tinted
    transparent symbol (the source PNG has no alpha channel)."""
    gray = Image.open(path).convert("L")
    alpha = gray.point(lambda v: max(0, min(255, (200 - v) * 3)))
    solid = Image.new("RGBA", gray.size, color)
    solid.putalpha(alpha)
    return solid.crop(solid.getbbox())


def fit_height(img: Image.Image, height: int) -> Image.Image:
    width = round(img.width * height / img.height)
    return img.resize((width, height), Image.LANCZOS)


def paste_centered(canvas: Image.Image, img: Image.Image, cx: int, cy: int) -> None:
    canvas.paste(img, (cx - img.width // 2, cy - img.height // 2), img)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbols-dir", type=Path, required=True)
    parser.add_argument("--layout", choices=["row", "triangle"], required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    hammer_svg = args.symbols_dir / "Hammer_and_sickle_red_on_transparent.svg"
    anarchy_svg = args.symbols_dir / "Circle-A_red.svg"
    dollar_png = args.symbols_dir / "pngwing-circle-dollar.png"

    canvas = Image.new("RGBA", CANVAS, BACKGROUND)
    width, height = CANVAS

    # Heights are hand-tuned for optical balance between the three symbols.
    if args.layout == "row":
        hammer = tint(rasterize_svg(hammer_svg, 420), INK)
        anarchy = tint(fit_height(rasterize_svg(anarchy_svg, 600), 540), INK)
        dollar = fit_height(load_ink_png(dollar_png, INK), 440)
        paste_centered(canvas, hammer, width // 4 - 30, height // 2)
        paste_centered(canvas, anarchy, width // 2, height // 2)
        paste_centered(canvas, dollar, 3 * width // 4 + 30, height // 2)
    else:
        hammer = tint(rasterize_svg(hammer_svg, 380), INK)
        anarchy = tint(fit_height(rasterize_svg(anarchy_svg, 600), 460), INK)
        dollar = fit_height(load_ink_png(dollar_png, INK), 390)
        paste_centered(canvas, anarchy, width // 2, 270)
        paste_centered(canvas, hammer, width // 2 - 480, 620)
        paste_centered(canvas, dollar, width // 2 + 480, 620)

    canvas.convert("RGB").save(args.out)


if __name__ == "__main__":
    main()
