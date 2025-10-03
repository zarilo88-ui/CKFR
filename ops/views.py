"""Views for the operations module."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

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

    queryset = Ship.objects.all()
    if category:
        queryset = queryset.filter(category=category)
    ships = queryset.order_by("name")

    return render(
        request,
        "ops/ships_list.html",
        {
            "ships": ships,
            "categories": Ship.CATEGORY_CHOICES,
            "current_cat": category,
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
    )


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

    return render(
        request,
        "ops/ship_detail.html",
        {
            "ship": ship,
            "slots_by_role": slots_by_role,
            "role_form": role_form,
            "can_edit": can_edit,
        },
    )


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