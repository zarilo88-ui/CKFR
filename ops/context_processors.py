"""Context processors for the operations app."""

from .permissions import can_manage_ops


def permissions_flags(request):
    """Expose permission-related flags to all templates."""

    user = getattr(request, "user", None)
    return {
        "can_manage_operations": can_manage_ops(user) if user is not None else False,
    }