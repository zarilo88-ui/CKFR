"""Signals related to authentication/session management."""

from __future__ import annotations

from django.contrib.auth.signals import user_logged_in
from django.contrib.sessions.models import Session
from django.dispatch import receiver
from django.utils import timezone


@receiver(user_logged_in)
def terminate_previous_sessions(sender, request, user, **kwargs):
    """Ensure a user only has one active session at a time."""

    current_session_key = getattr(getattr(request, "session", None), "session_key", None)
    if current_session_key is None:
        return

    user_id = str(user.pk)
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now()).exclude(
        session_key=current_session_key
    )

    for session in active_sessions:
        data = session.get_decoded()
        if data.get("_auth_user_id") == user_id:
            session.delete()