from django.apps import AppConfig

class CkfrSiteConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "ckfr_site"

    def ready(self):
        from . import session_management, user_admin  # noqa: F401