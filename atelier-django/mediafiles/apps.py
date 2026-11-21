from django.apps import AppConfig


class MediafilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mediafiles"

    def ready(self):
        from . import signals  # noqa: F401
