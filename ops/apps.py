from django.apps import AppConfig


class OpsConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "ops"

    def ready(self):
        from . import signals  # noqa
