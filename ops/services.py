"""High level helpers for preparing ship allocation data."""

from collections import OrderedDict
from typing import Iterable, List, Sequence, Tuple

from django.db.models import Prefetch, QuerySet

from .constants import STATUS_BADGES
from .forms import RoleSlotForm
from .models import RoleSlot, Ship

ShipCategoryGrouping = List[Tuple[str, List[Ship]]]


def ships_with_slots() -> QuerySet[Ship]:
    """Return ships with their role slots preloaded and ordered."""

    return Ship.objects.prefetch_related(
        Prefetch(
            "role_slots",
            queryset=RoleSlot.objects.select_related("user").order_by("role_name", "index"),
        )
    )


def prepare_slots_for_display(
    slots: Iterable[RoleSlot],
    *,
    can_edit: bool,
    user_queryset=None,
) -> "OrderedDict[str, List[RoleSlot]]":
    """Annotate slots for display and group them by role."""

    grouped: "OrderedDict[str, List[RoleSlot]]" = OrderedDict()
    for slot in slots:
        if can_edit:
            slot.form = RoleSlotForm(
                instance=slot,
                user_queryset=user_queryset,
            )
        slot.badge_class = STATUS_BADGES.get(slot.status, STATUS_BADGES["open"])
        grouped.setdefault(slot.role_name, []).append(slot)
    return grouped


def prepare_ship_for_display(
    ship: Ship,
    *,
    can_edit: bool,
    user_queryset=None,
) -> Ship:
    """Attach grouped slot information to the ship instance."""

    grouped_slots = prepare_slots_for_display(
        ship.role_slots.all(),
        can_edit=can_edit,
        user_queryset=user_queryset,
    )
    ship.grouped_slots = list(grouped_slots.items())
    ship.slots_by_role = grouped_slots
    return ship


def group_ships_by_category(ships: Sequence[Ship]) -> ShipCategoryGrouping:
    """Return ships grouped by category preserving category order."""

    categories = OrderedDict(Ship.CATEGORY_CHOICES)
    grouped = {code: [] for code in categories}

    for ship in ships:
        grouped.setdefault(ship.category, []).append(ship)

    return [
        (label, grouped[code])
        for code, label in categories.items()
        if grouped.get(code)
    ]


__all__ = [
    "group_ships_by_category",
    "prepare_ship_for_display",
    "prepare_slots_for_display",
    "ships_with_slots",
]