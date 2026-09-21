"""Prepare clean, store-ready screenshots from the Android captures in this folder.

The source captures are kept unchanged.  This script removes Android-only chrome,
neutralises the test-ad in the first capture, and writes the two store families:

* iOS App Store: 6.9-inch (1320x2868), 6.7-inch (1290x2796), and 6.5-inch
  (1284x2778) portrait canvases.
* Google Play: 1080x2160 portrait captures (the 2:1 maximum aspect ratio).
"""

from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
SOURCE = sorted(
    path for path in ROOT.glob("Screenshot_*.png")
    if re.fullmatch(r"Screenshot_\d{8}_\d{6}", path.stem)
)
TOP_CROP = 100       # Android status bar
BOTTOM_CROP = 100    # Android navigation bar
CONTENT_SIZE = (1080, 2140)

IOS_SIZES = {
    "6.9-inch": (1320, 2868),
    "6.7-inch": (1290, 2796),
    "6.5-inch": (1284, 2778),
}
PLAY_SIZE = (1080, 2160)
BACKGROUND = (13, 24, 44)


def font(size: int):
    # Verdana is available on macOS and has a clean storefront look for the
    # small neutral replacement panel used on the first screenshot.
    return ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana.ttf", size)


def remove_test_ad(image: Image.Image) -> None:
    """Replace the visible test-ad rectangle with a branded neutral panel.

    The ad is part of the first source capture only.  Keeping a clean panel in
    its place avoids inventing map details under the ad while removing the
    obvious test content from the store artwork.
    """
    draw = ImageDraw.Draw(image, "RGBA")
    # Coordinates after removing the 100 px Android status bar.
    box = (100, 218, 980, 360)
    draw.rectangle(box, fill=(24, 43, 66, 255))
    draw.rounded_rectangle(box, radius=18, fill=(24, 43, 66, 255), outline=(72, 215, 245, 255), width=3)

    cx, cy = 155, 289
    for radius, alpha in ((24, 235), (14, 235), (4, 255)):
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(108, 231, 255, alpha), width=4)
    draw.text((205, 250), "NEARBY EXPLORER", font=font(27), fill=(188, 245, 255, 255))
    draw.text((205, 292), "Explore places around you", font=font(19), fill=(232, 240, 248, 230))


def clean_source(path: Path) -> Image.Image:
    with Image.open(path) as src:
        src = src.convert("RGB")
        # This also strips the Android system bars while retaining the app's
        # own bottom navigation and full-bleed content.
        cleaned = src.crop((0, TOP_CROP, src.width, src.height - BOTTOM_CROP))
    if path.name == "Screenshot_20260918_152602.png":
        remove_test_ad(cleaned)
    if cleaned.size != CONTENT_SIZE:
        cleaned = cleaned.resize(CONTENT_SIZE, Image.Resampling.LANCZOS)
    return cleaned


def fit_on_canvas(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    canvas = Image.new("RGB", size, BACKGROUND)
    scale = size[0] / image.width
    fitted = image.resize((size[0], round(image.height * scale)), Image.Resampling.LANCZOS)
    y = (size[1] - fitted.height) // 2
    canvas.paste(fitted, (0, y))
    return canvas


def main() -> None:
    ios_root = ROOT / "ios_app_store"
    play_root = ROOT / "google_play"
    for directory in (ios_root, play_root):
        directory.mkdir(exist_ok=True)

    for source in SOURCE:
        cleaned = clean_source(source)
        stem = source.stem

        play = fit_on_canvas(cleaned, PLAY_SIZE)
        play.save(play_root / f"{stem}_1080x2160.png", optimize=True)

        for label, size in IOS_SIZES.items():
            ios = fit_on_canvas(cleaned, size)
            ios.save(ios_root / f"{stem}_{label}.png", optimize=True)

        # Keep a reviewable clean master at the exact source content ratio.
        cleaned.save(ROOT / f"{stem}_clean_1080x2140.png", optimize=True)

    print(f"Processed {len(SOURCE)} screenshots")


if __name__ == "__main__":
    main()
