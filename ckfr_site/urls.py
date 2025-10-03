from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

urlpatterns = [
    path(
        "",
        auth_views.LoginView.as_view(
            template_name="login.html",
            redirect_authenticated_user=True,
            success_url=settings.LOGIN_REDIRECT_URL,
        ),
        name="login",
    ),
    path("logout/", views.logout_and_redirect, name="logout"),
    path("admin/", admin.site.urls),
    path("", include("ops.urls")),
]