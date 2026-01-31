import os
import django
import cloudinary
import cloudinary.api
import cloudinary.uploader
from django.utils.text import slugify

# -----------------------------
# Setup Django
# -----------------------------
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_cart.settings')
django.setup()

from e_cart.models import Product  # replace your_app with actual app name

# -----------------------------
# Setup Cloudinary
# -----------------------------
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET")
)

# -----------------------------
# Rename Product Images
# -----------------------------
products = Product.objects.exclude(image='')  # only products with images

for p in products:
    if not p.image:
        continue

    old_public_id = p.image.public_id
    ext = p.image.name.split('.')[-1]
    new_public_id = f"products/{slugify(p.slug if p.slug else p.name)}.{ext}"

    if old_public_id != new_public_id:
        try:
            print(f"Renaming {old_public_id} -> {new_public_id}")
            cloudinary.api.rename(
                old_public_id,
                new_public_id,
                invalidate=True  # clears CDN cache
            )
        except Exception as e:
            print(f"Error renaming {old_public_id}: {e}")
