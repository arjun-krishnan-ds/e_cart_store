from django.apps import AppConfig
from django.contrib.auth import get_user_model
import os
from django.db.utils import OperationalError, ProgrammingError

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        if os.environ.get("CREATE_SUPERUSER") != "1":
            return

        User = get_user_model()
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username or not password:
            return

        try:
            # Only try to create superuser if table exists
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
        except (OperationalError, ProgrammingError):
            # Database not ready yet (migrations not applied)
            pass
