"""Permission helpers for operations related views."""

from __future__ import annotations

from typing import Iterable

MANAGER_GROUPS: tuple[str, ...] = ("Admin", "SuperAdmin")
MEMBER_GROUPS: tuple[str, ...] = MANAGER_GROUPS + ("Member",)


def _is_authenticated_user(user) -> bool:
    return getattr(user, "is_authenticated", False)


def user_in_groups(user, groups: Iterable[str]) -> bool:
    """Return True if the user belongs to one of the provided groups."""

    if not _is_authenticated_user(user):
        return False
    if getattr(user, "is_superuser", False):
        return True
    return user.groups.filter(name__in=list(groups)).exists()


def can_manage_ops(user) -> bool:
    """Return True when the user can manage ships and allocations."""

    return user_in_groups(user, MANAGER_GROUPS)


def can_access_member_home(user) -> bool:
    """Return True if the user can view the operation overview page."""

    if not _is_authenticated_user(user):
        return False
    if can_manage_ops(user):
        return True
    return user_in_groups(user, MEMBER_GROUPS)