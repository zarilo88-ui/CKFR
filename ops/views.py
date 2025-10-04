"""Views for the operations module."""

from collections import OrderedDict

from django.contrib import messages
from django.contrib.auth import decorators as auth_decorators
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import RoleSlotForm, ShipRoleTemplateForm
from .models import Operation, RoleSlot, Ship
from .permissions import can_manage_ops
from .services import (
    group_ships_by_category,
    prepare_ship_for_display,
    ships_with_slots,
)


FILTER_TREE = OrderedDict(
    (
        (
            "military",
            {
                "label": "Militaire",
                "subcategories": OrderedDict(
                    (
                        (
                            "chasseur",
                            {
                                "label": "Chasseur",
                                "keywords": (
                                    "fighter",
                                    "stealth",
                                    "combat",
                                    "interceptor",
                                    "racing",
                                    "patrol",
                                    "escort",
                                    "pursuit",
                                ),
                            },
                        ),
                        (
                            "capitaux",
                            {
                                "label": "Capitaux",
                                "keywords": (
                                    "destroyer",
                                    "frigate",
                                    "corvette",
                                    "carrier",
                                    "dread",
                                    "capital",
                                    "battle",
                                    "battleship",
                                ),
                            },
                        ),
                        (
                            "gunship",
                            {
                                "label": "Gun Ship",
                                "keywords": ("gunship",),
                            },
                        ),
                        (
                            "bomber",
                            {
                                "label": "Bomber",
                                "keywords": ("bomber",),
                            },
                        ),
                        (
                            "torpilleur",
                            {
                                "label": "Torpilleur",
                                "keywords": ("torpedo", "torp"),
                            },
                        ),
                        (
                            "interdicteur",
                            {
                                "label": "Interdicteur",
                                "keywords": (
                                    "interdict",
                                    "interdiction",
                                    "minelayer",
                                    "quantum enforcement",
                                    "quantum damp",
                                ),
                            },
                        ),
                        (
                            "dropship",
                            {
                                "label": "Drop Ship",
                                "keywords": (
                                    "dropship",
                                    "drop ship",
                                    "boarding",
                                    "troop",
                                    "personnel",
                                    "assault",
                                ),
                            },
                        ),
                    )
                ),
            },
        ),
        (
            "industrial",
            {
                "label": "Industriel",
                "subcategories": OrderedDict(
                    (
                        (
                            "salvage",
                            {
                                "label": "Salvage",
                                "keywords": ("salvage", "scrap"),
                            },
                        ),
                        (
                            "minage",
                            {
                                "label": "Minage",
                                "keywords": (
                                    "mining",
                                    "prospecting",
                                    "refinery",
                                ),
                            },
                        ),
                        (
                            "hauling",
                            {
                                "label": "Hauling",
                                "keywords": (
                                    "freight",
                                    "cargo",
                                    "hauling",
                                    "transport",
                                    "courier",
                                    "logistics",
                                    "delivery",
                                    "carrier",
                                    "merchant",
                                    "mercantile",
                                    "trader",
                                    "commerce",
                                ),
                            },
                        ),
                    )
                ),
            },
        ),
        (
            "support",
            {
                "label": "Support",
                "subcategories": OrderedDict(
                    (
                        (
                            "medical",
                            {
                                "label": "Medical",
                                "keywords": (
                                    "medical",
                                    "rescue",
                                    "hospital",
                                    "med",
                                    "triage",
                                ),
                            },
                        ),
                        (
                            "refuel",
                            {
                                "label": "Refuel",
                                "keywords": ("refuel", "fuel"),
                            },
                        ),
                        (
                            "repair",
                            {
                                "label": "Repair",
                                "keywords": (
                                    "repair",
                                    "service",
                                    "tow",
                                    "tractor",
                                ),
                            },
                        ),
                        (
                            "exploration",
                            {
                                "label": "Exploration",
                                "keywords": (
                                    "explor",
                                    "expedition",
                                    "pathfinder",
                                    "science",
                                    "survey",
                                    "touring",
                                    "recon",
                                    "scout",
                                    "reporting",
                                    "data",
                                    "observation",
                                ),
                            },
                        ),
                    )
                ),
            },
        ),
    )
)

CATEGORY_FALLBACK = {
    "LF": ("military", "chasseur"),
    "MF": ("military", "chasseur"),
    "HF": ("military", "chasseur"),
    "CAP": ("military", "capitaux"),
    "MR": ("support", "exploration"),
}

SUBCATEGORY_LOOKUP = {
    sub_slug: {
        "category": cat_slug,
        "label": sub_data["label"],
        "keywords": sub_data["keywords"],
    }
    for cat_slug, cat_data in FILTER_TREE.items()
    for sub_slug, sub_data in cat_data["subcategories"].items()
}


def _match_filter_category(role: str | None) -> tuple[str | None, str | None]:
    """Return the filter category/subcategory slugs matching the given role."""

    text = (role or "").lower()
    for cat_slug, cat_data in FILTER_TREE.items():
        for sub_slug, sub_data in cat_data["subcategories"].items():
            if any(keyword in text for keyword in sub_data["keywords"]):
                return cat_slug, sub_slug
    return None, None


def _fallback_filter_category(ship: Ship) -> tuple[str | None, str | None]:
    """Provide a best-effort category based on the legacy ship category."""

    return CATEGORY_FALLBACK.get(ship.category, (None, None))


def _classify_ship(ship: Ship) -> tuple[str | None, str | None]:
    """Attach filter metadata to the ship and return the selected slugs."""

    cat_slug, sub_slug = _match_filter_category(ship.role)
    if not cat_slug:
        cat_slug, sub_slug = _fallback_filter_category(ship)

    ship.filter_category = cat_slug
    ship.filter_category_label = FILTER_TREE.get(cat_slug, {}).get("label") if cat_slug else None
    ship.filter_subcategory = sub_slug
    if sub_slug and sub_slug in SUBCATEGORY_LOOKUP:
        ship.filter_subcategory_label = SUBCATEGORY_LOOKUP[sub_slug]["label"]
    else:
        ship.filter_subcategory_label = None
    return cat_slug, sub_slug


@auth_decorators.login_required
def operation_overview(request):
    """Display the current operation and its highlighted ship."""

    operation_qs = Operation.objects.select_related("highlighted_ship")
    operation = operation_qs.filter(is_active=True).first()
    if operation is None:
        operation = operation_qs.order_by("-updated_at").first()

    context = {
        "operation": operation,
        "can_manage_operations": can_manage_ops(request.user),
    }
    return render(request, "ops/operation_overview.html", context)


@auth_decorators.login_required
@auth_decorators.user_passes_test(can_manage_ops)
def ships_list(request):
    """Display the list of ships, optionally filtered by category."""

    category = request.GET.get("cat")
    if category not in FILTER_TREE:
        category = None

    subcategory = request.GET.get("subcat")
    if not category or subcategory not in SUBCATEGORY_LOOKUP:
        subcategory = None
    elif SUBCATEGORY_LOOKUP[subcategory]["category"] != category:
        subcategory = None

    ships_queryset = Ship.objects.all().order_by("name")
    ships = []
    for ship in ships_queryset:
        ship_cat, ship_subcat = _classify_ship(ship)

        if category and ship_cat != category:
            continue
        if subcategory and ship_subcat != subcategory:
            continue

        ships.append(ship)




            "label": cat_data["label"],
            "subcategories": [
                {"slug": sub_slug, "label": sub_data["label"]}
                for sub_slug, sub_data in cat_data["subcategories"].items()
            ],
        }
        for cat_slug, cat_data in FILTER_TREE.items()
    ]

    current_category = next(
        (item for item in display_categories if item["slug"] == category),
        None,
    )

    context = {
        "ships": ships,
        "categories": display_categories,
        "current_cat": category,
        "current_category": current_category,
        "current_subcat": subcategory,
    }
    return render(request, "ops/ships_list.html", context)


@auth_decorators.login_required
@auth_decorators.user_passes_test(can_manage_ops)
def ships_allocation(request):
    """Show all ships with their crew allocations."""

    can_edit = can_manage_ops(request.user)
    user_queryset = RoleSlotForm.default_user_queryset() if can_edit else None

    ships_queryset = ships_with_slots().order_by("category", "name")
    prepared_ships = [
        prepare_ship_for_display(ship, can_edit=can_edit, user_queryset=user_queryset)
        for ship in ships_queryset
    ]

    grouped_ships = group_ships_by_category(prepared_ships)

    context = {
        "can_edit": can_edit,
        "grouped_ships": grouped_ships,
    }
    return render(request, "ops/ships_allocation.html", context)


@auth_decorators.login_required
@auth_decorators.user_passes_test(can_manage_ops)
def ship_detail(request, pk):
    """Display the details of a single ship and manage its role templates."""
    ship = get_object_or_404(ships_with_slots(), pk=pk)
    can_edit = can_manage_ops(request.user)
    user_queryset = RoleSlotForm.default_user_queryset() if can_edit else None

    ship = prepare_ship_for_display(
        ship,
        can_edit=can_edit,
        user_queryset=user_queryset,
    )
    _classify_ship(ship)
    slots_by_role = ship.slots_by_role

    role_form = ShipRoleTemplateForm()

    if request.method == "POST" and can_edit and "role_name" in request.POST:
        role_form = ShipRoleTemplateForm(request.POST)
        if role_form.is_valid():
            role_template = role_form.save(commit=False)
            role_template.ship = ship
            role_template.save()
            messages.success(request, "Rôle ajouté au vaisseau.")
            return redirect("ship_detail", pk=ship.pk)

    context = {
        "ship": ship,
        "slots_by_role": slots_by_role,
        "role_form": role_form,
        "can_edit": can_edit,
    }
    return render(request, "ops/ship_detail.html", context)


@auth_decorators.login_required
@auth_decorators.user_passes_test(can_manage_ops)
def role_slot_update(request, pk):
    """Update a single role slot assignment."""
    slot = get_object_or_404(RoleSlot, pk=pk)

    if request.method == "POST":
        form = RoleSlotForm(
            request.POST,
            instance=slot,
            user_queryset=RoleSlotForm.default_user_queryset(),
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Affectation mise à jour.")

        next_url = request.POST.get("next")
        if next_url:
            allowed_hosts = {request.get_host()}
            if url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts=allowed_hosts,
                require_https=request.is_secure(),
            ):
                return redirect(next_url)

    return redirect("ship_detail", pk=slot.ship_id)