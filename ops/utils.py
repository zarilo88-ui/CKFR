"""Utility helpers for working with the configured user model."""

from django.contrib.auth import get_user_model
from django.core.exceptions import FieldDoesNotExist, FieldError


def resolve_username_lookup():
    """Return the active user model and a safe field name for ordering.

    The configured ``USERNAME_FIELD`` may not map to a real database field
    (for instance when authentication is handled via an adapter property).
    In that case we gracefully fall back to the primary key so lookups remain
    valid instead of raising ``FieldError`` at query time.
    """

    user_model = get_user_model()
    order_field = getattr(user_model, "USERNAME_FIELD", "username")
    try:
        user_model._meta.get_field(order_field)
    except FieldDoesNotExist:
        order_field = "pk"
    return user_model, order_field


def get_ordered_user_queryset():
    """Return a queryset of users ordered by a safe identifier field."""

    user_model, order_field = resolve_username_lookup()
    manager = user_model._default_manager
    try:
        return manager.order_by(order_field)
    except FieldError:
        return manager.order_by("pk")
