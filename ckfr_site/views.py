from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "HEAD", "POST"])
def logout_and_redirect(request):
    """Log the user out and send them back to the login page."""
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)