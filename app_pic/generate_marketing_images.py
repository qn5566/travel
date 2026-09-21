"""Generate two storefront marketing images from the real app screenshots."""

from pathlib import Path
import shutil
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "marketing_intro"
FONT_TC = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_EN = "/System/Library/Fonts/Supplemental/Verdana.ttf"


def tc(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_TC, size)


def en(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_EN, size)


def gradient(size, top, bottom):
    w, h = size
    image = Image.new("RGB", size)
    draw = ImageDraw.Draw(image)
    for y in range(h):
        t = y / max(h - 1, 1)
        color = tuple(round(a + (b - a) * t) for a, b in zip(top, bottom))
        draw.line((0, y, w, y), fill=color)
    return image


def add_background_details(image: Image.Image, accent, variant: int):
    draw = ImageDraw.Draw(image, "RGBA")
    w, h = image.size
    # Subtle map/radar motifs that echo the app without competing with copy.
    anchor = (int(w * (0.82 if variant == 1 else 0.15)), int(h * 0.22))
    for ratio, alpha in ((0.28, 20), (0.20, 28), (0.12, 38)):
        r = int(w * ratio)
        draw.ellipse((anchor[0]-r, anchor[1]-r, anchor[0]+r, anchor[1]+r), outline=(*accent, alpha), width=max(2, w // 300))
    for x, y, radius in ((.08,.31,.012),(.91,.37,.008),(.13,.75,.006),(.88,.68,.015)):
        r = int(w * radius)
        draw.ellipse((w*x-r,h*y-r,w*x+r,h*y+r), fill=(*accent, 90))
    # Gentle glow beneath the phone.
    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((int(w*.10), int(h*.48), int(w*.90), int(h*1.03)), fill=(*accent, 45))
    glow = glow.filter(ImageFilter.GaussianBlur(max(30, w // 14)))
    image.paste(glow, (0, 0), glow)


def paste_icon(image: Image.Image, x: int, y: int, side: int):
    icon = Image.open(ROOT.parent / "res" / "app_icon.png").convert("RGB").resize((side, side), Image.Resampling.LANCZOS)
    mask = Image.new("L", (side, side), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, side-1, side-1), radius=side//4, fill=255)
    ring = Image.new("RGBA", (side+8, side+8), (255,255,255,0))
    ImageDraw.Draw(ring).rounded_rectangle((0,0,side+7,side+7), radius=side//4+4, fill=(255,255,255,245))
    image.paste(ring, (x-4, y-4), ring)
    image.paste(icon, (x, y), mask)


def chip(image: Image.Image, x: int, y: int, text: str, accent, scale: float):
    f = tc(round(27 * scale))
    pad_x, height = round(24 * scale), round(58 * scale)
    bbox = f.getbbox(text)
    width = bbox[2] - bbox[0] + pad_x * 2
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((x, y, x+width, y+height), radius=height//2, fill=(255,255,255,34), outline=(*accent,150), width=max(2,round(2*scale)))
    draw.ellipse((x+round(15*scale), y+round(20*scale), x+round(25*scale), y+round(30*scale)), fill=(*accent,255))
    draw.text((x+round(36*scale), y+round(11*scale)), text, font=f, fill=(245,250,255,255))
    return width


def phone_mockup(image: Image.Image, screenshot_path: Path, x: int, y: int, width: int, height: int, accent):
    radius = width // 10
    shadow_pad = max(30, width // 12)
    layer = Image.new("RGBA", (width + shadow_pad*2, height + shadow_pad*2), (0,0,0,0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle((shadow_pad, shadow_pad, shadow_pad+width, shadow_pad+height), radius=radius, fill=(0,0,0,185))
    layer = layer.filter(ImageFilter.GaussianBlur(shadow_pad//2))
    image.paste(layer, (x-shadow_pad, y-shadow_pad//2), layer)

    frame = Image.new("RGBA", (width, height), (0,0,0,0))
    fd = ImageDraw.Draw(frame)
    fd.rounded_rectangle((0,0,width-1,height-1), radius=radius, fill=(6,13,26,255), outline=(*accent,255), width=max(4,width//100))

    inset = max(14, width // 35)
    inner_size = (width-inset*2, height-inset*2)
    shot = Image.open(screenshot_path).convert("RGB")
    # Fill the tall device window. Crop only the sides; preserve vertical UI.
    target_ratio = inner_size[0] / inner_size[1]
    src_ratio = shot.width / shot.height
    if src_ratio > target_ratio:
        crop_w = round(shot.height * target_ratio)
        left = (shot.width - crop_w) // 2
        shot = shot.crop((left, 0, left+crop_w, shot.height))
    else:
        crop_h = round(shot.width / target_ratio)
        top = (shot.height - crop_h) // 2
        shot = shot.crop((0, top, shot.width, top+crop_h))
    shot = shot.resize(inner_size, Image.Resampling.LANCZOS)
    shot_mask = Image.new("L", inner_size, 0)
    ImageDraw.Draw(shot_mask).rounded_rectangle((0,0,inner_size[0]-1,inner_size[1]-1), radius=max(12,radius-inset), fill=255)
    frame.paste(shot, (inset,inset), shot_mask)
    image.paste(frame, (x,y), frame)


def create(size, concept: int, output: Path):
    w, h = size
    scale = w / 1080
    if concept == 1:
        bg = gradient(size, (7, 19, 39), (14, 75, 104))
        accent = (77, 224, 246)
        title = "探索身邊的精彩"
        subtitle = "附近景點，一打開就發現"
        chips = ["景點", "公園", "夜市"]
        source = ROOT / "Screenshot_20260918_152602_clean_1080x2140.png"
    else:
        bg = gradient(size, (17, 16, 42), (65, 41, 117))
        accent = (163, 126, 255)
        title = "下一站，說走就走"
        subtitle = "搜尋、收藏、導航一次完成"
        chips = ["熱門排行", "快速搜尋", "開啟導航"]
        source = ROOT / "Screenshot_20260918_152613_clean_1080x2140.png"

    add_background_details(bg, accent, concept)
    draw = ImageDraw.Draw(bg, "RGBA")

    side = round(78 * scale)
    header_y = round(90 * scale)
    paste_icon(bg, round(78*scale), header_y, side)
    draw.text((round(178*scale), header_y+round(6*scale)), "台灣景點地圖", font=tc(round(31*scale)), fill=(246,250,255,255))
    draw.text((round(178*scale), header_y+round(45*scale)), "TAIWAN EXPLORER", font=en(round(14*scale)), fill=(*accent,230))

    title_y = round(240 * scale)
    draw.text((w//2, title_y), title, font=tc(round(73*scale)), fill=(255,255,255,255), anchor="ma")
    draw.text((w//2, title_y+round(108*scale)), subtitle, font=tc(round(31*scale)), fill=(220,232,244,245), anchor="ma")

    widths = []
    chip_font = tc(round(27 * scale))
    for label in chips:
        bbox = chip_font.getbbox(label)
        widths.append(bbox[2]-bbox[0]+round(48*scale))
    gap = round(16 * scale)
    x = (w - sum(widths) - gap*(len(chips)-1)) // 2
    chip_y = title_y + round(180*scale)
    for label in chips:
        used = chip(bg, x, chip_y, label, accent, scale)
        x += used + gap

    phone_w = round(755 * scale)
    # Scale the mockup to available vertical space for each storefront ratio.
    phone_y = title_y + round(290 * scale)
    available_h = h - phone_y + round(70*scale)
    phone_h = min(round(1570 * scale), available_h)
    if concept == 1:
        phone_x = (w-phone_w)//2
    else:
        phone_x = (w-phone_w)//2 + round(34*scale)
    phone_mockup(bg, source, phone_x, phone_y, phone_w, phone_h, accent)

    # Floating feature badge adds depth while keeping claims factual.
    badge_text = "即時探索" if concept == 1 else "全台景點"
    badge_w, badge_h = round(230*scale), round(78*scale)
    bx = round(42*scale) if concept == 2 else w-round(42*scale)-badge_w
    by = phone_y + round(420*scale)
    shadow = Image.new("RGBA", (badge_w+30,badge_h+30), (0,0,0,0))
    ImageDraw.Draw(shadow).rounded_rectangle((15,15,15+badge_w,15+badge_h), radius=badge_h//2, fill=(0,0,0,145))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    bg.paste(shadow,(bx-15,by-8),shadow)
    draw = ImageDraw.Draw(bg,"RGBA")
    draw.rounded_rectangle((bx,by,bx+badge_w,by+badge_h), radius=badge_h//2, fill=(250,252,255,246), outline=(*accent,255), width=max(3,round(3*scale)))
    draw.text((bx+badge_w//2,by+badge_h//2),badge_text,font=tc(round(27*scale)),fill=(22,31,53,255),anchor="mm")

    output.parent.mkdir(parents=True, exist_ok=True)
    bg.save(output, optimize=True)


def main():
    outputs = [
        ((1320, 2868), "ios_6.9-inch"),
        ((1284, 2778), "ios_6.5-inch"),
        ((1080, 2160), "google_play"),
    ]
    for size, label in outputs:
        for concept in (1, 2):
            create(size, concept, OUT / f"intro_{concept}_{label}.png")

    # App Store Connect may show a 6.5-inch upload slot that accepts only
    # 1284x2778 (or 1242x2688). Keep one ordered folder containing nothing but
    # valid 1284x2778 files so the wrong size cannot be selected accidentally.
    upload = ROOT / "ios_upload_1284x2778"
    upload.mkdir(exist_ok=True)
    sources = [
        (OUT / "intro_1_ios_6.5-inch.png", "01_explore_nearby.png"),
        (OUT / "intro_2_ios_6.5-inch.png", "02_find_your_next_stop.png"),
        (ROOT / "ios_app_store" / "Screenshot_20260918_152602_6.5-inch.png", "03_nearby_map.png"),
        (ROOT / "ios_app_store" / "Screenshot_20260918_152613_6.5-inch.png", "04_attractions.png"),
        (ROOT / "ios_app_store" / "Screenshot_20260918_152727_6.5-inch.png", "05_place_details.png"),
        (ROOT / "ios_app_store" / "Screenshot_20260918_152820_6.5-inch.png", "06_popular_ranking.png"),
    ]
    for source, name in sources:
        shutil.copyfile(source, upload / name)
    print("Generated 2 concepts and prepared the 1284x2778 App Store upload set")


if __name__ == "__main__":
    main()
