from PIL import Image
from PIL import ImageDraw
from io import BytesIO

from django.db.models import ImageField


def resize_image(image_field: ImageField, circular: bool = True) -> None:
    """
    Resize image to a maximum of 200x200 pixels.
    """

    img = Image.open(image_field)
    img.thumbnail((200, 200), Image.Resampling.LANCZOS)

    # Convert to RGB if necessary (for PNG with transparency)
    if img.mode in ('LA', 'P'):
        img = img.convert('RGB')

    if circular:
        # Create circular mask
        size = img.size
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse([0, 0, size[0], size[1]], fill=255)
        img.putalpha(mask)

    # Save to BytesIO
    resized_image = BytesIO()
    img.save(resized_image, format='PNG', quality=85)
    resized_image.seek(0)

    return resized_image
