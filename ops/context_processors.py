"""Context processors for the operations app."""

from .permissions import can_access_member_home, can_manage_ops, is_operations_member_only


def permissions_flags(request):
    """Expose permission-related flags to all templates."""

    user = getattr(request, "user", None)
    can_manage = can_manage_ops(user) if user is not None else False
    can_view = can_access_member_home(user) if user is not None else False
    member_only = is_operations_member_only(user) if user is not None else False
    return {
        "can_manage_operations": can_manage,
        "can_view_operations": can_view,
        "is_operations_member_only": member_only,
    }