import random
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont


AVATAR_COLORS = [
    "#6B7280",
    "#78716C",
    "#64748B",
    "#71717A",
    "#737373",
    "#5B6B7A",
    "#6C757D",
    "#7B8794",
]


def generate_avatar_image(name: str) -> ContentFile:
    letter = name[0].upper() if name else "?"
    size = 128
    bg_color = random.choice(AVATAR_COLORS)
    image = Image.new("RGB", (size, size), bg_color)
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 64)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size - text_width) / 2, (size - text_height) / 2 - bbox[1])
    draw.text(position, letter, fill="#FFFFFF", font=font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=f"avatar_{letter}.png")
