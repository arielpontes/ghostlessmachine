"""Compose a cluttered collage of ideological symbols into one image.

Rasterizes SVG symbols (downloaded from Wikimedia Commons) with
rsvg-convert, then scatters them over a canvas with random rotation and
sizes. Layout is deterministic for a given --seed, so a look can be
reproduced and tweaked.

Usage:
    uv run scripts/symbol_collage.py --symbols-dir DIR --out out.png \
        [--seed 42] [--width 1600] [--height 900]
"""

import argparse
import io
import random
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BACKGROUND = "#ece7db"
DOLLAR_COLOR = "#1f7a33"
DOLLAR_FONT = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"

# (filename, instances, min px width, max px width)
SYMBOLS = [
    # flags
    ("Hammer_and_sickle.svg", 1, 160, 230),
    ("Gadsden_flag.svg", 1, 180, 260),
    ("Anarcho-capitalist_flag.svg", 1, 170, 240),
    ("Black_flag.svg", 1, 150, 200),
    ("Red_and_black_flag.svg", 1, 170, 240),
    ("Green_and_Black_flag.svg", 1, 170, 240),
    ("Anarcho-pacifist_flag.svg", 1, 170, 240),
    ("Crypto-Anarchist_flag_with_symbol.svg", 1, 170, 240),
    ("Voluntaryism_flag.svg", 1, 170, 240),
    ("Democratic_Socialism_Flag.svg", 1, 170, 240),
    ("Ejército_Zapatista_de_Liberación_Nacional,_Flag.svg", 1, 170, 240),
    ("Flag_of_the_UNIA.svg", 1, 170, 240),
    # emblems and glyphs
    ("Red_star.svg", 1, 110, 180),
    ("Circle-A_red.svg", 1, 120, 200),
    ("Anarchy-symbol.svg", 1, 120, 200),
    ("Red_rose_02.svg", 1, 120, 190),
    ("Anarcha-feminism.svg", 1, 120, 190),
    ("Anarchist_black_cat.svg", 1, 130, 200),
    ("Mutualismo.svg", 1, 110, 180),
    ("Agorism-symbol.svg", 1, 110, 180),
    ("WPK_symbol.svg", 1, 130, 200),
    ("Antifa_logo.svg", 1, 130, 200),
    ("Woman-power_emblem.svg", 1, 120, 190),
    ("Sunflower_(Green_symbol).svg", 1, 120, 190),
    ("Libertatis_Æquilibritas.svg", 1, 120, 190),
    ("Bitcoin.svg", 1, 110, 170),
    ("Royal_crown_curved_simple.svg", 1, 120, 190),
    ("Transhumanism_h+.svg", 1, 110, 180),
    ("DemocraticLogo.svg", 1, 120, 190),
    ("Republicanlogo.svg", 1, 120, 190),
    ("Fasces.svg", 1, 110, 190),
    ("Logo_European_Pirate_Party_01.svg", 1, 120, 190),
    ("Christian_cross.svg", 1, 110, 180),
    ("Star_and_Crescent.svg", 1, 110, 180),
    ("Star_of_David.svg", 1, 110, 180),
    ("Om_symbol.svg", 1, 110, 180),
    ("Dharma_Wheel.svg", 1, 110, 180),
    ("Khanda.svg", 1, 110, 180),
    ("Yin_yang.svg", 1, 110, 180),
    ("Atom_of_Atheism-Zanaq.svg", 1, 110, 180),
]
DOLLAR_INSTANCES = 1


def raster_svg(path: Path, width: int) -> Image.Image:
    png = subprocess.run(
        ["rsvg-convert", "-w", str(width), str(path)],
        check=True,
        capture_output=True,
    ).stdout
    return Image.open(io.BytesIO(png)).convert("RGBA")


def dollar_sprite(height: int) -> Image.Image:
    font = ImageFont.truetype(DOLLAR_FONT, height)
    left, top, right, bottom = font.getbbox("$")
    img = Image.new("RGBA", (right - left, bottom - top), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((-left, -top), "$", font=font, fill=DOLLAR_COLOR)
    return img


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbols-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--height", type=int, default=900)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    canvas = Image.new("RGB", (args.width, args.height), BACKGROUND)

    # Sizes are requested as widths, so cap the tall symbols (flags-on-
    # poles, the fasces) by their largest dimension too.
    max_dim = 250
    sprites = []
    for filename, instances, min_w, max_w in SYMBOLS:
        for _ in range(instances):
            width = rng.randint(min_w, max_w)
            sprite = raster_svg(args.symbols_dir / filename, width)
            if max(sprite.size) > max_dim:
                sprite.thumbnail((max_dim, max_dim))
            sprites.append(sprite)
    for _ in range(DOLLAR_INSTANCES):
        sprites.append(dollar_sprite(rng.randint(140, 280)))

    # One shuffled grid cell per sprite, with jitter, so the clutter
    # still spreads over the whole canvas instead of clumping.
    cols = 9
    rows = -(-len(sprites) // cols)
    cells = [(c, r) for c in range(cols) for r in range(rows)]
    rng.shuffle(cells)
    rng.shuffle(sprites)

    cell_w = args.width / cols
    cell_h = args.height / rows
    for sprite, (col, row) in zip(sprites, cells):
        rotated = sprite.rotate(
            rng.uniform(-35, 35), expand=True, resample=Image.BICUBIC
        )
        x = int((col + 0.5) * cell_w - rotated.width / 2)
        y = int((row + 0.5) * cell_h - rotated.height / 2)
        x += rng.randint(-int(cell_w / 4), int(cell_w / 4))
        y += rng.randint(-int(cell_h / 4), int(cell_h / 4))
        canvas.paste(rotated, (x, y), rotated)

    canvas.save(args.out)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
