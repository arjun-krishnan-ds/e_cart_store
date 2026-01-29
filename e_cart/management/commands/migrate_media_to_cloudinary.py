from django.core.management.base import BaseCommand
from e_cart.models import Product
from django.core.files import File
import os

class Command(BaseCommand):
    help = "Upload existing local media files to Cloudinary and update DB"

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        for product in products:
            if product.image and not product.image.url.startswith("http"):
                local_path = product.image.path
                if os.path.exists(local_path):
                    with open(local_path, "rb") as f:
                        product.image.save(os.path.basename(local_path), File(f), save=True)
                    self.stdout.write(f"[✅] Uploaded {product.name} to Cloudinary → {product.image.url}")
                else:
                    self.stdout.write(f"[⚠️] File missing: {local_path}")
            else:
                self.stdout.write(f"[ℹ️] Already on Cloudinary: {product.name}")
