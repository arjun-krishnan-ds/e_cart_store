from django.core.management.base import BaseCommand
from django.core.management import call_command
from e_cart.models import Product

class Command(BaseCommand):
    help = "Load products only if DB is empty"

    def handle(self, *args, **kwargs):
        if Product.objects.exists():
            self.stdout.write("Products already exist. Skipping load.")
        else:
            call_command("loaddata", "products.json")
            self.stdout.write("Products loaded successfully.")
