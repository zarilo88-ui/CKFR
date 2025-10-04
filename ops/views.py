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

    return render(
        request,
        "ops/ships_list.html",
        {
            "ships": ships,
            "categories": Ship.CATEGORY_CHOICES,
            "current_cat": category,
            "ship_types": available_types,
            "current_type": ship_type,
        },
    )


@login_required
def ships_allocation(request):
    """Show all ships with their crew allocations."""

    can_edit = is_planner(request.user)
    user_queryset = RoleSlotForm.default_user_queryset() if can_edit else None

    prepared_ships = [
        prepare_ship_for_display(ship, can_edit=can_edit, user_queryset=user_queryset)
        for ship in ships_with_slots().order_by("category", "name")
    ]

    grouped_ships = group_ships_by_category(prepared_ships)

    return render(
        request,
        "ops/ships_allocation.html",  # ensure this template exists
        {
            "can_edit": can_edit,
            "grouped_ships": grouped_ships,
        },
@@ -111,26 +126,26 @@ def ship_detail(request, pk):
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