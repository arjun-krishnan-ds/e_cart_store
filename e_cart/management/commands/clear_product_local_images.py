import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "e_cart.settings")
django.setup()

from e_cart.models import Product


def run():
    qs = Product.objects.exclude(image=None)

    print(f"Found {qs.count()} product image entries")

    for p in qs:
        p.image = None
        p.save(update_fields=["image"])

    print("All Product image fields cleared.")


if __name__ == "__main__":
    run()
