"""Views for the operations module."""

from collections import OrderedDict

from django.contrib import messages
from django.contrib.auth import decorators as auth_decorators
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import (
    HighlightedShipFormSet,
    OperationForm,
    RoleSlotForm,
    ShipRoleTemplateForm,
)
from .models import (
    Operation,
    OperationHighlightedCrewAssignment,
    OperationHighlightedShip,
    RoleSlot,
    Ship,
)
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
    ship.filter_category_label = (
        FILTER_TREE.get(cat_slug, {}).get("label") if cat_slug else None
    )
    ship.filter_subcategory = sub_slug
    if sub_slug and sub_slug in SUBCATEGORY_LOOKUP:
        ship.filter_subcategory_label = SUBCATEGORY_LOOKUP[sub_slug]["label"]
    else:
        ship.filter_subcategory_label = None
    return cat_slug, sub_slug


@auth_decorators.login_required
def operation_overview(request):
    """Display the current operation and its highlighted ship."""

    operation_qs = Operation.objects.prefetch_related(
        "highlighted_ship_links__ship",
        "highlighted_ship_links__crew_assignments",
    )
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
def operations_manage(request):
    """Allow administrators to create and manage operations."""

    operations = (
        Operation.objects.prefetch_related(
            "highlighted_ship_links__ship",
            "highlighted_ship_links__crew_assignments",
        )
        .all()
        .order_by("-is_active", "-updated_at", "title")
    )
    form = OperationForm(request.POST or None)

    if request.method == "POST":
        ships_formset = HighlightedShipFormSet(request.POST, prefix="ships")
    else:
        ships_formset = HighlightedShipFormSet(prefix="ships", initial=[{}])

    if request.method == "POST":
        if form.is_valid() and ships_formset.is_valid():
            operation = form.save()
            _store_highlighted_ships(operation, ships_formset)
            messages.success(
                request,
                f"L’opération « {operation.title} » a été enregistrée.",
            )
            return redirect("operations_manage")
        messages.error(request, "Merci de corriger les erreurs ci-dessous.")

    context = {
        "operations": operations,
        "form": form,
        "ships_formset": ships_formset,
    }
    return render(request, "ops/operations_manage.html", context)


@auth_decorators.login_required
@auth_decorators.user_passes_test(can_manage_ops)
def operation_edit(request, pk):
    """Edit an existing operation."""

    operation = get_object_or_404(Operation, pk=pk)
    form = OperationForm(request.POST or None, instance=operation)
    if request.method == "POST":
        ships_formset = HighlightedShipFormSet(request.POST, prefix="ships")
    else:
        highlighted_links = operation.highlighted_ship_links.prefetch_related(
            "crew_assignments",
            "ship",
        )
        initial = []
        for link in highlighted_links:
            initial.append(
                {
                    "ship": link.ship_id,
                    **{
                        f"{role}_entries": link.get_crew_list(role)
                        for role, _ in OperationHighlightedShip.ROLE_CHOICES
                    },
                }
            )
        if not initial:
            initial.append({})
        ships_formset = HighlightedShipFormSet(prefix="ships", initial=initial)

    if request.method == "POST":
        if form.is_valid() and ships_formset.is_valid():
            operation = form.save()
            _store_highlighted_ships(operation, ships_formset)
            messages.success(
                request,
                f"L’opération « {operation.title} » a été mise à jour.",
            )
            return redirect("operations_manage")
        messages.error(request, "Merci de corriger les erreurs ci-dessous.")

    context = {
        "form": form,
        "operation": operation,
        "page_title": f"Modifier {operation.title}",
        "heading": "Modifier l’opération",
        "submit_label": "Enregistrer",
        "ships_formset": ships_formset,
    }
    return render(request, "ops/operation_form.html", context)


@auth_decorators.login_required
@auth_decorators.user_passes_test(can_manage_ops)
def operation_activate(request, pk):
    """Mark an operation as the active one."""

    if request.method == "POST":
        operation = get_object_or_404(Operation, pk=pk)
        operation.is_active = True
        operation.save()
        messages.success(
            request,
            f"L’opération « {operation.title} » est désormais active.",
        )
    return redirect("operations_manage")


@auth_decorators.login_required
@auth_decorators.user_passes_test(can_manage_ops)
def operation_delete(request, pk):
    """Delete an operation via the management dashboard."""

    if request.method == "POST":
        operation = get_object_or_404(Operation, pk=pk)
        title = operation.title
        operation.delete()
        messages.success(request, f"L’opération « {title} » a été supprimée.")
    return redirect("operations_manage")


def _store_highlighted_ships(operation: Operation, formset: HighlightedShipFormSet) -> None:
    """Persist highlighted ships (and associated crew) for an operation."""

    operation.highlighted_ship_links.all().delete()
    for form in formset:
        if not hasattr(form, "cleaned_data"):
            continue
        if form.cleaned_data.get("DELETE"):
            continue
        ship = form.cleaned_data.get("ship")
        if ship is None:
            continue
        link = OperationHighlightedShip.objects.create(
            operation=operation,
            ship=ship,
        )
        crew_assignments = []
        for role, _ in OperationHighlightedShip.ROLE_CHOICES:
            for order, name in enumerate(
                form.cleaned_data.get(f"{role}_entries", []),
                start=1,
            ):
                crew_assignments.append(
                    OperationHighlightedCrewAssignment(
                        highlighted_ship=link,
                        role=role,
                        crew_name=name,
                        order=order,
                    )
                )
        if crew_assignments:
            OperationHighlightedCrewAssignment.objects.bulk_create(crew_assignments)


@auth_decorators.login_required
def ships_allocation(request):
    """Display all ships with their role slots and assignments."""

    can_edit = can_manage_ops(request.user)
    user_queryset = None
    if can_edit:
        user_queryset = RoleSlotForm.default_user_queryset()

    ships = [
        prepare_ship_for_display(
            ship,
            can_edit=can_edit,
            user_queryset=user_queryset,
        )
        for ship in ships_with_slots()
    ]

    context = {
        "grouped_ships": group_ships_by_category(ships),
        "can_edit": can_edit,
    }
    return render(request, "ops/ships_allocation.html", context)


@auth_decorators.login_required
def ship_detail(request, pk):
    """Display detailed information for a ship and its role slots."""

    ship = get_object_or_404(ships_with_slots(), pk=pk)
    can_edit = can_manage_ops(request.user)
    user_queryset = RoleSlotForm.default_user_queryset() if can_edit else None

    ship = prepare_ship_for_display(
        ship,
        can_edit=can_edit,
        user_queryset=user_queryset,
    )
    _classify_ship(ship)

    role_form = None
    if can_edit:
        role_form = ShipRoleTemplateForm(request.POST or None)
        if request.method == "POST":
            if role_form.is_valid():
                template = role_form.save(commit=False)
                template.ship = ship
                template.save()
                messages.success(
                    request,
                    f"Le rôle « {template.role_name} » a été ajouté.",
                )
                return redirect("ship_detail", pk=ship.pk)
            messages.error(request, "Merci de corriger les erreurs ci-dessous.")

    context = {
        "ship": ship,
        "can_edit": can_edit,
        "role_form": role_form,
    }
    return render(request, "ops/ship_detail.html", context)


@auth_decorators.login_required
@auth_decorators.user_passes_test(can_manage_ops)
def role_slot_update(request, pk):
    """Update a role slot assignment and redirect appropriately."""

    slot = get_object_or_404(RoleSlot, pk=pk)
    if request.method != "POST":
        return redirect("ship_detail", pk=slot.ship_id)

    form = RoleSlotForm(request.POST, instance=slot)
    if form.is_valid():
        form.save()
        messages.success(request, "La place a été mise à jour.")
    else:
        messages.error(request, "Impossible de mettre à jour la place.")

    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect("ship_detail", pk=slot.ship_id)


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