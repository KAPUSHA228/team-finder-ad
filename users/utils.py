import hashlib
import io
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile

AVATAR_SIZE = 200
AVATAR_FONT_SIZE = 100

AVATAR_FONT_NAMES = ["arial.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"]


AVATAR_COLOR_PALETTE = [
    (100, 149, 237),  # Cornflower Blue
    (144, 238, 144),  # Light Green
    (255, 182, 193),  # Light Pink
    (221, 160, 221),  # Plum
    (173, 216, 230),  # Light Blue
    (255, 218, 185),  # Peach Puff
    (176, 224, 230),  # Powder Blue
    (240, 230, 140),  # Khaki
    (255, 160, 122),  # Light Salmon
]

AVATAR_TEXT_COLOR = (255, 255, 255)

AVATAR_FILENAME_PREFIX = "avatar_"


def generate_avatar_image(name: str, email: str) -> tuple[ContentFile, str]:

    img = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), color=get_avatar_color(email))
    draw = ImageDraw.Draw(img)

    letter = name[0].upper() if name else "?"

    font = None
    for font_name in AVATAR_FONT_NAMES:
        try:
            font = ImageFont.truetype(font_name, AVATAR_FONT_SIZE)
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((AVATAR_SIZE - text_width) // 2, (AVATAR_SIZE - text_height) // 2)

    draw.text(position, letter, fill=AVATAR_TEXT_COLOR, font=font)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    filename = f"{AVATAR_FILENAME_PREFIX}{hashlib.md5(email.encode()).hexdigest()[:8]}.png"
    return ContentFile(buffer.read()), filename


def get_avatar_color(email: str) -> tuple[int, int, int]:

    if not email:
        return AVATAR_COLOR_PALETTE[0]

    hash_value = int(hashlib.md5(email.lower().strip().encode()).hexdigest(), 16)
    index = hash_value % len(AVATAR_COLOR_PALETTE)
    return AVATAR_COLOR_PALETTE[index]
