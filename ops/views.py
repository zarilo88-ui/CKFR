
from .forms import RoleSlotForm, ShipRoleTemplateForm
from .models import RoleSlot, Ship
from .services import (
    group_ships_by_category,
    prepare_ship_for_display,
    ships_with_slots,
)


def is_planner(user):
    """Return True if the user can manage ship allocations."""
    return user.is_superuser or user.groups.filter(
        name__in=["Planner", "Administrateur", "Planificateur"]
    ).exists()


@login_required
def ships_list(request):
    """Display the list of ships, optionally filtered by category."""

    category = request.GET.get("cat")
    valid_categories = {code for code, _ in Ship.CATEGORY_CHOICES}
    if category not in valid_categories:
        category = None

    ship_type = request.GET.get("type")
    available_types_qs = (
        Ship.objects.exclude(role="")
        .order_by("role")
        .values_list("role", flat=True)
        .distinct()
    )
    available_types = list(available_types_qs)
    if ship_type not in available_types:
        ship_type = None

    queryset = Ship.objects.all()
    if category:
        queryset = queryset.filter(category=category)
    if ship_type:
        queryset = queryset.filter(role=ship_type)
    ships = queryset.order_by("name")

    context = {
        "ships": ships,
        "categories": Ship.CATEGORY_CHOICES,
        "current_cat": category,
        "ship_types": available_types,
        "current_type": ship_type,
    }
    return render(request, "ops/ships_list.html", context)


@login_required
def ships_allocation(request):
    """Show all ships with their crew allocations."""

    can_edit = is_planner(request.user)
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


@login_required
def ship_detail(request, pk):
    """Display the details of a single ship and manage its role templates."""
    ship = get_object_or_404(ships_with_slots(), pk=pk)
    can_edit = is_planner(request.user)
    user_queryset = RoleSlotForm.default_user_queryset() if can_edit else None

    ship = prepare_ship_for_display(
        ship,
        can_edit=can_edit,
        user_queryset=user_queryset,
    )
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


@login_required
@user_passes_test(is_planner)
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