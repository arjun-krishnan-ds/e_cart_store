import os
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from e_cart.models import Product

class Command(BaseCommand):
    help = "Upload existing local media files to Cloudinary"

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        for product in products:
            # Only migrate if image exists and is not already on Cloudinary
            if product.image and not product.image.url.startswith("http"):
                # Use the full relative path stored in the DB
                local_path = os.path.join(settings.MEDIA_ROOT, str(product.image))

                if os.path.exists(local_path):
                    try:
                        with open(local_path, "rb") as f:
                            # Save back to Cloudinary
                            product.image.save(os.path.basename(local_path), File(f), save=True)
                        self.stdout.write(self.style.SUCCESS(f"[✅] Uploaded {product.name} to Cloudinary"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"[❌] Failed to upload {product.name}: {str(e)}"))
                else:
                    self.stdout.write(self.style.WARNING(f"[⚠️] File missing: {local_path}"))
