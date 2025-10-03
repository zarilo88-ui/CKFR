from django.apps import AppConfig

class CkfrSiteConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "ckfr_site"

    def ready(self):
        # Register our custom user admin
        from . import user_admin  # noqa
