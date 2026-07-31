from PIL import Image
from io import BytesIO

from django.db.models import ImageField


def resize_image(image_field: ImageField) -> BytesIO:
    """
    Resize image based on aspect ratio conditions.
    """

    img = Image.open(image_field)

    # Calculate aspect ratio (width / height)
    width, height = img.size
    aspect_ratio = width / height

    if aspect_ratio <= 2.0:
        # Ratio ≤ 1:2 — resize to 200x200
        new_width, new_height = 200, 200
    elif aspect_ratio <= 5.0:
        # Ratio > 1:2 but ≤ 5.0 — height = 200, width proportional
        new_height = 200
        new_width = int(width * (new_height / height))
    else:
        # Ratio > 5.0 — height = 200, width = 1000
        new_width, new_height = 800, 200

    img.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)

    # Convert to RGB if necessary (for PNG with transparency)
    if img.mode in ('LA', 'P'):
        img = img.convert('RGB')

    # Save to BytesIO
    resized_image = BytesIO()
    img.save(resized_image, format='PNG', quality=85)
    resized_image.seek(0)

    return resized_image
